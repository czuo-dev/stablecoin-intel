# test_batch_simple.py

import os
from pathlib import Path
from src.processors.batch_summarizer import BatchSummarizer

# 加载 .env 文件
def load_env_file():
    """从 .env 文件加载环境变量"""
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                # 解析 KEY=VALUE 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # 如果环境变量未设置，则使用 .env 中的值
                    if key and not os.getenv(key):
                        os.environ[key] = value

# 加载 .env 文件
load_env_file()

# 获取 API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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

if not OPENAI_API_KEY:
    print("❌ 未找到 OPENAI_API_KEY")
    print("请在 .env 文件中设置 OPENAI_API_KEY 或设置环境变量")
    exit(1)

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