# 稳定币新闻智能过滤器 v2.0
# 用途：从大量新闻中筛选出相关的稳定币新闻
# 使用完整的专业关键词库

# =========================
# 导入完整关键词库
# =========================

policy_keywords = [
    # 英文 - 框架 / 法案
    "stablecoin regulation", "stablecoin bill", "digital asset regulation",
    "payment regulation", "licensing framework", "regulatory guidance",
    "consultation paper", "enforcement action", "sanctions", "OFAC",
    # 英文 - 具体制度 / 法规
    "MiCA", "EMT stablecoin", "ART stablecoin", "GENIUS Act",
    "Clarity Act", "Stablecoin Act",
    # 机构
    "SEC", "CFTC", "FinCEN", "OCC", "US Treasury", "MAS", "HKMA",
    "ESMA", "EBA",
    # 新加坡 / 香港 / 中国语境
    "MSA", "TCSP", "PSA", "DTSP", "VASP", "VATP",
    # 中文
    "监管", "合规", "牌照", "稳定币监管", "支付监管", "沙盒", "罚款", "执法",
]

company_keywords = [
    # 稳定币核心
    "Circle", "Tether", "USDC", "USDT", "PYUSD",
    # 支付 / 金融科技
    "Stripe", "Visa", "PayPal", "Mastercard",
    # 钱包 / 托管 / Infra
    "Fireblocks", "BVNK", "Anchorage", "BitGo", "Copper", "Metaco",
    # 银行 / 大机构
    "JP Morgan", "Onyx", "Goldman Sachs", "HSBC", "Standard Chartered",
    # 交易所 / 出入金
    "Coinbase", "Binance", "OKX", "Kraken",
]

funding_keywords = [
    # 英文 - 融资
    "funding round", "raises", "raised", "investment", "strategic investment",
    "venture capital", "Series A", "Series B", "Series C", "valuation",
    "post-money",
    # 并购 / 战略
    "acquisition", "acquired", "merger", "strategic partnership",
    "minority stake",
    # 中文
    "融资", "投资", "并购", "收购", "战略投资",
]

# =========================
# 模拟新闻数据（更真实的例子）
# =========================

all_news = [
    # 政策监管类
    {"title": "Circle获得新加坡MAS电子货币机构牌照，成为首家获批稳定币发行商", "source": "CoinDesk", "date": "2025-01-10"},
    {"title": "美国SEC主席称将在2025年Q1推出统一的稳定币监管框架", "source": "Bloomberg", "date": "2025-01-10"},
    {"title": "欧盟MiCA法规正式生效，要求所有EMT和ART稳定币发行商申请牌照", "source": "Financial Times", "date": "2025-01-09"},
    {"title": "香港金管局HKMA发布稳定币监管沙盒申请指引", "source": "South China Morning Post", "date": "2025-01-09"},
    {"title": "美国财政部OFAC对未经许可的稳定币发行商实施制裁", "source": "Reuters", "date": "2025-01-08"},
    
    # 公司动态类
    {"title": "PayPal的PYUSD稳定币总发行量突破10亿美元", "source": "The Block", "date": "2025-01-10"},
    {"title": "Visa与Circle达成战略合作，在全球推广USDC支付", "source": "TechCrunch", "date": "2025-01-09"},
    {"title": "Stripe宣布全面支持USDC和USDT的跨境支付结算", "source": "TechCrunch", "date": "2025-01-09"},
    {"title": "Tether在以太坊和Solana上累计发行USDT超过1200亿美元", "source": "CoinDesk", "date": "2025-01-08"},
    {"title": "JP Morgan旗下Onyx推出基于许可链的稳定币JPM Coin 2.0", "source": "Bloomberg", "date": "2025-01-08"},
    {"title": "Coinbase宣布支持更多稳定币的法币出入金通道", "source": "The Block", "date": "2025-01-07"},
    {"title": "BitGo获得新加坡VASP牌照，可提供稳定币托管服务", "source": "CoinDesk", "date": "2025-01-07"},
    
    # 融资并购类
    {"title": "稳定币基础设施公司Fireblocks完成5.5亿美元C轮融资", "source": "TechCrunch", "date": "2025-01-10"},
    {"title": "Circle考虑2025年下半年IPO，估值或达150亿美元", "source": "Bloomberg", "date": "2025-01-09"},
    {"title": "BVNK完成5000万美元B轮融资，由Haun Ventures领投", "source": "The Block", "date": "2025-01-08"},
    {"title": "Visa收购欧洲稳定币支付公司，交易金额未披露", "source": "Financial Times", "date": "2025-01-07"},
    {"title": "Mastercard宣布战略投资稳定币钱包提供商Copper", "source": "Reuters", "date": "2025-01-06"},
    
    # 不相关新闻
    {"title": "比特币价格突破10万美元创历史新高", "source": "CNBC", "date": "2025-01-10"},
    {"title": "以太坊完成上海升级，质押提款正式开启", "source": "CoinDesk", "date": "2025-01-09"},
    {"title": "特斯拉发布新款电动车Model Y 2025", "source": "TechCrunch", "date": "2025-01-08"},
    {"title": "苹果公司宣布推出Vision Pro 2", "source": "The Verge", "date": "2025-01-08"},
    {"title": "今天天气晴朗，适合户外活动", "source": "Weather.com", "date": "2025-01-10"},
]

# =========================
# 核心功能：智能分类
# =========================

def classify_news(title):
    """
    对新闻进行智能分类
    返回: (是否相关, 分类, 匹配的关键词列表)
    """
    title_lower = title.lower()
    matched_keywords = []
    
    # 检查政策监管类（优先级最高）
    for kw in policy_keywords:
        if kw.lower() in title_lower:
            matched_keywords.append(kw)
    
    if matched_keywords:
        return (True, "📋 政策监管", matched_keywords)
    
    # 检查融资并购类
    for kw in funding_keywords:
        if kw.lower() in title_lower:
            matched_keywords.append(kw)
    
    if matched_keywords:
        return (True, "💰 融资并购", matched_keywords)
    
    # 检查公司动态类
    for kw in company_keywords:
        if kw.lower() in title_lower:
            matched_keywords.append(kw)
    
    if matched_keywords:
        return (True, "🏢 公司动态", matched_keywords)
    
    return (False, "❌ 不相关", [])

# =========================
# 核心功能：优先级评估
# =========================

def assess_priority(title, category, keywords):
    """
    根据标题、分类和关键词评估优先级
    """
    title_lower = title.lower()
    
    # 超高优先级：监管执法类
    ultra_high = ["enforcement action", "sanctions", "OFAC", "罚款", "执法", "禁令"]
    
    # 高优先级关键词
    high_keywords = [
        "MiCA", "牌照", "license", "licensing", "regulation",
        "融资", "funding", "acquisition", "merger", "IPO",
        "HKMA", "MAS", "SEC"
    ]
    
    # 中优先级关键词
    medium_keywords = [
        "partnership", "合作", "推出", "launch", "支持", "support"
    ]
    
    # 根据分类给基础分
    if category == "📋 政策监管":
        base_priority = 1  # 政策天然高优先级
    elif category == "💰 融资并购":
        base_priority = 1  # 融资也很重要
    else:
        base_priority = 2  # 公司动态稍低
    
    # 检查超高优先级
    if any(kw in title_lower for kw in ultra_high):
        return "🔴 紧急"
    
    # 检查高优先级
    if base_priority == 1 or any(kw in title_lower for kw in high_keywords):
        return "🔴 高"
    elif any(kw in title_lower for kw in medium_keywords):
        return "🟡 中"
    else:
        return "⚪️ 低"

# =========================
# 核心功能：提取关键实体
# =========================

def extract_entities(title, keywords):
    """
    从标题中提取关键实体（公司、机构等）
    """
    entities = {
        "companies": [],
        "regulators": [],
        "products": []
    }
    
    # 监管机构
    regulators = ["SEC", "CFTC", "MAS", "HKMA", "OFAC", "OCC", "FinCEN"]
    for reg in regulators:
        if reg in title:
            entities["regulators"].append(reg)
    
    # 公司
    for company in company_keywords:
        if company in title:
            entities["companies"].append(company)
    
    # 稳定币产品
    products = ["USDC", "USDT", "PYUSD", "DAI"]
    for prod in products:
        if prod in title:
            entities["products"].append(prod)
    
    return entities

# =========================
# 主程序：过滤和分析
# =========================

print("=" * 90)
print("稳定币新闻智能过滤器 v2.0")
print("=" * 90)

# 统计
total_news = len(all_news)
relevant_news = []

# 过滤和分类
for news in all_news:
    is_relevant, category, keywords = classify_news(news["title"])
    
    if is_relevant:
        priority = assess_priority(news["title"], category, keywords)
        entities = extract_entities(news["title"], keywords)
        
        news["category"] = category
        news["priority"] = priority
        news["keywords"] = keywords
        news["entities"] = entities
        relevant_news.append(news)

# =========================
# 统计信息
# =========================

print(f"\n📊 过滤统计:")
print(f"  总新闻数: {total_news} 条")
print(f"  相关新闻: {len(relevant_news)} 条")
print(f"  过滤率: {len(relevant_news)/total_news*100:.1f}%")
print(f"  无关新闻: {total_news - len(relevant_news)} 条")

# =========================
# 分类统计
# =========================

categories_count = {}
for news in relevant_news:
    cat = news["category"]
    categories_count[cat] = categories_count.get(cat, 0) + 1

print(f"\n📂 分类分布:")
for category, count in sorted(categories_count.items(), key=lambda x: x[1], reverse=True):
    percentage = count / len(relevant_news) * 100
    print(f"  {category}: {count} 条 ({percentage:.1f}%)")

# =========================
# 按优先级排序并展示
# =========================

print("\n" + "=" * 90)
print("相关新闻详情（按优先级排序）")
print("=" * 90)

# 排序：紧急 > 高 > 中 > 低
priority_order = {"🔴 紧急": 0, "🔴 高": 1, "🟡 中": 2, "⚪️ 低": 3}
relevant_news.sort(key=lambda x: (priority_order[x["priority"]], x["date"]), reverse=True)

for i, news in enumerate(relevant_news, 1):
    print(f"\n{i}. {news['priority']} | {news['category']}")
    print(f"   📰 {news['title']}")
    print(f"   🔗 {news['source']} | 📅 {news['date']}")
    
    # 显示关键词（最多5个）
    if news['keywords']:
        kw_display = ', '.join(news['keywords'][:5])
        if len(news['keywords']) > 5:
            kw_display += f" (+{len(news['keywords'])-5}个)"
        print(f"   🔑 关键词: {kw_display}")
    
    # 显示实体
    entities = news['entities']
    entity_parts = []
    if entities['companies']:
        entity_parts.append(f"公司: {', '.join(entities['companies'][:3])}")
    if entities['regulators']:
        entity_parts.append(f"机构: {', '.join(entities['regulators'])}")
    if entities['products']:
        entity_parts.append(f"产品: {', '.join(entities['products'])}")
    
    if entity_parts:
        print(f"   🏷️  {' | '.join(entity_parts)}")

# =========================
# 高优先级新闻单独汇总
# =========================

high_priority = [n for n in relevant_news if n['priority'] in ["🔴 紧急", "🔴 高"]]

if high_priority:
    print("\n" + "=" * 90)
    print(f"⚠️  高优先级新闻摘要（{len(high_priority)} 条）")
    print("=" * 90)
    
    for news in high_priority:
        print(f"\n{news['priority']} {news['category']}")
        print(f"  {news['title']}")

# =========================
# 导出功能
# =========================

def export_to_markdown(news_list):
    """将过滤后的新闻导出为 Markdown 格式"""
    with open("data/filtered_news.md", "w", encoding="utf-8") as f:
        f.write("# 稳定币相关新闻汇总\n\n")
        f.write(f"**生成时间**: 2025-01-10\n")
        f.write(f"**总新闻数**: {total_news} 条\n")
        f.write(f"**相关新闻**: {len(news_list)} 条\n\n")
        
        f.write("---\n\n")
        
        # 按分类组织
        for category in ["📋 政策监管", "💰 融资并购", "🏢 公司动态"]:
            cat_news = [n for n in news_list if n['category'] == category]
            if cat_news:
                f.write(f"## {category} ({len(cat_news)} 条)\n\n")
                
                for news in cat_news:
                    f.write(f"### {news['priority']} {news['title']}\n\n")
                    f.write(f"- **来源**: {news['source']}\n")
                    f.write(f"- **日期**: {news['date']}\n")
                    
                    if news['keywords']:
                        f.write(f"- **关键词**: {', '.join(news['keywords'][:5])}\n")
                    
                    entities = news['entities']
                    if entities['companies']:
                        f.write(f"- **涉及公司**: {', '.join(entities['companies'])}\n")
                    if entities['regulators']:
                        f.write(f"- **监管机构**: {', '.join(entities['regulators'])}\n")
                    
                    f.write("\n")
        
        f.write("---\n\n")
        f.write(f"*由稳定币新闻智能过滤器生成*\n")
    
    print(f"\n✅ 已导出 Markdown 格式到 data/filtered_news.md")

def export_to_text(news_list):
    """将过滤后的新闻导出为纯文本"""
    with open("data/filtered_news.txt", "w", encoding="utf-8") as f:
        f.write("稳定币相关新闻汇总\n")
        f.write("=" * 90 + "\n\n")
        
        for i, news in enumerate(news_list, 1):
            f.write(f"{i}. {news['priority']} | {news['category']}\n")
            f.write(f"   {news['title']}\n")
            f.write(f"   {news['source']} | {news['date']}\n\n")
        
        f.write(f"\n总计: {len(news_list)} 条相关新闻\n")
    
    print(f"✅ 已导出纯文本格式到 data/filtered_news.txt")

# 创建 data 文件夹（如果不存在）
import os
os.makedirs("data", exist_ok=True)

# 调用导出
export_to_markdown(relevant_news)
export_to_text(relevant_news)

print("\n" + "=" * 90)
print("过滤完成！")
print("=" * 90)