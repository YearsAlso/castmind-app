import React, { useState, useEffect } from 'react';
import './App.css';

// 类型定义
interface Feed {
  id: string;
  name: string;
  url: string;
  category: string;
  status: string;
  items_count: number;
}

interface Article {
  id: string;
  title: string;
  summary: string;
  url: string;
  published_at: string | null;
  read_status: boolean;
}

const CastMindApp: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'feeds' | 'articles'>('dashboard');
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(false); // 个性功能：深色模式

  // 模拟数据
  const mockFeeds: Feed[] = [
    {
      id: '1',
      name: '技术博客',
      url: 'https://example.com/feed.xml',
      category: '技术',
      status: 'active',
      items_count: 45
    },
    {
      id: '2',
      name: '新闻聚合',
      url: 'https://news.example.com/rss',
      category: '新闻',
      status: 'active',
      items_count: 32
    },
    {
      id: '3',
      name: '科技媒体',
      url: 'https://tech.example.com/feed',
      category: '科技',
      status: 'error',
      items_count: 0
    }
  ];

  const mockArticles: Article[] = [
    {
      id: '1',
      title: 'AI技术的最新突破与应用前景',
      summary: '本文介绍了人工智能领域的最新研究成果和实际应用案例...',
      url: 'https://example.com/article1',
      published_at: '2024-02-20T10:30:00Z',
      read_status: false
    },
    {
      id: '2',
      title: 'Web开发趋势：2024年前端技术展望',
      summary: '分析2024年前端开发的主要趋势和技术发展方向...',
      url: 'https://example.com/article2',
      published_at: '2024-02-19T14:20:00Z',
      read_status: true
    },
    {
      id: '3',
      title: '云计算成本优化策略与实践',
      summary: '分享如何在云环境中优化成本并提高资源利用率...',
      url: 'https://example.com/article3',
      published_at: '2024-02-18T09:15:00Z',
      read_status: false
    }
  ];

  useEffect(() => {
    // 加载模拟数据
    setLoading(true);
    setTimeout(() => {
      setFeeds(mockFeeds);
      setArticles(mockArticles);
      setLoading(false);
    }, 1000);
  }, []);

  // 渲染仪表板
  const renderDashboard = () => (
    <div className="dashboard">
      <div className="welcome-section">
        <h1>🎯 CastMind</h1>
        <p className="subtitle">智能内容聚合与解析平台</p>
        
        <div className="stats-grid">
          <div className="stat-card">
            <h3>📰 订阅源</h3>
            <div className="stat-value">{feeds.length}</div>
            <div className="stat-detail">
              <span className="success">活跃: {feeds.filter(f => f.status === 'active').length}</span>
              <span className="error">错误: {feeds.filter(f => f.status === 'error').length}</span>
            </div>
          </div>
          
          <div className="stat-card">
            <h3>📄 文章</h3>
            <div className="stat-value">{articles.length}</div>
            <div className="stat-detail">
              <span>已读: {articles.filter(a => a.read_status).length}</span>
              <span>未读: {articles.filter(a => !a.read_status).length}</span>
            </div>
          </div>
          
          <div className="stat-card">
            <h3>🔄 状态</h3>
            <div className="stat-value">运行中</div>
            <div className="stat-detail">
              <span>系统正常</span>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="section">
          <h3>📊 快速开始</h3>
          <div className="quick-actions">
            <button className="btn" onClick={() => setActiveTab('feeds')}>
              📰 管理订阅源
            </button>
            <button className="btn btn-secondary">
              🎯 创建示例
            </button>
            <button className="btn btn-outline">
              🔄 开始抓取
            </button>
          </div>
        </div>

        <div className="section">
          <h3>📰 最新文章</h3>
          <div className="article-list">
            {articles.slice(0, 3).map(article => (
              <div key={article.id} className="article-item">
                <h4>{article.title}</h4>
                <p>{article.summary}</p>
                <div className="article-footer">
                  <span className="article-meta">
                    {article.published_at ? new Date(article.published_at).toLocaleDateString() : '未知时间'}
                  </span>
                  <a href={article.url} target="_blank" rel="noopener noreferrer" className="btn-link">
                    阅读原文
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // 渲染订阅源管理
  const renderFeeds = () => (
    <div className="feeds-page">
      <div className="page-header">
        <h2>📰 订阅源管理</h2>
        <div className="header-actions">
          <button className="btn">+ 添加订阅源</button>
          <button className="btn btn-secondary">🎯 创建示例</button>
        </div>
      </div>

      <div className="feeds-list">
        {feeds.map(feed => (
          <div key={feed.id} className="feed-card">
            <div className="feed-header">
              <h3>{feed.name}</h3>
              <div className="feed-actions">
                <button className="btn btn-sm">抓取</button>
                <button className="btn btn-sm btn-danger">删除</button>
              </div>
            </div>
            
            <div className="feed-info">
              <div className="info-row">
                <span className="label">URL:</span>
                <a href={feed.url} target="_blank" rel="noopener noreferrer" className="url">
                  {feed.url}
                </a>
              </div>
              
              <div className="info-row">
                <span className="label">分类:</span>
                <span className="category">{feed.category}</span>
              </div>
              
              <div className="info-row">
                <span className="label">状态:</span>
                <span className={`status ${feed.status}`}>
                  {feed.status === 'active' ? '活跃' : '错误'}
                </span>
              </div>
              
              <div className="info-row">
                <span className="label">文章数量:</span>
                <span className="count">{feed.items_count}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // 渲染文章列表
  const renderArticles = () => (
    <div className="articles-page">
      <div className="page-header">
        <h2>📄 文章管理</h2>
        <div className="header-actions">
          <div className="search-box">
            <input type="text" placeholder="搜索文章..." />
            <button className="btn btn-sm">搜索</button>
          </div>
          <span className="total-count">共 {articles.length} 篇文章</span>
        </div>
      </div>

      <div className="articles-list">
        {articles.map(article => (
          <div key={article.id} className="article-card">
            <div className="article-header">
              <h3>{article.title}</h3>
              <span className={`read-status ${article.read_status ? 'read' : 'unread'}`}>
                {article.read_status ? '已读' : '未读'}
              </span>
            </div>
            
            <p className="article-summary">{article.summary}</p>
            
            <div className="article-footer">
              <div className="article-meta">
                <span>发布时间: {article.published_at ? new Date(article.published_at).toLocaleDateString() : '未知'}</span>
              </div>
              
              <div className="article-actions">
                <a href={article.url} target="_blank" rel="noopener noreferrer" className="btn">
                  阅读原文
                </a>
                {!article.read_status && (
                  <button className="btn btn-outline">标记已读</button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className={`castmind-app ${darkMode ? 'dark-mode' : ''}`}>
      {/* 导航栏 */}
      <nav className="navbar">
        <div className="nav-brand">
          <div className="logo">
            <span className="logo-icon">🎯</span>
            <div className="logo-text">
              <h1>CastMind</h1>
              <p>智能内容聚合平台</p>
              <span className="branch-badge">🎭 个性分支</span>
            </div>
          </div>
        </div>
        
        <div className="nav-tabs">
          <button 
            className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 仪表板
          </button>
          <button 
            className={`tab ${activeTab === 'feeds' ? 'active' : ''}`}
            onClick={() => setActiveTab('feeds')}
          >
            📰 订阅源
          </button>
          <button 
            className={`tab ${activeTab === 'articles' ? 'active' : ''}`}
            onClick={() => setActiveTab('articles')}
          >
            📄 文章
          </button>
        </div>
        
        <div className="nav-actions">
          {/* 个性功能：主题切换 */}
          <button 
            className="btn btn-sm" 
            onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? '切换到浅色模式' : '切换到深色模式'}
          >
            {darkMode ? '☀️ 浅色' : '🌙 深色'}
          </button>
          <button className="btn btn-sm" onClick={() => window.location.reload()}>
            🔄 刷新
          </button>
        </div>
      </nav>

      {/* 主要内容 */}
      <main className="main-content">
        {loading ? (
          <div className="loading">
            <div className="loading-spinner"></div>
            <p>加载中...</p>
          </div>
        ) : error ? (
          <div className="error-alert">
            <p>{error}</p>
            <button onClick={() => setError(null)}>重试</button>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && renderDashboard()}
            {activeTab === 'feeds' && renderFeeds()}
            {activeTab === 'articles' && renderArticles()}
          </>
        )}
      </main>

      {/* 页脚 */}
      <footer className="footer">
        <p>🎯 CastMind - 智能内容聚合与解析平台</p>
        <p>版本 1.0.0 · © 2024 CastMind</p>
      </footer>
    </div>
  );
};

export default CastMindApp;