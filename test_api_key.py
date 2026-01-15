# test_api_key.py - 测试 API Key 是否有效

import openai
from config import OPENAI_API_KEY

print("🧪 测试 OpenAI API 连接...\n")

try:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    # 发送一个最简单的请求
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Say 'API works!' in Chinese"}
        ],
        max_tokens=10
    )
    
    result = response.choices[0].message.content
    print(f"✅ API 连接成功！")
    print(f"回复: {result}")
    print(f"\n💰 本次调用成本: ~$0.00001 USD")
    
except openai.AuthenticationError as e:
    print(f"❌ 认证失败: API Key 无效")
    print(f"错误详情: {e}")
    print("\n请检查:")
    print("1. API Key 是否正确复制（没有多余空格）")
    print("2. API Key 是否已过期或被撤销")
    print("3. 访问 https://platform.openai.com/api-keys 创建新Key")
    
except openai.(f"❌ 其他错误: {e}")

