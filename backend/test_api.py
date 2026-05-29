# -*- coding: utf-8 -*-
"""
测试后端API是否正常工作
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

BASE_URL = "http://localhost:9999"

print("=== 测试后端API ===\n")

# 测试根路由
try:
    print("1. 测试根路由...")
    res = requests.get(f"{BASE_URL}/")
    print(f"   状态码: {res.status_code}")
    print(f"   响应: {res.json()}\n")
except Exception as e:
    print(f"   错误: {e}\n")

# 测试Python解析
try:
    print("2. 测试Python解析...")
    test_code = "a = 10\nb = 20\nc = a + b"
    res = requests.post(
        f"{BASE_URL}/parse/python",
        json={"code": test_code, "language": "python"}
    )
    print(f"   状态码: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"   解析结果包含: {list(data.keys())}")
        if 'visuals' in data:
            print(f"   可视化数据: {list(data['visuals'].keys())}")
    else:
        print(f"   错误: {res.text}")
    print()
except Exception as e:
    print(f"   错误: {e}\n")

print("=== 测试完成 ===")
