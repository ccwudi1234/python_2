# -*- coding: utf-8 -*-
"""
【文件管理API路由 - file.py】
================================
这个文件处理用户文件上传和管理。

【学习要点】
1. UploadFile: FastAPI文件上传处理
2. 文件类型验证: 限制允许上传的文件类型
3. 文件大小限制: 防止上传过大文件
4. 用户权限验证: 确保用户只能操作自己的文件

【API接口】
- POST /files/upload: 上传文件
- GET /files: 获取文件列表
- DELETE /files/{file_id}: 删除文件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ============================================
# 【导入必要的库】
# ============================================
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import UploadedFile, get_db, User
from app.utils.file_helper import save_file, delete_file
from app.utils.logger import setup_logger
from app.utils.auth import get_current_user

logger = setup_logger(__name__)

# ============================================
# 【创建路由器】
# ============================================
router = APIRouter(prefix="/files", tags=["files"])

# ============================================
# 【配置常量】
# ============================================
# 最大文件大小限制：5MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# ============================================
# 【文件上传接口】
# ============================================
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传文件
    
    【请求】
    POST /files/upload
    Headers: Authorization: Bearer <token>
    Body: multipart/form-data (文件)
    
    【响应】
    {"file_id": 1, "filename": "test.py"}
    
    【流程】
    1. 读取文件内容
    2. 检查文件大小
    3. 检查文件类型
    4. 保存文件到服务器
    5. 创建数据库记录
    
    【安全措施】
    - 文件大小限制：防止服务器存储被耗尽
    - 文件类型限制：只允许代码文件
    - 用户关联：每个文件绑定到上传用户
    """
    # 读取文件内容
    content = await file.read()
    
    # 检查文件大小
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds 5MB limit")
    
    # 检查文件类型
    # 只允许 .py, .c, .h, .txt 文件
    allowed_extensions = ('.py', '.c', '.h', '.txt')
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .py, .c, .h, .txt allowed")
    
    # 保存文件到服务器
    file_path = save_file(content, file.filename)
    logger.info(f"File uploaded: {file.filename}")
    
    # 创建数据库记录
    db_file = UploadedFile(
        filename=file.filename,
        file_path=file_path,
        size=len(content),
        user_id=current_user.id  # 绑定到当前用户
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return {"file_id": db_file.id, "filename": file.filename}

# ============================================
# 【获取文件列表接口】
# ============================================
@router.get("/")
def get_all_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的文件列表
    
    【请求】
    GET /files
    Headers: Authorization: Bearer <token>
    
    【响应】
    [
        {"id": 1, "filename": "test.py", "size": 1024, "created_at": "2024-01-01T00:00:00"},
        ...
    ]
    
    【权限】
    只返回当前用户上传的文件
    """
    # 查询当前用户的文件
    files = db.query(UploadedFile).filter(
        UploadedFile.user_id == current_user.id
    ).order_by(UploadedFile.created_at.desc()).all()
    
    # 格式化返回数据
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "size": f.size,
            "created_at": f.created_at.isoformat()
        }
        for f in files
    ]

# ============================================
# 【删除文件接口】
# ============================================
@router.delete("/{file_id}")
def delete_file_endpoint(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除文件
    
    【请求】
    DELETE /files/{file_id}
    Headers: Authorization: Bearer <token>
    
    【响应】
    {"message": "File deleted"}
    
    【权限】
    只能删除自己上传的文件
    
    【流程】
    1. 查询文件（验证所有权）
    2. 删除服务器文件
    3. 删除数据库记录
    """
    # 查询文件，同时验证所有权
    db_file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == current_user.id
    ).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 删除服务器上的物理文件
    delete_file(db_file.file_path)
    
    # 删除数据库记录
    db.delete(db_file)
    db.commit()
    
    logger.info(f"File deleted: {db_file.filename}")
    return {"message": "File deleted"}