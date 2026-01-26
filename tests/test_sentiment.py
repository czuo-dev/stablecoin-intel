# test_sentiment.py

from src.processors.sentiment_analyzer import SentimentAnalyzer

print("🎭 测试情感分析器\n")
print("="*60)

analyzer = SentimentAnalyzer()

test_articles = [
    {
        "title": "PayPal launches PYUSD in Europe - Major expansion",
        "description": "Breakthrough partnership with Visa for stablecoin adoption"
    },
    {
        "title": "SEC sues Binance over stablecoin violations",
        "description": "Lawsuit alleges fraud and regulatory concerns"
    },
    {
        "title": "Report: Stablecoin market analysis for Q4",
        "description": "Research study shows neutral trends in adoption"
    },
    {
        "title": "Circle获得香港金管局稳定币牌照",
        "description": "监管批准标志着行业的突破性进展"
    },
    {
        "title": "Tether面临监管调查和欺诈指控",
        "description": "多个国家警告USDT存在风险"
    }
]

print("\n【单篇文章分析】")
print("-"*60)

for i, article in enumerate(test_articles, 1):
    result = analyzer.analyze_article(article)
    
    print(f"\n{i}. {article['title'][:50]}...")
    print(f"   情感: {result['emoji']} {result['sentiment']}")
    print(f"   置信度: {result['confidence']:.2f}")
    print(f"   关键词: {', '.join(result['keywords_found'])}")

print("\n" + "="*60)
print("\n【批量分析】")
print("-"*60)

batch_result = analyzer.analyze_batch(test_articles)

print(f"\n整体情感: {batch_result['overall_sentiment']}")
print(f"\n情感分布:")
print(f"  🟢 正面: {batch_result['sentiment_distribution']['positive']} 篇 ({batch_result['percentage']['positive']}%)")
print(f"  🔴 负面: {batch_result['sentiment_distribution']['negative']} 篇 ({batch_result['percentage']['negative']}%)")
print(f"  ⚪ 中性: {batch_result['sentiment_distribution']['neutral']} 篇 ({batch_result['percentage']['neutral']}%)")

print("\n✅ 测试完成！")