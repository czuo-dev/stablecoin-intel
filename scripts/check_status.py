# scripts/check_status.py

"""
检查系统运行状态
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

def check_system_status():
    """检查系统各组件状态"""
    
    print("=" * 70)
    print("🔍 系统状态检查")
    print("=" * 70 + "\n")
    
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 检查今天的数据
    print("📅 今天的数据:")
    files_today = {
        "原始新闻": f"data/raw/newsapi_raw_{today}.json",
        "分类新闻": f"data/processed/categorized_news_{today}.json",
        "整合数据": f"data/processed/integrated_data_{today}.json",
    }
    
    for name, path in files_today.items():
        if os.path.exists(path):
            size = os.path.getsize(path) / 1024  # KB
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            age = datetime.now() - mtime
            
            print(f"  ✅ {name}: {size:.1f}KB")
            print(f"     更新于: {mtime.strftime('%H:%M:%S')}")
            print(f"     距今: {age.seconds // 3600}小时{(age.seconds % 3600) // 60}分钟")
            
            # 显示数据统计
            if path.endswith('integrated_data' + f'_{today}.json'):
                with open(path, 'r') as f:
                    data = json.load(f)
                print(f"     数据量: {data['total_items']} 条")
        else:
            print(f"  ❌ {name}: 不存在")
    
    # 检查日志
    print(f"\n📋 最近的日志:")
    log_dir = Path('logs')
    if log_dir.exists():
        log_files = sorted(log_dir.glob('daily_job_*.log'), reverse=True)
        for log_file in log_files[:3]:
            size = log_file.stat().st_size / 1024
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            print(f"  📄 {log_file.name}: {size:.1f}KB")
            print(f"     更新于: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 检查是否有错误
            with open(log_file, 'r') as f:
                content = f.read()
                error_count = content.count('[ERROR]')
                success = '✅ 每日任务完成' in content
                
                if success:
                    print(f"     状态: ✅ 成功")
                elif error_count > 0:
                    print(f"     状态: ❌ 失败 ({error_count}个错误)")
                else:
                    print(f"     状态: ⚠️  未完成")
    else:
        print("  ❌ 日志目录不存在")
    
    # 检查Cron状态
    print(f"\n⏰ Cron任务状态:")
    import subprocess
    try:
        result = subprocess.run(['crontab', '-l'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        if result.returncode == 0 and 'stablecoin' in result.stdout.lower():
            print("  ✅ Cron任务已配置")
            # 显示相关任务
            for line in result.stdout.split('\n'):
                if 'stablecoin' in line.lower() or 'daily_job' in line:
                    print(f"     {line}")
        else:
            print("  ⚠️  Cron任务未配置")
    except Exception as e:
        print(f"  ❌ 无法检查Cron: {e}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    check_system_status()