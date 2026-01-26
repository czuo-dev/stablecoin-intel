# test_batch_real.py

import json
import os
from src.processors.batch_summarizer import BatchSummarizer
from config import OPENAI_API_KEY
from datetime import datetime

# 找到最新的数据文件
data_files = [f for f in os.listdir('data/processed/') if f.startswith('categorized_news')]

if not data_files:
    print("❌ 没有找到数据文件")
    print("请先运行数据收集脚本")
    exit(1)

# 使用最新的文件
latest_file = sorted(data_files)[-1]
file_path = f'data/processed/{latest_file}'

print(f"📁 读取数据: {file_path}\n")

# 加载数据
with open(file_path, 'r', encoding='utf-8') as f:
    articles_by_category = json.load(f)

# 显示数据统计
print("📊 数据统计:")
for category, articles in articles_by_category.items():
    print(f"  {category}: {len(articles)} 篇")
print()

# 初始化摘要器
print("🚀 开始生成日报...\n")
summarizer = BatchSummarizer(OPENAI_API_KEY)

# 生成报告
report = summarizer.generate_daily_report(articles_by_category)

# 保存报告
today = datetime.now().strftime('%Y-%m-%d')
report_path = f'reports/daily_brief_{today}.md'

# 确保reports目录存在
os.makedirs('reports', exist_ok=True)

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n✅ 报告已保存: {report_path}")

# 显示成本估算
total_articles = sum(len(articles) for articles in articles_by_category.values())
batches = (total_articles + 9) // 10
estimated_cost = batches * 0.0002

print(f"\n📊 统计信息:")
print(f"   总文章数: {total_articles}")
print(f"   处理批次: {batches}")
print(f"   预计成本: ${estimated_cost:.4f} USD")

# 预览报告前500字符
print(f"\n📄 报告预览:")
print("="*60)
print(report[:500])
print("...")
print("="*60)
