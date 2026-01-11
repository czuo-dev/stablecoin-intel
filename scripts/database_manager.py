# 数据库管理器
# 功能：创建和管理SQLite数据库

import sqlite3
from datetime import datetime
import json
import os

# =========================
# 配置
# =========================

DB_PATH = "data/stablecoin_intel.db"

# =========================
# 数据库初始化
# =========================

def init_database():
    """创建数据库和表"""
    print("=" * 60)
    print("初始化数据库")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建新闻表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE,
            source TEXT,
            category TEXT,
            date DATE,
            summary TEXT,
            full_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("✅ 创建表: articles")
    
    # 创建索引（加快查询速度）
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_date 
        ON articles(date)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_category 
        ON articles(category)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_source 
        ON articles(source)
    ''')
    
    print("✅ 创建索引: date, category, source")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 数据库初始化完成: {DB_PATH}")

# =========================
# 插入数据
# =========================

def insert_article(article):
    """
    插入一条新闻
    
    参数:
        article: 字典，包含新闻信息
    
    返回:
        新插入的记录ID，如果已存在则返回None
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO articles (title, url, source, category, date, summary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            article.get('title', ''),
            article.get('url', article.get('link', '')),
            article.get('source', ''),
            article.get('category', ''),
            article.get('date', article.get('published_at', ''))[:10],
            article.get('summary', '')
        ))
        
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    
    except sqlite3.IntegrityError:
        # URL已存在，跳过
        conn.close()
        return None
    
    except Exception as e:
        print(f"❌ 插入失败: {e}")
        conn.close()
        return None

def insert_articles_batch(articles):
    """
    批量插入新闻
    
    参数:
        articles: 新闻列表
    
    返回:
        成功插入的数量
    """
    print("\n" + "=" * 60)
    print(f"开始批量插入 {len(articles)} 条数据")
    print("=" * 60)
    
    success_count = 0
    duplicate_count = 0
    error_count = 0
    
    for i, article in enumerate(articles, 1):
        result = insert_article(article)
        
        if result is not None:
            success_count += 1
            if i % 10 == 0:  # 每10条显示一次进度
                print(f"  进度: {i}/{len(articles)} - 成功: {success_count}")
        elif result is None:
            duplicate_count += 1
        else:
            error_count += 1
    
    print("\n" + "=" * 60)
    print(f"批量插入完成")
    print("=" * 60)
    print(f"✅ 成功插入: {success_count} 条")
    print(f"⚠️  重复跳过: {duplicate_count} 条")
    if error_count > 0:
        print(f"❌ 插入失败: {error_count} 条")
    
    return success_count

# =========================
# 查询数据
# =========================

def get_all_articles(limit=None):
    """获取所有新闻"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = 'SELECT * FROM articles ORDER BY date DESC'
    if limit:
        query += f' LIMIT {limit}'
    
    cursor.execute(query)
    
    # 获取列名
    columns = [description[0] for description in cursor.description]
    
    # 转换为字典列表
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    
    conn.close()
    return results

def get_recent_articles(days=7):
    """
    获取最近N天的新闻
    
    参数:
        days: 天数
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM articles 
        WHERE date >= date('now', '-' || ? || ' days')
        ORDER BY date DESC
    ''', (days,))
    
    columns = [description[0] for description in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results

def search_articles(keyword):
    """
    搜索包含关键词的新闻
    
    参数:
        keyword: 搜索关键词
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM articles
        WHERE title LIKE ? OR summary LIKE ?
        ORDER BY date DESC
        LIMIT 50
    ''', (f'%{keyword}%', f'%{keyword}%'))
    
    columns = [description[0] for description in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results

def get_articles_by_category(category):
    """
    获取指定分类的新闻
    
    参数:
        category: 分类名称
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM articles
        WHERE category = ?
        ORDER BY date DESC
    ''', (category,))
    
    columns = [description[0] for description in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results

# =========================
# 统计功能
# =========================

def get_database_stats():
    """获取数据库统计信息"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总记录数
    cursor.execute('SELECT COUNT(*) FROM articles')
    total = cursor.fetchone()[0]
    
    # 按分类统计
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM articles
        GROUP BY category
        ORDER BY count DESC
    ''')
    by_category = cursor.fetchall()
    
    # 按来源统计
    cursor.execute('''
        SELECT source, COUNT(*) as count
        FROM articles
        GROUP BY source
        ORDER BY count DESC
        LIMIT 10
    ''')
    by_source = cursor.fetchall()
    
    # 按日期统计（最近7天）
    cursor.execute('''
        SELECT date, COUNT(*) as count
        FROM articles
        WHERE date >= date('now', '-7 days')
        GROUP BY date
        ORDER BY date DESC
    ''')
    by_date = cursor.fetchall()
    
    conn.close()
    
    return {
        'total': total,
        'by_category': by_category,
        'by_source': by_source,
        'by_date': by_date
    }

def display_stats():
    """显示数据库统计"""
    print("\n" + "=" * 60)
    print("数据库统计")
    print("=" * 60)
    
    stats = get_database_stats()
    
    print(f"\n📊 总记录数: {stats['total']} 条")
    
    print("\n📂 按分类:")
    for category, count in stats['by_category']:
        print(f"  {category:20} {count:3} 条")
    
    print("\n📰 主要来源 (Top 10):")
    for source, count in stats['by_source']:
        print(f"  {source:20} {count:3} 条")
    
    print("\n📅 最近7天:")
    for date, count in stats['by_date']:
        print(f"  {date} {count:3} 条")

# =========================
# 数据迁移
# =========================

def migrate_json_to_db(json_file):
    """
    将JSON数据迁移到数据库
    
    参数:
        json_file: JSON文件路径
    """
    print("\n" + "=" * 60)
    print(f"数据迁移: {json_file}")
    print("=" * 60)
    
    if not os.path.exists(json_file):
        print(f"❌ 文件不存在: {json_file}")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        print(f"✅ 读取到 {len(articles)} 条数据")
        
        # 批量插入
        count = insert_articles_batch(articles)
        
        print(f"\n✅ 迁移完成: {count} 条新数据")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")

# =========================
# 高级查询功能
# =========================

def get_trending_topics(days=7, limit=10):
    """
    获取热门话题
    
    参数:
        days: 时间范围（天）
        limit: 返回数量
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 统计关键词出现频率
    # 这里简化处理，实际可以用更复杂的算法
    cursor.execute('''
        SELECT 
            CASE 
                WHEN title LIKE '%Circle%' THEN 'Circle'
                WHEN title LIKE '%Tether%' OR title LIKE '%USDT%' THEN 'Tether'
                WHEN title LIKE '%USDC%' THEN 'USDC'
                WHEN title LIKE '%PayPal%' OR title LIKE '%PYUSD%' THEN 'PayPal'
                WHEN title LIKE '%regulation%' OR title LIKE '%监管%' THEN 'Regulation'
                ELSE 'Other'
            END as topic,
            COUNT(*) as count
        FROM articles
        WHERE date >= date('now', '-' || ? || ' days')
        GROUP BY topic
        ORDER BY count DESC
        LIMIT ?
    ''', (days, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def get_source_comparison(days=30):
    """
    对比不同来源的报道数量
    
    参数:
        days: 时间范围
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            source,
            COUNT(*) as total,
            SUM(CASE WHEN category = '📋 政策监管' THEN 1 ELSE 0 END) as policy,
            SUM(CASE WHEN category = '💰 融资并购' THEN 1 ELSE 0 END) as funding,
            SUM(CASE WHEN category = '🏢 公司动态' THEN 1 ELSE 0 END) as company
        FROM articles
        WHERE date >= date('now', '-' || ? || ' days')
        GROUP BY source
        ORDER BY total DESC
        LIMIT 10
    ''', (days,))
    
    columns = ['source', 'total', 'policy', 'funding', 'company']
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results

def get_daily_trend(days=30):
    """
    获取每日新闻趋势
    
    参数:
        days: 天数
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            date,
            COUNT(*) as count,
            GROUP_CONCAT(DISTINCT category) as categories
        FROM articles
        WHERE date >= date('now', '-' || ? || ' days')
        GROUP BY date
        ORDER BY date DESC
    ''', (days,))
    
    columns = ['date', 'count', 'categories']
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results

def get_category_timeline(category, days=30):
    """
    获取特定分类的时间线
    
    参数:
        category: 分类名称
        days: 天数
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            date,
            COUNT(*) as count
        FROM articles
        WHERE category = ?
        AND date >= date('now', '-' || ? || ' days')
        GROUP BY date
        ORDER BY date DESC
    ''', (category, days))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

# =========================
# 数据导出功能
# =========================

def export_to_csv(output_file='data/exports/articles.csv'):
    """导出所有数据为CSV"""
    import csv
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM articles ORDER BY date DESC')
    
    # 获取列名
    columns = [description[0] for description in cursor.description]
    
    # 写入CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)  # 写入表头
        writer.writerows(cursor.fetchall())  # 写入数据
    
    conn.close()
    
    print(f"✅ 数据已导出到: {output_file}")
    return output_file

# =========================
# 主程序
# =========================

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("=" * 60)
        print("数据库管理器")
        print("=" * 60)
        print("\n用法:")
        print("  python database_manager.py init                    # 初始化数据库")
        print("  python database_manager.py migrate <json文件>      # 迁移JSON数据")
        print("  python database_manager.py stats                   # 查看统计")
        print("  python database_manager.py search <关键词>         # 搜索")
        print("  python database_manager.py list [数量]             # 列出最新新闻")
        print("  python database_manager.py trending [天数]         # 热门话题")
        print("  python database_manager.py comparison [天数]       # 来源对比")
        print("  python database_manager.py trend [天数]            # 每日趋势")
        print("  python database_manager.py export-csv [文件路径]   # 导出CSV")
        return
    
    command = sys.argv[1]
    
    if command == "init":
        init_database()
    
    elif command == "migrate" and len(sys.argv) == 3:
        json_file = sys.argv[2]
        migrate_json_to_db(json_file)
    
    elif command == "stats":
        display_stats()
    
    elif command == "search" and len(sys.argv) == 3:
        keyword = sys.argv[2]
        results = search_articles(keyword)
        
        print(f"\n找到 {len(results)} 条结果:")
        for article in results[:10]:
            print(f"\n  {article['title']}")
            print(f"  来源: {article['source']} | 日期: {article['date']}")
            print(f"  分类: {article['category']}")
    
    elif command == "list":
        limit = int(sys.argv[2]) if len(sys.argv) == 3 else 10
        articles = get_all_articles(limit)
        
        print(f"\n最新 {len(articles)} 条新闻:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   来源: {article['source']} | 日期: {article['date']}")
    
    elif command == "trending":
        days = int(sys.argv[2]) if len(sys.argv) == 3 else 7
        topics = get_trending_topics(days)
        
        print(f"\n最近{days}天热门话题:")
        for topic, count in topics:
            print(f"  {topic:20} {count:3} 条")
    
    elif command == "comparison":
        days = int(sys.argv[2]) if len(sys.argv) == 3 else 30
        comparison = get_source_comparison(days)
        
        print(f"\n最近{days}天来源对比:")
        print(f"{'来源':<20} {'总计':>6} {'政策':>6} {'融资':>6} {'公司':>6}")
        print("-" * 60)
        for item in comparison:
            print(f"{item['source']:<20} {item['total']:>6} "
                  f"{item['policy']:>6} {item['funding']:>6} {item['company']:>6}")
    
    elif command == "trend":
        days = int(sys.argv[2]) if len(sys.argv) == 3 else 30
        trend = get_daily_trend(days)
        
        print(f"\n最近{days}天趋势:")
        for item in trend[:10]:  # 只显示前10天
            print(f"  {item['date']} {item['count']:3} 条")
    
    elif command == "export-csv":
        output = sys.argv[2] if len(sys.argv) == 3 else 'data/exports/articles.csv'
        export_to_csv(output)
    
    else:
        print("❌ 无效的命令")

if __name__ == "__main__":
    main()
