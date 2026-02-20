#!/bin/bash
# CastMind 清理脚本

echo "🧹 清理 CastMind 项目..."
echo "=========================================="

# 清理前端构建文件
echo "🗑️  清理前端构建文件..."
rm -rf frontend/dist
rm -rf frontend/node_modules

# 清理后端数据库
echo "🗑️  清理后端数据库..."
rm -f backend/castmind.db

# 清理临时文件
echo "🗑️  清理临时文件..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name ".DS_Store" -delete

echo "✅ 清理完成！"
echo ""
echo "📝 重新启动:"
echo "   1. 构建前端: cd frontend && npm install && npm run build"
echo "   2. 启动后端: cd backend && python main.py"
echo "   3. 或使用启动脚本: ./start.sh"