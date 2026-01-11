# 数据去重工具
# 功能：清理数据库中的重复新闻

import json
import os

# =========================
# 加载数据库
# =========================

def load_database(filepath):
    """加载数据库"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 文件不存在: {filepath}")
        return None
    except Exception as e:
        print(f"❌ 加载失败: {e}")
        return None

# =========================
# 去重逻辑
# =========================

def deduplicate_by_title(news_list):
    """根据标题去重（标题完全相同才算重复）"""
    seen_titles = set()
    unique_news = []
    duplicates = []
    
    for news in news_list:
        title = news.get("title", "").strip()
        
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_news.append(news)
        else:
            duplicates.append(news)
    
    return unique_news, duplicates

def deduplicate_by_url(news_list):
    """根据 URL 去重（更准确）"""
    seen_urls = set()
    unique_news = []
    duplicates = []
    
    for news in news_list:
        url = news.get("url", news.get("link", "")).strip()
        
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_news.append(news)
        else:
            duplicates.append(news)
    
    return unique_news, duplicates

def smart_deduplicate(news_list):
    """智能去重：先按URL，再按标题"""
    print("开始智能去重...")
    
    # 第一轮：按 URL 去重
    unique, dup1 = deduplicate_by_url(news_list)
    print(f"  按 URL 去重: 移除 {len(dup1)} 条")
    
    # 第二轮：按标题去重（针对没有URL的新闻）
    unique, dup2 = deduplicate_by_title(unique)
    print(f"  按标题去重: 移除 {len(dup2)} 条")
    
    total_removed = len(dup1) + len(dup2)
    print(f"\n✅ 去重完成: {len(news_list)} → {len(unique)} 条")
    print(f"   移除重复: {total_removed} 条")
    
    return unique

# =========================
# 备份功能
# =========================

def backup_database(filepath):
    """备份数据库"""
    if not os.path.exists(filepath):
        return None
    
    # 生成备份文件名
    backup_path = filepath.replace(".json", "_backup.json")
    
    try:
        with open(filepath, "r") as f:
            data = f.read()
        with open(backup_path, "w") as f:
            f.write(data)
        print(f"✅ 已备份到 {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

# =========================
# 保存功能
# =========================

def save_database(filepath, data):
    """保存数据库"""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存到 {filepath}")
        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

# =========================
# 主程序
# =========================

def main():
    print("=" * 60)
    print("数据库去重工具")
    print("=" * 60)
    
    # 要处理的数据库文件
    db_files = [
        "data/news_system_db.json",
        "data/news_database.json"
    ]
    
    for db_file in db_files:
        if not os.path.exists(db_file):
            print(f"\n⚠️  跳过不存在的文件: {db_file}")
            continue
        
        print(f"\n处理文件: {db_file}")
        print("-" * 60)
        
        # 加载数据
        data = load_database(db_file)
        if not data:
            continue
        
        original_count = len(data)
        print(f"原始记录数: {original_count}")
        
        # 备份
        backup_database(db_file)
        
        # 去重
        unique_data = smart_deduplicate(data)
        
        # 保存
        if len(unique_data) < original_count:
            save_database(db_file, unique_data)
        else:
            print("✅ 无重复数据，不需要保存")
    
    print("\n" + "=" * 60)
    print("去重完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()