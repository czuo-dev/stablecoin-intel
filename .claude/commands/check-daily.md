检查今日日报是否已成功生成并发布到网站。

执行步骤：

1. 获取今天的日期 (YYYY-MM-DD 格式)
2. 检查网站 https://czuo-dev.github.io/stablecoin-intel/ 是否有今日日报
3. 使用 GitHub API 检查最近的 daily-collect.yml 工作流运行状态：
   - `WebFetch` 访问 `https://api.github.com/repos/czuo-dev/stablecoin-intel/actions/runs?per_page=5`
   - 查找 "Daily Data Collection" 工作流的最新运行
4. 如果日报缺失或工作流失败：
   a. 获取失败运行的 job 详情：`https://api.github.com/repos/czuo-dev/stablecoin-intel/actions/runs/{run_id}/jobs`
   b. 分析可能的失败原因
   c. 检查本地是否有今日数据文件：
      - `data/processed/categorized_news_YYYY-MM-DD.json`
      - `reports/daily/daily_brief_YYYY-MM-DD.md`
   d. 尝试本地运行 `python3 scripts/daily_job_v2.py` 来复现问题

5. 报告结果：
   - 如果成功：显示今日日报的标题和条目数
   - 如果失败：显示错误原因和建议的修复步骤

常见失败原因：
- Twitter API 配额耗尽
- OpenAI API 调用超时或报错
- GitHub Actions secrets 配置问题
- 代码 bug（如时间解析错误）

注意：
- 每天 10:30 AM SGT 使用此命令检查
- 日报生成工作流在每天 10:00 AM SGT 运行
