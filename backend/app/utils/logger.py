# -*- coding: utf-8 -*-
"""
【日志工具模块 - logger.py】
================================
这个文件配置应用的日志系统，用于记录运行信息。

【学习要点】
1. logging: Python标准日志库
2. StreamHandler: 输出日志到控制台
3. FileHandler: 输出日志到文件
4. Formatter: 定义日志格式

【日志级别】
- DEBUG: 调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

【日志格式】
时间 - 模块名 - 级别 - 消息
"""

import logging
import os
from pathlib import Path

def setup_logger(name: str = __name__) -> logging.Logger:
    """
    配置并返回日志记录器
    
    【参数】
    - name: 日志记录器名称，通常使用模块名
    
    【返回】
    - 配置好的Logger对象
    
    【功能】
    1. 创建日志记录器
    2. 设置日志级别
    3. 创建控制台输出（开发调试）
    4. 创建文件输出（持久保存）
    5. 设置日志格式
    
    【使用示例】
    logger = setup_logger(__name__)
    logger.info("操作成功")
    logger.error("发生错误")
    """
    logger = logging.getLogger(name)
    
    # 如果已有处理器，直接返回（避免重复添加）
    if logger.handlers:
        return logger
    
    # 设置日志级别为INFO
    # INFO级别会记录INFO及以上级别的日志
    logger.setLevel(logging.INFO)
    
    # ============================================
    # 【日志格式配置】
    # ============================================
    # 格式: 时间 - 模块名 - 级别 - 消息
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # ============================================
    # 【控制台处理器】
    # ============================================
    # StreamHandler: 将日志输出到控制台
    # 适合开发调试时查看日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # ============================================
    # 【文件处理器】
    # ============================================
    # FileHandler: 将日志写入文件
    # 适合持久保存日志，便于排查问题
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)  # 自动创建日志目录
    
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # ============================================
    # 【添加处理器】
    # ============================================
    # 将控制台和文件处理器添加到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger