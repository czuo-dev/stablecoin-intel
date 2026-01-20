"""
改进版周报生成器 - 使用优化后的Prompt
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 使用改进版Prompt
from templates.prompt_templates_v2 import ImprovedPrompts
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_report_with_ai(prompt: str, language: str) -> str:
    """使用OpenAI生成周报"""
    
    print(f"   🤖 使用OpenAI生成{language}版本...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 使用mini版本节省成本
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
        
        # 统计token使用
        usage = response.usage
        print(f"   ✅ 生成成功")
        print(f"   📊 Token使用: {usage.prompt_tokens} + {usage.completion_tokens} = {usage.total_tokens}")
        
        return content
        
    except Exception as e:
        print(f"   ❌ 生成失败: {e}")
        return None

def generate_weekly_reports(weekly_data_file: str):
    """生成改进版三语周报"""
    
    print("=" * 70)
    print("📝 开始生成改进版周报")
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
    
    # 生成三种语言
    languages = {
        'zh': '中文',
        'en': 'English',
        'es': 'Español'
    }
    
    reports = {}
    total_tokens = 0
    
    for lang_code, lang_name in languages.items():
        print(f"🌍 生成{lang_name}周报...")
        
        # 使用改进版Prompt
        prompt = ImprovedPrompts.get_summary_prompt(lang_code, data)
        
        # 生成
        report_content = generate_report_with_ai(prompt, lang_code)
        
        if report_content:
            # 保存
            output_file = output_dir / f'weekly_report_{lang_code}_v2.md'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"   💾 已保存: {output_file}\n")
            reports[lang_code] = report_content
        else:
            print(f"   ⚠️  {lang_name}版本生成失败\n")
    
    # 保存元数据
    metadata = {
        'week': week_date,
        'period': data['period'],
        'generated_at': datetime.now().isoformat(),
        'stats': data['stats'],
        'version': 'v2',
        'model': 'gpt-4o-mini'
    }
    
    with open(output_dir / 'metadata_v2.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("=" * 70)
    print("✅ 改进版周报生成完成!")
    print("=" * 70)
    print(f"\n📁 报告位置: {output_dir}")
    
    return reports

if __name__ == '__main__':
    weekly_dir = Path('data/weekly')
    weekly_files = sorted(weekly_dir.glob('weekly_data_*.json'))
    
    if not weekly_files:
        print("❌ 未找到周报数据文件")
        print("   请先运行: python scripts/weekly_aggregator.py")
        sys.exit(1)
    
    latest_file = weekly_files[-1]
    print(f"📂 使用数据: {latest_file}\n")
    
    reports = generate_weekly_reports(str(latest_file))
