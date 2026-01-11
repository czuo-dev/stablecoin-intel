# Telegram通知模块
# 功能：发送消息到Telegram

import requests
import os
from pathlib import Path

# =========================
# 加载 .env 文件
# =========================

def load_env_file():
    """从 .env 文件加载环境变量"""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                # 解析 KEY=VALUE 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # 如果环境变量未设置，则使用 .env 中的值
                    if key and not os.getenv(key):
                        os.environ[key] = value

# 加载 .env 文件
load_env_file()

# =========================
# 配置
# =========================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# =========================
# 发送消息函数
# =========================

def send_message(text, parse_mode="Markdown"):
    """
    发送Telegram消息
    
    参数:
        text: 消息内容
        parse_mode: 格式（Markdown 或 HTML）
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 未配置Telegram Bot Token或Chat ID")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": parse_mode
    }
    
    try:
        print("正在发送Telegram消息...")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Telegram消息发送成功！")
        return True
    
    except Exception as e:
        print(f"❌ Telegram消息发送失败: {e}")
        return False

def send_weekly_summary(report_file):
    """
    发送周报摘要到Telegram
    
    参数:
        report_file: 周报文件路径
    """
    try:
        # 读取周报
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取前20行作为摘要
        lines = content.split('\n')[:20]
        summary = '\n'.join(lines)
        
        # Telegram消息长度限制为4096字符
        if len(summary) > 4000:
            summary = summary[:4000] + "...\n\n📧 完整报告已发送至邮箱"
        
        # 发送消息
        message = f"📊 **稳定币情报周报更新**\n\n{summary}"
        return send_message(message)
    
    except Exception as e:
        print(f"❌ 读取周报失败: {e}")
        return False

def send_alert(title, message):
    """
    发送紧急提醒
    
    参数:
        title: 标题
        message: 消息内容
    """
    text = f"🚨 **{title}**\n\n{message}"
    return send_message(text)

def test_telegram():
    """测试Telegram通知"""
    message = """
🤖 **稳定币情报系统测试**

这是一条测试消息。

如果您看到这条消息，说明Telegram通知功能已配置成功！

---
_稳定币情报系统_
    """
    return send_message(message)

# =========================
# 主程序
# =========================

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python telegram_notifier.py test                # 测试")
        print("  python telegram_notifier.py report <文件路径>    # 发送周报")
        print("  python telegram_notifier.py alert <标题> <消息> # 发送提醒")
        return
    
    command = sys.argv[1]
    
    if command == "test":
        test_telegram()
    
    elif command == "report" and len(sys.argv) == 3:
        report_file = sys.argv[2]
        if os.path.exists(report_file):
            send_weekly_summary(report_file)
        else:
            print(f"❌ 文件不存在: {report_file}")
    
    elif command == "alert" and len(sys.argv) >= 4:
        title = sys.argv[2]
        message = ' '.join(sys.argv[3:])
        send_alert(title, message)
    
    else:
        print("❌ 无效的命令")

if __name__ == "__main__":
    main()