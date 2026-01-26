# 稳定币情报系统优化计划

## 一、目标

从**业务负责人视角**（销售、BD、品牌、市场）优化数据采集，确保收集到的信息对业务决策有价值。

---

## 二、改动清单

### 2.1 NewsAPI 关键词可配置 ✅

**改动文件**: `src/collectors/news_collector.py`

**当前问题**: 关键词硬编码在代码中（第37-67行）

**改动方案**:
- 从 `config/keywords.json` 读取搜索关键词
- 复用已有的 `search_keywords` 和 `categories` 配置
- 保留优先级权重机制

**配置结构扩展** (`config/keywords.json`):
```json
{
  "newsapi_search": {
    "high_priority": {
      "keywords": ["从 categories.competitors 自动提取"],
      "weight": 1.5
    },
    "medium_priority": {
      "keywords": ["从 categories.clients 自动提取"],
      "weight": 1.0
    },
    "low_priority": {
      "keywords": ["从 categories.industry 自动提取"],
      "weight": 0.5
    }
  }
}
```

---

### 2.2 简单去重 ✅

**改动文件**: `scripts/daily_job_v2.py`

**当前问题**: NewsAPI 和 Twitter 合并时无去重

**改动方案**:
- 基于 URL 去重（完全匹配）
- 基于标题相似度去重（Jaccard 相似度 > 0.8）
- 不做复杂的语义去重

---

### 2.3 Twitter 内容质量过滤 ⭐ 重点

**改动文件**: `src/collectors/twitter_api_io.py`

**当前问题**: 所有推文都收集，包含大量噪音

**业务需求（你的角度）**:

| 需要 | 不需要 |
|------|--------|
| 产品功能更新 | 创始人日常闲聊 |
| 重要合作公告 | 表情包/meme |
| 融资/收购消息 | 转发抽奖活动 |
| 监管政策变化 | 交易所C端促销活动 |
| 竞争对手战略动向 | 个人观点/情绪发泄 |
| 客户采用案例 | 价格预测/喊单 |

**过滤规则设计**:

```python
# 1. 内容类型过滤（排除）
EXCLUDE_PATTERNS = [
    # 促销活动
    r"giveaway|airdrop|free\s+\$|win\s+\$|抽奖|送币",
    # 价格喊单
    r"to the moon|100x|pump|dump|买入|卖出|抄底",
    # 纯情绪
    r"^(gm|gn|lfg|wagmi|ngmi|lol|lmao)[\s!]*$",
    # 过多表情
    r"(🚀|🔥|💰|🎉){3,}",
]

# 2. 内容类型过滤（保留）
INCLUDE_PATTERNS = [
    # 产品更新
    r"launch|announce|release|update|upgrade|新功能|发布|上线",
    # 合作消息
    r"partner|collaboration|integrate|支持|合作|集成",
    # 融资消息
    r"raise|funding|series\s+[a-d]|investment|融资|投资",
    # 监管消息
    r"regulat|license|compliance|approve|ban|监管|牌照|合规",
    # 重要数据
    r"market\s+cap|volume|tvl|billion|million|市值|交易量",
]

# 3. 作者过滤
AUTHOR_RULES = {
    # 官方账号：保留所有内容
    "official": ["circle", "Tether_to", "paxos", "PayPal"],

    # KOL：只保留业务相关内容
    "kol": ["jerallaire", "paoloardoino"],

    # 媒体：保留所有内容
    "media": ["CoinDesk", "TheBlock__", "Cointelegraph"],
}

# 4. 互动数据过滤
MIN_ENGAGEMENT = {
    "official": 0,      # 官方账号无门槛
    "kol": 10,          # KOL 至少10个赞
    "media": 5,         # 媒体至少5个赞
    "other": 50,        # 其他账号至少50个赞
}
```

---

### 2.4 配置页面更新 ✅

**改动文件**: `docs/config-editor.html`

**新增功能**:
- NewsAPI 关键词编辑区域
- 过滤规则可视化配置
- 预览生成的搜索查询

---

## 三、配置文件完整结构

```json
{
  "version": "2.0",
  "last_updated": "2026-01-26",

  "categories": {
    "competitors": { ... },
    "clients": { ... },
    "industry": { ... }
  },

  "twitter_accounts": {
    "official": [...],
    "kol": [...],
    "media": [...]
  },

  "search_keywords": {
    "primary": [...],
    "secondary": [...]
  },

  "quality_filters": {
    "exclude_patterns": [...],
    "include_patterns": [...],
    "min_engagement": {
      "official": 0,
      "kol": 10,
      "media": 5,
      "other": 50
    }
  }
}
```

---

## 四、实施步骤

### Phase 1: NewsAPI 可配置（30分钟）
1. 修改 `news_collector.py`，从配置文件读取关键词
2. 更新 `config/keywords.json` 添加 newsapi 配置区
3. 更新 `config-editor.html` 添加 NewsAPI 编辑区

### Phase 2: 简单去重（15分钟）
1. 在 `daily_job_v2.py` 添加去重函数
2. 基于 URL + 标题相似度

### Phase 3: Twitter 质量过滤（45分钟）
1. 创建 `src/collectors/twitter_filter_v2.py`
2. 实现内容模式匹配过滤
3. 实现作者分级过滤
4. 实现互动数据过滤
5. 更新 `daily_job_v2.py` 调用新过滤器

### Phase 4: 配置页面更新（30分钟）
1. 添加 NewsAPI 关键词编辑
2. 添加过滤规则配置
3. 测试并部署

---

## 五、预期效果

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 每日推文数 | ~200条（含噪音） | ~50条（高质量） |
| 噪音比例 | ~60% | <10% |
| 关键词修改 | 需改代码 | 网页配置 |
| 重复内容 | 有 | 基本消除 |

---

## 六、待确认问题

1. **客户列表**：当前客户是 Visa、Mastercard、Stripe 等，需要补充交易所客户吗？
2. **交易所过滤**：你说交易所C端活动不重要，但交易所上币公告要不要？
3. **竞争对手**：当前8家竞争对手是否完整？需要增减吗？
4. **语言**：是否只收集英文，还是也要中文/其他语言？

---

*等待确认后开始实施*
