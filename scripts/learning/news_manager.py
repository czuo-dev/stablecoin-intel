# 稳定币新闻数据管理器
# 功能：保存新闻、加载新闻、搜索新闻

import json
import os
from datetime import datetime

# =========================
# 配置
# =========================

DATA_FILE = "data/news_database.json"
BACKUP_FILE = "data/news_database_backup.json"

# =========================
# 工具函数：安全文件操作
# =========================

def ensure_data_dir():
    """确保 data 目录存在"""
    os.makedirs("data", exist_ok=True)

def load_news_database():
    """加载新闻数据库"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ 成功加载数据库，共 {len(data)} 条新闻")
        return data
    except FileNotFoundError:
        print("⚠️  数据库文件不存在，创建新数据库")
        return []
    except json.JSONDecodeError:
        print("❌ 数据库文件损坏，尝试恢复备份...")
        return load_backup()
    except Exception as e:
        print(f"❌ 加载失败: {e}")
        return []

def load_backup():
    """加载备份数据库"""
    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ 从备份恢复，共 {len(data)} 条新闻")
        return data
    except:
        print("❌ 备份也不可用，返回空数据库")
        return []

def save_news_database(news_list):
    """保存新闻数据库"""
    ensure_data_dir()
    
    try:
        # 先备份旧数据
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                old_data = f.read()
            with open(BACKUP_FILE, "w", encoding="utf-8") as f:
                f.write(old_data)
        
        # 保存新数据
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功保存 {len(news_list)} 条新闻")
        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

# =========================
# 核心功能
# =========================

def add_news(news_list, title, source, category, url=""):
    """添加一条新闻"""
    news = {
        "id": len(news_list) + 1,
        "title": title,
        "source": source,
        "category": category,
        "url": url,
        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    news_list.append(news)
    print(f"✅ 已添加新闻: {title[:50]}...")
    return news_list

def search_news(news_list, keyword):
    """搜索新闻"""
    results = []
    keyword_lower = keyword.lower()
    
    for news in news_list:
        if (keyword_lower in news["title"].lower() or 
            keyword_lower in news["source"].lower() or
            keyword_lower in news["category"].lower()):
            results.append(news)
    
    return results

def get_news_by_category(news_list, category):
    """按分类筛选新闻"""
    return [n for n in news_list if n["category"] == category]

def display_news(news_list, max_show=10):
    """显示新闻列表"""
    if not news_list:
        print("📭 没有新闻")
        return
    
    print(f"\n共 {len(news_list)} 条新闻:")
    print("=" * 80)
    
    for i, news in enumerate(news_list[:max_show], 1):
        print(f"\n{i}. [{news['category']}] {news['title']}")
        print(f"   来源: {news['source']} | 时间: {news['added_at']}")
        if news.get('url'):
            print(f"   链接: {news['url']}")
    
    if len(news_list) > max_show:
        print(f"\n... 还有 {len(news_list) - max_show} 条")

def export_to_text(news_list, filename):
    """导出为文本文件"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("稳定币新闻汇总\n")
            f.write("=" * 80 + "\n\n")
            
            for i, news in enumerate(news_list, 1):
                f.write(f"{i}. [{news['category']}] {news['title']}\n")
                f.write(f"   来源: {news['source']} | 时间: {news['added_at']}\n")
                if news.get('url'):
                    f.write(f"   链接: {news['url']}\n")
                f.write("\n")
            
            f.write(f"总计: {len(news_list)} 条新闻\n")
        
        print(f"✅ 已导出到 {filename}")
        return True
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return False

# =========================
# 统计功能
# =========================

def get_statistics(news_list):
    """获取统计信息"""
    if not news_list:
        return {"total": 0}
    
    # 按分类统计
    categories = {}
    sources = {}
    
    for news in news_list:
        cat = news["category"]
        src = news["source"]
        
        categories[cat] = categories.get(cat, 0) + 1
        sources[src] = sources.get(src, 0) + 1
    
    return {
        "total": len(news_list),
        "categories": categories,
        "sources": sources
    }

def display_statistics(stats):
    """显示统计信息"""
    print("\n" + "=" * 50)
    print("📊 数据库统计")
    print("=" * 50)
    
    print(f"\n总新闻数: {stats['total']} 条")
    
    if stats.get('categories'):
        print("\n按分类:")
        for cat, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count} 条")
    
    if stats.get('sources'):
        print("\n按来源 (Top 5):")
        sorted_sources = sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True)
        for src, count in sorted_sources[:5]:
            print(f"  {src}: {count} 条")

# =========================
# 主程序
# =========================

def main():
    print("=" * 80)
    print("稳定币新闻数据管理器")
    print("=" * 80)
    
    # 加载数据库
    news_db = load_news_database()
    
    # 如果是新数据库，添加示例数据
    if len(news_db) == 0:
        print("\n首次运行，添加示例数据...")
        
        sample_news = [
            {
                "title": "Circle获得新加坡MAS电子货币机构牌照",
                "source": "CoinDesk",
                "category": "📋 政策监管",
                "url": "https://example.com/1"
            },
            {
                "title": "Tether完成5亿美元战略融资",
                "source": "The Block",
                "category": "💰 融资并购",
                "url": "https://example.com/2"
            },
            {
                "title": "PayPal的PYUSD稳定币在欧洲上线",
                "source": "Reuters",
                "category": "🏢 公司动态",
                "url": "https://example.com/3"
            },
            {
                "title": "美国SEC主席称将加强稳定币监管",
                "source": "Bloomberg",
                "category": "📋 政策监管",
                "url": "https://example.com/4"
            },
            {
                "title": "Visa与Circle达成战略合作",
                "source": "Financial Times",
                "category": "🏢 公司动态",
                "url": "https://example.com/5"
            },
        ]
        
        for news in sample_news:
            news_db = add_news(
                news_db, 
                news["title"], 
                news["source"], 
                news["category"],
                news["url"]
            )
        
        # 保存
        save_news_database(news_db)
    
    # 显示所有新闻
    print("\n" + "=" * 80)
    print("所有新闻")
    print("=" * 80)
    display_news(news_db)
    
    # 显示统计
    stats = get_statistics(news_db)
    display_statistics(stats)
    
    # 搜索功能演示
    print("\n" + "=" * 80)
    print("搜索功能测试")
    print("=" * 80)
    
    print("\n搜索关键词: Circle")
    search_results = search_news(news_db, "Circle")
    display_news(search_results)
    
    # 按分类筛选
    print("\n" + "=" * 80)
    print("分类筛选测试")
    print("=" * 80)
    
    print("\n分类: 📋 政策监管")
    policy_news = get_news_by_category(news_db, "📋 政策监管")
    display_news(policy_news)
    
    # 导出功能
    print("\n" + "=" * 80)
    print("导出功能")
    print("=" * 80)
    export_to_text(news_db, "data/news_export.txt")
    
    # 最终保存
    save_news_database(news_db)

if __name__ == "__main__":
    main()