#!/bin/bash
# 稳定币关键词生成脚本

# 定义目标文件
OUTPUT_FILE="../notes/keywords.txt"

# 删除旧文件（如果存在）
rm -f $OUTPUT_FILE

# 创建新文件并写入内容
cat > $OUTPUT_FILE << 'EOF'
# 稳定币行业情报关键词清单

## 政策监管类
- regulation
- licensing
- MiCA
- compliance
- 监管
- 牌照
- MAS

## 大公司动态
- Circle
- Tether
- USDC
- PayPal PYUSD
- Visa
- Stripe
- Fireblocks
- BVNK

## 融资事件
- funding round
- Series A/B/C
- investment
- 融资

## 产品技术
- cross-border payment
- reserves
- 跨境支付
EOF

echo "✅ keywords.txt 已更新！"
cat $OUTPUT_FILE