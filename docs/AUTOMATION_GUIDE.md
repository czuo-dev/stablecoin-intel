# 自动化部署指南

## 🎯 概述

本指南介绍如何部署稳定币情报Agent的自动化任务。

---

## 🤖 GitHub Actions 与每日发布

**日报流水线**（`.github/workflows/daily-collect.yml`）：

- **触发**：每天 UTC 02:00（新加坡 10:00）定时运行，或仓库 Actions 里手动 “Run workflow”。
- **步骤**：拉代码 → 装依赖 → 运行 `scripts/daily_job_v2.py` → 提交并推送 `data/`、`reports/`、**以及** `docs/daily-reports.js` 和 `docs/reports/daily/`。
- **前端数据**：日报列表和详情来自 `docs/daily-reports.js`；静态站（GitHub Pages）从 `docs/` 发布，所以 workflow 必须把 `docs/` 里上述文件一并提交，前端/Pages 才会看到最新日报。
- **Secrets**：在仓库 Settings → Secrets 中配置 `OPENAI_API_KEY`、`NEWSAPI_KEY`、`TWITTERAPI_IO_KEY`，否则日报中的 AI 分析与推文会失败。

**周报**（`.github/workflows/weekly-report.yml`）：每周五 UTC 15:00 运行，依赖 `weekly_aggregator.py`、`weekly_report_generator_v2.py`、`convert_to_html.py`、`update_website.py`。

**“自动更新”说明**：
- **GitHub Pages**：只有 Action 成功推送后，线上站才会更新；每天定时跑一次，无需人工。
- **本地 localhost**：读的是本机文件，**不会**自动从 GitHub 拉新数据。要看到最新日报：先 `git pull`（或本地跑 `python scripts/daily_job_v2.py`），再刷新页面即可；已改为每次请求重新读 `docs/daily-reports.js`，无需重启 dev server。

**前端没更新时自检**：
- **本地开发**（`pnpm dev`）：数据来自**本地** `docs/daily-reports.js`（项目根目录），不会自动从 GitHub 拉取。
  - 若希望看到 Action 跑出的最新日报：在**项目根**执行 `git pull`，然后**刷新浏览器**即可；dev server 每次请求会重新读文件，无需重启。
  - 若在本地自己跑日报：在项目根执行 `python scripts/daily_job_v2.py [--date YYYY-MM-DD]`，会更新 `docs/daily-reports.js` 和 `docs/reports/daily/*.md`，刷新浏览器即可看到。
- **GitHub Pages**：确认 Settings → Pages 的发布分支是 Action 推送的分支（多为 main）；推送后等 1～5 分钟再强制刷新或无痕打开。
- **Action 是否真的推了 docs**：在仓库最新一次 “📊 Daily data” 的 commit 里，看是否包含 `docs/daily-reports.js` 和 `docs/reports/daily/` 的变更。若没有，说明当时跑的 workflow 还是旧版（未合并“提交 docs”的改动），需把当前分支合并到 main 后再跑一次。

---

## 📋 方式1：使用Schedule库（推荐给开发/测试）

### 优点
- ✅ 简单易用
- ✅ 跨平台（Windows/Mac/Linux）
- ✅ 易于调试

### 缺点
- ❌ 需要一直运行
- ❌ 进程退出后任务停止

### 使用方法

1. **安装依赖**
```bash
pip3 install schedule
```

2. **启动调度器**
```bash
python3 scripts/scheduler.py
```

3. **后台运行（Mac/Linux）**
```bash
# 使用 nohup
nohup python3 scripts/scheduler.py > logs/scheduler_output.log 2>&1 &

# 查看进程
ps aux | grep scheduler

# 停止进程
kill <PID>
```

4. **后台运行（Windows）**
```batch
# 使用 start
start /B python scripts\scheduler.py > logs\scheduler_output.log 2>&1
```

---

## 📋 方式2：使用Cron（推荐给生产环境 - Mac/Linux）

### 优点
- ✅ 系统级定时任务
- ✅ 自动重启
- ✅ 资源占用少

### 使用方法

1. **获取Python路径和项目路径**
```bash
which python3
# 输出示例: /usr/local/bin/python3

pwd
# 输出示例: /Users/yourname/projects/stablecoin-intel
```

2. **编辑crontab**
```bash
crontab -e
```

3. **添加任务**
```bash
# 设置环境变量
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
PYTHONPATH=/Users/yourname/projects/stablecoin-intel

# 每日任务：工作日早上9点
0 9 * * 1-5 cd /Users/yourname/projects/stablecoin-intel && /usr/local/bin/python3 scripts/daily_job.py

# 周报任务：每周一早上10点
0 10 * * 1 cd /Users/yourname/projects/stablecoin-intel && /usr/local/bin/python3 scripts/weekly_job.py

# 日志轮转：每天午夜清理30天前的日志
0 0 * * * find /Users/yourname/projects/stablecoin-intel/logs -name "*.log" -mtime +30 -delete
```

4. **验证cron任务**
```bash
# 查看当前cron任务
crontab -l

# 查看cron日志（Mac）
log show --predicate 'process == "cron"' --info

# 查看cron日志（Linux）
grep CRON /var/log/syslog
```

### Cron时间格式说明
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── 星期 (0-7, 0和7都代表周日)
│ │ │ └───── 月份 (1-12)
│ │ └─────── 日期 (1-31)
│ └───────── 小时 (0-23)
└─────────── 分钟 (0-59)

示例：
0 9 * * 1-5  → 工作日早上9点
0 10 * * 1   → 每周一上午10点
*/30 * * * * → 每30分钟
0 0 * * *    → 每天午夜
```

---

## 📋 方式3：使用Task Scheduler（Windows）

### 使用方法

1. **打开任务计划程序**
   - Win+R → `taskschd.msc`

2. **创建基本任务**
   - 右键"任务计划程序库" → "创建基本任务"
   - 名称：Stablecoin Intel Daily Job

3. **配置触发器**
   - 每日任务：每天早上9点
   - 条件：仅在工作日

4. **配置操作**
   - 程序：`python`
   - 参数：`scripts/daily_job.py`
   - 起始于：`C:\path\to\stablecoin-intel`

5. **高级设置**
   - ✅ 允许按需运行任务
   - ✅ 如果任务失败，每隔1分钟重启
   - ✅ 限制重启次数：3

---

## 🐳 方式4：使用Docker（高级）

### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "scripts/scheduler.py"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  scheduler:
    build: .
    volumes:
      - ./data:/app/data
      - ./reports:/app/reports
      - ./logs:/app/logs
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
```

### 运行
```bash
docker-compose up -d
```

---

## 📊 监控和维护

### 1. 查看日志
```bash
# 查看今日日志
cat logs/daily_$(date +%Y-%m-%d).log

# 实时查看
tail -f logs/daily_$(date +%Y-%m-%d).log

# 查看错误日志
grep ERROR logs/*.log
```

### 2. 检查任务执行状态
```bash
# 查看最新的报告
ls -lht reports/daily/ | head -5

# 检查文件大小（太小可能有问题）
find reports/daily/ -name "*.md" -size -1k
```

### 3. 磁盘空间管理
```bash
# 查看各目录大小
du -sh data/ reports/ logs/

# 清理30天前的日志
find logs/ -name "*.log" -mtime +30 -delete

# 清理90天前的报告
find reports/ -name "*.md" -mtime +90 -delete
```

### 4. 设置告警（可选）
```bash
# 创建告警脚本：scripts/check_daily_job.sh
#!/bin/bash

TODAY=$(date +%Y-%m-%d)
REPORT="reports/daily/daily_brief_$TODAY.md"

if [ ! -f "$REPORT" ]; then
    echo "❌ 今日报告未生成: $TODAY"
    # 发送邮件或Slack通知
else
    echo "✅ 今日报告正常: $TODAY"
fi
```

```bash
# 添加到cron，每天下午2点检查
0 14 * * * /path/to/scripts/check_daily_job.sh
```

---

## 🔧 故障排查

### 问题1：任务没有执行

**检查项**：
```bash
# 1. 检查Python路径
which python3

# 2. 检查项目路径
pwd

# 3. 测试手动运行
python3 scripts/daily_job.py

# 4. 查看cron日志
# Mac: log show --predicate 'process == "cron"' --info
# Linux: grep CRON /var/log/syslog
```

### 问题2：API调用失败

**检查项**：
```bash
# 1. 检查API Key
grep OPENAI_API_KEY config.py

# 2. 测试API连接
python3 -c "from config import OPENAI_API_KEY; print(OPENAI_API_KEY[:10])"

# 3. 检查网络
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 问题3：权限问题

```bash
# 确保脚本可执行
chmod +x scripts/*.py

# 确保日志目录可写
chmod 755 logs/ data/ reports/
```

---

## 💰 成本监控

### 每日成本估算
```
数据收集: $0 (使用免费API)
AI分类: 50篇 × $0.00004 = $0.002
批量摘要: 5批 × $0.0003 = $0.0015
情感分析: $0.001
趋势分析: $0.001
━━━━━━━━━━━━━━━━━━━━━
日成本: ~$0.006 (约4分钱)
```

### 月度成本
```
每日任务: $0.006 × 22天 = $0.13
周报任务: $0.005 × 4次 = $0.02
━━━━━━━━━━━━━━━━━━━━━
月成本: ~$0.15 (约1块钱)
```

### 成本控制建议
1. ✅ 只在工作日运行每日任务
2. ✅ 使用批量处理（节省60%）
3. ✅ 设置每日处理上限（如50篇）
4. ✅ 缓存重复内容

---

## 🎯 最佳实践

### 1. 环境配置
```bash
# 创建 .env 文件（不提交到Git）
echo "OPENAI_API_KEY=your-key" > .env

# 修改 config.py 读取环境变量
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

### 2. 日志管理
- ✅ 使用日期命名日志文件
- ✅ 定期清理旧日志（保留30天）
- ✅ 重要事件单独记录

### 3. 备份策略
```bash
# 每周备份分类数据
tar -czf backup_$(date +%Y-%m-%d).tar.gz data/classified/

# 保留最近4周的备份
find backups/ -name "backup_*.tar.gz" -mtime +28 -delete
```

### 4. 监控指标
- 📊 每日处理文章数
- 📊 API调用次数
- 📊 任务执行时间
- 📊 失败率
- 📊 成本支出

---

## 📚 参考资源

- [Schedule库文档](https://schedule.readthedocs.io/)
- [Cron表达式生成器](https://crontab.guru/)
- [OpenAI API价格](https://openai.com/pricing)

---

**最后更新**: 2025-01-15