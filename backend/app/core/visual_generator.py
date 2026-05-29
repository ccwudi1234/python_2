# -*- coding: utf-8 -*-
"""
【可视化数据生成器 - visual_generator.py】 - 改进版
================================
根据Python和C语言变量存储逻辑的区别，重新设计的可视化生成器。

【核心概念】
Python采用【引用存储】方式，C语言采用【直接存储】方式。
这个文件负责为两种语言生成不同风格的可视化数据。

【Python可视化】
- 展示变量（引用/标签）和对象（实际数据）的区分
- 用箭头表示引用关系
- 展示引用计数
- 区分浅拷贝和深拷贝

【C语言可视化】
- 展示变量直接存储值
- 展示连续的内存布局
- 展示指针的指向关系
"""

from typing import List, Dict, Any

# ============================================
# 【可视化生成器类】
# ============================================
class VisualGenerator:
    """
    可视化数据生成器

    【核心功能】
    1. 为Python生成引用模式的可视化数据
    2. 为C语言生成直接模式的可视化数据
    3. 展示引用关系（箭头）
    4. 生成深浅拷贝对比

    【使用示例】
    generator = VisualGenerator()

    # Python可视化
    visual_data = generator.generate_python_visualization(variable_history)

    # C语言可视化
    visual_data = generator.generate_c_visualization(variable_history)
    """

    def __init__(self):
        """初始化生成器"""
        pass

    # ========================
    # Python可视化方法
    # ========================

    def generate_python_visualization(self, variable_history: List[Dict]) -> Dict[str, Any]:
        """
        生成Python代码的可视化数据

        【核心功能】
        1. 生成变量引用信息（展示变量指向对象）
        2. 生成对象信息（展示实际数据）
        3. 生成引用关系（展示箭头连接）

        【返回数据结构】
        {
            "variables": [...],  # 变量引用列表
            "objects": [...],    # 对象列表
            "references": [...], # 引用关系
            "memory_summary": {...}  # 内存摘要
        }
        """
        visual_data = {
            "variables": [],
            "objects": [],
            "references": [],
            "memory_summary": {
                "total_variables": 0,
                "total_objects": 0,
                "total_references": 0
            }
        }

        # 获取最后状态
        last_state = variable_history[-1] if variable_history else {}

        # 生成变量引用数据
        variables = last_state.get("variables", {})
        for name, var_info in variables.items():
            visual_data["variables"].append({
                "name": name,
                "address": var_info.get("address"),
                "points_to": var_info.get("points_to"),
                "type": var_info.get("type"),
                "value": var_info.get("value"),
                "is_reference": True,
                "ref_count": var_info.get("ref_count", 1),
                "referenced_by": var_info.get("referenced_by", []),
                "is_list": var_info.get("is_list", False),
                "elements": var_info.get("elements", [])
            })

        # 生成对象数据
        objects = last_state.get("objects", [])
        for obj in objects:
            visual_data["objects"].append({
                "address": obj.get("address"),
                "type": obj.get("type"),
                "value": obj.get("value"),
                "ref_count": obj.get("ref_count", 1),
                "referenced_by": obj.get("referenced_by", []),
                "elements": obj.get("elements", []),
                "is_shared": len(obj.get("referenced_by", [])) > 1
            })

        # 生成引用关系
        references = last_state.get("references", [])
        for ref in references:
            visual_data["references"].append({
                "variable": ref.get("variable"),
                "variable_address": ref.get("variable_address"),
                "object_address": ref.get("object_address")
            })

        # 统计
        visual_data["memory_summary"]["total_variables"] = len(visual_data["variables"])
        visual_data["memory_summary"]["total_objects"] = len(visual_data["objects"])
        visual_data["memory_summary"]["total_references"] = len(visual_data["references"])

        return visual_data

    def generate_python_step_by_step(self, variable_history: List[Dict]) -> List[Dict]:
        """
        生成Python代码的分步可视化数据

        【用途】
        用于动画展示每一步的变量和对象变化

        【返回】
        每一步的完整可视化数据
        """
        steps = []

        for state in variable_history:
            step_data = {
                "step": state["step"],
                "description": state["description"],
                "variables": [],
                "objects": [],
                "references": [],
                "changes": {
                    "new_variables": [],
                    "changed_variables": [],
                    "new_objects": [],
                    "new_references": []
                }
            }

            # 获取上一步状态（用于检测变化）
            prev_state = variable_history[state["step"] - 2] if state["step"] > 1 else None

            # 生成变量引用数据
            variables = state.get("variables", {})
            prev_variables = prev_state.get("variables", {}) if prev_state else {}

            for name, var_info in variables.items():
                is_new = name not in prev_variables
                is_changed = (
                    not is_new and
                    prev_variables[name].get("points_to") != var_info.get("points_to")
                )

                var_data = {
                    "name": name,
                    "address": var_info.get("address"),
                    "points_to": var_info.get("points_to"),
                    "type": var_info.get("type"),
                    "value": var_info.get("value"),
                    "is_reference": True,
                    "ref_count": var_info.get("ref_count", 1),
                    "is_new": is_new,
                    "is_changed": is_changed
                }

                if is_new:
                    step_data["changes"]["new_variables"].append(name)
                if is_changed:
                    step_data["changes"]["changed_variables"].append(name)

                step_data["variables"].append(var_data)

            # 生成对象数据
            objects = state.get("objects", [])
            prev_objects = prev_state.get("objects", []) if prev_state else []
            prev_object_addrs = {obj["address"] for obj in prev_objects}

            for obj in objects:
                is_new = obj["address"] not in prev_object_addrs

                obj_data = {
                    "address": obj.get("address"),
                    "type": obj.get("type"),
                    "value": obj.get("value"),
                    "ref_count": obj.get("ref_count", 1),
                    "referenced_by": obj.get("referenced_by", []),
                    "is_shared": len(obj.get("referenced_by", [])) > 1,
                    "is_new": is_new
                }

                if is_new:
                    step_data["changes"]["new_objects"].append(obj["address"])

                step_data["objects"].append(obj_data)

            # 生成引用关系
            references = state.get("references", [])
            step_data["references"] = references

            steps.append(step_data)

        return steps

    def generate_copy_comparison(self, variable_history: List[Dict]) -> Dict[str, Any]:
        """
        生成深浅拷贝对比数据

        【教学目的】
        展示浅拷贝和深拷贝的区别：
        - 浅拷贝：外层新地址，内层元素共享地址
        - 深拷贝：所有对象都是新地址

        【返回数据结构】
        {
            "original": {
                "name": "original",
                "address": "0x100000",
                "elements": [
                    {
                        "index": 0,
                        "value": [1, 2],
                        "address": "0x100100",
                        "is_shared": False
                    }
                ]
            },
            "shallow_copy": {
                "name": "shallow",
                "address": "0x200000",
                "elements": [
                    {
                        "index": 0,
                        "value": [1, 2],
                        "address": "0x100100",  # 共享地址！
                        "is_shared": True
                    }
                ]
            },
            "deep_copy": {
                "name": "deep",
                "address": "0x300000",
                "elements": [
                    {
                        "index": 0,
                        "value": [1, 2],
                        "address": "0x300100",  # 新地址
                        "is_shared": False
                    }
                ]
            },
            "has_comparison": True,
            "explanation": {
                "shallow": "浅拷贝：外层列表是新对象，但元素仍是原列表的引用",
                "deep": "深拷贝：所有对象都是新创建的，完全独立"
            }
        }
        """
        last_state = variable_history[-1] if variable_history else {}
        variables = last_state.get("variables", {})
        objects = last_state.get("objects", [])

        result = {
            "original": None,
            "shallow_copy": None,
            "deep_copy": None,
            "has_comparison": False,
            "explanation": {
                "shallow": "浅拷贝：复制引用，嵌套对象共享内存",
                "deep": "深拷贝：完全独立，所有对象都是新创建的"
            }
        }

        # 查找original、shallow、deep变量
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

        # 只有当存在列表类型的original时才生成对比
        if original_name:
            original_var = variables.get(original_name, {})
            if original_var.get("is_list"):
                result["has_comparison"] = True

                # 构建original数据
                result["original"] = {
                    "name": original_name,
                    "address": original_var.get("address"),
                    "points_to": original_var.get("points_to"),
                    "type": original_var.get("type"),
                    "elements": [],
                    "ref_count": original_var.get("ref_count", 1)
                }

                # 获取original指向的对象
                original_obj = None
                for obj in objects:
                    if obj["address"] == original_var.get("points_to"):
                        original_obj = obj
                        break

                if original_obj:
                    for elem in original_obj.get("elements", []):
                        result["original"]["elements"].append({
                            "index": elem.get("index"),
                            "value": elem.get("value"),
                            "address": elem.get("address"),
                            "type": elem.get("type"),
                            "is_shared": False
                        })

                # 构建shallow_copy数据
                if shallow_name:
                    shallow_var = variables.get(shallow_name, {})
                    if shallow_var.get("is_list"):
                        result["shallow_copy"] = {
                            "name": shallow_name,
                            "address": shallow_var.get("address"),
                            "points_to": shallow_var.get("points_to"),
                            "type": shallow_var.get("type"),
                            "elements": [],
                            "ref_count": shallow_var.get("ref_count", 1),
                            "is_shallow": True
                        }

                        # 获取shallow指向的对象
                        shallow_obj = None
                        for obj in objects:
                            if obj["address"] == shallow_var.get("points_to"):
                                shallow_obj = obj
                                break

                        if shallow_obj:
                            for i, elem in enumerate(shallow_obj.get("elements", [])):
                                # 判断是否与original共享地址
                                is_shared = False
                                if i < len(result["original"]["elements"]):
                                    is_shared = (
                                        elem.get("address") == result["original"]["elements"][i].get("address")
                                    )

                                result["shallow_copy"]["elements"].append({
                                    "index": elem.get("index"),
                                    "value": elem.get("value"),
                                    "address": elem.get("address"),
                                    "type": elem.get("type"),
                                    "is_shared": is_shared
                                })

                # 构建deep_copy数据
                if deep_name:
                    deep_var = variables.get(deep_name, {})
                    if deep_var.get("is_list"):
                        result["deep_copy"] = {
                            "name": deep_name,
                            "address": deep_var.get("address"),
                            "points_to": deep_var.get("points_to"),
                            "type": deep_var.get("type"),
                            "elements": [],
                            "ref_count": deep_var.get("ref_count", 1),
                            "is_deep": True
                        }

                        # 获取deep指向的对象
                        deep_obj = None
                        for obj in objects:
                            if obj["address"] == deep_var.get("points_to"):
                                deep_obj = obj
                                break

                        if deep_obj:
                            for i, elem in enumerate(deep_obj.get("elements", [])):
                                # 深拷贝的元素地址必然与original不同
                                is_shared = (
                                    i < len(result["original"]["elements"]) and
                                    elem.get("address") == result["original"]["elements"][i].get("address")
                                )

                                result["deep_copy"]["elements"].append({
                                    "index": elem.get("index"),
                                    "value": elem.get("value"),
                                    "address": elem.get("address"),
                                    "type": elem.get("type"),
                                    "is_shared": is_shared
                                })

        return result

    # ========================
    # C语言可视化方法
    # ========================

    def generate_c_visualization(self, variable_history: List[Dict]) -> Dict[str, Any]:
        """
        生成C代码的可视化数据

        【核心功能】
        C语言采用直接存储方式，变量直接存储值

        【返回数据结构】
        {
            "variables": [...],  # 变量列表（直接存储值）
            "memory_blocks": [...],  # 内存块列表
            "memory_layout": {...}  # 内存布局信息
        }
        """
        visual_data = {
            "variables": [],
            "memory_blocks": [],
            "memory_layout": {
                "start_address": None,
                "end_address": None,
                "total_size": 0
            }
        }

        last_state = variable_history[-1] if variable_history else {}
        variables = last_state.get("variables", {})

        # 收集所有内存地址
        addresses = []
        for name, var_info in variables.items():
            block = {
                "name": name,
                "address": var_info.get("address"),
                "value": var_info.get("value"),
                "type": var_info.get("type"),
                "is_pointer": var_info.get("is_pointer", False),
                "is_array": var_info.get("is_array", False),
                "points_to": var_info.get("points_to"),
                "elements": var_info.get("elements", [])
            }

            visual_data["variables"].append(block)
            addresses.append((int(var_info.get("address", "0x0"), 16), block))

        # 按地址排序
        addresses.sort(key=lambda x: x[0])

        # 构建内存块列表
        for addr, block in addresses:
            visual_data["memory_blocks"].append(block)

        # 设置内存布局信息
        if addresses:
            visual_data["memory_layout"]["start_address"] = hex(addresses[0][0])
            visual_data["memory_layout"]["end_address"] = hex(addresses[-1][0] + 0x10)
            visual_data["memory_layout"]["total_size"] = len(addresses) * 0x10

        return visual_data

    # ========================
    # 兼容性方法（保持向后兼容）
    # ========================

    def generate_variable_data(self, variable_history: List[Dict]) -> List[Dict]:
        """
        生成变量可视化数据（兼容性方法）

        【说明】
        为了保持向后兼容，保留原方法
        """
        visual_data = []

        for state in variable_history:
            step_data = {
                "step": state["step"],
                "description": state["description"],
                "variables": []
            }

            variables = state.get("variables", {})

            for name, var_info in variables.items():
                var_data = {
                    "name": name,
                    "value": var_info.get("value"),
                    "address": var_info.get("address"),
                    "type": var_info.get("type", "unknown"),
                    "is_list": var_info.get("is_list", False),
                    "is_reference": var_info.get("is_reference", False),
                    "points_to": var_info.get("points_to"),
                    "ref_count": var_info.get("ref_count", 1)
                }

                step_data["variables"].append(var_data)

            visual_data.append(step_data)

        return visual_data

    def generate_list_data(self, variable_history: List[Dict]) -> List[Dict]:
        """
        生成列表/数组可视化数据（兼容性方法）

        【说明】
        为了保持向后兼容，保留原方法
        """
        visual_data = []

        for state in variable_history:
            step_data = {
                "step": state["step"],
                "description": state["description"],
                "lists": []
            }

            variables = state.get("variables", {})

            for name, var_info in variables.items():
                if var_info.get("is_list") or var_info.get("is_array"):
                    list_data = {
                        "name": name,
                        "address": var_info.get("address"),
                        "points_to": var_info.get("points_to"),
                        "type": var_info.get("type", "list"),
                        "elements": var_info.get("elements", [])
                    }

                    step_data["lists"].append(list_data)

            visual_data.append(step_data)

        return visual_data

    def generate_memory_layout(self, variable_history: List[Dict]) -> Dict[str, Any]:
        """
        生成内存布局可视化（兼容性方法）

        【说明】
        为了保持向后兼容，保留原方法
        """
        last_state = variable_history[-1] if variable_history else {}
        variables = last_state.get("variables", {})

        memory_blocks = []
        addresses = []

        for name, var_info in variables.items():
            address = var_info.get("address")
            if address:
                try:
                    addr_int = int(address, 16)
                    addresses.append((addr_int, name, var_info))
                except ValueError:
                    pass

        addresses.sort(key=lambda x: x[0])

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
            "end_address": hex(addresses[-1][0] + 0x10) if addresses else None
        }
