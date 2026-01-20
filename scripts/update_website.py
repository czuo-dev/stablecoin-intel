"""
自动更新网站数据
"""

import json
from pathlib import Path
from datetime import datetime

def update_website_data():
    """更新网站的周报数据"""
    
    print("🔄 更新网站数据...")
    
    reports_data = []
    
    # 扫描所有周报
    reports_dir = Path('reports')
    for week_dir in sorted(reports_dir.glob('2026-*'), reverse=True):
        # 读取元数据
        metadata_file = week_dir / 'metadata_v2.json'
        if not metadata_file.exists():
            continue
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # 添加到列表
        reports_data.append({
            'date': week_dir.name,
            'title': f'稳定币行业周报 Week {len(reports_data) + 1}',
            'period': f"{metadata['period']['start']} 至 {metadata['period']['end']}",
            'stats': metadata['stats'],
            'languages': ['zh', 'en', 'es']
        })
    
    # 更新JavaScript数据文件
    js_file = Path('docs') / 'reports.js'
    
    # 如果文件不存在，创建它
    if not js_file.exists():
        js_file.parent.mkdir(parents=True, exist_ok=True)
        js_content = 'const reports = [];\n'
    else:
        # 读取现有内容
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
    
    # 替换reports数据
    reports_json = json.dumps(reports_data, ensure_ascii=False, indent=4)
    
    # 找到并替换
    start_marker = 'const reports ='
    end_marker = ';'
    
    start_idx = js_content.find(start_marker)
    if start_idx == -1:
        # 如果找不到标记，直接替换整个文件
        new_content = f'const reports = {reports_json};\n'
    else:
        end_idx = js_content.find(end_marker, start_idx) + len(end_marker)
        new_content = (
            js_content[:start_idx] +
            f'const reports = {reports_json};' +
            js_content[end_idx:]
        )
    
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 已更新 {len(reports_data)} 期周报数据")
    print(f"📁 网站目录: docs/")

if __name__ == '__main__':
    update_website_data()
