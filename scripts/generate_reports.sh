#!/bin/bash
# 手动生成各类报告

PROJECT_DIR="/Users/changbaizuo_1/projects/stablecoin-intel"
cd "$PROJECT_DIR"
source venv/bin/activate

echo "=========================================="
echo "报告生成工具"
echo "=========================================="

echo ""
echo "1. 数据分析报告"
python scripts/data_analyzer.py

echo ""
echo "2. 周报"
python scripts/weekly_report.py

echo ""
echo "=========================================="
echo "所有报告生成完成！"
echo "=========================================="
echo ""
echo "查看报告:"
echo "  周报: reports/"
ls -lh reports/