# src/processors/daily_summary_generator.py
"""
每日综合洞察生成器 V1.0
为竞争对手动态和行业新闻生成综合总结
"""

import os
from typing import Dict, List
from openai import OpenAI


class DailySummaryGenerator:
    """
    生成每日综合洞察
    - 竞争对手威胁总结
    - 行业趋势总结
    """

    def __init__(self, api_key: str = None):
        """
        初始化生成器

        Args:
            api_key: OpenAI API Key
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("需要设置 OPENAI_API_KEY")

        self.client = OpenAI(api_key=self.api_key)

    def generate_competitor_summary(self, items: List[Dict]) -> str:
        """
        综合所有竞争对手新闻，生成威胁总结

        Args:
            items: 竞争对手相关新闻列表

        Returns:
            100-150字中文总结
        """
        if not items:
            return "今日暂无竞争对手相关动态。"

        # 准备输入数据
        news_data = []
        for item in items[:10]:  # 限制最多10条
            news_data.append({
                "title": item.get("title", "")[:100],
                "summary": item.get("ai_summary", ""),
                "threat_level": item.get("threat_level", ""),
                "impact_areas": item.get("impact_areas", []),
                "companies": item.get("mentioned_companies", [])
            })

        prompt = f"""你是一位稳定币行业分析师，请根据以下今日竞争对手相关新闻，生成一段综合洞察。

今日竞争对手新闻（共{len(items)}条）：
{self._format_news_for_prompt(news_data)}

请生成100-150字的中文总结，要求：
1. 指出今日最大的竞争威胁是什么
2. 提及哪些公司有重要动态
3. 给出简要的应对建议方向

直接输出总结内容，不要加任何前缀或标题。语气专业、简洁。"""

        return self._call_ai(prompt)

    def generate_industry_summary(self, items: List[Dict]) -> str:
        """
        综合所有行业新闻，生成趋势总结

        Args:
            items: 行业相关新闻列表

        Returns:
            100-150字中文总结
        """
        if not items:
            return "今日暂无重要行业进展。"

        # 准备输入数据
        news_data = []
        for item in items[:10]:  # 限制最多10条
            news_data.append({
                "title": item.get("title", "")[:100],
                "summary": item.get("ai_summary", "")
            })

        prompt = f"""你是一位稳定币行业分析师，请根据以下今日行业新闻，生成一段综合洞察。

今日行业新闻（共{len(items)}条）：
{self._format_news_for_prompt(news_data)}

请生成100-150字的中文总结，要求：
1. 指出今日主要的行业热点
2. 分析值得关注的趋势或信号
3. 对稳定币托管/支付基础设施行业的潜在影响

直接输出总结内容，不要加任何前缀或标题。语气专业、简洁。"""

        return self._call_ai(prompt)

    def generate_daily_insights(self, data: Dict) -> Dict[str, str]:
        """
        生成完整的每日洞察

        Args:
            data: 分类后的数据 {"competitors": [...], "clients": [...], "industry": [...]}

        Returns:
            {
                "competitor_summary": "竞争对手威胁总结",
                "industry_summary": "行业趋势总结"
            }
        """
        competitors = data.get("competitors", [])
        industry = data.get("industry", [])

        print("  📝 生成竞争对手威胁总结...")
        competitor_summary = self.generate_competitor_summary(competitors)

        print("  📝 生成行业趋势总结...")
        industry_summary = self.generate_industry_summary(industry)

        return {
            "competitor_summary": competitor_summary,
            "industry_summary": industry_summary
        }

    def _format_news_for_prompt(self, news_data: List[Dict]) -> str:
        """格式化新闻数据为提示词输入"""
        lines = []
        for i, item in enumerate(news_data, 1):
            line = f"{i}. {item.get('title', '')}"
            if item.get('summary'):
                line += f"\n   摘要: {item['summary']}"
            if item.get('threat_level'):
                line += f"\n   威胁等级: {item['threat_level']}"
            if item.get('companies'):
                line += f"\n   涉及公司: {', '.join(item['companies'])}"
            lines.append(line)
        return "\n".join(lines)

    def _call_ai(self, prompt: str) -> str:
        """调用 AI 生成内容"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  ⚠️ AI 生成失败: {e}")
            return "AI 总结生成失败，请查看详细新闻列表。"


# 测试
if __name__ == "__main__":
    # 测试数据
    test_data = {
        "competitors": [
            {
                "title": "Fireblocks launches new MPC custody solution",
                "ai_summary": "Fireblocks 推出新一代 MPC 托管方案，支持更多链",
                "threat_level": "high",
                "impact_areas": ["产品竞争", "技术差距"],
                "mentioned_companies": ["Fireblocks"]
            },
            {
                "title": "BitGo expands to Asia Pacific",
                "ai_summary": "BitGo 宣布扩展亚太业务，新设新加坡办公室",
                "threat_level": "medium",
                "impact_areas": ["客户争夺"],
                "mentioned_companies": ["BitGo"]
            }
        ],
        "industry": [
            {
                "title": "EU MiCA stablecoin rules take effect",
                "ai_summary": "欧盟 MiCA 稳定币规则正式生效，要求发行商获得授权"
            },
            {
                "title": "USDC market cap hits new high",
                "ai_summary": "USDC 市值创新高，机构需求增长"
            }
        ]
    }

    generator = DailySummaryGenerator()
    insights = generator.generate_daily_insights(test_data)

    print("\n" + "=" * 50)
    print("竞争对手威胁总结:")
    print(insights["competitor_summary"])
    print("\n行业趋势总结:")
    print(insights["industry_summary"])
