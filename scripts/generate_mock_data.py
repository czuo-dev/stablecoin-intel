import json
from datetime import datetime, timedelta
import random
import os

def generate_mock_tweets(count=20):
    """生成模拟Twitter数据"""
    
    accounts = [
        {'username': 'circle', 'verified': True, 'followers': 500000},
        {'username': 'Tether_to', 'verified': True, 'followers': 800000},
        {'username': 'paxos', 'verified': True, 'followers': 200000},
        {'username': 'coinbase', 'verified': True, 'followers': 5000000},
        {'username': 'MessariCrypto', 'verified': True, 'followers': 300000},
    ]
    
    templates = [
        "BREAKINGB #USDT",
        "Singapore MAS approves new stablecoin framework. Big win for crypto adoption in Asia!",
        "PayPal PYUSD reaches $1B market cap. Impressive growth in just 6 months.",
        "EU MiCA regulations taking effect next month. Stablecoin issuers must comply by Feb 2025.",
        "Breaking: Coinbase partners with Visa for USDC settlement. Real-time payments now live.",
        "SEC charges crypto firm for unregistered stablecoin offering. $50M penalty imposed.",
        "Hong Kong regulatory sandbox welcomes 3 new stablecoin issuers. HKD stablecoins coming soon.",
        "Stablecoin trading volume hits record $100B in 24 hours. USDT dominates with 65% share.",
        "IMF report: Stablecoins pose systemic risk if not properly regulated. Calls for global standards.",
    ]
    
    regions = ['Singapore', 'Hong Kong', 'United States', 'Europe', 'Latin America']
    categories_options = [
        ['policy'],
        ['company'],
        ['funding'],
        ['market'],
        ['policy', 'company'],
    ]
    coins = ['USDC', 'USDT', 'PYUSD', 'DAI', 'BUSD']
    
    tweets = []
    base_time = datetime.now() - timedelta(hours=12)
    
    for i in range(count):
        account = random.choice(accounts)
        template = random.choice(templates)
        region = random.choice(regions)
        
        tweet = {
            'id': str(1234567890 + i),
            'text': template.format(region=region) if '{region}' in template else template,
            'author_username': account['username'],
            'author_verified': account['verified'],
            'author_followers': account['followers'],
            'created_at': (base_time + timedelta(minutes=i*30)).isoformat() + 'Z',
            'public_metrics': {
                'like_count': random.randint(50, 2000),
                'retweet_count': random.randint(20, 800),
                'reply_count': random.randint(5, 200)
            },
            'categories': random.choice(categories_options),
            'regions': [region],
            'mentioned_stablecoins': random.sample(coins, random.randint(1, 3)),
            'quality_score': random.randint(60, 95),
            'url': f'https://twitter.com/{account["username"]}/status/{1234567890 + i}'
        }
        tweets.append(tweet)
    
    return tweets

def generate_mock_news(count=30):
    """生成模拟NewsAPI数据"""
    
    sources = ['Reuters', 'Bloomberg', 'CoinDesk', 'The Block', 'Decrypt']
    
    articles_templates = [
        {
            'title': 'Circle Receives Payment Institution License in Singapore',
            'description': 'Circle Internet Financial has obtained a Major Payment Institution license from MAS.',
            'category': 'company',
            'region': 'Asia',
            'coins': ['USDC']
        },
        {
            'title': 'Tether Reports $1.5B Profit in Q3 2024',
            'description': 'Stablecoin issuer Tether announced record quarterly profits driven by Treasury yields.',
            'category': 'company',
            'region': 'Global',
            'coins': ['USDT']
        },
        {
            'title': 'US House Passes Stablecoin Regulation Bill',
            'description': 'The CLARITY Act establishes federal framework for stablecoin issuers in the United States.',
            'category': 'policy',
            'region': 'US',
            'coins': ['USDC', 'USDT']
        },
        {
            'title': 'European Central Bank Warns on Stablecoin Risks',
            'description': 'ECB publishes report highlighting potential financial stability risks.',
            'category': 'policy',
            'region': 'EU',
            'coins': []
        },
        {
            'title': 'Visa Expands USDC Settlement to 50+ Countries',
            'description': 'Payment giant Visa announces major expansion of its stablecoin settlement capabilities.',
            'category': 'company',
            'region': 'Global',
            'coins': ['USDC']
        },
    ]
    
    articles = []
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(count):
        template = random.choice(articles_templates)
        source = random.choice(sources)
        
        article = {
            'title': template['title'],
            'description': template['description'],
            'content': template['description'] + ' Full article content here...',
            'url': f'https://example.com/article-{i}',
            'source': {'name': source},
            'author': 'Staff Writer',
            'publishedAt': (base_time + timedelta(hours=i)).isoformat() + 'Z',
            'categories': [template['category']],
            'regions': [template['region']],
            'mentioned_coins': template['coins'],
            'relevance_score': random.randint(60, 98)
        }
        articles.append(article)
    
    return articles

def save_mock_data(date_str=None):
    """保存模拟数据到文件"""
    
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    tweets = generate_mock_tweets(20)
    news = generate_mock_news(30)
    news_by_category = {
        'policy': [n for n in news if 'policy' in n.get('categories', [])],
        'company': [n for n in news if 'company' in n.get('categories', [])],
        'funding': [n for n in news if 'funding' in n.get('categories', [])],
        'market': [n for n in news if 'market' in n.get('categories', [])],
        'general': []
    }
    
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    twitter_file = f'data/raw/twitter_data_{date_str}.json'
    with open(twitter_file, 'w', encoding='utf-8') as f:
        json.dump(tweets, f, indent=2, ensure_ascii=False)
    print(f"✅ Twitter数据: {twitter_file} ({len(tweets)} 条)")
    
    news_file = f'data/processed/categorized_news_{date_str}.json'
    with open(news_file, 'w', encoding='utf-8') as f:
        json.dump(news_by_category, f, indent=2, ensure_ascii=False)
    print(f"✅ 新闻数据: {news_file} ({len(news)} 条)")
    
    return twitter_file, news_file

if __name__ == '__main__':
    twitter_file, news_file = save_mock_data()
    print(f"\n✅ 完成! 现在运行: python scripts/integrate_data.py")
