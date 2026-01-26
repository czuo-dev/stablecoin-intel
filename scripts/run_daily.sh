#!/bin/bash
# 每日新闻收集和AI分析脚本

# 设置工作目录
cd /Users/changbaizuo_1/projects/stablecoin-intel

# 激活虚拟环境
source venv/bin/activate

# 记录开始时间
echo "=== $(date) ===" >> logs/cron.log

# 1. 运行 RSS 抓取器（免费，无限制）
echo "[RSS] 开始收集..." >> logs/cron.log
python scripts/rss_fetcher.py >> logs/cron.log 2>&1

# 2. 运行完整的每日任务（NewsAPI + AI分类）
echo "[Daily Job] 开始处理..." >> logs/cron.log
python scripts/daily_job.py >> logs/cron.log 2>&1

echo "[完成] $(date)" >> logs/cron.log
echo "" >> logs/cron.log
