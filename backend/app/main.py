# -*- coding: utf-8 -*-
"""
【FastAPI主应用 - main.py】
================================
这是后端应用的入口文件，创建和配置FastAPI应用。

【学习要点】
1. FastAPI: 高性能的现代Python Web框架
2. CORS中间件: 解决跨域请求问题
3. 路由注册: 将API路由模块注册到主应用
4. 生命周期事件: 应用启动时初始化数据库

【应用结构】
- 创建FastAPI应用实例
- 配置CORS跨域
- 初始化数据库
- 注册API路由
- 定义根路由和健康检查
"""

import sys
import os

# 添加项目路径到Python模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# 【导入必要的库】
# ============================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import setup_logger

# 创建日志记录器，用于记录应用运行信息
logger = setup_logger(__name__)

# 导入配置和路由模块
from app.config import ALLOWED_ORIGINS
from app.db.models import init_db
from app.api import auth, file, parse, record, visualize

# ============================================
# 【创建FastAPI应用】
# ============================================
# title: API文档标题
# version: API版本号
app = FastAPI(title="Code Analysis Visualizer", version="1.0.0")

# ============================================
# 【配置CORS中间件】
# ============================================
# CORS (Cross-Origin Resource Sharing) 跨域资源共享
# 前端(Vue)和后端(FastAPI)运行在不同端口，需要CORS允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 允许的域名列表
    allow_credentials=True,         # 允许携带Cookie/认证信息
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 允许的HTTP方法
    allow_headers=["*"],            # 允许所有请求头
)

# ============================================
# 【初始化数据库】
# ============================================
# 应用启动时创建数据库表
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

# ============================================
# 【注册API路由】
# ============================================
# include_router: 将路由模块注册到应用
# 每个路由模块处理不同的业务功能
app.include_router(auth.router)      # 用户认证：注册、登录、获取用户信息
app.include_router(file.router)      # 文件管理：上传、查看、删除文件
app.include_router(parse.router)     # 代码解析：Python和C代码分析
app.include_router(record.router)    # 分析记录：保存和查看分析历史
app.include_router(visualize.router) # 可视化：生成可视化数据

# ============================================
# 【根路由】
# ============================================
# 访问 http://localhost:9999/ 会返回这个信息
@app.get("/")
def root():
    """
    API根路由
    
    【用途】
    提供API基本信息，方便用户确认服务是否正常运行
    """
    return {"message": "Code Analysis Visualizer API", "version": "1.0.0"}

# ============================================
# 【健康检查路由】
# ============================================
# 用于监控服务状态，部署时常用
@app.get("/health")
def health_check():
    """
    健康检查路由
    
    【用途】
    监控系统、负载均衡器检查服务是否健康运行
    返回 {"status": "healthy"} 表示服务正常
    """
    return {"status": "healthy"}