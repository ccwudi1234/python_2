# -*- coding: utf-8 -*-
"""
【代码解析API路由 - parse.py】
================================
这个文件处理代码分析和可视化的核心API。

【学习要点】
1. AST (Abstract Syntax Tree): Python抽象语法树解析
2. 代码可视化: 将代码执行过程转换为可视化数据
3. 内存模拟: 模拟变量和内存的变化过程

【API接口】
- POST /parse/python: 解析Python代码
- POST /parse/c: 解析C/C++代码
- POST /parse/copy-comparison: 深浅拷贝对比分析
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ============================================
# 【导入必要的库】
# ============================================
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.logger import setup_logger

from app.core.python_parser import PythonParser
from app.core.c_parser import CParser
from app.core.visual_generator import VisualGenerator

logger = setup_logger(__name__)

# ============================================
# 【创建路由器】
# ============================================
router = APIRouter(prefix="/parse", tags=["parse"])

# ============================================
# 【请求数据模型】
# ============================================
class CodeRequest(BaseModel):
    """
    代码分析请求模型
    
    【字段】
    - code: 要分析的代码内容
    - language: 编程语言（python或c）
    """
    code: str
    language: str

# ============================================
# 【Python代码解析接口】
# ============================================
@router.post("/python")
def parse_python(request: CodeRequest):
    """
    解析Python代码
    
    【请求】
    POST /parse/python
    Body: {"code": "a = 10\\nb = 20", "language": "python"}
    
    【响应】
    {
        "parse_result": {...},  // 解析结果
        "visuals": {
            "variables": [...],  // 变量可视化数据
            "lists": [...]       // 列表可视化数据
        }
    }
    
    【流程】
    1. 创建Python解析器
    2. 解析代码，获取执行步骤
    3. 生成可视化数据
    4. 返回结果
    
    【Python解析器功能】
    - 解析变量赋值
    - 追踪变量历史
    - 模拟内存地址
    - 处理列表操作
    """
    logger.info(f"Parsing Python code (length: {len(request.code)})")
    
    # 创建Python解析器实例
    parser = PythonParser()
    
    # 解析代码，返回执行步骤和变量历史
    result = parser.parse_code(request.code)
    
    # 检查是否有错误
    if "error" in result:
        logger.error(f"Python parsing error: {result['error']}")
        raise HTTPException(status_code=400, detail=result["error"])
    
    # 创建可视化生成器
    generator = VisualGenerator()
    
    # 生成变量可视化数据
    variable_data = generator.generate_variable_data(result.get("variable_history", []))
    
    # 生成列表可视化数据
    list_data = generator.generate_list_data(result.get("variable_history", []))
    
    return {
        "parse_result": result,
        "visuals": {
            "variables": variable_data,
            "lists": list_data
        }
    }

# ============================================
# 【C/C++代码解析接口】
# ============================================
@router.post("/c")
def parse_c(request: CodeRequest):
    """
    解析C/C++代码
    
    【请求】
    POST /parse/c
    Body: {"code": "int main() { int a = 10; }", "language": "c"}
    
    【响应】
    {
        "parse_result": {...},
        "visuals": {
            "variables": [...],
            "lists": [...]
        }
    }
    
    【C解析器功能】
    - 解析变量声明和赋值
    - 模拟内存布局
    - 处理数组操作
    - 模拟指针操作
    - 模拟malloc/free
    """
    logger.info(f"Parsing C code (length: {len(request.code)})")
    
    # 创建C解析器实例
    parser = CParser()
    
    # 解析代码
    result = parser.parse_code(request.code)
    
    if "error" in result:
        logger.error(f"C parsing error: {result['error']}")
        raise HTTPException(status_code=400, detail=result["error"])
    
    # 生成可视化数据
    generator = VisualGenerator()
    variable_data = generator.generate_variable_data(result.get("variable_history", []))
    list_data = generator.generate_list_data(result.get("variable_history", []))
    
    return {
        "parse_result": result,
        "visuals": {
            "variables": variable_data,
            "lists": list_data
        }
    }

# ============================================
# 【拷贝对比分析接口】
# ============================================
@router.post("/copy-comparison")
def get_copy_comparison(request: CodeRequest):
    """
    深浅拷贝对比分析
    
    【请求】
    POST /parse/copy-comparison
    Body: {"code": "original = [[1,2],[3,4]]\\nshallow = list(original)", "language": "python"}
    
    【响应】
    {
        "original": {...},      // 原始对象信息
        "shallow_copy": {...},  // 浅拷贝信息
        "deep_copy": {...},     // 深拷贝信息
        "has_comparison": true  // 是否有对比数据
    }
    
    【教学目的】
    展示浅拷贝和深拷贝的区别：
    - 浅拷贝：复制引用，嵌套对象共享内存
    - 深拷贝：完全独立，所有对象都是新的
    """
    logger.info(f"Generating copy comparison (length: {len(request.code)})")
    
    # 使用Python解析器解析代码
    parser = PythonParser()
    result = parser.parse_code(request.code)
    
    if "error" in result:
        logger.error(f"Copy comparison error: {result['error']}")
        raise HTTPException(status_code=400, detail=result["error"])
    
    # 生成拷贝对比数据
    generator = VisualGenerator()
    comparison = generator.generate_copy_comparison(result.get("variable_history", []))
    
    return comparison