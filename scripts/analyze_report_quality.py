"""
周报质量分析器
"""

import json
from pathlib import Path

def analyze_report_quality(report_file: str):
    """分析周报质量"""
    
    print("=" * 70)
    print("📊 周报质量分析")
    print("=" * 70 + "\n")
    
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 基础统计
    total_chars = len(content)
    total_words = len(content.split())
    lines = content.split('\n')
    
    print(f"📝 基础统计:")
    print(f"   字符数: {total_chars:,}")
    print(f"   单词数: {total_words:,}")
    print(f"   行数: {len(lines):,}")
    
    # 结构检查
    print(f"\n📋 结构检查:")
    required_sections = [
        '概览', 'Overview', 'Resumen',
        '重点', 'Highlights', 'Destacadas',
        '监管', 'Policy', 'Regulatorias',
        '市场', 'Market', 'Mercado'
    ]
    
    found_sections = []
    for section in required_sections:
        if section in content:
            found_sections.append(section)
    
    print(f"   找到章节: {len(found_sections)}/{len(required_sections)}")
    for section in found_sections:
        print(f"     ✓ {section}")
    
    # 数据真实性检查
    print(f"\n⚠️  潜在问题:")
    
    suspicious_phrases = [
        '根据最新数据', '据报道', '预计', '有消息称',
        'according to reports', 'it is estimated',
        'según informes', 'se estima'
    ]
    
    issues = []
    for phrase in suspicious_phrases:
        if phrase in content:
            issues.append(phrase)
    
    if issues:
        print(f"   可能编造数据: 发现 {len(issues)} 处模糊表述")
        for issue in issues[:3]:
            print(f"     - '{issue}'")
    else:
        print(f"   ✓ 未发现明显编造")
    
    # 质量评分
    score = 100
    
    if total_chars < 1500:
        score -= 20
        print(f"   - 内容太短 (-20分)")
    
    if len(found_sections) < 4:
        score -= 15
        print(f"   - 结构不完整 (-15分)")
    
    if len(issues) > 3:
        score -= 25
        print(f"   - 可能有编造内容 (-25分)")
    
    print(f"\n📊 总体评分: {score}/100")
    print("=" * 70)
    
    return score

if __name__ == '__main__':
    # 分析最新的中文周报
    reports = sorted(Path('reports').glob('*/weekly_report_zh.md'))
    if reports:
        latest = reports[-1]
        print(f"分析文件: {latest}\n")
        analyze_report_quality(str(latest))
    else:
        print("❌ 未找到周报文件")
