# 数据恢复工具
# 功能：从备份恢复数据库

import json
import os
import shutil
from datetime import datetime

def list_backups():
    """列出所有备份文件"""
    backups = []
    
    for root, dirs, files in os.walk("data"):
        for file in files:
            if "backup" in file and file.endswith(".json"):
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                mtime = os.path.getmtime(filepath)
                mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                backups.append({
                    "path": filepath,
                    "size": size,
                    "modified": mtime_str
                })
    
    return backups

def restore_backup(backup_path, target_path):
    """恢复备份"""
    try:
        shutil.copy2(backup_path, target_path)
        print(f"✅ 已恢复: {backup_path} → {target_path}")
        return True
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False

def main():
    print("=" * 60)
    print("数据恢复工具")
    print("=" * 60)
    
    backups = list_backups()
    
    if not backups:
        print("\n未找到备份文件")
        return
    
    print(f"\n找到 {len(backups)} 个备份文件:")
    for i, backup in enumerate(backups, 1):
        print(f"\n{i}. {backup['path']}")
        print(f"   大小: {backup['size']} 字节")
        print(f"   修改时间: {backup['modified']}")
    
    print("\n提示：手动恢复备份的方法:")
    print("cp data/xxx_backup.json data/xxx.json")

if __name__ == "__main__":
    main()