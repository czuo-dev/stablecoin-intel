# scripts/daily_job.py

"""
每日完整数据收集和AI分析流程
整合 NewsAPI + Twitter + AI分类
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入你的模块
from src.collectors.news_collector import NewsCollector
from src.collectors.twitter_collector import TwitterCollector
from src.collectors.data_normalizer import DataNormalizer
from src.collectors.twitter_filter import TwitterFilter
from src.processors.smart_classifier import SmartClassifier
from src.processors.batch_summarizer import BatchSummarizer

# 从 config 导入配置
try:
    from config import OPENAI_API_KEY, TWITTER_BEARER_TOKEN
except ImportError:
    # 如果 config.py 不存在，从环境变量读取
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# 加载环境变量
load_dotenv()

def daily_pipeline():
    """完整的每日数据处理流程"""
    
    print("=" * 70)
    print(f"🤖 每日情报系统 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 检查 API Keys
    if not OPENAI_API_KEY:
        print("❌ 未配置 OPENAI_API_KEY，无法进行AI分析")
        print("   请在 config.py 或 .env 中设置\n")
        return False
    
    # ===== STEP 1: 收集 NewsAPI 数据 =====
    print("📡 STEP 1: 收集 NewsAPI 数据")
    print("-" * 70)
    
    try:
        news_collector = NewsCollector()
        raw_news = news_collector.collect_news(days_back=1)
        print(f"✅ NewsAPI 收集完成: {len(raw_news)} 条\n")
    except Exception as e:
        print(f"❌ NewsAPI 收集失败: {e}\n")
        raw_news = []
    
    # ===== STEP 2: 收集 Twitter 数据 =====
    print("📡 STEP 2: 收集 Twitter 数据")
    print("-" * 70)
    
    raw_tweets = []
    
    if TWITTER_BEARER_TOKEN:
        try:
            # 检查token格式（URL解码）
            import urllib.parse
            # 如果token包含URL编码，先解码
            decoded_token = urllib.parse.unquote(TWITTER_BEARER_TOKEN)
            
            # 初始化 Twitter 收集器
            print("   初始化Twitter收集器...")
            twitter_collector = TwitterCollector(
                bearer_token=decoded_token,
                monitored_accounts=[
                    "circle", "Tether_to", "paoloardoino", "coinbase",
                    "MessariCrypto", "jerallaire"
                ],
                monitored_keywords=[
                    "stablecoin", "USDC", "USDT", "PYUSD", 
                    "Circle", "Tether"
                ]
            )
            
            # 收集推文（使用 collect_all 返回兼容格式）
            print("   开始收集推文...")
            twitter_data = twitter_collector.collect_all(hours=24)
            
            # 合并用户推文和关键词推文
            user_tweets = twitter_data.get('user_tweets', [])
            keyword_tweets = twitter_data.get('keyword_tweets', [])
            raw_tweets = user_tweets + keyword_tweets
            
            # 保存原始Twitter数据
            os.makedirs('data/raw', exist_ok=True)
            twitter_file = f'data/raw/twitter_data_{date_str}.json'
            with open(twitter_file, 'w', encoding='utf-8') as f:
                json.dump(raw_tweets, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Twitter 收集完成: {len(raw_tweets)} 条")
            print(f"   (用户推文: {len(user_tweets)}, 关键词推文: {len(keyword_tweets)})")
            print(f"   已保存: {twitter_file}\n")
            
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️  Twitter 收集失败: {error_msg}")
            
            # 提供更详细的错误信息
            if "401" in error_msg or "Unauthorized" in error_msg:
                print("   💡 可能原因:")
                print("      - Bearer Token 无效或已过期")
                print("      - Twitter API免费版配额已用完（只有100次读取/月）")
                print("      - 你的需求：390次/月，免费版：100次/月（超出290%）")
                print("      - 免费版可以读，但配额太少，不适合每天自动收集")
                print("      - 如需读操作，建议升级到Basic版（$100/月，10,000次/月）")
                print("   📝 注意：脚本会继续使用NewsAPI数据，不影响整体流程")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                print("   💡 API速率限制，请稍后重试")
            else:
                print(f"   💡 错误详情: {type(e).__name__}")
            
            print(f"   ⏭️  继续使用 NewsAPI 数据\n")
            raw_tweets = []
    else:
        print("⚠️  未配置 TWITTER_BEARER_TOKEN，跳过 Twitter 收集\n")
    
    # ===== STEP 3: 数据标准化和筛选 =====
    print("🔄 STEP 3: 数据标准化和筛选")
    print("-" * 70)
    
    normalizer = DataNormalizer()
    
    # 标准化新闻
    normalized_news = [normalizer.normalize_news(n) for n in raw_news]
    print(f"✅ 新闻标准化: {len(normalized_news)} 条")
    
    # 筛选和标准化 Twitter
    if raw_tweets:
        twitter_filter = TwitterFilter()
        filtered_tweets = twitter_filter.filter_tweets(raw_tweets, min_score=60)
        enriched_tweets = [twitter_filter.enrich_tweet_data(t) for t in filtered_tweets]
        normalized_tweets = [normalizer.normalize_tweet(t) for t in enriched_tweets]
        print(f"✅ Twitter 筛选: {len(raw_tweets)} → {len(normalized_tweets)} 条")
    else:
        normalized_tweets = []
    
    # 合并所有数据
    all_items = normalized_news + normalized_tweets
    
    if len(all_items) == 0:
        print("\n❌ 没有数据可处理，任务结束")
        return False
    
    print(f"✅ 合并后总数据: {len(all_items)} 条\n")
    
    # ===== STEP 4: AI 智能分类 =====
    print("🧠 STEP 4: AI 智能分类")
    print("-" * 70)
    
    classifier = SmartClassifier(api_key=OPENAI_API_KEY)
    
    # 初始化分类结果
    categorized_data = {
        'policy': [],
        'company': [],
        'funding': []
    }
    
    print(f"开始分类 {len(all_items)} 条数据...\n")
    
    for i, item in enumerate(all_items, 1):
        title = item.get('title', '')[:50]
        print(f"  [{i}/{len(all_items)}] {title}...", end=' ')
        
        try:
            # AI 分类
            classification = classifier.classify_article({
                'title': item.get('title', ''),
                'description': item.get('description', item.get('text', ''))
            })
            
            # 添加分类结果到 item
            item['categories'] = [classification['primary_category']]
            item['ai_confidence'] = classification['confidence']
            item['ai_tags'] = classification.get('tags', [])
            item['importance_score'] = classification.get('importance', 5)
            item['ai_reasoning'] = classification.get('reasoning', '')
            
            # 分类到对应类别
            category = classification['primary_category']
            if category in categorized_data:
                categorized_data[category].append(item)
                print(f"✓ {category}")
            else:
                categorized_data['company'].append(item)
                print(f"✓ company (默认)")
        
        except Exception as e:
            print(f"✗ 失败: {e}")
            # 失败时使用默认分类
            item['categories'] = ['company']
            item['importance_score'] = 5
            categorized_data['company'].append(item)
    
    print(f"\n✅ AI分类完成:")
    for category, items in categorized_data.items():
        if items:
            avg_score = sum(i.get('importance_score', 5) for i in items) / len(items)
            print(f"   {category}: {len(items)} 条 (平均重要性: {avg_score:.1f})")
    print()
    
    # ===== STEP 5: 保存分类数据（关键！）=====
    print("💾 STEP 5: 保存分类数据")
    print("-" * 70)
    
    os.makedirs('data/processed', exist_ok=True)
    
    # 这是 weekly_reporter.aggregate_weekly_data() 需要读取的格式！
    categorized_file = f'data/processed/categorized_news_{date_str}.json'
    with open(categorized_file, 'w', encoding='utf-8') as f:
        json.dump(categorized_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 分类数据已保存: {categorized_file}")
    print(f"   格式: {{policy: [...], company: [...], funding: [...]}}")
    print(f"   👉 weekly_job.py 会读取这个文件生成周报\n")
    
    # ===== STEP 6: 可选 - 生成每日简报 =====
    print("📄 STEP 6: 生成每日简报（可选）")
    print("-" * 70)
    
    try:
        summarizer = BatchSummarizer(api_key=OPENAI_API_KEY)
        
        # 生成带情感分析的日报
        daily_report = summarizer.generate_daily_report_with_sentiment(categorized_data)
        
        # 保存日报
        os.makedirs('reports/daily', exist_ok=True)
        report_file = f'reports/daily/daily_report_{date_str}.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(daily_report)
        
        print(f"✅ 每日简报已生成: {report_file}\n")
    
    except Exception as e:
        print(f"⚠️  日报生成失败（不影响主流程）: {e}\n")
    
    # ===== 完成 =====
    print("=" * 70)
    print("✅ 每日任务完成")
    print("=" * 70)
    
    total_items = sum(len(items) for items in categorized_data.values())
    
    print(f"\n📊 数据统计:")
    print(f"  原始数据:")
    print(f"    - NewsAPI: {len(raw_news)} 条")
    print(f"    - Twitter: {len(raw_tweets)} 条")
    print(f"  处理后: {total_items} 条")
    print(f"\n  分类结果:")
    for category, items in categorized_data.items():
        if items:
            avg_score = sum(i.get('importance_score', 5) for i in items) / len(items)
            top_item = max(items, key=lambda x: x.get('importance_score', 0))
            print(f"    - {category}: {len(items)} 条")
            print(f"      平均重要性: {avg_score:.1f}/10")
            print(f"      最高分: {top_item['title'][:50]}... ({top_item['importance_score']}/10)")
    
    print(f"\n📁 输出文件:")
    print(f"  - {categorized_file}")
    if raw_tweets:
        print(f"  - data/raw/twitter_data_{date_str}.json")
    
    print(f"\n💡 下一步:")
    print(f"  每天运行: python scripts/daily_job.py")
    print(f"  生成周报: python scripts/weekly_job.py")
    print(f"\n💰 预计成本:")
    print(f"  AI分类: ~{len(all_items) * 0.0002:.4f} USD")
    print(f"  日报生成: ~0.002 USD")
    print(f"  总计: ~{len(all_items) * 0.0002 + 0.002:.4f} USD/天")
    
    return True

if __name__ == '__main__':
    success = daily_pipeline()
    exit(0 if success else 1)