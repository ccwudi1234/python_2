# -*- coding: utf-8 -*-
"""
【文件助手模块 - file_helper.py】
================================
这个文件处理文件上传和删除的操作。

【学习要点】
1. uuid: 生成唯一标识符，避免文件名冲突
2. Path: 路径处理，构建文件存储路径
3. 文件读写: 二进制文件的保存和删除

【功能说明】
- save_file: 保存上传的文件到服务器
- delete_file: 删除服务器上的文件

【安全考虑】
- 使用UUID重命名文件，防止路径遍历攻击
- 保留原始文件扩展名，便于识别文件类型
"""

import sys
import os
import uuid
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

from app.config import UPLOAD_DIR

# ============================================
# 【文件保存函数】
# ============================================
def save_file(file_content: bytes, filename: str) -> str:
    """
    保存上传的文件
    
    【参数】
    - file_content: 文件内容（二进制数据）
    - filename: 原始文件名
    
    【返回】
    - 文件存储路径
    
    【工作流程】
    1. 获取文件扩展名
    2. 生成UUID作为新文件名（避免冲突）
    3. 构建存储路径
    4. 写入文件
    5. 返回路径
    
    【安全说明】
    使用UUID重命名文件的原因：
    - 防止文件名冲突（多个用户上传同名文件）
    - 防止路径遍历攻击（恶意文件名如../../../etc/passwd）
    - 保护用户隐私（隐藏原始文件名）
    """
    # 获取文件扩展名（如 .py, .c）
    file_extension = Path(filename).suffix
    
    # 生成唯一文件名：UUID + 扩展名
    # uuid.uuid4() 生成随机UUID，如 "550e8400-e29b-41d4-a716-446655440000"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # 构建完整存储路径
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        # 以二进制模式写入文件
        # "wb" = write binary
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"File saved: {file_path}")
        return str(file_path)
    
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise  # 抛出异常，让上层处理

# ============================================
# 【文件删除函数】
# ============================================
def delete_file(file_path: str) -> bool:
    """
    删除服务器上的文件
    
    【参数】
    - file_path: 文件存储路径
    
    【返回】
    - True: 删除成功
    - False: 删除失败
    
    【错误处理】
    - FileNotFoundError: 文件不存在时返回True（已删除）
    - 其他错误: 记录日志并返回False
    """
    try:
        os.remove(file_path)
        logger.info(f"File deleted: {file_path}")
        return True
    
    except FileNotFoundError:
        # 文件不存在也算"删除成功"
        logger.warning(f"File not found for deletion: {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        return False