# scripts/weekly_aggregator.py

"""
周报数据聚合器
功能：收集过去7天的数据，整理成周报需要的格式

数据源优先级：
1. data/processed/categorized_news_{date}.json (新格式，按类别分组)
2. data/processed/integrated_data_{date}.json (旧格式，items 数组)
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

def get_past_week_dates():
    """获取过去7天的日期列表"""
    today = datetime.now()
    dates = []
    for i in range(7):
        date = today - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    return dates

def load_categorized_news(file_path):
    """
    加载 categorized_news 格式的数据
    格式: { "policy": [...], "competitor": [...], "industry": [...], ... }
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_items = []
    by_category = {}

    # 遍历所有类别
    for category, items in data.items():
        if isinstance(items, list):
            by_category[category] = items
            for item in items:
                # 添加类别信息到 item
                item['_category'] = category
                all_items.append(item)

    return all_items, by_category

def load_integrated_data(file_path):
    """
    加载 integrated_data 格式的数据（旧格式）
    格式: { "items": [...] }
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data.get('items', [])
    by_category = defaultdict(list)

    for item in items:
        categories = item.get('categories', ['general'])
        main_category = categories[0] if categories else 'general'
        by_category[main_category].append(item)
        item['_category'] = main_category

    return items, dict(by_category)

def aggregate_weekly_data():
    """聚合过去7天的数据"""

    print("=" * 70)
    print("📊 开始聚合周报数据")
    print("=" * 70 + "\n")

    dates = get_past_week_dates()
    print(f"📅 数据范围: {dates[-1]} 至 {dates[0]}\n")

    # 收集所有数据
    all_news = []
    all_tweets = []
    combined_by_category = defaultdict(list)

    for date in dates:
        # 优先尝试新格式 categorized_news
        categorized_path = f'data/processed/categorized_news_{date}.json'
        integrated_path = f'data/processed/integrated_data_{date}.json'

        items = []
        by_category = {}
        source_type = None

        if os.path.exists(categorized_path):
            items, by_category = load_categorized_news(categorized_path)
            source_type = 'categorized'
        elif os.path.exists(integrated_path):
            items, by_category = load_integrated_data(integrated_path)
            source_type = 'integrated'

        if items:
            # 分类收集：Twitter vs 新闻
            for item in items:
                data_type = item.get('data_type', item.get('source_type', ''))
                if data_type == 'twitter':
                    all_tweets.append(item)
                else:
                    all_news.append(item)

            # 合并类别
            for cat, cat_items in by_category.items():
                combined_by_category[cat].extend(cat_items)

            print(f"  ✓ {date}: {len(items)} 条 ({source_type})")
        else:
            print(f"  ✗ {date}: 无数据")

    print(f"\n📊 汇总结果:")
    print(f"   新闻: {len(all_news)} 篇")
    print(f"   Twitter: {len(all_tweets)} 条")
    print(f"   总计: {len(all_news) + len(all_tweets)} 条")

    print(f"\n📂 分类分布:")
    for category, items in sorted(combined_by_category.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   {category}: {len(items)} 篇")

    # 按重要性分数排序，获取 Top 20
    # 支持 importance_score (新) 和 quality_score (旧)
    all_content = all_news + all_tweets

    def get_score(item):
        return item.get('importance_score', item.get('quality_score', 0))

    top_news = sorted(all_content, key=get_score, reverse=True)[:20]

    print(f"\n🏆 Top 20 重要新闻已选出")

    # 整理周报数据
    weekly_data = {
        'period': {
            'start': dates[-1],
            'end': dates[0],
            'days': 7
        },
        'stats': {
            'total_news': len(all_news),
            'total_tweets': len(all_tweets),
            'total_items': len(all_content),
            'by_category': {k: len(v) for k, v in combined_by_category.items()}
        },
        'top_news': top_news,
        'all_news': all_news,
        'all_tweets': all_tweets,
        'by_category': dict(combined_by_category)
    }

    # 保存周报数据
    output_dir = Path('data/weekly')
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f'weekly_data_{dates[0]}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(weekly_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 周报数据已保存: {output_file}")
    print("=" * 70)

    return weekly_data

if __name__ == '__main__':
    weekly_data = aggregate_weekly_data()

    # 显示 Top 5 预览
    if weekly_data['top_news']:
        print("\n🔍 Top 5 新闻预览:")
        for i, item in enumerate(weekly_data['top_news'][:5], 1):
            score = item.get('importance_score', item.get('quality_score', 0))
            title = item.get('title', 'No title')[:60]
            source = item.get('source', 'Unknown')
            category = item.get('_category', item.get('business_category', 'general'))
            print(f"\n{i}. [{score}] {title}...")
            print(f"   来源: {source} | 类别: {category}")
    else:
        print("\n⚠️ 没有找到任何新闻数据")
