#!/bin/bash
# 快速导航脚本

echo "🚀 稳定币情报项目快速导航"
echo ""
echo "选择你想去的地方："
echo "1. 查看项目结构"
echo "2. 进入 notes 文件夹"
echo "3. 进入 data/raw 文件夹"
echo "4. 进入 scripts 文件夹"
echo "5. 查看 TODO 列表"
echo "6. 查看数据源清单"
echo ""
read -p "请输入数字 (1-6): " choice

case $choice in
  1)
    tree -L 2
    ;;
  2)
    cd notes && pwd && ls
    ;;
  3)
    cd data/raw && pwd && ls
    ;;
  4)
    cd scripts && pwd && ls
    ;;
  5)
    cat notes/todo.md
    ;;
  6)
    cat notes/data-sources.md
    ;;
  *)
    echo "无效选项"
    ;;
esac