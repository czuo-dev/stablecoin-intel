# 数据库备份和维护工具
# 功能：备份、恢复、清理数据库

import sqlite3
import shutil
import os
from datetime import datetime

DB_PATH = "data/stablecoin_intel.db"
BACKUP_DIR = "data/backups"

# =========================
# 备份功能
# =========================

def backup_database():
    """备份数据库"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}/backup_{timestamp}.db"
    
    try:
        shutil.copy2(DB_PATH, backup_path)
        
        # 获取文件大小
        size = os.path.getsize(backup_path)
        size_mb = size / (1024 * 1024)
        
        print(f"✅ 备份成功!")
        print(f"   源文件: {DB_PATH}")
        print(f"   备份: {backup_path}")
        print(f"   大小: {size_mb:.2f} MB")
        
        return backup_path
        
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

def list_backups():
    """列出所有备份"""
    if not os.path.exists(BACKUP_DIR):
        print("没有找到备份")
        return []
    
    backups = []
    for file in os.listdir(BACKUP_DIR):
        if file.endswith('.db'):
            path = os.path.join(BACKUP_DIR, file)
            size = os.path.getsize(path)
            mtime = os.path.getmtime(path)
            
            backups.append({
                'file': file,
                'path': path,
                'size': size,
                'time': datetime.fromtimestamp(mtime)
            })
    
    # 按时间排序
    backups.sort(key=lambda x: x['time'], reverse=True)
    
    return backups

def restore_backup(backup_path):
    """恢复备份"""
    if not os.path.exists(backup_path):
        print(f"❌ 备份文件不存在: {backup_path}")
        return False
    
    # 先备份当前数据库
    print("先备份当前数据库...")
    current_backup = backup_database()
    
    try:
        shutil.copy2(backup_path, DB_PATH)
        print(f"\n✅ 恢复成功!")
        print(f"   从: {backup_path}")
        print(f"   到: {DB_PATH}")
        return True
        
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False

# =========================
# 清理功能
# =========================

def vacuum_database():
    """压缩数据库（清理碎片）"""
    print("开始压缩数据库...")
    
    # 获取压缩前大小
    size_before = os.path.getsize(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute('VACUUM')
    conn.close()
    
    # 获取压缩后大小
    size_after = os.path.getsize(DB_PATH)
    
    saved = size_before - size_after
    saved_mb = saved / (1024 * 1024)
    
    print(f"\n✅ 压缩完成!")
    print(f"   压缩前: {size_before / (1024*1024):.2f} MB")
    print(f"   压缩后: {size_after / (1024*1024):.2f} MB")
    print(f"   节省: {saved_mb:.2f} MB")

def clean_old_backups(keep=5):
    """清理旧备份，只保留最新的N个"""
    backups = list_backups()
    
    if len(backups) <= keep:
        print(f"当前有 {len(backups)} 个备份，无需清理")
        return
    
    to_delete = backups[keep:]
    
    print(f"保留最新 {keep} 个备份，删除 {len(to_delete)} 个旧备份:")
    
    for backup in to_delete:
        try:
            os.remove(backup['path'])
            print(f"  ✅ 删除: {backup['file']}")
        except Exception as e:
            print(f"  ❌ 删除失败 {backup['file']}: {e}")

def remove_duplicates():
    """删除数据库中的重复数据"""
    print("检查重复数据...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查找重复的URL
    cursor.execute('''
        SELECT url, COUNT(*) as count
        FROM articles
        WHERE url IS NOT NULL AND url != ''
        GROUP BY url
        HAVING count > 1
    ''')
    
    duplicates = cursor.fetchall()
    
    if not duplicates:
        print("✅ 没有重复数据")
        conn.close()
        return
    
    print(f"⚠️  发现 {len(duplicates)} 个重复URL")
    
    # 删除重复项（保留最早的一条）
    for url, count in duplicates:
        cursor.execute('''
            DELETE FROM articles
            WHERE url = ?
            AND id NOT IN (
                SELECT MIN(id) FROM articles WHERE url = ?
            )
        ''', (url, url))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ 删除了 {deleted} 条重复记录")

# =========================
# 数据库统计
# =========================

def analyze_database():
    """分析数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总记录数
    cursor.execute('SELECT COUNT(*) FROM articles')
    total = cursor.fetchone()[0]
    
    # 表大小
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    db_size = cursor.fetchone()[0]
    
    # 索引数量
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
    index_count = cursor.fetchone()[0]
    
    # 最早和最新记录
    cursor.execute('SELECT MIN(date), MAX(date) FROM articles')
    date_range = cursor.fetchone()
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("数据库分析")
    print("=" * 60)
    print(f"\n📊 基本信息:")
    print(f"   总记录数: {total:,} 条")
    print(f"   数据库大小: {db_size / (1024*1024):.2f} MB")
    print(f"   索引数量: {index_count}")
    print(f"\n📅 时间范围:")
    print(f"   最早: {date_range[0]}")
    print(f"   最新: {date_range[1]}")

# =========================
# 主程序
# =========================

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("=" * 60)
        print("数据库备份和维护工具")
        print("=" * 60)
        print("\n用法:")
        print("  python db_backup.py backup            # 备份数据库")
        print("  python db_backup.py list              # 列出所有备份")
        print("  python db_backup.py restore <文件>    # 恢复备份")
        print("  python db_backup.py vacuum            # 压缩数据库")
        print("  python db_backup.py clean [保留数]    # 清理旧备份")
        print("  python db_backup.py dedup             # 删除重复数据")
        print("  python db_backup.py analyze           # 分析数据库")
        return
    
    command = sys.argv[1]
    
    if command == "backup":
        backup_database()
    
    elif command == "list":
        backups = list_backups()
        print(f"\n找到 {len(backups)} 个备份:")
        for i, backup in enumerate(backups, 1):
            print(f"\n{i}. {backup['file']}")
            print(f"   大小: {backup['size'] / (1024*1024):.2f} MB")
            print(f"   时间: {backup['time'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    elif command == "restore" and len(sys.argv) == 3:
        backup_path = sys.argv[2]
        restore_backup(backup_path)
    
    elif command == "vacuum":
        vacuum_database()
    
    elif command == "clean":
        keep = int(sys.argv[2]) if len(sys.argv) == 3 else 5
        clean_old_backups(keep)
    
    elif command == "dedup":
        remove_duplicates()
    
    elif command == "analyze":
        analyze_database()
    
    else:
        print("❌ 无效的命令")

if __name__ == "__main__":
    main()