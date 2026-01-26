# src/collectors/content_filter.py
"""
内容质量过滤器
- 跨数据源去重
- Twitter 内容质量过滤（业务视角）
"""

import re
import json
import os
from typing import List, Dict, Set, Tuple
from datetime import datetime


class ContentFilter:
    """
    从业务负责人视角过滤内容
    目标：保留对销售、BD、品牌、市场有价值的信息
    """

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self._build_patterns()

    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置"""
        if config_path is None:
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'keywords.json'),
                os.path.join(os.getcwd(), 'config', 'keywords.json'),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _build_patterns(self):
        """构建过滤规则"""

        # ========== 排除模式（低价值内容）==========
        self.exclude_patterns = [
            # 促销/抽奖
            r'\b(giveaway|airdrop|free\s+(tokens?|coins?|crypto)|win\s+\$|抽奖|送币|空投)\b',
            # 价格喊单
            r'\b(to\s+the\s+moon|100x|1000x|pump|dump|买入|卖出|抄底|all\s+in)\b',
            # 纯情绪/社交
            r'^(gm|gn|lfg|wagmi|ngmi|gmi)\s*[!.]*$',
            r'^(lol|lmao|rofl|haha)\s*$',
            # 过多表情（3个以上火箭/火等）
            r'(🚀|🔥|💰|🎉|💎|🙌){3,}',
            # 求关注
            r'\b(follow\s+(me|us)|like\s+and\s+(rt|retweet)|转发|关注)\b',
            # C端促销活动（交易所）
            r'\b(trading\s+competition|deposit\s+bonus|refer\s+a\s+friend|新用户|注册送|充值送)\b',
            # 无意义转发
            r'^RT\s+@',
        ]

        # ========== 保留模式（高价值内容）==========
        self.include_patterns = [
            # 产品更新
            r'\b(launch(ed|ing)?|announce(d|ment)?|release(d)?|update(d)?|upgrade(d)?|新功能|发布|上线|推出)\b',
            # 合作消息
            r'\b(partner(ship)?|collaborat(e|ion)|integrat(e|ion|ed)|支持|合作|集成|接入)\b',
            # 融资消息
            r'\b(rais(e|ed|ing)|funding|series\s+[a-d]|investment|融资|投资|估值)\b',
            # 监管消息
            r'\b(regulat(ion|ory|ed)|license|compliance|approv(e|ed|al)|ban(ned)?|监管|牌照|合规|批准)\b',
            # 重要数据/里程碑
            r'\b(market\s+cap|volume|tvl|billion|million|milestone|市值|交易量|里程碑)\b',
            # 战略动向
            r'\b(acqui(re|sition)|merg(e|er)|expansion|战略|收购|合并|扩张)\b',
            # 上币/下架
            r'\b(list(ing|ed)|delist(ing|ed)|上线|下架)\b',
        ]

        # ========== 官方账号（无条件保留）==========
        self.official_accounts = set()
        categories = self.config.get('categories', {})

        # 竞争对手官方账号
        for company in categories.get('competitors', {}).get('companies', []):
            if company.get('twitter'):
                self.official_accounts.add(company['twitter'].lower())

        # 客户官方账号
        for company in categories.get('clients', {}).get('companies', []):
            if company.get('twitter'):
                self.official_accounts.add(company['twitter'].lower())

        # 媒体账号
        for acc in self.config.get('twitter_accounts', {}).get('media', []):
            if acc.get('username'):
                self.official_accounts.add(acc['username'].lower())

        # ========== KOL 账号（需要业务相关）==========
        self.kol_accounts = set()
        for acc in self.config.get('twitter_accounts', {}).get('kol', []):
            if acc.get('username'):
                self.kol_accounts.add(acc['username'].lower())

        # ========== 互动阈值 ==========
        self.engagement_thresholds = {
            'official': 0,      # 官方账号无门槛
            'media': 5,         # 媒体至少5个赞
            'kol': 10,          # KOL 至少10个赞
            'other': 30,        # 其他账号至少30个赞
        }

    def _get_account_type(self, username: str) -> str:
        """判断账号类型"""
        username_lower = username.lower()

        if username_lower in self.official_accounts:
            return 'official'
        if username_lower in self.kol_accounts:
            return 'kol'

        # 检查是否是媒体
        media_keywords = ['news', 'crypto', 'coin', 'block', 'defi', 'telegraph', 'decrypt', 'messari']
        if any(kw in username_lower for kw in media_keywords):
            return 'media'

        return 'other'

    def _matches_exclude_pattern(self, text: str) -> bool:
        """检查是否匹配排除模式"""
        text_lower = text.lower()
        for pattern in self.exclude_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    def _matches_include_pattern(self, text: str) -> bool:
        """检查是否匹配保留模式"""
        text_lower = text.lower()
        for pattern in self.include_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    def _get_engagement(self, item: Dict) -> int:
        """获取互动数"""
        # Twitter 格式
        if 'likes' in item:
            return item.get('likes', 0) + item.get('retweets', 0) * 2

        # 标准化格式
        engagement = item.get('engagement', {})
        if isinstance(engagement, dict):
            return engagement.get('likes', 0) + engagement.get('retweets', 0) * 2

        return 0

    def filter_tweet(self, tweet: Dict) -> Tuple[bool, str]:
        """
        过滤单条推文

        Returns:
            (是否保留, 原因)
        """
        text = tweet.get('text', tweet.get('description', ''))
        username = tweet.get('author_username', '')
        account_type = self._get_account_type(username)
        engagement = self._get_engagement(tweet)

        # 1. 检查排除模式
        if self._matches_exclude_pattern(text):
            # 官方账号例外
            if account_type != 'official':
                return False, "匹配排除模式（促销/喊单/情绪）"

        # 2. 检查互动阈值
        min_engagement = self.engagement_thresholds.get(account_type, 30)
        if engagement < min_engagement:
            # 如果匹配高价值模式，降低门槛
            if self._matches_include_pattern(text):
                min_engagement = min_engagement // 2

            if engagement < min_engagement:
                return False, f"互动不足（{engagement}<{min_engagement}）"

        # 3. 对于 KOL，需要匹配业务相关模式
        if account_type == 'kol':
            if not self._matches_include_pattern(text):
                # 检查是否太短（可能是闲聊）
                if len(text) < 100:
                    return False, "KOL 闲聊内容"

        # 4. 对于其他账号，必须匹配高价值模式
        if account_type == 'other':
            if not self._matches_include_pattern(text):
                return False, "非高价值内容"

        return True, f"保留（{account_type}）"

    def filter_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """
        批量过滤推文

        Returns:
            过滤后的推文列表
        """
        filtered = []
        stats = {'total': len(tweets), 'kept': 0, 'excluded': {}}

        for tweet in tweets:
            keep, reason = self.filter_tweet(tweet)

            if keep:
                tweet['filter_reason'] = reason
                filtered.append(tweet)
                stats['kept'] += 1
            else:
                stats['excluded'][reason] = stats['excluded'].get(reason, 0) + 1

        # 打印统计
        print(f"\n🔍 Twitter 质量过滤:")
        print(f"   输入: {stats['total']} 条")
        print(f"   保留: {stats['kept']} 条 ({stats['kept']/max(stats['total'],1)*100:.0f}%)")
        if stats['excluded']:
            print(f"   排除原因:")
            for reason, count in sorted(stats['excluded'].items(), key=lambda x: -x[1])[:5]:
                print(f"      - {reason}: {count} 条")

        return filtered

    def deduplicate(self, items: List[Dict]) -> List[Dict]:
        """
        跨数据源去重

        基于:
        1. URL 完全匹配
        2. 标题/内容前60字符相似
        """
        seen_urls: Set[str] = set()
        seen_content: Set[str] = set()
        unique_items = []

        for item in items:
            # URL 去重
            url = item.get('url', '')
            if url and url in seen_urls:
                continue

            # 内容去重（取标题或文本的前60字符）
            title = item.get('title', '')
            text = item.get('text', item.get('description', ''))
            content_key = (title or text)[:60].lower().strip()

            # 移除特殊字符
            content_key = re.sub(r'[^\w\s]', '', content_key)

            if content_key and content_key in seen_content:
                continue

            if url:
                seen_urls.add(url)
            if content_key:
                seen_content.add(content_key)

            unique_items.append(item)

        removed = len(items) - len(unique_items)
        if removed > 0:
            print(f"🔄 去重: 移除 {removed} 条重复内容")

        return unique_items

    def process_all(self, news: List[Dict], tweets: List[Dict]) -> List[Dict]:
        """
        完整处理流程：过滤 + 去重

        Args:
            news: NewsAPI 新闻列表
            tweets: Twitter 推文列表

        Returns:
            处理后的合并列表
        """
        print("\n" + "=" * 60)
        print("🧹 内容质量过滤")
        print("=" * 60)

        # 1. 过滤 Twitter
        filtered_tweets = self.filter_tweets(tweets)

        # 2. 合并
        all_items = news + filtered_tweets

        # 3. 去重
        unique_items = self.deduplicate(all_items)

        print(f"\n📊 最终结果: {len(unique_items)} 条")
        print(f"   新闻: {len(news)} 条")
        print(f"   推文: {len(filtered_tweets)} 条（原 {len(tweets)} 条）")
        print("=" * 60 + "\n")

        return unique_items


# 测试
if __name__ == "__main__":
    filter = ContentFilter()

    test_tweets = [
        {"text": "🚀🚀🚀 USDC to the moon! 100x coming!", "author_username": "random_user", "likes": 5},
        {"text": "Circle announces new cross-chain USDC support for Ethereum L2s", "author_username": "circle", "likes": 100},
        {"text": "gm frens", "author_username": "jerallaire", "likes": 50},
        {"text": "We're excited to announce our partnership with Visa for stablecoin settlements", "author_username": "circle", "likes": 500},
        {"text": "Free airdrop! Follow and RT to win $1000 USDC", "author_username": "crypto_giveaway", "likes": 1000},
    ]

    filtered = filter.filter_tweets(test_tweets)
    print(f"\n保留 {len(filtered)} 条:")
    for t in filtered:
        print(f"  - @{t['author_username']}: {t['text'][:50]}...")
