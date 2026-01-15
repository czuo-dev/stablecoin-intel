# scripts/scheduler.py

"""
定时调度器 - 管理所有定时任务

使用 schedule 库实现简单的定时任务
适合开发和测试环境
"""

import schedule
import time
import logging
from datetime import datetime
import subprocess
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Scheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.setup_logging()
        self.logger.info("调度器启动")
        self.logger.info("="*60)
    
    def setup_logging(self):
        """配置日志"""
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler('logs/scheduler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_daily_job(self):
        """运行每日任务"""
        self.logger.info("\n" + "🔔 触发每日任务")
        self.logger.info("-"*60)
        
        try:
            # 使用subprocess运行脚本（独立进程，更安全）
            result = subprocess.run(
                [sys.executable, 'scripts/daily_job.py'],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                self.logger.info("✅ 每日任务执行成功")
            else:
                self.logger.error(f"❌ 每日任务执行失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ 每日任务超时（超过5分钟）")
        except Exception as e:
            self.logger.error(f"❌ 每日任务执行异常: {e}")
    
    def run_weekly_job(self):
        """运行周报任务"""
        self.logger.info("\n" + "🔔 触发周报任务")
        self.logger.info("-"*60)
        
        try:
            result = subprocess.run(
                [sys.executable, 'scripts/weekly_job.py'],
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                self.logger.info("✅ 周报任务执行成功")
            else:
                self.logger.error(f"❌ 周报任务执行失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ 周报任务超时（超过10分钟）")
        except Exception as e:
            self.logger.error(f"❌ 周报任务执行异常: {e}")
    
    def setup_schedules(self):
        """配置定时任务"""
        
        # 每日任务：工作日早上9点
        schedule.every().monday.at("09:00").do(self.run_daily_job)
        schedule.every().tuesday.at("09:00").do(self.run_daily_job)
        schedule.every().wednesday.at("09:00").do(self.run_daily_job)
        schedule.every().thursday.at("09:00").do(self.run_daily_job)
        schedule.every().friday.at("09:00").do(self.run_daily_job)
        
        # 周报任务：每周一早上10点
        schedule.every().monday.at("10:00").do(self.run_weekly_job)
        
        self.logger.info("\n📅 定时任务已配置:")
        self.logger.info("  - 每日任务: 周一至周五 09:00")
        self.logger.info("  - 周报任务: 每周一 10:00")
        self.logger.info("\n调度器正在运行...")
    
    def run(self):
        """启动调度器（持续运行）"""
        
        self.setup_schedules()
        
        # 显示下次运行时间
        self.show_next_runs()
        
        # 持续运行
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            self.logger.info("\n\n调度器已停止（用户中断）")
        except Exception as e:
            self.logger.error(f"\n\n调度器异常: {e}", exc_info=True)
    
    def show_next_runs(self):
        """显示下次运行时间"""
        self.logger.info("\n⏰ 下次运行时间:")
        
        jobs = schedule.get_jobs()
        for job in jobs:
            next_run = job.next_run
            if next_run:
                self.logger.info(f"  - {next_run.strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """主函数"""
    
    print("\n🤖 稳定币情报Agent - 定时调度器")
    print("="*60)
    print("\n按 Ctrl+C 停止调度器\n")
    
    scheduler = Scheduler()
    scheduler.run()


if __name__ == "__main__":
    main()