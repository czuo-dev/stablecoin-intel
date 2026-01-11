# Python 字典学习

# =========================
# 基础：创建字典
# =========================

# 稳定币信息
usdc_info = {
    "name": "USD Coin",
    "symbol": "USDC",
    "issuer": "Circle",
    "price": 1.00,
    "market_cap": 74000000000,  # 740亿美元
    "chains": ["Ethereum", "Solana", "Polygon"]
}

# 打印整个字典
print("USDC 信息:")
print(usdc_info)

# =========================
# 访问字典中的值
# =========================

print("\n" + "=" * 50)
print("访问单个值:")
print("=" * 50)

# 用 key 获取 value
print(f"名称: {usdc_info['name']}")
print(f"发行方: {usdc_info['issuer']}")
print(f"价格: ${usdc_info['price']}")
print(f"市值: ${usdc_info['market_cap']:,}")  # 千分位格式化

# =========================
# 修改字典
# =========================

print("\n" + "=" * 50)
print("修改值:")
print("=" * 50)

# 修改价格
usdc_info["price"] = 0.9999
print(f"新价格: ${usdc_info['price']}")

# 添加新的键值对
usdc_info["regulated"] = True
print(f"是否受监管: {usdc_info['regulated']}")

# =========================
# 多个稳定币对比
# =========================

print("\n" + "=" * 50)
print("稳定币对比:")
print("=" * 50)

stablecoins = {
    "USDC": {
        "issuer": "Circle",
        "market_cap": 76000000000,
        "regulated": True
    },
    "USDT": {
        "issuer": "Tether",
        "market_cap": 180000000000,
        "regulated": False
    },
    "DAI": {
        "issuer": "MakerDAO",
        "market_cap": 4000000000,
        "regulated": False
    }
}

# 遍历所有稳定币
for coin, info in stablecoins.items():
    print(f"\n{coin}:")
    print(f"  发行方: {info['issuer']}")
    print(f"  市值: ${info['market_cap']:,}")
    print(f"  受监管: {'是' if info['regulated'] else '否'}")

# =========================
# 实用操作
# =========================

print("\n" + "=" * 50)
print("实用操作:")
print("=" * 50)

# 检查 key 是否存在
if "USDC" in stablecoins:
    print("✅ USDC 在列表中")

# 获取所有 key
print(f"所有稳定币: {list(stablecoins.keys())}")

# 获取所有 value
print(f"共 {len(stablecoins)} 个稳定币")

# 安全获取值（如果不存在返回默认值）
busd_info = stablecoins.get("BUSD", "未找到")
print(f"BUSD 信息: {busd_info}")