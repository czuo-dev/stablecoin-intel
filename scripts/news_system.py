# 稳定币新闻智能系统（整合版）
# 功能：过滤 + 管理 + 查询

import json
import os
from datetime import datetime

# =========================
# 导入关键词库
# =========================

policy_keywords = [
    "stablecoin regulation", "MiCA", "SEC", "CFTC", "MAS", "HKMA",
    "监管", "牌照", "合规"
]

company_keywords = [
    "Circle", "Tether", "USDC", "USDT", "PayPal", "Visa", "Stripe"
]

funding_keywords = [
    "funding round", "raises", "Series A", "investment", 
    "融资", "并购", "acquisition"
]

# =========================
# 数据库操作（来自 news_manager.py）
# =========================

DATABASE_FILE = "data/news_system_db.json"

def load_database():
    """加载数据库"""
    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"❌ 加载失败: {e}")
        return []

def save_database(news_list):
    """保存数据库"""
    os.makedirs("data", exist_ok=True)
    try:
        with open(DATABASE_FILE, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

def add_news_to_db(news_list, news_item):
    """添加新闻到数据库"""
    news_item["id"] = len(news_list) + 1
    news_item["added_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    news_list.append(news_item)
    return news_list

# =========================
# 过滤逻辑（来自 news_filter.py）
# =========================

def classify_news(title):
    """分类新闻"""
    title_lower = title.lower()
    matched_keywords = []
    
    # 检查政策类
    for kw in policy_keywords:
        if kw.lower() in title_lower:
            matched_keywords.append(kw)
            return (True, "📋 政策监管", matched_keywords)
    
    # 检查融资类
    for kw in funding_keywords:
        if kw.lower() in title_lower:
            matched_keywords.append(kw)
            return (True, "💰 融资并购", matched_keywords)
    
    # 检查公司类
    for kw in company_keywords:
        if kw.lower() in title_lower:
            matched_keywords.append(kw)
            return (True, "🏢 公司动态", matched_keywords)
    
    return (False, "❌ 不相关", [])

def filter_and_add_news(raw_news_list):
    """过滤新闻并添加到数据库"""
    db = load_database()
    added_count = 0
    
    print("\n" + "=" * 60)
    print("新闻过滤和入库")
    print("=" * 60)
    
    for news in raw_news_list:
        is_relevant, category, keywords = classify_news(news["title"])
        
        if is_relevant:
            # 准备要保存的新闻
            news_item = {
                "title": news["title"],
                "source": news["source"],
                "date": news["date"],
                "category": category,
                "keywords": keywords
            }
            
            # 添加到数据库
            db = add_news_to_db(db, news_item)
            added_count += 1
            
            print(f"✅ {category} - {news['title'][:50]}...")
    
    # 保存数据库
    if save_database(db):
        print(f"\n✅ 成功添加 {added_count} 条相关新闻到数据库")
        print(f"📊 数据库总计: {len(db)} 条新闻")
    
    return db

# =========================
# 查询功能
# =========================

def search_news(keyword):
    """搜索新闻"""
    db = load_database()
    results = []
    
    keyword_lower = keyword.lower()
    for news in db:
        if (keyword_lower in news["title"].lower() or
            keyword_lower in news["source"].lower()):
            results.append(news)
    
    return results

def get_recent_news(days=7):
    """获取最近几天的新闻"""
    db = load_database()
    # 简化版：返回最后N条
    return db[-days*5:] if len(db) > days*5 else db

def get_statistics():
    """统计信息"""
    db = load_database()
    
    if not db:
        return {"total": 0}
    
    stats = {
        "total": len(db),
        "categories": {},
        "sources": {}
    }
    
    for news in db:
        cat = news.get("category", "未分类")
        src = news.get("source", "未知")
        
        stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
        stats["sources"][src] = stats["sources"].get(src, 0) + 1
    
    return stats

# =========================
# 显示功能
# =========================

def display_news_list(news_list, title="新闻列表"):
    """显示新闻"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    
    if not news_list:
        print("📭 没有新闻")
        return
    
    for i, news in enumerate(news_list, 1):
        print(f"\n{i}. [{news.get('category', '未分类')}]")
        print(f"   {news['title']}")
        print(f"   来源: {news.get('source', '未知')} | {news.get('date', '未知')}")

def display_statistics(stats):
    """显示统计"""
    print("\n" + "=" * 60)
    print("📊 数据库统计")
    print("=" * 60)
    
    print(f"\n总新闻数: {stats['total']} 条")
    
    if stats.get('categories'):
        print("\n按分类:")
        for cat, count in sorted(stats['categories'].items(), 
                                key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count} 条")
    
    if stats.get('sources'):
        print("\n按来源 (Top 5):")
        sorted_sources = sorted(stats['sources'].items(), 
                              key=lambda x: x[1], reverse=True)
        for src, count in sorted_sources[:5]:
            print(f"  {src}: {count} 条")

# =========================
# 主程序：演示完整流程
# =========================

def main():
    print("=" * 60)
    print("稳定币新闻智能系统")
    print("=" * 60)
    
    # 步骤1: 模拟获取原始新闻（实际应该从API获取）
    raw_news = [
        {"title": "Circle获得新加坡MAS支付牌照", "source": "CoinDesk", "date": "2025-01-10"},
        {"title": "Tether完成5亿美元融资", "source": "The Block", "date": "2025-01-10"},
        {"title": "比特币突破10万美元", "source": "CNBC", "date": "2025-01-10"},
        {"title": "PayPal PYUSD在欧洲上线", "source": "Reuters", "date": "2025-01-09"},
        {"title": "SEC加强稳定币监管", "source": "Bloomberg", "date": "2025-01-09"},
    ]
    
    print(f"\n获取到 {len(raw_news)} 条原始新闻")
    
    # 步骤2: 过滤并入库（整合了两个功能）
    db = filter_and_add_news(raw_news)
    
    # 步骤3: 查询功能演示
    print("\n" + "=" * 60)
    print("功能演示：搜索")
    print("=" * 60)
    
    search_results = search_news("Circle")
    display_news_list(search_results, "搜索结果: Circle")
    
    # 步骤4: 统计
    stats = get_statistics()
    display_statistics(stats)
    
    # 步骤5: 显示最近新闻
    recent = get_recent_news(days=7)
    display_news_list(recent[-5:], "最近5条新闻")

if __name__ == "__main__":
    main()