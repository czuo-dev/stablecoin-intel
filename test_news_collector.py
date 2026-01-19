# test_news_collector.py

from src.collectors.news_collector import NewsCollector
import json
from datetime import datetime

def test_collect_news():
    """测试新闻收集功能"""
    
    collector = NewsCollector()
    
    # 收集过去3天的新闻（避免超过API限制）
    articles = collector.collect_news(days_back=3)
    
    # 显示Top 10
    print("\n🏆 Top 10 新闻:")
    for i, article in enumerate(articles[:10], 1):
        print(f"\n【{i}】{article['title']}")
        print(f"    来源: {article['source']['name']} ({article.get('source_quality', 'unknown')})")
        print(f"    关键词: {article.get('search_keyword', 'N/A')}")
        print(f"    权重: {article.get('priority_weight', 0)}")
        print(f"    日期: {article['publishedAt'][:10]}")
    
    # 保存到文件
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_file = f'data/raw/newsapi_raw_{date_str}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 数据已保存: {output_file}")
    
    # 统计分析
    print(f"\n📈 数据分析:")
    
    # 按来源统计
    sources = {}
    for article in articles:
        source = article['source']['name']
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\n   热门新闻源:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {source}: {count} 篇")
    
    # 按关键词统计
    keywords = {}
    for article in articles:
        kw = article.get('search_keyword', 'unknown')
        keywords[kw] = keywords.get(kw, 0) + 1
    
    print(f"\n   热门关键词:")
    for kw, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {kw}: {count} 篇")

if __name__ == '__main__':
    test_collect_news()