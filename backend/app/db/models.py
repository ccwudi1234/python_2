# -*- coding: utf-8 -*-
"""
【数据库模型文件 - models.py】
================================
这个文件定义了数据库的表结构（数据模型）。
使用 SQLAlchemy ORM（对象关系映射）将Python类映射到数据库表。

【学习要点】
1. SQLAlchemy ORM: 用Python类定义数据库表，无需手写SQL
2. Column: 定义表的列（字段）
3. relationship: 定义表之间的关系（如用户和记录的一对多关系）
4. SessionLocal: 数据库会话，用于执行数据库操作

【数据库表说明】
- User: 用户表，存储用户账号信息
- AnalysisRecord: 分析记录表，存储用户的代码分析历史
- UploadedFile: 上传文件表，存储用户上传的文件信息
"""

# ============================================
# 【导入必要的库】
# ============================================
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
import sys
import os

# 添加项目路径，以便导入配置
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.config import DATABASE_URL

# ============================================
# 【创建ORM基础类】
# ============================================
# declarative_base(): 所有模型类的基类
# 继承Base的类会被自动映射为数据库表
Base = declarative_base()

# ============================================
# 【用户表模型】
# ============================================
class User(Base):
    """
    用户表 - 存储用户账号信息
    
    【字段说明】
    - id: 主键，自动递增的唯一标识
    - username: 用户名，唯一且不能为空
    - nickname: 昵称，可选
    - hashed_password: 加密后的密码（使用bcrypt加密）
    - created_at: 创建时间，自动记录
    
    【关系说明】
    - records: 用户的分析记录（一对多）
    - files: 用户上传的文件（一对多）
    """
    __tablename__ = "users"  # 表名
    
    # 字段定义
    id = Column(Integer, primary_key=True, index=True)  # 主键，建立索引加速查询
    username = Column(String, unique=True, index=True, nullable=False)  # 用户名，唯一
    nickname = Column(String, nullable=True)  # 昵称，可选
    hashed_password = Column(String, nullable=False)  # 加密密码，必填
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间，UTC时间
    
    # 关系定义：一个用户可以有多个记录和文件
    records = relationship("AnalysisRecord", back_populates="user")  # 用户的分析记录
    files = relationship("UploadedFile", back_populates="user")  # 用户上传的文件

# ============================================
# 【分析记录表模型】
# ============================================
class AnalysisRecord(Base):
    """
    分析记录表 - 存储用户的代码分析历史
    
    【字段说明】
    - id: 主键
    - code_content: 代码内容（完整代码）
    - language: 编程语言（python/c）
    - user_id: 所属用户ID（外键）
    - created_at: 分析时间
    
    【用途】
    用户每次分析代码后，记录会被保存，方便查看历史
    """
    __tablename__ = "analysis_records"  # 表名
    
    # 字段定义
    id = Column(Integer, primary_key=True, index=True)
    code_content = Column(Text, nullable=False)  # Text类型，可存储长文本
    language = Column(String, nullable=False)  # 语言类型：python或c
    user_id = Column(Integer, ForeignKey("users.id"))  # 外键，关联用户表
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系：每条记录属于一个用户
    user = relationship("User", back_populates="records")

# ============================================
# 【上传文件表模型】
# ============================================
class UploadedFile(Base):
    """
    上传文件表 - 存储用户上传的文件信息
    
    【字段说明】
    - id: 主键
    - filename: 文件名
    - file_path: 文件存储路径
    - size: 文件大小（字节）
    - user_id: 所属用户ID
    - created_at: 上传时间
    """
    __tablename__ = "uploaded_files"  # 表名
    
    # 字段定义
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)  # 原始文件名
    file_path = Column(String, nullable=False)  # 服务器上的存储路径
    size = Column(Integer, nullable=False)  # 文件大小（字节）
    user_id = Column(Integer, ForeignKey("users.id"))  # 外键
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系：每个文件属于一个用户
    user = relationship("User", back_populates="files")

# ============================================
# 【数据库引擎和会话】
# ============================================
# create_engine: 创建数据库连接引擎
# connect_args: SQLite特有参数，允许多线程访问
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal: 数据库会话工厂
# autocommit=False: 需手动提交事务
# autoflush=False: 需手动刷新
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================================
# 【数据库操作函数】
# ============================================
def get_db():
    """
    获取数据库会话
    
    【用途】
    在API路由中使用，通过依赖注入获取数据库连接
    
    【用法】
    @router.get("/")
    def get_items(db: Session = Depends(get_db)):
        # 使用db进行数据库操作
        ...
    
    【工作原理】
    1. 创建数据库会话
    2. yield返回会话（使用生成器）
    3. 请求结束后自动关闭会话
    """
    db = SessionLocal()
    try:
        yield db  # 返回会话给调用者
    finally:
        db.close()  # 确保会话被关闭，释放资源

def init_db():
    """
    初始化数据库
    
    【用途】
    在应用启动时调用，创建所有表
    
    【工作原理】
    Base.metadata.create_all: 根据所有模型类创建对应的数据库表
    如果表已存在，不会重复创建
    """
    Base.metadata.create_all(bind=engine)