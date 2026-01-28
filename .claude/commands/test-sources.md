测试所有数据源的连通性和状态。

执行步骤：

1. **测试 NewsAPI**
   - 检查环境变量 `NEWSAPI_KEY` 是否存在
   - 尝试调用 API 获取 1 条新闻
   - 报告状态：✅ 正常 / ❌ 失败（原因）

2. **测试 TwitterAPI.io**
   - 检查环境变量 `TWITTERAPI_IO_KEY` 是否存在
   - 如果有配额跟踪，显示今日已用/剩余配额
   - 报告状态：✅ 正常 / ❌ 失败（原因）

3. **测试 RSS 订阅源**
   - 读取 `config/rss_feeds.json`
   - 逐个测试每个 RSS URL 是否可以访问
   - 统计成功/失败数量
   - 列出失败的源

4. **测试 Google News RSS**
   - 尝试搜索一个关键词
   - 报告状态

5. **输出汇总报告**
   ```
   === 数据源状态检查 ===

   NewsAPI:     ✅ 正常
   TwitterAPI:  ✅ 正常 (今日配额: 850/1000)
   RSS 订阅:    ✅ 8/10 源正常
   Google News: ✅ 正常

   ❌ 失败的 RSS 源：
   - Fireblocks Blog: 连接超时
   - Circle Blog: 404 Not Found
   ```

用途：
- 日报内容少时，排查是哪个数据源出了问题
- 定期检查确保所有源正常工作
