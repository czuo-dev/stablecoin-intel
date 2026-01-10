# 我的第一个 Python 脚本
print("Hello, Stablecoin World!")

# 基础运算
price_usdc = 1.00
price_usdt = 0.99
total = price_usdc + price_usdt

print(f"USDC 价格: ${price_usdc}")
print(f"USDT 价格: ${price_usdt}")
print(f"总计: ${total}")

# 列表示例
stablecoins = ["USDC", "USDT", "DAI", "BUSD"]
print(f"\n支持的稳定币: {stablecoins}")
print(f"共 {len(stablecoins)} 种")