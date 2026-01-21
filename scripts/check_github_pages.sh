#!/bin/bash
# GitHub Pages 诊断脚本

echo "=========================================="
echo "GitHub Pages 诊断检查"
echo "=========================================="
echo ""

# 1. 检查必需文件
echo "1. 检查必需文件："
files=("docs/index.html" "docs/.nojekyll" "docs/reports.js" "docs/js/main.js" "docs/css/style.css")
all_ok=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (缺失)"
        all_ok=false
    fi
done

echo ""

# 2. 检查文件是否在 git 中
echo "2. 检查文件是否已提交到 git："
for file in "${files[@]}"; do
    if git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
        echo "   ✅ $file (已提交)"
    else
        echo "   ❌ $file (未提交)"
        all_ok=false
    fi
done

echo ""

# 3. 检查当前分支
echo "3. 当前分支："
current_branch=$(git branch --show-current)
echo "   📍 $current_branch"
if [ "$current_branch" != "main" ]; then
    echo "   ⚠️  警告: GitHub Pages 通常需要 main 分支"
fi

echo ""

# 4. 检查 .nojekyll 文件内容
echo "4. 检查 .nojekyll 文件："
if [ -f "docs/.nojekyll" ]; then
    size=$(stat -f%z "docs/.nojekyll" 2>/dev/null || stat -c%s "docs/.nojekyll" 2>/dev/null)
    if [ "$size" -eq 0 ]; then
        echo "   ✅ .nojekyll 文件存在且为空（正确）"
    else
        echo "   ⚠️  .nojekyll 文件不为空"
    fi
else
    echo "   ❌ .nojekyll 文件不存在"
    all_ok=false
fi

echo ""

# 5. 检查 index.html 位置
echo "5. 检查 index.html 位置："
if [ -f "docs/index.html" ]; then
    echo "   ✅ index.html 在 docs/ 目录下（正确）"
else
    echo "   ❌ index.html 不在正确位置"
    all_ok=false
fi

echo ""

# 总结
echo "=========================================="
if [ "$all_ok" = true ]; then
    echo "✅ 所有检查通过！"
    echo ""
    echo "如果 GitHub Pages 还是 404，请："
    echo "1. 确认 GitHub 仓库设置："
    echo "   - Settings → Pages"
    echo "   - Source: Deploy from a branch"
    echo "   - Branch: main"
    echo "   - Folder: /docs"
    echo ""
    echo "2. 触发重新部署："
    echo "   git commit --allow-empty -m 'Trigger GitHub Pages rebuild'"
    echo "   git push"
    echo ""
    echo "3. 等待 5-10 分钟"
    echo "4. 访问: https://czuo-dev.github.io/stablecoin-intel/"
else
    echo "❌ 发现问题，请先修复上述错误"
fi
echo "=========================================="
