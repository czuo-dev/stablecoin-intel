"""
纯模拟版每日任务 - 完全不调用真实API
"""

import json
import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.collectors.twitter_filter import TwitterFilter
from src.collectors.data_normalizer import DataNormalizer

def daily_news_collection():
    """每日新闻收集任务（纯模拟数据）"""
    
    print("=" * 70)
    print(f"📅 纯模拟版每日任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # ===== Step 1: 读取模拟新闻数据 =====
    print("📂 Step 1: 读取模拟新闻数据...")
    
    raw_file = f'data/raw/newsapi_raw_{date_str}.json'
    
    # 检查文件是否存在
    if not os.path.exists(raw_file):
        print(f"❌ 模拟数据不存在: {raw_file}")
        print("   请先运行: python mock_news_collector.py")
        return
    
    # 读取数据
    with open(raw_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print(f"✅ 加载了 {len(articles)} 篇新闻\n")
    
    # ===== Step 2: 分类新闻 =====
    print("🏷️  Step 2: 分类新闻...")
    
    categorized_news = {
        'policy': [],
        'company': [],
        'funding': [],
        'market': [],
        'general': []
    }
    
    # 使用已有的categories字段分类
    for article in articles:
        categories = article.get('categories', ['general'])
        main_category = categories[0]
        
        if main_category in categorized_news:
            categorized_news[main_category].append(article)
        else:
            categorized_news['general'].append(article)
    
    # 保存分类数据
    os.makedirs('data/processed', exist_ok=True)
    categorized_file = f'data/processed/categorized_news_{date_str}.json'
    
    with open(categorized_file, 'w', encoding='utf-8') as f:
        json.dump(categorized_news, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 分类完成: {categorized_file}")
    
    # 显示分布
    for category, items in categorized_news.items():
        if items:
            print(f"   {category}: {len(items)} 篇")
    print()
    
    # ===== Step 3: 数据整合 =====
    print("🔄 Step 3: 数据整合...")
    
    # 尝试加载Twitter数据（如果存在）
    twitter_file = f'data/raw/twitter_data_{date_str}.json'
    enriched_tweets = []
    
    if os.path.exists(twitter_file):
        with open(twitter_file, 'r', encoding='utf-8') as f:
            raw_tweets = json.load(f)
        print(f"   找到Twitter数据: {len(raw_tweets)} 条")
        
        # 筛选Twitter数据
        try:
            filter_obj = TwitterFilter()
            filtered_tweets = filter_obj.filter_tweets(raw_tweets, min_score=60)
            enriched_tweets = [filter_obj.enrich_tweet_data(t) for t in filtered_tweets]
            print(f"   筛选后: {len(enriched_tweets)} 条")
        except Exception as e:
            print(f"   Twitter筛选失败: {e}")
    else:
        print(f"   未找到Twitter数据，跳过")
    
    # 标准化数据
    normalizer = DataNormalizer()
    
    normalized_tweets = [normalizer.normalize_tweet(t) for t in enriched_tweets]
    
    # 标准化新闻（从categorized_news中提取）
    all_news = []
    for articles_list in categorized_news.values():
        all_news.extend(articles_list)
    
    normalized_news = [normalizer.normalize_news(n) for n in all_news]
    
    print(f"   标准化: Twitter {len(normalized_tweets)} 条, News {len(normalized_news)} 条")
    
    # 合并去重
    all_items = normalized_tweets + normalized_news
    merged_items = normalizer.merge_and_deduplicate(all_items)
    
    print(f"   合并去重: {len(merged_items)} 条")
    
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
    
    print(f"✅ 整合完成: {integrated_file}\n")
    
    # ===== 完成汇总 =====
    print("=" * 70)
    print(f"✅ 任务完成 - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    
    print(f"\n📊 数据汇总:")
    print(f"   原始新闻: {len(articles)} 篇")
    print(f"   Twitter: {len(enriched_tweets)} 条")
    print(f"   整合后: {len(merged_items)} 条")
    
    print(f"\n💾 生成文件:")
    print(f"   1. {raw_file}")
    print(f"   2. {categorized_file}")
    print(f"   3. {integrated_file}")
    
    # 显示Top 5标题
    print(f"\n📰 Top 5 新闻标题:")
    for i, item in enumerate(merged_items[:5], 1):
        print(f"   {i}. {item['title'][:65]}...")

if __name__ == '__main__':
    daily_news_collection()
