# GitHub Pages 部署指南

## 当前状态检查

✅ 必需文件都已存在：
- `index.html` ✓
- `.nojekyll` ✓ (需要提交到 git)
- `reports.js` ✓
- `js/main.js` ✓
- `css/style.css` ✓

## 解决 404 问题的步骤

### 1. 确保所有文件已提交

```bash
# 添加 .nojekyll 文件（这个很重要！）
git add docs/.nojekyll

# 添加所有 docs 文件
git add docs/

# 提交
git commit -m "Add GitHub Pages files"

# 推送到 GitHub
git push
```

### 2. GitHub Pages 设置

1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Pages**
3. 在 "Source" 部分：
   - 选择 **"Deploy from a branch"**
   - Branch: **main** (或你的主分支名)
   - Folder: **/docs**
   - 点击 **Save**

### 3. 等待部署

- GitHub Pages 通常需要 **1-5 分钟** 来部署
- 部署完成后，Settings → Pages 页面会显示绿色勾号 ✓
- 你的网站地址会是：`https://[你的用户名].github.io/stablecoin-intel/`

### 4. 如果还是 404

**检查清单：**
- [ ] 确认 `.nojekyll` 文件已提交到 git
- [ ] 确认 `index.html` 在 `docs/` 目录下（不是 `docs/index/index.html`）
- [ ] 确认 GitHub Pages 设置中 Folder 选择了 `/docs`
- [ ] 等待至少 5 分钟让 GitHub 完成部署
- [ ] 清除浏览器缓存或使用无痕模式访问

**验证命令：**
```bash
# 检查文件是否在正确位置
ls -la docs/index.html

# 检查 .nojekyll 是否已提交
git ls-files docs/.nojekyll

# 本地测试（应该能正常显示）
python3 -m http.server 8000 --directory docs
# 访问 http://localhost:8000
```

### 5. 调试技巧

如果本地测试正常但 GitHub Pages 404：

1. **检查 GitHub Actions**
   - 进入仓库 → Actions 标签
   - 查看是否有部署错误

2. **检查文件路径**
   - GitHub Pages 的根路径是 `/docs/`
   - 所以 `index.html` 应该在 `docs/index.html`
   - 不是 `docs/index/index.html`

3. **检查文件大小**
   - 确保文件不是空的
   - 确保文件编码是 UTF-8

4. **强制刷新**
   - 访问 `https://[用户名].github.io/stablecoin-intel/`
   - 使用 Ctrl+F5 (Windows) 或 Cmd+Shift+R (Mac) 强制刷新

## 常见问题

**Q: 为什么选择 `/docs` 而不是根目录？**
A: 使用 `/docs` 可以保持项目结构整洁，源代码和文档分离。

**Q: `.nojekyll` 文件是做什么的？**
A: 告诉 GitHub Pages 不要使用 Jekyll 处理文件，直接提供静态文件。这对于纯 HTML/JS/CSS 网站很重要。

**Q: 部署后多久能看到更新？**
A: 通常 1-5 分钟，但有时可能需要 10-15 分钟。
