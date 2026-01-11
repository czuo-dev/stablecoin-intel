#!/bin/bash
# 健康检查脚本
# 功能：检查自动化流程是否正常运行

PROJECT_DIR="/Users/changbaizuo_1/projects/stablecoin-intel"
cd "$PROJECT_DIR"

echo "=" "=" "=" "=" "="
echo "系统健康检查"
echo "=" "=" "=" "=" "="

# 检查1：最近一次运行是什么时候
echo ""
echo "1. 最近运行时间:"
if [ -f "logs/cron.log" ]; then
    tail -5 logs/cron.log
else
    echo "❌ 未找到日志文件"
fi

# 检查2：数据库是否在增长
echo ""
echo "2. 数据库状态:"
if [ -f "data/news_system_db.json" ]; then
    LINES=$(wc -l < data/news_system_db.json)
    SIZE=$(du -h data/news_system_db.json | cut -f1)
    echo "✅ 数据库存在"
    echo "   行数: $LINES"
    echo "   大小: $SIZE"
else
    echo "❌ 数据库不存在"
fi

# 检查3：今天有没有抓取新数据
echo ""
echo "3. 今日数据:"
TODAY=$(date +%Y-%m-%d)
RSS_FILES=$(find data/rss -name "*${TODAY}*.json" 2>/dev/null | wc -l)
RAW_FILES=$(find data/raw -name "*${TODAY}*.json" 2>/dev/null | wc -l)
echo "   RSS 文件: $RSS_FILES 个"
echo "   RAW 文件: $RAW_FILES 个"

if [ $RSS_FILES -eq 0 ] && [ $RAW_FILES -eq 0 ]; then
    echo "⚠️  警告：今天还没有新数据"
fi

# 检查4：磁盘空间
echo ""
echo "4. 磁盘空间:"
df -h "$PROJECT_DIR" | tail -1 | awk '{print "   使用: "$5" ("$3" / "$2")"}'

# 检查5：cron 任务
echo ""
echo "5. Cron 任务:"
CRON_COUNT=$(crontab -l 2>/dev/null | grep -v "^#" | grep -c "stablecoin")
if [ $CRON_COUNT -gt 0 ]; then
    echo "✅ 已设置 $CRON_COUNT 个定时任务"
    crontab -l | grep "stablecoin"
else
    echo "⚠️  未设置定时任务"
fi

echo ""
echo "=" "=" "=" "=" "="
echo "检查完成"
echo "=" "=" "=" "=" "="