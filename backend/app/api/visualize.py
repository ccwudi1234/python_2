# -*- coding: utf-8 -*-
"""
【可视化API路由 - visualize.py】
================================
这个文件处理可视化数据的生成。

【学习要点】
1. 数据转换: 将解析结果转换为可视化格式
2. 前后端数据交互: 定义清晰的API接口

【API接口】
- POST /visualize/variables: 生成变量可视化数据
- POST /visualize/lists: 生成列表可视化数据
- POST /visualize/memory-layout: 生成内存布局图
- POST /visualize/copy-comparison: 生成深浅拷贝对比
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ============================================
# 【导入必要的库】
# ============================================
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from app.utils.logger import setup_logger

from app.core.visual_generator import VisualGenerator

logger = setup_logger(__name__)

# ============================================
# 【创建路由器】
# ============================================
router = APIRouter(prefix="/visualize", tags=["visualize"])

# ============================================
# 【请求数据模型】
# ============================================
class VisualRequest(BaseModel):
    """
    可视化请求模型
    
    【字段】
    - variable_history: 变量历史数据列表
    """
    variable_history: list

class CopyRequest(BaseModel):
    """
    拷贝对比请求模型
    
    【字段】
    - original: 原始对象
    - shallow: 浅拷贝对象
    - deep: 深拷贝对象
    """
    original: Any
    shallow: Any
    deep: Any

# ============================================
# 【变量可视化接口】
# ============================================
@router.post("/variables")
def visualize_variables(request: VisualRequest):
    """
    生成变量可视化数据
    
    【请求】
    POST /visualize/variables
    Body: {"variable_history": [...]}
    
    【响应】
    {"visuals": [...]}
    
    【功能】
    将变量历史转换为前端可显示的格式，
    包含变量名、值、地址、类型等信息
    """
    logger.info(f"Generating variable visualization")
    
    # 创建可视化生成器
    generator = VisualGenerator()
    
    # 生成变量可视化数据
    visuals = generator.generate_variable_data(request.variable_history)
    
    return {"visuals": visuals}

# ============================================
# 【列表可视化接口】
# ============================================
@router.post("/lists")
def visualize_lists(request: VisualRequest):
    """
    生成列表可视化数据
    
    【请求】
    POST /visualize/lists
    Body: {"variable_history": [...]}
    
    【响应】
    {"visuals": [...]}
    
    【功能】
    将列表/数组数据转换为可视化格式，
    包含元素索引、值、地址等信息
    """
    logger.info(f"Generating list visualization")
    
    generator = VisualGenerator()
    visuals = generator.generate_list_data(request.variable_history)
    
    return {"visuals": visuals}

# ============================================
# 【内存布局接口】
# ============================================
@router.post("/memory-layout")
def visualize_memory_layout(request: VisualRequest):
    """
    生成内存布局可视化
    
    【请求】
    POST /visualize/memory-layout
    Body: {"variable_history": [...]}
    
    【响应】
    {"layout": {...}}
    
    【功能】
    模拟内存布局，展示变量在内存中的排列，
    用于理解C语言的内存模型
    """
    logger.info(f"Generating memory layout")
    
    generator = VisualGenerator()
    layout = generator.generate_memory_layout(request.variable_history)
    
    return {"layout": layout}

# ============================================
# 【拷贝对比接口】
# ============================================
@router.post("/copy-comparison")
def visualize_copy_comparison(request: VisualRequest):
    """
    生成深浅拷贝对比可视化
    
    【请求】
    POST /visualize/copy-comparison
    Body: {"variable_history": [...]}
    
    【响应】
    {"comparison": {...}}
    
    【教学目的】
    展示浅拷贝和深拷贝的内存差异：
    - 浅拷贝：外层对象新地址，内层对象共享地址
    - 深拷贝：所有对象都是新地址
    """
    logger.info(f"Generating copy comparison visualization")
    
    generator = VisualGenerator()
    comparison = generator.generate_copy_comparison(request.variable_history)
    
    return {"comparison": comparison}