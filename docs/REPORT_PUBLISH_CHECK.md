# 日报/周报发布自检说明

## 当前状态（基于仓库文件检查）

| 类型 | 最新日期 | 是否含 1 月 31 日 |
|------|----------|-------------------|
| **日报** | `docs/daily-reports.js` 中最新为 **2026-01-30** | ❌ 无 2026-01-31 |
| **周报** | `reports/weekly/` 最新为 **W05 2026-01-26** | ❌ 无 1 月 31 日当周（W05 2026-01-31） |

结论：**1 月 31 日的日报和周报目前都未出现在仓库里，因此前端也还没有。**

---

## 发布流程简述

1. **日报**：`Daily Data Collection`（daily-collect.yml）每天 **UTC 02:00（新加坡 10:00）** 跑 → 生成 `docs/daily-reports.js` 等 → **commit + push**。
2. **周报**：`Weekly Report`（weekly-report.yml）**每周五 UTC 15:00（新加坡 23:00）** 跑 → 生成 `reports/{date}/` 并复制到 `reports/weekly/` → **commit + push**。
3. **前端**：对 `main` 的 push 若改动了 `docs/daily-reports.js` 或 `reports/weekly/` 等，会触发 **Deploy to GitHub Pages**，把最新日报/周报部署到前端。

---

## ⚠️ 必须配置 GH_PAT，前端才会自动更新

**原因**：GitHub 规定，用默认 `GITHUB_TOKEN` 发起的 push **不会**触发其他 workflow。所以 Daily/Weekly 里若用普通 `git push`，数据会进仓库，但 **Deploy to GitHub Pages 不会跑**，前端就不会更新。

**做法**：用 Personal Access Token (PAT) 来推送，这样 push 会触发 Deploy。

1. 打开 GitHub → **Settings**（个人）→ **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**。
2. 勾选 **repo** 权限，生成后复制 token（只显示一次）。
3. 打开**本仓库** → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**。
4. 名称填 **`GH_PAT`**，值贴刚才的 token，保存。

保存后，下次 Daily / Weekly 跑完并 push 时，会自动触发 **Deploy to GitHub Pages**，前端就会更新。若还没配 `GH_PAT`，先配好再手动触发一次 Daily 或 Weekly 测试。

---

## 可能原因与排查

### 1. 日报（1 月 31 日）没有

- **时间未到**：日报是每天 **10:00 SGT** 跑。若当前仍是 1 月 31 日 10:00 之前，当天日报还没生成。
- **Workflow 未跑或失败**：  
  - 打开仓库 **Actions** → 看 **Daily Data Collection** 在 1 月 31 日是否有一次 run。  
  - 若有 run 且失败：点进去看失败步骤（常见：缺少 `OPENAI_API_KEY` / `NEWSAPI_KEY` / `TWITTERAPI_IO_KEY`、网络/API 报错、脚本报错）。
- **跑成功但无 commit**：`daily_job_v2.py` 里若检测到“无变更”可能不 commit；或只 add 了部分路径，未包含 `docs/daily-reports.js`。  
  - 在 **daily-collect.yml** 里确认有：`git add docs/daily-reports.js` 且在 `git diff --staged --quiet` 为 false 时会 commit + push。
- **分支/权限**：确认 workflow 有 `contents: write`，且 push 的是默认分支（一般为 `main`）。

**建议**：在 Actions 里对 1 月 31 日手动触发一次 **Daily Data Collection**（workflow_dispatch），看是否成功并产生包含 2026-01-31 的 `docs/daily-reports.js` 并 push。

---

### 2. 周报（1 月 31 日当周）没有

- **时间未到**：周报是 **每周五 23:00 SGT** 跑。1 月 31 日是周五，若当前早于 1 月 31 日 23:00 SGT，本周周报还没跑。
- **Workflow 未跑或失败**：  
  - Actions → **Weekly Report**：看 1 月 31 日（或 30 日 UTC 15:00 对应的时间）是否有 run、是否成功。  
  - 失败时查看日志：常见为 `OPENAI_API_KEY` 未设、`weekly_aggregator` 找不到数据（依赖 `data/processed/integrated_data_*.json`）、或 `weekly_report_generator_v2.py` 报错。
- **数据依赖**：周报依赖过去 7 天的 `data/processed/integrated_data_{date}.json`。若这些文件缺失（例如日报/采集多日未跑），周报会无数据或报错。

**建议**：若已过周五 23:00 SGT 仍无周报，在 Actions 里手动触发一次 **Weekly Report**，根据报错修数据或配置。

---

### 3. 前端没有更新（日报/周报已 push 但页面仍是旧的）

- **未配置 GH_PAT**（最常见）：  
  - 用默认 GITHUB_TOKEN 的 push **不会**触发 Deploy。  
  - 必须按上面「必须配置 GH_PAT」在仓库里添加 **GH_PAT** secret，Daily/Weekly 已改为用 PAT 推送，配好后下次 push 就会触发 Deploy。
- **Deploy 未触发**：  
  - 到 Actions 看 **Deploy to GitHub Pages** 在 Daily/Weekly push 之后是否有 run、是否成功。
- **Pages 未用 Actions**：  
  - 仓库 **Settings → Pages → Build and deployment** 里 Source 需为 **GitHub Actions**，否则不会用 workflow 的部署结果。
- **缓存**：浏览器或 CDN 缓存可能导致看到旧页面，可无痕/换设备或等几分钟再试。

---

## 快速检查清单

1. [ ] Actions 中 **Daily Data Collection** 在 1 月 31 日是否有成功 run？  
2. [ ] Actions 中 **Weekly Report** 在 1 月 31 日（或周五 23:00 SGT 左右）是否有成功 run？  
3. [ ] 仓库 **main** 上 `docs/daily-reports.js` 是否包含 `"date": "2026-01-31"`？  
4. [ ] 仓库 **main** 上 `reports/weekly/` 是否出现 `weekly_*_2026_W05_2026-01-31.md`？  
5. [ ] **Deploy to GitHub Pages** 在最近一次日报/周报 push 之后是否成功跑完？  
6. [ ] **Settings → Pages** 是否选用 **GitHub Actions** 作为来源？

按上述顺序排查，即可确定是“未生成”“未 push”还是“未部署到前端”，并针对对应步骤修配置或重跑 workflow。
