# -*- coding: utf-8 -*-
"""
【认证工具模块 - auth.py】
================================
这个文件处理用户认证相关的功能，包括密码加密和JWT令牌。

【学习要点】
1. bcrypt: 密码加密算法，安全存储用户密码
2. JWT (JSON Web Token): 无状态认证机制
3. OAuth2: 标准认证协议
4. Depends: FastAPI依赖注入系统

【认证流程】
1. 用户注册 -> 密码加密存储
2. 用户登录 -> 验证密码 -> 生成JWT令牌
3. 访问API -> 验证JWT令牌 -> 获取用户信息
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ============================================
# 【导入必要的库】
# ============================================
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.models import get_db, User
from sqlalchemy.orm import Session

# ============================================
# 【密码加密配置】
# ============================================
# CryptContext: 密码加密上下文
# schemes=["bcrypt"]: 使用bcrypt算法
# deprecated="auto": 自动处理过时的算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================
# 【OAuth2配置】
# ============================================
# OAuth2PasswordBearer: 从请求头获取Token
# tokenUrl: 获取Token的URL（登录接口）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ============================================
# 【密码处理函数】
# ============================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    【参数】
    - plain_password: 用户输入的原始密码
    - hashed_password: 数据库中存储的加密密码
    
    【返回】
    - True: 密码匹配
    - False: 密码不匹配
    
    【原理】
    bcrypt加密后的密码包含盐值，每次验证都会重新计算
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    加密密码
    
    【参数】
    - password: 原始密码
    
    【返回】
    - 加密后的密码字符串
    
    【原理】
    bcrypt会自动生成随机盐值并加入密码，防止彩虹表攻击
    """
    return pwd_context.hash(password)

# ============================================
# 【JWT令牌函数】
# ============================================
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    创建JWT访问令牌
    
    【参数】
    - data: 要编码的数据（通常是用户名、用户ID）
    - expires_delta: 过期时间增量
    
    【返回】
    - JWT令牌字符串
    
    【JWT结构】
    Header: {"alg": "HS256", "typ": "JWT"}
    Payload: {"sub": "username", "exp": 过期时间}
    Signature: 使用SECRET_KEY签名
    
    【安全说明】
    - 令牌包含用户信息，但不包含密码
    - 令牌有过期时间，防止长期有效
    - 使用SECRET_KEY签名，防止伪造
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 将过期时间加入Payload
    to_encode.update({"exp": expire})
    
    # 使用SECRET_KEY和ALGORITHM编码JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# ============================================
# 【获取当前用户函数】
# ============================================
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    从JWT令牌获取当前用户
    
    【用途】
    在需要认证的API中使用，自动验证用户身份
    
    【用法示例】
    @router.get("/profile")
    def get_profile(current_user: User = Depends(get_current_user)):
        return {"username": current_user.username}
    
    【工作流程】
    1. 从请求头获取Token
    2. 解码Token获取用户名
    3. 从数据库查询用户
    4. 返回用户对象
    
    【错误处理】
    - Token无效: 返回401错误
    - 用户不存在: 返回401错误
    """
    # 定义认证失败异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 获取用户名（"sub"是JWT标准字段，表示subject）
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        # JWT解码失败（令牌无效或过期）
        raise credentials_exception
    
    # 从数据库查询用户
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user