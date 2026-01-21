# weekly_report.py

import json
import os
from datetime import datetime, timedelta
from collections import Counter

# =========================
# 配置
# =========================

REPORT_DIR = "reports"

# =========================
# 数据加载（修复版）
# =========================

def load_all_news():
    """加载所有新闻 - 修复版"""
    all_news = []
    db_files = [
        "data/news_system_db.json",
        "data/news_database.json"
    ]
    
    for db_file in db_files:
        if not os.path.exists(db_file):
            print(f"⚠️  文件不存在: {db_file}")
            continue
        
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 处理不同的数据格式
            if isinstance(data, list):
                # 如果是数组，直接添加
                all_news.extend(data)
                print(f"✅ 加载 {db_file}: {len(data)} 条")
            
            elif isinstance(data, dict):
                # 如果是对象，尝试提取 articles
                if 'articles' in data:
                    all_news.extend(data['articles'])
                    print(f"✅ 加载 {db_file}: {len(data['articles'])} 条")
                else:
                    # 如果对象本身就是一条新闻
                    all_news.append(data)
                    print(f"✅ 加载 {db_file}: 1 条")
        
        except json.JSONDecodeError as e:
            print(f"❌ {db_file} JSON格式错误: {e}")
        except Exception as e:
            print(f"❌ {db_file} 加载失败: {e}")
    
    print(f"\n📊 总计加载: {len(all_news)} 条新闻\n")
    return all_news

def normalize_news_item(news):
    """标准化新闻数据格式"""
    try:
        return {
            'title': news.get('title', '无标题'),
            'source': news.get('source', '未知'),
            'url': news.get('url', ''),
            'date': news.get('date', news.get('published_at', ''))[:10],
            'category': news.get('category', '未分类'),
            'keywords': news.get('keywords', []),
            'description': news.get('description', '')
        }
    except Exception as e:
        print(f"⚠️  标准化数据时出错: {e}")
        return None

def filter_by_week(news_list):
    """筛选本周的新闻 - 修复版"""
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())  # 本周一
    
    print(f"📅 筛选本周新闻（{week_start.strftime('%Y-%m-%d')} 至今）\n")
    
    weekly_news = []
    error_count = 0
    
    for news in news_list:
        try:
            # 标准化数据
            normalized = normalize_news_item(news)
            if not normalized:
                error_count += 1
                continue
            
            # 提取日期
            date_str = normalized.get('date', '')
            if not date_str:
                error_count += 1
                continue
            
            # 解析日期（只取前10个字符 YYYY-MM-DD）
            date_str = date_str[:10]
            news_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # 判断是否在本周
            if news_date >= week_start:
                weekly_news.append(normalized)
        
        except ValueError as e:
            print(f"⚠️  日期格式错误: {news.get('date', 'N/A')} - {e}")
            error_count += 1
        except Exception as e:
            print(f"⚠️  处理新闻时出错: {e}")
            error_count += 1
    
    if error_count > 0:
        print(f"⚠️  跳过 {error_count} 条有问题的数据\n")
    
    print(f"✅ 本周新闻: {len(weekly_news)} 条\n")
    return weekly_news

# =========================
# 报告生成（保持原样）
# =========================

def generate_weekly_report(news_list):
    """生成周报内容"""
    if not news_list:
        return "# 本周暂无新闻数据"
    
    today = datetime.now()
    week_num = today.isocalendar()[1]
    
    # 统计
    stats = {
        "total": len(news_list),
        "categories": Counter(),
        "sources": Counter(),
        "keywords": Counter()
    }
    
    for news in news_list:
        stats["categories"][news.get("category", "未分类")] += 1
        stats["sources"][news.get("source", "未知")] += 1
        
        # 关键词统计
        keywords = news.get("keywords", [])
        for kw in keywords:
            stats["keywords"][kw] += 1
    
    # 生成 Markdown 报告
    report = []
    report.append(f"# 稳定币情报周报")
    report.append(f"")
    report.append(f"**报告周期**: {today.year} 年第 {week_num} 周")
    report.append(f"**生成时间**: {today.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"")
    report.append(f"---")
    report.append(f"")
    
    # 概览
    report.append(f"## 📊 本周概览")
    report.append(f"")
    report.append(f"- **新闻总数**: {stats['total']} 条")
    report.append(f"- **日均新闻**: {stats['total']/7:.1f} 条")
    report.append(f"")
    
    # 分类分布
    report.append(f"## 📂 分类分布")
    report.append(f"")
    for category, count in stats["categories"].most_common():
        percentage = (count / stats['total']) * 100
        report.append(f"- **{category}**: {count} 条 ({percentage:.1f}%)")
    report.append(f"")
    
    # 主要来源
    report.append(f"## 📰 主要来源")
    report.append(f"")
    for source, count in stats["sources"].most_common(10):
        report.append(f"- **{source}**: {count} 条")
    report.append(f"")
    
    # 热点关键词
    if stats["keywords"]:
        report.append(f"## 🔥 热点关键词")
        report.append(f"")
        for keyword, count in stats["keywords"].most_common(10):
            report.append(f"- **{keyword}**: 提及 {count} 次")
        report.append(f"")
    
    # 重点新闻（按分类）
    report.append(f"## 📌 本周重点新闻")
    report.append(f"")
    
    # 按分类整理
    by_category = {}
    for news in news_list:
        cat = news.get("category", "未分类")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(news)
    
    for category, articles in by_category.items():
        if articles:
            report.append(f"### {category}")
            report.append(f"")
            
            # 只显示前5条
            for news in articles[:5]:
                title = news.get("title", "无标题")
                source = news.get("source", "未知")
                date = news.get("date", "")
                url = news.get("url", "")
                
                report.append(f"#### {title}")
                report.append(f"")
                report.append(f"- **来源**: {source}")
                report.append(f"- **日期**: {date}")
                if url:
                    report.append(f"- **链接**: [{url}]({url})")
                report.append(f"")
            
            if len(articles) > 5:
                report.append(f"*...还有 {len(articles)-5} 条新闻*")
                report.append(f"")
    
    # 结尾
    report.append(f"---")
    report.append(f"")
    report.append(f"*本报告由稳定币情报系统自动生成*")
    
    return "\n".join(report)

# =========================
# 保存报告
# =========================

def save_report(report_content):
    """保存周报到文件"""
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    today = datetime.now()
    filename = f"{REPORT_DIR}/weekly_report_{today.strftime('%Y_W%W')}.md"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"✅ 周报已保存: {filename}")
        return filename
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return None

# =========================
# 主程序
# =========================

def main():
    print("=" * 60)
    print("稳定币情报周报生成器")
    print("=" * 60 + "\n")
    
    # 加载数据
    print("📂 加载数据...")
    all_news = load_all_news()
    
    if not all_news:
        print("❌ 没有数据")
        return
    
    # 筛选本周
    print("🔍 筛选本周新闻...")
    weekly_news = filter_by_week(all_news)
    
    if not weekly_news:
        print("⚠️  本周暂无新闻")
        # 仍然生成报告，但是空的
    
    # 生成报告
    print("📝 生成周报...")
    report = generate_weekly_report(weekly_news)
    
    # 保存
    filename = save_report(report)
    
    if filename:
        # 显示预览
        print("\n" + "=" * 60)
        print("报告预览（前20行）")
        print("=" * 60)
        lines = report.split("\n")
        for line in lines[:20]:
            print(line)
        
        if len(lines) > 20:
            print(f"\n... 还有 {len(lines)-20} 行")
        
        print("\n" + "=" * 60)
        print("周报生成完成！")
        print("=" * 60)
        print(f"📄 查看完整报告: {filename}")

if __name__ == "__main__":
    main()