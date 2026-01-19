# src/collectors/twitter_collector.py

"""
Twitter数据收集器 - Free Tier专用版本
针对Twitter API Free tier的严格限制进行优化
"""

import tweepy
import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pickle


class TwitterCollectorFree:
    """Twitter数据收集器（Free tier专用）"""
    
    # Free tier限制参考：
    # - get_user: 300 requests / 15分钟
    # - get_users_tweets: 1,500 tweets / 月
    # - search_recent_tweets: 10,000 tweets / 月，每次最多10条
    
    def __init__(
        self,
        bearer_token: str,
        monitored_accounts: List[str] = None,
        monitored_keywords: List[str] = None,
        cache_file: str = "data/cache/twitter_cache.pkl"
    ):
        """
        初始化Twitter收集器
        
        Args:
            bearer_token: Twitter Bearer Token
            monitored_accounts: 要监控的账号列表
            monitored_keywords: 要监控的关键词列表
            cache_file: 缓存文件路径
        """
        
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            wait_on_rate_limit=True
        )
        
        self.monitored_accounts = monitored_accounts or []
        self.monitored_keywords = monitored_keywords or []
        self.cache_file = cache_file
        
        # 加载缓存
        self.cache = self._load_cache()
        
        print(f"✅ Twitter收集器初始化完成（Free tier优化版）")
        print(f"   监控账号: {len(self.monitored_accounts)}")
        print(f"   监控关键词: {len(self.monitored_keywords)}")
        print(f"   缓存记录: {len(self.cache.get('user_ids', {}))}")
    
    def _load_cache(self) -> Dict:
        """加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache = pickle.load(f)
                print(f"💾 缓存加载成功: {self.cache_file}")
                return cache
            except Exception as e:
                print(f"⚠️  缓存加载失败: {e}")
        
        return {
            'user_ids': {},
            'last_update': None
        }
    
    def _save_cache(self):
        """保存缓存"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)
        
        print(f"💾 缓存已保存")
    
    def get_user_id_cached(self, username: str) -> Optional[str]:
        """获取用户ID（优先使用缓存）"""
        
        # 检查缓存
        if username in self.cache['user_ids']:
            print(f"   {username}: 使用缓存ID")
            return self.cache['user_ids'][username]
        
        # 缓存未命中，需要API调用
        try:
            print(f"   {username}: 查询ID...")
            time.sleep(2)  # 延迟避免速率限制
            
            user = self.client.get_user(username=username)
            if user.data:
                user_id = str(user.data.id)
                self.cache['user_ids'][username] = user_id
                self._save_cache()
                return user_id
                
        except tweepy.TooManyRequests as e:
            print(f"❌ 速率限制 ({username}): {e}")
            print(f"⏳ 建议等待15分钟后重试")
            return None
        except Exception as e:
            print(f"⚠️  获取用户ID失败 ({username}): {e}")
            return None
        
        return None
    
    def batch_get_user_ids(self, usernames: List[str]) -> Dict[str, str]:
        """
        批量获取用户ID（优化版）
        
        策略：优先使用缓存，只查询未缓存的用户
        """
        
        print(f"\n📋 批量获取用户ID...")
        
        user_ids = {}
        uncached = []
        
        # 第一步：从缓存获取
        for username in usernames:
            if username in self.cache['user_ids']:
                user_ids[username] = self.cache['user_ids'][username]
            else:
                uncached.append(username)
        
        print(f"   缓存命中: {len(user_ids)}/{len(usernames)}")
        
        # 第二步：批量查询未缓存的（最多100个一次）
        if uncached:
            print(f"   需要查询: {len(uncached)} 个账号")
            
            # 分批，每次最多100个
            for i in range(0, len(uncached), 100):
                batch = uncached[i:i+100]
                
                try:
                    time.sleep(3)  # 批量查询前延迟
                    
                    users = self.client.get_users(usernames=batch)
                    
                    if users.data:
                        for user in users.data:
                            username = user.username
                            user_id = str(user.id)
                            user_ids[username] = user_id
                            self.cache['user_ids'][username] = user_id
                        
                        print(f"   ✅ 批次 {i//100 + 1}: 获取 {len(users.data)} 个ID")
                    
                except tweepy.TooManyRequests:
                    print(f"   ❌ 速率限制！请15分钟后重试")
                    break
                except Exception as e:
                    print(f"   ⚠️  批量查询失败: {e}")
            
            # 保存新获取的ID
            if len(user_ids) > len(usernames) - len(uncached):
                self._save_cache()
        
        print(f"   最终获取: {len(user_ids)}/{len(usernames)}")
        
        return user_ids
    
    def collect_minimal(self, hours: int = 24) -> Dict[str, List[Dict]]:
        """
        最小化API调用的收集策略
        
        策略：
        1. 批量获取所有用户ID（1次API调用）
        2. 只用1次搜索覆盖所有关键词
        3. 不单独查询用户推文（太消耗配额）
        """
        
        print(f"\n🐦 最小化收集策略（适配Free tier）")
        print("="*60)
        print(f"⚠️  注意：Free tier限制严格，将跳过单个账号查询")
        print(f"   策略：仅使用关键词搜索收集相关推文")
        
        # 步骤1：批量获取用户ID（缓存优先）
        print(f"\n📋 步骤1: 批量获取用户ID")
        if self.monitored_accounts:
            user_ids = self.batch_get_user_ids(self.monitored_accounts)
        else:
            user_ids = {}
        
        # 步骤2：使用关键词搜索（包含账号名）
        print(f"\n🔍 步骤2: 关键词搜索")
        
        all_keywords = list(self.monitored_keywords)
        
        # 将监控的账号也作为关键词（搜索提到这些账号的推文）
        for username in self.monitored_accounts[:5]:  # 只取前5个最重要的
            all_keywords.append(f"@{username}")
        
        keyword_tweets = self.search_combined_keywords(
            keywords=all_keywords,
            max_results=100,
            hours=hours
        )
        
        # 标记来源账号
        for tweet in keyword_tweets:
            tweet['from_monitored'] = any(
                f"@{acc}" in tweet['text'].lower() or 
                acc.lower() in tweet.get('author_username', '').lower()
                for acc in self.monitored_accounts
            )
        
        print(f"\n📊 收集完成")
        print(f"   关键词推文: {len(keyword_tweets)}")
        print(f"   来自监控账号: {sum(1 for t in keyword_tweets if t.get('from_monitored'))}")
        print(f"   API调用估计: 1-2次")
        
        return {
            "keyword_tweets": keyword_tweets,
            "user_ids": user_ids,
            "collected_at": datetime.now().isoformat()
        }
    
    def search_combined_keywords(
        self,
        keywords: List[str],
        max_results: int = 100,
        hours: int = 24
    ) -> List[Dict]:
        """
        组合关键词搜索（一次API调用）
        
        Free tier限制：每次最多10条，但可以多次调用（10,000 tweets/月）
        """
        
        tweets = []
        
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            # 策略：用OR连接关键词（Twitter查询语法）
            # 限制：查询长度不超过512字符
            keyword_groups = self._split_keywords_into_groups(keywords, max_chars=400)
            
            print(f"   关键词分为 {len(keyword_groups)} 组")
            
            for idx, group in enumerate(keyword_groups):
                print(f"   组 {idx+1}: {len(group)} 个关键词")
                
                # 构建查询
                query = " OR ".join([f'"{kw}"' for kw in group])
                query += " -is:retweet lang:en"  # 排除转推，只要英文
                
                try:
                    time.sleep(3)  # 每次搜索前延迟
                    
                    # Free tier每次最多10条，但可以分页
                    collected_in_group = 0
                    next_token = None
                    
                    while collected_in_group < max_results:
                        remaining = min(10, max_results - collected_in_group)
                        
                        response = self.client.search_recent_tweets(
                            query=query,
                            max_results=remaining,
                            start_time=start_time,
                            tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang'],
                            expansions=['author_id'],
                            user_fields=['username'],
                            pagination_token=next_token
                        )
                        
                        if response.data:
                            # 获取作者用户名映射
                            users = {user.id: user.username for user in response.includes.get('users', [])}
                            
                            for tweet in response.data:
                                matched_keywords = [kw for kw in group if kw.lower() in tweet.text.lower()]
                                
                                tweets.append({
                                    'id': str(tweet.id),
                                    'text': tweet.text,
                                    'created_at': tweet.created_at.isoformat(),
                                    'author_id': str(tweet.author_id),
                                    'author_username': users.get(tweet.author_id, 'unknown'),
                                    'likes': tweet.public_metrics['like_count'],
                                    'retweets': tweet.public_metrics['retweet_count'],
                                    'replies': tweet.public_metrics['reply_count'],
                                    'language': tweet.lang,
                                    'keywords': matched_keywords,
                                    'url': f'https://twitter.com/i/status/{tweet.id}'
                                })
                            
                            collected_in_group += len(response.data)
                            
                            # 检查是否还有更多结果
                            if hasattr(response.meta, 'next_token'):
                                next_token = response.meta.next_token
                                time.sleep(2)  # 分页延迟
                            else:
                                break
                        else:
                            break
                    
                    print(f"      ✅ 收集 {collected_in_group} 条")
                    
                except tweepy.TooManyRequests:
                    print(f"      ❌ 速率限制！停止收集")
                    break
                except Exception as e:
                    print(f"      ⚠️  搜索失败: {e}")
            
            # 去重
            unique_tweets = {}
            for tweet in tweets:
                if tweet['id'] not in unique_tweets:
                    unique_tweets[tweet['id']] = tweet
            
            tweets = list(unique_tweets.values())
            print(f"   总计（去重后）: {len(tweets)} 条")
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
        
        return tweets
    
    def _split_keywords_into_groups(self, keywords: List[str], max_chars: int = 400) -> List[List[str]]:
        """将关键词分组，避免查询过长"""
        
        groups = []
        current_group = []
        current_length = 0
        
        for kw in keywords:
            # 估算长度：关键词 + 引号 + OR
            estimated_length = len(kw) + 7  # "keyword" OR 
            
            if current_length + estimated_length > max_chars:
                if current_group:
                    groups.append(current_group)
                current_group = [kw]
                current_length = estimated_length
            else:
                current_group.append(kw)
                current_length += estimated_length
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def save_tweets(self, tweets_data: Dict, output_dir: str = "data/twitter"):
        """保存推文数据"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        output_file = f"{output_dir}/tweets_{timestamp}.json"
        
        # 添加元数据
        tweets_data['metadata'] = {
            'collected_at': datetime.now().isoformat(),
            'total_tweets': len(tweets_data.get('keyword_tweets', [])),
            'monitored_accounts': len(self.monitored_accounts),
            'monitored_keywords': len(self.monitored_keywords)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tweets_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 数据已保存: {output_file}")
        
        return output_file
    
    def get_rate_limit_status(self):
        """检查速率限制状态"""
        try:
            limits = self.client.get_rate_limit_status()
            print(f"\n📊 API速率限制状态:")
            print(json.dumps(limits, indent=2))
        except Exception as e:
            print(f"⚠️  无法获取速率限制状态: {e}")
    
    def collect_all(self, hours: int = 24) -> Dict[str, List[Dict]]:
        """
        收集所有推文（兼容方法）
        
        返回格式与旧版本兼容：
        {
            'user_tweets': [...],
            'keyword_tweets': [...]
        }
        """
        data = self.collect_minimal(hours=hours)
        
        # 将格式转换为兼容格式
        keyword_tweets = data.get('keyword_tweets', [])
        
        # 分离用户推文和关键词推文
        user_tweets = [
            t for t in keyword_tweets 
            if t.get('from_monitored', False)
        ]
        
        # 关键词推文（排除已包含在user_tweets中的）
        keyword_only_tweets = [
            t for t in keyword_tweets 
            if not t.get('from_monitored', False)
        ]
        
        return {
            'user_tweets': user_tweets,
            'keyword_tweets': keyword_only_tweets
        }
    
    def collect_user_tweets(
        self, 
        username: str, 
        max_results: int = 10, 
        hours: int = 24
    ) -> List[Dict]:
        """
        收集单个用户的推文（兼容方法）
        
        注意：Free tier限制严格，此方法使用关键词搜索来模拟
        """
        # 使用关键词搜索包含该用户名的推文
        query = f"from:{username} -is:retweet lang:en"
        
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            tweets = []
            next_token = None
            
            while len(tweets) < max_results:
                remaining = min(10, max_results - len(tweets))
                
                time.sleep(3)  # 延迟避免速率限制
                
                response = self.client.search_recent_tweets(
                    query=query,
                    max_results=remaining,
                    start_time=start_time,
                    tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang'],
                    expansions=['author_id'],
                    user_fields=['username'],
                    pagination_token=next_token
                )
                
                if response.data:
                    users = {user.id: user.username for user in response.includes.get('users', [])}
                    
                    for tweet in response.data:
                        tweets.append({
                            'id': str(tweet.id),
                            'text': tweet.text,
                            'created_at': tweet.created_at.isoformat(),
                            'author': users.get(tweet.author_id, username),
                            'author_id': str(tweet.author_id),
                            'author_username': users.get(tweet.author_id, username),
                            'likes': tweet.public_metrics['like_count'],
                            'retweets': tweet.public_metrics['retweet_count'],
                            'replies': tweet.public_metrics['reply_count'],
                            'language': tweet.lang,
                            'url': f'https://twitter.com/i/status/{tweet.id}'
                        })
                    
                    if hasattr(response.meta, 'next_token'):
                        next_token = response.meta.next_token
                        time.sleep(2)
                    else:
                        break
                else:
                    break
                
        except Exception as e:
            print(f"⚠️  收集用户推文失败 ({username}): {e}")
        
        return tweets
    
    def collect_keyword_tweets(
        self,
        keyword: str,
        max_results: int = 10,
        hours: int = 24
    ) -> List[Dict]:
        """
        收集关键词推文（兼容方法）
        """
        return self.search_combined_keywords(
            keywords=[keyword],
            max_results=max_results,
            hours=hours
        )
    
    def filter_high_quality(
        self,
        tweets: List[Dict],
        min_likes: int = 10,
        min_retweets: int = 5
    ) -> List[Dict]:
        """
        筛选高质量推文
        
        Args:
            tweets: 推文列表
            min_likes: 最小点赞数
            min_retweets: 最小转发数
        
        Returns:
            筛选后的推文列表
        """
        filtered = []
        
        for tweet in tweets:
            likes = tweet.get('likes', 0)
            retweets = tweet.get('retweets', 0)
            
            if likes >= min_likes and retweets >= min_retweets:
                filtered.append(tweet)
        
        return filtered


# 向后兼容：创建别名
TwitterCollector = TwitterCollectorFree


# 使用示例
if __name__ == "__main__":
    
    # 初始化收集器
    collector = TwitterCollectorFree(
        bearer_token="YOUR_BEARER_TOKEN",
        monitored_accounts=[
            "circle", "Tether_to", "paxos", "coinbase",
            "MessariCrypto", "paoloardoino", "jerallaire"
        ],
        monitored_keywords=[
            "stablecoin", "USDC", "USDT", "PYUSD", 
            "stablecoins", "稳定币"
        ]
    )
    
    # 收集数据
    data = collector.collect_minimal(hours=24)
    
    # 保存结果
    collector.save_tweets(data)