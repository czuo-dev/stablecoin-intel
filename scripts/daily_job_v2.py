# scripts/daily_job_v2.py
"""
每日完整数据收集和AI分析流程 V2
- 使用 TwitterAPI.io 替代官方 API（成本降低96%）
- 新分类体系：竞争对手 / 客户进展 / 行业进展
- 支持从 config/keywords.json 读取配置
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入模块
from src.collectors.news_collector import NewsCollector
from src.collectors.data_normalizer import DataNormalizer
from src.processors.business_classifier import BusinessClassifier

# 尝试导入 TwitterAPI.io 收集器
try:
    from src.collectors.twitter_api_io import TwitterAPIioCollector
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

# 加载环境变量
load_dotenv()

# 配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TWITTERAPI_IO_KEY = os.getenv('TWITTERAPI_IO_KEY')


def load_keywords_config():
    """加载关键词配置"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config', 'keywords.json'
    )

    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # 默认配置
    return {
        "search_keywords": {
            "primary": ["stablecoin", "USDC", "USDT", "PYUSD"]
        },
        "twitter_accounts": {
            "kol": [{"username": "jerallaire"}, {"username": "paoloardoino"}],
            "media": [{"username": "CoinDesk"}, {"username": "TheBlock__"}]
        }
    }


def daily_pipeline_v2():
    """完整的每日数据处理流程 V2"""

    print("=" * 70)
    print(f"🤖 每日情报系统 V2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    date_str = datetime.now().strftime('%Y-%m-%d')

    # 检查必要的 API Keys
    if not OPENAI_API_KEY:
        print("❌ 未配置 OPENAI_API_KEY，无法进行AI分析")
        return False

    # 加载配置
    config = load_keywords_config()

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

    # ===== STEP 2: 收集 Twitter 数据（使用 TwitterAPI.io）=====
    print("📡 STEP 2: 收集 Twitter 数据 (TwitterAPI.io)")
    print("-" * 70)

    raw_tweets = []

    if TWITTER_AVAILABLE and TWITTERAPI_IO_KEY:
        try:
            twitter_collector = TwitterAPIioCollector(api_key=TWITTERAPI_IO_KEY)

            # 从配置获取关键词和账号
            keywords = config.get("search_keywords", {}).get("primary", [])
            keywords += config.get("search_keywords", {}).get("secondary", [])

            accounts = []
            for group in config.get("twitter_accounts", {}).values():
                for acc in group:
                    accounts.append(acc["username"])

            # 收集数据
            twitter_data = twitter_collector.collect_all(
                keywords=keywords[:10],  # 限制关键词数量控制成本
                accounts=accounts[:10],
                hours_back=24
            )

            raw_tweets = twitter_data.get("all_tweets", [])

            # 保存原始 Twitter 数据
            os.makedirs('data/raw', exist_ok=True)
            twitter_file = f'data/raw/twitter_apiio_{date_str}.json'
            with open(twitter_file, 'w', encoding='utf-8') as f:
                json.dump(raw_tweets, f, indent=2, ensure_ascii=False)

            print(f"✅ Twitter 收集完成: {len(raw_tweets)} 条")
            print(f"   已保存: {twitter_file}\n")

        except Exception as e:
            print(f"⚠️  Twitter 收集失败: {e}")
            print(f"   ⏭️  继续使用 NewsAPI 数据\n")
    else:
        if not TWITTERAPI_IO_KEY:
            print("⚠️  未配置 TWITTERAPI_IO_KEY，跳过 Twitter 收集")
            print("   💡 获取 API Key: https://twitterapi.io/\n")
        elif not TWITTER_AVAILABLE:
            print("⚠️  TwitterAPI.io 模块未安装\n")

    # ===== STEP 3: 数据标准化 =====
    print("🔄 STEP 3: 数据标准化")
    print("-" * 70)

    normalizer = DataNormalizer()

    # 标准化新闻
    normalized_news = [normalizer.normalize_news(n) for n in raw_news]
    print(f"✅ 新闻标准化: {len(normalized_news)} 条")

    # 标准化 Twitter（已经是标准格式）
    normalized_tweets = []
    for tweet in raw_tweets:
        normalized_tweets.append({
            "title": tweet.get("text", "")[:100],
            "description": tweet.get("text", ""),
            "url": tweet.get("url", ""),
            "source": f"Twitter @{tweet.get('author_username', 'unknown')}",
            "published_at": tweet.get("created_at", ""),
            "data_type": "twitter",
            "engagement": {
                "likes": tweet.get("likes", 0),
                "retweets": tweet.get("retweets", 0),
                "views": tweet.get("views", 0)
            }
        })
    print(f"✅ Twitter 标准化: {len(normalized_tweets)} 条")

    # 合并所有数据
    all_items = normalized_news + normalized_tweets

    if len(all_items) == 0:
        print("\n❌ 没有数据可处理，任务结束")
        return False

    print(f"✅ 合并后总数据: {len(all_items)} 条\n")

    # ===== STEP 4: 商业智能分类 =====
    print("🧠 STEP 4: 商业智能分类（竞争对手/客户/行业）")
    print("-" * 70)

    classifier = BusinessClassifier(api_key=OPENAI_API_KEY)
    categorized_data = classifier.classify_batch(all_items, use_ai=True)

    print()

    # ===== STEP 5: 保存分类数据 =====
    print("💾 STEP 5: 保存分类数据")
    print("-" * 70)

    os.makedirs('data/processed', exist_ok=True)

    # 新格式：按商业分类保存
    categorized_file = f'data/processed/business_intel_{date_str}.json'
    with open(categorized_file, 'w', encoding='utf-8') as f:
        json.dump(categorized_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 商业智能数据已保存: {categorized_file}")

    # 同时保存兼容旧格式（供周报使用）
    legacy_data = {
        "policy": categorized_data.get("industry", []),
        "company": categorized_data.get("competitors", []) + categorized_data.get("clients", []),
        "funding": [item for item in categorized_data.get("industry", [])
                   if "funding" in item.get("ai_summary", "").lower() or
                      "investment" in item.get("title", "").lower()]
    }

    legacy_file = f'data/processed/categorized_news_{date_str}.json'
    with open(legacy_file, 'w', encoding='utf-8') as f:
        json.dump(legacy_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 兼容格式已保存: {legacy_file}\n")

    # ===== STEP 6: 生成每日简报 =====
    print("📄 STEP 6: 生成每日简报")
    print("-" * 70)

    try:
        daily_report = generate_daily_brief(categorized_data, date_str)

        os.makedirs('reports/daily', exist_ok=True)
        report_file = f'reports/daily/daily_brief_{date_str}.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(daily_report)

        print(f"✅ 每日简报已生成: {report_file}\n")
    except Exception as e:
        print(f"⚠️  日报生成失败: {e}\n")

    # ===== 完成 =====
    print("=" * 70)
    print("✅ 每日任务完成")
    print("=" * 70)

    total_items = sum(len(items) for items in categorized_data.values())

    print(f"\n📊 数据统计:")
    print(f"   NewsAPI: {len(raw_news)} 条")
    print(f"   Twitter: {len(raw_tweets)} 条")
    print(f"   总计: {total_items} 条")

    print(f"\n📂 分类结果:")
    print(f"   🏢 竞争对手: {len(categorized_data.get('competitors', []))} 条")
    print(f"   🤝 客户进展: {len(categorized_data.get('clients', []))} 条")
    print(f"   📈 行业进展: {len(categorized_data.get('industry', []))} 条")

    print(f"\n📁 输出文件:")
    print(f"   - {categorized_file}")
    print(f"   - {legacy_file}")

    return True


def generate_daily_brief(data: dict, date_str: str) -> str:
    """生成每日简报"""
    report = []
    report.append(f"# 稳定币行业日报")
    report.append(f"\n**日期**: {date_str}")
    report.append(f"\n---\n")

    # 竞争对手动态
    competitors = data.get("competitors", [])
    if competitors:
        report.append("## 🏢 竞争对手动态\n")
        for item in competitors[:5]:
            title = item.get("title", "")[:80]
            source = item.get("source", "")
            summary = item.get("ai_summary", "")
            companies = ", ".join(item.get("mentioned_companies", []))

            report.append(f"### {title}")
            if companies:
                report.append(f"**涉及公司**: {companies}")
            if summary:
                report.append(f"\n{summary}")
            report.append(f"\n*来源: {source}*\n")

    # 客户进展
    clients = data.get("clients", [])
    if clients:
        report.append("\n## 🤝 客户进展\n")
        for item in clients[:5]:
            title = item.get("title", "")[:80]
            source = item.get("source", "")
            summary = item.get("ai_summary", "")

            report.append(f"### {title}")
            if summary:
                report.append(f"\n{summary}")
            report.append(f"\n*来源: {source}*\n")

    # 行业进展
    industry = data.get("industry", [])
    if industry:
        report.append("\n## 📈 行业进展\n")
        for item in industry[:5]:
            title = item.get("title", "")[:80]
            source = item.get("source", "")
            summary = item.get("ai_summary", "")

            report.append(f"### {title}")
            if summary:
                report.append(f"\n{summary}")
            report.append(f"\n*来源: {source}*\n")

    report.append("\n---")
    report.append(f"\n*本报告由稳定币情报系统自动生成*")

    return "\n".join(report)


if __name__ == '__main__':
    success = daily_pipeline_v2()
    exit(0 if success else 1)
