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

    def _get_company_context(self) -> tuple:
        """从配置读取我司名称与关注地区（用于行业相关性判定）。返回 (company_name, focus_regions_list)。"""
        company = self.config.get("company", {})
        name = company.get("name", "本公司")
        regions = company.get("focus_regions", []) or []
        return (name, regions)

    def _quick_classify(self, text: str, source_account: str = None) -> Optional[str]:
        """
        基于关键词的快速分类（节省 API 调用）

        Args:
            text: 内容文本
            source_account: 来源账号（如果是 Twitter 推文）

        Returns:
            分类结果或 None（需要 AI 判断）
        """
        text_lower = text.lower()

        # 检查是否精确匹配竞争对手公司名
        competitor_name_matches = sum(1 for name in self.competitor_names if name.lower() in text_lower)

        # 检查是否精确匹配客户公司名
        client_name_matches = sum(1 for name in self.client_names if name.lower() in text_lower)

        # 如果来源是客户的 Twitter 账号，直接归类为客户动态
        if source_account:
            source_lower = source_account.lower()
            # 检查是否是客户账号
            customers = self.config.get("customers", {})
            for company in customers.get("layer_a", []):
                twitter = company.get("twitter", "").lower()
                if twitter and twitter == source_lower:
                    return "clients"
            # 检查是否是竞争对手账号
            competitors = self.config.get("competitors", {})
            for tier in ['tier_0_custody', 'tier_1_payment_infra']:
                for company in competitors.get(tier, []):
                    twitter = company.get("twitter", "").lower()
                    if twitter and twitter == source_lower:
                        return "competitors"

        # 如果同时提到客户和竞争对手，需要 AI 判断
        if competitor_name_matches > 0 and client_name_matches > 0:
            return None  # 需要 AI 判断

        # 如果只提到客户公司名（精确匹配），归类为客户动态
        if client_name_matches > 0:
            return "clients"

        # 如果只提到竞争对手公司名（精确匹配），归类为竞争对手动态
        if competitor_name_matches > 0:
            return "competitors"

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

        # 获取来源账号（Twitter 推文可能有 monitored_account 或 author_username）
        source_account = item.get('monitored_account') or item.get('author_username', '')

        # 尝试快速分类（基于来源账号或公司名精确匹配）
        quick_result = self._quick_classify(content, source_account)
        if quick_result:
            # 如果是基于来源账号判断，置信度更高
            confidence = 0.9 if source_account else 0.7
            if not use_ai:
                return self._build_result(quick_result, content, confidence=confidence)
            # 即使启用 AI，如果来源账号明确是客户/竞争对手，也优先使用快速分类
            if source_account:
                return self._build_result(quick_result, content, confidence=confidence)

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
        company_name, focus_regions = self._get_company_context()
        regions_str = "、".join(focus_regions) if focus_regions else "（无）"

        prompt = f"""分析以下新闻，判断其与 {company_name}（稳定币托管/支付业务）的相关性并分类。

标题: {title}
内容: {description[:500]}

**首先判断业务相关性（最重要）**：
- 1.0 (高度相关): 直接提到竞争对手、目标客户、稳定币托管/支付、MPC/多签技术、{regions_str}地区加密监管
- 0.7-0.9 (相关): 加密货币监管、交易所动态、区块链基础设施、跨境支付
- 0.5-0.6 (间接相关): 一般加密货币新闻、DeFi、Web3
- 0.2-0.4 (弱相关): 仅提到比特币价格、一般金融科技、科技公司动态
- 0.0-0.1 (无关): 矿业、体育、医疗、农业、一般科学研究、与加密货币无关的内容

**然后分类到以下类别**：
1. competitors（竞争对手）- 关于 {competitor_desc} 等托管/支付基础设施公司的动态
2. clients（客户进展）- 仅当明确涉及以下客户：{client_desc}
3. industry（行业进展）- 监管政策、市场趋势、融资事件、技术发展等

请以 JSON 格式回复：

{{
    "business_relevance": 0.0-1.0,
    "relevance_reason": "简述相关原因（中文，10字内）",
    "category": "competitors",
    "confidence": 0.0-1.0,
    "mentioned_companies": ["公司名"],
    "importance": 1-10,
    "summary": "一句话摘要（中文）",

    // ===== competitors 类别额外字段 =====
    "threat_level": "high/medium/low",
    "impact_areas": ["产品竞争", "客户争夺", "市场定价", "技术差距", "合规优势", "品牌影响"],
    "suggested_action": "具体应对建议（中文，一句话）",

    // ===== clients 类别额外字段 =====
    "opportunity_level": "high/medium/low",
    "opportunity_type": ["合作机会", "客户扩展", "技术需求", "合规需求", "市场拓展"],
    "client_action": "建议的跟进行动（中文，一句话）",

    // ===== industry 类别额外字段 =====
    "relevance_level": "high/medium/low",
    "impact_type": ["监管影响", "市场趋势", "技术发展", "竞争格局", "投资机会"],
    "industry_action": "需要采取的行动（中文，一句话，如无则留空）"
}}

**重要**：business_relevance 打分要严格！与加密货币/稳定币/托管完全无关的内容（如矿业股票、体育、医疗科研）应该给 0.0-0.1 分。
**category 必须且只能是以下三个值之一**：competitors、clients、industry（不要输出其它文字）。"""

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

            # 规范化 category：只允许 competitors / clients / industry
            raw_cat = (result.get("category") or "industry").strip().lower()
            if raw_cat in ("competitors", "clients", "industry"):
                result["category"] = raw_cat
            else:
                # 模型可能返回 "competitors/clients/industry" 等歧义值，归为行业进展
                result["category"] = "industry"

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
            "suggested_action": "",
            # 客户机会分析字段（默认值）
            "opportunity_level": "",
            "opportunity_type": [],
            "client_action": "",
            # 行业相关性分析字段（默认值）
            "relevance_level": "",
            "impact_type": [],
            "industry_action": ""
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
                # 业务相关性打分（用于过滤）
                "business_relevance": classification.get("business_relevance", 1.0),
                "relevance_reason": classification.get("relevance_reason", ""),
                # 竞争对手影响分析
                "threat_level": classification.get("threat_level", ""),
                "impact_areas": classification.get("impact_areas", []),
                "suggested_action": classification.get("suggested_action", ""),
                # 客户机会分析
                "opportunity_level": classification.get("opportunity_level", ""),
                "opportunity_type": classification.get("opportunity_type", []),
                "client_action": classification.get("client_action", ""),
                # 行业相关性分析
                "relevance_level": classification.get("relevance_level", ""),
                "impact_type": classification.get("impact_type", []),
                "industry_action": classification.get("industry_action", "")
            })

            category = classification.get("category", "industry")
            if category not in results:
                category = "industry"
            results[category].append(item)

            # 显示分类结果，带等级图标
            category_cn = classification.get("category_cn", "行业进展")
            level_icon = ""
            if category == "competitors" and classification.get("threat_level"):
                level_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(classification.get("threat_level", ""), "")
            elif category == "clients" and classification.get("opportunity_level"):
                level_icon = {"high": "🟢", "medium": "🟡", "low": "⚪"}.get(classification.get("opportunity_level", ""), "")
            elif category == "industry" and classification.get("relevance_level"):
                level_icon = {"high": "🔵", "medium": "🟡", "low": "⚪"}.get(classification.get("relevance_level", ""), "")

            if level_icon:
                print(f"✓ {category_cn} {level_icon}")
            else:
                print(f"✓ {category_cn}")

        print(f"\n📊 分类统计:")
        print(f"   竞争对手: {len(results['competitors'])} 条")
        print(f"   客户进展: {len(results['clients'])} 条")
        print(f"   行业进展: {len(results['industry'])} 条")

        return results

    def filter_by_relevance(self, categorized_data: Dict, min_score: float = 0.5) -> Dict:
        """
        根据 business_relevance 分数过滤低相关性内容

        Args:
            categorized_data: AI 分类后的数据 {"competitors": [...], "clients": [...], "industry": [...]}
            min_score: 最低相关性阈值（默认 0.5）

        Returns:
            过滤后的数据，结构相同
        """
        filtered = {}
        removed_count = 0
        removed_items = []

        for category in ['competitors', 'clients', 'industry']:
            items = categorized_data.get(category, [])
            kept = []
            for item in items:
                score = item.get('business_relevance', 1.0)  # 默认保留（向后兼容）
                if score >= min_score:
                    kept.append(item)
                else:
                    removed_count += 1
                    removed_items.append({
                        'title': item.get('title', '')[:50],
                        'score': score,
                        'reason': item.get('relevance_reason', 'N/A')
                    })
            filtered[category] = kept

        # 打印过滤统计
        print(f"\n🎯 业务相关性过滤 (阈值: {min_score}):")
        print(f"   移除: {removed_count} 条低相关性内容")
        if removed_items and removed_count <= 10:
            print(f"   移除的内容:")
            for item in removed_items[:10]:
                print(f"      - [{item['score']:.1f}] {item['title']}... ({item['reason']})")
        elif removed_count > 10:
            print(f"   移除的内容 (仅显示前10条):")
            for item in removed_items[:10]:
                print(f"      - [{item['score']:.1f}] {item['title']}... ({item['reason']})")

        print(f"\n📊 过滤后统计:")
        print(f"   竞争对手: {len(filtered.get('competitors', []))} 条")
        print(f"   客户进展: {len(filtered.get('clients', []))} 条")
        print(f"   行业进展: {len(filtered.get('industry', []))} 条")

        return filtered


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
