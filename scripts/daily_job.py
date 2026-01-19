# scripts/daily_job.py

"""
每日自动任务：收集新闻 + 整合数据
"""

import json
import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.collectors.news_collector import NewsCollector
from src.collectors.twitter_filter import TwitterFilter
from src.collectors.data_normalizer import DataNormalizer

def daily_news_collection():
    """每日新闻收集任务"""
    
    print("=" * 70)
    print(f"📅 每日任务开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # ===== Step 1: 收集NewsAPI数据 =====
    print("🔍 Step 1: 收集新闻数据...")
    collector = NewsCollector()
    articles = collector.collect_news(days_back=1)  # 只收集最近1天
    
    if not articles:
        print("⚠️  没有收集到新闻数据")
        return
    
    # 保存原始数据
    raw_file = f'data/raw/newsapi_raw_{date_str}.json'
    os.makedirs('data/raw', exist_ok=True)
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"✅ 原始数据已保存: {raw_file}\n")
    
    # ===== Step 2: 分类新闻 =====
    print("🏷️  Step 2: 分类新闻...")
    
    categorized_news = {
        'policy': [],
        'company': [],
        'funding': [],
        'market': [],
        'general': []
    }
    
    # 简单分类（基于标题和描述）
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
        
        # 添加到主要类别
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
    
    # ===== Step 3: 数据整合（如果有Twitter数据）=====
    print("🔄 Step 3: 整合数据...")
    
    # 加载Twitter数据（如果存在）
    twitter_file = f'data/raw/twitter_data_{date_str}.json'
    if os.path.exists(twitter_file):
        with open(twitter_file, 'r') as f:
            raw_tweets = json.load(f)
        print(f"✅ 加载Twitter数据: {len(raw_tweets)} 条")
        
        # 筛选Twitter数据
        filter = TwitterFilter()
        filtered_tweets = filter.filter_tweets(raw_tweets, min_score=60)
        enriched_tweets = [filter.enrich_tweet_data(t) for t in filtered_tweets]
    else:
        print("⚠️  未找到Twitter数据，跳过")
        enriched_tweets = []
    
    # 标准化数据
    normalizer = DataNormalizer()
    normalized_tweets = [normalizer.normalize_tweet(t) for t in enriched_tweets]
    
    # 标准化新闻（从categorized_news中提取）
    all_news = []
    for articles_list in categorized_news.values():
        all_news.extend(articles_list)
    normalized_news = [normalizer.normalize_news(n) for n in all_news]
    
    # 合并去重
    all_items = normalized_tweets + normalized_news
    merged_items = normalizer.merge_and_deduplicate(all_items)
    
    # 保存整合数据
    integrated_data = {
        'date': date_str,
        'total_items': len(merged_items),
        'by_source': {
            'twitter': len([i for i in merged_items if i['source_type'] == 'twitter']),
            'news': len([i for i in merged_items if i['source_type'] == 'news'])
        },
        'items': merged_items
    }
    
    integrated_file = f'data/processed/integrated_data_{date_str}.json'
    with open(integrated_file, 'w', encoding='utf-8') as f:
        json.dump(integrated_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 整合数据已保存: {integrated_file}")
    print(f"   总计: {len(merged_items)} 条\n")
    
    # ===== 完成 =====
    print("=" * 70)
    print(f"✅ 每日任务完成 - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    print(f"\n📊 今日数据汇总:")
    print(f"   新闻: {len(articles)} 篇")
    print(f"   Twitter: {len(enriched_tweets)} 条")
    print(f"   整合后: {len(merged_items)} 条")
    print(f"\n💾 输出文件:")
    print(f"   - {raw_file}")
    print(f"   - {categorized_file}")
    print(f"   - {integrated_file}")

if __name__ == '__main__':
    daily_news_collection()