# scripts/daily_job_simple.py

"""
简化版每日任务：只收集和分类新闻数据
"""

import json
import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 检查是否使用模拟数据
USE_MOCK_DATA = '--mock' in sys.argv or os.path.exists(os.path.join(project_root, 'USE_MOCK_MODE'))

def simple_daily_job():
    """简化的每日任务 - 只收集和分类新闻"""
    
    print("=" * 70)
    print(f"📅 简化版每日任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    raw_file = f'data/raw/newsapi_raw_{date_str}.json'
    
    # ===== Step 1: 收集新闻数据 =====
    print("🔍 Step 1: 收集新闻数据...")
    
    if USE_MOCK_DATA:
        print("⚠️  使用模拟数据模式")
        # 使用模拟数据
        if os.path.exists(raw_file):
            print(f"📂 加载现有模拟数据: {raw_file}")
            with open(raw_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
        else:
            print("🎲 生成新的模拟数据...")
            from mock_news_collector import generate_realistic_news
            articles = generate_realistic_news()
            os.makedirs('data/raw', exist_ok=True)
            with open(raw_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            print(f"✅ 模拟数据已保存: {raw_file}\n")
    else:
        # 使用真实API
        from src.collectors.news_collector import NewsCollector
        collector = NewsCollector()
        articles = collector.collect_news(days_back=1)
        
        if not articles:
            print("⚠️  没有收集到新闻数据")
            return
        
        os.makedirs('data/raw', exist_ok=True)
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"✅ 原始数据已保存: {raw_file}\n")
    
    # ===== Step 2: 简单分类 =====
    print("🏷️  Step 2: 分类新闻...")
    
    categorized_news = {
        'policy': [],
        'company': [],
        'funding': [],
        'market': [],
        'general': []
    }
    
    for article in articles:
        text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        
        categories = []
        if any(kw in text for kw in ['regulation', 'ban', 'license', 'law', 'sec', 'compliance']):
            categories.append('policy')
        if any(kw in text for kw in ['partnership', 'launch', 'acquisition', 'expands', 'announces']):
            categories.append('company')
        if any(kw in text for kw in ['funding', 'raises', 'investment', 'million', 'billion']):
            categories.append('funding')
        if any(kw in text for kw in ['market', 'price', 'volume', 'trading', 'cap']):
            categories.append('market')
        
        if not categories:
            categories = ['general']
        
        article['categories'] = categories
        main_category = categories[0]
        categorized_news[main_category].append(article)
    
    # 保存分类数据
    categorized_file = f'data/processed/categorized_news_{date_str}.json'
    os.makedirs('data/processed', exist_ok=True)
    with open(categorized_file, 'w', encoding='utf-8') as f:
        json.dump(categorized_news, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 分类数据已保存: {categorized_file}")
    print(f"   分布: policy={len(categorized_news['policy'])}, "
          f"company={len(categorized_news['company'])}, "
          f"funding={len(categorized_news['funding'])}, "
          f"market={len(categorized_news['market'])}\n")
    
    # ===== 完成 =====
    print("=" * 70)
    print(f"✅ 任务完成 - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    print(f"\n📊 数据汇总:")
    print(f"   新闻: {len(articles)} 篇")
    print(f"\n💾 输出文件:")
    print(f"   - {raw_file}")
    print(f"   - {categorized_file}")

if __name__ == '__main__':
    simple_daily_job()
