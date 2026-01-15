# scripts/daily_job.py

"""
每日自动任务：收集新闻 → 分类 → 生成报告
"""

import os
import sys
import json
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import OPENAI_API_KEY
from src.processors.batch_summarizer import BatchSummarizer
from src.processors.smart_classifier import SmartClassifier
from src.processors.sentiment_analyzer import SentimentAnalyzer
from src.processors.trend_analyzer import TrendAnalyzer


class DailyJob:
    """每日自动任务"""
    
    def __init__(self):
        # 设置日志
        self.setup_logging()
        
        # 初始化处理器
        self.logger.info("初始化处理器...")
        self.summarizer = BatchSummarizer(OPENAI_API_KEY)
        self.classifier = SmartClassifier(OPENAI_API_KEY)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        
        # 日期
        self.today = datetime.now().strftime('%Y-%m-%d')
        
        self.logger.info(f"每日任务初始化完成 - {self.today}")
    
    def setup_logging(self):
        """配置日志"""
        os.makedirs('logs', exist_ok=True)
        
        log_file = f'logs/daily_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def load_daily_data(self) -> dict:
        """
        加载今天的数据
        
        Returns:
            {"policy": [...], "company": [...], "funding": [...]}
        """
        
        data_file = f'data/processed/categorized_news_{self.today}.json'
        
        if not os.path.exists(data_file):
            self.logger.warning(f"今日数据文件不存在: {data_file}")
            self.logger.info("尝试加载最新数据...")
            
            # 查找最新的数据文件
            processed_dir = 'data/processed'
            if os.path.exists(processed_dir):
                files = [f for f in os.listdir(processed_dir) if f.startswith('categorized_news_')]
                if files:
                    latest_file = sorted(files)[-1]
                    data_file = os.path.join(processed_dir, latest_file)
                    self.logger.info(f"使用最新数据: {latest_file}")
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total = sum(len(articles) for articles in data.values())
            self.logger.info(f"成功加载数据: {total} 篇文章")
            
            return data
            
        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")
            return {"policy": [], "company": [], "funding": []}
    
    def classify_articles(self, articles_by_category: dict) -> list:
        """
        AI分类所有文章
        
        Returns:
            分类结果列表
        """
        
        all_articles = []
        for category, articles in articles_by_category.items():
            all_articles.extend(articles)
        
        if not all_articles:
            self.logger.warning("没有文章需要分类")
            return []
        
        self.logger.info(f"开始AI分类 {len(all_articles)} 篇文章...")
        
        try:
            classified = self.classifier.batch_classify(all_articles, max_batch_size=10)
            self.logger.info(f"分类完成: {len(classified)} 篇")
            return classified
            
        except Exception as e:
            self.logger.error(f"AI分类失败: {e}")
            return []
    
    def analyze_sentiment(self, articles: list) -> dict:
        """情感分析"""
        
        self.logger.info("开始情感分析...")
        
        try:
            # 提取原始文章（从分类结果中）
            raw_articles = [a.get("article", a) for a in articles]
            sentiment = self.sentiment_analyzer.analyze_batch(raw_articles)
            
            self.logger.info(f"情感分析完成: {sentiment['overall_sentiment']}")
            return sentiment
            
        except Exception as e:
            self.logger.error(f"情感分析失败: {e}")
            return {}
    
    def generate_daily_report(self, articles_by_category: dict, classified_articles: list) -> str:
        """生成每日报告"""
        
        self.logger.info("生成每日报告...")
        
        try:
            report = self.summarizer.generate_daily_report(articles_by_category)
            
            # 保存报告
            os.makedirs('reports/daily', exist_ok=True)
            report_file = f'reports/daily/daily_brief_{self.today}.md'
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.logger.info(f"报告已保存: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"生成报告失败: {e}")
            return None
    
    def generate_trend_analysis(self, classified_articles: list) -> str:
        """生成趋势分析"""
        
        self.logger.info("生成趋势分析...")
        
        try:
            report = self.trend_analyzer.generate_trend_report(classified_articles)
            
            # 保存报告
            os.makedirs('reports/trends', exist_ok=True)
            trend_file = f'reports/trends/trend_{self.today}.md'
            
            with open(trend_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.logger.info(f"趋势分析已保存: {trend_file}")
            return trend_file
            
        except Exception as e:
            self.logger.error(f"趋势分析失败: {e}")
            return None
    
    def save_classified_data(self, classified_articles: list):
        """保存分类后的数据（供后续分析）"""
        
        os.makedirs('data/classified', exist_ok=True)
        output_file = f'data/classified/classified_{self.today}.json'
        
        try:
            # 简化数据结构
            simplified = []
            for article in classified_articles:
                simplified.append({
                    "title": article.get("article", {}).get("title", ""),
                    "category": article.get("primary_category", "unknown"),
                    "tags": article.get("tags", []),
                    "importance": article.get("importance", 5),
                    "confidence": article.get("confidence", 0.5)
                })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(simplified, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"分类数据已保存: {output_file}")
            
        except Exception as e:
            self.logger.error(f"保存分类数据失败: {e}")
    
    def run(self):
        """运行完整的每日任务"""
        
        self.logger.info("="*60)
        self.logger.info("开始每日任务")
        self.logger.info("="*60)
        
        start_time = datetime.now()
        
        try:
            # 1. 加载数据
            self.logger.info("\n步骤1: 加载今日数据")
            articles_by_category = self.load_daily_data()
            
            total_articles = sum(len(articles) for articles in articles_by_category.values())
            
            if total_articles == 0:
                self.logger.warning("今日无新闻数据，任务结束")
                return
            
            # 2. AI分类
            self.logger.info("\n步骤2: AI智能分类")
            classified_articles = self.classify_articles(articles_by_category)
            
            # 3. 情感分析
            self.logger.info("\n步骤3: 情感分析")
            sentiment = self.analyze_sentiment(classified_articles)
            
            # 4. 生成日报
            self.logger.info("\n步骤4: 生成每日报告")
            report_file = self.generate_daily_report(articles_by_category, classified_articles)
            
            # 5. 生成趋势分析
            self.logger.info("\n步骤5: 生成趋势分析")
            trend_file = self.generate_trend_analysis(classified_articles)
            
            # 6. 保存分类数据
            self.logger.info("\n步骤6: 保存分类数据")
            self.save_classified_data(classified_articles)
            
            # 统计信息
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.info("\n" + "="*60)
            self.logger.info("每日任务完成")
            self.logger.info("="*60)
            self.logger.info(f"处理文章数: {total_articles}")
            self.logger.info(f"耗时: {duration:.1f}秒")
            self.logger.info(f"日报: {report_file}")
            self.logger.info(f"趋势: {trend_file}")
            
            if sentiment:
                self.logger.info(f"市场情绪: {sentiment.get('overall_sentiment', 'N/A')}")
            
            # 成本估算
            api_calls = (total_articles + 9) // 10  # 批量分类
            estimated_cost = api_calls * 0.0003
            self.logger.info(f"预计成本: ${estimated_cost:.4f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"每日任务执行失败: {e}", exc_info=True)
            return False


def main():
    """主函数"""
    job = DailyJob()
    success = job.run()
    
    if success:
        print("\n✅ 每日任务执行成功！")
        return 0
    else:
        print("\n❌ 每日任务执行失败，请查看日志")
        return 1


if __name__ == "__main__":
    exit(main())