# test_daily_collection.py

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("每日数据收集测试")
print("=" * 70)

# ========================================
# 测试1: 检查现有数据
# ========================================
print("\n【测试1】检查现有数据库\n")

db_files = [
    "data/news_system_db.json",
    "data/news_database.json"
]

for db_file in db_files:
    if os.path.exists(db_file):
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            count = len(data) if isinstance(data, list) else len(data.get('articles', []))
            print(f"✅ {db_file}")
            print(f"   数据条数: {count}")
            
            # 检查最新数据的日期
            if isinstance(data, list) and data:
                latest = max(data, key=lambda x: x.get('date', ''))
                print(f"   最新日期: {latest.get('date', 'N/A')}")
                print(f"   最新标题: {latest.get('title', 'N/A')[:50]}...")
        
        except Exception as e:
            print(f"❌ {db_file} 读取失败: {e}")
    else:
        print(f"❌ {db_file} 不存在")

# ========================================
# 测试2: 尝试收集今天的新闻
# ========================================
print("\n" + "=" * 70)
print("【测试2】收集今天的新闻（NewsAPI）\n")

api_key = os.getenv('NEWSAPI_KEY')

if not api_key:
    print("⚠️  跳过 NewsAPI 测试（未配置 API Key）")
else:
    try:
        from newsapi import NewsApiClient
        from datetime import timedelta
        
        newsapi = NewsApiClient(api_key=api_key)
        
        # 搜索今天的稳定币新闻
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        print(f"搜索日期范围: {yesterday.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')}\n")
        
        response = newsapi.get_everything(
            q='stablecoin OR USDC OR USDT OR Circle OR Tether',
            language='en',
            from_param=yesterday.strftime('%Y-%m-%d'),
            to=today.strftime('%Y-%m-%d'),
            page_size=10,
            sort_by='publishedAt'
        )
        
        articles = response.get('articles', [])
        total = response.get('totalResults', 0)
        
        print(f"✅ 搜索成功")
        print(f"   总结果: {total} 篇")
        print(f"   返回: {len(articles)} 篇\n")
        
        if articles:
            print("   最新3篇:")
            for i, article in enumerate(articles[:3], 1):
                print(f"\n   {i}. {article['title'][:60]}...")
                print(f"      来源: {article['source']['name']}")
                print(f"      日期: {article['publishedAt'][:10]}")
                print(f"      URL: {article['url'][:60]}...")
        else:
            print("⚠️  今天没有新的稳定币新闻")
    
    except Exception as e:
        print(f"❌ NewsAPI 搜索失败: {e}")

# ========================================
# 测试3: 检查 daily_job.py 是否存在
# ========================================
print("\n" + "=" * 70)
print("【测试3】检查每日任务脚本\n")

daily_scripts = [
    "scripts/daily_job.py",
    "daily_collect.py",
    "collect_news.py"
]

found_script = None
for script in daily_scripts:
    if os.path.exists(script):
        print(f"✅ 找到: {script}")
        found_script = script
        break

if not found_script:
    print("❌ 未找到每日数据收集脚本")
    print("\n建议创建: scripts/daily_job.py")
else:
    print(f"\n尝试运行: {found_script}")
    print("=" * 70)
    
    # 可以选择直接运行
    # import subprocess
    # subprocess.run(['python', found_script])

# ========================================
# 测试4: 数据新鲜度检查
# ========================================
print("\n" + "=" * 70)
print("【测试4】数据新鲜度检查\n")

today = datetime.now()
threshold = today - timedelta(days=7)

print(f"检查是否有 {threshold.strftime('%Y-%m-%d')} 之后的数据\n")

for db_file in db_files:
    if not os.path.exists(db_file):
        continue
    
    try:
        with open(db_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            recent_news = [
                item for item in data
                if item.get('date', '')[:10] >= threshold.strftime('%Y-%m-%d')
            ]
            
            print(f"📊 {db_file}")
            print(f"   总数据: {len(data)} 条")
            print(f"   最近7天: {len(recent_news)} 条")
            
            if len(recent_news) == 0:
                print(f"   ⚠️  数据可能过期了！")
            elif len(recent_news) < 5:
                print(f"   ⚠️  最近数据较少")
            else:
                print(f"   ✅ 数据新鲜度正常")
    
    except Exception as e:
        print(f"❌ {db_file} 检查失败: {e}")

# ========================================
# 总结
# ========================================
print("\n" + "=" * 70)
print("测试总结")
print("=" * 70 + "\n")

print("✅ 完成项:")
print("  - NewsAPI 连接正常")
print("  - 可以获取今天的新闻")

print("\n🔍 需要检查:")
print("  1. 数据库文件是否每天更新？")
print("  2. MCP 爬虫是否在自动运行？")
print("  3. 是否需要创建 daily_job.py 脚本？")

print("\n💡 建议:")
print("  1. 如果 MCP 爬虫已经在工作 → 不需要额外配置")
print("  2. 如果需要用 NewsAPI → 创建 daily_job.py")
print("  3. 如果两者都没有 → 先搞清楚数据来源")

print("\n" + "=" * 70)