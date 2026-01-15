# src/processors/notification_formatter.py

from typing import Dict, List
from datetime import datetime
import json


class NotificationFormatter:
    """格式化报告为不同通知渠道的格式"""
    
    @staticmethod
    def format_for_slack(daily_report: str, articles_by_category: Dict[str, List[Dict]]) -> Dict:
        """转换成Slack消息格式"""
        
        total_articles = sum(len(articles) for articles in articles_by_category.values())
        summary = daily_report[:500].replace("#", "").replace("*", "")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📰 稳定币日报 - {datetime.now().strftime('%m/%d')}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*今日共收集 {total_articles} 条新闻*\n\n{summary}..."
                }
            },
            {
                "type": "divider"
            }
        ]
        
        category_emojis = {
            "policy": "📋",
            "company": "🏢",
            "funding": "💰"
        }
        
        category_names = {
            "policy": "政策监管",
            "company": "公司动态",
            "funding": "融资事件"
        }
        
        for category, articles in articles_by_category.items():
            if articles:
                emoji = category_emojis.get(category, "📌")
                name = category_names.get(category, category)
                
                top_3 = articles[:3]
                news_list = "\n".join([f"• {a['title'][:60]}..." for a in top_3])
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{emoji} {name}* ({len(articles)}条)\n{news_list}"
                    }
                })
        
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "查看完整报告 📄"
                    },
                    "url": "https://github.com/czuo-dev/stablecoin-intel/tree/main/reports",
                    "style": "primary"
                }
            ]
        })
        
        return {
            "blocks": blocks,
            "text": f"稳定币日报 - {total_articles}条新闻"
        }
    
    @staticmethod
    def format_for_email(daily_report: str, articles_by_category: Dict[str, List[Dict]]) -> Dict:
        """转换成Email格式"""
        
        total_articles = sum(len(articles) for articles in articles_by_category.values())
        date_str = datetime.now().strftime('%Y年%m月%d日')
        
        subject = f"稳定币行业日报 - {date_str} ({total_articles}条新闻)"
        
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .category {{ background-color: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        a {{ color: #3498db; text-decoration: none; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #bdc3c7; color: #7f8c8d; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>📰 稳定币行业日报</h1>
    <p><strong>日期</strong>: {date_str} | <strong>新闻数量</strong>: {total_articles}条</p>
    
    <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
        <strong>⚡ 今日要点</strong><br>
        本报告通过AI自动收集和分析全球稳定币行业动态
    </div>
    
    {daily_report.replace('# ', '<h1>').replace('## ', '<h2>').replace('### ', '<h3>')}
    
    <div class="footer">
        <p>本报告由稳定币情报Agent自动生成</p>
        <p>GitHub: <a href="https://github.com/czuo-dev/stablecoin-intel">czuo-dev/stablecoin-intel</a></p>
    </div>
</body>
</html>"""
        
        plain_body = daily_report.replace("#", "").replace("*", "").replace("-", "•")
        
        return {
            "subject": subject,
            "html_body": html_body,
            "plain_body": plain_body
        }