# 本地与 GitHub 同步步骤（当前状态）

## 1. 当前状态一览

| 项目 | 说明 |
|------|------|
| **分支** | `main`，比 `origin/main` **领先 1 个 commit**（未 push） |
| **领先的 1 个 commit** | `57b4968` — "fix: Daily/Weekly 用 GH_PAT 推送以触发 Deploy；周报静态嵌入与自检说明" |
| **该 commit 包含** | `.github/workflows/daily-collect.yml`、`deploy-pages.yml`、`weekly-report.yml`，`docs/REPORT_PUBLISH_CHECK.md`，`docs/daily-reports.js`，`scripts/daily_job_v2.py`，`scripts/extract_weekly_reports_json.js`，`Settings.tsx`，以及 `.DS_Store`（建议之后从仓库移除） |
| **未暂存修改** | 前端/周报/日报相关：`App.tsx`、`Layout.tsx`、`data-service.ts`、`ReportDetail.tsx`、`package.json`、`pnpm-lock.yaml`、`server/index.ts`、`vite.config.ts` |
| **未跟踪文件** | Firebase/登录：`FIREBASE_AUTH.md`、`AuthContext.tsx`、`firebase.ts`、`Login.tsx`；以及 `.pnpm-store/`（本地 pnpm 缓存，**不要提交**） |

---

## 2. 建议操作顺序

### 步骤 A：先 push 已有的 1 个 commit（让 GitHub 用上 GH_PAT 的 workflow）

```bash
cd /Users/changbaizuo_1/projects/stablecoin-intel

# 确认当前状态
git status
git log -1 --oneline

# 推送到 origin/main（只推送已有 commit，不包含未暂存修改）
git push origin main
```

推送成功后，GitHub 上就有「用 GH_PAT 推送」的 Daily/Weekly workflow；配好 `GH_PAT` 后，下次日报/周报跑完会自动触发 Deploy。

---

### 步骤 B：再提交并推送「周报静态 + 日报排序 + 前端展示」等修改（可选，一次或分两次）

**选项 1：一次提交（周报 + 日报排序 + 英文周报 + Markdown 渲染）**

```bash
cd /Users/changbaizuo_1/projects/stablecoin-intel

# 只 add 与报告/前端展示相关的文件，不包含 .pnpm-store 和 Firebase
git add stablecoin-intel-web-source/client/src/App.tsx
git add stablecoin-intel-web-source/client/src/components/Layout.tsx
git add stablecoin-intel-web-source/client/src/lib/data-service.ts
git add stablecoin-intel-web-source/client/src/pages/ReportDetail.tsx
git add stablecoin-intel-web-source/client/src/pages/Settings.tsx
git add stablecoin-intel-web-source/package.json
git add stablecoin-intel-web-source/pnpm-lock.yaml
git add stablecoin-intel-web-source/server/index.ts
git add stablecoin-intel-web-source/vite.config.ts

# 检查暂存区，避免误加
git status

# 提交
git commit -m "feat: 周报静态 fallback、日报按日期排序、周报详情 Markdown 渲染、weekly en 支持"

# 推送
git push origin main
```

**选项 2：分两次提交（先报告/展示，再 Firebase/登录）**

第一次：只提交报告与展示相关（同上，但不包含 Firebase 相关文件）。

第二次：再 add Firebase/登录相关文件并单独 commit：

```bash
git add stablecoin-intel-web-source/FIREBASE_AUTH.md
git add stablecoin-intel-web-source/client/src/contexts/AuthContext.tsx
git add stablecoin-intel-web-source/client/src/lib/firebase.ts
git add stablecoin-intel-web-source/client/src/pages/Login.tsx
git status
git commit -m "feat: Firebase 登录与 AuthGate"
git push origin main
```

---

## 3. 不要提交的内容

| 路径/类型 | 说明 |
|-----------|------|
| **.pnpm-store/** | 本地 pnpm 缓存，体积大且不应进仓库。若希望彻底忽略，可在仓库根目录 `.gitignore` 里加一行：`.pnpm-store/` |
| **.DS_Store** | 已在 `.gitignore`；若之前被误提交，可在下次清理时用 `git rm --cached .DS_Store` 再 commit |

---

## 4. 一键检查命令（每次提交前可跑）

```bash
cd /Users/changbaizuo_1/projects/stablecoin-intel

# 看是否有不该提交的文件被 add
git status

# 看暂存区具体改了哪些文件（add 之后）
git diff --cached --name-only
```

---

## 5. 若想忽略 .pnpm-store

在项目根目录的 `.gitignore` 末尾加一行：

```
.pnpm-store/
```

保存后执行 `git status`，`.pnpm-store/` 就不会再出现在 "Untracked files" 里。
