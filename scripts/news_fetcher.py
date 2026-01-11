# 稳定币新闻抓取器
# 功能：从 NewsAPI 获取真实新闻
# 在文件开头添加导入
from database_manager import insert_articles_batch, get_database_stats

# =========================
# 修改保存函数
# =========================

def save_news_to_database(articles):
    """保存新闻到数据库"""
    print("\n" + "=" * 60)
    print("保存新闻到数据库")
    print("=" * 60)
    
    # 插入数据库
    count = insert_articles_batch(articles)
    
    # 显示数据库统计
    stats = get_database_stats()
    print(f"\n数据库现有记录: {stats['total']} 条")
    
    return count

# =========================
# 修改main函数
# =========================

def main():
    # ... 前面获取新闻的代码不变 ...
    
    # 过滤和分类
    filtered_news = filter_stablecoin_news(articles)
    classified_news = classify_news(filtered_news)
    
    # 保存到数据库（新方式）
    save_news_to_database(classified_news)
    
    # 可选：仍然保存一份JSON备份
    # save_json_backup(classified_news)
    
    print("\n✅ 完成！新闻已保存到数据库")
import requests
import json
import os
from datetime import datetime, timedelta

# =========================
# 配置
# =========================

# 读取 API Key
def load_api_key():
    """从配置文件读取 API Key"""
    try:
        with open("config/api_keys.txt", "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    if "NewsAPI_Key" in line:
                        return line.split("=")[1].strip()
        print("❌ 未找到 NewsAPI_Key")
        return None
    except FileNotFoundError:
        print("❌ 配置文件不存在: config/api_keys.txt")
        print("请先创建配置文件并添加 API Key")
        return None
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        return None

# NewsAPI 配置
NEWS_API_URL = "https://newsapi.org/v2/everything"
API_KEY = load_api_key()

# 稳定币相关的搜索关键词
SEARCH_KEYWORDS = [
    "stablecoin",
    "USDC", 
    "USDT",
    "Tether",
    "Circle",
    "stablecoin regulation"
]

# =========================
# 核心功能：获取新闻
# =========================

def fetch_news_from_api(keyword, days=7, max_results=20):
    """
    从 NewsAPI 获取新闻
    
    参数:
        keyword: 搜索关键词
        days: 获取最近几天的新闻
        max_results: 最多返回多少条
    """
    if not API_KEY:
        print("❌ API Key 未配置")
        return []
    
    # 计算日期范围
    today = datetime.now()
    from_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # 构建请求参数
    params = {
        "q": keyword,
        "from": from_date,
        "sortBy": "publishedAt",  # 按发布时间排序
        "language": "en",  # 英文新闻
        "pageSize": max_results,
        "apiKey": API_KEY
    }
    
    try:
        print(f"正在搜索关键词: {keyword}")
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data["status"] == "ok":
            articles = data["articles"]
            print(f"✅ 找到 {len(articles)} 条新闻")
            return articles
        else:
            print(f"❌ API 返回错误: {data.get('message', '未知错误')}")
            return []
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return []
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return []

def fetch_all_stablecoin_news(days=7):
    """获取所有稳定币相关新闻"""
    all_news = []
    seen_urls = set()  # 用于去重
    
    print("\n" + "=" * 60)
    print("开始抓取稳定币新闻")
    print("=" * 60)
    
    for keyword in SEARCH_KEYWORDS:
        articles = fetch_news_from_api(keyword, days=days, max_results=10)
        
        for article in articles:
            url = article.get("url")
            
            # 去重
            if url and url not in seen_urls:
                seen_urls.add(url)
                
                # 转换为我们的格式
                news_item = {
                    "title": article.get("title", "无标题"),
                    "source": article.get("source", {}).get("name", "未知来源"),
                    "url": url,
                    "published_at": article.get("publishedAt", ""),
                    "description": article.get("description", ""),
                    "author": article.get("author", "未知"),
                    "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                all_news.append(news_item)
    
    print(f"\n✅ 共获取 {len(all_news)} 条不重复的新闻")
    return all_news

# =========================
# 保存功能
# =========================

def save_raw_news(news_list):
    """保存原始新闻数据"""
    os.makedirs("data/raw", exist_ok=True)
    
    filename = f"data/raw/news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        print(f"✅ 原始数据已保存到 {filename}")
        return filename
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return None

def save_to_daily_log(news_list):
    """追加到每日日志"""
    os.makedirs("data", exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"data/news_log_{today}.txt"
    
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"\n抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            
            for i, news in enumerate(news_list, 1):
                f.write(f"\n{i}. {news['title']}\n")
                f.write(f"   来源: {news['source']}\n")
                f.write(f"   链接: {news['url']}\n")
                f.write(f"   时间: {news['published_at']}\n")
        
        print(f"✅ 已追加到每日日志 {filename}")
        return filename
    except Exception as e:
        print(f"❌ 保存日志失败: {e}")
        return None

# =========================
# 显示功能
# =========================

def display_news(news_list, max_show=10):
    """显示新闻列表"""
    print("\n" + "=" * 60)
    print(f"新闻列表（共 {len(news_list)} 条）")
    print("=" * 60)
    
    for i, news in enumerate(news_list[:max_show], 1):
        print(f"\n{i}. {news['title']}")
        print(f"   来源: {news['source']}")
        print(f"   发布: {news['published_at'][:10]}")  # 只显示日期
        print(f"   链接: {news['url'][:60]}...")
        
        # 显示摘要（如果有）
        if news.get('description'):
            desc = news['description'][:100]
            print(f"   摘要: {desc}...")
    
    if len(news_list) > max_show:
        print(f"\n... 还有 {len(news_list) - max_show} 条新闻")

# =========================
# 主程序
# =========================

def main():
    print("=" * 60)
    print("稳定币新闻抓取器")
    print("=" * 60)
    
    # 检查 API Key
    if not API_KEY:
        print("\n❌ 无法运行，请先配置 API Key:")
        print("1. 访问 https://newsapi.org/register")
        print("2. 注册并获取 API Key")
        print("3. 保存到 config/api_keys.txt")
        return
    
    print(f"\n✅ API Key 已配置")
    print(f"搜索关键词: {', '.join(SEARCH_KEYWORDS)}")
    
    # 获取新闻（最近7天）
    news_list = fetch_all_stablecoin_news(days=7)
    
    if news_list:
        # 显示新闻
        display_news(news_list, max_show=10)
        
        # 保存数据
        save_raw_news(news_list)
        save_to_daily_log(news_list)
        
        print("\n" + "=" * 60)
        print("抓取完成！")
        print("=" * 60)
        print(f"📊 本次抓取: {len(news_list)} 条新闻")
        print(f"📁 原始数据: data/raw/")
        print(f"📝 每日日志: data/news_log_{datetime.now().strftime('%Y-%m-%d')}.txt")
    else:
        print("\n❌ 未获取到任何新闻")

if __name__ == "__main__":
    main()