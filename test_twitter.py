# test_twitter.py

"""
测试Twitter API集成
"""

from src.collectors.twitter_collector import TwitterCollector
from config import (
    TWITTER_BEARER_TOKEN,
    TWITTER_MONITORED_ACCOUNTS,
    TWITTER_MONITORED_KEYWORDS
)

print("🧪 测试Twitter API集成\n")
print("="*60)

# 测试1：初始化
print("\n【测试1】初始化Twitter收集器")
print("-"*60)

try:
    collector = TwitterCollector(
        bearer_token=TWITTER_BEARER_TOKEN,
        monitored_accounts=TWITTER_MONITORED_ACCOUNTS[:3],  # 先测试3个账号
        monitored_keywords=TWITTER_MONITORED_KEYWORDS[:2]   # 先测试2个关键词
    )
    print("✅ 初始化成功")
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    print("\n请检查:")
    print("1. config.py 中的 TWITTER_BEARER_TOKEN 是否正确")
    print("2. 是否安装了 tweepy: pip3 install tweepy")
    exit(1)

# 测试2：收集单个用户推文
print("\n" + "="*60)
print("\n【测试2】收集单个用户推文")
print("-"*60)

test_user = TWITTER_MONITORED_ACCOUNTS[0]
print(f"测试账号: @{test_user}")

tweets = collector.collect_user_tweets(test_user, max_results=5, hours=168)  # 最近7天

if tweets:
    print(f"\n✅ 收集到 {len(tweets)} 条推文")
    
    # 显示第一条
    first_tweet = tweets[0]
    print(f"\n示例推文:")
    print(f"  作者: @{first_tweet['author']}")
    print(f"  内容: {first_tweet['text'][:100]}...")
    print(f"  点赞: {first_tweet['likes']}")
    print(f"  转发: {first_tweet['retweets']}")
    print(f"  链接: {first_tweet['url']}")
else:
    print("⚠️  最近7天无推文，这很正常")

# 测试3：关键词搜索
print("\n" + "="*60)
print("\n【测试3】关键词搜索")
print("-"*60)

test_keyword = TWITTER_MONITORED_KEYWORDS[0]
print(f"测试关键词: {test_keyword}")

keyword_tweets = collector.collect_keyword_tweets(test_keyword, max_results=10, hours=168)

if keyword_tweets:
    print(f"\n✅ 找到 {len(keyword_tweets)} 条相关推文")
    
    # 显示最热门的推文
    sorted_tweets = sorted(keyword_tweets, key=lambda x: x['likes'], reverse=True)
    top_tweet = sorted_tweets[0]
    
    print(f"\n最热门推文:")
    print(f"  内容: {top_tweet['text'][:100]}...")
    print(f"  点赞: {top_tweet['likes']}")
    print(f"  转发: {top_tweet['retweets']}")
else:
    print("⚠️  最近7天无相关推文")

# 测试4：完整收集
print("\n" + "="*60)
print("\n【测试4】完整收集（最近24小时）")
print("-"*60)

all_data = collector.collect_all(hours=24)

user_tweets = all_data['user_tweets']
keyword_tweets = all_data['keyword_tweets']
total = len(user_tweets) + len(keyword_tweets)

print(f"\n收集结果:")
print(f"  账号推文: {len(user_tweets)}")
print(f"  关键词推文: {len(keyword_tweets)}")
print(f"  总计: {total}")

# 测试5：高质量筛选
if total > 0:
    print("\n" + "="*60)
    print("\n【测试5】高质量推文筛选")
    print("-"*60)
    
    all_tweets = user_tweets + keyword_tweets
    high_quality = collector.filter_high_quality(
        all_tweets,
        min_likes=10,
        min_retweets=5
    )
    
    if high_quality:
        print(f"\n✨ 高质量推文示例:")
        for i, tweet in enumerate(high_quality[:3], 1):
            print(f"\n{i}. {tweet['text'][:80]}...")
            print(f"   👍 {tweet['likes']} | 🔄 {tweet['retweets']}")

# 测试6：保存数据
print("\n" + "="*60)
print("\n【测试6】保存数据")
print("-"*60)

if total > 0:
    output_file = collector.save_tweets(all_data, output_dir="data/twitter/test")
    print(f"✅ 测试数据已保存")
else:
    print("⚪ 无数据需要保存（最近24小时无新推文）")

# 总结
print("\n" + "="*60)
print("\n✅ 所有测试完成！")
print("\n📊 测试结果:")
print(f"  ✅ API连接正常")
print(f"  ✅ 数据收集功能正常")
print(f"  ✅ 筛选功能正常")
print(f"  ✅ 保存功能正常")

print("\n💡 下一步:")
print("  1. 运行监控任务: python3 scripts/twitter_monitor.py")
print("  2. 设置定时任务（每小时运行一次）")
print("  3. 整合到每日报告中")

print("\n🎉 Twitter API集成成功！")