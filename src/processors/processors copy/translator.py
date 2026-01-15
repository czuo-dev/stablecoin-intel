# src/processors/translator.py

import openai
from typing import Dict, Optional


class MultilingualTranslator:
    """多语言翻译器 - 专注金融科技领域"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        
        # 稳定币行业术语对照表
        self.terminology = {
            # 核心术语
            "stablecoin": {"es": "stablecoin", "en": "stablecoin"},
            "稳定币": {"es": "stablecoin", "en": "stablecoin"},
            
            # 监管术语
            "监管": {"es": "regulación", "en": "regulation"},
            "牌照": {"es": "licencia", "en": "license"},
            "合规": {"es": "cumplimiento", "en": "compliance"},
            "审计": {"es": "auditoría", "en": "audit"},
            
            # 金融术语
            "融资": {"es": "financiación", "en": "funding"},
            "发行": {"es": "emisión", "en": "issuance"},
            "储备": {"es": "reservas", "en": "reserves"},
            "赎回": {"es": "redención", "en": "redemption"},
            
            # 公司/产品（保持原文）
            "USDT": {"es": "USDT", "en": "USDT"},
            "USDC": {"es": "USDC", "en": "USDC"},
            "PYUSD": {"es": "PYUSD", "en": "PYUSD"},
            "Circle": {"es": "Circle", "en": "Circle"},
            "Tether": {"es": "Tether", "en": "Tether"},
            "PayPal": {"es": "PayPal", "en": "PayPal"},
        }
    
    def get_terminology_prompt(self, target_lang: str) -> str:
        """生成术语对照表提示"""
        terms_list = []
        for zh_term, translations in self.terminology.items():
            target_term = translations.get(target_lang, zh_term)
            terms_list.append(f"- {zh_term} → {target_term}")
        
        return "\n".join(terms_list)
    
    def translate_to_spanish(self, chinese_text: str) -> str:
        """
        将中文翻译成西班牙语
        
        Args:
            chinese_text: 中文文本（支持Markdown格式）
            
        Returns:
            西班牙语译文
        """
        
        terminology_prompt = self.get_terminology_prompt("es")
        
        prompt = f"""你是一个金融科技领域的专业翻译，精通中文和西班牙语。

请将以下中文内容翻译成西班牙语，注意：

【翻译要求】
1. 保持专业术语的准确性（参考术语表）
2. 使用金融行业的标准西班牙语表达
3. 完整保留Markdown格式（#、##、###、**、-等）
4. 保留所有emoji符号
5. 专有名词（公司名、产品名、货币代码）保持英文不翻译
6. 直接输出西班牙语译文，不要添加任何解释或前言

【术语对照表】
{terminology_prompt}

【待翻译内容】
{chinese_text}

【输出】
（直接输出西班牙语译文）
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un traductor profesional especializado en finanzas y tecnología."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.3  # 低温度保证准确性
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ 翻译失败: {e}")
            return None
    
    def translate_to_english(self, chinese_text: str) -> str:
        """将中文翻译成英文"""
        
        terminology_prompt = self.get_terminology_prompt("en")
        
        prompt = f"""You are a professional translator specializing in fintech and cryptocurrency.

Translate the following Chinese content to English:

【Translation Requirements】
1. Maintain accuracy of technical terms (refer to terminology table)
2. Use standard financial industry English
3. Preserve all Markdown formatting
4. Keep all emoji symbols
5. Keep proper nouns (company names, product names) as is
6. Output English translation only, no explanations

【Terminology Table】
{terminology_prompt}

【Content to Translate】
{chinese_text}

【Output】
(English translation only)
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional fintech translator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Translation failed: {e}")
            return None
    
    def generate_bilingual_summary(self, articles_text: str, target_lang: str = "es") -> Dict[str, str]:
        """
        一次调用生成中文和目标语言的双语摘要（省成本）
        
        Args:
            articles_text: 文章内容
            target_lang: 目标语言（"es"西班牙语 / "en"英文）
            
        Returns:
            {"zh": "中文摘要", "target": "目标语言摘要"}
        """
        
        lang_names = {"es": "西班牙语 (Español)", "en": "英文 (English)"}
        terminology_prompt = self.get_terminology_prompt(target_lang)
        
        prompt = f"""你是稳定币行业分析师。请阅读以下新闻，同时生成中文和{lang_names[target_lang]}摘要。

【新闻内容】
{articles_text}

【术语对照表】
{terminology_prompt}

【输出要求】
请严格按照以下格式输出（保留标记）：

===中文摘要===
[用中文写摘要，包含：核心要点、重要性评估、行业影响]

==={lang_names[target_lang]}摘要===
[用{lang_names[target_lang]}写摘要，内容与中文版对应]

注意：
1. 中文摘要控制在300字以内
2. {lang_names[target_lang]}摘要也要简洁
3. 专有名词保持英文
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的稳定币行业双语分析师"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            
            # 解析双语内容
            zh_summary = ""
            target_summary = ""
            
            if "===中文摘要===" in content:
                parts = content.split("===中文摘要===")
                if len(parts) > 1:
                    zh_part = parts[1].split(f"==={lang_names[target_lang]}摘要===")
                    if len(zh_part) > 1:
                        zh_summary = zh_part[0].strip()
                        target_summary = zh_part[1].strip()
            
            return {
                "zh": zh_summary or content[:len(content)//2],
                target_lang: target_summary or content[len(content)//2:]
            }
            
        except Exception as e:
            print(f"❌ 双语摘要生成失败: {e}")
            return {"zh": "", target_lang: ""}