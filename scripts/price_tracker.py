#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
稳定币价格追踪器 - 完整集成版
功能：
1. 实时价格追踪（USDC、USDT、DAI）
2. 价格历史记录
3. 脱锚检测（1%阈值）
4. 价格告警（0.5%阈值）
5. ASCII 价格趋势图表
6. 完整的错误处理
"""

import requests
import json
import os
from datetime import datetime, timedelta


# ============ 配置部分 ============
# CoinGecko API 端点（免费，无需 API Key）
API_URL = "https://api.coingecko.com/api/v3/simple/price"
PARAMS = {
    "ids": "usd-coin,tether,dai",  # 要查询的币种
    "vs_currencies": "usd"          # 对标货币
}

# 数据文件路径
DATA_DIR = "data"
PRICE_FILE = os.path.join(DATA_DIR, "prices.json")
ALERT_FILE = os.path.join(DATA_DIR, "alerts.json")

# 阈值设置
DEPEG_THRESHOLD = 0.01      # 脱锚阈值（1%）
ALERT_THRESHOLD = 0.005     # 告警阈值（0.5%）

# 图表设置
CHART_HEIGHT = 7            # 图表高度（行数）
CHART_WIDTH = 48            # 图表宽度（数据点数）

# 币种映射（CoinGecko ID 到显示名称）
COIN_MAPPING = {
    "usd-coin": "USDC",
    "tether": "USDT",
    "dai": "DAI"
}

# 终端颜色代码
class Colors:
    RED = '\033[91m'        # 红色
    GREEN = '\033[92m'      # 绿色
    YELLOW = '\033[93m'     # 黄色
    BLUE = '\033[94m'       # 蓝色
    BOLD = '\033[1m'        # 粗体
    END = '\033[0m'         # 重置


# ============ 核心功能函数 ============

def fetch_prices():
    """
    从 CoinGecko 获取实时价格
    
    返回:
        dict: 包含价格信息的字典，格式为 {"USDC": 0.9999, "USDT": 1.0001, ...}
        None: 如果请求失败
    """
    try:
        print("正在获取实时价格...")
        
        # 发送 HTTP GET 请求
        response = requests.get(API_URL, params=PARAMS, timeout=10)
        
        # 检查响应状态码
        response.raise_for_status()
        
        # 解析 JSON 数据
        data = response.json()
        
        # 转换为友好的格式
        prices = {}
        for coingecko_id, display_name in COIN_MAPPING.items():
            if coingecko_id in data and "usd" in data[coingecko_id]:
                prices[display_name] = data[coingecko_id]["usd"]
        
        print(f"{Colors.GREEN}✓ 价格获取成功{Colors.END}")
        return prices
        
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}✗ 错误：请求超时，请检查网络连接{Colors.END}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ 错误：无法连接到 CoinGecko API{Colors.END}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}✗ 错误：API 请求失败 - {e}{Colors.END}")
        return None
    except (KeyError, ValueError) as e:
        print(f"{Colors.RED}✗ 错误：数据解析失败 - {e}{Colors.END}")
        return None


def ensure_data_directory():
    """
    确保 data 目录存在，如果不存在则创建
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"{Colors.GREEN}✓ 创建数据目录：{DATA_DIR}{Colors.END}")


def save_price_data(prices):
    """
    保存价格数据到 JSON 文件
    
    参数:
        prices (dict): 价格字典
    
    返回:
        bool: 保存是否成功
    """
    try:
        ensure_data_directory()
        
        # 加载现有数据
        history = load_price_history()
        
        # 创建新的价格记录
        new_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prices": prices
        }
        
        # 添加到历史记录
        history.append(new_record)
        
        # 保存到文件
        with open(PRICE_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.GREEN}✓ 数据已保存到：{PRICE_FILE}{Colors.END}")
        return True
        
    except IOError as e:
        print(f"{Colors.RED}✗ 错误：文件写入失败 - {e}{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗ 错误：保存数据失败 - {e}{Colors.END}")
        return False


def load_price_history():
    """
    从文件加载价格历史记录
    
    返回:
        list: 历史价格记录列表
    """
    try:
        if os.path.exists(PRICE_FILE):
            with open(PRICE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    except json.JSONDecodeError:
        print(f"{Colors.YELLOW}⚠ 警告：价格文件格式错误，将创建新文件{Colors.END}")
        return []
    except Exception as e:
        print(f"{Colors.YELLOW}⚠ 警告：读取历史数据失败 - {e}{Colors.END}")
        return []


def display_current_prices(prices):
    """
    显示当前价格
    
    参数:
        prices (dict): 价格字典
    """
    print("\n" + "="*50)
    print(f"{Colors.BOLD}当前稳定币价格{Colors.END}")
    print("="*50)
    
    for coin, price in prices.items():
        # 计算与 $1 的偏离
        deviation = abs(price - 1.0)
        deviation_percent = deviation * 100
        
        # 根据偏离程度选择颜色
        if deviation > ALERT_THRESHOLD:
            color = Colors.RED
        elif deviation > DEPEG_THRESHOLD / 2:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN
        
        # 显示价格
        print(f"{coin:6s}: {color}${price:.6f}{Colors.END}  (偏离: {deviation_percent:.4f}%)")
    
    print("="*50)


def display_price_history(limit=10):
    """
    显示历史价格记录
    
    参数:
        limit (int): 显示最近多少条记录
    """
    history = load_price_history()
    
    if not history:
        print(f"\n{Colors.YELLOW}暂无历史价格数据{Colors.END}")
        return
    
    print("\n" + "="*50)
    print(f"{Colors.BOLD}价格历史（最近 {limit} 条）{Colors.END}")
    print("="*50)
    
    # 获取最近的记录（倒序）
    recent = history[-limit:]
    recent.reverse()
    
    for record in recent:
        print(f"\n{Colors.BLUE}时间：{record['timestamp']}{Colors.END}")
        for coin, price in record['prices'].items():
            print(f"  {coin:6s}: ${price:.6f}")
    
    print("="*50)


# ============ 脱锚检测功能 ============

def check_depegging(prices):
    """
    检查是否有稳定币脱锚（1%阈值）
    
    参数:
        prices (dict): 价格字典
    
    返回:
        list: 脱锚币种列表
    """
    depegged = []
    
    for coin, price in prices.items():
        deviation = abs(price - 1.0)
        if deviation > DEPEG_THRESHOLD:
            depegged.append({
                "coin": coin,
                "price": price,
                "deviation": deviation
            })
    
    return depegged


def display_depeg_alert(depegged):
    """
    显示脱锚警报
    
    参数:
        depegged (list): 脱锚币种列表
    """
    if depegged:
        print("\n" + "!"*50)
        print(f"{Colors.RED}{Colors.BOLD}⚠️  脱锚警报（1%阈值）⚠️{Colors.END}")
        print("!"*50)
        
        for item in depegged:
            direction = "高于" if item["price"] > 1.0 else "低于"
            print(f"{Colors.RED}{item['coin']} 脱锚：${item['price']:.6f} "
                  f"({direction} $1 达 {item['deviation']*100:.2f}%){Colors.END}")
        
        print("!"*50)
    else:
        print(f"\n{Colors.GREEN}✓ 所有稳定币价格稳定（脱锚检测通过）{Colors.END}")


# ============ 告警功能 ============

def check_alerts(prices):
    """
    检查价格是否触发告警条件（0.5%阈值）
    
    参数:
        prices (dict): 价格字典
    
    返回:
        list: 触发告警的币种列表
    """
    alerts = []
    
    for coin, price in prices.items():
        # 计算偏离幅度
        deviation = abs(price - 1.0)
        deviation_percent = deviation * 100
        
        # 检查是否超过告警阈值
        if deviation > ALERT_THRESHOLD:
            alerts.append({
                "coin": coin,
                "price": price,
                "deviation": deviation,
                "deviation_percent": deviation_percent
            })
            
            # 显示红色警告
            direction = "高于" if price > 1.0 else "低于"
            print(f"\n{Colors.RED}{Colors.BOLD}🚨 告警！{Colors.END}")
            print(f"{Colors.RED}{coin} 价格异常：${price:.6f}{Colors.END}")
            print(f"{Colors.RED}{direction} $1 达 {deviation_percent:.2f}% "
                  f"(阈值: {ALERT_THRESHOLD * 100}%){Colors.END}")
    
    return alerts


def add_alert(coin, price, deviation):
    """
    保存告警记录到 JSON 文件
    
    参数:
        coin (str): 币种名称
        price (float): 触发告警时的价格
        deviation (float): 偏离幅度（绝对值）
    
    返回:
        bool: 保存是否成功
    """
    try:
        ensure_data_directory()
        
        # 创建告警记录
        alert_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "coin": coin,
            "price": price,
            "deviation": round(deviation * 100, 2)  # 转换为百分比
        }
        
        # 加载现有告警历史
        alert_history = load_alert_history()
        
        # 添加新记录
        alert_history.append(alert_record)
        
        # 保存到文件
        with open(ALERT_FILE, 'w', encoding='utf-8') as f:
            json.dump(alert_history, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.GREEN}✓ 告警已记录到：{ALERT_FILE}{Colors.END}")
        return True
        
    except Exception as e:
        print(f"{Colors.RED}✗ 错误：保存告警失败 - {e}{Colors.END}")
        return False


def load_alert_history():
    """
    从文件加载告警历史记录
    
    返回:
        list: 告警历史记录列表
    """
    try:
        if os.path.exists(ALERT_FILE):
            with open(ALERT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    except json.JSONDecodeError:
        print(f"{Colors.YELLOW}⚠ 警告：告警文件格式错误，将创建新文件{Colors.END}")
        return []
    except Exception as e:
        print(f"{Colors.YELLOW}⚠ 警告：读取告警历史失败 - {e}{Colors.END}")
        return []


def display_alert_history(limit=10):
    """
    显示告警历史记录
    
    参数:
        limit (int): 显示最近多少条记录
    """
    history = load_alert_history()
    
    if not history:
        print(f"\n{Colors.GREEN}✓ 暂无告警记录{Colors.END}")
        return
    
    print("\n" + "="*50)
    print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  告警历史（最近 {limit} 条）{Colors.END}")
    print("="*50)
    
    # 获取最近的记录（倒序）
    recent = history[-limit:]
    recent.reverse()
    
    for record in recent:
        print(f"\n{Colors.RED}时间：{record['timestamp']}{Colors.END}")
        print(f"  币种：{record['coin']}")
        print(f"  价格：${record['price']:.6f}")
        print(f"  偏离：{record['deviation']}%")
    
    print("="*50)
    print(f"总告警次数：{len(history)}")


# ============ 价格趋势图表功能 ============

def get_price_data_for_chart(coin, hours=24):
    """
    获取指定币种的历史价格数据
    
    参数:
        coin (str): 币种名称
        hours (int): 获取最近多少小时的数据
    
    返回:
        list: 价格列表
    """
    try:
        if not os.path.exists(PRICE_FILE):
            return []
        
        with open(PRICE_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if not history:
            return []
        
        # 计算时间范围
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 提取该币种的价格数据
        prices = []
        for record in history:
            # 解析时间戳
            record_time = datetime.strptime(record['timestamp'], "%Y-%m-%d %H:%M:%S")
            
            # 只取指定时间范围内的数据
            if record_time >= cutoff_time:
                if coin in record['prices']:
                    prices.append(record['prices'][coin])
        
        return prices
        
    except Exception as e:
        print(f"{Colors.YELLOW}⚠ 警告：读取价格数据失败 - {e}{Colors.END}")
        return []


def draw_price_chart(coin, hours=24):
    """
    绘制 ASCII 价格趋势图
    
    参数:
        coin (str): 币种名称
        hours (int): 显示最近多少小时的数据
    """
    # 获取价格数据
    prices = get_price_data_for_chart(coin, hours)
    
    if not prices or len(prices) < 2:
        print(f"\n{Colors.YELLOW}{coin} 价格趋势：数据不足（需要至少 2 个数据点）{Colors.END}")
        return
    
    # 数据采样（如果数据点太多，取样到 CHART_WIDTH 个点）
    if len(prices) > CHART_WIDTH:
        step = len(prices) / CHART_WIDTH
        sampled_prices = [prices[int(i * step)] for i in range(CHART_WIDTH)]
    else:
        sampled_prices = prices
    
    # 计算价格范围
    min_price = min(sampled_prices)
    max_price = max(sampled_prices)
    price_range = max_price - min_price
    
    # 如果价格波动太小，扩大范围以便显示
    if price_range < 0.0001:
        center = (min_price + max_price) / 2
        min_price = center - 0.001
        max_price = center + 0.001
        price_range = 0.002
    
    # 绘制图表
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}{Colors.BOLD}{coin} 价格趋势（最近 {hours} 小时，共 {len(prices)} 个数据点）{Colors.END}")
    print(f"{'='*60}")
    
    # 绘制每一行
    for row in range(CHART_HEIGHT):
        # 计算当前行对应的价格值
        row_price = max_price - (row * price_range / (CHART_HEIGHT - 1))
        
        # 显示价格标签
        print(f"${row_price:.6f} │", end="")
        
        # 绘制趋势线
        for i, price in enumerate(sampled_prices):
            # 计算价格对应的行位置
            price_row = (max_price - price) / price_range * (CHART_HEIGHT - 1)
            
            # 判断是否在当前行
            if abs(price_row - row) < 0.5:
                # 在当前行，绘制点
                if i > 0:
                    prev_price = sampled_prices[i - 1]
                    
                    if price > prev_price:
                        print(f"{Colors.GREEN}╱{Colors.END}", end="")      # 上升
                    elif price < prev_price:
                        print(f"{Colors.RED}╲{Colors.END}", end="")        # 下降
                    else:
                        print("─", end="")                                   # 持平
                else:
                    print("●", end="")                                       # 起点
            else:
                print(" ", end="")
        
        print()  # 换行
    
    # 绘制底部
    print(" " * 11 + "└" + "─" * len(sampled_prices))
    
    # 显示统计信息
    current_price = sampled_prices[-1]
    first_price = sampled_prices[0]
    change = current_price - first_price
    change_percent = (change / first_price) * 100 if first_price != 0 else 0
    
    # 根据涨跌选择颜色
    change_color = Colors.GREEN if change >= 0 else Colors.RED
    
    print(f"\n{Colors.BOLD}统计信息：{Colors.END}")
    print(f"  当前价格：${current_price:.6f}")
    print(f"  最高价格：${max_price:.6f}")
    print(f"  最低价格：${min_price:.6f}")
    print(f"  期间变化：{change_color}${change:+.6f} ({change_percent:+.2f}%){Colors.END}")
    print(f"{'='*60}\n")


def draw_all_charts(hours=24):
    """
    绘制所有稳定币的价格趋势图
    
    参数:
        hours (int): 显示最近多少小时的数据
    """
    coins = ["USDC", "USDT", "DAI"]
    
    for coin in coins:
        draw_price_chart(coin, hours)


# ============ 主函数 ============

def main():
    """
    主函数：执行价格追踪流程
    """
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}🔍 稳定币价格追踪器 - 完整版{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    # 1. 获取实时价格
    prices = fetch_prices()
    
    if prices is None:
        print(f"\n{Colors.RED}程序终止：无法获取价格数据{Colors.END}")
        return
    
    # 2. 显示当前价格
    display_current_prices(prices)
    
    # 3. 检查告警（0.5%阈值）
    alerts = check_alerts(prices)
    
    # 4. 保存告警记录
    if alerts:
        for alert in alerts:
            add_alert(
                coin=alert['coin'],
                price=alert['price'],
                deviation=alert['deviation']
            )
    
    # 5. 检查脱锚情况（1%阈值）
    depegged = check_depegging(prices)
    display_depeg_alert(depegged)
    
    # 6. 保存价格数据
    save_price_data(prices)
    
    # 7. 显示历史价格
    display_price_history(limit=10)
    
    # 8. 显示告警历史
    display_alert_history(limit=10)
    
    # 9. 显示价格趋势图表
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}📊 价格趋势分析{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    draw_all_charts(hours=24)
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ 追踪完成{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")


# ============ 程序入口 ============
if __name__ == "__main__":
    main()
