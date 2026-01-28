添加新的竞争对手到监控列表。

用法示例：
- `/add-competitor Ripple ripple` - 添加 Ripple 公司，Twitter 账号 @ripple
- `/add-competitor "Copper Technologies" CopperHQ` - 公司名有空格时用引号

执行步骤：
1. 解析用户输入的公司名称和 Twitter 用户名
2. 读取 `config/keywords.json`
3. 询问用户要放入哪个分类：
   - `tier_0_custody` - 头部托管竞争对手（如 Fireblocks, BitGo）
   - `tier_1_payment_infra` - 支付基础设施竞争对手（如 BVNK）
4. 添加 `{"name": "公司名", "twitter": "用户名"}` 到对应数组
5. 保存文件
6. 确认添加成功，显示更新后的竞争对手列表

注意：
- 检查是否已存在相同的公司名或 Twitter 账号，避免重复添加
- 不自动 commit，用户稍后统一提交
