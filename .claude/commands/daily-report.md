生成今日的稳定币行业日报。

执行步骤：
1. 运行 `python scripts/daily_job_v2.py`
2. 等待执行完成
3. 读取今天生成的日报文件 `reports/daily/daily_brief_YYYY-MM-DD.md`
4. 显示「每日洞察」板块的内容
5. 告知用户完整报告的文件路径

注意：
- 如果执行失败，显示错误信息并分析原因
- 执行成功后不需要 git commit，用户会在满意后手动提交
