# test_smart_classifier.py

from src.processors.smart_classifier import SmartClassifier
from config import OPENAI_API_KEY

print("🤖 测试AI智能分类器\n")
print("="*60)

# 初始化分类器
classifier = SmartClassifier(OPENAI_API_KEY)

# 测试文章
test_articles = [
    {
        "title": "Circle获得香港金管局首个稳定币发行牌照",
        "description": "香港金融管理局宣布，Circle成为首家获得稳定币发行牌照的公司，这标志着香港稳定币监管框架正式落地。"
    },
    {
        "title": "PayPal扩展PYUSD到欧洲五国",
        "description": "PayPal宣布其稳定币PYUSD将在德国、法国、意大利、西班牙和荷兰推出，进一步扩大全球市场布局。"
    },
    {
        "title": "稳定币基础设施公司Bridge完成5800万美元B轮融资",
        "description": "由Ribbit Capital和Index Ventures领投，Bridge计划用资金加速产品开发和全球扩张。"
    },
    {
        "title": "美联储主席警告稳定币可能带来系统性风险",
        "description": "鲍威尔在国会听证会上表示，稳定币需要明确的监管框架，以防止潜在的金融稳定风险。"
    },
    {
        "title": "Visa推出基于USDC的跨境支付解决方案",
        "description": "Visa与Circle合作，利用USDC实现更快速、低成本的跨境B2B支付。"
    }
]

# 测试1：单个分类
print("\n【测试1】单篇文章AI分类")
print("-"*60)

article = test_articles[0]
print(f"\n文章标题: {article['title']}")
print(f"文章内容: {article['description'][:50]}...")

result = classifier.classify_article(article)

print(f"\n分类结果:")
print(f"  主分类: {result['primary_category']}")
print(f"  置信度: {result['confidence']:.2f}")
print(f"  重要性: {result['importance']}/10")
print(f"  标签: {', '.join(result['tags'])}")
print(f"  理由: {result.get('reasoning', 'N/A')}")

# 测试2：批量分类（对比单个和批量的速度）
print("\n" + "="*60)
print("\n【测试2】批量分类测试")
print("-"*60)

import time

# 方式1：逐个分类
print("\n方式1: 逐个分类（5篇）")
start_time = time.time()
individual_results = []
for article in test_articles:
    result = classifier.classify_article(article)
    individual_results.append(result)
individual_time = time.time() - start_time

print(f"  耗时: {individual_time:.2f}秒")
print(f"  平均: {individual_time/len(test_articles):.2f}秒/篇")

# 方式2：批量分类
print("\n方式2: 批量分类（5篇）")
start_time = time.time()
batch_results = classifier.batch_classify(test_articles)
batch_time = time.time() - start_time

print(f"  耗时: {batch_time:.2f}秒")
print(f"  平均: {batch_time/len(test_articles):.2f}秒/篇")

print(f"\n⚡ 速度提升: {(individual_time/batch_time):.1f}x")

# 测试3：显示所有分类结果
print("\n" + "="*60)
print("\n【测试3】所有文章分类结果")
print("-"*60)

category_emojis = {
    "policy": "📜",
    "company": "🏢",
    "funding": "💰"
}

for i, result in enumerate(batch_results, 1):
    article = result.get("article", test_articles[i-1])
    category = result.get("primary_category", "unknown")
    emoji = category_emojis.get(category, "📌")
    
    print(f"\n{i}. {emoji} {article['title'][:50]}...")
    print(f"   分类: {category} | 置信度: {result.get('confidence', 0):.2f} | 重要性: {result.get('importance', 5)}/10")
    print(f"   标签: {', '.join(result.get('tags', [])[:5])}")

# 测试4：对比关键词分类和AI分类
print("\n" + "="*60)
print("\n【测试4】AI分类 vs 关键词分类对比")
print("-"*60)

# 模拟关键词分类结果
keyword_results = ["policy", "company", "funding", "policy", "company"]

matches = 0
for i, (ai_result, keyword_result) in enumerate(zip(batch_results, keyword_results), 1):
    article = ai_result.get("article", test_articles[i-1])
    ai_category = ai_result.get("primary_category", "unknown")
    
    match = "✅" if ai_category == keyword_result else "❌"
    if ai_category == keyword_result:
        matches += 1
    
    print(f"\n{i}. {article['title'][:40]}...")
    print(f"   关键词分类: {keyword_result}")
    print(f"   AI分类: {ai_category} (置信度: {ai_result.get('confidence', 0):.2f})")
    print(f"   {match} {'一致' if ai_category == keyword_result else '不一致'}")
    if ai_category != keyword_result:
        print(f"   AI理由: {ai_result.get('reasoning', 'N/A')}")

accuracy = (matches / len(batch_results)) * 100
print(f"\n一致率: {accuracy:.1f}%")

# 成本估算
print("\n" + "="*60)
print("\n💰 成本估算")
print("-"*60)

single_cost = 0.0001  # 单个分类约$0.0001
batch_cost = 0.0002  # 批量分类（5篇）约$0.0002

print(f"单个分类: {len(test_articles)} × ${single_cost} = ${len(test_articles) * single_cost:.4f}")
print(f"批量分类: 1批(5篇) × ${batch_cost} = ${batch_cost:.4f}")
print(f"节省: {((len(test_articles) * single_cost - batch_cost) / (len(test_articles) * single_cost) * 100):.0f}%")

print("\n✅ 测试完成！")
print("\n💡 建议：在实际使用中使用 batch_classify() 方法节省成本和时间")