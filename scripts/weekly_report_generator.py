# scripts/weekly_report_generator.py

"""
周报生成器 - 使用AI生成三语周报
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from templates.prompt_templates import WeeklyReportPrompts
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

def generate_report_with_ai(prompt: str, language: str) -> str:
    """使用AI生成周报内容"""
    
    print(f"   🤖 使用AI生成{language}版本...")
    
    try:
        # 使用OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是专业的稳定币行业分析师。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        content = response.choices[0].message.content
        
        print(f"   ✅ {language}版本生成成功")
        return content
        
    except Exception as e:
        print(f"   ❌ 生成失败: {e}")
        return None

def generate_weekly_reports(weekly_data_file: str):
    """生成三语周报"""
    
    print("=" * 70)
    print("📝 开始生成周报")
    print("=" * 70 + "\n")
    
    # 1. 加载周报数据
    print("📂 加载周报数据...")
    with open(weekly_data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    period = f"{data['period']['start']} 至 {data['period']['end']}"
    print(f"   期间: {period}")
    print(f"   新闻: {data['stats']['total_news']} 篇\n")
    
    # 2. 创建输出目录
    week_date = data['period']['end']
    output_dir = Path('reports') / week_date
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 3. 生成三种语言版本
    languages = {
        'zh': '中文',
        'en': 'English',
        'es': 'Español'
    }
    
    reports = {}
    
    for lang_code, lang_name in languages.items():
        print(f"🌍 生成{lang_name}周报...")
        
        # 获取Prompt
        prompt = WeeklyReportPrompts.get_summary_prompt(lang_code, data)
        
        # 使用AI生成
        report_content = generate_report_with_ai(prompt, lang_code)
        
        if report_content:
            # 保存Markdown文件
            output_file = output_dir / f'weekly_report_{lang_code}.md'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"   💾 已保存: {output_file}\n")
            reports[lang_code] = report_content
        else:
            print(f"   ⚠️  {lang_name}版本生成失败\n")
    
    # 4. 保存元数据
    metadata = {
        'week': week_date,
        'period': data['period'],
        'generated_at': datetime.now().isoformat(),
        'stats': data['stats'],
        'languages': list(reports.keys())
    }
    
    metadata_file = output_dir / 'metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("=" * 70)
    print("✅ 周报生成完成!")
    print("=" * 70)
    print(f"\n📁 报告位置: {output_dir}")
    print(f"📄 生成文件:")
    for lang in reports.keys():
        print(f"   - weekly_report_{lang}.md")
    print(f"   - metadata.json")
    
    return reports

if __name__ == '__main__':
    # 获取最新的周报数据文件
    weekly_dir = Path('data/weekly')
    if not weekly_dir.exists():
        print("❌ 请先运行 weekly_aggregator.py 生成周报数据")
        sys.exit(1)
    
    # 找最新的文件
    weekly_files = sorted(weekly_dir.glob('weekly_data_*.json'))
    if not weekly_files:
        print("❌ 未找到周报数据文件")
        sys.exit(1)
    
    latest_file = weekly_files[-1]
    print(f"📂 使用数据文件: {latest_file}\n")
    
    # 生成周报
    reports = generate_weekly_reports(str(latest_file))