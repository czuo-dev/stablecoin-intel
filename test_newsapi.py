# test_newsapi.py

from newsapi import NewsApiClient
from config import NEWSAPI_KEY
from datetime import datetime, timedelta

def test_newsapi_connection():
    """测试NewsAPI连接"""
    
    print("🔍 测试NewsAPI连接...\n")
    
    # 初始化客户端
    try:
        newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
        print("✅ NewsAPI客户端初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False
    
    # 测试搜索
    try:
        print("\n📰 测试搜索 'stablecoin' 关键词...")
        
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        articles = newsapi.get_everything(
            q='stablecoin',
            language='en',
            sort_by='publishedAt',
            page_size=5,
            from_param=from_date
        )
        
        print(f"✅ 搜索成功！找到 {articles['totalResults']} 篇相关文章")
        print(f"\n前5篇文章预览:")
        
        for i, article in enumerate(articles['articles'][:5], 1):
            print(f"\n【{i}】{article['title']}")
            print(f"    来源: {article['source']['name']}")
            print(f"    日期: {article['publishedAt'][:10]}")
            print(f"    链接: {article['url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return False

if __name__ == '__main__':
    success = test_newsapi_connection()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 NewsAPI配置成功！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 配置失败，请检查API密钥")
        print("=" * 60)