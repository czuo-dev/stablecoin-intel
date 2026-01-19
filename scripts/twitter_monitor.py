# scripts/twitter_monitor.py

"""
Twitter监控任务
每小时运行一次，收集最新推文
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    TWITTER_BEARER_TOKEN,
    TWITTER_MONITORED_ACCOUNTS,
    TWITTER_MONITORED_KEYWORDS
)
from src.collectors.twitter_collector import TwitterCollector


class TwitterMonitorJob:
    """Twitter监控任务"""
    
    def __init__(self):
        self.setup_logging()
        
        self.logger.info("初始化Twitter监控器...")
        self.collector = TwitterCollector(
            bearer_token=TWITTER_BEARER_TOKEN,
            monitored_accounts=TWITTER_MONITORED_ACCOUNTS,
            monitored_keywords=TWITTER_MONITORED_KEYWORDS
        )
        
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.logger.info(f"Twitter监控任务初始化完成 - {self.today}")
    
    def setup_logging(self):
        """配置日志"""
        os.makedirs('logs', exist_ok=True)
        
        log_file = f'logs/twitter_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run(self, hours: int = 1):
        """
        运行监控任务
        
        Args:
            hours: 收集最近多少小时的数据（默认1小时）
        """
        
        self.logger.info("="*60)
        self.logger.info(f"开始Twitter监控任务（最近{hours}小时）")
        self.logger.info("="*60)
        
        start_time = datetime.now()
        
        try:
            # 收集推文
            self.logger.info("\n步骤1: 收集推文")
            tweets_data = self.collector.collect_all(hours=hours)
            
            user_tweets = tweets_data['user_tweets']
            keyword_tweets = tweets_data['keyword_tweets']
            
            total_tweets = len(user_tweets) + len(keyword_tweets)
            
            if total_tweets == 0:
                self.logger.info(f"最近{hours}小时无新推文")
                return True
            
            # 保存原始数据
            self.logger.info("\n步骤2: 保存原始数据")
            output_file = self.collector.save_tweets(tweets_data)
            
            # 筛选高质量推文
            self.logger.info("\n步骤3: 筛选高质量推文")
            
            all_tweets = user_tweets + keyword_tweets
            high_quality = self.collector.filter_high_quality(
                all_tweets,
                min_likes=10,
                min_retweets=5
            )
            
            # 保存高质量推文（供后续处理）
            if high_quality:
                self.save_high_quality(high_quality)
            
            # 统计信息
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.info("\n" + "="*60)
            self.logger.info("Twitter监控任务完成")
            self.logger.info("="*60)
            self.logger.info(f"收集推文: {total_tweets}")
            self.logger.info(f"高质量推文: {len(high_quality)}")
            self.logger.info(f"耗时: {duration:.1f}秒")
            self.logger.info(f"数据文件: {output_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Twitter监控任务失败: {e}", exc_info=True)
            return False
    
    def save_high_quality(self, tweets: list):
        """保存高质量推文（供日报使用）"""
        
        import json
        
        os.makedirs('data/twitter/high_quality', exist_ok=True)
        
        output_file = f'data/twitter/high_quality/tweets_{self.today}.json'
        
        # 如果文件已存在，追加而不是覆盖
        existing_tweets = []
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_tweets = json.load(f)
            except:
                pass
        
        # 去重
        existing_ids = {t.get('id') for t in existing_tweets}
        new_tweets = [t for t in tweets if t.get('id') not in existing_ids]
        
        all_tweets = existing_tweets + new_tweets
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_tweets, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"高质量推文已保存: {output_file}")
        self.logger.info(f"  新增: {len(new_tweets)} 条")
        self.logger.info(f"  总计: {len(all_tweets)} 条")


def main():
    """主函数"""
    
    job = TwitterMonitorJob()
    
    # 每小时运行一次，收集最近1小时的数据
    success = job.run(hours=1)
    
    if success:
        print("\n✅ Twitter监控任务执行成功！")
        return 0
    else:
        print("\n❌ Twitter监控任务执行失败，请查看日志")
        return 1


if __name__ == "__main__":
    exit(main())