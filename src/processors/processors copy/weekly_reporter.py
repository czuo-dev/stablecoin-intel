# src/processors/weekly_reporter.py

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
from src.processors.batch_summarizer import BatchSummarizer
from src.processors.translator import MultilingualTranslator
from src.processors.sentiment_analyzer import SentimentAnalyzer


class WeeklyReportGenerator:
    """周报生成器 - 支持多语言"""
    
    def __init__(self, api_key: str):
        self.summarizer = BatchSummarizer(api_key)
        self.translator = MultilingualTranslator(api_key)
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def aggregate_weekly_data(self, data_dir: str = "data/processed") -> Dict[str, List[Dict]]:
        """
        聚合本周的所有数据
        
        Returns:
            {
                "policy": [所有政策类新闻],
                "company": [所有公司类新闻],
                "funding": [所有融资类新闻]
            }
        """
        
        aggregated = {
            "policy": [],
            "company": [],
            "funding": []
        }
        
        # 获取过去7天的日期
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        
        print(f"📅 聚合日期范围: {dates[-1]} 到 {dates[0]}")
        
        # 读取每天的数据文件
        for date in dates:
            filename = f"{data_dir}/categorized_news_{date}.json"
            
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        daily_data = json.load(f)
                    
                    for category in aggregated.keys():
                        if category in daily_data:
                            aggregated[category].extend(daily_data[category])
                    
                    print(f"  ✅ 已加载: {date}")
                except Exception as e:
                    print(f"  ⚠️  加载失败: {date} - {e}")
            else:
                print(f"  ⏭️  跳过: {date} (文件不存在)")
        
        # 统计
        total = sum(len(articles) for articles in aggregated.values())
        print(f"\n📊 本周数据统计:")
        for category, articles in aggregated.items():
            print(f"  {category}: {len(articles)} 篇")
        print(f"  总计: {total} 篇\n")
        
        return aggregated
    
    def generate_weekly_report(
        self, 
        articles_by_category: Dict[str, List[Dict]], 
        target_lang: str = "es"
    ) -> Dict[str, str]:
        """
        生成双语周报
        
        Args:
            articles_by_category: 按类别分类的文章
            target_lang: 目标语言 ("es" 西班牙语 / "en" 英文)
            
        Returns:
            {
                "zh": "中文周报",
                "target": "目标语言周报",
                "combined": "双语合并版"
            }
        """
        
        lang_names = {
            "es": {"name": "Español", "title": "Informe Semanal de Stablecoins"},
            "en": {"name": "English", "title": "Weekly Stablecoin Report"}
        }
        
        week_num = datetime.now().isocalendar()[1]
        year = datetime.now().year
        
        # 生成中文报告头部
        zh_report = f"# 稳定币行业周报\n\n"
        zh_report += f"**{year}年第{week_num}周** | "
        zh_report += f"{datetime.now().strftime('%Y年%m月%d日')}\n\n"
        zh_report += "---\n\n"
        
        # 生成目标语言报告头部
        target_report = f"# {lang_names[target_lang]['title']}\n\n"
        target_report += f"**Semana {week_num}, {year}** | "
        target_report += f"{datetime.now().strftime('%d/%m/%Y')}\n\n"
        target_report += "---\n\n"
        
        # 整体情感分析
        all_articles = []
        for articles in articles_by_category.values():
            all_articles.extend(articles)
        
        if all_articles:
            overall_sentiment = self.sentiment_analyzer.analyze_batch(all_articles)
            
            zh_report += f"## 📊 本周市场情绪\n\n"
            zh_report += f"**整体氛围**: {overall_sentiment['overall_sentiment'].upper()}\n\n"
            zh_report += f"- 🟢 正面: {overall_sentiment['percentage']['positive']}%\n"
            zh_report += f"- 🔴 负面: {overall_sentiment['percentage']['negative']}%\n"
            zh_report += f"- ⚪ 中性: {overall_sentiment['percentage']['neutral']}%\n\n"
            
            target_report += f"## 📊 Sentimiento del Mercado\n\n"
            target_report += f"**Atmósfera general**: {overall_sentiment['overall_sentiment'].upper()}\n\n"
            target_report += f"- 🟢 Positivo: {overall_sentiment['percentage']['positive']}%\n"
            target_report += f"- 🔴 Negativo: {overall_sentiment['percentage']['negative']}%\n"
            target_report += f"- ⚪ Neutral: {overall_sentiment['percentage']['neutral']}%\n\n"
        
        category_names = {
            "policy": {"zh": "📋 政策监管", "es": "📋 Regulación", "en": "📋 Regulation"},
            "company": {"zh": "🏢 公司动态", "es": "🏢 Empresas", "en": "🏢 Companies"},
            "funding": {"zh": "💰 融资事件", "es": "💰 Financiación", "en": "💰 Funding"}
        }
        
        # 按类别生成摘要
        for category, articles in articles_by_category.items():
            if not articles:
                continue
            
            print(f"生成 {category} 类别摘要...")
            
            # 准备文章文本（最多取前20篇）
            sample_articles = articles[:20]
            articles_text = "\n\n".join([
                f"【{i+1}】{a.get('title', 'N/A')}\n{a.get('description', 'N/A')}"
                for i, a in enumerate(sample_articles)
            ])
            
            # 使用双语生成（一次调用，节省成本）
            bilingual = self.translator.generate_bilingual_summary(
                articles_text, 
                target_lang=target_lang
            )
            
            # 添加到中文报告
            zh_report += f"## {category_names[category]['zh']}\n\n"
            zh_report += f"*本周共{len(articles)}条新闻*\n\n"
            if bilingual["zh"]:
                zh_report += bilingual["zh"] + "\n\n"
            else:
                zh_report += "（摘要生成失败）\n\n"
            
            # 添加到目标语言报告
            target_report += f"## {category_names[category][target_lang]}\n\n"
            target_report += f"*{len(articles)} noticias esta semana*\n\n"
            if bilingual.get(target_lang):
                target_report += bilingual[target_lang] + "\n\n"
            else:
                target_report += "(Resumen no disponible)\n\n"
        
        # 生成合并的双语报告
        combined_report = f"# 稳定币行业周报 / {lang_names[target_lang]['title']}\n\n"
        combined_report += f"**{year}年第{week_num}周 / Semana {week_num}, {year}**\n\n"
        combined_report += "---\n\n"
        
        for category, articles in articles_by_category.items():
            if not articles:
                continue
            
            combined_report += f"## {category_names[category]['zh']} / {category_names[category][target_lang]}\n\n"
            
            # 准备文章文本
            sample_articles = articles[:20]
            articles_text = "\n\n".join([
                f"【{i+1}】{a.get('title', 'N/A')}\n{a.get('description', 'N/A')}"
                for i, a in enumerate(sample_articles)
            ])
            
            bilingual = self.translator.generate_bilingual_summary(
                articles_text, 
                target_lang=target_lang
            )
            
            combined_report += "### 中文\n\n"
            combined_report += bilingual["zh"] + "\n\n"
            
            combined_report += f"### {lang_names[target_lang]['name']}\n\n"
            combined_report += bilingual.get(target_lang, "") + "\n\n"
            combined_report += "---\n\n"
        
        return {
            "zh": zh_report,
            target_lang: target_report,
            "combined": combined_report
        }
    
    def save_weekly_report(
        self, 
        reports: Dict[str, str], 
        target_lang: str = "es",
        output_dir: str = "reports/weekly"
    ):
        """保存周报到文件"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        week_num = datetime.now().isocalendar()[1]
        year = datetime.now().year
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # 保存中文版
        zh_file = f"{output_dir}/weekly_zh_{year}_W{week_num:02d}_{date_str}.md"
        with open(zh_file, 'w', encoding='utf-8') as f:
            f.write(reports["zh"])
        print(f"✅ 已保存中文版: {zh_file}")
        
        # 保存目标语言版
        target_file = f"{output_dir}/weekly_{target_lang}_{year}_W{week_num:02d}_{date_str}.md"
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(reports[target_lang])
        print(f"✅ 已保存{target_lang.upper()}版: {target_file}")
        
        # 保存双语合并版
        combined_file = f"{output_dir}/weekly_bilingual_{year}_W{week_num:02d}_{date_str}.md"
        with open(combined_file, 'w', encoding='utf-8') as f:
            f.write(reports["combined"])
        print(f"✅ 已保存双语版: {combined_file}")
        
        return {
            "zh": zh_file,
            target_lang: target_file,
            "combined": combined_file
        }