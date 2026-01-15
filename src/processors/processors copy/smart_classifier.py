# src/processors/smart_classifier.py

import openai
import json
from typing import Dict, List, Optional


class SmartClassifier:
    """AI智能分类器 - 使用GPT进行新闻分类和标签生成"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        
        # 分类示例（Few-shot learning）
        self.examples = [
            {
                "title": "PayPal在德国和法国推出PYUSD稳定币",
                "description": "PayPal宣布将其稳定币PYUSD扩展到欧洲市场，首先在德国和法国推出。",
                "category": "company",
                "tags": ["PayPal", "PYUSD", "欧洲市场", "产品发布", "市场扩张"],
                "reasoning": "主要报道PayPal的产品扩张动态"
            },
            {
                "title": "香港金管局向Circle发放首个稳定币发行牌照",
                "description": "HKMA宣布Circle成为首家获得稳定币发行牌照的公司。",
                "category": "policy",
                "tags": ["Circle", "香港", "HKMA", "监管牌照", "合规"],
                "reasoning": "涉及监管机构发放牌照，属于政策监管类"
            },
            {
                "title": "稳定币基础设施公司Bridge获5000万美元B轮融资",
                "description": "由Sequoia Capital领投，Bridge计划用资金扩展全球业务。",
                "category": "funding",
                "tags": ["Bridge", "融资", "SeriesB", "Sequoia", "5000万美元"],
                "reasoning": "报道公司融资事件"
            }
        ]
    
    def classify_article(self, article: Dict) -> Dict:
        """
        使用AI对单篇文章进行分类
        
        Args:
            article: {"title": "...", "description": "..."}
            
        Returns:
            {
                "primary_category": "policy",
                "confidence": 0.95,
                "tags": ["香港", "监管", "牌照"],
                "reasoning": "文章讨论监管牌照发放",
                "importance": 8.5
            }
        """
        
        # 准备Few-shot示例
        examples_text = ""
        for i, ex in enumerate(self.examples, 1):
            examples_text += f"""
【示例{i}】
标题: {ex['title']}
内容: {ex['description']}
分类: {ex['category']}
标签: {', '.join(ex['tags'])}
理由: {ex['reasoning']}
"""
        
        prompt = f"""你是稳定币行业的新闻分类专家。参考以下示例，对新文章进行分类。

{examples_text}

【分类规则】
- policy: 监管政策、法规、政府态度、牌照发放
- company: 公司产品、战略合作、市场动态、技术升级
- funding: 融资、投资、并购、财务报表

【待分类文章】
标题: {article.get('title', 'N/A')}
内容: {article.get('description', 'N/A')}

【输出要求】
以JSON格式输出，包含：
{{
    "primary_category": "policy/company/funding之一",
    "confidence": 0.0-1.0之间的数字,
    "tags": ["标签1", "标签2", "标签3", "标签4", "标签5"],
    "reasoning": "50字以内的分类理由",
    "importance": 1-10之间的数字，评估新闻重要性
}}

注意：
1. tags必须包含3-5个关键标签
2. 标签可以是公司名、地区、事件类型、产品名等
3. importance评分考虑：行业影响、涉及金额、监管重要性
4. 只输出JSON，不要其他解释
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的新闻分类专家，只输出JSON格式结果。"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=300,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # 验证结果格式
            if not all(k in result for k in ["primary_category", "confidence", "tags"]):
                raise ValueError("返回格式不完整")
            
            # 确保tags是列表
            if isinstance(result.get("tags"), str):
                result["tags"] = [tag.strip() for tag in result["tags"].split(",")]
            
            # 确保confidence在0-1之间
            result["confidence"] = max(0.0, min(1.0, float(result.get("confidence", 0.5))))
            
            # 确保importance在1-10之间
            result["importance"] = max(1, min(10, int(result.get("importance", 5))))
            
            return result
            
        except Exception as e:
            print(f"❌ 分类失败: {e}")
            # 返回默认分类
            return {
                "primary_category": "company",
                "confidence": 0.5,
                "tags": ["未分类"],
                "reasoning": "AI分类失败，使用默认值",
                "importance": 5
            }
    
    def batch_classify(self, articles: List[Dict], max_batch_size: int = 5) -> List[Dict]:
        """
        批量分类文章（节省成本）
        
        Args:
            articles: 文章列表
            max_batch_size: 每批最多处理的文章数
            
        Returns:
            分类结果列表
        """
        
        results = []
        
        # 分批处理
        for i in range(0, len(articles), max_batch_size):
            batch = articles[i:i + max_batch_size]
            print(f"处理批次 {i//max_batch_size + 1}: {len(batch)} 篇文章...")
            
            # 准备批量文章文本
            articles_text = ""
            for j, article in enumerate(batch, 1):
                articles_text += f"""
【文章{j}】
标题: {article.get('title', 'N/A')}
内容: {article.get('description', 'N/A')}
"""
            
            # Few-shot示例
            examples_text = ""
            for ex in self.examples[:2]:  # 只用前2个示例节省token
                examples_text += f"""
示例:
标题: {ex['title']}
分类: {ex['category']}
标签: {', '.join(ex['tags'][:3])}
"""
            
            prompt = f"""你是新闻分类专家。参考示例，对以下{len(batch)}篇文章分类。

{examples_text}

{articles_text}

输出JSON数组，格式：
[
    {{
        "article_index": 1,
        "primary_category": "policy/company/funding",
        "confidence": 0.0-1.0,
        "tags": ["标签1", "标签2", "标签3"],
        "importance": 1-10
    }},
    ...
]

只输出JSON数组，不要其他内容。
"""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是专业的新闻分类专家。"},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=800,
                    temperature=0.3
                )
                
                content = response.choices[0].message.content
                
                # 尝试解析JSON
                try:
                    # 如果返回的是对象包含数组
                    parsed = json.loads(content)
                    if "results" in parsed:
                        batch_results = parsed["results"]
                    elif "classifications" in parsed:
                        batch_results = parsed["classifications"]
                    elif isinstance(parsed, list):
                        batch_results = parsed
                    else:
                        # 可能是包含数组的对象，取第一个数组值
                        batch_results = list(parsed.values())[0] if parsed else []
                except:
                    batch_results = []
                
                # 合并结果
                for j, article in enumerate(batch):
                    if j < len(batch_results):
                        result = batch_results[j]
                        result["article"] = article
                        results.append(result)
                    else:
                        # 如果批量分类失败，使用单个分类
                        result = self.classify_article(article)
                        result["article"] = article
                        results.append(result)
                        
            except Exception as e:
                print(f"⚠️  批量分类失败，使用单个分类: {e}")
                # 失败时使用单个分类
                for article in batch:
                    result = self.classify_article(article)
                    result["article"] = article
                    results.append(result)
        
        return results
    
    def compare_with_keyword_classifier(
        self, 
        article: Dict, 
        keyword_result: str
    ) -> Dict:
        """
        对比AI分类和关键词分类的结果
        
        Args:
            article: 文章内容
            keyword_result: 关键词分类的结果（"policy"/"company"/"funding"）
            
        Returns:
            对比分析
        """
        
        ai_result = self.classify_article(article)
        
        return {
            "article_title": article.get("title", "")[:50],
            "keyword_classification": keyword_result,
            "ai_classification": ai_result["primary_category"],
            "match": keyword_result == ai_result["primary_category"],
            "ai_confidence": ai_result["confidence"],
            "ai_tags": ai_result["tags"],
            "ai_reasoning": ai_result.get("reasoning", "")
        }