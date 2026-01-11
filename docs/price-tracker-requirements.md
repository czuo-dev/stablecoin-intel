#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格追踪器测试脚本
生成测试数据并验证所有功能
"""

import json
import os
import random
from datetime import datetime, timedelta


# 配置
DATA_DIR = "data"
PRICE_FILE = os.path.join(DATA_DIR, "prices.json")
ALERT_FILE = os.path.join(DATA_DIR, "alerts.json")


def setup_test_environment():
    """设置测试环境"""
    print("=" * 60)
    print("🧪 设置测试环境")
    print("=" * 60)
    
    # 创建 data 目录
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"✓ 创建目录：{DATA_DIR}")
    
    # 清空现有数据（可选）
    if os.path.exists(PRICE_FILE):
        print(f"⚠ 发现现有价格数据，将追加新数据")
    
    if os.path.exists(ALERT_FILE):
        os.remove(ALERT_FILE)
        print(f"✓ 清空告警历史")


def generate_test_prices():
    """
    生成测试价格数据
    包含以下场景：
    1. 正常价格（波动 < 0.5%）
    2. 告警价格（波动 0.5% - 1%）
    3. 脱锚价格（波动 > 1%）
    """
    print("\n" + "=" * 60)
    print("📊 生成测试价格数据")
    print("=" * 60)
    
    test_data = []
    base_time = datetime.now() - timedelta(hours=48)
    
    # 定义不同的价格场景
    scenarios = [
        # 时间段1: 正常价格（0-12小时）
        {"hours": 0, "duration": 12, "usdc_dev": 0.002, "usdt_dev": 0.001, "dai_dev": 0.003, "desc": "正常波动"},
        
        # 时间段2: USDC 告警（12-18小时）
        {"hours": 12, "duration": 6, "usdc_dev": 0.007, "usdt_dev": 0.001, "dai_dev": 0.003, "desc": "USDC 告警"},
        
        # 时间段3: DAI 脱锚（18-24小时）
        {"hours": 18, "duration": 6, "usdc_dev": 0.002, "usdt_dev": 0.001, "dai_dev": 0.015, "desc": "DAI 脱锚"},
        
        # 时间段4: 价格恢复（24-36小时）
        {"hours": 24, "duration": 12, "usdc_dev": 0.002, "usdt_dev": 0.001, "dai_dev": 0.004, "desc": "价格恢复"},
        
        # 时间段5: 多币种异常（36-48小时）
        {"hours": 36, "duration": 12, "usdc_dev": 0.006, "usdt_dev": 0.008, "dai_dev": 0.005, "desc": "多币种告警"},
    ]
    
    for scenario in scenarios:
        start_hour = scenario["hours"]
        duration = scenario["duration"]
        
        print(f"\n时间段 {start_hour}-{start_hour + duration} 小时: {scenario['desc']}")
        
        # 每30分钟一个数据点
        for i in range(duration * 2):
            timestamp = base_time + timedelta(hours=start_hour, minutes=30 * i)
            
            # 生成价格（$1 ± 偏差）
            usdc_price = 1.0 + random.uniform(-scenario["usdc_dev"], scenario["usdc_dev"])
            usdt_price = 1.0 + random.uniform(-scenario["usdt_dev"], scenario["usdt_dev"])
            dai_price = 1.0 + random.uniform(-scenario["dai_dev"], scenario["dai_dev"])
            
            test_data.append({
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "prices": {
                    "USDC": round(usdc_price, 6),
                    "USDT": round(usdt_price, 6),
                    "DAI": round(dai_price, 6)
                }
            })
    
    # 保存测试数据
    with open(PRICE_FILE, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ 已生成 {len(test_data)} 个数据点")
    print(f"✓ 数据已保存到：{PRICE_FILE}")
    
    # 显示数据摘要
    print("\n数据摘要：")
    latest = test_data[-1]
    print(f"最新时间：{latest['timestamp']}")
    for coin, price in latest['prices'].items():
        deviation = abs(price - 1.0) * 100
        print(f"  {coin}: ${price:.6f} (偏离 {deviation:.3f}%)")


def display_test_scenarios():
    """显示测试场景说明"""
    print("\n" + "=" * 60)
    print("📋 测试场景说明")
    print("=" * 60)
    
    scenarios = [
        ("✓", "正常波动", "价格偏离 < 0.5%", "无告警，无脱锚"),
        ("⚠", "告警触发", "价格偏离 0.5% - 1%", "红色告警显示"),
        ("🚨", "脱锚警报", "价格偏离 > 1%", "脱锚警报显示"),
        ("📊", "趋势图表", "48小时历史数据", "ASCII 图表显示"),
        ("📜", "历史记录", "所有时间点数据", "最近10条记录"),
    ]
    
    for icon, name, condition, expected in scenarios:
        print(f"\n{icon} {name}")
        print(f"   条件：{condition}")
        print(f"   预期：{expected}")


def verify_files():
    """验证生成的文件"""
    print("\n" + "=" * 60)
    print("🔍 验证生成的文件")
    print("=" * 60)
    
    # 检查价格文件
    if os.path.exists(PRICE_FILE):
        with open(PRICE_FILE, 'r') as f:
            data = json.load(f)
        print(f"✓ {PRICE_FILE}")
        print(f"  包含 {len(data)} 条价格记录")
    else:
        print(f"✗ {PRICE_FILE} 不存在")
    
    # 检查告警文件
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, 'r') as f:
            data = json.load(f)
        print(f"✓ {ALERT_FILE}")
        print(f"  包含 {len(data)} 条告警记录")
    else:
        print(f"ℹ {ALERT_FILE} 尚未生成（运行 price_tracker.py 后会创建）")


def run_manual_test():
    """运行手动测试"""
    print("\n" + "=" * 60)
    print("🚀 准备运行测试")
    print("=" * 60)
    
    print("\n现在请运行以下命令测试功能：")
    print("\n  python scripts/price_tracker.py")
    
    print("\n你应该看到：")
    print("  ✓ 当前价格（带颜色标识）")
    print("  ⚠ 告警提示（红色）")
    print("  🚨 脱锚警报")
    print("  📜 价格历史（最近10条）")
    print("  ⚠ 告警历史")
    print("  📊 价格趋势图（3个币种，48小时）")


def create_quick_test():
    """创建快速测试：只生成最近几个数据点，用于触发实时告警"""
    print("\n" + "=" * 60)
    print("⚡ 创建快速测试数据（触发实时告警）")
    print("=" * 60)
    
    quick_data = []
    
    # 添加几个正常价格
    for i in range(3):
        timestamp = datetime.now() - timedelta(minutes=10 * (3 - i))
        quick_data.append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "prices": {
                "USDC": 0.9999,
                "USDT": 1.0001,
                "DAI": 0.9998
            }
        })
    
    # 添加触发告警的价格
    quick_data.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prices": {
            "USDC": 0.994,   # 触发告警（-0.6%）
            "USDT": 1.0001,  # 正常
            "DAI": 1.012     # 触发脱锚（+1.2%）
        }
    })
    
    # 保存
    quick_file = os.path.join(DATA_DIR, "prices_quick_test.json")
    with open(quick_file, 'w', encoding='utf-8') as f:
        json.dump(quick_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 快速测试数据已保存到：{quick_file}")
    print("\n要使用快速测试，请临时重命名文件：")
    print(f"  mv {PRICE_FILE} {PRICE_FILE}.backup")
    print(f"  mv {quick_file} {PRICE_FILE}")
    print("  python scripts/price_tracker.py")
    print(f"  mv {PRICE_FILE}.backup {PRICE_FILE}")


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("🧪 稳定币价格追踪器 - 测试套件")
    print("=" * 60)
    
    # 1. 设置测试环境
    setup_test_environment()
    
    # 2. 生成测试数据
    generate_test_prices()
    
    # 3. 显示测试场景
    display_test_scenarios()
    
    # 4. 验证文件
    verify_files()
    
    # 5. 创建快速测试
    create_quick_test()
    
    # 6. 运行说明
    run_manual_test()
    
    print("\n" + "=" * 60)
    print("✓ 测试准备完成")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()