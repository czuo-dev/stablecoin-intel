# 稳定币关键词管理器
# 用途：读取、显示、添加关键词

# =========================
# 政策 / 监管类关键词
# =========================
policy_keywords = [
    # 英文 - 框架 / 法案
    "stablecoin regulation",
    "stablecoin bill",
    "digital asset regulation",
    "payment regulation",
    "licensing framework",
    "regulatory guidance",
    "consultation paper",
    "enforcement action",
    "sanctions",
    "OFAC",

    # 英文 - 具体制度 / 法规
    "MiCA",
    "EMT stablecoin",
    "ART stablecoin",
    "GENIUS Act",
    "Clarity Act",
    "Stablecoin Act",

    # 机构
    "SEC",
    "CFTC",
    "FinCEN",
    "OCC",
    "US Treasury",
    "MAS",
    "HKMA",
    "ESMA",
    "EBA",

    # 新加坡 / 香港 / 中国语境
    "MSA",
    "TCSP",
    "PSA",
    "DTSP",
    "VASP",
    "VATP",

    # 中文
    "监管",
    "合规",
    "牌照",
    "稳定币监管",
    "支付监管",
    "沙盒",
    "罚款",
    "执法",
]

# =========================
# 公司 / 大机构类关键词
# =========================
company_keywords = [
    # 稳定币核心
    "Circle",
    "Tether",
    "USDC",
    "USDT",
    "PYUSD",

    # 支付 / 金融科技
    "Stripe",
    "Visa",
    "PayPal",
    "Mastercard",

    # 钱包 / 托管 / Infra
    "Fireblocks",
    "BVNK",
    "Anchorage",
    "BitGo",
    "Copper",
    "Metaco",

    # 银行 / 大机构
    "JP Morgan",
    "Onyx",
    "Goldman Sachs",
    "HSBC",
    "Standard Chartered",

    # 交易所 / 出入金
    "Coinbase",
    "Binance",
    "OKX",
    "Kraken",
]

# =========================
# 融资 / 并购类关键词
# =========================
funding_keywords = [
    # 英文 - 融资
    "funding round",
    "raises",
    "raised",
    "investment",
    "strategic investment",
    "venture capital",
    "Series A",
    "Series B",
    "Series C",
    "valuation",
    "post-money",

    # 并购 / 战略
    "acquisition",
    "acquired",
    "merger",
    "strategic partnership",
    "minority stake",

    # 中文
    "融资",
    "投资",
    "并购",
    "收购",
    "战略投资",
]

# =========================
# 打印所有关键词
# =========================
print("=" * 50)
print("稳定币情报关键词库")
print("=" * 50)

print("\n📋 政策监管类 ({} 个):".format(len(policy_keywords)))
for keyword in policy_keywords:
    print(f"  - {keyword}")

print("\n🏢 公司 / 机构类 ({} 个):".format(len(company_keywords)))
for keyword in company_keywords:
    print(f"  - {keyword}")

print("\n💰 融资 / 并购类 ({} 个):".format(len(funding_keywords)))
for keyword in funding_keywords:
    print(f"  - {keyword}")

# 在最后添加总计
total_keywords = len(policy_keywords) + len(company_keywords) + len(funding_keywords)
print("\n" + "=" * 50)
print(f"总计: {total_keywords} 个关键词")
print("=" * 50)
