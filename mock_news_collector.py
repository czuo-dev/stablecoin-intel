import json
from datetime import datetime, timedelta
import random
import os

def generate_realistic_news():
    """生成逼真的新闻数据"""
    
    print("=" * 60)
    print("🎲 生成模拟NewsAPI数据（用于测试）")
    print("=" * 60 + "\n")
    
    sources = {
        'high': ['Bloomberg', 'Reuters', 'Wall Street Journal', 'Financial Times'],
        'medium': ['CoinDesk', 'The Block', 'Decrypt', 'Cointelegraph']
    }
    
    news_templates = [
        {
            'title': 'Circle Secures Payment Institution License in Singapore',
            'description': 'Circle Internet Financial has been granted a Major Payment Institution license by the Monetary Authority of Singapore (MAS).',
            'category': 'company',
            'region': 'Asia',
            'coins': ['USDC'],
            'priority': 'high'
        },
        {
            'title': 'US House Financial Services Committee Advances Stablecoin Bill',
            'description': 'US House advances federal framework for stablecoin regulation.',
            'category': 'policy',
            'region': 'US',
            'coins': ['USDC', 'USDT'],
            'priority': 'high'
        },
        {
            'title': 'Tether Reports Record $5.2B Net Profit in 2024',
            'description': 'Stablecoin issuer Tether announces record annual profits driven by US Treasury yields.',
            'category': 'company',
            'region': 'Global',
            'coins': ['USDT'],
            'priority': 'high'
        },
        {
            'title': 'ECB Publishes Stablecoin Risk Assessment Report',
            'description': 'European Central Bank warns about potential systemic risks from widespread stablecoin adoption.',
            'category': 'policy',
            'region': 'EU',
            'coins': [],
            'priority': 'medium'
        },
        {
            'title': 'Visa Expands USDC Settlement to 60+ Countries',
            'description': 'Payment giant Visa announces major expansion of stablecoin settlement capabilities.',
            'category': 'company',
            'region': 'Global',
            'coins': ['USDC'],
            'priority': 'high'
        },
        {
            'title': 'Hong Kong Launches HKD Stablecoin Sandbox Program',
            'description': 'HKMA invites licensed institutions to participate in pilot program for Hong Kong dollar stablecoins.',
            'category': 'policy',
            'region': 'Asia',
            'coins': [],
            'priority': 'medium'
        },
        {
            'title': 'Paxos Expands Stablecoin to Solana and Polygon',
            'description': 'Regulated stablecoin issuer Paxos launches USDP on additional blockchain networks.',
            'category': 'company',
            'region': 'US',
            'coins': ['USDP'],
            'priority': 'medium'
        },
        {
            'title': 'Global Stablecoin Market Cap Surpasses $180 Billion',
            'description': 'Total stablecoin market capitalization reaches new all-time high amid institutional adoption.',
            'category': 'market',
            'region': 'Global',
            'coins': ['USDC', 'USDT'],
            'priority': 'medium'
        },
        {
            'title': 'Brazil Approves First Licensed Stablecoin Issuer',
            'description': 'Brazilian Central Bank grants approval to local fintech for BRL-backed stablecoin issuance.',
            'category': 'policy',
            'region': 'LATAM',
            'coins': [],
            'priority': 'medium'
        },
        {
            'title': 'IMF Proposes Global Stablecoin Regulatory Framework',
            'description': 'International Monetary Fund calls for coordinated international approach to stablecoin regulation.',
            'category': 'policy',
            'region': 'Global',
            'coins': [],
            'priority': 'high'
        },
    ]
    
    articles = []
    base_time = datetime.now() - timedelta(hours=24)
    
    # 生成40篇新闻
    for i in range(40):
        template = random.choice(news_templates)
        source_quality = random.choice(['high', 'high', 'medium'])  # 偏向高质量
        source = random.choice(sources[source_quality])
        
        article = {
            'title': template['title'],
            'description': template['description'],
            'content': template['description'] + ' [Full article content would be here...]',
            'url': f'https://example.com/news/{i}',
            'source': {
                'name': source,
                'id': source.lower().replace(' ', '-')
            },
            'author': random.choice(['John Smith', 'Jane Doe', 'Staff Writer', 'Editorial Team']),
            'publishedAt': (base_time + timedelta(hours=i*0.5)).isoformat() + 'Z',
            'categories': [template['category']],
            'regions': [template['region']],
            'mentioned_coins': template['coins'],
            'relevance_score': random.randint(75, 98),
            'priority_weight': 1.5 if template['priority'] == 'high' else 1.0,
            'search_keyword': random.choice([
                'stablecoin regulation',
                'USDC Circle',
                'Tether USDT',
                'stablecoin market',
                'PayPal PYUSD'
            ]),
            'source_quality': source_quality
        }
        articles.append(article)
    
    print(f"✅ 生成 {len(articles)} 篇新闻")
    
    # 统计
    by_category = {}
    for article in articles:
        cat = article['categories'][0]
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print(f"\n📊 分类统计:")
    for cat, count in by_category.items():
        print(f"   {cat}: {count} 篇")
    
    return articles

def save_mock_data():
    """保存模拟数据"""
    
    articles = generate_realistic_news()
    
    # 创建目录
    os.makedirs('data/raw', exist_ok=True)
    
    # 保存
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_file = f'data/raw/newsapi_raw_{date_str}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 数据已保存: {output_file}")
    print(f"\n现在可以运行: python scripts/daily_job.py")
    
    return output_file

if __name__ == '__main__':
    save_mock_data()
