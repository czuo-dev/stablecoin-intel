# scripts/weekly_job.py

"""
每周自动任务：生成双语周报
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import OPENAI_API_KEY
from src.processors.weekly_reporter import WeeklyReportGenerator


class WeeklyJob:
    """每周自动任务"""
    
    def __init__(self):
        # 设置日志
        self.setup_logging()
        
        # 初始化生成器
        self.logger.info("初始化周报生成器...")
        self.reporter = WeeklyReportGenerator(OPENAI_API_KEY)
        
        # 日期
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.week_num = datetime.now().isocalendar()[1]
        
        self.logger.info(f"周报任务初始化完成 - 第{self.week_num}周")
    
    def setup_logging(self):
        """配置日志"""
        os.makedirs('logs', exist_ok=True)
        
        log_file = f'logs/weekly_{datetime.now().strftime("%Y-W%V")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run(self, target_lang: str = "es"):
        """
        运行周报生成任务
        
        Args:
            target_lang: 目标语言（"es"西班牙语 / "en"英文）
        """
        
        self.logger.info("="*60)
        self.logger.info(f"开始周报生成任务 - 第{self.week_num}周")
        self.logger.info("="*60)
        
        start_time = datetime.now()
        
        try:
            # 1. 聚合本周数据
            self.logger.info("\n步骤1: 聚合本周数据")
            aggregated_data = self.reporter.aggregate_weekly_data()
            
            total_articles = sum(len(articles) for articles in aggregated_data.values())
            
            if total_articles == 0:
                self.logger.warning("本周无数据，任务结束")
                return False
            
            # 2. 生成双语周报
            self.logger.info(f"\n步骤2: 生成双语周报（中文+{target_lang.upper()}）")
            reports = self.reporter.generate_weekly_report(aggregated_data, target_lang)
            
            # 3. 保存周报
            self.logger.info("\n步骤3: 保存周报文件")
            files = self.reporter.save_weekly_report(reports, target_lang)
            
            # 统计信息
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.info("\n" + "="*60)
            self.logger.info("周报生成完成")
            self.logger.info("="*60)
            self.logger.info(f"处理文章数: {total_articles}")
            self.logger.info(f"耗时: {duration:.1f}秒")
            self.logger.info(f"中文版: {files['zh']}")
            self.logger.info(f"{target_lang.upper()}版: {files[target_lang]}")
            self.logger.info(f"双语版: {files['combined']}")
            
            # 成本估算
            api_calls = len([cat for cat, arts in aggregated_data.items() if arts])
            estimated_cost = api_calls * 0.002
            self.logger.info(f"预计成本: ${estimated_cost:.4f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"周报生成失败: {e}", exc_info=True)
            return False


def main():
    """主函数"""
    job = WeeklyJob()
    
    # 可以指定语言：es（西班牙语）或 en（英文）
    success = job.run(target_lang="es")
    
    if success:
        print("\n✅ 周报生成成功！")
        return 0
    else:
        print("\n❌ 周报生成失败，请查看日志")
        return 1


if __name__ == "__main__":
    exit(main())