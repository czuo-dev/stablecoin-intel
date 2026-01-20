#!/bin/bash
# 启动本地Web服务器

PORT=8000
DIR="docs"

# 检查端口是否被占用
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "⚠️  端口 $PORT 已被占用，正在终止..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

# 检查目录是否存在
if [ ! -d "$DIR" ]; then
    echo "❌ 目录 $DIR 不存在"
    exit 1
fi

echo "🚀 启动Web服务器..."
echo "📁 目录: $DIR"
echo "🌐 地址: http://localhost:$PORT"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
cd "$(dirname "$0")/.."
python3 -m http.server $PORT --directory $DIR
