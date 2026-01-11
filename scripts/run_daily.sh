#!/bin/bash
# 每日新闻抓取脚本

# 设置工作目录
cd /Users/changbaizuo_1/projects/stablecoin-intel

# 激活虚拟环境
source venv/bin/activate

# 运行 RSS 抓取器
echo "=== $(date) ===" >> logs/cron.log
python scripts/rss_fetcher.py >> logs/cron.log 2>&1

# 可选：也运行 NewsAPI 抓取器
# python scripts/news_fetcher.py >> logs/cron.log 2>&1

echo "完成" >> logs/cron.log
echo "" >> logs/cron.log