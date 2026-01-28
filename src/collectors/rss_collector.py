# src/collectors/rss_collector.py
"""
RSS 订阅收集器 V1.0
- 支持多源 RSS 收集
- 内置内容过滤（排除行情类）
- 支持 Google News RSS
"""

import os
import json
import re
import feedparser
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


class RSSCollector:
    """
    RSS 订阅收集器
    - 从配置文件加载 RSS 源
    - 自动过滤行情/价格类内容
    - 支持 Google News RSS 搜索
    """

    def __init__(self, config_path: str = None):
        """
        初始化收集器

        Args:
            config_path: RSS 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.filters = self.config.get('filters', {})

        # 统计
        self.stats = {
            'total_fetched': 0,
            'total_filtered': 0,
            'by_source': {}
        }

    def _load_config(self, config_path: str = None) -> Dict:
        """加载 RSS 配置"""
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(base_dir, 'config', 'rss_feeds.json')

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 默认配置
        return {
            'feeds': {},
            'filters': {
                'must_contain_any': ['stablecoin', 'crypto', 'USDC'],
                'exclude_keywords': ['price prediction', 'pump', 'dump']
            }
        }

    def _should_include(self, title: str, description: str, source_filters: List[str] = None) -> bool:
        """
        判断内容是否应该保留

        Args:
            title: 文章标题
            description: 文章描述
            source_filters: 该源特定的过滤关键词（必须包含其中之一）

        Returns:
            True 如果应该保留
        """
        text = f"{title} {description}".lower()

        # 1. 检查排除关键词
        exclude_keywords = self.filters.get('exclude_keywords', [])
        for kw in exclude_keywords:
            if kw.lower() in text:
                return False

        # 2. 如果有源特定过滤词，必须包含其中之一
        if source_filters:
            has_filter_keyword = any(kw.lower() in text for kw in source_filters)
            if not has_filter_keyword:
                return False

        # 3. 检查必须包含的关键词（至少一个）
        must_contain = self.filters.get('must_contain_any', [])
        if must_contain:
            has_required = any(kw.lower() in text for kw in must_contain)
            if not has_required:
                return False

        return True

    def _fetch_feed(self, url: str):
        """使用 User-Agent 获取 feed"""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                data = response.read()
                return feedparser.parse(data)
        except Exception:
            # 回退到直接解析
            return feedparser.parse(url)

    def _parse_feed(self, feed_config: Dict, hours_back: int = 24) -> List[Dict]:
        """
        解析单个 RSS feed

        Args:
            feed_config: feed 配置
            hours_back: 收集多少小时内的内容

        Returns:
            标准化的文章列表
        """
        url = feed_config.get('url', '')
        name = feed_config.get('name', 'Unknown')
        category = feed_config.get('category', 'unknown')
        source_filters = feed_config.get('filter_keywords', [])

        articles = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        try:
            print(f"  📡 {name}...", end=' ', flush=True)
            feed = self._fetch_feed(url)

            if feed.bozo and not feed.entries:
                print(f"⚠️ 解析失败")
                return []

            fetched = 0
            kept = 0

            for entry in feed.entries:
                fetched += 1

                # 解析发布时间
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])

                # 时间过滤
                if published and published < cutoff_time:
                    continue

                title = entry.get('title', '')
                description = entry.get('summary', entry.get('description', ''))

                # 清理 HTML 标签
                description = re.sub(r'<[^>]+>', '', description)

                # 内容过滤
                if not self._should_include(title, description, source_filters):
                    continue

                kept += 1
                articles.append({
                    'title': title,
                    'description': description[:500],  # 限制长度
                    'url': entry.get('link', ''),
                    'source': name,
                    'source_category': category,
                    'published_at': published.isoformat() if published else '',
                    'data_type': 'rss'
                })

            print(f"✓ {kept}/{fetched} 条")

            self.stats['total_fetched'] += fetched
            self.stats['total_filtered'] += kept
            self.stats['by_source'][name] = {'fetched': fetched, 'kept': kept}

            return articles

        except Exception as e:
            print(f"❌ 错误: {e}")
            return []

    def collect_from_feeds(self, hours_back: int = 24) -> List[Dict]:
        """
        从所有配置的 RSS 源收集内容

        Args:
            hours_back: 收集多少小时内的内容

        Returns:
            所有文章列表
        """
        all_articles = []
        feeds_config = self.config.get('feeds', {})

        print("\n" + "=" * 60)
        print("📰 RSS 订阅收集")
        print("=" * 60)

        for group_name, feeds in feeds_config.items():
            print(f"\n📌 {group_name.upper()}:")

            for feed_config in feeds:
                articles = self._parse_feed(feed_config, hours_back)
                all_articles.extend(articles)
                time.sleep(1)  # 避免请求过快

        return all_articles

    def collect_from_google_news(self, hours_back: int = 24) -> List[Dict]:
        """
        从 Google News RSS 收集内容

        Args:
            hours_back: 收集多少小时内的内容

        Returns:
            文章列表
        """
        google_config = self.config.get('google_news', {})
        keywords = google_config.get('keywords', [])
        max_results = google_config.get('max_results_per_keyword', 10)

        if not keywords:
            return []

        all_articles = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        print(f"\n📌 GOOGLE NEWS:")

        for keyword in keywords:
            print(f"  🔍 '{keyword}'...", end=' ', flush=True)

            try:
                # 构建 Google News RSS URL
                encoded_keyword = urllib.parse.quote(keyword)
                url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en-US&gl=US&ceid=US:en"

                feed = feedparser.parse(url)

                fetched = 0
                kept = 0

                for entry in feed.entries[:max_results]:
                    fetched += 1

                    # 解析发布时间
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])

                    # 时间过滤
                    if published and published < cutoff_time:
                        continue

                    title = entry.get('title', '')
                    description = entry.get('summary', '')
                    description = re.sub(r'<[^>]+>', '', description)

                    # 内容过滤
                    if not self._should_include(title, description):
                        continue

                    kept += 1
                    all_articles.append({
                        'title': title,
                        'description': description[:500],
                        'url': entry.get('link', ''),
                        'source': f"Google News ({keyword})",
                        'source_category': 'google_news',
                        'published_at': published.isoformat() if published else '',
                        'data_type': 'rss',
                        'search_keyword': keyword
                    })

                print(f"✓ {kept}/{fetched} 条")
                time.sleep(1)

            except Exception as e:
                print(f"❌ 错误: {e}")

        return all_articles

    def collect_all(self, hours_back: int = 24) -> List[Dict]:
        """
        收集所有 RSS 内容（订阅源 + Google News）

        Args:
            hours_back: 收集多少小时内的内容

        Returns:
            去重后的文章列表
        """
        # 收集订阅源
        feed_articles = self.collect_from_feeds(hours_back)

        # 收集 Google News
        google_articles = self.collect_from_google_news(hours_back)

        # 合并
        all_articles = feed_articles + google_articles

        # 去重（基于标题）
        seen_titles = set()
        unique_articles = []

        for article in all_articles:
            title_key = article.get('title', '').lower()[:50]
            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)

        print("\n" + "=" * 60)
        print(f"✅ RSS 收集完成")
        print(f"   订阅源: {len(feed_articles)} 条")
        print(f"   Google News: {len(google_articles)} 条")
        print(f"   去重后: {len(unique_articles)} 条")
        print("=" * 60)

        return unique_articles


# 测试
if __name__ == "__main__":
    collector = RSSCollector()

    # 测试收集
    articles = collector.collect_all(hours_back=48)

    print(f"\n📋 收集到 {len(articles)} 篇文章:")
    for i, article in enumerate(articles[:10], 1):
        print(f"\n{i}. [{article['source']}]")
        print(f"   {article['title'][:60]}...")
        print(f"   {article['url'][:60]}...")
