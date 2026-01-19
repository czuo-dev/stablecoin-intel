# scripts/setup_cron.sh

#!/bin/bash

# 获取项目绝对路径
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
echo "项目目录: $PROJECT_DIR"

# 生成Cron任务配置
cat > /tmp/stablecoin_cron.txt << EOF
# 稳定币情报系统 - 定时任务

# 每天早上9点运行数据收集
0 9 * * * cd $PROJECT_DIR && $PROJECT_DIR/venv/bin/python scripts/daily_job_with_logging.py >> logs/cron.log 2>&1

# 每周一早上10点生成周报（Week 10 Day 2-3会实现）
# 0 10 * * 1 cd $PROJECT_DIR && $PROJECT_DIR/venv/bin/python scripts/weekly_report.py >> logs/cron.log 2>&1

# 测试用：每小时运行一次（可以先用这个测试）
# 0 * * * * cd $PROJECT_DIR && $PROJECT_DIR/venv/bin/python scripts/daily_job_with_logging.py >> logs/cron.log 2>&1
EOF

echo ""
echo "Cron配置已生成: /tmp/stablecoin_cron.txt"
echo ""
cat /tmp/stablecoin_cron.txt
echo ""
echo "要安装这些定时任务，运行:"
echo "  crontab /tmp/stablecoin_cron.txt"
echo ""
echo "查看当前的Cron任务:"
echo "  crontab -l"
echo ""
echo "取消所有Cron任务:"
echo "  crontab -r"