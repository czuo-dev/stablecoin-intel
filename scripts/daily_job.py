# scripts/daily_job.py

"""
每日数据收集 - 简化版
直接从 NewsAPI 收集新闻，不使用复杂的收集器
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def collect_daily_news():
    """收集今天的新闻"""
    
    print("=" * 70)
    print(f"📅 每日数据收集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    # 检查 API Key
    api_key = os.getenv('NEWSAPI_KEY')
    if not api_key:
        print("❌ 未配置 NEWSAPI_KEY")
        print("\n请在 .env 文件中添加:")
        print("NEWSAPI_KEY=你的密钥")
        return
    
    print(f"✅ API Key: {api_key[:10]}...{api_key[-5:]}\n")
    
    # 导入 NewsAPI
    try:
        from newsapi import NewsApiClient
        newsapi = NewsApiClient(api_key=api_key)
        print("✅ NewsAPI 客户端初始化成功\n")
    except ImportError:
        print("❌ 请先安装: pip install newsapi-python")
        return
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 计算日期
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    print(f"🔍 搜索日期: {yesterday.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')}\n")
    
    # 搜索新闻
    try:
        print("📡 正在搜索稳定币新闻...\n")
        
        response = newsapi.get_everything(
            q='stablecoin OR USDC OR USDT OR Circle OR Tether',
            language='en',
            from_param=yesterday.strftime('%Y-%m-%d'),
            to=today.strftime('%Y-%m-%d'),
            page_size=50,
            sort_by='publishedAt'
        )
        
        articles = response.get('articles', [])
        total_results = response.get('totalResults', 0)
        
        print(f"✅ 搜索成功")
        print(f"   总结果: {total_results} 篇")
        print(f"   返回: {len(articles)} 篇\n")
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}\n")
        
        if "401" in str(e):
            print("💡 401 错误 = API Key 无效")
            print("   请检查 .env 文件中的 NEWSAPI_KEY")
        elif "429" in str(e):
            print("💡 429 错误 = 超过请求限制")
            print("   免费版每天只能请求 100 次")
        
        return
    
    # 加载现有数据
    db_file = 'data/news_system_db.json'
    os.makedirs('data', exist_ok=True)
    
    existing_data = []
    if os.path.exists(db_file):
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print(f"📂 现有数据: {len(existing_data)} 条\n")
        except:
            print("⚠️  无法读取现有数据，将创建新数据库\n")
    
    # 处理新数据
    print("🔄 处理新数据...\n")
    
    existing_urls = {item.get('url') for item in existing_data}
    new_count = 0
    
    for article in articles:
        # 跳过重复
        if article['url'] in existing_urls:
            continue
        
        # 简单分类
        text = (article['title'] + ' ' + article.get('description', '')).lower()
        
        if any(kw in text for kw in ['regulation', 'ban', 'sec', 'license']):
            category = '📋 政策监管'
        elif any(kw in text for kw in ['partnership', 'launch', 'acquire']):
            category = '🏢 公司动态'
        elif any(kw in text for kw in ['funding', 'raise', 'invest']):
            category = '💰 融资并购'
        else:
            category = '📰 行业新闻'
        
        # 提取关键词
        keywords = []
        for kw in ['USDC', 'USDT', 'Circle', 'Tether', 'SEC', 'MAS']:
            if kw.lower() in text:
                keywords.append(kw)
        
        # 添加到数据库
        existing_data.append({
            'title': article['title'],
            'source': article['source']['name'],
            'url': article['url'],
            'date': article['publishedAt'][:10],
            'category': category,
            'keywords': keywords,
            'description': article.get('description', ''),
            'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        new_count += 1
    
    print(f"🆕 新增数据: {new_count} 条\n")
    
    # 清理旧数据（只保留30天）
    cutoff_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    existing_data = [
        item for item in existing_data
        if item.get('date', '') >= cutoff_date
    ]
    
    # 排序（最新的在前）
    existing_data.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    # 保存
    try:
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 数据已保存: {db_file}")
        print(f"   总数据: {len(existing_data)} 条")
        print(f"   新增: {new_count} 条")
        print(f"   日期范围: {cutoff_date} 至今\n")
    
    except Exception as e:
        print(f"❌ 保存失败: {e}\n")
        return
    
    # 显示最新3条
    if new_count > 0:
        print("📰 最新添加的新闻:\n")
        for i, item in enumerate(existing_data[:min(3, new_count)], 1):
            print(f"   {i}. [{item['category']}] {item['title'][:60]}...")
            print(f"      来源: {item['source']} | 日期: {item['date']}\n")
    
    print("=" * 70)
    print("✅ 每日任务完成")
    print("=" * 70)

if __name__ == '__main__':
    collect_daily_news()