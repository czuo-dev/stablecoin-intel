# test_batch_simple.py

from src.processors.batch_summarizer import BatchSummarizer
from config import OPENAI_API_KEY

# 创建测试数据（模拟文章）
test_articles = [
    {
        "title": "PayPal expands PYUSD to Europe",
        "description": "PayPal announced expansion of its stablecoin PYUSD to European markets",
        "source": {"name": "Reuters"},
        "publishedAt": "2025-01-15",
        "url": "https://example.com/1"
    },
    {
        "title": "Hong Kong issues stablecoin license to Circle",
        "description": "HKMA grants first stablecoin license to Circle under new regulatory framework",
        "source": {"name": "Bloomberg"},
        "publishedAt": "2025-01-15",
        "url": "https://example.com/2"
    }
]

print("🚀 开始测试批量摘要器...\n")

# 步骤1：初始化
print("步骤1: 初始化BatchSummarizer")
summarizer = BatchSummarizer(OPENAI_API_KEY)
print("✅ 初始化成功\n")

# 步骤2：测试单批次摘要
print("步骤2: 测试摘要生成")
print(f"处理 {len(test_articles)} 篇测试文章...")

summary = summarizer.summarize_batch(test_articles, category="company")

if summary:
    print("\n✅ 摘要生成成功！")
    print("\n" + "="*60)
    print("生成的摘要：")
    print("="*60)
    print(summary)
    print("="*60)
else:
    print("\n❌ 摘要生成失败")

print("\n🎉 测试完成！")
