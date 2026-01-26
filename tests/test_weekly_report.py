# test_weekly_report.py

from src.processors.weekly_reporter import WeeklyReportGenerator
from config import OPENAI_API_KEY
from datetime import datetime

print("📰 测试周报生成器\n")
print("="*60)

# 初始化周报生成器
reporter = WeeklyReportGenerator(OPENAI_API_KEY)

# 步骤1：聚合本周数据
print("\n步骤1: 聚合本周数据")
print("-"*60)

aggregated_data = reporter.aggregate_weekly_data()

total_articles = sum(len(articles) for articles in aggregated_data.values())

if total_articles == 0:
    print("\n⚠️  没有找到本周数据")
    print("提示：请确保 data/processed/ 目录下有 categorized_news_*.json 文件")
    print("\n使用测试数据继续...")
    
    # 使用测试数据
    import json
    with open('data/processed/categorized_news_2025-01-15.json', 'r') as f:
        daily_data = json.load(f)
    
    # 复制几份模拟一周的数据
    aggregated_data = {
        "policy": daily_data.get("policy", []) * 2,
        "company": daily_data.get("company", []) * 2,
        "funding": daily_data.get("funding", []) * 2
    }
    
    total_articles = sum(len(articles) for articles in aggregated_data.values())
    print(f"测试数据总计: {total_articles} 篇")

# 步骤2：生成双语周报
print("\n" + "="*60)
print("\n步骤2: 生成双语周报（中文+西班牙语）")
print("-"*60)
print("⏳ 这可能需要30-60秒...\n")

reports = reporter.generate_weekly_report(
    aggregated_data,
    target_lang="es"
)

# 步骤3：保存周报
print("\n" + "="*60)
print("\n步骤3: 保存周报文件")
print("-"*60)

files = reporter.save_weekly_report(reports, target_lang="es")

# 显示生成的报告摘要
print("\n" + "="*60)
print("\n📄 周报预览")
print("="*60)

print("\n【中文版】前500字:")
print("-"*60)
print(reports["zh"][:500])
print("...")

print("\n【西班牙语版】前500字:")
print("-"*60)
print(reports["es"][:500])
print("...")

# 统计信息
print("\n" + "="*60)
print("\n📊 统计信息")
print("-"*60)

zh_length = len(reports["zh"])
es_length = len(reports["es"])
combined_length = len(reports["combined"])

print(f"中文版长度: {zh_length:,} 字符")
print(f"西班牙语版长度: {es_length:,} 字符")
print(f"双语合并版长度: {combined_length:,} 字符")

# 成本估算
api_calls = len([cat for cat, arts in aggregated_data.items() if arts])  # 每个类别一次调用
estimated_cost = api_calls * 0.001  # 每次调用约$0.001

print(f"\n💰 成本估算:")
print(f"   API调用次数: ~{api_calls}")
print(f"   预计成本: ${estimated_cost:.4f} USD")

print("\n" + "="*60)
print("\n✅ 周报生成完成！")
print("\n查看文件:")
print(f"   中文版: {files['zh']}")
print(f"   西班牙语版: {files['es']}")
print(f"   双语版: {files['combined']}")

print("\n💡 用Cursor或VS Code打开查看效果更佳")