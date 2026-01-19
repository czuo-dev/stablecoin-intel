# src/collectors/twitter_filter.py

from typing import List, Dict
import re
from datetime import datetime, timedelta

class TwitterFilter:
    """
    Twitter推文质量筛选器
    过滤低质量内容，保留高价值信息
    """
    
    def __init__(self):
        # 高质量账号列表（已验证账号、行业KOL）
        self.verified_accounts = [
            "circle", "Tether_to", "paxos", "coinbase",
            "MessariCrypto", "delcastillop", "jp_koning",
            "JSeyff", "francispouliot_", "CaitlinLong_"
        ]
        
        # 垃圾内容特征
        self.spam_patterns = [
            r'airdrop',
            r'giveaway',
            r'🎁',
            r'free\s+\w+',
            r'click\s+here',
            r'dm\s+me',
            r'follow\s+back'
        ]
        
        # 高价值关键词（加权计分）
        self.quality_keywords = {
            'high': ['regulation', 'license', 'ban', 'approval', 'partnership', 
                    'launch', 'acquisition', '监管', '牌照', '禁令'],
            'medium': ['stablecoin', 'USDC', 'USDT', 'Tether', 'Circle',
                      '稳定币', 'market cap', 'volume'],
            'low': ['crypto', 'blockchain', 'DeFi', 'payment']
        }
    
    def is_spam(self, tweet_text: str) -> bool:
        """检测垃圾推文"""
        text_lower = tweet_text.lower()
        
        for pattern in self.spam_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        # 检测过多emoji（超过3个）
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]', tweet_text))
        if emoji_count > 3:
            return True
        
        # 检测过多链接（超过2个）
        url_count = len(re.findall(r'http[s]?://\S+', tweet_text))
        if url_count > 2:
            return True
        
        return False
    
    def calculate_quality_score(self, tweet: Dict) -> float:
        """
        计算推文质量分数（0-100）
        
        评分标准：
        - 账号质量：30分
        - 内容质量：40分
        - 互动数据：30分
        """
        score = 0
        
        # 1. 账号质量评分（0-30分）
        author_username = tweet.get('author_username', '').lower()
        if author_username in self.verified_accounts:
            score += 30  # 认证账号或KOL
        elif tweet.get('author_verified', False):
            score += 20  # 蓝V认证
        elif tweet.get('author_followers', 0) > 10000:
            score += 15  # 粉丝数>1万
        elif tweet.get('author_followers', 0) > 1000:
            score += 10  # 粉丝数>1千
        else:
            score += 5   # 普通账号
        
        # 2. 内容质量评分（0-40分）
        text = tweet.get('text', '')
        
        # 检测高价值关键词
        high_kw = sum(1 for kw in self.quality_keywords['high'] if kw.lower() in text.lower())
        medium_kw = sum(1 for kw in self.quality_keywords['medium'] if kw.lower() in text.lower())
        low_kw = sum(1 for kw in self.quality_keywords['low'] if kw.lower() in text.lower())
        
        content_score = min(high_kw * 15 + medium_kw * 8 + low_kw * 3, 40)
        score += content_score
        
        # 3. 互动数据评分（0-30分）
        likes = tweet.get('public_metrics', {}).get('like_count', 0)
        retweets = tweet.get('public_metrics', {}).get('retweet_count', 0)
        replies = tweet.get('public_metrics', {}).get('reply_count', 0)
        
        engagement = likes + retweets * 2 + replies * 3
        
        if engagement > 1000:
            score += 30
        elif engagement > 500:
            score += 25
        elif engagement > 100:
            score += 20
        elif engagement > 50:
            score += 15
        elif engagement > 10:
            score += 10
        else:
            score += 5
        
        return min(score, 100)  # 最高100分
    
    def filter_tweets(self, tweets: List[Dict], min_score: int = 50) -> List[Dict]:
        """
        筛选高质量推文
        
        Args:
            tweets: 原始推文列表
            min_score: 最低质量分数（默认50分）
        
        Returns:
            筛选后的高质量推文
        """
        filtered = []
        
        for tweet in tweets:
            # 1. 排除垃圾内容
            if self.is_spam(tweet.get('text', '')):
                continue
            
            # 2. 计算质量分数
            score = self.calculate_quality_score(tweet)
            tweet['quality_score'] = score
            
            # 3. 只保留高于阈值的推文
            if score >= min_score:
                filtered.append(tweet)
        
        # 按质量分数降序排列
        filtered.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return filtered
    
    def deduplicate_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """
        去重相似推文（同一新闻的多个转发）
        使用简单的文本相似度算法
        """
        if not tweets:
            return []
        
        unique_tweets = []
        seen_texts = set()
        
        for tweet in tweets:
            text = tweet.get('text', '')
            
            # 提取核心内容（去掉链接、@mention、#hashtag）
            core_text = re.sub(r'http[s]?://\S+', '', text)
            core_text = re.sub(r'@\w+', '', core_text)
            core_text = re.sub(r'#\w+', '', core_text)
            core_text = core_text.strip().lower()
            
            # 生成文本指纹（前50个字符）
            fingerprint = core_text[:50]
            
            if fingerprint not in seen_texts:
                seen_texts.add(fingerprint)
                unique_tweets.append(tweet)
        
        return unique_tweets
    
    def enrich_tweet_data(self, tweet: Dict) -> Dict:
        """
        丰富推文数据（添加分类、标签等）
        """
        text = tweet.get('text', '')
        
        # 识别主题类别
        categories = []
        if any(kw in text.lower() for kw in ['regulation', 'ban', 'license', '监管', '牌照']):
            categories.append('policy')
        if any(kw in text.lower() for kw in ['launch', 'partnership', 'acquisition']):
            categories.append('company')
        if any(kw in text.lower() for kw in ['funding', 'investment', 'raise']):
            categories.append('funding')
        if any(kw in text.lower() for kw in ['market', 'price', 'volume', '市值']):
            categories.append('market')
        
        tweet['categories'] = categories if categories else ['general']
        
        # 识别提及的稳定币
        stablecoins = []
        coin_patterns = {
            'USDC': r'\bUSDC\b',
            'USDT': r'\bUSDT\b',
            'DAI': r'\bDAI\b',
            'BUSD': r'\bBUSD\b',
            'PYUSD': r'\bPYUSD\b'
        }
        
        for coin, pattern in coin_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                stablecoins.append(coin)
        
        tweet['mentioned_stablecoins'] = stablecoins
        
        # 识别地区
        regions = []
        region_keywords = {
            'US': ['US', 'United States', 'America', 'SEC', 'CFTC'],
            'EU': ['EU', 'Europe', 'MiCA', 'ECB'],
            'Asia': ['China', 'Hong Kong', 'Singapore', 'Japan', '中国', '香港'],
            'LATAM': ['Brazil', 'Argentina', 'Mexico', 'Latin America']
        }
        
        for region, keywords in region_keywords.items():
            if any(kw.lower() in text.lower() for kw in keywords):
                regions.append(region)
        
        tweet['regions'] = regions if regions else ['Global']
        
        return tweet