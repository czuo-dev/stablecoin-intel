# src/processors/sentiment_analyzer.py

from typing import Dict, List


class SentimentAnalyzer:
    """简单的情感分析器（基于关键词）"""
    
    def __init__(self):
        # 正面关键词
        self.positive_keywords = [
            "launch", "partnership", "approval", "growth", "success",
            "expand", "adoption", "integration", "breakthrough", "innovation",
            "support", "bullish", "positive", "increase", "rally",
            "推出", "合作", "批准", "增长", "成功", "扩展", "采用", "整合", "突破", "创新"
        ]
        
        # 负面关键词
        self.negative_keywords = [
            "ban", "lawsuit", "hack", "decline", "crash",
            "fraud", "scam", "risk", "concern", "warning",
            "suspend", "restrict", "penalty", "investigation",
            "禁止", "诉讼", "黑客", "下跌", "崩盘", "欺诈", "骗局", "风险", "担忧", "警告"
        ]
        
        # 中性关键词
        self.neutral_keywords = [
            "report", "study", "research", "analysis", "update",
            "statement", "comment", "discussion",
            "报告", "研究", "分析", "更新", "声明"
        ]
    
    def analyze_article(self, article: Dict) -> Dict:
        """分析单篇文章的情感"""
        text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        
        positive_matches = [kw for kw in self.positive_keywords if kw.lower() in text]
        negative_matches = [kw for kw in self.negative_keywords if kw.lower() in text]
        neutral_matches = [kw for kw in self.neutral_keywords if kw.lower() in text]
        
        positive_count = len(positive_matches)
        negative_count = len(negative_matches)
        
        if positive_count > negative_count:
            sentiment = "positive"
            emoji = "🟢"
            confidence = positive_count / (positive_count + negative_count + 0.5)
            keywords = positive_matches
        elif negative_count > positive_count:
            sentiment = "negative"
            emoji = "🔴"
            confidence = negative_count / (positive_count + negative_count + 0.5)
            keywords = negative_matches
        else:
            sentiment = "neutral"
            emoji = "⚪"
            confidence = 0.5
            keywords = neutral_matches
        
        return {
            "sentiment": sentiment,
            "emoji": emoji,
            "confidence": min(confidence, 1.0),
            "keywords_found": keywords[:3]
        }
    
    def analyze_batch(self, articles: List[Dict]) -> Dict:
        """分析一批文章的整体情感"""
        sentiments = []
        
        for article in articles:
            result = self.analyze_article(article)
            sentiments.append(result["sentiment"])
        
        distribution = {
            "positive": sentiments.count("positive"),
            "negative": sentiments.count("negative"),
            "neutral": sentiments.count("neutral")
        }
        
        total = len(sentiments)
        percentage = {
            "positive": round(distribution["positive"] / total * 100, 1),
            "negative": round(distribution["negative"] / total * 100, 1),
            "neutral": round(distribution["neutral"] / total * 100, 1)
        }
        
        if distribution["positive"] > distribution["negative"]:
            overall = "positive"
        elif distribution["negative"] > distribution["positive"]:
            overall = "negative"
        else:
            overall = "neutral"
        
        return {
            "overall_sentiment": overall,
            "sentiment_distribution": distribution,
            "percentage": percentage
        }