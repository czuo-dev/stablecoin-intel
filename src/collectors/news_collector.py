# src/collectors/news_collector.py
"""
新闻收集器 V1.1
- 支持新配置结构：competitors.tier_0/tier_1, customers.layer_a, industry_topics
- 支持 keywords_any + keywords_context 组合搜索
"""

import os
import json
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from typing import List, Dict
import time
import urllib3

# 从环境变量读取配置（兼容 GitHub Actions）
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
NEWSAPI_DAILY_LIMIT = int(os.getenv('NEWSAPI_DAILY_LIMIT', '100'))
NEWSAPI_REQUEST_INTERVAL = int(os.getenv('NEWSAPI_REQUEST_INTERVAL', '5'))

# 如果环境变量没有，尝试从 config.py 读取（本地开发用）
if not NEWSAPI_KEY:
    try:
        from config import NEWSAPI_KEY as CONFIG_KEY
        NEWSAPI_KEY = CONFIG_KEY
    except ImportError:
        pass

# 禁用HTTP/2以避免协议错误
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_keywords_config() -> Dict:
    """从 config/keywords.json 加载关键词配置"""
    # 尝试多个可能的路径
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'keywords.json'),
        os.path.join(os.getcwd(), 'config', 'keywords.json'),
    ]

    for config_path in possible_paths:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)

    return {}


class NewsCollector:
    """
    新闻收集器 - 使用NewsAPI收集稳定币相关新闻
    关键词从 config/keywords.json 读取
    支持新配置结构 V1.1
    """

    def __init__(self):
        self.client = NewsApiClient(api_key=NEWSAPI_KEY)
        self.request_count = 0
        self.max_requests = NEWSAPI_DAILY_LIMIT

        # 从配置文件加载关键词
        self.config = load_keywords_config()
        self.search_strategies = self._build_search_strategies()

        # 高质量新闻源（优先）
        self.preferred_sources = [
            'bloomberg', 'reuters', 'the-wall-street-journal', 'financial-times',
            'coindesk', 'the-block', 'decrypt', 'cointelegraph'
        ]

        # 排除的低质量源
        self.excluded_sources = [
            'crypto-news-flash', 'newsbtc', 'bitcoinist', 'ambcrypto'
        ]

    def _build_search_strategies(self) -> Dict:
        """
        从配置文件构建搜索策略
        支持新配置结构 V1.1：
        - competitors.tier_0_custody / tier_1_payment_infra
        - customers.layer_a
        - industry_topics with keywords_any + keywords_context
        """
        config = self.config

        # 如果配置文件中有 newsapi_search，直接使用
        if 'newsapi_search' in config:
            return config['newsapi_search']

        strategies = {
            'high_priority': {
                'keywords': [],
                'weight': 1.5
            },
            'medium_priority': {
                'keywords': [],
                'weight': 1.0
            },
            'low_priority': {
                'keywords': [],
                'weight': 0.5
            }
        }

        # ========== 高优先级：竞争对手 ==========
        competitors = config.get('competitors', {})

        # 新结构：tier_0_custody + tier_1_payment_infra
        for tier in ['tier_0_custody', 'tier_1_payment_infra']:
            for company in competitors.get(tier, []):
                name = company.get('name', '')
                if name and name not in strategies['high_priority']['keywords']:
                    strategies['high_priority']['keywords'].append(name)

        # 兼容旧结构：categories.competitors.companies
        old_categories = config.get('categories', {})
        for company in old_categories.get('competitors', {}).get('companies', []):
            for kw in company.get('keywords', []):
                if kw not in strategies['high_priority']['keywords']:
                    strategies['high_priority']['keywords'].append(kw)

        # ========== 中优先级：客户 + 主要搜索词 ==========
        customers = config.get('customers', {})

        # 新结构：layer_a
        for company in customers.get('layer_a', []):
            name = company.get('name', '')
            if name and name not in strategies['medium_priority']['keywords']:
                strategies['medium_priority']['keywords'].append(name)

        # 兼容旧结构：categories.clients.companies
        for company in old_categories.get('clients', {}).get('companies', []):
            for kw in company.get('keywords', []):
                if kw not in strategies['medium_priority']['keywords']:
                    strategies['medium_priority']['keywords'].append(kw)

        # 添加主要搜索关键词
        search_keywords = config.get('search_keywords', {})
        for kw in search_keywords.get('primary', []):
            if kw not in strategies['medium_priority']['keywords']:
                strategies['medium_priority']['keywords'].append(kw)

        # ========== 低优先级：行业话题 ==========
        industry_topics = config.get('industry_topics', {})

        # 新结构：industry_topics with keywords_any + keywords_context
        for topic_key, topic_config in industry_topics.items():
            keywords_any = topic_config.get('keywords_any', [])
            keywords_context = topic_config.get('keywords_context', [])

            # 直接添加 keywords_any
            for kw in keywords_any:
                if kw not in strategies['low_priority']['keywords']:
                    strategies['low_priority']['keywords'].append(kw)

            # 生成组合搜索（keywords_any + keywords_context）
            # 限制组合数量避免过多请求
            for any_kw in keywords_any[:3]:
                for ctx_kw in keywords_context[:2]:
                    combined = f"{any_kw} {ctx_kw}"
                    if combined not in strategies['low_priority']['keywords']:
                        strategies['low_priority']['keywords'].append(combined)

        # 兼容旧结构：categories.industry.topics
        for topic in old_categories.get('industry', {}).get('topics', []):
            for kw in topic.get('keywords', []):
                if kw not in strategies['low_priority']['keywords']:
                    strategies['low_priority']['keywords'].append(kw)

        # 添加次要搜索关键词
        for kw in search_keywords.get('secondary', []):
            if kw not in strategies['low_priority']['keywords']:
                strategies['low_priority']['keywords'].append(kw)

        # ========== 默认值（配置为空时使用）==========
        if not strategies['high_priority']['keywords']:
            strategies['high_priority']['keywords'] = [
                'Fireblocks', 'BitGo', 'Copper', 'Anchorage',
                'stablecoin custody', 'MPC wallet'
            ]

        if not strategies['medium_priority']['keywords']:
            strategies['medium_priority']['keywords'] = [
                'stablecoin', 'USDC', 'USDT', 'PYUSD', 'stablecoin market'
            ]

        if not strategies['low_priority']['keywords']:
            strategies['low_priority']['keywords'] = [
                'cryptocurrency payment', 'blockchain finance', 'digital dollar'
            ]

        return strategies

    def search_with_keyword(self, keyword: str, days_back: int = 7, page_size: int = 20) -> List[Dict]:
        """使用单个关键词搜索新闻"""

        if self.request_count >= self.max_requests:
            print(f"⚠️  已达到每日API限制 ({self.max_requests}次)")
            return []

        try:
            if self.request_count > 0:
                time.sleep(NEWSAPI_REQUEST_INTERVAL)

            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.client.get_everything(
                        q=keyword,
                        language='en',
                        sort_by='relevancy',
                        page_size=page_size,
                        from_param=from_date
                    )

                    self.request_count += 1
                    return response.get('articles', [])

                except Exception as retry_error:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        print(f"  ⚠️  请求失败，{wait_time}秒后重试... ({retry_error})")
                        time.sleep(wait_time)
                    else:
                        raise retry_error

        except Exception as e:
            print(f"  ✗ '{keyword}': 搜索失败 - {e}")
            return []

    def collect_by_strategy(self, days_back: int = 7) -> Dict[str, List[Dict]]:
        """按搜索策略收集新闻"""

        print(f"🔍 开始收集过去{days_back}天的新闻...\n")

        results = {}

        total_keywords = sum(len(config['keywords']) for config in self.search_strategies.values())
        current_keyword = 0

        for priority, config in self.search_strategies.items():
            print(f"📌 {priority.upper()}:")
            articles = []

            for keyword in config['keywords']:
                current_keyword += 1
                print(f"  [{current_keyword}/{total_keywords}] 搜索: '{keyword}'...", end=' ', flush=True)

                keyword_articles = self.search_with_keyword(keyword, days_back, page_size=15)

                for article in keyword_articles:
                    article['priority_weight'] = config['weight']
                    article['search_keyword'] = keyword

                articles.extend(keyword_articles)
                print(f"✓ {len(keyword_articles)} 篇")

            print(f"  小计: {len(articles)} 篇\n")
            results[priority] = articles

        return results

    def filter_by_source_quality(self, articles: List[Dict]) -> List[Dict]:
        """根据新闻源质量过滤"""

        filtered = []

        for article in articles:
            source_id = article.get('source', {}).get('id', '')
            source_name = article.get('source', {}).get('name', '').lower()

            if any(excluded in source_name for excluded in self.excluded_sources):
                continue

            if source_id in self.preferred_sources or any(pref in source_name for pref in self.preferred_sources):
                article['source_quality'] = 'high'
            else:
                article['source_quality'] = 'medium'

            filtered.append(article)

        return filtered

    def deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """去重（基于URL和标题）"""

        seen_urls = set()
        seen_titles = set()
        unique_articles = []

        for article in articles:
            url = article.get('url', '')
            title = article.get('title', '').lower().strip()

            if url and url in seen_urls:
                continue

            title_key = title[:50]
            if title_key in seen_titles:
                continue

            seen_urls.add(url)
            seen_titles.add(title_key)
            unique_articles.append(article)

        return unique_articles

    def collect_news(self, days_back: int = 7) -> List[Dict]:
        """完整的新闻收集流程"""

        print("=" * 60)
        print("📰 NewsAPI 新闻收集")
        print("=" * 60 + "\n")

        # 显示当前使用的关键词
        print("📋 当前关键词配置:")
        for priority, config in self.search_strategies.items():
            print(f"   {priority}: {len(config['keywords'])} 个")
        print()

        results_by_priority = self.collect_by_strategy(days_back)

        all_articles = []
        for priority, articles in results_by_priority.items():
            all_articles.extend(articles)

        print(f"📊 收集统计:")
        print(f"   原始文章: {len(all_articles)} 篇")

        filtered_articles = self.filter_by_source_quality(all_articles)
        print(f"   质量过滤: {len(filtered_articles)} 篇")

        unique_articles = self.deduplicate_articles(filtered_articles)
        print(f"   去重后: {len(unique_articles)} 篇")

        unique_articles.sort(
            key=lambda x: (x.get('priority_weight', 0), x.get('source_quality') == 'high'),
            reverse=True
        )

        print(f"\n✅ 收集完成！共 {len(unique_articles)} 篇高质量新闻")
        print(f"📊 API使用: {self.request_count}/{self.max_requests} 次")
        print("=" * 60 + "\n")

        return unique_articles
