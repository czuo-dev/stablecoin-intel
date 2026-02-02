# src/collectors/twitter_api_io.py
"""
TwitterAPI.io 数据收集器
使用第三方 API 替代官方 Twitter API，成本降低 96%
价格: $0.15/1000条推文
文档: https://docs.twitterapi.io/
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

# 默认每日预算上限（美元）
DEFAULT_DAILY_BUDGET = 0.2  # $0.20/天

class TwitterAPIioCollector:
    """
    使用 TwitterAPI.io 收集推文数据
    比官方 API 便宜 96%，无需 Twitter 开发者账号
    """

    BASE_URL = "https://api.twitterapi.io/twitter"
    COST_PER_TWEET = 0.00015  # $0.15 / 1000 条

    def __init__(self, api_key: str = None, daily_budget: float = None):
        """
        初始化收集器

        Args:
            api_key: TwitterAPI.io 的 API Key，可从环境变量 TWITTERAPI_IO_KEY 读取
            daily_budget: 每日预算上限（美元），默认 $0.20
        """
        self.api_key = api_key or os.getenv('TWITTERAPI_IO_KEY')
        if not self.api_key:
            raise ValueError("需要设置 TWITTERAPI_IO_KEY 环境变量或传入 api_key")

        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

        # 每日预算（从环境变量或参数读取）
        self.daily_budget = daily_budget or float(os.getenv('TWITTER_DAILY_BUDGET', DEFAULT_DAILY_BUDGET))

        # 统计
        self.request_count = 0
        self.tweet_count = 0
        self.budget_exceeded = False

    def _parse_twitter_time(self, time_str: str) -> Optional[datetime]:
        """
        解析 Twitter 时间格式
        支持:
        - ISO 格式: 2026-02-02T10:38:31Z
        - Twitter 格式: Mon Feb 02 10:38:31 +0000 2026
        """
        if not time_str:
            return None

        # 尝试 ISO 格式
        try:
            return datetime.fromisoformat(time_str.replace("Z", "+00:00")).replace(tzinfo=None)
        except:
            pass

        # 尝试 Twitter 格式: "Mon Feb 02 10:38:31 +0000 2026"
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(time_str).replace(tzinfo=None)
        except:
            pass

        # 尝试另一种 Twitter 格式
        try:
            return datetime.strptime(time_str, "%a %b %d %H:%M:%S %z %Y").replace(tzinfo=None)
        except:
            pass

        return None

    def _check_budget(self) -> bool:
        """检查是否超出预算"""
        current_cost = self.tweet_count * self.COST_PER_TWEET
        if current_cost >= self.daily_budget:
            if not self.budget_exceeded:
                print(f"\n⚠️  已达到每日预算上限 ${self.daily_budget:.2f}，停止收集")
                self.budget_exceeded = True
            return False
        return True

    def _get_remaining_budget(self) -> float:
        """获取剩余预算"""
        current_cost = self.tweet_count * self.COST_PER_TWEET
        return max(0, self.daily_budget - current_cost)

    def search_tweets(self, query: str, max_results: int = 100,
                     query_type: str = "Latest") -> List[Dict]:
        """
        搜索推文

        Args:
            query: 搜索查询（支持 Twitter 高级搜索语法）
                   例如: "stablecoin" 或 "from:circle USDC"
            max_results: 最大返回数量
            query_type: "Latest" 或 "Top"

        Returns:
            推文列表
        """
        url = f"{self.BASE_URL}/tweet/advanced_search"

        all_tweets = []
        cursor = None

        while len(all_tweets) < max_results:
            # 检查预算
            if not self._check_budget():
                break

            params = {
                "query": query,
                "queryType": query_type
            }
            if cursor:
                params["cursor"] = cursor

            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                self.request_count += 1

                if response.status_code != 200:
                    print(f"  ✗ API 错误: {response.status_code} - {response.text[:200]}")
                    break

                data = response.json()
                tweets = data.get("tweets", [])

                if not tweets:
                    break

                all_tweets.extend(tweets)
                self.tweet_count += len(tweets)

                # 获取下一页游标
                cursor = data.get("next_cursor")
                if not cursor:
                    break

                # 避免请求过快
                time.sleep(0.5)

            except Exception as e:
                print(f"  ✗ 请求失败: {e}")
                break

        return all_tweets[:max_results]

    def get_user_tweets(self, username: str, max_results: int = 50) -> List[Dict]:
        """
        获取指定用户的推文

        Args:
            username: Twitter 用户名（不带@）
            max_results: 最大返回数量

        Returns:
            推文列表
        """
        url = f"{self.BASE_URL}/user/last_tweets"

        # 检查预算
        if not self._check_budget():
            return []

        params = {
            "userName": username
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            self.request_count += 1

            if response.status_code != 200:
                print(f"  ✗ 获取 @{username} 失败: {response.status_code}")
                return []

            data = response.json()
            tweets = data.get("tweets", [])
            self.tweet_count += len(tweets)

            return tweets[:max_results]

        except Exception as e:
            print(f"  ✗ 获取 @{username} 失败: {e}")
            return []

    def normalize_tweet(self, tweet: Dict) -> Dict:
        """
        标准化推文数据格式，与现有系统兼容

        Args:
            tweet: TwitterAPI.io 返回的原始推文

        Returns:
            标准化后的推文数据
        """
        author = tweet.get("author", {})

        return {
            "id": tweet.get("id", ""),
            "text": tweet.get("text", ""),
            "created_at": tweet.get("createdAt", ""),
            "author_id": author.get("id", ""),
            "author_username": author.get("userName", ""),
            "author_name": author.get("name", ""),
            "author_followers": author.get("followers", 0),
            "author_verified": author.get("isBlueVerified", False),
            "likes": tweet.get("likeCount", 0),
            "retweets": tweet.get("retweetCount", 0),
            "replies": tweet.get("replyCount", 0),
            "quotes": tweet.get("quoteCount", 0),
            "views": tweet.get("viewCount", 0),
            "language": tweet.get("lang", "en"),
            "url": tweet.get("url", ""),
            "source": "twitter_api_io"
        }

    def collect_by_keywords(self, keywords: List[str],
                           max_per_keyword: int = 30,
                           hours_back: int = 24) -> List[Dict]:
        """
        按关键词列表收集推文

        Args:
            keywords: 关键词列表
            max_per_keyword: 每个关键词最大收集数
            hours_back: 回溯小时数（用于过滤）

        Returns:
            去重后的推文列表
        """
        print(f"🐦 TwitterAPI.io: 开始收集 {len(keywords)} 个关键词...")
        print(f"   💰 每日预算: ${self.daily_budget:.2f}")

        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        all_tweets = []
        seen_ids = set()

        for i, keyword in enumerate(keywords, 1):
            # 检查预算
            if not self._check_budget():
                print(f"   ⏭️  跳过剩余 {len(keywords) - i + 1} 个关键词")
                break

            print(f"  [{i}/{len(keywords)}] 搜索: '{keyword}'...", end=" ")

            tweets = self.search_tweets(keyword, max_results=max_per_keyword)

            # 去重和时间过滤
            new_count = 0
            for tweet in tweets:
                tweet_id = tweet.get("id")
                if tweet_id and tweet_id not in seen_ids:
                    # 检查时间
                    created_at = tweet.get("createdAt", "")
                    try:
                        tweet_time = self._parse_twitter_time(created_at)
                        if tweet_time and tweet_time >= cutoff_time:
                            seen_ids.add(tweet_id)
                            normalized = self.normalize_tweet(tweet)
                            normalized["search_keyword"] = keyword
                            all_tweets.append(normalized)
                            new_count += 1
                    except:
                        # 时间解析失败时仍保留推文（可能是最近的）
                        seen_ids.add(tweet_id)
                        normalized = self.normalize_tweet(tweet)
                        normalized["search_keyword"] = keyword
                        all_tweets.append(normalized)
                        new_count += 1

            print(f"✓ {new_count} 条")
            time.sleep(0.5)  # 避免请求过快

        return all_tweets

    def collect_by_accounts(self, accounts: List[str],
                           max_per_account: int = 20,
                           hours_back: int = 24) -> List[Dict]:
        """
        按账号列表收集推文，只保留指定时间范围内的推文（与日报“当日”一致，避免混入历史推文）。

        Args:
            accounts: 用户名列表
            max_per_account: 每个账号最大拉取数（API 返回最近 N 条，再按时间过滤）
            hours_back: 回溯小时数，只保留此时间内的推文

        Returns:
            推文列表
        """
        print(f"🐦 TwitterAPI.io: 收集 {len(accounts)} 个账号的推文（仅 {hours_back}h 内）...")

        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        all_tweets = []

        for i, username in enumerate(accounts, 1):
            # 检查预算
            if not self._check_budget():
                print(f"   ⏭️  跳过剩余 {len(accounts) - i + 1} 个账号")
                break

            print(f"  [{i}/{len(accounts)}] @{username}...", end=" ")

            tweets = self.get_user_tweets(username, max_results=max_per_account)
            new_count = 0

            for tweet in tweets:
                created_at = tweet.get("createdAt", "")
                try:
                    tweet_time = self._parse_twitter_time(created_at)
                    # 与 collect_by_keywords 一致：只保留 cutoff_time 之后的推文
                    if tweet_time and tweet_time < cutoff_time:
                        continue
                except Exception:
                    # 时间解析失败时仍保留（可能是最近的推文）
                    pass
                normalized = self.normalize_tweet(tweet)
                normalized["monitored_account"] = username
                all_tweets.append(normalized)
                new_count += 1

            print(f"✓ {new_count} 条")
            time.sleep(0.5)

        return all_tweets

    def collect_all(self, keywords: List[str], accounts: List[str],
                   hours_back: int = 24) -> Dict[str, List[Dict]]:
        """
        完整收集：关键词 + 账号

        Args:
            keywords: 关键词列表
            accounts: 监控账号列表
            hours_back: 回溯小时数

        Returns:
            {
                "keyword_tweets": [...],
                "account_tweets": [...],
                "all_tweets": [...]  # 去重合并
            }
        """
        print("=" * 60)
        print("🐦 TwitterAPI.io 数据收集")
        print("=" * 60 + "\n")

        # 收集关键词推文
        keyword_tweets = self.collect_by_keywords(keywords, hours_back=hours_back)
        print(f"\n📊 关键词推文: {len(keyword_tweets)} 条\n")

        # 收集账号推文（同样按 hours_back 过滤，避免 competitor 混入 12 月等历史推文）
        account_tweets = self.collect_by_accounts(accounts, hours_back=hours_back)
        print(f"\n📊 账号推文: {len(account_tweets)} 条\n")

        # 合并去重
        seen_ids = set()
        all_tweets = []

        for tweet in keyword_tweets + account_tweets:
            if tweet["id"] not in seen_ids:
                seen_ids.add(tweet["id"])
                all_tweets.append(tweet)

        current_cost = self.tweet_count * self.COST_PER_TWEET
        print("=" * 60)
        print(f"✅ 收集完成")
        print(f"   总推文: {len(all_tweets)} 条")
        print(f"   API 请求: {self.request_count} 次")
        print(f"   💰 本次成本: ${current_cost:.4f} / 预算 ${self.daily_budget:.2f}")
        if self.budget_exceeded:
            print(f"   ⚠️  已达预算上限，部分数据未收集")
        print("=" * 60 + "\n")

        return {
            "keyword_tweets": keyword_tweets,
            "account_tweets": account_tweets,
            "all_tweets": all_tweets
        }


# 测试代码
if __name__ == "__main__":
    # 测试收集器
    collector = TwitterAPIioCollector()

    # 测试搜索
    tweets = collector.search_tweets("stablecoin USDC", max_results=5)
    print(f"搜索结果: {len(tweets)} 条")

    if tweets:
        print("\n第一条推文:")
        normalized = collector.normalize_tweet(tweets[0])
        print(json.dumps(normalized, indent=2, ensure_ascii=False))
