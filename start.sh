#!/bin/bash
# CastMind 启动脚本

set -e

echo "🎯 CastMind 智能内容聚合平台启动中..."
echo "=========================================="

# 检查前端是否已构建
FRONTEND_DIST="frontend/dist"
if [ ! -d "$FRONTEND_DIST" ]; then
    echo "⚠️  前端未构建，正在构建前端..."
    cd frontend
    echo "📦 安装前端依赖..."
    npm install
    echo "🔨 构建前端..."
    npm run build
    cd ..
    echo "✅ 前端构建完成"
else
    echo "✅ 前端已构建"
fi

# 检查Python依赖
echo "🐍 检查Python依赖..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "📦 安装FastAPI..."
    pip3 install fastapi uvicorn
fi

# 启动后端服务
echo "🚀 启动后端服务..."
cd backend
python3 main.py

echo "🎉 CastMind 启动完成！"
echo "🌐 访问地址: http://localhost:8888"
echo "📚 API文档: http://localhost:8888/api/docs"