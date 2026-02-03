# Stablecoin Intel - Claude Code 项目配置

## 项目概述
稳定币行业情报收集和分析系统，自动收集 Twitter、RSS、新闻等数据源，进行 AI 分类和报告生成。

## 每日提醒

### 10:30 AM SGT - 检查日报生成
每天早上 10:30 运行 `/check-daily` 检查今日日报是否成功生成。

工作流时间表：
- 10:00 AM SGT - Daily Data Collection 运行
- 10:30 AM SGT - 检查日报是否生成成功
- 如果失败，诊断原因并修复

## 可用命令 (Skills)

| 命令 | 说明 |
|------|------|
| `/daily-report` | 手动生成今日日报 |
| `/check-daily` | 检查今日日报状态和诊断问题 |
| `/add-competitor` | 添加新的竞争对手到监控列表 |
| `/add-rss` | 添加新的 RSS 订阅源 |
| `/test-sources` | 测试所有数据源的连通性 |

## 关键文件

### 配置
- `config/keywords.json` - 关键词、竞对、客户配置
- `.env` - API 密钥（本地）
- GitHub Secrets - 生产环境密钥

### 数据收集
- `scripts/daily_job_v2.py` - 每日数据收集主脚本
- `src/collectors/twitter_api_io.py` - Twitter 数据收集
- `src/collectors/rss_collector.py` - RSS 订阅收集
- `src/processors/business_classifier.py` - AI 业务分类

### 工作流
- `.github/workflows/daily-collect.yml` - 每日收集 (10:00 AM SGT)
- `.github/workflows/weekly-report.yml` - 周报生成 (周五 23:00 SGT)
- `.github/workflows/deploy-pages.yml` - 网站部署

### 输出
- `data/processed/categorized_news_YYYY-MM-DD.json` - 分类后的每日数据
- `reports/daily/daily_brief_YYYY-MM-DD.md` - 每日日报
- `reports/weekly/` - 周报文件

## 常见问题排查

### 日报生成失败
1. 检查 GitHub Actions 运行日志
2. 常见原因：
   - Twitter API 时间格式解析错误 → 已修复 `_parse_twitter_time()`
   - User tweets API 结构变化 → 已修复 `get_user_tweets()`
   - OpenAI API 超时 → 检查网络和配额

### 周报内容缺失
1. 确认 `weekly_aggregator.py` 读取正确的文件格式
2. 检查周数计算是否正确（使用 Python isocalendar）

### 客户信息监控缺失
1. 检查 `business_classifier.py` 的分类逻辑
2. 确保客户 Twitter 账号在配置中正确设置
