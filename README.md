# 🎯 CastMind - 智能内容聚合平台

## 📋 项目概述

**CastMind** 是一个现代化的内容聚合与解析平台，帮助用户高效管理订阅源、抓取内容并监控进度。

### ✨ 核心功能
- ✅ **订阅源管理** - 添加、编辑、删除 RSS/Atom 订阅源
- ✅ **内容抓取** - 自动定时抓取订阅源内容
- ✅ **文章管理** - 查看、搜索、标记文章- ✅ **进度监控** - 实时查看抓取进度和状态
- ✅ **系统统计** - 数据统计和健康检查
- ✅ **响应式界面** - 适配桌面和移动设备

## 🏗️ 技术栈

### 前端
- **React 19** - 现代化的前端框架
- **TypeScript** - 类型安全的 JavaScript
- **Vite** - 快速的构建工具
- **CSS3** - 现代化的样式设计

### 后端
- **FastAPI** - 高性能的 Python Web 框架
- **SQLite** - 轻量级数据库
- **Uvicorn** - ASGI 服务器

## 📁 项目结构

```
castmind/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── App.tsx          # 主应用组件
│   │   ├── App.css          # 主样式文件
│   │   └── main.tsx         # 入口文件
│   ├── package.json         # 前端依赖
│   ├── vite.config.ts       # Vite 配置
│   └── tsconfig.json        # TypeScript 配置
│
├── backend/                 # 后端项目
│   ├── main.py             # 后端主程序
│   └── requirements.txt    # Python 依赖
│
├── docs/                   # 项目文档
├── scripts/               # 工具脚本
└── README.md             # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

确保已安装：
- **Node.js** (v18+)
- **Python** (v3.8+)
- **npm** 或 **yarn**

### 2. 前端安装和运行

```bash
# 进入前端目录
cd castmind/frontend

# 安装依赖
npm install

# 开发模式运行
npm run dev

# 构建生产版本
npm run build
```

### 3. 后端安装和运行

```bash
# 进入后端目录
cd castmind/backend

# 安装依赖
pip install fastapi uvicorn sqlite3

# 运行后端服务
python main.py

# 或指定端口
python main.py --host 0.0.0.0 --port 8888
```

### 4. 集成运行（推荐）

```bash
# 构建前端
cd castmind/frontend && npm run build

# 启动后端（自动服务前端）
cd castmind/backend && python main.py
```

## 🌐 访问地址

- **前端界面**: http://localhost:8888
- **API 文档**: http://localhost:8888/api/docs
- **健康检查**: http://localhost:8888/api/health

## 📊 API 接口

### 基础接口
- `GET /api/hello` - 测试接口
- `GET /api/info` - 项目信息
- `GET /api/health` - 健康检查

### 订阅源管理
- `GET /api/feeds` - 获取订阅源列表
- `POST /api/feeds` - 创建订阅源
- `GET /api/feeds/{id}` - 获取单个订阅源
- `DELETE /api/feeds/{id}` - 删除订阅源

### 文章管理
- `GET /api/articles` - 获取文章列表
- `PUT /api/articles/{id}/read` - 标记文章阅读状态

### 系统功能
- `GET /api/stats` - 获取系统统计
- `POST /api/samples/feeds` - 创建示例订阅源

## 🎨 界面预览

### 仪表板
- 系统概览和统计数据
- 快速操作按钮
- 最新文章列表

### 订阅源管理
- 订阅源列表展示
- 添加/编辑/删除功能
- 状态监控

### 文章管理
- 文章列表和搜索
- 阅读状态管理
- 原文链接跳转

## 🔧 开发指南

### 前端开发
```bash
# 开发模式（热重载）
cd frontend && npm run dev

# 代码检查
npm run lint

# 清理构建
npm run clean
```

### 后端开发
```python
# 开发模式运行
uvicorn main:app --reload --host 0.0.0.0 --port 8888

# 查看API文档
# 访问 http://localhost:8888/api/docs
```

### 数据库操作
```python
# 数据库文件: castmind.db
# 初始化数据库会自动创建表结构
# 数据模型在 main.py 中定义
```

## 📈 系统特性

### 性能优化
- ✅ 前端代码分割和懒加载
- ✅ 后端异步处理
- ✅ 数据库连接池
- ✅ 静态文件缓存

### 用户体验
- ✅ 响应式设计
- ✅ 加载状态提示
- ✅ 错误处理
- ✅ 键盘导航支持

### 安全性
- ✅ CORS 配置
- ✅ 输入验证
- ✅ SQL 注入防护
- ✅ 错误信息过滤

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持与反馈

- **问题报告**: 请使用 GitHub Issues
- **功能建议**: 欢迎提交 Pull Request
- **文档改进**: 帮助我们完善文档

## 🎯 下一步计划

- [ ] 定时抓取任务
- [ ] 内容解析增强
- [ ] 用户认证系统
- [ ] 多语言支持
- [ ] 移动端应用
- [ ] 数据导出功能

---

**🎯 CastMind - 让内容聚合更智能！**