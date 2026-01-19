# Twitter API 配置指南

## 🎯 目标

集成Twitter API，自动监控稳定币相关推文。

---

## 📋 审批通过后的步骤

### 步骤1：获取API密钥

1. **登录 Twitter Developer Portal**
   - 访问：https://developer.twitter.com/en/portal/dashboard

2. **创建App**
   - 点击 "Projects & Apps"
   - 点击 "+ Create App"
   - 名称：`Stablecoin Intel Bot`
   - 描述：`News aggregation for stablecoin industry research`

3. **获取密钥**
   
   进入App设置，获取以下密钥：
   
   **需要的密钥（API v2 只需要这1个）**：
   ```
   ✅ Bearer Token
   ```
   
   **可选（如果要发推文才需要）**：
   ```
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
   ```

4. **保存密钥**
   
   ⚠️ **重要**：密钥只显示一次，立即复制保存！

---

### 步骤2：配置项目

1. **更新 config.py**

打开 `config.py`，找到Twitter配置部分，填入你的密钥：

```python
# Twitter API配置
TWITTER_BEARER_TOKEN = "你的Bearer-Token"

# 如果要发推文（后续Week 10需要）
TWITTER_API_KEY = "你的API-Key"
TWITTER_API_SECRET = "你的API-Secret"
TWITTER_ACCESS_TOKEN = "你的Access-Token"
TWITTER_ACCESS_SECRET = "你的Access-Token-Secret"
```

2. **安装依赖**

```bash
pip3 install tweepy python-dotenv
```

---

### 步骤3：测试连接

```bash
python3 test_twitter.py
```

**预期输出**：
```
🧪 测试Twitter API集成

【测试1】初始化Twitter收集器
✅ 初始化成功
   监控账号: 3
   监控关键词: 2

【测试2】收集单个用户推文
测试账号: @circle
✅ 收集到 5 条推文

【测试3】关键词搜索
测试关键词: stablecoin
✅ 找到 10 条相关推文

✅ 所有测试完成！
```

---

## 🔧 配置监控策略

### 当前配置（config.py）

```python
# 监控的账号（可以添加更多）
TWITTER_MONITORED_ACCOUNTS = [
    "circle",           # Circle官方
    "Tether_to",        # Tether
    "paxos",           # Paxos
    "coinbase",        # Coinbase
    "MessariCrypto",   # 行业分析
    "paoloardoino",    # Tether CTO
    "jerallaire",      # Circle CEO
]

# 监控的关键词（可以添加更多）
TWITTER_MONITORED_KEYWORDS = [
    "stablecoin",
    "USDC",
    "USDT",
    "PYUSD",
    "stablecoins",
    "稳定币"
]
```

### 建议的监控账号

**监管机构**：
- `federalreserve` - 美联储
- `USOCC` - 美国货币监理署
- `HKMAgovhk` - 香港金管局

**公司官方**：
- `PayPal` - PayPal
- `Visa` - Visa
- `Mastercard` - Mastercard

**行业媒体**：
- `coindesk` - CoinDesk
- `TheBlock__` - The Block
- `cointelegraph` - Cointelegraph

**分析师/KOL**：
- `cburniske` - Chris Burniske
- `nic__carter` - Nic Carter
- `lawmaster` - Jake Chervinsky

---

## 📊 使用方法

### 1. 手动运行监控

```bash
# 收集最近1小时的推文
python3 scripts/twitter_monitor.py

# 收集最近24小时的推文
python3 -c "
from scripts.twitter_monitor import TwitterMonitorJob
job = TwitterMonitorJob()
job.run(hours=24)
"
```

### 2. 设置定时任务

在crontab中添加：

```bash
# 每小时运行一次
0 * * * * cd /path/to/stablecoin-intel && python3 scripts/twitter_monitor.py
```

### 3. 查看收集的数据

```bash
# 查看原始数据
ls -lh data/twitter/

# 查看今天的高质量推文
cat data/twitter/high_quality/tweets_$(date +%Y-%m-%d).json | jq
```

---

## 📈 数据流程

```
Twitter API
    ↓
收集推文（每小时）
    ↓
筛选高质量推文
    ↓
保存到 data/twitter/high_quality/
    ↓
整合到每日报告
    ↓
发布到Twitter（Week 10）
```

---

## 🔍 API限额说明

### Free tier（基础版 - 你现在用的）

| 操作 | 限额 |
|------|------|
| 搜索推文 | 10,000次/月 |
| 获取用户推文 | 100,000次/月 |
| 发布推文 | 免费（后续Week 10用） |

### 成本

✅ **完全免费**（在限额内）

按照我们的配置：
- 每小时监控：7个账号 + 6个关键词 = 13次API调用
- 每天：13 × 24 = 312次
- 每月：312 × 30 = 9,360次

**完全在免费额度内！** 👍

---

## ⚠️ 常见问题

### Q1: 审批要多久？

**A**: 通常1-24小时，周末可能稍慢。

### Q2: 如果被拒怎么办？

**A**: 
1. 查看拒绝原因
2. 修改申请理由
3. 重新申请
4. 或联系Twitter支持

### Q3: Bearer Token在哪里找？

**A**:
1. 进入Developer Portal
2. 选择你的App
3. 点击 "Keys and tokens"
4. 找到 "Bearer Token"
5. 如果没有，点击 "Regenerate"

### Q4: 为什么收集不到推文？

**A**: 可能原因：
1. 最近24小时这些账号没有发推
2. 关键词太具体，匹配少
3. API限额用完了（查看Developer Portal）
4. Bearer Token错误

### Q5: 如何知道API还剩多少额度？

**A**: 
1. 访问 Developer Portal
2. 查看 "Usage" 页面
3. 或在代码中添加：

```python
# 查看API限额
import tweepy

client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
rate_limit = client.get_users_tweets.__wrapped__.rate_limit_status

print(f"剩余调用次数: {rate_limit['remaining']}")
print(f"重置时间: {rate_limit['reset']}")
```

---

## 🎯 下一步

完成Twitter API配置后：

1. ✅ **今天**：测试数据收集
2. ✅ **明天**：整合到每日报告
3. ⏭️ **Day 5**：配置NewsAPI
4. ⏭️ **Week 10**：实现自动发推

---

## 📞 需要帮助？

遇到问题随时问我：
- API密钥配置问题
- 代码报错
- 功能不清楚
- 想调整监控策略

---

**最后更新**: 2026-01-15