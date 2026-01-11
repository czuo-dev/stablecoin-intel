# 稳定币新闻数据分析器
# 功能：统计分析、趋势识别、生成洞察

import json
import os
from datetime import datetime, timedelta
from collections import Counter

# =========================
# 加载数据
# =========================

def load_all_news():
    """加载所有新闻数据"""
    all_news = []
    
    # 从主数据库加载
    db_files = [
        "data/news_system_db.json",
        "data/news_database.json"
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                with open(db_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_news.extend(data)
                    print(f"✅ 加载 {db_file}: {len(data)} 条")
            except Exception as e:
                print(f"❌ 加载失败 {db_file}: {e}")
    
    print(f"\n总计: {len(all_news)} 条新闻")
    return all_news

# =========================
# 基础统计
# =========================

def basic_statistics(news_list):
    """基础统计信息"""
    stats = {
        "total": len(news_list),
        "sources": Counter(),
        "categories": Counter(),
        "dates": Counter()
    }
    
    for news in news_list:
        # 来源统计
        source = news.get("source", "未知")
        stats["sources"][source] += 1
        
        # 分类统计
        category = news.get("category", "未分类")
        stats["categories"][category] += 1
        
        # 日期统计
        date = news.get("date", news.get("published_at", ""))[:10]
        if date:
            stats["dates"][date] += 1
    
    return stats

# =========================
# 时间分析
# =========================

def time_analysis(news_list, days=7):
    """时间维度分析"""
    today = datetime.now()
    cutoff = today - timedelta(days=days)
    
    recent_news = []
    for news in news_list:
        date_str = news.get("date", news.get("published_at", ""))[:10]
        if date_str:
            try:
                news_date = datetime.strptime(date_str, "%Y-%m-%d")
                if news_date >= cutoff:
                    recent_news.append(news)
            except:
                pass
    
    return {
        "period": f"最近 {days} 天",
        "total": len(recent_news),
        "daily_avg": len(recent_news) / days,
        "news_list": recent_news
    }

# =========================
# 关键词热度分析
# =========================

def keyword_analysis(news_list):
    """关键词热度分析"""
    keyword_count = Counter()
    
    # 预定义的关键公司/产品
    key_entities = [
        "Circle", "Tether", "USDC", "USDT", "PayPal", "Visa",
        "MAS", "HKMA", "SEC", "MiCA"
    ]
    
    for news in news_list:
        title = news.get("title", "")
        
        for entity in key_entities:
            if entity.lower() in title.lower():
                keyword_count[entity] += 1
    
    return keyword_count

# =========================
# 趋势识别
# =========================

def identify_trends(stats, keyword_count):
    """识别趋势和热点"""
    trends = []
    
    # 1. 最活跃的分类
    if stats["categories"]:
        top_category = stats["categories"].most_common(1)[0]
        trends.append({
            "type": "热门分类",
            "content": f"{top_category[0]} 最活跃（{top_category[1]} 条）"
        })
    
    # 2. 最多报道的来源
    if stats["sources"]:
        top_source = stats["sources"].most_common(1)[0]
        trends.append({
            "type": "主要来源",
            "content": f"{top_source[0]} 报道最多（{top_source[1]} 条）"
        })
    
    # 3. 最热门的实体
    if keyword_count:
        top_entity = keyword_count.most_common(1)[0]
        trends.append({
            "type": "热点实体",
            "content": f"{top_entity[0]} 被提及 {top_entity[1]} 次"
        })
    
    return trends

# =========================
# 显示功能
# =========================

def display_statistics(stats):
    """显示统计信息"""
    print("\n" + "=" * 60)
    print("📊 数据统计")
    print("=" * 60)
    
    print(f"\n总新闻数: {stats['total']} 条")
    
    # 按分类
    print("\n分类分布:")
    for category, count in stats["categories"].most_common():
        percentage = (count / stats['total']) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {category:20} {count:3}条 {percentage:5.1f}% {bar}")
    
    # 按来源（Top 10）
    print("\n主要来源 (Top 10):")
    for source, count in stats["sources"].most_common(10):
        percentage = (count / stats['total']) * 100
        print(f"  {source:20} {count:3}条 {percentage:5.1f}%")
    
    # 按日期（最近7天）
    if stats["dates"]:
        print("\n最近日期:")
        for date, count in sorted(stats["dates"].items(), reverse=True)[:7]:
            print(f"  {date} {count:3}条")

def display_time_analysis(time_data):
    """显示时间分析"""
    print("\n" + "=" * 60)
    print(f"📅 {time_data['period']}分析")
    print("=" * 60)
    
    print(f"\n新闻总数: {time_data['total']} 条")
    print(f"日均新闻: {time_data['daily_avg']:.1f} 条")

def display_trends(trends):
    """显示趋势"""
    print("\n" + "=" * 60)
    print("🔥 趋势洞察")
    print("=" * 60)
    
    for i, trend in enumerate(trends, 1):
        print(f"\n{i}. [{trend['type']}]")
        print(f"   {trend['content']}")

def display_keyword_analysis(keyword_count):
    """显示关键词分析"""
    print("\n" + "=" * 60)
    print("🏷️  关键实体热度")
    print("=" * 60)
    
    for entity, count in keyword_count.most_common(10):
        bar = "●" * count
        print(f"  {entity:15} {count:3}次 {bar}")

# =========================
# 主程序
# =========================

def main():
    print("=" * 60)
    print("稳定币新闻数据分析器")
    print("=" * 60)
    
    # 加载数据
    news_list = load_all_news()
    
    if not news_list:
        print("\n❌ 没有数据可分析")
        return
    
    # 基础统计
    stats = basic_statistics(news_list)
    display_statistics(stats)
    
    # 时间分析
    time_data = time_analysis(news_list, days=7)
    display_time_analysis(time_data)
    
    # 关键词分析
    keyword_count = keyword_analysis(news_list)
    display_keyword_analysis(keyword_count)
    
    # 趋势识别
    trends = identify_trends(stats, keyword_count)
    display_trends(trends)
    
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()