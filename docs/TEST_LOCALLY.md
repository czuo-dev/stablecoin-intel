# 本地测试网站

## 方法1：使用 Python（推荐）

```bash
cd /Users/changbaizuo_1/projects/stablecoin-intel
python3 -m http.server 8000 --directory docs
```

然后访问：http://localhost:8000

## 方法2：使用启动脚本

```bash
./scripts/start_server.sh
```

## 方法3：使用 Node.js（如果已安装）

```bash
cd docs
npx http-server -p 8000
```

## 重要说明

⚠️ **这个项目不需要 Jekyll！**

- 这是纯静态 HTML/JS/CSS 网站
- `.nojekyll` 文件告诉 GitHub Pages 不要使用 Jekyll
- 不需要 `Gemfile` 或 `bundle install`
- 直接使用简单的 HTTP 服务器即可

## 测试清单

访问 http://localhost:8000 后检查：

- [ ] 页面能正常加载
- [ ] 样式文件加载（CSS）
- [ ] JavaScript 文件加载
- [ ] 周报列表显示
- [ ] 点击链接能跳转到周报页面

如果本地测试正常但 GitHub Pages 404，通常是 GitHub 设置问题。
