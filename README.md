# 稳定币行业情报系统 V2.2

> 自动化稳定币行业竞争情报收集、AI 分析与日报生成

## 功能特性

### 数据收集
- **Twitter 监控** - 追踪竞争对手、客户和行业 KOL 动态（使用 TwitterAPI.io）
- **NewsAPI** - 收集稳定币相关新闻报道
- **RSS 订阅** - 聚合行业媒体和公司博客
- **Google News** - 基于关键词的新闻搜索

### AI 分析
- **商业智能分类** - 自动识别竞争对手/客户/行业动态
- **威胁分析** - 评估竞争对手动态的威胁等级和影响领域
- **每日洞察** - 综合分析竞争态势和行业趋势

### 自动化报告
- **每日简报** - Markdown 格式的结构化日报
- **GitHub Actions** - 每日自动运行，报告自动提交

## 项目结构

```
stablecoin-intel/
├── config/
│   ├── keywords.json         # 关键词和公司配置
│   └── rss_feeds.json        # RSS 订阅源配置
├── src/
│   ├── collectors/           # 数据收集器
│   │   ├── twitter_api_io.py # Twitter 数据收集
│   │   ├── news_collector.py # NewsAPI 收集
│   │   └── rss_collector.py  # RSS 订阅收集
│   └── processors/           # 数据处理器
│       ├── ai_classifier.py  # AI 分类器
│       ├── content_filter.py # 内容过滤
│       └── daily_summary_generator.py  # 每日洞察生成
├── scripts/
│   └── daily_job_v2.py       # 每日任务主脚本
├── data/
│   ├── raw/                  # 原始数据
│   └── processed/            # 处理后数据
└── reports/
    └── daily/                # 每日简报
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
OPENAI_API_KEY=sk-xxx          # 必需 - AI 分析
TWITTERAPI_IO_KEY=xxx          # 可选 - Twitter 数据
NEWSAPI_KEY=xxx                # 可选 - 新闻数据
```

### 3. 运行日报生成

```bash
python scripts/daily_job_v2.py
```

输出文件：
- `reports/daily/daily_brief_YYYY-MM-DD.md` - 每日简报
- `data/processed/categorized_YYYY-MM-DD.json` - 分类数据

## 配置说明

### 监控对象 (config/keywords.json)

```json
{
  "competitors": {
    "tier_0": ["Fireblocks", "Anchorage"],
    "tier_1": ["Paxos", "BitGo"]
  },
  "customers": {
    "layer_a": ["WazirX", "OKX"]
  },
  "industry_topics": ["stablecoin", "crypto custody"]
}
```

### RSS 订阅源 (config/rss_feeds.json)

- 竞争对手博客（Fireblocks 等）
- 行业媒体（The Block、Decrypt）
- 发行商动态（Circle）
- Google News 关键词搜索

## 日报示例

```markdown
# 稳定币行业日报

## 每日洞察

### 竞争对手威胁总结
今日最大威胁来自 Fireblocks，其通过...

### 行业趋势总结
今日行业热点集中在...

## 竞争对手动态
[详细新闻列表]

## 行业进展
[详细新闻列表]
```

## 自动化运行

项目使用 GitHub Actions 每日自动运行：
- 运行时间：每天 10:00 SGT (UTC+8)
- 自动提交生成的日报到仓库

## API 成本

| 服务 | 用途 | 预估成本 |
|------|------|---------|
| OpenAI GPT-4o-mini | AI 分析 | ~$0.01/天 |
| TwitterAPI.io | Twitter 数据 | ~$0.05/天 |
| NewsAPI | 新闻数据 | 免费层 |
| RSS | 订阅数据 | 免费 |

## 许可证

MIT License
