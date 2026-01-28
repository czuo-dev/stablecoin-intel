添加新的 RSS 订阅源到监控列表。

用法示例：
- `/add-rss https://example.com/feed.xml "Example Blog" media`
- `/add-rss https://company.com/rss "Company Blog" competitors`

参数：
1. RSS URL - 订阅源地址
2. 源名称 - 显示名称
3. 分类 - competitors / industry_players / media

执行步骤：
1. 解析用户输入的 URL、名称和分类
2. 测试 RSS URL 是否可以正常访问和解析
3. 如果测试失败，提示用户检查 URL
4. 读取 `config/rss_feeds.json`
5. 添加新源到指定分类：
   ```json
   {"name": "源名称", "url": "RSS URL", "category": "分类"}
   ```
6. 保存文件
7. 抓取该源的最新 3 篇文章标题，确认工作正常

可用分类说明：
- `competitors` - 竞争对手博客（如 Fireblocks Blog）
- `industry_players` - 行业玩家（如 Circle, Stripe）
- `media` - 行业媒体（如 The Block, Decrypt）

注意：
- 检查是否已存在相同 URL，避免重复
- 不自动 commit
