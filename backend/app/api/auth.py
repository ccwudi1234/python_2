# -*- coding: utf-8 -*-
"""
【认证API路由 - auth.py】
================================
这个文件处理用户认证相关的API接口。

【学习要点】
1. APIRouter: 创建路由模块
2. Pydantic BaseModel: 定义请求/响应数据模型
3. Depends: 依赖注入，获取数据库连接和当前用户
4. HTTPException: 返回HTTP错误响应

【API接口】
- POST /auth/register: 用户注册
- POST /auth/login: 用户登录
- GET /auth/profile: 获取用户信息
- DELETE /auth/user: 删除用户
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ============================================
# 【导入必要的库】
# ============================================
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.models import User, get_db
from app.utils.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES

# ============================================
# 【创建路由器】
# ============================================
# prefix: 路由前缀，所有接口都以 /auth 开头
# tags: API文档中的分组标签
router = APIRouter(prefix="/auth", tags=["auth"])

# ============================================
# 【请求/响应数据模型】
# ============================================
# Pydantic模型用于验证请求数据格式
class UserCreate(BaseModel):
    """
    用户注册请求模型
    
    【字段】
    - username: 用户名
    - password: 密码
    """
    username: str
    password: str

class UserLogin(BaseModel):
    """
    用户登录请求模型
    
    【字段】
    - username: 用户名
    - password: 密码
    """
    username: str
    password: str

class Token(BaseModel):
    """
    登录响应模型
    
    【字段】
    - access_token: JWT访问令牌
    - token_type: 令牌类型（Bearer）
    """
    access_token: str
    token_type: str

# ============================================
# 【用户注册接口】
# ============================================
@router.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    
    【请求】
    POST /auth/register
    Body: {"username": "test", "password": "123456"}
    
    【响应】
    {"message": "User created successfully", "user_id": 1}
    
    【流程】
    1. 检查用户名是否已存在
    2. 加密密码
    3. 创建用户记录
    4. 保存到数据库
    """
    # 查询用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        # 用户名已存在，返回400错误
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 加密密码（使用bcrypt）
    hashed_password = get_password_hash(user.password)
    
    # 创建用户对象
    db_user = User(
        username=user.username,
        hashed_password=hashed_password
    )
    
    # 添加到数据库
    db.add(db_user)
    db.commit()  # 提交事务
    db.refresh(db_user)  # 刷新对象，获取数据库生成的ID
    
    return {"message": "User created successfully", "user_id": db_user.id}

# ============================================
# 【用户登录接口】
# ============================================
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    
    【请求】
    POST /auth/login
    Body: {"username": "test", "password": "123456"}
    
    【响应】
    {"access_token": "eyJhbG...", "token_type": "bearer"}
    
    【流程】
    1. 查询用户
    2. 验证密码
    3. 生成JWT令牌
    4. 返回令牌
    """
    # 查询用户
    db_user = db.query(User).filter(User.username == user.username).first()
    
    # 验证用户存在和密码正确
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # 设置令牌过期时间
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 生成JWT令牌
    # data包含用户名和用户ID，用于后续验证
    access_token = create_access_token(
        data={"sub": db_user.username, "user_id": db_user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# ============================================
# 【获取用户信息接口】
# ============================================
@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    
    【请求】
    GET /auth/profile
    Headers: Authorization: Bearer <token>
    
    【响应】
    {"id": 1, "username": "test", "created_at": "2024-01-01T00:00:00"}
    
    【认证】
    使用get_current_user依赖，自动验证JWT令牌
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "created_at": current_user.created_at.isoformat()
    }

# ============================================
# 【删除用户接口】
# ============================================
@router.delete("/user")
def delete_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除当前用户
    
    【请求】
    DELETE /auth/user
    Headers: Authorization: Bearer <token>
    
    【响应】
    {"message": "User deleted successfully"}
    
    【流程】
    1. 验证用户身份
    2. 删除用户记录
    3. 提交事务
    """
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully"}