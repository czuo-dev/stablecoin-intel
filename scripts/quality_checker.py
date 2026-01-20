"""
周报质量自动检查器
"""

def check_report_quality(report_content: str, language: str) -> dict:
    """
    自动检查周报质量
    
    返回: {
        'score': 85,
        'passed': True,
        'issues': [],
        'suggestions': []
    }
    """
    
    result = {
        'score': 100,
        'passed': True,
        'issues': [],
        'suggestions': []
    }
    
    # 1. 长度检查
    char_count = len(report_content)
    if char_count < 1500:
        result['score'] -= 20
        result['issues'].append(f"内容过短: {char_count} 字符（建议>2000）")
    
    # 2. 结构检查
    required_sections = {
        'zh': ['概览', '重点', '监管', '市场'],
        'en': ['Overview', 'Highlights', 'Policy', 'Market'],
        'es': ['Resumen', 'Destacadas', 'Regulatorias', 'Mercado']
    }
    
    missing_sections = []
    for section in required_sections.get(language, []):
        if section not in report_content:
            missing_sections.append(section)
    
    if missing_sections:
        result['score'] -= 15
        result['issues'].append(f"缺少章节: {', '.join(missing_sections)}")
    
    # 3. 数据真实性检查
    suspicious = ['据报道', '有消息', 'according to reports', 'it is said']
    found_suspicious = [s for s in suspicious if s in report_content]
    
    if found_suspicious:
        result['score'] -= 10
        result['issues'].append(f"可能编造内容: {len(found_suspicious)} 处")
    
    # 4. 日期检查
    if '2026' not in report_content and '2025' not in report_content:
        result['score'] -= 5
        result['suggestions'].append("缺少具体日期")
    
    # 5. 来源检查
    sources = ['Bloomberg', 'Reuters', 'CoinDesk', 'The Block']
    has_sources = any(s in report_content for s in sources)
    
    if not has_sources:
        result['score'] -= 10
        result['suggestions'].append("建议添加新闻来源引用")
    
    # 总体评估
    result['passed'] = result['score'] >= 70
    
    return result

def batch_check_all_reports(reports_dir: str):
    """批量检查所有周报质量"""
    print("=" * 70)
    print("📊 周报质量检查")
    print("=" * 70 + "\n")
    
    reports_path = Path(reports_dir)
    report_files = list(reports_path.glob('weekly_report_*_v2.md'))
    
    for report_file in report_files:
        # 判断语言
        if '_zh_' in report_file.name:
            lang = 'zh'
        elif '_en_' in report_file.name:
            lang = 'en'
        elif '_es_' in report_file.name:
            lang = 'es'
        else:
            continue
        
        # 读取并检查
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = check_report_quality(content, lang)
        
        # 显示结果
        status = "✅" if result['passed'] else "❌"
        print(f"{status} {report_file.name}")
        print(f"   评分: {result['score']}/100")
        
        if result['issues']:
            print(f"   问题:")
            for issue in result['issues']:
                print(f"     - {issue}")
        
        if result['suggestions']:
            print(f"   建议:")
            for suggestion in result['suggestions']:
                print(f"     - {suggestion}")
        
        print()
    
    print("=" * 70)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    # 找最新的报告目录
    reports_dirs = sorted(Path('reports').glob('2026-*'))
    if reports_dirs:
        batch_check_all_reports(str(reports_dirs[-1]))
    else:
        print("❌ 未找到周报目录")
