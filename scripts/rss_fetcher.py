# RSS 新闻订阅器
# 功能：从多个 RSS 源获取稳定币新闻

import feedparser
import json
import os
from datetime import datetime

# =========================
# RSS 源配置
# =========================

RSS_FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss",
    "The Block": "https://www.theblock.co/rss.xml",
    "Decrypt": "https://decrypt.co/feed",
}

# 稳定币关键词（用于过滤）
STABLECOIN_KEYWORDS = [
    "stablecoin", "USDC", "USDT", "Tether", "Circle", 
    "DAI", "BUSD", "PYUSD", "PayPal", "稳定币"
]

# =========================
# 核心功能：获取 RSS 内容
# =========================

def fetch_rss_feed(feed_name, feed_url):
    """
    从单个 RSS 源获取内容
    
    参数:
        feed_name: RSS 源名称
        feed_url: RSS 源地址
    """
    try:
        print(f"正在获取 {feed_name}...")
        
        # 解析 RSS
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:  # bozo = RSS 格式有问题
            print(f"  ⚠️  RSS 格式警告")
        
        entries = feed.entries
        print(f"  ✅ 获取到 {len(entries)} 条内容")
        
        # 转换为统一格式
        news_list = []
        for entry in entries:
            news_item = {
                "title": entry.get("title", "无标题"),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "source": feed_name,
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            news_list.append(news_item)
        
        return news_list
        
    except Exception as e:
        print(f"  ❌ 获取失败: {e}")
        return []

def fetch_all_rss_feeds():
    """从所有 RSS 源获取内容"""
    all_news = []
    
    print("\n" + "=" * 60)
    print("开始获取 RSS 订阅")
    print("=" * 60)
    
    for feed_name, feed_url in RSS_FEEDS.items():
        news_list = fetch_rss_feed(feed_name, feed_url)
        all_news.extend(news_list)
    
    print(f"\n✅ 共获取 {len(all_news)} 条内容")
    return all_news

# =========================
# 过滤功能：只保留稳定币相关
# =========================

def filter_stablecoin_news(news_list):
    """过滤出包含稳定币关键词的新闻"""
    filtered = []
    
    print("\n" + "=" * 60)
    print("过滤稳定币相关新闻")
    print("=" * 60)
    
    for news in news_list:
        title = news["title"].lower()
        summary = news.get("summary", "").lower()
        
        # 检查标题或摘要是否包含关键词
        is_relevant = False
        matched_keywords = []
        
        for keyword in STABLECOIN_KEYWORDS:
            if keyword.lower() in title or keyword.lower() in summary:
                is_relevant = True
                matched_keywords.append(keyword)
        
        if is_relevant:
            news["matched_keywords"] = matched_keywords
            filtered.append(news)
            print(f"  ✅ [{news['source']}] {news['title'][:50]}...")
    
    print(f"\n过滤结果: {len(filtered)}/{len(news_list)} 条相关新闻")
    return filtered

# =========================
# 去重功能
# =========================

def deduplicate_news(news_list):
    """根据链接去重"""
    seen_urls = set()
    unique_news = []
    
    for news in news_list:
        url = news.get("link", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_news.append(news)
    
    removed = len(news_list) - len(unique_news)
    if removed > 0:
        print(f"去重：移除 {removed} 条重复新闻")
    
    return unique_news

# =========================
# 保存功能
# =========================

def save_rss_news(news_list):
    """保存 RSS 新闻到文件"""
    os.makedirs("data/rss", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/rss/news_{timestamp}.json"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        print(f"✅ 数据已保存到 {filename}")
        return filename
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return None

def append_to_master_log(news_list):
    """追加到总日志"""
    os.makedirs("data", exist_ok=True)
    
    filename = "data/rss_master_log.json"
    
    try:
        # 加载现有日志
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                master_log = json.load(f)
        else:
            master_log = []
        
        # 追加新数据（带时间戳）
        log_entry = {
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(news_list),
            "news": news_list
        }
        master_log.append(log_entry)
        
        # 保存（只保留最近30次）
        if len(master_log) > 30:
            master_log = master_log[-30:]
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(master_log, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已追加到总日志 {filename}")
        return filename
    except Exception as e:
        print(f"❌ 追加日志失败: {e}")
        return None

# =========================
# 显示功能
# =========================

def display_rss_news(news_list, max_show=10):
    """显示 RSS 新闻"""
    print("\n" + "=" * 60)
    print(f"RSS 新闻列表（共 {len(news_list)} 条）")
    print("=" * 60)
    
    for i, news in enumerate(news_list[:max_show], 1):
        print(f"\n{i}. {news['title']}")
        print(f"   来源: {news['source']}")
        print(f"   发布: {news.get('published', '未知')}")
        print(f"   链接: {news['link'][:60]}...")
        
        # 显示匹配的关键词
        if news.get("matched_keywords"):
            keywords = ", ".join(news["matched_keywords"][:3])
            print(f"   关键词: {keywords}")
    
    if len(news_list) > max_show:
        print(f"\n... 还有 {len(news_list) - max_show} 条")

# =========================
# 主程序
# =========================

def main():
    print("=" * 60)
    print("RSS 稳定币新闻订阅器")
    print("=" * 60)
    
    print(f"\n订阅源: {len(RSS_FEEDS)} 个")
    for name in RSS_FEEDS.keys():
        print(f"  - {name}")
    
    # 步骤1：获取所有 RSS 内容
    all_news = fetch_all_rss_feeds()
    
    if not all_news:
        print("\n❌ 未获取到任何内容")
        return
    
    # 步骤2：过滤稳定币相关
    stablecoin_news = filter_stablecoin_news(all_news)
    
    if not stablecoin_news:
        print("\n⚠️  未找到稳定币相关新闻")
        return
    
    # 步骤3：去重
    unique_news = deduplicate_news(stablecoin_news)
    
    # 步骤4：显示
    display_rss_news(unique_news, max_show=10)
    
    # 步骤5：保存
    save_rss_news(unique_news)
    append_to_master_log(unique_news)
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print(f"📊 本次获取: {len(unique_news)} 条相关新闻")
    print(f"📁 数据保存: data/rss/")

if __name__ == "__main__":
    main()