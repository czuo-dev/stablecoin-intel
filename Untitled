# test_trend_analysis.py

import json
import os
from src.processors.smart_classifier import SmartClassifier
from src.processors.trend_analyzer import TrendAnalyzer
from config import OPENAI_API_KEY

print("📊 测试趋势分析器\n")
print("="*60)

# 初始化
classifier = SmartClassifier(OPENAI_API_KEY)
analyzer = TrendAnalyzer()

# 步骤1：加载并分类文章
print("\n步骤1: 加载和分类文章")
print("-"*60)

# 尝试加载真实数据
data_file = 'data/processed/categorized_news_2025-01-15.json'

if os.path.exists(data_file):
    print(f"加载数据: {data_file}")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 合并所有类别的文章
    all_articles = []
    for category, articles in data.items():
        all_articles.extend(articles[:5])  # 每个类别取5篇，避免成本太高
    
    print(f"总共: {len(all_articles)} 篇文章")
else:
    # 使用测试数据
    print("⚠️  未找到数据文件，使用测试数据")
    all_articles = [
        {
            "title": "Circle获得香港金管局首个稳定币牌照",
            "description": "香港金融管理局宣布Circle成为首家获得牌照的公司"
        },
        {
            "title": "PayPal扩展PYUSD到欧洲市场",
            "description": "PayPal在德国和法国推出PYUSD稳定币"
        },
        {
            "title": "Bridge完成5000万美元B轮融资",
            "description": "由Sequoia领投的稳定币基础设施融资"
        },
        {
            "title": "新加坡MAS更新稳定币监管框架",
            "description": "MAS发布更新的稳定币发行指南"
        },
        {
            "title": "Visa与Circle合作推出USDC支付",
            "description": "Visa利用USDC实现跨境支付"
        },
        {
            "title": "香港HKMA批准第二家稳定币申请",
            "description": "继Circle之后，又一家公司获得牌照"
        },
        {
            "title": "欧盟MiCA法规正式生效",
            "description": "欧盟加密资产监管框架开始实施"
        },
        {
            "title": "Tether发布储备金审计报告",
            "description": "USDT发行方公布最新资产审计结果"
        }
    ]

# 进行AI分类
print("\n正在进行AI分类...")
classified_articles = classifier.batch_classify(all_articles)

print(f"✅ 分类完成: {len(classified_articles)} 篇")

# 步骤2：分析标签趋势
print("\n" + "="*60)
print("\n步骤2: 分析标签趋势")
print("-"*60)

tags_analysis = analyzer.analyze_tags(classified_articles, top_n=10)

print(f"\n📊 标签统计:")
print(f"  总标签数: {tags_analysis['total_tags']}")
print(f"  独特标签: {tags_analysis['unique_tags']}")

print(f"\n🔥 Top 10 热门标签:")
for i, tag_info in enumerate(tags_analysis["top_tags"], 1):
    tag = tag_info["tag"]
    count = tag_info["count"]
    pct = tag_info["percentage"]
    
    # 火焰emoji
    if count >= 5:
        emoji = "🔥🔥🔥"
    elif count >= 3:
        emoji = "🔥🔥"
    else:
        emoji = "🔥"
    
    print(f"  {i}. {emoji} {tag}: {count}次 ({pct}%)")

# 步骤3：分析类别分布
print("\n" + "="*60)
print("\n步骤3: 分析类别分布")
print("-"*60)

categories_analysis = analyzer.analyze_categories(classified_articles)

print(f"\n总文章数: {categories_analysis['total']}")
print(f"\n类别分布:")

category_names = {
    "policy": "📜 政策监管",
    "company": "🏢 公司动态",
    "funding": "💰 融资事件"
}

for category, data in categories_analysis["distribution"].items():
    name = category_names.get(category, category)
    count = data["count"]
    pct = data["percentage"]
    
    # 进度条
    bar_length = int(pct / 5)
    bar = "█" * bar_length + "░" * (20 - bar_length)
    
    print(f"\n{name}")
    print(f"  {bar} {count}篇 ({pct}%)")

# 步骤4：分析重要性
print("\n" + "="*60)
print("\n步骤4: 分析新闻重要性")
print("-"*60)

importance_analysis = analyzer.analyze_importance(classified_articles)

print(f"\n重要性分布:")
print(f"  🔴 高重要性 (≥8分): {importance_analysis['high_importance']}篇")
print(f"  🟡 中等重要性 (5-7分): {importance_analysis['medium_importance']}篇")
print(f"  🟢 低重要性 (<5分): {importance_analysis['low_importance']}篇")
print(f"  📊 平均重要性: {importance_analysis['average_importance']}/10")

if importance_analysis["top_important_articles"]:
    print(f"\n🌟 最重要的新闻:")
    for i, article in enumerate(importance_analysis["top_important_articles"], 1):
        title = article["title"]
        importance = article["importance"]
        tags = ", ".join(article["tags"])
        
        print(f"\n  {i}. {title}")
        print(f"     重要性: {importance}/10 | 标签: {tags}")

# 步骤5：生成完整趋势报告
print("\n" + "="*60)
print("\n步骤5: 生成完整趋势报告")
print("-"*60)

report = analyzer.generate_trend_report(classified_articles)

# 保存报告
os.makedirs('reports', exist_ok=True)
report_file = 'reports/trend_analysis.md'

with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n✅ 趋势报告已保存: {report_file}")

# 显示报告预览
print(f"\n【报告预览】")
print("-"*60)
print(report[:800])
print("\n...")

# 步骤6：识别新兴趋势（对比功能演示）
print("\n" + "="*60)
print("\n步骤6: 新兴趋势识别（演示）")
print("-"*60)

# 模拟上周的标签
previous_tags = ["Circle", "USDC", "监管", "PayPal", "香港"] * 2
current_tags = []
for article in classified_articles:
    current_tags.extend(article.get("tags", []))

emerging_trends = analyzer.identify_emerging_trends(current_tags, previous_tags)

print(f"\n📈 新兴趋势 Top 5:")
for i, trend in enumerate(emerging_trends[:5], 1):
    tag = trend["tag"]
    current = trend["current_count"]
    previous = trend["previous_count"]
    growth = trend["growth"]
    is_new = trend["is_new"]
    
    if is_new:
        print(f"  {i}. 🆕 {tag}: {current}次提及 (全新标签)")
    else:
        print(f"  {i}. 📈 {tag}: {current}次提及 (增长{growth:.0f}%, 上周{previous}次)")

# 总结
print("\n" + "="*60)
print("\n✅ 趋势分析完成！")
print("\n📄 生成的文件:")
print(f"   - {report_file}")

print("\n💡 建议:")
print("   - 每周运行一次趋势分析")
print("   - 对比不同时期的趋势变化")
print("   - 关注新兴标签和快速增长的话题")

# 成本统计
print("\n💰 本次测试成本:")
api_calls = (len(all_articles) + 4) // 5  # 批量分类，每批5篇
estimated_cost = api_calls * 0.0002
print(f"   分类{len(all_articles)}篇文章")
print(f"   API调用: ~{api_calls}次")
print(f"   预计成本: ${estimated_cost:.4f}")

print("\n🎉 测试完成！")