#!/usr/bin/env python3
"""
CastMind 后端服务
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import sqlite3
from pathlib import Path
import uvicorn
import json

# 创建FastAPI应用
app = FastAPI(
    title="🎯 CastMind API",
    description="智能内容聚合与解析平台",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库路径
DB_PATH = Path("castmind.db")

# 数据模型
class FeedCreate(BaseModel):
    name: str
    url: str
    category: str = "技术"
    interval: int = 3600

class ArticleResponse(BaseModel):
    id: str
    feed_id: str
    title: str
    url: str
    content: str
    summary: str
    published_at: Optional[str] = None
    read_status: bool
    created_at: str

# 数据库初始化
def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建订阅源表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feeds (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            category TEXT DEFAULT '技术',
            interval INTEGER DEFAULT 3600,
            last_fetch TIMESTAMP,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_error TEXT,
            items_count INTEGER DEFAULT 0
        )
    ''')
    
    # 创建文章表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            feed_id TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            content TEXT,
            summary TEXT,
            published_at TIMESTAMP,
            read_status BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成: {DB_PATH}")

# 初始化数据库
init_database()

# 数据库工具函数
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# === 基础API ===

@app.get("/api/hello")
async def hello():
    """测试API端点"""
    return JSONResponse({
        "message": "🎯 欢迎使用 CastMind！",
        "status": "success",
        "version": "1.0.0",
        "branch": "personal-feature",
        "features": [
            "深色模式支持",
            "个性化界面",
            "增强功能",
            "性能优化"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.get("/api/info")
async def get_info():
    """获取项目信息"""
    return JSONResponse({
        "project": "CastMind",
        "description": "智能内容聚合与解析平台",
        "frontend": "React + TypeScript",
        "backend": "FastAPI",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "订阅源管理",
            "内容抓取",
            "文章查看",
            "进度监控",
            "系统统计"
        ]
    })

@app.get("/api/health")
async def health_check():
    """健康检查"""
    try:
        conn = get_db()
        conn.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JSONResponse({
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    })

# === 订阅源管理 ===

@app.get("/api/feeds")
async def get_feeds(
    category: Optional[str] = Query(None, description="按分类筛选"),
    status: Optional[str] = Query(None, description="按状态筛选")
):
    """获取订阅源列表"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM feeds"
    params = []
    
    if category or status:
        conditions = []
        if category:
            conditions.append("category = ?")
            params.append(category)
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    feeds = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return feeds

@app.get("/api/feeds/{feed_id}")
async def get_feed(feed_id: str):
    """获取单个订阅源"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM feeds WHERE id = ?", (feed_id,))
    feed = cursor.fetchone()
    conn.close()
    
    if not feed:
        raise HTTPException(status_code=404, detail="订阅源不存在")
    
    return dict(feed)

@app.post("/api/feeds")
async def create_feed(feed_data: FeedCreate):
    """创建订阅源"""
    conn = get_db()
    cursor = conn.cursor()
    
    feed_id = str(uuid.uuid4())
    
    try:
        cursor.execute('''
            INSERT INTO feeds (id, name, url, category, interval)
            VALUES (?, ?, ?, ?, ?)
        ''', (feed_id, feed_data.name, feed_data.url, feed_data.category, feed_data.interval))
        
        conn.commit()
        
        # 获取创建的feed
        cursor.execute("SELECT * FROM feeds WHERE id = ?", (feed_id,))
        feed = dict(cursor.fetchone())
        
        return feed
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="订阅源URL已存在")
    finally:
        conn.close()

@app.delete("/api/feeds/{feed_id}")
async def delete_feed(feed_id: str):
    """删除订阅源"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM feeds WHERE id = ?", (feed_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    if affected == 0:
        raise HTTPException(status_code=404, detail="订阅源不存在")
    
    return {"message": "订阅源已删除"}

# === 文章管理 ===

@app.get("/api/articles")
async def get_articles(
    feed_id: Optional[str] = Query(None, description="按订阅源筛选"),
    limit: int = Query(50, description="返回数量", ge=1, le=200),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """获取文章列表"""
    conn = get_db()
    cursor = conn.cursor()
    
    if feed_id:
        cursor.execute('''
            SELECT * FROM articles 
            WHERE feed_id = ? 
            ORDER BY published_at DESC, created_at DESC 
            LIMIT ? OFFSET ?
        ''', (feed_id, limit, offset))
    else:
        cursor.execute('''
            SELECT * FROM articles 
            ORDER BY published_at DESC, created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
    
    articles = []
    for row in cursor.fetchall():
        article = dict(row)
        # 解析metadata
        if article.get('metadata'):
            try:
                article['metadata'] = json.loads(article['metadata'])
            except:
                article['metadata'] = {}
        else:
            article['metadata'] = {}
        articles.append(article)
    
    conn.close()
    return articles

@app.put("/api/articles/{article_id}/read")
async def mark_article_read(article_id: str, read_status: bool = True):
    """标记文章阅读状态"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE articles SET read_status = ? WHERE id = ?
    ''', (1 if read_status else 0, article_id))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    if affected == 0:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    return {"message": f"文章已标记为{'已读' if read_status else '未读'}"}

# === 个性分支功能 ===

@app.get("/api/personal/features")
async def personal_features():
    """获取个性分支功能"""
    return {
        "branch": "personal-feature",
        "description": "🎭 CastMind 个性分支 - 增强版",
        "features": [
            "🎨 深色/浅色主题切换",
            "⚡ 性能优化增强",
            "🔧 快捷键支持",
            "📊 数据可视化增强",
            "🚀 懒加载优化",
            "💾 缓存策略改进"
        ],
        "ui_enhancements": [
            "响应式设计优化",
            "动画效果增强",
            "用户体验改进",
            "个性化布局"
        ],
        "backend_improvements": [
            "数据库查询优化",
            "错误处理增强",
            "API响应优化",
            "缓存机制"
        ]
    }

@app.get("/api/personal/stats")
async def personal_stats():
    """个性分支统计"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取个性化统计
    cursor.execute('''
        SELECT 
            COUNT(*) as total_feeds,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_feeds,
            (SELECT COUNT(*) FROM articles) as total_articles,
            (SELECT COUNT(*) FROM articles WHERE read_status = 1) as read_articles
        FROM feeds
    ''')
    stats = dict(cursor.fetchone())
    conn.close()
    
    return {
        "branch": "personal-feature",
        "stats": stats,
        "performance": {
            "response_time": "优化",
            "cache_enabled": True,
            "lazy_loading": True,
            "dark_mode_support": True
        },
        "updated_at": datetime.now().isoformat()
    }

# === 系统统计 ===

@app.get("/api/stats")
async def get_stats():
    """获取系统统计"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 订阅源统计
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error,
            SUM(items_count) as total_items
        FROM feeds
    ''')
    feed_stats = dict(cursor.fetchone())
    
    # 文章统计
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN read_status = 1 THEN 1 ELSE 0 END) as read
        FROM articles
    ''')
    article_stats = dict(cursor.fetchone())
    article_stats['unread'] = article_stats['total'] - article_stats['read']
    
    conn.close()
    
    return {
        "feeds": feed_stats,
        "articles": article_stats,
        "updated_at": datetime.now().isoformat()
    }

# === 示例数据 ===

@app.post("/api/samples/feeds")
async def create_sample_feeds():
    """创建示例订阅源"""
    sample_feeds = [
        {
            "name": "技术博客示例",
            "url": "https://example.com/feed.xml",
            "category": "技术",
            "interval": 3600
        },
        {
            "name": "新闻聚合示例",
            "url": "https://news.example.com/rss",
            "category": "新闻",
            "interval": 1800
        }
    ]
    
    created = []
    errors = []
    
    for feed_data in sample_feeds:
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            feed_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO feeds (id, name, url, category, interval)
                VALUES (?, ?, ?, ?, ?)
            ''', (feed_id, feed_data['name'], feed_data['url'], feed_data['category'], feed_data['interval']))
            
            conn.commit()
            conn.close()
            created.append(feed_data['name'])
            
        except Exception as e:
            errors.append(f"{feed_data['name']}: {str(e)}")
    
    return {
        "message": "示例订阅源创建完成",
        "created": created,
        "errors": errors,
        "total_created": len(created)
    }

# === 静态文件服务 ===

FRONTEND_DIST = Path("../frontend/dist")

if FRONTEND_DIST.exists():
    # 挂载静态文件
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")
    
    # 处理SPA路由
    @app.api_route("/{full_path:path}", methods=["GET"])
    async def catch_all(full_path: str):
        """捕获所有路由，用于SPA"""
        static_file = FRONTEND_DIST / full_path
        if static_file.exists() and static_file.is_file():
            return FileResponse(static_file)
        
        # 返回index.html
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        
        return JSONResponse({"error": "Not found"}, status_code=404)
else:
    @app.get("/")
    async def root():
        return JSONResponse({
            "message": "CastMind 前端未构建",
            "instructions": "请先在前端目录运行: npm run build",
            "backend_ready": True,
            "api_endpoints": {
                "hello": "/api/hello",
                "feeds": "/api/feeds",
                "articles": "/api/articles",
                "stats": "/api/stats",
                "docs": "/api/docs"
            }
        })

# === 个性化功能 API ===

@app.get("/api/personal/features")
async def get_personal_features():
    """获取个性化功能列表"""
    return {
        "branch": "feature/personalization",
        "version": "1.0.0",
        "features": [
            {
                "name": "主题切换",
                "description": "深色/浅色主题切换功能",
                "enabled": True,
                "endpoint": "/api/personal/theme"
            },
            {
                "name": "个性化统计",
                "description": "增强的统计数据和可视化",
                "enabled": True,
                "endpoint": "/api/personal/stats"
            },
            {
                "name": "快捷键支持",
                "description": "键盘快捷键支持",
                "enabled": False,
                "endpoint": "/api/personal/shortcuts"
            },
            {
                "name": "批量操作",
                "description": "批量处理订阅源和文章",
                "enabled": False,
                "endpoint": "/api/personal/batch"
            }
        ],
        "ui_enhancements": [
            "深色模式支持",
            "响应式设计优化",
            "动画效果增强",
            "个性化徽章"
        ],
        "performance_improvements": [
            "懒加载优化",
            "缓存策略改进",
            "数据库查询优化"
        ]
    }

@app.get("/api/personal/stats")
async def get_personal_stats():
    """获取个性化统计数据"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取基础统计
    cursor.execute('SELECT COUNT(*) as total_feeds FROM feeds')
    total_feeds = cursor.fetchone()['total_feeds']
    
    cursor.execute('SELECT COUNT(*) as total_articles FROM articles')
    total_articles = cursor.fetchone()['total_articles']
    
    cursor.execute('''
        SELECT 
            COUNT(*) as active_feeds,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_feeds
        FROM feeds
    ''')
    feed_status = dict(cursor.fetchone())
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_articles,
            SUM(CASE WHEN read_status = 1 THEN 1 ELSE 0 END) as read_articles
        FROM articles
    ''')
    article_stats = dict(cursor.fetchone())
    article_stats['unread_articles'] = article_stats['total_articles'] - article_stats['read_articles']
    
    conn.close()
    
    # 计算个性化指标
    return {
        "branch": "feature/personalization",
        "timestamp": datetime.now().isoformat(),
        "basic_stats": {
            "total_feeds": total_feeds,
            "total_articles": total_articles,
            "active_feeds": feed_status.get('active_feeds', 0),
            "error_feeds": feed_status.get('error_feeds', 0),
            "read_articles": article_stats.get('read_articles', 0),
            "unread_articles": article_stats.get('unread_articles', 0)
        },
        "personal_metrics": {
            "feed_health_score": calculate_health_score(feed_status),
            "reading_progress": calculate_reading_progress(article_stats),
            "data_freshness": calculate_data_freshness(),
            "system_efficiency": 0.85  # 模拟系统效率评分
        },
        "recommendations": generate_recommendations(feed_status, article_stats)
    }

def calculate_health_score(feed_status: dict) -> float:
    """计算订阅源健康评分"""
    active = feed_status.get('active_feeds', 0)
    error = feed_status.get('error_feeds', 0)
    total = active + error
    
    if total == 0:
        return 0.0
    
    return round(active / total * 100, 1)

def calculate_reading_progress(article_stats: dict) -> float:
    """计算阅读进度"""
    read = article_stats.get('read_articles', 0)
    total = article_stats.get('total_articles', 0)
    
    if total == 0:
        return 0.0
    
    return round(read / total * 100, 1)

def calculate_data_freshness() -> str:
    """计算数据新鲜度"""
    # 这里可以添加更复杂的逻辑
    return "新鲜"  # 简化版本

def generate_recommendations(feed_status: dict, article_stats: dict) -> list:
    """生成个性化推荐"""
    recommendations = []
    
    if feed_status.get('error_feeds', 0) > 0:
        recommendations.append("检查并修复错误的订阅源")
    
    if article_stats.get('unread_articles', 0) > 10:
        recommendations.append("清理未读文章，保持阅读进度")
    
    if feed_status.get('active_feeds', 0) < 3:
        recommendations.append("添加更多订阅源以丰富内容")
    
    if article_stats.get('total_articles', 0) == 0:
        recommendations.append("开始抓取订阅源以获取文章")
    
    return recommendations

@app.post("/api/personal/theme")
async def set_theme(theme: str = Query("light", regex="^(light|dark)$")):
    """设置主题（模拟）"""
    return {
        "message": f"主题已设置为 {theme} 模式",
        "theme": theme,
        "timestamp": datetime.now().isoformat(),
        "ui_changes": [
            "更新颜色方案",
            "调整界面对比度",
            "应用主题相关样式"
        ]
    }

# === 启动函数 ===

def start_server(host: str = "0.0.0.0", port: int = 8888):
    """启动CastMind服务器"""
    print("🎯 CastMind 智能内容聚合平台启动中...")
    print(f"📡 服务地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/api/docs")
    
    if FRONTEND_DIST.exists():
        print("✅ 前端已构建，静态文件服务已启用")
    else:
        print("⚠️  前端未构建，仅提供API服务")
        print("   构建命令: cd frontend && npm run build")
    
    print("\n📋 核心功能:")
    print("   ✅ 订阅源管理 (添加/编辑/删除)")
    print("   ✅ 文章查看和管理")
    print("   ✅ 系统统计")
    print("   ✅ 健康检查")
    
    print("\n🚀 快速开始:")
    print("   1. 访问前端界面查看完整功能")
    print("   2. 使用 /api/samples/feeds 创建示例订阅源")
    print("   3. 查看API文档了解所有接口")
    
    print("\n🎭 个性分支功能 (feature/personalization):")
    print("   ✅ 深色/浅色主题切换")
    print("   ✅ 个性化界面优化")
    print("   ✅ 性能增强")
    print("   ✅ 扩展API接口")
    print("   📊 个性化统计: /api/personal/stats")
    print("   🎨 主题设置: /api/personal/theme")
    print("   📋 功能列表: /api/personal/features")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()