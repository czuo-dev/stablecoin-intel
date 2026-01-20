"""
将Markdown周报转换为HTML
"""

import markdown
from pathlib import Path
import json

def convert_md_to_html(md_file: Path, output_file: Path):
    """转换单个Markdown文件为HTML"""
    
    # 读取Markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 转换为HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'toc']
    )
    
    # 确定语言
    if '_zh' in md_file.name:
        lang = 'zh-CN'
        title = '稳定币行业周报'
    elif '_en' in md_file.name:
        lang = 'en'
        title = 'Stablecoin Weekly Report'
    elif '_es' in md_file.name:
        lang = 'es'
        title = 'Informe Semanal de Stablecoins'
    else:
        lang = 'zh-CN'
        title = '周报'
    
    # HTML模板
    full_html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.8;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            color: #2c3e50;
            background: #f5f7fa;
        }}
        .content {{
            background: white;
            padding: 3rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #0066cc;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }}
        h2 {{
            color: #0066cc;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-left: 4px solid #0066cc;
            padding-left: 1rem;
        }}
        h3 {{
            color: #2c3e50;
            margin-top: 1.5rem;
        }}
        p {{
            margin: 1rem 0;
        }}
        strong {{
            color: #34495e;
        }}
        ul, ol {{
            padding-left: 2rem;
        }}
        li {{
            margin: 0.5rem 0;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 2rem;
            padding: 0.5rem 1rem;
            background: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }}
        .back-link:hover {{
            background: #0052a3;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            .content {{
                padding: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <a href="../../index.html" class="back-link">← 返回首页</a>
    <div class="content">
        {html_content}
    </div>
    <div style="text-align: center; margin-top: 2rem; color: #7f8c8d; font-size: 0.9rem;">
        <p>Powered by Stablecoin Intelligence System</p>
    </div>
</body>
</html>"""
    
    # 保存HTML
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✅ 已转换: {output_file}")

def convert_all_reports():
    """转换所有周报"""
    
    print("=" * 70)
    print("📄 转换Markdown周报为HTML")
    print("=" * 70 + "\n")
    
    reports_dir = Path('reports')
    
    # 遍历所有周报目录
    for week_dir in sorted(reports_dir.glob('2026-*')):
        print(f"📅 处理 {week_dir.name}")
        
        # 转换v2版本的周报
        for md_file in week_dir.glob('weekly_report_*_v2.md'):
            # 确定语言
            if '_zh_' in md_file.name:
                html_name = 'zh.html'
            elif '_en_' in md_file.name:
                html_name = 'en.html'
            elif '_es_' in md_file.name:
                html_name = 'es.html'
            else:
                continue
            
            # 输出路径
            output_file = Path('docs/reports') / week_dir.name / html_name
            
            # 转换
            convert_md_to_html(md_file, output_file)
        
        print()
    
    print("=" * 70)
    print("✅ 所有周报已转换为HTML")
    print("=" * 70)

if __name__ == '__main__':
    try:
        import markdown
    except ImportError:
        print("请先安装markdown库:")
        print("  pip install markdown")
        exit(1)
    
    convert_all_reports()
