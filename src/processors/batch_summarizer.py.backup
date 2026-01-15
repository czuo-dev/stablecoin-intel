# src/processors/batch_summarizer.py

import openai
from typing import List, Dict
import json
from datetime import datetime


class BatchSummarizer:
    """批量处理新闻摘要的类"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """初始化批量摘要器"""
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.max_articles_per_batch = 10
        
    def prepare_batch(self, articles: List[Dict]) -> List[List[Dict]]:
        """将文章分批"""
        batches = []
        for i in range(0, len(articles), self.max_articles_per_batch):
            batch = articles[i:i + self.max_articles_per_batch]
            batches.append(batch)
        return batches
    
    def summarize_batch(self, articles: List[Dict], category: str = "general") -> str:
        """批量总结一组文章"""
        
        # 准备文章内容
        articles_text = ""
        for i, article in enumerate(articles):
            articles_text += f"标题: {article.get('title', 'N/A')}\n"
            articles_text += f"来源: {article.get('source', {}).get('name', 'Unknown')}\n"
            articles_text += f"日期: {article.get('publishedAt', 'N/A')}\n"
            articles_text += f"内容: {article.get('description', article.get('content', 'N/A'))}\n"
            articles_text += "-" * 50 + "\n"
        
        # 根据类别定制prompt
        category_prompts = {
            "policy": """
请关注：
- 监管政策变化（许可、合规要求）
- 政府态度转变
- 对行业的影响
""",
            "company": """
请关注：
- 产品发布或更新
- 战略合作
- 市场布局
""",
            "funding": """
请关注：
- 融资金额和轮次
- 投资方背景
- 资金用途
"""
        }
        
        prompt = f"""
你是一个专注稳定币行业的分析师。请阅读以下{len(articles)}条新闻，生成一份专业的中文摘要。

{category_prompts.get(category, "")}

【新闻内容】
{articles_text}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是稳定币行业情报分析专家"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return None
    
    def generate_daily_report(self, articles_by_category: Dict[str, List[Dict]]) -> str:
        """生成完整的每日报告"""
        
        report = f"# 稳定币行业日报 - {datetime.now().strftime('%Y年%m月%d日')}\n\n"
        report += "---\n\n"
        
        category_names = {
            "policy": "📋 政策监管",
            "company": "🏢 公司动态", 
            "funding": "💰 融资事件"
        }
        
        for category, articles in articles_by_category.items():
            if not articles:
                continue
                
            report += f"## {category_names.get(category, category)}\n\n"
            
            batches = self.prepare_batch(articles)
            
            for i, batch in enumerate(batches, 1):
                print(f"  处理 {category} 第 {i}/{len(batches)} 批...")
                summary = self.summarize_batch(batch, category)
                
                if summary:
                    report += f"### 批次 {i}\n\n"
                    report += summary + "\n\n"
        
        # 添加原文链接
        report += "\n---\n\n## 📎 原文链接\n\n"
        for category, articles in articles_by_category.items():
            if articles:
                report += f"\n**{category_names.get(category, category)}**\n"
                for article in articles[:5]:
                    report += f"- [{article['title']}]({article['url']})\n"
        
        return report
