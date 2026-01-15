# src/processors/prompt_templates.py

class PromptTemplates:
    """
    不同场景的Prompt模板库
    """
    
    # 基础版（当前使用）
    BASIC_SUMMARY = """
请总结以下新闻：
{articles_text}
"""
    
    # 改进版（添加角色和格式）
    IMPROVED_SUMMARY = """
你是稳定币行业资深分析师，拥有5年监管和市场研究经验。

请分析以下{count}条新闻，提供专业洞察：

{articles_text}

输出格式：
1. 【核心事件】（一句话概括）
2. 【深度分析】（影响和意义）
3. 【行动建议】（从业者应关注什么）
"""
    
    # 专家版 - 政策分析
    POLICY_EXPERT = """
你是全球稳定币监管政策专家，跟踪美国、欧盟、亚洲市场政策动态。

【分析任务】
阅读以下{count}条政策新闻，识别监管趋势。

{articles_text}

【输出要求】
1. 政策分类
   - 🔴 限制性政策（禁令、严格监管）
   - 🟡 中性政策（观察、研究）
   - 🟢 支持性政策（试点、许可）

2. 关键信息提取
   - 涉及国家/地区：
   - 监管机构：
   - 生效时间：
   - 核心要求：

3. 影响评估
   - 对本地市场影响：【高/中/低】
   - 对全球市场溢出：【有/无】

4. 行动建议（50字内）

不要编造信息，如果某项信息缺失，标注"未提及"。
"""
    
    # 专家版 - 公司动态
    COMPANY_EXPERT = """
你是稳定币企业战略分析师，擅长解读大公司布局。

【分析任务】
评估以下{count}条公司动态的战略意义。

{articles_text}

【输出框架】
1. 事件类型
   - 产品发布 / 战略合作 / 市场扩张 / 技术升级

2. 竞争分析
   - 涉及公司：
   - 市场地位：
   - 竞争对手反应：

3. 战略意图（推测）
   为什么现在做这个决定？背后的商业逻辑是什么？

4. 启示
   对同行业公司有何借鉴意义？
"""
    
    # 专家版 - 融资分析
    FUNDING_EXPERT = """
你是加密货币投资分析师，熟悉VC生态和融资趋势。

【分析任务】
解读以下{count}条融资新闻，识别行业热点。

{articles_text}

【输出内容】
1. 融资概况表格

2. 投资者画像
   - 传统VC vs 加密原生VC
   - 战略投资者（Visa/PayPal等）占比
   - 地域分布（美国/亚洲/欧洲）

3. 赛道分析
   这轮融资主要集中在哪些细分领域？

4. 估值合理性
   当前估值水平的判断
"""

    @staticmethod
    def get_prompt(category: str, articles_text: str, count: int, level: str = "expert") -> str:
        """
        根据类别返回对应的prompt
        
        Args:
            category: 类别（policy/company/funding）
            articles_text: 文章内容
            count: 文章数量
            level: prompt级别（basic/improved/expert）
        """
        
        if level == "basic":
            return PromptTemplates.BASIC_SUMMARY.format(articles_text=articles_text)
        
        if level == "improved":
            return PromptTemplates.IMPROVED_SUMMARY.format(
                articles_text=articles_text, 
                count=count
            )
        
        # Expert level
        templates = {
            "policy": PromptTemplates.POLICY_EXPERT,
            "company": PromptTemplates.COMPANY_EXPERT,
            "funding": PromptTemplates.FUNDING_EXPERT
        }
        
        template = templates.get(category, PromptTemplates.IMPROVED_SUMMARY)
        return template.format(articles_text=articles_text, count=count)


# 测试代码
if __name__ == "__main__":
    # 测试生成prompt
    test_text = "Test article about stablecoin regulation"
    
    print("Basic Prompt:")
    print(PromptTemplates.get_prompt("policy", test_text, 1, "basic"))
    print("\n" + "="*60 + "\n")
    
    print("Expert Prompt:")
    print(PromptTemplates.get_prompt("policy", test_text, 1, "expert"))