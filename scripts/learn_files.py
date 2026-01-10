# Python 文件操作学习

import os

# =========================
# Part 1: 写入文件
# =========================

print("=" * 50)
print("1. 写入文件")
print("=" * 50)

# 确保 data 文件夹存在
os.makedirs("data", exist_ok=True)

# 写入文本文件
with open("data/test_write.txt", "w", encoding="utf-8") as f:
    f.write("这是第一行\n")
    f.write("这是第二行\n")
    f.write("USDC, USDT, DAI\n")

print("✅ 已写入 data/test_write.txt")

# =========================
# Part 2: 读取文件
# =========================

print("\n" + "=" * 50)
print("2. 读取文件")
print("=" * 50)

# 读取整个文件
with open("data/test_write.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print("文件内容:")
    print(content)

# 按行读取
print("\n按行读取:")
with open("data/test_write.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        print(f"第 {i} 行: {line.strip()}")  # strip() 去掉换行符

# =========================
# Part 3: 追加内容
# =========================

print("\n" + "=" * 50)
print("3. 追加内容到文件")
print("=" * 50)

# 用 'a' 模式追加（不会覆盖原内容）
with open("data/test_write.txt", "a", encoding="utf-8") as f:
    f.write("这是追加的第四行\n")
    f.write("Tether, Circle, PayPal\n")

print("✅ 已追加内容")

# 再次读取查看结果
with open("data/test_write.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print("\n追加后的内容:")
    print(content)

# =========================
# Part 4: 处理 CSV 格式
# =========================

print("\n" + "=" * 50)
print("4. CSV 格式数据")
print("=" * 50)

# 写入 CSV 数据
stablecoins_data = [
    "名称,发行方,市值",
    "USDC,Circle,35000000000",
    "USDT,Tether,120000000000",
    "DAI,MakerDAO,5000000000"
]

with open("data/stablecoins.csv", "w", encoding="utf-8") as f:
    for line in stablecoins_data:
        f.write(line + "\n")

print("✅ 已写入 data/stablecoins.csv")

# 读取并解析 CSV
print("\n读取 CSV:")
with open("data/stablecoins.csv", "r", encoding="utf-8") as f:
    lines = f.readlines()
    
    # 第一行是表头
    header = lines[0].strip().split(",")
    print(f"表头: {header}")
    
    # 处理数据行
    print("\n数据:")
    for line in lines[1:]:  # 跳过表头
        values = line.strip().split(",")
        name, issuer, market_cap = values
        print(f"  {name}: {issuer} - ${int(market_cap):,}")

# =========================
# Part 5: JSON 格式
# =========================

print("\n" + "=" * 50)
print("5. JSON 格式数据")
print("=" * 50)

import json

# Python 字典
stablecoin_info = {
    "USDC": {
        "issuer": "Circle",
        "market_cap": 35000000000,
        "regulated": True,
        "chains": ["Ethereum", "Solana", "Polygon"]
    },
    "USDT": {
        "issuer": "Tether",
        "market_cap": 120000000000,
        "regulated": False,
        "chains": ["Ethereum", "Tron", "BSC"]
    }
}

# 写入 JSON 文件
with open("data/stablecoins.json", "w", encoding="utf-8") as f:
    json.dump(stablecoin_info, f, ensure_ascii=False, indent=2)

print("✅ 已写入 data/stablecoins.json")

# 读取 JSON 文件
with open("data/stablecoins.json", "r", encoding="utf-8") as f:
    loaded_data = json.load(f)

print("\n从 JSON 读取的数据:")
for coin, info in loaded_data.items():
    print(f"\n{coin}:")
    print(f"  发行方: {info['issuer']}")
    print(f"  市值: ${info['market_cap']:,}")
    print(f"  受监管: {info['regulated']}")
    print(f"  支持链: {', '.join(info['chains'])}")

# =========================
# Part 6: 检查文件是否存在
# =========================

print("\n" + "=" * 50)
print("6. 检查文件")
print("=" * 50)

files_to_check = [
    "data/stablecoins.json",
    "data/not_exist.txt",
    "data/test_write.txt"
]

for filepath in files_to_check:
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {filepath} 存在 (大小: {size} 字节)")
    else:
        print(f"❌ {filepath} 不存在")

# =========================
# 总结
# =========================

print("\n" + "=" * 50)
print("文件操作总结")
print("=" * 50)
print("""
模式说明:
  'r'  - 读取（文件必须存在）
  'w'  - 写入（会覆盖原文件）
  'a'  - 追加（在文件末尾添加）
  
常用操作:
  - f.read()       读取全部内容
  - f.readlines()  按行读取（列表）
  - f.write(text)  写入文本
  - json.dump()    写入 JSON
  - json.load()    读取 JSON
""")