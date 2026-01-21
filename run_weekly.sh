#!/bin/bash
# 运行周报生成脚本

cd "$(dirname "$0")"
python scripts/weekly_report.py
