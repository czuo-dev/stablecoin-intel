"""
改进版周报生成器 - 包含成本优化
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from templates.prompt_templates_v2 import ImprovedPrompts
from openai import OpenAI

# 优先从环境变量读取 API Key（用于 GitHub Actions）
# 如果不存在，则从 config 模块导入（用于本地开发）
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    try:
        from config import OPENAI_API_KEY
    except ImportError:
        OPENAI_API_KEY = None

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 未设置。请在环境变量或 config.py 中设置。")

client = OpenAI(api_key=OPENAI_API_KEY)

# ============================================================
# 成本优化工具类
# ============================================================

import hashlib
from datetime import timedelta

class CostOptimizer:
    """成本优化器"""
    
    def __init__(self):
        self.cache_dir = Path('cache/reports')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_key(self, data: dict, language: str) -> str:
        """生成缓存key"""
        content = json.dumps(data['stats'], sort_keys=True) + language
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_report(self, cache_key: str) -> str:
        """获取缓存的周报"""
        cache_file = self.cache_dir / f"{cache_key}.md"
        
        if cache_file.exists():
            # 检查缓存是否过期（7天）
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime < timedelta(days=7):
                print(f"   ♻️  使用缓存版本")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
        
        return None
    
    def cache_report(self, cache_key: str, content: str):
        """缓存周报"""
        cache_file = self.cache_dir / f"{cache_key}.md"
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def estimate_cost(total_tokens: int, model: str = 'gpt-4o-mini') -> float:
        """估算成本"""
        
        prices = {
            'gpt-4o-mini': {
                'input': 0.150 / 1_000_000,
                'output': 0.600 / 1_000_000
            }
        }
        
        # 假设输入:输出 = 1:1.3
        input_tokens = int(total_tokens / 2.3)
        output_tokens = total_tokens - input_tokens
        
        cost = (
            input_tokens * prices[model]['input'] +
            output_tokens * prices[model]['output']
        )
        
        return cost

# ============================================================
# 周报生成函数
# ============================================================

def generate_report_single(prompt: str, language: str, use_cache: bool = True) -> tuple:
    """
    单独生成一份周报（带缓存）
    
    Returns:
        (content, tokens_used)
    """
    
    optimizer = CostOptimizer()
    
    # 检查缓存
    if use_cache:
        cache_key = hashlib.md5(prompt.encode()).hexdigest()[:16]
        cached = optimizer.get_cached_report(cache_key)
        if cached:
            return cached, 0  # 0 tokens因为用了缓存
    
    print(f"   🤖 使用OpenAI生成{language}版本...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "你是专业的稳定币行业分析师。你只基于提供的真实数据生成报告，不编造任何信息。"
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.3,  # 降低温度提高准确性
        )
        
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        print(f"   ✅ 生成成功")
        print(f"   📊 Token: {response.usage.prompt_tokens} + {response.usage.completion_tokens} = {tokens_used}")
        
        # 缓存结果
        if use_cache:
            optimizer.cache_report(cache_key, content)
        
        return content, tokens_used
        
    except Exception as e:
        print(f"   ❌ 生成失败: {e}")
        return None, 0

def generate_report_batch(data: dict) -> tuple:
    """
    批量生成三语周报（一次API调用）
    
    Returns:
        (reports_dict, tokens_used)
    """
    
    print(f"   🚀 使用批量模式生成三语周报...")
    
    # 准备简化的数据
    simplified_data = {
        'period': data['period'],
        'stats': data['stats'],
        'top_news': [
            {
                'title': item['title'],
                'source': item.get('source', 'Unknown'),
                'date': item.get('published_at', '')[:10],
                'summary': item.get('content', '')[:200]
            }
            for item in data['top_news'][:8]
        ]
    }
    
    # 批量Prompt
    batch_prompt = f"""你是专业的稳定币行业分析师。请基于以下真实数据，同时生成中文、英文、西班牙语三个版本的周报摘要。

【数据范围】
时间: {simplified_data['period']['start']} 至 {simplified_data['period']['end']}
新闻总数: {simplified_data['stats']['total_news']}

【Top新闻】
{json.dumps(simplified_data['top_news'], ensure_ascii=False, indent=2)}

【输出要求】
请严格按照以下格式输出，使用明确的分隔符：

===CHINESE_START===
# 稳定币行业周报
**报告期**: {simplified_data['period']['start']} 至 {simplified_data['period']['end']}

## 📊 本周概览
（3-5个要点，基于真实新闻）

## 🔥 重点新闻
（Top 5，每条150字）

===CHINESE_END===

===ENGLISH_START===
# Stablecoin Weekly Report
**Period**: {simplified_data['period']['start']} to {simplified_data['period']['end']}

## 📊 Weekly Overview
(3-5 bullet points based on real news)

## 🔥 Key Highlights
(Top 5, 150 words each)

===ENGLISH_END===

===SPANISH_START===
# Informe Semanal de Stablecoins
**Período**: {simplified_data['period']['start']} a {simplified_data['period']['end']}

## 📊 Resumen Semanal
(3-5 puntos basados en noticias reales)

## 🔥 Noticias Destacadas
(Top 5, 150 palabras cada una)

===SPANISH_END===

【重要】
- 只使用提供的真实新闻
- 不要编造数据
- 包含具体来源和日期
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "你是专业的多语言分析师，能同时生成中英西三语报告。"
                },
                {"role": "user", "content": batch_prompt}
            ],
            max_tokens=6000,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # 分割三份报告
        reports = {}
        
        # 提取中文
        if '===CHINESE_START===' in content and '===CHINESE_END===' in content:
            start = content.find('===CHINESE_START===') + len('===CHINESE_START===')
            end = content.find('===CHINESE_END===')
            reports['zh'] = content[start:end].strip()
        
        # 提取英文
        if '===ENGLISH_START===' in content and '===ENGLISH_END===' in content:
            start = content.find('===ENGLISH_START===') + len('===ENGLISH_START===')
            end = content.find('===ENGLISH_END===')
            reports['en'] = content[start:end].strip()
        
        # 提取西班牙语
        if '===SPANISH_START===' in content and '===SPANISH_END===' in content:
            start = content.find('===SPANISH_START===') + len('===SPANISH_START===')
            end = content.find('===SPANISH_END===')
            reports['es'] = content[start:end].strip()
        
        print(f"   ✅ 批量生成成功")
        print(f"   📊 Token: {response.usage.prompt_tokens} + {response.usage.completion_tokens} = {tokens_used}")
        print(f"   💰 成本: ${CostOptimizer.estimate_cost(tokens_used):.4f}")
        
        return reports, tokens_used
        
    except Exception as e:
        print(f"   ❌ 批量生成失败: {e}")
        return {}, 0

# ============================================================
# 主生成函数
# ============================================================

def generate_weekly_reports(weekly_data_file: str, use_batch: bool = False):
    """
    生成改进版三语周报
    
    Args:
        weekly_data_file: 周报数据文件路径
        use_batch: 是否使用批量模式（更省钱但质量稍低）
    """
    
    print("=" * 70)
    print(f"📝 开始生成{'批量' if use_batch else '单独'}模式周报")
    print("=" * 70 + "\n")
    
    # 加载数据
    with open(weekly_data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    period = f"{data['period']['start']} 至 {data['period']['end']}"
    print(f"📅 报告期: {period}")
    print(f"📊 新闻数: {data['stats']['total_news']} 篇\n")
    
    # 创建输出目录
    week_date = data['period']['end']
    output_dir = Path('reports') / week_date
    output_dir.mkdir(parents=True, exist_ok=True)
    
    total_tokens = 0
    reports = {}
    
    if use_batch:
        # 批量模式
        reports, tokens = generate_report_batch(data)
        total_tokens = tokens
        
    else:
        # 单独生成模式
        languages = {
            'zh': '中文',
            'en': 'English',
            'es': 'Español'
        }
        
        for lang_code, lang_name in languages.items():
            print(f"🌍 生成{lang_name}周报...")
            
            # 使用改进版Prompt
            prompt = ImprovedPrompts.get_summary_prompt(lang_code, data)
            
            # 生成
            report_content, tokens = generate_report_single(prompt, lang_code)
            
            if report_content:
                reports[lang_code] = report_content
                total_tokens += tokens
            
            print()
    
    # 保存报告
    for lang_code, content in reports.items():
        output_file = output_dir / f'weekly_report_{lang_code}_v2.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 已保存: {output_file}")
    
    # 保存元数据
    metadata = {
        'week': week_date,
        'period': data['period'],
        'generated_at': datetime.now().isoformat(),
        'stats': data['stats'],
        'version': 'v2',
        'model': 'gpt-4o-mini',
        'mode': 'batch' if use_batch else 'single',
        'total_tokens': total_tokens,
        'estimated_cost': CostOptimizer.estimate_cost(total_tokens)
    }
    
    with open(output_dir / 'metadata_v2.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    # 成本总结
    print("\n" + "=" * 70)
    print("✅ 周报生成完成!")
    print("=" * 70)
    print(f"📁 报告位置: {output_dir}")
    print(f"📊 Token使用: {total_tokens:,}")
    print(f"💰 预估成本: ${CostOptimizer.estimate_cost(total_tokens):.4f}")
    print(f"📈 年度成本: ${CostOptimizer.estimate_cost(total_tokens) * 52:.2f}")
    
    return reports

# ============================================================
# 主程序
# ============================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='生成周报')
    parser.add_argument('--batch', action='store_true', 
                       help='使用批量模式（更省钱）')
    parser.add_argument('--no-cache', action='store_true',
                       help='不使用缓存')
    
    args = parser.parse_args()
    
    # 找周报数据
    weekly_dir = Path('data/weekly')
    weekly_files = sorted(weekly_dir.glob('weekly_data_*.json'))
    
    if not weekly_files:
        print("❌ 未找到周报数据文件")
        print("   请先运行: python scripts/weekly_aggregator.py")
        sys.exit(1)
    
    latest_file = weekly_files[-1]
    print(f"📂 使用数据: {latest_file}\n")
    
    # 生成周报
    reports = generate_weekly_reports(
        str(latest_file), 
        use_batch=args.batch
    )