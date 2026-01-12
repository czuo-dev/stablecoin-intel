# AI智能摘要器（使用OpenAI）
# 功能：使用GPT生成新闻摘要

from openai import OpenAI
import os
import json
from datetime import datetime

# =========================
# 配置
# =========================

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-3.5-turbo"  # 或使用 "gpt-4" 获得更好效果

# 创建客户端
client = OpenAI(api_key=API_KEY) if API_KEY else None

# =========================
# 单条新闻摘要
# =========================

def summarize_article(article, language="zh"):
    """
    为单条新闻生成智能摘要
    
    参数:
        article: 新闻字典（包含title, summary, url等）
        language: 输出语言（zh=中文, en=英文）
    
    返回:
        摘要文本
    """
    if not client:
        print("❌ OpenAI API未配置")
        return None
    
    # 准备新闻内容
    title = article.get('title', '')
    content = article.get('summary', article.get('description', ''))
    
    # 构建提示词
    if language == "zh":
        system_prompt = """你是一个专业的稳定币行业分析师。你的任务是为新闻生成简洁的中文摘要。

要求：
1. 用1-2句话概括核心内容
2. 突出关键信息（公司名、产品名、金额等）
3. 保持客观中立
4. 使用专业但易懂的语言"""

        user_prompt = f"""请为以下新闻生成中文摘要：

新闻标题：{title}
新闻内容：{content}

中文摘要："""
    else:
        system_prompt = """You are a professional stablecoin industry analyst. Generate concise English summaries for news articles.

Requirements:
1. Summarize in 1-2 sentences
2. Highlight key information (company names, product names, amounts)
3. Maintain objectivity
4. Use professional but accessible language"""

        user_prompt = f"""Summarize the following news:

Title: {title}
Content: {content}

Summary:"""
    
    try:
        # 调用OpenAI API
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,
            temperature=0.3  # 较低的temperature使输出更稳定
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        print(f"❌ 摘要生成失败: {e}")
        return None

# =========================
# 批量处理
# =========================

def summarize_articles_batch(articles, language="zh", max_count=10):
    """
    批量生成新闻摘要
    
    参数:
        articles: 新闻列表
        language: 输出语言
        max_count: 最多处理数量（避免API费用过高）
    
    返回:
        带摘要的新闻列表
    """
    print("\n" + "=" * 60)
    print(f"批量生成摘要（最多{max_count}条）")
    print("=" * 60)
    
    # 限制数量
    articles_to_process = articles[:max_count]
    
    results = []
    success_count = 0
    total_tokens = 0
    
    for i, article in enumerate(articles_to_process, 1):
        print(f"\n处理 {i}/{len(articles_to_process)}: {article.get('title', '')[:50]}...")
        
        # 生成摘要
        summary = summarize_article(article, language)
        
        if summary:
            article['ai_summary'] = summary
            article['summarized_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            success_count += 1
            print(f"  ✅ 摘要: {summary[:80]}...")
        else:
            article['ai_summary'] = None
            print(f"  ❌ 摘要生成失败")
        
        results.append(article)
    
    print("\n" + "=" * 60)
    print(f"批量处理完成")
    print("=" * 60)
    print(f"✅ 成功: {success_count}/{len(articles_to_process)}")
    
    return results

# =========================
# 智能分类
# =========================

def classify_article(article):
    """
    使用GPT智能分类新闻
    
    参数:
        article: 新闻字典
    
    返回:
        分类标签
    """
    if not client:
        return None
    
    title = article.get('title', '')
    content = article.get('summary', article.get('description', ''))
    
    system_prompt = """你是稳定币行业专家。请将新闻分类到合适的类别。

类别选项：
1. 📋 政策监管 - 涉及监管政策、法律法规、牌照许可
2. 🏢 公司动态 - 公司产品发布、业务拓展、合作伙伴
3. 💰 融资并购 - 融资、投资、收购、IPO

只回复一个类别标签。"""
    
    user_prompt = f"""新闻标题：{title}
新闻内容：{content}

分类："""
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        category = response.choices[0].message.content.strip()
        return category
        
    except Exception as e:
        print(f"❌ 分类失败: {e}")
        return None

# =========================
# 重要性评分
# =========================

def rate_importance(article):
    """
    评估新闻的重要程度
    
    参数:
        article: 新闻字典
    
    返回:
        重要性评分（高/中/低）
    """
    if not client:
        return None
    
    title = article.get('title', '')
    content = article.get('summary', article.get('description', ''))
    
    system_prompt = """你是稳定币行业专家。评估新闻的重要程度。

评估标准：
- 高：重大监管变化、大公司战略布局、大额融资（>$50M）
- 中：一般公司动态、中等融资、常规政策更新
- 低：小公司消息、技术更新、市场分析

只回复：高、中 或 低"""
    
    user_prompt = f"""新闻标题：{title}
新闻内容：{content}

重要性："""
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=10,
            temperature=0.1
        )
        
        importance = response.choices[0].message.content.strip()
        return importance
        
    except Exception as e:
        print(f"❌ 评分失败: {e}")
        return None

# =========================
# 提取关键信息
# =========================

def extract_key_info(article):
    """
    提取新闻中的关键信息
    
    返回:
        字典，包含公司、产品、金额等关键信息
    """
    if not client:
        return None
    
    title = article.get('title', '')
    content = article.get('summary', article.get('description', ''))
    
    system_prompt = """你是信息提取专家。从新闻中提取关键信息。

提取以下信息（如果存在）：
- 公司名称
- 产品名称
- 涉及金额
- 地区/国家
- 时间

以JSON格式返回，例如：
{
  "companies": ["Circle", "Tether"],
  "products": ["USDC"],
  "amount": "$100M",
  "regions": ["Singapore"],
  "date": "2025-01"
}"""
    
    user_prompt = f"""新闻标题：{title}
新闻内容：{content}

关键信息（JSON）："""
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        key_info = response.choices[0].message.content.strip()
        # 尝试解析JSON
        try:
            return json.loads(key_info)
        except:
            return key_info
        
    except Exception as e:
        print(f"❌ 信息提取失败: {e}")
        return None

# =========================
# 测试函数
# =========================

def test_summarizer():
    """测试摘要器"""
    
    # 测试新闻
    test_article = {
        'title': 'Circle Receives Singapore Regulatory Approval for MiCA-Compliant Stablecoin',
        'summary': 'Circle, the issuer of USDC stablecoin, has received regulatory approval from Singapore\'s central bank to operate its stablecoin under the new MiCA framework.',
        'source': 'CoinDesk',
        'date': '2025-01-10'
    }
    
    print("=" * 60)
    print("测试AI摘要器")
    print("=" * 60)
    
    # 测试摘要
    print("\n1. 测试中文摘要:")
    summary_zh = summarize_article(test_article, language="zh")
    if summary_zh:
        print(f"✅ 中文摘要: {summary_zh}")
    
    # 测试分类
    print("\n2. 测试智能分类:")
    category = classify_article(test_article)
    if category:
        print(f"✅ 分类: {category}")
    
    # 测试重要性
    print("\n3. 测试重要性评分:")
    importance = rate_importance(test_article)
    if importance:
        print(f"✅ 重要性: {importance}")
    
    # 测试关键信息提取
    print("\n4. 测试关键信息提取:")
    key_info = extract_key_info(test_article)
    if key_info:
        print(f"✅ 关键信息:")
        if isinstance(key_info, dict):
            for key, value in key_info.items():
                print(f"   {key}: {value}")
        else:
            print(f"   {key_info}")

# =========================
# 主程序
# =========================

def main():
    import sys
    
    if not API_KEY:
        print("❌ 未配置API Key")
        print("请在.env文件中设置 OPENAI_API_KEY")
        return
    
    if len(sys.argv) < 2:
        print("=" * 60)
        print("AI智能摘要器（OpenAI）")
        print("=" * 60)
        print("\n用法:")
        print("  python ai_summarizer.py test              # 测试功能")
        print("  python ai_summarizer.py summarize <json>  # 批量摘要")
        return
    
    command = sys.argv[1]
    
    if command == "test":
        test_summarizer()
    
    elif command == "summarize" and len(sys.argv) == 3:
        json_file = sys.argv[2]
        
        # 读取新闻
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            print(f"读取到 {len(articles)} 条新闻")
            
            # 批量处理（最多10条）
            results = summarize_articles_batch(articles[:10], language="zh")
            
            # 保存结果
            output_file = json_file.replace('.json', '_summarized.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ 结果已保存: {output_file}")
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
    
    else:
        print("❌ 无效的命令")

if __name__ == "__main__":
    main()