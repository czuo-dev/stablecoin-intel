# src/processors/trend_analyzer.py

from typing import Dict, List
from collections import Counter
from datetime import datetime


class TrendAnalyzer:
    """趋势分析器 - 分析标签和分类趋势"""
    
    def __init__(self):
        pass
    
    def analyze_tags(self, classified_articles: List[Dict], top_n: int = 10) -> Dict:
        """
        分析标签趋势
        
        Args:
            classified_articles: AI分类后的文章列表
            top_n: 返回前N个热门标签
            
        Returns:
            {
                "top_tags": [{"tag": "香港", "count": 15, "percentage": 25.0}, ...],
                "total_tags": 45,
                "unique_tags": 28
            }
        """
        
        all_tags = []
        for article in classified_articles:
            tags = article.get("tags", [])
            all_tags.extend(tags)
        
        # 统计标签频率
        tag_counter = Counter(all_tags)
        total_tags = len(all_tags)
        
        # 计算百分比
        top_tags = []
        for tag, count in tag_counter.most_common(top_n):
            percentage = (count / total_tags * 100) if total_tags > 0 else 0
            top_tags.append({
                "tag": tag,
                "count": count,
                "percentage": round(percentage, 1)
            })
        
        return {
            "top_tags": top_tags,
            "total_tags": total_tags,
            "unique_tags": len(tag_counter)
        }
    
    def analyze_categories(self, classified_articles: List[Dict]) -> Dict:
        """
        分析类别分布
        
        Returns:
            {
                "distribution": {
                    "policy": {"count": 10, "percentage": 40.0},
                    "company": {"count": 12, "percentage": 48.0},
                    "funding": {"count": 3, "percentage": 12.0}
                },
                "total": 25
            }
        """
        
        categories = [a.get("primary_category", "unknown") for a in classified_articles]
        category_counter = Counter(categories)
        total = len(categories)
        
        distribution = {}
        for category, count in category_counter.items():
            percentage = (count / total * 100) if total > 0 else 0
            distribution[category] = {
                "count": count,
                "percentage": round(percentage, 1)
            }
        
        return {
            "distribution": distribution,
            "total": total
        }
    
    def analyze_importance(self, classified_articles: List[Dict]) -> Dict:
        """
        分析新闻重要性分布
        
        Returns:
            {
                "high_importance": 5,  # importance >= 8
                "medium_importance": 12,  # 5 <= importance < 8
                "low_importance": 8,  # importance < 5
                "average_importance": 6.2,
                "top_important_articles": [...]
            }
        """
        
        importances = [a.get("importance", 5) for a in classified_articles]
        
        high = sum(1 for i in importances if i >= 8)
        medium = sum(1 for i in importances if 5 <= i < 8)
        low = sum(1 for i in importances if i < 5)
        
        avg_importance = sum(importances) / len(importances) if importances else 0
        
        # 找出最重要的文章（importance >= 8）
        top_articles = sorted(
            [a for a in classified_articles if a.get("importance", 0) >= 8],
            key=lambda x: x.get("importance", 0),
            reverse=True
        )[:5]
        
        top_important = [
            {
                "title": a["article"]["title"][:60],
                "importance": a.get("importance", 0),
                "category": a.get("primary_category", "unknown"),
                "tags": a.get("tags", [])[:3]
            }
            for a in top_articles
        ]
        
        return {
            "high_importance": high,
            "medium_importance": medium,
            "low_importance": low,
            "average_importance": round(avg_importance, 1),
            "top_important_articles": top_important
        }
    
    def generate_trend_report(self, classified_articles: List[Dict]) -> str:
        """
        生成趋势分析报告（文本格式）
        
        Returns:
            Markdown格式的趋势报告
        """
        
        tags_analysis = self.analyze_tags(classified_articles, top_n=10)
        categories_analysis = self.analyze_categories(classified_articles)
        importance_analysis = self.analyze_importance(classified_articles)
        
        report = f"""# 📊 稳定币行业趋势分析

**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

---

## 🔥 热点标签 Top 10

"""
        
        # 添加热点标签（带火焰emoji）
        for i, tag_info in enumerate(tags_analysis["top_tags"], 1):
            count = tag_info["count"]
            tag = tag_info["tag"]
            pct = tag_info["percentage"]
            
            # 根据提及次数显示火焰
            if count >= 10:
                emoji = "🔥🔥🔥"
            elif count >= 5:
                emoji = "🔥🔥"
            else:
                emoji = "🔥"
            
            report += f"{i}. {emoji} **{tag}** ({count}次提及, {pct}%)\n"
        
        report += f"\n总标签数: {tags_analysis['total_tags']} | 独特标签: {tags_analysis['unique_tags']}\n\n"
        
        # 类别分布
        report += "---\n\n## 📋 新闻类别分布\n\n"
        
        category_emojis = {
            "policy": "📜",
            "company": "🏢",
            "funding": "💰"
        }
        
        category_names = {
            "policy": "政策监管",
            "company": "公司动态",
            "funding": "融资事件"
        }
        
        for category, data in categories_analysis["distribution"].items():
            emoji = category_emojis.get(category, "📌")
            name = category_names.get(category, category)
            count = data["count"]
            pct = data["percentage"]
            
            # 进度条
            bar_length = int(pct / 5)  # 每5%一个方块
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            report += f"{emoji} **{name}**: {count}篇 ({pct}%)\n"
            report += f"   {bar}\n\n"
        
        # 重要性分析
        report += "---\n\n## ⭐ 新闻重要性分析\n\n"
        
        report += f"- 🔴 高重要性 (≥8分): {importance_analysis['high_importance']}篇\n"
        report += f"- 🟡 中等重要性 (5-7分): {importance_analysis['medium_importance']}篇\n"
        report += f"- 🟢 低重要性 (<5分): {importance_analysis['low_importance']}篇\n"
        report += f"- 📊 平均重要性: {importance_analysis['average_importance']}/10\n\n"
        
        # Top重要新闻
        if importance_analysis["top_important_articles"]:
            report += "### 🌟 本周最重要新闻\n\n"
            
            for i, article in enumerate(importance_analysis["top_important_articles"], 1):
                title = article["title"]
                importance = article["importance"]
                category = article["category"]
                tags = ", ".join(article["tags"])
                
                report += f"{i}. **{title}...** (重要性: {importance}/10)\n"
                report += f"   分类: {category} | 标签: {tags}\n\n"
        
        report += "---\n\n"
        report += "*报告由AI自动生成*\n"
        
        return report
    
    def identify_emerging_trends(
        self, 
        current_tags: List[str], 
        previous_tags: List[str]
    ) -> List[Dict]:
        """
        识别新兴趋势（对比上周和本周的标签）
        
        Args:
            current_tags: 本周的所有标签
            previous_tags: 上周的所有标签
            
        Returns:
            [
                {"tag": "MiCA", "growth": 150, "is_new": False},
                {"tag": "Coinbase", "growth": 999, "is_new": True}
            ]
        """
        
        current_counter = Counter(current_tags)
        previous_counter = Counter(previous_tags)
        
        emerging = []
        
        for tag, current_count in current_counter.most_common(20):
            previous_count = previous_counter.get(tag, 0)
            
            if previous_count == 0:
                # 全新的标签
                emerging.append({
                    "tag": tag,
                    "current_count": current_count,
                    "previous_count": 0,
                    "growth": 999,  # 表示新标签
                    "is_new": True
                })
            elif current_count > previous_count:
                # 增长的标签
                growth_pct = ((current_count - previous_count) / previous_count) * 100
                emerging.append({
                    "tag": tag,
                    "current_count": current_count,
                    "previous_count": previous_count,
                    "growth": round(growth_pct, 1),
                    "is_new": False
                })
        
        # 按增长率排序
        emerging.sort(key=lambda x: x["growth"], reverse=True)
        
        return emerging[:10]  # 返回Top 10