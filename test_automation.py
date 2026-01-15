# test_automation.py

"""
测试自动化任务
"""

import sys
import os

print("🧪 测试自动化任务\n")
print("="*60)

# 测试1：每日任务
print("\n【测试1】每日任务")
print("-"*60)

choice = input("运行每日任务测试？(y/n): ")
if choice.lower() == 'y':
    print("\n正在运行每日任务...")
    os.system(f"{sys.executable} scripts/daily_job.py")
else:
    print("跳过每日任务测试")

# 测试2：周报任务
print("\n" + "="*60)
print("\n【测试2】周报任务")
print("-"*60)

choice = input("运行周报任务测试？(y/n): ")
if choice.lower() == 'y':
    print("\n正在运行周报任务...")
    os.system(f"{sys.executable} scripts/weekly_job.py")
else:
    print("跳过周报任务测试")

# 测试3：定时调度器（演示模式）
print("\n" + "="*60)
print("\n【测试3】定时调度器")
print("-"*60)

print("\n定时调度器配置:")
print("  - 每日任务: 周一至周五 09:00")
print("  - 周报任务: 每周一 10:00")
print("\n💡 启动调度器: python3 scripts/scheduler.py")
print("   （按 Ctrl+C 停止）")

print("\n" + "="*60)
print("\n✅ 测试完成！")
print("\n📚 使用指南:")
print("  1. 手动运行每日任务: python3 scripts/daily_job.py")
print("  2. 手动运行周报任务: python3 scripts/weekly_job.py")
print("  3. 启动定时调度器: python3 scripts/scheduler.py")
print("  4. 查看日志: ls -lh logs/")
print("\n💡 生产环境建议使用 cron（见下方配置）")