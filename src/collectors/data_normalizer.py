# src/collectors/data_normalizer.py

from typing import Dict, List
from datetime import datetime
import hashlib

class DataNormalizer:
    """
    数据标准化器
    将Twitter和NewsAPI的不同格式统一成标准格式
    """
    
    @staticmethod
    def normalize_tweet(tweet: Dict) -> Dict:
        """
        将Twitter推文转换为标准格式
        
        标准格式：
        {
            'id': str,
            'title': str,
            'content': str,
            'url': str,
            'source': str,
            'source_type': 'twitter',
            'author': str,
            'published_at': str (ISO format),
            'categories': List[str],
            'regions': List[str],
            'mentioned_coins': List[str],
            'quality_score': float,
            'engagement': int,
            'raw_data': Dict
        }
        """
        
        text = tweet.get('text', '')
        
        # 提取标题（前100个字符）
        title = text[:100] + ('...' if len(text) > 100 else '')
        
        # 计算互动数
        metrics = tweet.get('public_metrics', {})
        engagement = (
            metrics.get('like_count', 0) + 
            metrics.get('retweet_count', 0) * 2 + 
            metrics.get('reply_count', 0) * 3
        )
        
        # 生成唯一ID
        tweet_id = tweet.get('id', '')
        unique_id = f"twitter_{tweet_id}"
        
        return {
            'id': unique_id,
            'title': title,
            'content': text,
            'url': tweet.get('url', f"https://twitter.com/i/web/status/{tweet_id}"),
            'source': f"@{tweet.get('author_username', 'unknown')}",
            'source_type': 'twitter',
            'author': tweet.get('author_username', 'unknown'),
            'published_at': tweet.get('created_at', datetime.now().isoformat()),
            'categories': tweet.get('categories', ['general']),
            'regions': tweet.get('regions', ['Global']),
            'mentioned_coins': tweet.get('mentioned_stablecoins', []),
            'quality_score': tweet.get('quality_score', 0),
            'engagement': engagement,
            'raw_data': tweet
        }
    
    @staticmethod
    def normalize_news(article: Dict) -> Dict:
        """
        将NewsAPI文章转换为标准格式
        """
        
        # 生成唯一ID
        url = article.get('url', '')
        unique_id = 'news_' + hashlib.md5(url.encode()).hexdigest()[:12]
        
        return {
            'id': unique_id,
            'title': article.get('title', 'Untitled'),
            'content': article.get('description', article.get('content', '')),
            'url': url,
            'source': article.get('source', {}).get('name', 'Unknown'),
            'source_type': 'news',
            'author': article.get('author', 'Unknown'),
            'published_at': article.get('publishedAt', datetime.now().isoformat()),
            'categories': article.get('categories', ['general']),
            'regions': article.get('regions', ['Global']),
            'mentioned_coins': article.get('mentioned_coins', []),
            'quality_score': article.get('relevance_score', 50),  # 默认50分
            'engagement': 0,  # 新闻文章没有直接互动数据
            'raw_data': article
        }
    
    @staticmethod
    def merge_and_deduplicate(items: List[Dict]) -> List[Dict]:
        """
        合并数据并去重
        
        去重规则：
        1. 相同URL视为重复
        2. 标题相似度>80%视为重复（保留质量分数高的）
        """
        
        # 按URL去重
        url_map = {}
        for item in items:
            url = item.get('url', '')
            if url and url not in url_map:
                url_map[url] = item
            elif url:
                # 如果URL重复,保留质量分数更高的
                if item.get('quality_score', 0) > url_map[url].get('quality_score', 0):
                    url_map[url] = item
        
        unique_items = list(url_map.values())
        
        # 按标题相似度去重（简化版：前50字符相同）
        title_map = {}
        for item in unique_items:
            title_key = item.get('title', '')[:50].lower().strip()
            if title_key not in title_map:
                title_map[title_key] = item
            else:
                # 保留质量分数更高的
                if item.get('quality_score', 0) > title_map[title_key].get('quality_score', 0):
                    title_map[title_key] = item
        
        final_items = list(title_map.values())
        
        # 按质量分数和时间排序
        final_items.sort(
            key=lambda x: (x.get('quality_score', 0), x.get('published_at', '')),
            reverse=True
        )
        
        return final_items
    
    @staticmethod
    def categorize_by_source(items: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按数据源分类
        """
        categorized = {
            'twitter': [],
            'news': []
        }
        
        for item in items:
            source_type = item.get('source_type', 'news')
            categorized[source_type].append(item)
        
        return categorized
    
    @staticmethod
    def categorize_by_topic(items: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按主题分类
        """
        categorized = {
            'policy': [],
            'company': [],
            'funding': [],
            'market': [],
            'general': []
        }
        
        for item in items:
            categories = item.get('categories', ['general'])
            for category in categories:
                if category in categorized:
                    categorized[category].append(item)
        
        return categorized