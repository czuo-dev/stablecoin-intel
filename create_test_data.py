# create_test_data.py

"""
创建本周的测试数据
"""

import json
import os
from datetime import datetime, timedelta

print("📝 创建本周测试数据\n")

# 测试数据模板
test_data = {
    "policy": [
        {
            "title": "香港金管局向Circle发放首个稳定币牌照",
            "description": "HKMA宣布Circle成为首家获得稳定币发行牌照的公司",
            "source": {"name": "Bloomberg"},
            "publishedAt": "2026-01-15T10:00:00Z",
            "url": "https://example.com/1"
        },
        {
            "title": "新加坡MAS更新稳定币监管框架",
            "description": "MAS发布更新的稳定币发行指南",
            "source": {"name": "Reuters"},
            "publishedAt": "2026-01-14T14:30:00Z",
            "url": "https://example.com/2"
        }
    ],
    "company": [
        {
            "title": "PayPal扩展PYUSD到欧洲五国",
            "description": "PayPal宣布在德国、法国等国推出PYUSD",
            "source": {"name": "TechCrunch"},
            "publishedAt": "2026-01-15T12:00:00Z",
            "url": "https://example.com/3"
        },
        {
            "title": "Visa推出基于USDC的跨境支付",
            "description": "Visa与Circle合作推出新支付解决方案",
            "source": {"name": "CoinDesk"},
            "publishedAt": "2026-01-13T16:45:00Z",
            "url": "https://example.com/4"
        }
    ],
    "funding": [
        {
            "title": "Bridge完成5000万美元B轮融资",
            "description": "由Sequoia领投的稳定币基础设施融资",
            "source": {"name": "The Block"},
            "publishedAt": "2026-01-12T09:00:00Z",
            "url": "https://example.com/5"
        }
    ]
}

# 创建本周7天的数据
os.makedirs('data/processed', exist_ok=True)

today = datetime.now()
dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

for date in dates:
    filename = f'data/processed/categorized_news_{date}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 已创建: {filename}")

print("\n🎉 测试数据创建完成！")
print("现在可以运行: python3 scripts/weekly_job.py")