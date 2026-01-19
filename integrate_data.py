# scripts/integrate_data.py

import json
from datetime import datetime
from src.collectors.twitter_filter import TwitterFilter
from src.collectors.data_normalizer import DataNormalizer

def integrate_all_data(date_str: str = None):
    """
    整合所有数据源
    
    Args:
        date_str: 日期字符串，格式YYYY-MM-DD，默认今天
    """
    
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    print(f"🔄 开始整合 {date_str} 的数据...\n")
    
    # 1. 加载Twitter数据
    twitter_file = f'data/raw/twitter_data_{date_str}.json'
    try:
        with open(twitter_file, 'r') as f:
            raw_tweets = json.load(f)
        print(f"✅ 加载Twitter数据: {len(raw_tweets)} 条")
    except FileNotFoundError:
        print(f"⚠️  未找到Twitter数据: {twitter_file}")
        raw_tweets = []
    
    # 2. 加载NewsAPI数据
    news_file = f'data/processed/categorized_news_{date_str}.json'
    try:
        with open(news_file, 'r') as f:
            news_by_category = json.load(f)
        raw_news = []
        for articles in news_by_category.values():
            raw_news.extend(articles)
        print(f"✅ 加载NewsAPI数据: {len(raw_news)} 条")
    except FileNotFoundError:
        print(f"⚠️  未找到新闻数据: {news_file}")
        raw_news = []
    
    # 3. 筛选Twitter数据
    if raw_tweets:
        filter = TwitterFilter()
        filtered_tweets = filter.filter_tweets(raw_tweets, min_score=50)
        unique_tweets = filter.deduplicate_tweets(filtered_tweets)
        enriched_tweets = [filter.enrich_tweet_data(t) for t in unique_tweets]
        print(f"✨ Twitter筛选后: {len(enriched_tweets)} 条高质量推文")
    else:
        enriched_tweets = []
    
    # 4. 标准化数据
    normalizer = DataNormalizer()
    
    normalized_tweets = [normalizer.normalize_tweet(t) for t in enriched_tweets]
    normalized_news = [normalizer.normalize_news(n) for n in raw_news]
    
    print(f"📋 标准化完成:")
    print(f"   Twitter: {len(normalized_tweets)} 条")
    print(f"   News: {len(normalized_news)} 条")
    
    # 5. 合并去重
    all_items = normalized_tweets + normalized_news
    merged_items = normalizer.merge_and_deduplicate(all_items)
    
    print(f"🎯 合并去重后: {len(merged_items)} 条")
    
    # 6. 分类保存
    by_source = normalizer.categorize_by_source(merged_items)
    by_topic = normalizer.categorize_by_topic(merged_items)
    
    # 保存统一数据
    output = {
        'date': date_str,
        'total_items': len(merged_items),
        'by_source': {
            'twitter': len(by_source['twitter']),
            'news': len(by_source['news'])
        },
        'by_topic': {k: len(v) for k, v in by_topic.items()},
        'items': merged_items
    }
    
    output_file = f'data/processed/integrated_data_{date_str}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 整合数据已保存: {output_file}")
    
    # 7. 生成统计报告
    print("\n" + "=" * 60)
    print("📊 数据统计报告")
    print("=" * 60)
    
    print(f"\n📌 数据源分布:")
    print(f"   Twitter: {by_source['twitter'].__len__()} 条 ({by_source['twitter'].__len__()/len(merged_items)*100:.1f}%)")
    print(f"   News: {by_source['news'].__len__()} 条 ({by_source['news'].__len__()/len(merged_items)*100:.1f}%)")
    
    print(f"\n📌 主题分布:")
    for topic, items in by_topic.items():
        if items:
            print(f"   {topic}: {len(items)} 条")
    
    print(f"\n📌 质量分布:")
    high_quality = sum(1 for item in merged_items if item.get('quality_score', 0) >= 70)
    medium_quality = sum(1 for item in merged_items if 50 <= item.get('quality_score', 0) < 70)
    low_quality = sum(1 for item in merged_items if item.get('quality_score', 0) < 50)
    
    print(f"   高质量(≥70分): {high_quality} 条")
    print(f"   中质量(50-69分): {medium_quality} 条")
    print(f"   低质量(<50分): {low_quality} 条")
    
    # 8. 显示Top 5
    print(f"\n🏆 Top 5 最高质量内容:")
    for i, item in enumerate(merged_items[:5], 1):
        print(f"\n【{i}】{item.get('title')}")
        print(f"    来源: {item.get('source')} ({item.get('source_type')})")
        print(f"    分数: {item.get('quality_score')}/100")
        print(f"    类别: {', '.join(item.get('categories', []))}")
        print(f"    链接: {item.get('url')}")
    
    return merged_items

if __name__ == '__main__':
    integrate_all_data()
```

**验收标准**：
- [ ] 能同时处理Twitter和NewsAPI数据
- [ ] 数据格式统一（包含所有必要字段）
- [ ] 去重后总数据量合理（50-100条/天）
- [ ] 生成的统计报告清晰易读
- [ ] 保存的JSON文件格式正确

---

## 📊 今天的成果

完成后你将拥有：
```
data/processed/
├── filtered_tweets_2025-01-17.json      # 筛选后的Twitter数据
├── integrated_data_2025-01-17.json      # 整合后的统一数据
└── categorized_news_2025-01-17.json     # NewsAPI数据（已有）

统一数据格式包含：
- 标准化字段（id, title, content, url等）
- 丰富的元数据（类别、地区、币种）
- 质量评分（0-100）
- 原始数据备份