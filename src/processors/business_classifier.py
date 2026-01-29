# src/processors/business_classifier.py
"""
商业智能分类器 V1.1
将新闻/推文分为三类：竞争对手、客户进展、行业进展
支持新配置结构：competitors.tier_0/tier_1, customers.layer_a, industry_topics
"""

import os
import json
from typing import Dict, List, Optional
from openai import OpenAI


class BusinessClassifier:
    """
    基于 AI 的商业智能分类器
    分类维度：competitors（竞争对手）、clients（客户进展）、industry（行业进展）
    """

    def __init__(self, api_key: str = None, config_path: str = None):
        """
        初始化分类器

        Args:
            api_key: OpenAI API Key
            config_path: 关键词配置文件路径
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("需要设置 OPENAI_API_KEY")

        self.client = OpenAI(api_key=self.api_key)

        # 加载配置
        self.config = self._load_config(config_path)

        # 构建关键词映射
        self._build_keyword_maps()

    def _load_config(self, config_path: str = None) -> Dict:
        """加载关键词配置"""
        if config_path is None:
            # 默认路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(base_dir, 'config', 'keywords.json')

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 默认配置
        return {
            "competitors": {
                "tier_0_custody": [
                    {"name": "Fireblocks", "twitter": "FireblocksHQ"},
                    {"name": "BitGo", "twitter": "BitGo"}
                ],
                "tier_1_payment_infra": [
                    {"name": "OSL", "twitter": "OSL_exchange"}
                ]
            },
            "customers": {
                "layer_a": [
                    {"name": "Vantage", "twitter": "VantageMarkets"}
                ],
                "context_keywords": ["stablecoin", "custody"]
            }
        }

    def _build_keyword_maps(self):
        """构建关键词到分类的映射，支持新配置结构 V1.1"""
        self.competitor_keywords = set()
        self.competitor_names = []
        self.client_keywords = set()
        self.client_names = []
        self.industry_keywords = set()

        # ========== 竞争对手 (新结构) ==========
        competitors = self.config.get("competitors", {})

        # 新结构：tier_0_custody + tier_1_payment_infra
        for tier in ['tier_0_custody', 'tier_1_payment_infra']:
            for company in competitors.get(tier, []):
                name = company.get("name", "")
                if name:
                    self.competitor_names.append(name)
                    self.competitor_keywords.add(name.lower())

        # 兼容旧结构：categories.competitors.companies
        old_categories = self.config.get("categories", {})
        for company in old_categories.get("competitors", {}).get("companies", []):
            name = company.get("name", "")
            if name and name not in self.competitor_names:
                self.competitor_names.append(name)
            for kw in company.get("keywords", []):
                self.competitor_keywords.add(kw.lower())

        # ========== 客户 (新结构) ==========
        customers = self.config.get("customers", {})

        # 新结构：layer_a
        for company in customers.get("layer_a", []):
            name = company.get("name", "")
            if name:
                self.client_names.append(name)
                self.client_keywords.add(name.lower())

        # 客户上下文关键词
        for kw in customers.get("context_keywords", []):
            self.client_keywords.add(kw.lower())

        # 兼容旧结构：categories.clients.companies
        for company in old_categories.get("clients", {}).get("companies", []):
            name = company.get("name", "")
            if name and name not in self.client_names:
                self.client_names.append(name)
            for kw in company.get("keywords", []):
                self.client_keywords.add(kw.lower())

        # ========== 行业话题 (新结构) ==========
        industry_topics = self.config.get("industry_topics", {})

        # 新结构：industry_topics with keywords_any + keywords_context
        for topic_key, topic_config in industry_topics.items():
            for kw in topic_config.get("keywords_any", []):
                self.industry_keywords.add(kw.lower())
            for kw in topic_config.get("keywords_context", []):
                self.industry_keywords.add(kw.lower())

        # 兼容旧结构：categories.industry.topics
        for topic in old_categories.get("industry", {}).get("topics", []):
            for kw in topic.get("keywords", []):
                self.industry_keywords.add(kw.lower())

    def _get_competitor_description(self) -> str:
        """从配置动态生成竞争对手描述"""
        if self.competitor_names:
            return "、".join(self.competitor_names[:8])
        return "Fireblocks、BitGo、Copper、Anchorage 等托管/支付基础设施公司"

    def _get_client_description(self) -> str:
        """从配置动态生成客户描述"""
        if self.client_names:
            return "、".join(self.client_names[:8])
        return "Vantage、WEEX、Bitunix、Antalpha 等交易所/金融机构"

    def _quick_classify(self, text: str) -> Optional[str]:
        """
        基于关键词的快速分类（节省 API 调用）

        Returns:
            分类结果或 None（需要 AI 判断）
        """
        text_lower = text.lower()

        # 检查竞争对手关键词（精确匹配公司名）
        competitor_matches = sum(1 for kw in self.competitor_keywords if kw in text_lower)

        # 检查客户关键词
        client_matches = sum(1 for kw in self.client_keywords if kw in text_lower)

        # 竞争对手优先：如果提到竞争对手公司，优先归类为竞争对手动态
        # 例如 "Fireblocks powers Papaya Global" 应该是竞争对手动态而非客户动态
        if competitor_matches > 0:
            return "competitors"

        # 如果只匹配客户
        if client_matches > 0:
            return "clients"

        return None  # 需要 AI 判断

    def classify(self, item: Dict, use_ai: bool = True) -> Dict:
        """
        对单条内容进行分类

        Args:
            item: 包含 title 和 description/text 的字典
            use_ai: 是否使用 AI（False 则只用关键词匹配）

        Returns:
            {
                "category": "competitors" | "clients" | "industry",
                "category_cn": "竞争对手" | "客户进展" | "行业进展",
                "confidence": 0.0-1.0,
                "mentioned_companies": ["Circle", "Visa"],
                "importance": 1-10,
                "summary": "简短摘要"
            }
        """
        title = item.get('title', '')
        description = item.get('description', item.get('text', ''))
        content = f"{title} {description}"

        # 尝试快速分类
        quick_result = self._quick_classify(content)
        if quick_result and not use_ai:
            return self._build_result(quick_result, content, confidence=0.7)

        # AI 分类
        if use_ai:
            return self._ai_classify(title, description)

        # 默认归为行业进展
        return self._build_result("industry", content, confidence=0.5)

    def _ai_classify(self, title: str, description: str) -> Dict:
        """使用 AI 进行分类，动态生成提示词"""

        # 动态生成公司列表
        competitor_desc = self._get_competitor_description()
        client_desc = self._get_client_description()

        prompt = f"""分析以下稳定币/加密货币行业新闻，进行分类。

标题: {title}
内容: {description[:500]}

请分类到以下三个类别之一：
1. competitors（竞争对手）- 关于 {competitor_desc} 等托管/支付基础设施公司的动态。注意：如果新闻主角是这些竞争对手公司（即使他们在服务其他公司），都应该归类为 competitors。
2. clients（客户进展）- 关于 {client_desc} 等交易所/金融机构采用稳定币、托管服务的动态。仅当新闻主角是客户公司且不涉及竞争对手时才归类为 clients。
3. industry（行业进展）- 关于监管政策、市场趋势、融资事件、技术发展等行业整体动态

请以 JSON 格式回复。

如果是 competitors 类别，请额外分析对我们（一家提供稳定币托管和支付基础设施的公司）的影响：

{{
    "category": "competitors/clients/industry",
    "confidence": 0.0-1.0,
    "mentioned_companies": ["公司名"],
    "importance": 1-10,
    "summary": "一句话摘要（中文）",

    // 仅 competitors 类别需要以下字段：
    "threat_level": "high/medium/low",
    "impact_areas": ["产品竞争", "客户争夺", "市场定价", "技术差距", "合规优势", "品牌影响"],
    "suggested_action": "具体应对建议（中文，一句话）"
}}

注意：
- threat_level: high=直接威胁核心业务, medium=间接影响, low=需关注但影响有限
- impact_areas: 从列表中选择1-3个最相关的
- 如果不是 competitors 类别，不需要 threat_level/impact_areas/suggested_action 字段"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )

            result_text = response.choices[0].message.content.strip()

            # 解析 JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]

            result = json.loads(result_text)

            # 添加中文分类名
            category_map = {
                "competitors": "竞争对手",
                "clients": "客户进展",
                "industry": "行业进展"
            }
            result["category_cn"] = category_map.get(result["category"], "行业进展")

            return result

        except Exception as e:
            print(f"  ⚠️ AI 分类失败: {e}")
            return self._build_result("industry", f"{title} {description}", confidence=0.5)

    def _build_result(self, category: str, content: str, confidence: float) -> Dict:
        """构建分类结果"""
        # 查找提到的公司
        content_lower = content.lower()
        mentioned = []

        for name in self.competitor_names + self.client_names:
            if name.lower() in content_lower:
                mentioned.append(name)

        category_map = {
            "competitors": "竞争对手",
            "clients": "客户进展",
            "industry": "行业进展"
        }

        return {
            "category": category,
            "category_cn": category_map.get(category, "行业进展"),
            "confidence": confidence,
            "mentioned_companies": mentioned,
            "importance": 5,
            "summary": "",
            # 竞争对手影响分析字段（默认值）
            "threat_level": "",
            "impact_areas": [],
            "suggested_action": ""
        }

    def classify_batch(self, items: List[Dict], use_ai: bool = True) -> Dict[str, List[Dict]]:
        """
        批量分类

        Args:
            items: 内容列表
            use_ai: 是否使用 AI

        Returns:
            {
                "competitors": [...],
                "clients": [...],
                "industry": [...]
            }
        """
        results = {
            "competitors": [],
            "clients": [],
            "industry": []
        }

        print(f"\n🧠 商业智能分类: 处理 {len(items)} 条内容...")

        for i, item in enumerate(items, 1):
            title = item.get('title', '')[:40]
            print(f"  [{i}/{len(items)}] {title}...", end=" ")

            classification = self.classify(item, use_ai=use_ai)

            # 合并分类结果到原始数据
            item.update({
                "business_category": classification.get("category", "industry"),
                "business_category_cn": classification.get("category_cn", "行业进展"),
                "ai_confidence": classification.get("confidence", 0.5),
                "mentioned_companies": classification.get("mentioned_companies", []),
                "importance_score": classification.get("importance", 5),
                "ai_summary": classification.get("summary", ""),
                # 竞争对手影响分析
                "threat_level": classification.get("threat_level", ""),
                "impact_areas": classification.get("impact_areas", []),
                "suggested_action": classification.get("suggested_action", "")
            })

            category = classification.get("category", "industry")
            results[category].append(item)

            # 显示分类结果，竞争对手显示威胁等级
            category_cn = classification.get("category_cn", "行业进展")
            if category == "competitors" and classification.get("threat_level"):
                threat_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(classification.get("threat_level", ""), "⚪")
                print(f"✓ {category_cn} {threat_icon}")
            else:
                print(f"✓ {category_cn}")

        print(f"\n📊 分类统计:")
        print(f"   竞争对手: {len(results['competitors'])} 条")
        print(f"   客户进展: {len(results['clients'])} 条")
        print(f"   行业进展: {len(results['industry'])} 条")

        return results


# 测试
if __name__ == "__main__":
    classifier = BusinessClassifier()

    print("📋 配置加载测试:")
    print(f"   竞争对手: {classifier.competitor_names}")
    print(f"   客户: {classifier.client_names}")

    test_items = [
        {"title": "Fireblocks announces new MPC custody solution", "description": "Fireblocks launches institutional custody"},
        {"title": "WEEX expands stablecoin trading", "description": "WEEX adds USDC trading pairs"},
        {"title": "EU finalizes MiCA stablecoin rules", "description": "New regulations for stablecoins in Europe"}
    ]

    results = classifier.classify_batch(test_items)
    print(json.dumps(results, indent=2, ensure_ascii=False))
