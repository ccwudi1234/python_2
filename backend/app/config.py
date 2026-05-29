# -*- coding: utf-8 -*-
"""
【配置文件 - config.py】
================================
这是整个后端应用的核心配置文件。
它负责管理所有环境变量、数据库连接、安全密钥等关键配置。

【学习要点】
1. dotenv: 用于从.env文件加载环境变量，保护敏感信息
2. Path: Python的路径处理库，用于构建文件路径
3. 环境区分: 开发环境(development)和生产环境(production)的配置分离

【应用场景】
- 数据库连接配置
- JWT认证密钥配置  
- CORS跨域配置
- 文件上传目录配置
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件中的环境变量
# .env文件用于存储敏感信息（如密钥、密码），不应提交到git
load_dotenv()

# ============================================
# 【路径配置】
# ============================================
# BASE_DIR: backend根目录
# Path(__file__)获取当前文件路径（app/config.py），向上两级到 backend/
BASE_DIR = Path(__file__).parent.parent

# UPLOAD_DIR: 文件上传目录
UPLOAD_DIR = BASE_DIR / "app" / "static"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# DB_DIR: 数据库文件存储目录
DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# 【环境配置】
# ============================================
# ENV: 当前运行环境，从环境变量读取
# 默认为'development'（开发环境），生产环境应设置为'production'
ENV = os.getenv("ENV", "development")

# ============================================
# 【数据库配置】
# ============================================
# DATABASE_URL: 数据库连接字符串
# SQLite是轻量级数据库，适合小型项目和学习
# 格式: sqlite:///路径/数据库文件.db
if ENV == "production":
    # 生产环境：使用环境变量中的数据库URL，或默认的生产数据库
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_DIR / 'production.db'}")
    # SECRET_KEY: JWT签名密钥，生产环境必须使用强密钥
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-very-long-key-1234567890abcdef")
else:
    # 开发环境：使用开发数据库
    DATABASE_URL = f"sqlite:///{DB_DIR / 'database.db'}"
    # 开发环境的密钥（仅用于测试，生产环境必须更换）
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-1234567890")

# ============================================
# 【JWT认证配置】
# ============================================
# ALGORITHM: JWT加密算法，HS256是常用的对称加密算法
ALGORITHM = "HS256"

# ACCESS_TOKEN_EXPIRE_MINUTES: Token过期时间（分钟）
# 60 * 24 * 7 = 7天，用户登录后7天内无需重新登录
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# ============================================
# 【CORS跨域配置】
# ============================================
# CORS (Cross-Origin Resource Sharing): 跨域资源共享
# 前端和后端通常运行在不同端口，需要CORS允许跨域请求
ALLOWED_ORIGINS = [
    "http://localhost:5173",      # Vite开发服务器默认端口
    "http://127.0.0.1:5173",  # 同上，IP地址形式
    "http://localhost:5174",      # Vite备用端口
    "http://127.0.0.1:5174",
    "http://localhost:8080",      # 其他可能的开发端口
    "http://127.0.0.1:8080",
    "http://localhost",           # 生产环境可能使用的端口
    "http://127.0.0.1",
]

# 生产环境：从环境变量读取额外的允许域名
if ENV == "production":
    PROD_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")
    if PROD_ORIGINS:
        # 将逗号分隔的域名字符串转换为列表
        ALLOWED_ORIGINS.extend([origin.strip() for origin in PROD_ORIGINS.split(",")])