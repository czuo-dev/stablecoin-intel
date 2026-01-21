# scripts/daily_collect.py
"""每日数据收集（不调用AI，节省成本）"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.collectors.news_collector import NewsCollector
from src.collectors.data_normalizer import DataNormalizer

def main():
    print("📡 开始每日数据收集...")
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 收集新闻
    collector = NewsCollector()
    # 使用 collect_news 方法，它会自动使用预设的关键词策略
    articles = collector.collect_news(days_back=1)  # 只收集今天的
    
    # 标准化
    normalizer = DataNormalizer()
    normalized = [normalizer.normalize_news(a) for a in articles]
    
    # 保存
    output_file = f'data/daily/news_{date_str}.json'
    os.makedirs('data/daily', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': date_str,
            'count': len(normalized),
            'items': normalized
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 收集完成: {len(normalized)} 条数据")
    print(f"📁 保存到: {output_file}")

if __name__ == '__main__':
    main()