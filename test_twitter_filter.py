# test_twitter_filter.py

import json
import os
import glob
from src.collectors.twitter_filter import TwitterFilter

# 查找可用的Twitter数据文件
twitter_files = glob.glob('data/twitter/tweets_*.json')
if not twitter_files:
    # 也检查raw目录
    twitter_files = glob.glob('data/raw/twitter_*.json')

if not twitter_files:
    raise FileNotFoundError("未找到Twitter数据文件。请先运行 twitter_monitor.py 收集数据。")

# 使用最新的文件
twitter_file = sorted(twitter_files)[-1]
print(f"📂 使用数据文件: {twitter_file}")

# 加载Twitter数据
with open(twitter_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 处理嵌套结构：提取所有推文
if isinstance(data, dict):
    # 如果是字典格式（包含 user_tweets 和 keyword_tweets）
    raw_tweets = data.get('user_tweets', []) + data.get('keyword_tweets', [])
    # 如果没有这些键，尝试直接使用所有列表值
    if not raw_tweets:
        list_values = [v for v in data.values() if isinstance(v, list) and len(v) > 0]
        if list_values:
            # 合并所有列表
            raw_tweets = []
            for lst in list_values:
                raw_tweets.extend(lst)
elif isinstance(data, list):
    raw_tweets = data
else:
    raise ValueError(f"不支持的数据格式: {type(data)}")

if not raw_tweets:
    raise ValueError("数据文件中没有找到推文数据")

print(f"📊 原始推文数量: {len(raw_tweets)}")

# 初始化筛选器
filter = TwitterFilter()

# 1. 垃圾检测
spam_count = sum(1 for t in raw_tweets if filter.is_spam(t.get('text', '')))
print(f"🗑️  垃圾推文: {spam_count} ({spam_count/len(raw_tweets)*100:.1f}%)")

# 2. 质量筛选
filtered_tweets = filter.filter_tweets(raw_tweets, min_score=50)
print(f"✨ 高质量推文: {len(filtered_tweets)}")

# 3. 去重
unique_tweets = filter.deduplicate_tweets(filtered_tweets)
print(f"🎯 去重后推文: {len(unique_tweets)}")

# 4. 数据丰富
enriched_tweets = [filter.enrich_tweet_data(t) for t in unique_tweets]

# 显示前3条高质量推文
print("\n🏆 Top 3 高质量推文:\n")
for i, tweet in enumerate(enriched_tweets[:3], 1):
    print(f"【推文 {i}】")
    print(f"作者: @{tweet.get('author_username')}")
    print(f"质量分数: {tweet.get('quality_score')}/100")
    print(f"类别: {', '.join(tweet.get('categories', []))}")
    print(f"提及币种: {', '.join(tweet.get('mentioned_stablecoins', ['无']))}")
    print(f"内容: {tweet.get('text')[:100]}...")
    print(f"链接: {tweet.get('url', 'N/A')}")
    print("-" * 60 + "\n")

# 保存筛选后的数据
os.makedirs('data/processed', exist_ok=True)
output_file = f'data/processed/filtered_tweets_{os.path.basename(twitter_file).replace("tweets_", "").replace(".json", "")}.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(enriched_tweets, f, indent=2, ensure_ascii=False)

print(f"✅ 筛选后数据已保存: {output_file}")

# 统计分析
print("\n📈 统计分析:")
categories_count = {}
for tweet in enriched_tweets:
    for cat in tweet.get('categories', []):
        categories_count[cat] = categories_count.get(cat, 0) + 1

print(f"类别分布: {categories_count}")

stablecoins_count = {}
for tweet in enriched_tweets:
    for coin in tweet.get('mentioned_stablecoins', []):
        stablecoins_count[coin] = stablecoins_count.get(coin, 0) + 1

print(f"稳定币提及: {stablecoins_count}")

regions_count = {}
for tweet in enriched_tweets:
    for region in tweet.get('regions', []):
        regions_count[region] = regions_count.get(region, 0) + 1

print(f"地区分布: {regions_count}")