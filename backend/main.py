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
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()