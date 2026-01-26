# src/collectors/news_collector.py

from newsapi import NewsApiClient
from datetime import datetime, timedelta
from typing import List, Dict
import time
import urllib3
from config import NEWSAPI_KEY, NEWSAPI_DAILY_LIMIT, NEWSAPI_REQUEST_INTERVAL

# 禁用HTTP/2以避免协议错误（某些服务器不支持HTTP/2）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NewsCollector:
    """
    新闻收集器 - 使用NewsAPI收集稳定币相关新闻
    """
    
    def __init__(self):
        self.client = NewsApiClient(api_key=NEWSAPI_KEY)
        self.request_count = 0
        self.max_requests = NEWSAPI_DAILY_LIMIT
        
        # 搜索策略配置
        self.search_strategies = {
            'high_priority': {
                'keywords': [
                    'stablecoin regulation',
                    'USDC Circle',
                    'Tether USDT',
                    'stablecoin ban',
                    'stablecoin license',
                    'PayPal PYUSD'
                ],
                'weight': 1.5  # 高优先级关键词权重
            },
            'medium_priority': {
                'keywords': [
                    'stablecoin market',
                    'digital dollar',
                    'CBDC stablecoin',
                    'Paxos USDP',
                    'stablecoin adoption'
                ],
                'weight': 1.0
            },
            'low_priority': {
                'keywords': [
                    'cryptocurrency payment',
                    'blockchain finance',
                    'crypto regulation'
                ],
                'weight': 0.5
            }
        }
        
        # 高质量新闻源（优先）
        self.preferred_sources = [
            'bloomberg',
            'reuters',
            'the-wall-street-journal',
            'financial-times',
            'coindesk',
            'the-block',
            'decrypt'
        ]
        
        # 排除的低质量源
        self.excluded_sources = [
            'crypto-news-flash',
            'newsbtc',
            'bitcoinist'
        ]
    
    def search_with_keyword(self, keyword: str, days_back: int = 7, page_size: int = 20) -> List[Dict]:
        """
        使用单个关键词搜索新闻
        
        Args:
            keyword: 搜索关键词
            days_back: 回溯天数
            page_size: 每页结果数
        """
        
        if self.request_count >= self.max_requests:
            print(f"⚠️  已达到每日API限制 ({self.max_requests}次)")
            return []
        
        try:
            # 控制请求频率（只在非第一个请求时等待）
            if self.request_count > 0:
                time.sleep(NEWSAPI_REQUEST_INTERVAL)
            
            # 格式化日期为 YYYY-MM-DD 格式（避免HTTP/2协议错误）
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # 重试逻辑（最多3次）
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.client.get_everything(
                        q=keyword,
                        language='en',
                        sort_by='relevancy',  # 按相关性排序
                        page_size=page_size,
                        from_param=from_date
                    )
                    
                    self.request_count += 1
                    
                    articles = response.get('articles', [])
                    # 不在这里打印，由调用者打印进度
                    
                    return articles
                    
                except Exception as retry_error:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # 递增等待时间：2s, 4s, 6s
                        print(f"  ⚠️  请求失败，{wait_time}秒后重试... ({retry_error})")
                        time.sleep(wait_time)
                    else:
                        raise retry_error
            
        except Exception as e:
            print(f"  ✗ '{keyword}': 搜索失败 - {e}")
            return []
    
    def collect_by_strategy(self, days_back: int = 7) -> Dict[str, List[Dict]]:
        """
        按搜索策略收集新闻
        
        Returns:
            {
                'high_priority': [...],
                'medium_priority': [...],
                'low_priority': [...]
            }
        """
        
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
                
                # 为文章添加优先级权重
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
            
            # 排除黑名单源
            if any(excluded in source_name for excluded in self.excluded_sources):
                continue
            
            # 优先白名单源
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
            
            # URL去重
            if url and url in seen_urls:
                continue
            
            # 标题相似度去重（简化版：前50字符）
            title_key = title[:50]
            if title_key in seen_titles:
                continue
            
            seen_urls.add(url)
            seen_titles.add(title_key)
            unique_articles.append(article)
        
        return unique_articles
    
    def collect_news(self, days_back: int = 7) -> List[Dict]:
        """
        完整的新闻收集流程
        
        Returns:
            去重后的高质量新闻列表
        """
        
        print("=" * 60)
        print("📰 NewsAPI 新闻收集")
        print("=" * 60 + "\n")
        
        # 1. 按策略搜索
        results_by_priority = self.collect_by_strategy(days_back)
        
        # 2. 合并所有结果
        all_articles = []
        for priority, articles in results_by_priority.items():
            all_articles.extend(articles)
        
        print(f"📊 收集统计:")
        print(f"   原始文章: {len(all_articles)} 篇")
        
        # 3. 过滤低质量源
        filtered_articles = self.filter_by_source_quality(all_articles)
        print(f"   质量过滤: {len(filtered_articles)} 篇")
        
        # 4. 去重
        unique_articles = self.deduplicate_articles(filtered_articles)
        print(f"   去重后: {len(unique_articles)} 篇")
        
        # 5. 按优先级权重排序
        unique_articles.sort(
            key=lambda x: (x.get('priority_weight', 0), x.get('source_quality') == 'high'),
            reverse=True
        )
        
        print(f"\n✅ 收集完成！共 {len(unique_articles)} 篇高质量新闻")
        print(f"📊 API使用: {self.request_count}/{self.max_requests} 次")
        print("=" * 60 + "\n")
        
        return unique_articles