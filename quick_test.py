# quick_test.py

from src.collectors.data_normalizer import DataNormalizer
import json

# 初始化
normalizer = DataNormalizer()

# 快速测试Twitter标准化
print("🐦 测试Twitter标准化...")
tweet = {
    'id': '123',
    'text': 'Circle launches USDC in Singapore',
    'author_username': 'circle',
    'created_at': '2025-01-17T10:00:00Z',
    'public_metrics': {'like_count': 100, 'retweet_count': 50, 'reply_count': 10},
    'quality_score': 80
}
result = normalizer.normalize_tweet(tweet)
print(f"✅ Twitter: {result['title']}")
print(f"   类型: {result['source_type']}")
print(f"   互动: {result['engagement']}")

# 快速测试News标准化
print("\n📰 测试News标准化...")
news = {
    'title': 'SEC Approves Stablecoin Rules',
    'url': 'https://example.com/article',
    'source': {'name': 'Reuters'},
    'publishedAt': '2025-01-17T09:00:00Z'
}
result = normalizer.normalize_news(news)
print(f"✅ News: {result['title']}")
print(f"   类型: {result['source_type']}")
print(f"   来源: {result['source']}")

# 测试合并
print("\n🔄 测试合并去重...")
items = [
    normalizer.normalize_tweet(tweet),
    normalizer.normalize_news(news)
]
merged = normalizer.merge_and_deduplicate(items)
print(f"✅ 合并结果: {len(merged)} 条")

print("\n🎉 所有快速测试通过!")