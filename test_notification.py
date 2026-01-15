# test_notification.py

import json
import os
from src.processors.notification_formatter import NotificationFormatter

print("📧 测试通知格式化器\n")
print("="*60)

# 加载测试数据
with open('data/processed/categorized_news_2025-01-15.json', 'r') as f:
    articles_by_category = json.load(f)

simple_report = """# 稳定币行业日报 - 2025年01月15日

## 📋 政策监管

香港金管局向Circle发放首个稳定币牌照...

## 🏢 公司动态

PayPal扩展PYUSD到欧洲市场..."""

formatter = NotificationFormatter()

# 测试Slack格式
print("\n【Slack格式】")
print("-"*60)
slack_msg = formatter.format_for_slack(simple_report, articles_by_category)

os.makedirs('notifications', exist_ok=True)

with open('notifications/slack_message.json', 'w', encoding='utf-8') as f:
    json.dump(slack_msg, f, indent=2, ensure_ascii=False)

print("✅ 保存到: notifications/slack_message.json")
print(json.dumps(slack_msg, indent=2, ensure_ascii=False)[:300])

# 测试Email格式
print("\n" + "="*60)
print("\n【Email格式】")
print("-"*60)
email_msg = formatter.format_for_email(simple_report, articles_by_category)
print(f"主题: {email_msg['subject']}")

with open('notifications/email.html', 'w', encoding='utf-8') as f:
    f.write(email_msg['html_body'])

with open('notifications/email.txt', 'w', encoding='utf-8') as f:
    f.write(email_msg['plain_body'])

print("✅ 保存到: notifications/email.html")
print("\n用浏览器打开查看: open notifications/email.html")