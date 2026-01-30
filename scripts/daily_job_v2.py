# scripts/daily_job_v2.py
"""
每日完整数据收集和AI分析流程 V2.2
- 使用 TwitterAPI.io 替代官方 API（成本降低96%）
- 新增 RSS 订阅收集（媒体 + Google News）
- 新分类体系：竞争对手 / 客户进展 / 行业进展
- 支持新配置结构 V1.1：competitors.tier_0/tier_1, customers.layer_a
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
from src.processors.daily_summary_generator import DailySummaryGenerator
from src.collectors.content_filter import ContentFilter

# 尝试导入 TwitterAPI.io 收集器
try:
    from src.collectors.twitter_api_io import TwitterAPIioCollector
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

# 尝试导入 RSS 收集器
try:
    from src.collectors.rss_collector import RSSCollector
    RSS_AVAILABLE = True
except ImportError:
    RSS_AVAILABLE = False

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

    # 默认配置（新结构 V1.1）
    return {
        "search_keywords": {
            "primary": ["stablecoin", "USDC", "USDT"],
            "secondary": ["cross-border payment crypto"]
        },
        "competitors": {
            "tier_0_custody": [{"name": "Fireblocks", "twitter": "FireblocksHQ"}],
            "tier_1_payment_infra": [{"name": "OSL", "twitter": "OSL_exchange"}]
        },
        "customers": {
            "layer_a": [{"name": "Vantage", "twitter": "VantageMarkets"}],
            "context_keywords": ["stablecoin", "custody"]
        },
        "twitter_accounts": {
            "kol": [{"username": "jerallaire"}, {"username": "paoloardoino"}],
            "media": [{"username": "CoinDesk"}, {"username": "TheBlock__"}]
        }
    }


def extract_twitter_accounts(config: dict) -> list:
    """从配置中提取所有需要监控的 Twitter 账号"""
    accounts = []

    # 1. 竞争对手账号（新结构）
    competitors = config.get("competitors", {})
    for tier in ['tier_0_custody', 'tier_1_payment_infra']:
        for company in competitors.get(tier, []):
            twitter = company.get("twitter", "")
            if twitter and twitter not in accounts:
                accounts.append(twitter)

    # 2. 客户账号（新结构）
    customers = config.get("customers", {})
    for company in customers.get("layer_a", []):
        twitter = company.get("twitter", "")
        if twitter and twitter not in accounts:
            accounts.append(twitter)

    # 3. KOL 和媒体账号
    for group in config.get("twitter_accounts", {}).values():
        for acc in group:
            username = acc.get("username", "")
            if username and username not in accounts:
                accounts.append(username)

    # 4. 兼容旧结构
    old_categories = config.get("categories", {})
    for company in old_categories.get("competitors", {}).get("companies", []):
        twitter = company.get("twitter", "")
        if twitter and twitter not in accounts:
            accounts.append(twitter)
    for company in old_categories.get("clients", {}).get("companies", []):
        twitter = company.get("twitter", "")
        if twitter and twitter not in accounts:
            accounts.append(twitter)

    return accounts


def get_client_allowlist(config: dict) -> set:
    """从 config 取出客户名单（customers.layer_a[].name），用于白名单过滤。大小写不敏感。"""
    names = set()
    for company in config.get("customers", {}).get("layer_a", []):
        name = company.get("name", "").strip()
        if name:
            names.add(name.lower())
    # 兼容旧结构
    for company in config.get("categories", {}).get("clients", {}).get("companies", []):
        name = company.get("name", "").strip()
        if name:
            names.add(name.lower())
    return names


def filter_clients_by_allowlist(categorized_data: dict, keywords_config: dict) -> None:
    """
    客户进展只保留「我的客户」：mentioned_companies 中至少有一个在 config 客户名单里。
    被筛掉的条目移到 industry，避免丢失。
    """
    allowlist = get_client_allowlist(keywords_config)
    if not allowlist:
        return

    clients = categorized_data.get("clients", [])
    keep = []
    move_to_industry = []

    for item in clients:
        mentioned = item.get("mentioned_companies", []) or []
        mentioned_lower = [m.strip().lower() for m in mentioned if m and isinstance(m, str)]
        if any(m in allowlist for m in mentioned_lower):
            keep.append(item)
        else:
            move_to_industry.append(item)

    categorized_data["clients"] = keep
    categorized_data["industry"] = categorized_data.get("industry", []) + move_to_industry


# 行业子类在简报中的输出顺序
INDUSTRY_SUBCATEGORY_ORDER = [
    "custody_mpc_risk",
    "regulation_licensing",
    "stablecoin_payments",
    "funding_mna",
    "other",
]


def assign_industry_subcategory(industry_items: list, keywords_config: dict) -> None:
    """
    为每条行业进展打子类（industry_subcategory, industry_subcategory_name）。
    基于 config 的 industry_topics 关键词匹配；无匹配则为 other。
    """
    topics = keywords_config.get("industry_topics", {})
    if not topics:
        for item in industry_items:
            item["industry_subcategory"] = "other"
            item["industry_subcategory_name"] = "其他"
        return

    for item in industry_items:
        text_parts = [
            item.get("title") or "",
            item.get("ai_summary") or "",
            item.get("description") or "",
            item.get("text") or "",
        ]
        text = " ".join(str(p) for p in text_parts).lower()

        best_key = "other"
        best_score = 0

        for topic_key, topic_config in topics.items():
            keywords_any = topic_config.get("keywords_any", []) or []
            keywords_context = topic_config.get("keywords_context", []) or []
            score = 0
            for kw in keywords_any:
                if kw.lower() in text:
                    score += 2
            for kw in keywords_context:
                if kw.lower() in text:
                    score += 1
            if score > best_score:
                best_score = score
                best_key = topic_key

        item["industry_subcategory"] = best_key
        item["industry_subcategory_name"] = (
            topics.get(best_key, {}).get("name", "其他") if best_key != "other" else "其他"
        )


def extract_search_keywords(config: dict) -> list:
    """从配置中提取搜索关键词"""
    keywords = []

    # 1. 主要和次要搜索关键词
    search_keywords = config.get("search_keywords", {})
    keywords.extend(search_keywords.get("primary", []))
    keywords.extend(search_keywords.get("secondary", []))

    # 2. 竞争对手公司名
    competitors = config.get("competitors", {})
    for tier in ['tier_0_custody', 'tier_1_payment_infra']:
        for company in competitors.get(tier, []):
            name = company.get("name", "")
            if name and name not in keywords:
                keywords.append(name)

    # 3. 客户公司名
    customers = config.get("customers", {})
    for company in customers.get("layer_a", []):
        name = company.get("name", "")
        if name and name not in keywords:
            keywords.append(name)

    return keywords


def daily_pipeline_v2(date_str=None):
    """完整的每日数据处理流程 V2.2
    date_str: 可选，指定日期 YYYY-MM-DD；不传则使用当天。
    """

    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')

    print("=" * 70)
    print(f"🤖 每日情报系统 V2.2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (报告日期: {date_str})")
    print("=" * 70 + "\n")

    # 检查必要的 API Keys
    if not OPENAI_API_KEY:
        print("❌ 未配置 OPENAI_API_KEY，无法进行AI分析")
        return False

    # 加载配置
    config = load_keywords_config()
    print(f"📋 配置版本: {config.get('version', '1.0')}\n")

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

            # 从配置获取关键词和账号（使用新的提取函数）
            keywords = extract_search_keywords(config)
            accounts = extract_twitter_accounts(config)

            print(f"   关键词: {len(keywords)} 个")
            print(f"   账号: {len(accounts)} 个")

            # 收集数据
            twitter_data = twitter_collector.collect_all(
                keywords=keywords[:10],  # 限制关键词数量控制成本
                accounts=accounts[:15],  # 增加账号监控数量
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

    # ===== STEP 2.5: 收集 RSS 数据 =====
    print("📡 STEP 2.5: 收集 RSS 订阅数据")
    print("-" * 70)

    raw_rss = []

    if RSS_AVAILABLE:
        try:
            rss_collector = RSSCollector()
            raw_rss = rss_collector.collect_all(hours_back=24)

            # 保存原始 RSS 数据
            os.makedirs('data/raw', exist_ok=True)
            rss_file = f'data/raw/rss_{date_str}.json'
            with open(rss_file, 'w', encoding='utf-8') as f:
                json.dump(raw_rss, f, indent=2, ensure_ascii=False)

            print(f"   已保存: {rss_file}\n")

        except Exception as e:
            print(f"⚠️  RSS 收集失败: {e}\n")
    else:
        print("⚠️  RSS 收集器未安装，跳过\n")

    # ===== STEP 3: 数据标准化 =====
    print("🔄 STEP 3: 数据标准化")
    print("-" * 70)

    normalizer = DataNormalizer()

    # 标准化新闻
    normalized_news = [normalizer.normalize_news(n) for n in raw_news]
    print(f"✅ 新闻标准化: {len(normalized_news)} 条")

    # 标准化 Twitter（保留原始字段用于过滤）
    normalized_tweets = []
    for tweet in raw_tweets:
        normalized_tweets.append({
            "title": tweet.get("text", "")[:100],
            "description": tweet.get("text", ""),
            "text": tweet.get("text", ""),  # 保留原始文本用于过滤
            "url": tweet.get("url", ""),
            "source": f"Twitter @{tweet.get('author_username', 'unknown')}",
            "author_username": tweet.get("author_username", ""),
            "published_at": tweet.get("created_at", ""),
            "data_type": "twitter",
            "likes": tweet.get("likes", 0),
            "retweets": tweet.get("retweets", 0),
            "views": tweet.get("views", 0),
            "engagement": {
                "likes": tweet.get("likes", 0),
                "retweets": tweet.get("retweets", 0),
                "views": tweet.get("views", 0)
            }
        })
    print(f"✅ Twitter 标准化: {len(normalized_tweets)} 条")

    # RSS 数据已经是标准化格式，直接使用
    print(f"✅ RSS 标准化: {len(raw_rss)} 条\n")

    # ===== STEP 3.5: 内容质量过滤 =====
    print("🧹 STEP 3.5: 内容质量过滤")
    print("-" * 70)

    content_filter = ContentFilter()

    # 合并所有新闻类数据（NewsAPI + RSS）
    all_news = normalized_news + raw_rss
    all_items = content_filter.process_all(all_news, normalized_tweets)

    if len(all_items) == 0:
        print("\n❌ 没有数据可处理，任务结束")
        return False

    # ===== STEP 4: 商业智能分类 =====
    print("🧠 STEP 4: 商业智能分类（竞争对手/客户/行业）")
    print("-" * 70)

    classifier = BusinessClassifier(api_key=OPENAI_API_KEY)
    categorized_data = classifier.classify_batch(all_items, use_ai=True)

    # 客户进展只保留 config 中的客户（白名单过滤），其余移到行业进展
    keywords_config = load_keywords_config()
    filter_clients_by_allowlist(categorized_data, keywords_config)

    # 为行业进展打子类（监管/融资/支付/托管/其他），便于简报分组展示
    assign_industry_subcategory(categorized_data.get("industry", []), keywords_config)

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

    # ===== STEP 6: 生成每日洞察 =====
    print("📊 STEP 6: 生成每日洞察")
    print("-" * 70)

    insights = None
    try:
        summary_generator = DailySummaryGenerator(api_key=OPENAI_API_KEY)
        insights = summary_generator.generate_daily_insights(categorized_data)
        # 行业进展小类总结（按子类分组后生成，供简报先展示再进入细分类）
        industry_list = categorized_data.get("industry", [])
        if industry_list:
            by_sub = {}
            for item in industry_list:
                sub = item.get("industry_subcategory") or "other"
                by_sub.setdefault(sub, []).append(item)
            focus_regions = keywords_config.get("company", {}).get("focus_regions", []) or []
            try:
                print("  📝 生成行业小类总结...")
                insights["industry_subcategory_summary"] = summary_generator.generate_industry_subcategory_summary(
                    by_sub, INDUSTRY_SUBCATEGORY_ORDER, focus_regions
                )
            except Exception as e:
                print(f"  ⚠️ 行业小类总结生成失败: {e}")
                insights["industry_subcategory_summary"] = ""
        else:
            insights["industry_subcategory_summary"] = ""
        print("✅ 每日洞察生成完成\n")
    except Exception as e:
        print(f"⚠️  每日洞察生成失败: {e}\n")

    # ===== STEP 7: 生成每日简报 =====
    print("📄 STEP 7: 生成每日简报")
    print("-" * 70)

    try:
        daily_report = generate_daily_brief(categorized_data, date_str, insights)

        os.makedirs('reports/daily', exist_ok=True)
        report_file = f'reports/daily/daily_brief_{date_str}.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(daily_report)

        print(f"✅ 每日简报已生成: {report_file}")

        # 复制到 docs 目录供 GitHub Pages 使用
        os.makedirs('docs/reports/daily', exist_ok=True)
        docs_report_file = f'docs/reports/daily/daily_brief_{date_str}.md'
        with open(docs_report_file, 'w', encoding='utf-8') as f:
            f.write(daily_report)
        print(f"✅ 已复制到: {docs_report_file}")

        # 生成前端数据文件（传入 insights 用于生成每日总结）
        generate_daily_reports_js(categorized_data, date_str, insights)
        print(f"✅ 前端数据已更新: docs/daily-reports.js\n")

    except Exception as e:
        print(f"⚠️  日报生成失败: {e}\n")

    # ===== 完成 =====
    print("=" * 70)
    print("✅ 每日任务完成")
    print("=" * 70)

    total_items = sum(len(items) for items in categorized_data.values())

    print(f"\n📊 数据统计:")
    print(f"   NewsAPI: {len(raw_news)} 条")
    print(f"   RSS: {len(raw_rss)} 条")
    print(f"   Twitter: {len(raw_tweets)} 条")
    print(f"   总计（过滤后）: {total_items} 条")

    print(f"\n📂 分类结果:")
    print(f"   🏢 竞争对手: {len(categorized_data.get('competitors', []))} 条")
    print(f"   🤝 客户进展: {len(categorized_data.get('clients', []))} 条")
    print(f"   📈 行业进展: {len(categorized_data.get('industry', []))} 条")

    print(f"\n📁 输出文件:")
    print(f"   - {categorized_file}")
    print(f"   - {legacy_file}")

    return True


def generate_daily_reports_js(data: dict, date_str: str, insights: dict = None):
    """
    生成前端日报数据文件 (docs/daily-reports.js)
    输出格式与前端 NewsItem 接口对齐，使用 camelCase 命名
    """

    # 读取现有数据
    js_file = 'docs/daily-reports.js'
    existing_reports = []

    if os.path.exists(js_file):
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # 提取最外层 JSON 数组（括号匹配，避免嵌套数组或字符串里的 ] 截断）
            start = content.find('[')
            if start >= 0:
                depth = 0
                in_string = None
                escape = False
                i = start
                while i < len(content):
                    c = content[i]
                    if escape:
                        escape = False
                        i += 1
                        continue
                    if c == '\\' and in_string:
                        escape = True
                        i += 1
                        continue
                    if in_string:
                        if c == in_string:
                            in_string = None
                        i += 1
                        continue
                    if c == '"':
                        in_string = '"'
                        i += 1
                        continue
                    if c == '[':
                        depth += 1
                    elif c == ']':
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            existing_reports = json.loads(content[start:end])
                            break
                    i += 1
        except Exception as e:
            print(f"  ⚠️ 读取现有数据失败: {e}")

    def convert_to_news_item(item: dict, category: str, index: int) -> dict:
        """
        将后端数据转换为前端 NewsItem 格式
        使用 camelCase 命名，包含所有前端需要的字段
        """
        url = item.get('url', '')
        source = item.get('source', '')

        # 如果没有 URL，尝试从 source 构建 Twitter URL
        if not url and 'Twitter @' in source:
            username = source.replace('Twitter @', '').strip()
            url = f'https://twitter.com/{username}'

        # 生成唯一 ID
        item_id = f"{date_str}-{category}-{index}"

        # 基础字段
        news_item = {
            'id': item_id,
            'title': item.get('title', '')[:100],
            'source': source,
            'date': date_str,
            'url': url,
            'category': category,  # 'competitor', 'customer', 'industry'
            'summary': item.get('ai_summary', item.get('description', ''))[:200],
        }

        # 根据分类添加特定字段
        if category == 'competitor':
            news_item['threatLevel'] = item.get('threat_level', 'neutral') or 'neutral'
            news_item['impact'] = item.get('impact_areas', [])
            news_item['action'] = item.get('suggested_action', '')
        elif category == 'customer':
            # 客户使用 opportunity_level 映射到 threatLevel（语义不同但复用字段）
            opp_level = item.get('opportunity_level', 'neutral') or 'neutral'
            news_item['threatLevel'] = opp_level  # high opportunity = good
            news_item['impact'] = item.get('opportunity_type', [])
            news_item['action'] = item.get('client_action', '')
        else:  # industry
            news_item['threatLevel'] = item.get('relevance_level', 'neutral') or 'neutral'
            news_item['impact'] = item.get('impact_type', [])
            news_item['action'] = item.get('industry_action', '')
            # 行业子类
            news_item['subcategory'] = item.get('industry_subcategory', 'other')
            news_item['subcategoryName'] = item.get('industry_subcategory_name', '其他')

        # 涉及的公司
        mentioned = item.get('mentioned_companies', [])
        if mentioned:
            news_item['tickers'] = mentioned

        return news_item

    # 转换所有数据为 NewsItem 格式
    all_news_items = []

    # 竞争对手
    for i, item in enumerate(data.get('competitors', [])):
        all_news_items.append(convert_to_news_item(item, 'competitor', i))

    # 客户
    for i, item in enumerate(data.get('clients', [])):
        all_news_items.append(convert_to_news_item(item, 'customer', i))

    # 行业
    for i, item in enumerate(data.get('industry', [])):
        all_news_items.append(convert_to_news_item(item, 'industry', i))

    # 统计数据（使用前端期望的字段名）
    competitors_list = data.get('competitors', [])
    clients_list = data.get('clients', [])
    industry_list = data.get('industry', [])

    # 统计威胁等级
    high_threats = len([x for x in competitors_list if x.get('threat_level') == 'high'])
    medium_threats = len([x for x in competitors_list if x.get('threat_level') == 'medium'])
    low_threats = len([x for x in competitors_list if x.get('threat_level') == 'low'])

    stats = {
        'totalThreats': len(competitors_list),
        'highThreats': high_threats,
        'mediumThreats': medium_threats,
        'lowThreats': low_threats,
        'competitorUpdates': len(competitors_list),
        'customerUpdates': len(clients_list),
        'industryUpdates': len(industry_list)
    }

    # 每日总结
    daily_summary = {
        'competitorThreat': (insights or {}).get('competitor_summary', ''),
        'industryTrend': (insights or {}).get('industry_summary', '')
    }

    # 构建今日完整报告
    today_report = {
        'date': date_str,
        'title': '稳定币行业日报',
        'file': f'reports/daily/daily_brief_{date_str}.md',
        # 新格式：完整的新闻项列表
        'newsItems': all_news_items,
        # 统计数据（前端格式）
        'stats': stats,
        # 每日总结
        'dailySummary': daily_summary,
        # 兼容旧格式：highlights 保留用于向后兼容
        'highlights': {
            'competitors': [convert_to_news_item(x, 'competitor', i) for i, x in enumerate(competitors_list[:3])],
            'clients': [convert_to_news_item(x, 'customer', i) for i, x in enumerate(clients_list[:3])],
            'industry': [convert_to_news_item(x, 'industry', i) for i, x in enumerate(industry_list[:3])]
        }
    }

    # 更新或添加今日数据
    updated = False
    for i, report in enumerate(existing_reports):
        if report.get('date') == date_str:
            existing_reports[i] = today_report
            updated = True
            break

    if not updated:
        existing_reports.insert(0, today_report)

    # 只保留最近 90 天的数据
    existing_reports = existing_reports[:90]

    # 写入文件（ES Module 格式，便于前端导入）
    js_content = f"""// 日报数据
// 由 daily_job_v2.py 自动生成
// 格式与前端 NewsItem 接口对齐

const dailyReports = {json.dumps(existing_reports, indent=4, ensure_ascii=False)};

// 导出最新报告的快捷访问
const latestReport = dailyReports[0] || null;
const latestNewsItems = latestReport ? latestReport.newsItems : [];
const latestStats = latestReport ? latestReport.stats : {{}};
const latestDailySummary = latestReport ? latestReport.dailySummary : {{}};

// CommonJS 兼容
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ dailyReports, latestReport, latestNewsItems, latestStats, latestDailySummary }};
}}
"""

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content)


def deduplicate_by_company(items: list) -> list:
    """
    按公司去重：同一公司的多条重复报道只保留互动最高的一条
    避免如 Cactus Custody 的同一新闻被多个账号转发都显示
    """
    if not items:
        return []

    # 按主要公司分组
    company_groups = {}

    for item in items:
        # 获取涉及的公司
        companies = item.get("mentioned_companies", [])
        # 取第一个公司作为主键，或使用标题前20字符
        if companies:
            key = companies[0].lower()
        else:
            key = item.get("title", "")[:20].lower()

        if key not in company_groups:
            company_groups[key] = []
        company_groups[key].append(item)

    # 每组只保留互动最高或来源最好的一条
    result = []
    for key, group in company_groups.items():
        if len(group) == 1:
            result.append(group[0])
        else:
            # 按优先级排序：RSS/新闻 > Twitter，高互动优先
            def score(item):
                source = item.get("source", "")
                is_news = "Twitter" not in source
                engagement = item.get("engagement", {})
                likes = engagement.get("likes", 0) if isinstance(engagement, dict) else 0
                return (is_news, likes)

            group.sort(key=score, reverse=True)
            result.append(group[0])

    return result


def generate_daily_brief(data: dict, date_str: str, insights: dict = None) -> str:
    """生成每日简报"""
    report = []
    report.append(f"# 稳定币行业日报")
    report.append(f"\n**日期**: {date_str}")
    report.append(f"\n---\n")

    # 每日洞察板块
    if insights:
        report.append("## 📊 每日洞察\n")

        competitor_summary = insights.get("competitor_summary", "")
        industry_summary = insights.get("industry_summary", "")

        if competitor_summary:
            report.append("### 🔴 竞争对手威胁总结")
            report.append(f"\n{competitor_summary}\n")

        if industry_summary:
            report.append("### 📈 行业趋势总结")
            report.append(f"\n{industry_summary}\n")

        report.append("---\n")

    # 竞争对手动态（按公司去重，避免同一事件多次报道）
    competitors = deduplicate_by_company(data.get("competitors", []))
    if competitors:
        report.append("## 🏢 竞争对手动态\n")
        for item in competitors:  # 显示全部内容
            title = item.get("title", "")[:80]
            url = item.get("url", "")
            source = item.get("source", "")
            summary = item.get("ai_summary", "")
            companies = ", ".join(item.get("mentioned_companies", []))

            # 威胁分析
            threat_level = item.get("threat_level", "")
            impact_areas = item.get("impact_areas", [])
            suggested_action = item.get("suggested_action", "")

            threat_icon = {"high": "🔴 高", "medium": "🟡 中", "low": "🟢 低"}.get(threat_level, "")

            # 标题带链接
            if url:
                report.append(f"### [{title}]({url})")
            else:
                report.append(f"### {title}")
            if companies:
                report.append(f"**涉及公司**: {companies}")

            # 显示威胁分析
            if threat_level:
                report.append(f"\n**威胁等级**: {threat_icon}")
            if impact_areas:
                report.append(f"**影响领域**: {', '.join(impact_areas)}")
            if suggested_action:
                report.append(f"**建议行动**: {suggested_action}")

            if summary:
                report.append(f"\n{summary}")
            report.append(f"\n*来源: {source}*\n")

    # 客户进展
    clients = data.get("clients", [])
    if clients:
        report.append("\n## 🤝 客户进展\n")
        for item in clients:  # 显示全部内容
            title = item.get("title", "")[:80]
            url = item.get("url", "")
            source = item.get("source", "")
            summary = item.get("ai_summary", "")
            companies = ", ".join(item.get("mentioned_companies", []))

            # 机会分析
            opportunity_level = item.get("opportunity_level", "")
            opportunity_type = item.get("opportunity_type", [])
            client_action = item.get("client_action", "")

            opportunity_icon = {"high": "🟢 高", "medium": "🟡 中", "low": "⚪ 低"}.get(opportunity_level, "")

            # 标题带链接
            if url:
                report.append(f"### [{title}]({url})")
            else:
                report.append(f"### {title}")
            if companies:
                report.append(f"**涉及公司**: {companies}")

            # 显示机会分析
            if opportunity_level:
                report.append(f"\n**机会等级**: {opportunity_icon}")
            if opportunity_type:
                report.append(f"**机会类型**: {', '.join(opportunity_type)}")
            if client_action:
                report.append(f"**建议行动**: {client_action}")

            if summary:
                report.append(f"\n{summary}")
            report.append(f"\n*来源: {source}*\n")

    # 行业进展（先小类总结，再按子类分组：托管与风险 / 监管牌照 / 稳定币支付 / 融资并购 / 其他）
    industry = data.get("industry", [])
    if industry:
        report.append("\n## 📈 行业进展\n")

        # 先输出小类总结（若有）
        industry_subcategory_summary = (insights or {}).get("industry_subcategory_summary", "")
        if industry_subcategory_summary:
            report.append(f"\n{industry_subcategory_summary}\n")

        # 按 industry_subcategory 分组，缺省归为 other
        by_sub = {}
        for item in industry:
            sub = item.get("industry_subcategory") or "other"
            by_sub.setdefault(sub, []).append(item)

        for sub_key in INDUSTRY_SUBCATEGORY_ORDER:
            items = by_sub.get(sub_key, [])
            if not items:
                continue
            # 子类标题（使用 config 中的 name；other 显示为「其他」）
            section_name = (items[0].get("industry_subcategory_name") or sub_key) if items else sub_key
            if section_name == "other" or not section_name:
                section_name = "其他"
            report.append(f"\n### {section_name}\n")

            for item in items:
                title = item.get("title", "")[:80]
                url = item.get("url", "")
                source = item.get("source", "")
                summary = item.get("ai_summary", "")

                relevance_level = item.get("relevance_level", "")
                impact_type = item.get("impact_type", [])
                industry_action = item.get("industry_action", "")

                relevance_icon = {"high": "🔵 高", "medium": "🟡 中", "low": "⚪ 低"}.get(relevance_level, "")

                if url:
                    report.append(f"#### [{title}]({url})")
                else:
                    report.append(f"#### {title}")

                if relevance_level:
                    report.append(f"\n**相关度**: {relevance_icon}")
                if impact_type:
                    report.append(f"**影响类型**: {', '.join(impact_type)}")
                if industry_action:
                    report.append(f"**需要行动**: {industry_action}")

                if summary:
                    report.append(f"\n{summary}")
                report.append(f"\n*来源: {source}*\n")

        # 未在 ORDER 中的子类也输出（如 config 新增的 key）
        for sub_key, items in by_sub.items():
            if sub_key in INDUSTRY_SUBCATEGORY_ORDER:
                continue
            section_name = (items[0].get("industry_subcategory_name") or sub_key) if items else sub_key
            if section_name == "other" or not section_name:
                section_name = "其他"
            report.append(f"\n### {section_name}\n")
            for item in items:
                title = item.get("title", "")[:80]
                url = item.get("url", "")
                source = item.get("source", "")
                summary = item.get("ai_summary", "")
                relevance_level = item.get("relevance_level", "")
                impact_type = item.get("impact_type", [])
                industry_action = item.get("industry_action", "")
                relevance_icon = {"high": "🔵 高", "medium": "🟡 中", "low": "⚪ 低"}.get(relevance_level, "")
                if url:
                    report.append(f"#### [{title}]({url})")
                else:
                    report.append(f"#### {title}")
                if relevance_level:
                    report.append(f"\n**相关度**: {relevance_icon}")
                if impact_type:
                    report.append(f"**影响类型**: {', '.join(impact_type)}")
                if industry_action:
                    report.append(f"**需要行动**: {industry_action}")
                if summary:
                    report.append(f"\n{summary}")
                report.append(f"\n*来源: {source}*\n")

    report.append("\n---")
    report.append(f"\n*本报告由稳定币情报系统自动生成*")

    return "\n".join(report)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='稳定币日报流水线')
    parser.add_argument('--date', type=str, metavar='YYYY-MM-DD', help='指定报告日期，不传则使用当天')
    args = parser.parse_args()
    success = daily_pipeline_v2(date_str=args.date)
    exit(0 if success else 1)
