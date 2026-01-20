# Stablecoin Intelligence - Web Portal

这是稳定币情报系统的前端网站。

## GitHub Pages 部署检查清单

### ✅ 必需文件
- [x] `index.html` - 主页文件
- [x] `.nojekyll` - 禁用 Jekyll 处理
- [x] `reports.js` - 周报数据
- [x] `js/main.js` - 前端脚本
- [x] `css/style.css` - 样式文件

### 📋 GitHub Pages 设置步骤

1. **仓库设置**
   - 进入 GitHub 仓库 → Settings → Pages
   - Source: 选择 "Deploy from a branch"
   - Branch: 选择 `main`
   - Folder: 选择 `/docs`
   - 点击 Save

2. **等待部署**
   - GitHub Pages 通常需要 1-5 分钟部署
   - 部署完成后会显示绿色勾号
   - 访问地址: `https://[你的用户名].github.io/stablecoin-intel/`

3. **常见问题排查**

   **404 错误：**
   - 确认 `docs/index.html` 文件存在
   - 确认 `.nojekyll` 文件在 `docs/` 目录下
   - 确认所有文件已提交到 GitHub
   - 等待几分钟让 GitHub Pages 完成部署

   **页面空白：**
   - 打开浏览器开发者工具（F12）
   - 查看 Console 是否有 JavaScript 错误
   - 检查 Network 标签，确认所有资源都成功加载

   **数据不显示：**
   - 确认 `reports.js` 文件存在且格式正确
   - 确认 `js/main.js` 正确加载了 `reports.js`
   - 检查浏览器控制台的错误信息

### 🔍 验证命令

```bash
# 检查必需文件
ls -la docs/index.html docs/.nojekyll docs/reports.js docs/js/main.js docs/css/style.css

# 检查文件是否已提交
git status docs/

# 本地测试
python3 -m http.server 8000 --directory docs
# 然后访问 http://localhost:8000
```

### 📝 更新网站

每次生成新周报后，运行：

```bash
# 1. 生成周报
python scripts/weekly_report_generator_v2.py

# 2. 转换为 HTML
python scripts/convert_to_html.py

# 3. 更新网站数据
python scripts/update_website.py

# 4. 提交到 GitHub
git add docs/
git commit -m "Update weekly reports"
git push
```

GitHub Pages 会自动重新部署（通常需要几分钟）。
