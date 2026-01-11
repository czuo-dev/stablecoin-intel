# 稳定币情报周报生成器
# 功能：自动生成 Markdown 格式的周报

import json
import os
from datetime import datetime, timedelta
from collections import Counter

# =========================
# 配置
# =========================

REPORT_DIR = "reports"

# =========================
# 数据加载（复用）
# =========================

def load_all_news():
    """加载所有新闻"""
    all_news = []
    db_files = ["data/news_system_db.json", "data/news_database.json"]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                with open(db_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_news.extend(data)
            except:
                pass
    
    return all_news

def filter_by_week(news_list):
    """筛选本周的新闻"""
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())  # 本周一
    
    weekly_news = []
    for news in news_list:
        date_str = news.get("date", news.get("published_at", ""))[:10]
        if date_str:
            try:
                news_date = datetime.strptime(date_str, "%Y-%m-%d")
                if news_date >= week_start:
                    weekly_news.append(news)
            except:
                pass
    
    return weekly_news

# =========================
# 报告生成
# =========================

def generate_weekly_report(news_list):
    """生成周报内容"""
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
        title = news.get("title", "")
        for word in ["Circle", "Tether", "USDC", "USDT", "MAS", "HKMA", "SEC"]:
            if word.lower() in title.lower():
                stats["keywords"][word] += 1
    
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
    for source, count in stats["sources"].most_common(5):
        report.append(f"- **{source}**: {count} 条")
    report.append(f"")
    
    # 热点实体
    report.append(f"## 🔥 热点实体")
    report.append(f"")
    if stats["keywords"]:
        for keyword, count in stats["keywords"].most_common(10):
            report.append(f"- **{keyword}**: 提及 {count} 次")
    else:
        report.append(f"暂无数据")
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
    
    for category in ["📋 政策监管", "💰 融资并购", "🏢 公司动态"]:
        if category in by_category:
            report.append(f"### {category}")
            report.append(f"")
            
            # 只显示前5条
            for news in by_category[category][:5]:
                title = news.get("title", "无标题")
                source = news.get("source", "未知")
                date = news.get("date", news.get("published_at", ""))[:10]
                url = news.get("url", news.get("link", ""))
                
                report.append(f"#### {title}")
                report.append(f"")
                report.append(f"- **来源**: {source}")
                report.append(f"- **日期**: {date}")
                if url:
                    report.append(f"- **链接**: [{url}]({url})")
                report.append(f"")
            
            if len(by_category[category]) > 5:
                report.append(f"*...还有 {len(by_category[category])-5} 条新闻*")
                report.append(f"")
    
    # 趋势分析
    report.append(f"## 📈 趋势分析")
    report.append(f"")
    
    # 简单的趋势判断
    if stats["categories"]:
        top_cat = stats["categories"].most_common(1)[0]
        report.append(f"- 本周 **{top_cat[0]}** 类新闻最为活跃")
    
    if stats["keywords"]:
        top_kw = stats["keywords"].most_common(1)[0]
        report.append(f"- **{top_kw[0]}** 是本周最热门的话题")
    
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
    print("=" * 60)
    
    # 加载数据
    print("\n加载数据...")
    all_news = load_all_news()
    
    if not all_news:
        print("❌ 没有数据")
        return
    
    # 筛选本周
    print("筛选本周新闻...")
    weekly_news = filter_by_week(all_news)
    print(f"✅ 本周新闻: {len(weekly_news)} 条")
    
    if not weekly_news:
        print("⚠️  本周暂无新闻")
        return
    
    # 生成报告
    print("\n生成周报...")
    report = generate_weekly_report(weekly_news)
    
    # 保存
    filename = save_report(report)
    
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