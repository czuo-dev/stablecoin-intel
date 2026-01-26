#!/bin/bash
# 周报生成脚本 - 每周日运行

# 设置工作目录
cd /Users/changbaizuo_1/projects/stablecoin-intel

# 激活虚拟环境
source venv/bin/activate

# 获取周数
WEEK_NUM=$(date +%W)
LOG_FILE="logs/weekly_$(date +%Y)-W${WEEK_NUM}.log"

# 记录开始时间
echo "=== 周报生成 $(date) ===" >> "$LOG_FILE"

# 运行周报生成
python scripts/weekly_job.py >> "$LOG_FILE" 2>&1

echo "[完成] $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
