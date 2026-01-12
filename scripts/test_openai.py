# 测试OpenAI API连接

from openai import OpenAI
import os

# 加载API Key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ 未找到API Key")
    print("请在.env文件中设置 OPENAI_API_KEY")
    exit(1)

# 创建客户端
client = OpenAI(api_key=api_key)

# 测试API调用
print("测试OpenAI API连接...")

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # 或使用 gpt-4
        messages=[
            {"role": "user", "content": "你好，请用一句话介绍你自己。"}
        ],
        max_tokens=100
    )
    
    reply = response.choices[0].message.content
    print(f"\n✅ API连接成功！")
    print(f"\nGPT回复：{reply}")
    print(f"\n使用的模型：{response.model}")
    print(f"Token使用：{response.usage.total_tokens}")
    
except Exception as e:
    print(f"\n❌ API连接失败: {e}")