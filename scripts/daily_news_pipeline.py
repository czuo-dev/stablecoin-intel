# 每日新闻处理流程
# 功能：抓取 → 过滤 → 入库 → 报告

import sys
import os

# 添加 scripts 到路径（为了导入其他脚本）
sys.path.append(os.path.dirname(__file__))

from news_fetcher import fetch_all_stablecoin_news, save_raw_news
from news_system import classify_news, add_news_to_db, load_database, save_database
from news_system import get_statistics, display_statistics

def run_daily_pipeline():
    """运行每日新闻处理流程"""
    print("=" * 70)
    print("每日新闻处理流程")
    print("=" * 70)
    
    # 步骤1：抓取新闻
    print("\n步骤 1/4: 抓取新闻...")
    raw_news = fetch_all_stablecoin_news(days=1)  # 只抓取今天的
    
    if not raw_news:
        print("❌ 未获取到新闻，流程终止")
        return
    
    # 保存原始数据
    save_raw_news(raw_news)
    
    # 步骤2：过滤相关新闻
    print("\n步骤 2/4: 过滤新闻...")
    db = load_database()
    added_count = 0
    
    for news in raw_news:
        is_relevant, category, keywords = classify_news(news["title"])
        
        if is_relevant:
            news_item = {
                "title": news["title"],
                "source": news["source"],
                "url": news["url"],
                "date": news["published_at"][:10],
                "category": category,
                "keywords": keywords
            }
            
            db = add_news_to_db(db, news_item)
            added_count += 1
            print(f"  ✅ {category} - {news['title'][:50]}...")
    
    print(f"\n过滤结果: {added_count}/{len(raw_news)} 条相关新闻")
    
    # 步骤3：保存到数据库
    print("\n步骤 3/4: 保存到数据库...")
    if save_database(db):
        print(f"✅ 数据库已更新，总计 {len(db)} 条新闻")
    
    # 步骤4：生成统计报告
    print("\n步骤 4/4: 生成统计报告...")
    stats = get_statistics()
    display_statistics(stats)
    
    print("\n" + "=" * 70)
    print("流程完成！")
    print("=" * 70)

if __name__ == "__main__":
    run_daily_pipeline()