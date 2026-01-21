# test_newsapi_simple.py
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("NewsAPI 连接测试")
print("=" * 60)

# 1. 检查 API Key
api_key = os.getenv('NEWSAPI_KEY')
print(f"\n1️⃣ API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'NOT FOUND'}")

if not api_key:
    print("❌ 没有找到 NEWSAPI_KEY")
    print("\n解决方案：")
    print("1. 注册 NewsAPI: https://newsapi.org/register")
    print("2. 创建 .env 文件，添加: NEWSAPI_KEY=你的密钥")
    exit(1)

# 2. 测试连接
print("\n2️⃣ 测试 NewsAPI 连接...\n")

try:
    from newsapi import NewsApiClient
    newsapi = NewsApiClient(api_key=api_key)
    print("✅ NewsAPI 客户端初始化成功")
except ImportError:
    print("❌ newsapi-python 未安装")
    print("\n解决方案：")
    print("pip install newsapi-python")
    exit(1)
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    exit(1)

# 3. 测试搜索
print("\n3️⃣ 测试搜索 'stablecoin'...\n")

try:
    response = newsapi.get_everything(
        q='stablecoin',
        language='en',
        page_size=5,
        sort_by='publishedAt'
    )
    
    total = response.get('totalResults', 0)
    articles = response.get('articles', [])
    
    print(f"✅ 搜索成功！")
    print(f"   总结果: {total} 篇")
    print(f"   返回: {len(articles)} 篇")
    
    if articles:
        print(f"\n   最新文章:")
        for i, article in enumerate(articles[:3], 1):
            print(f"   {i}. {article['title'][:60]}...")
            print(f"      来源: {article['source']['name']}")
            print(f"      日期: {article['publishedAt'][:10]}")
    
    print("\n🎉 NewsAPI 工作正常！")

except Exception as e:
    print(f"❌ 搜索失败: {e}")
    print(f"\n可能的原因:")
    print("1. API Key 无效（检查是否复制完整）")
    print("2. 超过每日限制（免费版 100次/天）")
    print("3. 网络连接问题")
    
    # 如果是 401 错误
    if "401" in str(e):
        print("\n❌ 401 错误 = API Key 无效")
        print("   去 https://newsapi.org/account 检查你的 API Key")
    
    # 如果是 429 错误
    if "429" in str(e):
        print("\n❌ 429 错误 = 超过请求限制")
        print("   免费版每天只能请求 100 次")

print("\n" + "=" * 60)