# -*- coding: utf-8 -*-
"""
【分析记录API路由 - record.py】
================================
这个文件处理用户代码分析历史的保存和查询。

【学习要点】
1. CRUD操作: 创建、读取、更新、删除
2. 用户数据隔离: 每个用户只能查看自己的记录
3. 数据分页: 防止返回过多数据

【API接口】
- POST /records: 创建分析记录
- GET /records: 获取记录列表
- GET /records/{record_id}: 获取单条记录
- DELETE /records/{record_id}: 删除记录
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ============================================
# 【导入必要的库】
# ============================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.utils.logger import setup_logger

from app.db.models import AnalysisRecord, get_db, User
from app.utils.auth import get_current_user

logger = setup_logger(__name__)

# ============================================
# 【创建路由器】
# ============================================
router = APIRouter(prefix="/records", tags=["records"])

# ============================================
# 【请求数据模型】
# ============================================
class RecordCreate(BaseModel):
    """
    创建分析记录请求模型
    
    【字段】
    - code_content: 代码内容
    - language: 编程语言
    """
    code_content: str
    language: str

# ============================================
# 【创建分析记录接口】
# ============================================
@router.post("/")
def create_record(
    record: RecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建分析记录
    
    【请求】
    POST /records
    Headers: Authorization: Bearer <token>
    Body: {"code_content": "a = 10", "language": "python"}
    
    【响应】
    {"record_id": 1}
    
    【用途】
    用户每次分析代码后，可以保存分析历史，
    方便后续查看和重新分析
    """
    # 创建记录对象
    db_record = AnalysisRecord(
        code_content=record.code_content,
        language=record.language,
        user_id=current_user.id
    )
    
    # 保存到数据库
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    logger.info(f"Record created: {db_record.id}")
    return {"record_id": db_record.id}

# ============================================
# 【获取记录列表接口】
# ============================================
@router.get("/")
def get_all_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的分析记录列表
    
    【请求】
    GET /records
    Headers: Authorization: Bearer <token>
    
    【响应】
    [
        {
            "id": 1,
            "code_content": "a = 10...",
            "language": "python",
            "created_at": "2024-01-01T00:00:00"
        },
        ...
    ]
    
    【数据处理】
    - 只返回当前用户的记录
    - 按时间倒序排列（最新的在前）
    - 代码内容截断显示（只显示前100字符）
    """
    # 查询当前用户的记录
    records = db.query(AnalysisRecord).filter(
        AnalysisRecord.user_id == current_user.id
    ).order_by(AnalysisRecord.created_at.desc()).all()
    
    # 格式化返回数据
    return [
        {
            "id": r.id,
            # 截断长代码，方便列表显示
            "code_content": r.code_content[:100] + "..." if len(r.code_content) > 100 else r.code_content,
            "language": r.language,
            "created_at": r.created_at.isoformat()
        }
        for r in records
    ]

# ============================================
# 【获取单条记录接口】
# ============================================
@router.get("/{record_id}")
def get_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单条分析记录详情
    
    【请求】
    GET /records/{record_id}
    Headers: Authorization: Bearer <token>
    
    【响应】
    {
        "id": 1,
        "code_content": "完整代码内容",
        "language": "python",
        "created_at": "2024-01-01T00:00:00"
    }
    
    【权限】
    只能查看自己的记录
    """
    # 查询记录，验证所有权
    record = db.query(AnalysisRecord).filter(
        AnalysisRecord.id == record_id,
        AnalysisRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {
        "id": record.id,
        "code_content": record.code_content,  # 返回完整代码
        "language": record.language,
        "created_at": record.created_at.isoformat()
    }

# ============================================
# 【删除记录接口】
# ============================================
@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除分析记录
    
    【请求】
    DELETE /records/{record_id}
    Headers: Authorization: Bearer <token>
    
    【响应】
    {"message": "Record deleted"}
    
    【权限】
    只能删除自己的记录
    """
    # 查询记录，验证所有权
    record = db.query(AnalysisRecord).filter(
        AnalysisRecord.id == record_id,
        AnalysisRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # 删除记录
    db.delete(record)
    db.commit()
    
    logger.info(f"Record deleted: {record_id}")
    return {"message": "Record deleted"}