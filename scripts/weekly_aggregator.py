# scripts/weekly_aggregator.py

"""
周报数据聚合器
功能：收集过去7天的数据，整理成周报需要的格式
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
    
    for date in dates:
        # 读取每天的整合数据
        file_path = f'data/processed/integrated_data_{date}.json'
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 分类收集
            for item in data.get('items', []):
                if item['source_type'] == 'twitter':
                    all_tweets.append(item)
                else:
                    all_news.append(item)
            
            print(f"  ✓ {date}: {len(data.get('items', []))} 条")
        else:
            print(f"  ✗ {date}: 文件不存在")
    
    print(f"\n📊 汇总结果:")
    print(f"   新闻: {len(all_news)} 篇")
    print(f"   Twitter: {len(all_tweets)} 条")
    print(f"   总计: {len(all_news) + len(all_tweets)} 条")
    
    # 按类别分组
    by_category = defaultdict(list)
    for item in all_news:
        categories = item.get('categories', ['general'])
        main_category = categories[0]
        by_category[main_category].append(item)
    
    print(f"\n📂 分类分布:")
    for category, items in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   {category}: {len(items)} 篇")
    
    # 按质量分数排序，获取Top 20
    all_content = all_news + all_tweets
    top_news = sorted(all_content, key=lambda x: x.get('quality_score', 0), reverse=True)[:20]
    
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
            'by_category': {k: len(v) for k, v in by_category.items()}
        },
        'top_news': top_news,
        'all_news': all_news,
        'all_tweets': all_tweets,
        'by_category': dict(by_category)
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
    
    # 显示Top 5预览
    print("\n🔍 Top 5 新闻预览:")
    for i, item in enumerate(weekly_data['top_news'][:5], 1):
        print(f"\n{i}. [{item['quality_score']}/100] {item['title'][:60]}...")
        print(f"   来源: {item['source']} | 类别: {', '.join(item.get('categories', []))}")