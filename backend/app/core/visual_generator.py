# -*- coding: utf-8 -*-
"""
【可视化数据生成器 - visual_generator.py】
================================
这个文件将解析结果转换为前端可视化数据。

【学习要点】
1. 数据转换：将解析数据转换为可视化格式
2. 变化追踪：对比前后步骤，标记变化
3. 深浅拷贝对比：分析内存地址是否共享

【核心功能】
- generate_variable_data: 生成变量可视化数据
- generate_list_data: 生成列表/数组可视化数据
- generate_copy_comparison: 生成深浅拷贝对比
- generate_memory_layout: 生成内存布局图
"""

from typing import List, Dict, Any

# ============================================
# 【可视化生成器类】
# ============================================
class VisualGenerator:
    """
    可视化数据生成器
    
    【核心功能】
    将解析器输出的variable_history转换为前端可用的可视化数据
    
    【使用示例】
    generator = VisualGenerator()
    visual_data = generator.generate_variable_data(variable_history)
    
    【数据格式】
    前端需要的可视化数据包含：
    - 变量名、值、地址、类型
    - 是否发生变化（用于高亮显示）
    - 旧值、旧地址（用于对比）
    """
    
    def __init__(self):
        """初始化生成器"""
        pass
    
    def generate_variable_data(self, variable_history: List[Dict]) -> List[Dict]:
        """
        生成变量可视化数据
        
        【参数】
        - variable_history: 解析器输出的变量历史列表
        
        【返回】
        - 可视化数据列表，每个元素代表一个步骤
        
        【数据结构】
        [
            {
                "step": 1,
                "description": "Assign: a = 10",
                "variables": [
                    {
                        "name": "a",
                        "value": "10",
                        "address": "0x100000",
                        "type": "int",
                        "is_changed": True,  # 是否变化
                        "old_value": None,   # 旧值
                        "old_address": None  # 旧地址
                    }
                ]
            }
        ]
        
        【变化追踪】
        对比当前步骤和上一步骤，标记变化的变量
        用于前端高亮显示变化的变量
        """
        visual_data = []
        
        for state in variable_history:
            step_data = {
                "step": state["step"],
                "description": state["description"],
                "variables": []
            }
            
            for name, var_info in state.get("variables", {}).items():
                var_data = {
                    "name": name,
                    "value": var_info.get("value"),
                    "address": var_info.get("address"),
                    "type": var_info.get("type", "unknown"),
                    "is_changed": False,  # 默认未变化
                    "old_value": None,
                    "old_address": None
                }
                
                # 对比上一步骤，检测变化
                if visual_data:
                    prev_step = visual_data[-1]
                    # 查找上一步的同名变量
                    prev_var = next((v for v in prev_step["variables"] if v["name"] == name), None)
                    if prev_var:
                        # 检测值或地址是否变化
                        var_data["is_changed"] = (
                            prev_var["value"] != var_info.get("value") or
                            prev_var["address"] != var_info.get("address")
                        )
                        var_data["old_value"] = prev_var["value"]
                        var_data["old_address"] = prev_var["address"]
                
                step_data["variables"].append(var_data)
            
            visual_data.append(step_data)
        
        return visual_data
    
    def generate_list_data(self, variable_history: List[Dict]) -> List[Dict]:
        """
        生成列表/数组可视化数据
        
        【参数】
        - variable_history: 解析器输出的变量历史
        
        【返回】
        - 列表可视化数据
        
        【数据结构】
        [
            {
                "step": 1,
                "description": "Array Declare: arr[5]",
                "lists": [
                    {
                        "name": "arr",
                        "address": "0x100000",
                        "type": "int[5]",
                        "elements": [
                            {
                                "index": 0,
                                "value": 1,
                                "address": "0x100000",
                                "type": "int",
                                "is_changed": False,
                                "is_nested": False,  # 是否是嵌套列表
                                "nested_elements": []  # 嵌套元素
                            }
                        ]
                    }
                ]
            }
        ]
        
        【嵌套列表处理】
        支持二维数组/嵌套列表的可视化
        如 [[1, 2], [3, 4]]
        """
        visual_data = []
        
        for state in variable_history:
            step_data = {
                "step": state["step"],
                "description": state["description"],
                "lists": []
            }
            
            for name, var_info in state.get("variables", {}).items():
                # 只处理列表/数组类型
                if var_info.get("is_list") or var_info.get("is_array"):
                    list_data = {
                        "name": name,
                        "address": var_info.get("address"),
                        "type": var_info.get("type", "list"),
                        "elements": []
                    }
                    
                    elements = var_info.get("elements", [])
                    for elem in elements:
                        elem_data = {
                            "index": elem.get("index"),
                            "value": elem.get("value"),
                            "address": elem.get("address"),
                            "type": elem.get("type", "unknown"),
                            "is_changed": False,
                            "is_nested": False,
                            "nested_elements": []
                        }
                        
                        # 处理嵌套元素（二维数组）
                        if elem.get("nested_elements"):
                            elem_data["is_nested"] = True
                            for nested in elem["nested_elements"]:
                                elem_data["nested_elements"].append({
                                    "index": nested.get("index"),
                                    "value": nested.get("value"),
                                    "address": nested.get("address"),
                                    "type": nested.get("type", "unknown")
                                })
                        
                        # 对比上一步骤，检测元素变化
                        if visual_data:
                            prev_step = visual_data[-1]
                            prev_list = next((l for l in prev_step["lists"] if l["name"] == name), None)
                            if prev_list:
                                prev_elem = next((e for e in prev_list["elements"] if e["index"] == elem.get("index")), None)
                                if prev_elem:
                                    elem_data["is_changed"] = (
                                        prev_elem["value"] != elem.get("value") or
                                        prev_elem["address"] != elem.get("address")
                                    )
                        
                        list_data["elements"].append(elem_data)
                    
                    step_data["lists"].append(list_data)
            
            visual_data.append(step_data)
        
        return visual_data
    
    def generate_copy_comparison(self, variable_history: List[Dict]) -> Dict:
        """
        生成深浅拷贝对比数据
        
        【参数】
        - variable_history: 解析器输出的变量历史
        
        【返回】
        - 深浅拷贝对比数据
        
        【教学目的】
        展示浅拷贝和深拷贝的区别：
        - 浅拷贝：外层列表新地址，内层元素共享地址
        - 深拷贝：所有对象都是新地址
        
        【数据结构】
        {
            "original": {
                "name": "original",
                "address": "0x100000",
                "elements": [
                    {"index": 0, "value": [1, 2], "address": "0x100100"}
                ]
            },
            "shallow_copy": {
                "name": "shallow",
                "address": "0x200000",  # 新地址
                "elements": [
                    {"index": 0, "value": [1, 2], "address": "0x100100", "is_shared": True}  # 共享地址
                ]
            },
            "deep_copy": {
                "name": "deep",
                "address": "0x300000",
                "elements": [
                    {"index": 0, "value": [1, 2], "address": "0x300100", "is_shared": False}  # 新地址
                ]
            },
            "has_comparison": True
        }
        
        【判断共享】
        比较元素地址是否与原始对象相同
        相同 = 共享（浅拷贝）
        不同 = 独立（深拷贝）
        """
        # 获取最后状态
        last_state = variable_history[-1] if variable_history else {}
        variables = last_state.get("variables", {})
        
        result = {
            "original": None,
            "shallow_copy": None,
            "deep_copy": None,
            "has_comparison": False
        }
        
        # 查找原始、浅拷贝、深拷贝变量
        original_name = None
        shallow_name = None
        deep_name = None
        
        for name in variables.keys():
            if name.lower() == "original":
                original_name = name
            elif "shallow" in name.lower():
                shallow_name = name
            elif "deep" in name.lower():
                deep_name = name
        
        # 只有原始对象是列表时才生成对比
        if original_name and variables.get(original_name, {}).get("is_list"):
            result["has_comparison"] = True
            
            # 构建原始对象数据
            result["original"] = {
                "name": original_name,
                "address": variables[original_name].get("address"),
                "type": variables[original_name].get("type"),
                "elements": []
            }
            
            for elem in variables[original_name].get("elements", []):
                result["original"]["elements"].append({
                    "index": elem.get("index"),
                    "value": elem.get("value"),
                    "address": elem.get("address"),
                    "type": elem.get("type")
                })
            
            # 构建浅拷贝数据
            if shallow_name and variables.get(shallow_name, {}).get("is_list"):
                result["shallow_copy"] = {
                    "name": shallow_name,
                    "address": variables[shallow_name].get("address"),
                    "type": variables[shallow_name].get("type"),
                    "elements": []
                }
                
                for i, elem in enumerate(variables[shallow_name].get("elements", [])):
                    # 判断是否与原始对象共享地址
                    is_shared = False
                    if i < len(result["original"]["elements"]):
                        is_shared = elem.get("address") == result["original"]["elements"][i].get("address")
                    
                    result["shallow_copy"]["elements"].append({
                        "index": elem.get("index"),
                        "value": elem.get("value"),
                        "address": elem.get("address"),
                        "type": elem.get("type"),
                        "is_shared": is_shared  # 共享标记
                    })
            
            # 构建深拷贝数据
            if deep_name and variables.get(deep_name, {}).get("is_list"):
                result["deep_copy"] = {
                    "name": deep_name,
                    "address": variables[deep_name].get("address"),
                    "type": variables[deep_name].get("type"),
                    "elements": []
                }
                
                for i, elem in enumerate(variables[deep_name].get("elements", [])):
                    is_shared = False
                    if i < len(result["original"]["elements"]):
                        is_shared = elem.get("address") == result["original"]["elements"][i].get("address")
                    
                    result["deep_copy"]["elements"].append({
                        "index": elem.get("index"),
                        "value": elem.get("value"),
                        "address": elem.get("address"),
                        "type": elem.get("type"),
                        "is_shared": is_shared
                    })
        
        return result
    
    def generate_memory_layout(self, variable_history: List[Dict]) -> Dict:
        """
        生成内存布局可视化
        
        【参数】
        - variable_history: 解析器输出的变量历史
        
        【返回】
        - 内存布局数据
        
        【用途】
        展示变量在内存中的排列顺序
        用于理解C语言的内存模型
        
        【数据结构】
        {
            "blocks": [
                {
                    "address": "0x100000",
                    "name": "a",
                    "value": 10,
                    "type": "int",
                    "is_pointer": False,
                    "is_array": False
                }
            ],
            "start_address": "0x100000",
            "end_address": "0x100008"
        }
        
        【排序】
        按地址从小到大排序，展示内存布局
        """
        last_state = variable_history[-1] if variable_history else {}
        variables = last_state.get("variables", {})
        
        memory_blocks = []
        addresses = []
        
        # 收集所有变量的地址
        for name, var_info in variables.items():
            address = var_info.get("address")
            if address:
                addresses.append((int(address, 16), name, var_info))
        
        # 按地址排序
        addresses.sort(key=lambda x: x[0])
        
        # 构建内存块数据
        for addr, name, var_info in addresses:
            block = {
                "address": hex(addr),
                "name": name,
                "value": var_info.get("value"),
                "type": var_info.get("type"),
                "is_pointer": var_info.get("is_pointer", False),
                "is_array": var_info.get("is_array", False),
                "points_to": var_info.get("points_to")
            }
            memory_blocks.append(block)
        
        return {
            "blocks": memory_blocks,
            "start_address": hex(addresses[0][0]) if addresses else None,
            "end_address": hex(addresses[-1][0] + 8) if addresses else None
        }