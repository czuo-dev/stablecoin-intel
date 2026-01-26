# src/processors/business_classifier.py
"""
商业智能分类器
将新闻/推文分为三类：竞争对手、客户进展、行业进展
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
            "categories": {
                "competitors": {
                    "companies": [
                        {"name": "Circle", "keywords": ["Circle", "USDC"]},
                        {"name": "Tether", "keywords": ["Tether", "USDT"]},
                        {"name": "Paxos", "keywords": ["Paxos", "USDP"]},
                        {"name": "PayPal", "keywords": ["PayPal", "PYUSD"]}
                    ]
                },
                "clients": {
                    "companies": [
                        {"name": "Visa", "keywords": ["Visa stablecoin"]},
                        {"name": "Mastercard", "keywords": ["Mastercard stablecoin"]},
                        {"name": "Stripe", "keywords": ["Stripe stablecoin"]}
                    ]
                },
                "industry": {
                    "topics": [
                        {"name": "监管政策", "keywords": ["regulation", "MiCA", "stablecoin bill"]},
                        {"name": "市场动态", "keywords": ["market cap", "adoption"]},
                        {"name": "融资投资", "keywords": ["funding", "investment", "raises"]}
                    ]
                }
            }
        }

    def _build_keyword_maps(self):
        """构建关键词到分类的映射"""
        self.competitor_keywords = set()
        self.competitor_names = []
        self.client_keywords = set()
        self.client_names = []
        self.industry_keywords = set()

        categories = self.config.get("categories", {})

        # 竞争对手关键词
        for company in categories.get("competitors", {}).get("companies", []):
            self.competitor_names.append(company["name"])
            for kw in company.get("keywords", []):
                self.competitor_keywords.add(kw.lower())

        # 客户关键词
        for company in categories.get("clients", {}).get("companies", []):
            self.client_names.append(company["name"])
            for kw in company.get("keywords", []):
                self.client_keywords.add(kw.lower())

        # 行业关键词
        for topic in categories.get("industry", {}).get("topics", []):
            for kw in topic.get("keywords", []):
                self.industry_keywords.add(kw.lower())

    def _quick_classify(self, text: str) -> Optional[str]:
        """
        基于关键词的快速分类（节省 API 调用）

        Returns:
            分类结果或 None（需要 AI 判断）
        """
        text_lower = text.lower()

        # 检查竞争对手关键词
        competitor_matches = sum(1 for kw in self.competitor_keywords if kw in text_lower)

        # 检查客户关键词
        client_matches = sum(1 for kw in self.client_keywords if kw in text_lower)

        # 如果明确匹配，直接返回
        if competitor_matches > 0 and client_matches == 0:
            return "competitors"
        if client_matches > 0 and competitor_matches == 0:
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
        """使用 AI 进行分类"""
        prompt = f"""分析以下稳定币行业新闻，进行分类。

标题: {title}
内容: {description[:500]}

请分类到以下三个类别之一：
1. competitors（竞争对手）- 关于 Circle/USDC、Tether/USDT、Paxos、PayPal/PYUSD 等稳定币发行商的动态
2. clients（客户进展）- 关于 Visa、Mastercard、Stripe、JPMorgan 等金融机构采用稳定币的动态
3. industry（行业进展）- 关于监管政策、市场趋势、融资事件等行业整体动态

请以 JSON 格式回复：
{{
    "category": "competitors/clients/industry",
    "confidence": 0.0-1.0,
    "mentioned_companies": ["公司名"],
    "importance": 1-10,
    "summary": "一句话摘要（中文）"
}}"""

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
            "summary": ""
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
                "business_category": classification["category"],
                "business_category_cn": classification["category_cn"],
                "ai_confidence": classification["confidence"],
                "mentioned_companies": classification["mentioned_companies"],
                "importance_score": classification["importance"],
                "ai_summary": classification.get("summary", "")
            })

            category = classification["category"]
            results[category].append(item)
            print(f"✓ {classification['category_cn']}")

        print(f"\n📊 分类统计:")
        print(f"   竞争对手: {len(results['competitors'])} 条")
        print(f"   客户进展: {len(results['clients'])} 条")
        print(f"   行业进展: {len(results['industry'])} 条")

        return results


# 测试
if __name__ == "__main__":
    classifier = BusinessClassifier()

    test_items = [
        {"title": "Circle announces new USDC features", "description": "Circle launches cross-chain USDC"},
        {"title": "Visa expands stablecoin settlement", "description": "Visa partners with Circle for USDC settlement"},
        {"title": "EU finalizes MiCA stablecoin rules", "description": "New regulations for stablecoins in Europe"}
    ]

    results = classifier.classify_batch(test_items)
    print(json.dumps(results, indent=2, ensure_ascii=False))
