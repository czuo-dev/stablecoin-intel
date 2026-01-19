# scripts/daily_job_with_logging.py

"""
带日志记录的每日任务
"""

import json
import logging
import os
import sys
import traceback
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.collectors.twitter_filter import TwitterFilter
from src.collectors.data_normalizer import DataNormalizer

# 配置日志
def setup_logging():
    """配置日志系统"""
    
    # 创建日志目录
    os.makedirs('logs', exist_ok=True)
    
    # 日志文件名包含日期
    date_str = datetime.now().strftime('%Y-%m-%d')
    log_file = f'logs/daily_job_{date_str}.log'
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)  # 同时输出到屏幕
        ]
    )
    
    return logging.getLogger(__name__)

def daily_news_collection():
    """每日新闻收集任务（带日志）"""
    
    logger = setup_logging()
    
    logger.info("=" * 70)
    logger.info(f"每日任务开始")
    logger.info("=" * 70)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # ===== Step 1: 加载模拟新闻数据 =====
        logger.info("Step 1: 加载模拟新闻数据...")
        
        raw_file = f'data/raw/newsapi_raw_{date_str}.json'
        
        if not os.path.exists(raw_file):
            logger.warning(f"模拟数据不存在: {raw_file}")
            logger.info("生成模拟数据...")
            
            import subprocess
            result = subprocess.run(
                ['python', 'mock_news_collector.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"生成模拟数据失败: {result.stderr}")
                raise Exception("模拟数据生成失败")
            
            logger.info("模拟数据生成成功")
        
        # 加载数据
        with open(raw_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        logger.info(f"成功加载 {len(articles)} 篇新闻")
        
        # ===== Step 2: 分类新闻 =====
        logger.info("Step 2: 分类新闻...")
        
        categorized_news = {
            'policy': [],
            'company': [],
            'funding': [],
            'market': [],
            'general': []
        }
        
        for article in articles:
            categories = article.get('categories', ['general'])
            main_category = categories[0]
            
            if main_category in categorized_news:
                categorized_news[main_category].append(article)
            else:
                categorized_news['general'].append(article)
        
        # 保存分类数据
        os.makedirs('data/processed', exist_ok=True)
        categorized_file = f'data/processed/categorized_news_{date_str}.json'
        
        with open(categorized_file, 'w', encoding='utf-8') as f:
            json.dump(categorized_news, f, indent=2, ensure_ascii=False)
        
        logger.info(f"分类完成: {categorized_file}")
        
        # 记录分布
        for category, items in categorized_news.items():
            if items:
                logger.info(f"  {category}: {len(items)} 篇")
        
        # ===== Step 3: 数据整合 =====
        logger.info("Step 3: 整合数据...")
        
        # 加载Twitter数据（如果存在）
        twitter_file = f'data/raw/twitter_data_{date_str}.json'
        enriched_tweets = []
        
        if os.path.exists(twitter_file):
            with open(twitter_file, 'r', encoding='utf-8') as f:
                raw_tweets = json.load(f)
            logger.info(f"找到Twitter数据: {len(raw_tweets)} 条")
            
            # 筛选
            filter_obj = TwitterFilter()
            filtered_tweets = filter_obj.filter_tweets(raw_tweets, min_score=60)
            enriched_tweets = [filter_obj.enrich_tweet_data(t) for t in filtered_tweets]
            logger.info(f"筛选后: {len(enriched_tweets)} 条")
        else:
            logger.info("未找到Twitter数据，跳过")
        
        # 标准化
        normalizer = DataNormalizer()
        normalized_tweets = [normalizer.normalize_tweet(t) for t in enriched_tweets]
        
        all_news = []
        for articles_list in categorized_news.values():
            all_news.extend(articles_list)
        normalized_news = [normalizer.normalize_news(n) for n in all_news]
        
        logger.info(f"标准化: Twitter {len(normalized_tweets)} 条, News {len(normalized_news)} 条")
        
        # 合并去重
        all_items = normalized_tweets + normalized_news
        merged_items = normalizer.merge_and_deduplicate(all_items)
        
        logger.info(f"合并去重: {len(merged_items)} 条")
        
        # 保存整合数据
        integrated_data = {
            'date': date_str,
            'total_items': len(merged_items),
            'by_source': {
                'twitter': len([i for i in merged_items if i['source_type'] == 'twitter']),
                'news': len([i for i in merged_items if i['source_type'] == 'news'])
            },
            'items': merged_items
        }
        
        integrated_file = f'data/processed/integrated_data_{date_str}.json'
        with open(integrated_file, 'w', encoding='utf-8') as f:
            json.dump(integrated_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"整合完成: {integrated_file}")
        
        # ===== 完成 =====
        logger.info("=" * 70)
        logger.info("✅ 每日任务完成")
        logger.info("=" * 70)
        logger.info(f"数据汇总:")
        logger.info(f"  新闻: {len(articles)} 篇")
        logger.info(f"  Twitter: {len(enriched_tweets)} 条")
        logger.info(f"  整合后: {len(merged_items)} 条")
        logger.info(f"输出文件:")
        logger.info(f"  - {raw_file}")
        logger.info(f"  - {categorized_file}")
        logger.info(f"  - {integrated_file}")
        
        return True
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"❌ 任务失败: {e}")
        logger.error("=" * 70)
        logger.error("错误详情:")
        logger.error(traceback.format_exc())
        
        return False

if __name__ == '__main__':
    success = daily_news_collection()
    sys.exit(0 if success else 1)