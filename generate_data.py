import json
import os

print("正在生成测试数据...")

# 创建目录
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

date_str = '2026-01-17'

# Twitter数据
tweets = []
for i in range(20):
    tweet = {
        'id': str(1234567890 + i),
        'text': 'Breaking: Circle announces USDC expansion. Major regulatory approval received.',
        'author_username': 'circle',
        'author_verified': True,
        'author_followers': 500000,
        'created_at': '2026-01-17T10:00:00Z',
        'public_metrics': {
            'like_count': 1000,
            'retweet_count': 200,
            'reply_count': 50
        },
        'categories': ['company'],
        'regions': ['Singapore'],
        'mentioned_stablecoins': ['USDC'],
        'quality_score': 80,
        'url': 'https://twitter.com/circle/status/123'
    }
    tweets.append(tweet)

twitter_file = 'data/raw/twitter_data_2026-01-17.json'
with o as f:
    json.dump(tweets, f, indent=2)
print(f"Twitter数据: {twitter_file} - {len(tweets)}条")

# 新闻数据
news_by_category = {
    'policy': [
        {
            'title': 'US House Passes Stablecoin Bill',
            'description': 'New regulations approved',
            'content': 'Full content here',
            'url': 'https://example.com/1',
            'source': {'name': 'Reuters'},
            'author': 'John Smith',
            'publishedAt': '2026-01-17T09:00:00Z',
            'categories': ['policy'],
            'regions': ['US'],
            'mentioned_coins': ['USDC'],
            'relevance_score': 95
        }
    ],
    'company': [
        {
            'title': 'Circle Singapore License',
            'description': 'MAS approval received',
            'content': 'Full content here',
            'url': 'https://example.com/2',
            'source': {'name': 'Bloomberg'},
            'author': 'Jane Doe',
            'publishedAt': '2026-01-17T08:00:00Z',
            'categorie],
            'regions': ['Asia'],
            'mentioned_coins': ['USDC'],
            'relevance_score': 90
        }
    ],
    'funding': [],
    'market': [],
    'general': []
}

news_file = 'data/processed/categorized_news_2026-01-17.json'
with open(news_file, 'w', encoding='utf-8') as f:
    json.dump(news_by_category, f, indent=2)

total = sum(len(v) for v in news_by_category.values())
print(f"新闻数据: {news_file} - {total}条")

print("\n数据生成完成!")
print("现在运行: python scripts/integrate_data.py")
