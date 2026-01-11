# Python 条件判断学习

# =========================
# 基础 if/else
# =========================

print("=" * 50)
print("稳定币风险评估")
print("=" * 50)

# 示例1：评估市值
market_cap = 35000000000  # USDC 市值

if market_cap > 100000000000:
    risk_level = "低风险"
elif market_cap > 10000000000:
    risk_level = "中风险"
else:
    risk_level = "高风险"

print(f"\n市值: ${market_cap:,}")
print(f"风险等级: {risk_level}")

# =========================
# 多条件判断
# =========================

print("\n" + "=" * 50)
print("监管合规检查")
print("=" * 50)

stablecoin = {
    "name": "USDC",
    "regulated": True,
    "reserves_audited": True,
    "market_cap": 35000000000
}

# 使用 and, or, not
if stablecoin["regulated"] and stablecoin["reserves_audited"]:
    compliance_score = "优秀"
elif stablecoin["regulated"] or stablecoin["reserves_audited"]:
    compliance_score = "良好"
else:
    compliance_score = "需改进"

print(f"{stablecoin['name']} 合规评分: {compliance_score}")

# =========================
# 实战：新闻分类
# =========================

print("\n" + "=" * 50)
print("新闻智能分类")
print("=" * 50)

# 假设这是从网上抓取的新闻标题
news_titles = [
    "Circle获得新加坡MAS支付牌照",
    "Tether完成20亿美元融资",
    "美国SEC对稳定币发行商展开调查",
    "PayPal推出PYUSD稳定币",
    "今天天气真好"
]

# 导入之前的关键词（简化版）
policy_keywords = ["MAS", "牌照", "SEC", "调查", "监管"]
company_keywords = ["Circle", "Tether", "PayPal", "USDC"]
funding_keywords = ["融资", "投资", "并购"]

# 分类每条新闻
for title in news_titles:
    print(f"\n标题: {title}")
    
    # 判断是否包含关键词
    has_policy = any(kw in title for kw in policy_keywords)
    has_company = any(kw in title for kw in company_keywords)
    has_funding = any(kw in title for kw in funding_keywords)
    
    # 分类
    if has_policy:
        category = "📋 政策监管"
    elif has_funding:
        category = "💰 融资事件"
    elif has_company:
        category = "🏢 公司动态"
    else:
        category = "❌ 不相关"
    
    print(f"分类: {category}")

# =========================
# 优先级判断
# =========================

print("\n" + "=" * 50)
print("新闻优先级评估")
print("=" * 50)

def assess_priority(title):
    """评估新闻优先级"""
    # 高优先级关键词
    high_priority = ["禁令", "调查", "融资", "牌照"]
    medium_priority = ["推出", "发布", "合作"]
    
    if any(kw in title for kw in high_priority):
        return "🔴 高优先级"
    elif any(kw in title for kw in medium_priority):
        return "🟡 中优先级"
    else:
        return "⚪️ 低优先级"

# 测试优先级
for title in news_titles[:4]:  # 只测试前4条
    priority = assess_priority(title)
    print(f"{priority} - {title}")