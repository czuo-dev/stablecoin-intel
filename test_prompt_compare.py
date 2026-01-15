# test_prompt_compare.py

import json
from src.processors.batch_summarizer import BatchSummarizer
from src.processors.prompt_templates import PromptTemplates
from config import OPENAI_API_KEY

print("🔬 Prompt A/B 测试\n")
print("="*60)

# 准备测试数据（使用3-5篇真实文章）
test_articles = [
    {
        "title": "Hong Kong grants first stablecoin license",
        "description": "HKMA issues first stablecoin license under new regulatory framework",
        "source": {"name": "Reuters"},
        "publishedAt": "2025-01-15"
    },
    {
        "title": "EU finalizes MiCA stablecoin rules",
        "description": "European Union completes Markets in Crypto-Assets regulation for stablecoins",
        "source": {"name": "Bloomberg"},
        "publishedAt": "2025-01-14"
    },
    {
        "title": "Singapore MAS updates stablecoin framework",
        "description": "Monetary Authority of Singapore releases updated guidelines for stablecoin issuers",
        "source": {"name": "CoinDesk"},
        "publishedAt": "2025-01-14"
    }
]

# 准备文章文本
articles_text = "\n\n".join([
    f"标题: {a['title']}\n"
    f"来源: {a['source']['name']}\n"
    f"内容: {a['description']}"
    for a in test_articles
])

# 初始化
summarizer = BatchSummarizer(OPENAI_API_KEY)

# 测试1：基础Prompt
print("\n【测试 A】基础 Prompt")
print("="*60)

basic_prompt = PromptTemplates.get_prompt("policy", articles_text, len(test_articles), "basic")

response_a = summarizer.client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": basic_prompt}],
    max_tokens=400
)

result_a = response_a.choices[0].message.content
print(result_a)
print(f"\nToken使用: {response_a.usage.total_tokens}")

# 测试2：专家Prompt
print("\n" + "="*60)
print("\n【测试 B】专家 Prompt（政策分析）")
print("="*60)

expert_prompt = PromptTemplates.get_prompt("policy", articles_text, len(test_articles), "expert")

response_b = summarizer.client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "你是全球稳定币监管政策专家"},
        {"role": "user", "content": expert_prompt}
    ],
    max_tokens=800,
    temperature=0.3
)

result_b = response_b.choices[0].message.content
print(result_b)
print(f"\nToken使用: {response_b.usage.total_tokens}")

# 对比分析
print("\n" + "="*60)
print("\n📊 对比分析")
print("="*60)

print("\n请根据以下标准评分（1-10分）：\n")

print("1. 信息完整性")
print("   测试A: __ /10")
print("   测试B: __ /10\n")

print("2. 分析深度")
print("   测试A: __ /10")
print("   测试B: __ /10\n")

print("3. 结构化程度")
print("   测试A: __ /10")
print("   测试B: __ /10\n")

print("4. 可操作性（能否直接用于工作）")
print("   测试A: __ /10")
print("   测试B: __ /10\n")

# 成本对比
cost_a = (response_a.usage.total_tokens / 1000000) * 0.15
cost_b = (response_b.usage.total_tokens / 1000000) * 0.15

print("5. 成本对比")
print(f"   测试A: ${cost_a:.6f}")
print(f"   测试B: ${cost_b:.6f}")
print(f"   差异: ${abs(cost_b - cost_a):.6f}")

print("\n💡 建议：如果测试B的评分显著高于A，考虑使用专家级Prompt")