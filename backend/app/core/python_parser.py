# -*- coding: utf-8 -*-
"""
【Python代码解析器 - python_parser.py】 - 改进版
================================
根据Python和C语言变量存储逻辑的区别，重新设计的解析器。

【核心概念】
Python的变量存储逻辑采用【引用存储】方式：
- 变量是"标签"（引用），贴在对象上
- 所有数据都是对象（整数、字符串、列表等）
- 变量存储的是对象的引用（类似指针，但不是地址）
- 赋值操作是让变量指向新的对象

【与C语言的区别】
C语言采用【直接存储】方式：
- 变量是固定大小的内存区域
- 变量直接存储值
- 赋值操作是复制值

【学习要点】
1. 引用 vs 直接存储
   - Python：变量是引用（标签），对象在别处
   - C语言：变量直接存储值

2. 赋值操作
   - Python：b = a，b和a指向同一个对象（共享引用）
   - C语言：b = a，b得到a的值的副本（独立变量）

3. 列表/数组存储差异
   - Python列表：存储引用（指针），指向实际对象
   - C数组：连续内存，存储值本身

4. 浅拷贝 vs 深拷贝
   - 浅拷贝：复制引用，嵌套对象共享内存
   - 深拷贝：完全独立，所有对象都是新的
"""

import ast
import copy
from typing import List, Dict, Any, Optional

# ============================================
# 【对象追踪器 - 追踪Python中的实际对象】
# ============================================
class ObjectTracker:
    """
    对象追踪器 - 追踪Python中的实际对象

    【核心概念】
    在Python中，所有数据都是对象：
    - 整数对象：存储整数值
    - 字符串对象：存储字符串
    - 列表对象：存储元素引用列表

    【功能】
    1. 为每个对象分配唯一标识（模拟内存地址）
    2. 追踪对象的类型、值、引用计数
    3. 记录对象之间的关系（列表的元素引用）

    【数据结构】
    objects: {
        "对象ID": {
            "address": "0x100000",      # 对象地址
            "type": "int/list/str",     # 对象类型
            "value": 10 或 [...],       # 对象值
            "ref_count": 2,              # 引用计数
            "referenced_by": ["a", "b"], # 引用此对象的变量
            "elements": [...]            # 如果是列表，存储元素信息
        }
    }
    """

    def __init__(self):
        """初始化对象追踪器"""
        self.objects = {}  # 存储所有对象
        self.next_address = 0x100000  # 下一个可用地址

    def create_object(self, obj, referenced_by: str = None):
        """
        创建并追踪一个对象

        【参数】
        - obj: Python对象
        - referenced_by: 引用此对象的变量名

        【返回】
        - 对象信息字典
        """
        # 获取对象的唯一标识
        obj_id = id(obj)

        # 如果对象已存在，增加引用计数
        if obj_id in self.objects:
            self.objects[obj_id]["ref_count"] += 1
            if referenced_by:
                self.objects[obj_id]["referenced_by"].append(referenced_by)
        else:
            # 创建新对象记录
            obj_info = {
                "address": hex(self.next_address),
                "type": type(obj).__name__,
                "value": obj,
                "ref_count": 1,
                "referenced_by": [referenced_by] if referenced_by else [],
                "elements": []
            }

            # 如果是列表，追踪元素引用
            if isinstance(obj, list):
                obj_info["elements"] = []
                for i, elem in enumerate(obj):
                    # 递归追踪元素
                    elem_info = self.create_object(elem)
                    obj_info["elements"].append({
                        "index": i,
                        "value": elem,
                        "address": elem_info["address"],
                        "type": type(elem).__name__,
                        "is_reference": True  # 明确标记为引用
                    })

            # 如果是嵌套列表，继续追踪
            if isinstance(obj, list):
                for i, elem in enumerate(obj):
                    if isinstance(elem, list):
                        # 为嵌套列表创建独立对象
                        nested_obj = elem
                        nested_info = self.create_object(nested_obj, f"{referenced_by}[{i}]")
                        obj_info["elements"][i]["nested_object"] = nested_info

            self.objects[obj_id] = obj_info
            self.next_address += 0x20  # 每个对象分配32字节空间

        return self.objects[obj_id]

    def remove_reference(self, obj, variable_name: str = None):
        """
        移除对象引用

        【用途】
        当变量被重新赋值或删除时，调用此方法减少引用计数
        """
        obj_id = id(obj)
        if obj_id in self.objects:
            self.objects[obj_id]["ref_count"] -= 1
            if variable_name and variable_name in self.objects[obj_id]["referenced_by"]:
                self.objects[obj_id]["referenced_by"].remove(variable_name)

            # 引用计数为0，释放对象
            if self.objects[obj_id]["ref_count"] <= 0:
                del self.objects[obj_id]

    def get_all_objects(self):
        """获取所有对象的列表"""
        return list(self.objects.values())

    def get_object_by_address(self, address: str):
        """根据地址获取对象"""
        for obj_info in self.objects.values():
            if obj_info["address"] == address:
                return obj_info
        return None


# ============================================
# 【变量追踪器 - 追踪Python中的变量（引用）】
# ============================================
class VariableTracker:
    """
    变量追踪器 - 追踪Python中的变量（引用）

    【核心概念】
    Python的变量是"标签"（引用），贴在对象上：
    - 变量存储的是对象的地址（引用）
    - 变量本身不是对象，是指向对象的引用
    - 同一个对象可以被多个变量引用

    【数据结构】
    variables: {
        "变量名": {
            "name": "a",                    # 变量名
            "address": "0x100000",          # 变量自己的地址（标签的位置）
            "points_to": "0x200000",        # 指向的对象地址
            "type": "int/list",            # 变量类型（实际是引用的类型）
            "is_reference": True,            # 明确标记为引用
            "value": 10 或 [...]           # 变量的值（实际是对象的值）
        }
    }

    【示例】
    a = 10
    b = a

    内存布局：
    - 变量 a: 地址 0x100000，指向 0x200000（整数对象10）
    - 变量 b: 地址 0x100010，指向 0x200000（同一个整数对象10）
    - 对象 10: 地址 0x200000，值=10，引用计数=2
    """

    def __init__(self, object_tracker: ObjectTracker):
        """初始化变量追踪器"""
        self.variables = {}  # 存储所有变量
        self.object_tracker = object_tracker  # 关联对象追踪器
        self.next_address = 0x100000  # 变量地址从0x100000开始

    def create_variable(self, name: str, value: Any):
        """
        创建变量（引用）

        【参数】
        - name: 变量名
        - value: 变量值

        【返回值】
        - 变量信息字典

        【工作流程】
        1. 为变量分配地址（标签的位置）
        2. 创建值对象
        3. 记录变量指向对象的关系
        """
        # 为变量分配地址
        var_address = hex(self.next_address)
        self.next_address += 0x10  # 每个变量占16字节

        # 创建对象
        obj_info = self.object_tracker.create_object(value, referenced_by=name)

        # 创建变量引用
        var_info = {
            "name": name,
            "address": var_address,           # 变量自己的地址
            "points_to": obj_info["address"], # 指向的对象地址
            "type": type(value).__name__,      # 类型
            "is_reference": True,             # 明确标记为引用
            "value": value,                   # 变量的值
            "object": obj_info                # 关联的对象信息
        }

        self.variables[name] = var_info
        return var_info

    def update_variable(self, name: str, new_value: Any):
        """
        更新变量引用

        【参数】
        - name: 变量名
        - new_value: 新值

        【说明】
        更新变量时，需要：
        1. 减少旧对象的引用计数
        2. 创建新对象
        3. 更新变量指向新对象
        """
        # 如果变量已存在，减少旧对象的引用
        if name in self.variables:
            old_obj = self.variables[name]["object"]
            self.object_tracker.remove_reference(old_obj["value"], variable_name=name)

        # 创建新对象并更新变量
        var_info = self.create_variable(name, new_value)
        return var_info

    def get_variable_info(self, name: str) -> Optional[Dict]:
        """获取变量信息"""
        return self.variables.get(name)

    def get_all_variables(self) -> List[Dict]:
        """获取所有变量"""
        return list(self.variables.values())

    def get_references_to_object(self, object_address: str) -> List[str]:
        """获取指向特定对象的所有变量"""
        refs = []
        for var_info in self.variables.values():
            if var_info["points_to"] == object_address:
                refs.append(var_info["name"])
        return refs


# ============================================
# 【Python解析器类 - 改进版】
# ============================================
class PythonParser:
    """
    Python代码解析器 - 改进版

    【核心功能】
    根据Python的引用存储逻辑，正确解析和追踪代码执行过程：
    1. 区分变量（引用/标签）和对象（实际数据）
    2. 追踪变量到对象的引用关系
    3. 展示引用计数
    4. 正确处理浅拷贝和深拷贝

    【与原版的区别】
    原版将变量和对象混在一起，无法清晰展示Python的引用机制。
    改进版明确区分：
    - variables: 变量（引用/标签）
    - objects: 对象（实际数据）
    - references: 引用关系（箭头）

    【可视化数据结构】
    {
        "variables": [  # 变量列表（引用）
            {
                "name": "a",
                "address": "0x100000",      # 变量地址
                "points_to": "0x200000",    # 指向的对象地址
                "type": "int",
                "value": 10,
                "is_reference": True
            }
        ],
        "objects": [  # 对象列表（实际数据）
            {
                "address": "0x200000",
                "type": "int",
                "value": 10,
                "ref_count": 2,
                "referenced_by": ["a", "b"]
            }
        ],
        "references": [  # 引用关系（箭头）
            {
                "from": "a",        # 变量名
                "to": "0x200000"    # 对象地址
            }
        ]
    }
    """

    def __init__(self):
        """初始化解析器"""
        self.steps = []  # 执行步骤
        self.variable_history = []  # 变量历史
        self.object_tracker = ObjectTracker()  # 对象追踪器
        self.variable_tracker = VariableTracker(self.object_tracker)  # 变量追踪器

    def parse_code(self, code: str) -> Dict[str, Any]:
        """
        解析Python代码

        【参数】
        - code: Python代码字符串

        【返回】
        - 包含解析结果的字典：
          {
            "steps": [...],
            "variable_history": [...],
            "success": True
          }
        """
        # 重置状态
        self.steps = []
        self.variable_history = []
        self.object_tracker = ObjectTracker()
        self.variable_tracker = VariableTracker(self.object_tracker)

        # 解析代码生成AST树
        try:
            tree = ast.parse(code)
        except Exception as e:
            return {"error": str(e)}

        # 记录初始状态
        self._record_state(0, "初始状态")

        # 遍历AST树的每个节点
        step_index = 1
        for node in tree.body:
            step_info = self._process_node(node, code, step_index)
            if step_info:
                self.steps.append(step_info)
                step_index += 1

        return {
            "steps": self.steps,
            "variable_history": self.variable_history,
            "success": True
        }

    def _record_state(self, step_num: int, description: str):
        """
        记录当前步骤的完整状态

        【功能】
        记录变量、对象和引用关系，用于可视化展示
        """
        state = {
            "step": step_num,
            "description": description,
            "variables": {},
            "objects": [],
            "references": []
        }

        # 记录所有变量
        for name, var_info in self.variable_tracker.variables.items():
            # 获取对象的详细信息
            obj_info = var_info["object"]
            state["variables"][name] = {
                "name": name,
                "address": var_info["address"],
                "points_to": var_info["points_to"],
                "type": var_info["type"],
                "value": self._format_value(var_info["value"]),
                "is_reference": True,
                "ref_count": obj_info["ref_count"],
                "referenced_by": obj_info["referenced_by"]
            }

            # 如果是列表，添加元素引用信息
            if isinstance(var_info["value"], list):
                state["variables"][name]["elements"] = obj_info["elements"]
                state["variables"][name]["is_list"] = True

        # 记录所有对象
        for obj_id, obj_info in self.object_tracker.objects.items():
            state["objects"].append({
                "address": obj_info["address"],
                "type": obj_info["type"],
                "value": self._format_value(obj_info["value"]),
                "ref_count": obj_info["ref_count"],
                "referenced_by": obj_info["referenced_by"],
                "elements": obj_info.get("elements", [])
            })

        # 记录引用关系
        for var_info in self.variable_tracker.variables.values():
            state["references"].append({
                "variable": var_info["name"],
                "variable_address": var_info["address"],
                "object_address": var_info["points_to"]
            })

        self.variable_history.append(state)

    def _format_value(self, value):
        """格式化值用于显示"""
        if isinstance(value, str):
            if len(value) > 50:
                return repr(value[:47] + "...")
            return repr(value)
        if isinstance(value, list):
            if len(str(value)) > 50:
                return repr(value[:47] + "...")
        return repr(value)

    def _process_node(self, node, code: str, step_num: int) -> Optional[Dict]:
        """处理AST节点"""
        code_line = ast.get_source_segment(code, node)

        if isinstance(node, ast.Assign):
            return self._process_assign(node, code_line, step_num)
        elif isinstance(node, ast.AnnAssign):
            return self._process_ann_assign(node, code_line, step_num)
        elif isinstance(node, ast.Expr):
            return self._process_expr(node, code_line, step_num)
        elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            return self._process_import(node, code_line, step_num)

        return None

    def _process_assign(self, node: ast.Assign, code_line: str, step_num: int) -> Optional[Dict]:
        """
        处理赋值语句

        【示例】
        a = 10          # 创建变量a，指向整数对象10
        b = a           # 创建变量b，指向变量a指向的对象（共享引用）
        lst = [1, 2]    # 创建列表对象，创建变量lst指向它

        【Python的赋值逻辑】
        1. 计算右侧表达式的值（创建对象）
        2. 创建变量（如果不存在）
        3. 让变量指向对象
        4. 增加对象的引用计数
        """
        targets = []

        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                value = self._eval_node(node.value)

                # 如果变量已存在，更新引用
                if var_name in self.variable_tracker.variables:
                    self.variable_tracker.update_variable(var_name, value)
                else:
                    # 创建新变量
                    self.variable_tracker.create_variable(var_name, value)

                var_info = self.variable_tracker.get_variable_info(var_name)
                targets.append({
                    "name": var_name,
                    "address": var_info["address"],
                    "points_to": var_info["points_to"],
                    "type": var_info["type"],
                    "value": self._format_value(value)
                })

        self._record_state(step_num, f"赋值: {code_line}")

        return {
            "type": "assign",
            "targets": targets,
            "code": code_line,
            "line": node.lineno
        }

    def _process_ann_assign(self, node: ast.AnnAssign, code_line: str, step_num: int) -> Optional[Dict]:
        """处理类型注解赋值"""
        if node.value and isinstance(node.target, ast.Name):
            var_name = node.target.id
            value = self._eval_node(node.value)

            if var_name in self.variable_tracker.variables:
                self.variable_tracker.update_variable(var_name, value)
            else:
                self.variable_tracker.create_variable(var_name, value)

            var_info = self.variable_tracker.get_variable_info(var_name)
            self._record_state(step_num, f"声明: {code_line}")

            return {
                "type": "declare",
                "targets": [{
                    "name": var_name,
                    "address": var_info["address"],
                    "points_to": var_info["points_to"],
                    "type": var_info["type"],
                    "value": self._format_value(value)
                }],
                "code": code_line,
                "line": node.lineno
            }
        return None

    def _process_expr(self, node: ast.Expr, code_line: str, step_num: int) -> Optional[Dict]:
        """处理表达式语句"""
        if isinstance(node.value, ast.Call):
            return self._process_call(node.value, code_line, step_num)
        return None

    def _process_import(self, node, code_line: str, step_num: int) -> Optional[Dict]:
        """处理导入语句"""
        self._record_state(step_num, f"导入: {code_line}")
        return {
            "type": "import",
            "code": code_line,
            "line": node.lineno
        }

    def _process_call(self, node: ast.Call, code_line: str, step_num: int) -> Optional[Dict]:
        """
        处理函数调用

        【示例】
        lst.append(10)    # 列表方法调用
        copy.copy(lst)    # 浅拷贝
        deepcopy(lst)     # 深拷贝

        【浅拷贝 vs 深拷贝】
        浅拷贝：
        - 创建新列表对象
        - 元素仍是原列表元素的引用
        - 修改原列表元素会影响拷贝列表

        深拷贝：
        - 创建新列表对象
        - 递归创建所有元素的新副本
        - 完全独立，互不影响
        """
        if isinstance(node.func, ast.Attribute):
            obj = self._eval_node(node.func.value)
            method_name = node.func.attr
            args = [self._eval_node(arg) for arg in node.args]

            if isinstance(obj, list):
                if method_name == "append":
                    obj.append(args[0])
                    # 更新列表对象
                    var_name = self._find_variable_for_object(id(obj))
                    if var_name:
                        # 更新对象追踪器中的列表元素
                        obj_info = self.object_tracker.objects.get(id(obj))
                        if obj_info:
                            new_elem_info = self.object_tracker.create_object(args[0], f"{var_name}[{len(obj)-1}]")
                            obj_info["elements"].append({
                                "index": len(obj) - 1,
                                "value": args[0],
                                "address": new_elem_info["address"],
                                "type": type(args[0]).__name__,
                                "is_reference": True
                            })

                    self._record_state(step_num, f"列表追加: {code_line}")
                    return {
                        "type": "list_method",
                        "method": "append",
                        "code": code_line,
                        "line": node.lineno
                    }
                elif method_name == "copy":
                    new_list = copy.copy(obj)
                    return {
                        "type": "copy",
                        "method": "shallow",
                        "code": code_line,
                        "line": node.lineno
                    }

        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            args = [self._eval_node(arg) for arg in node.args]

            if func_name == "copy" and args:
                result = copy.copy(args[0])
                return {
                    "type": "copy",
                    "method": "shallow",
                    "code": code_line,
                    "line": node.lineno
                }
            elif func_name == "deepcopy" and args:
                result = copy.deepcopy(args[0])
                return {
                    "type": "copy",
                    "method": "deep",
                    "code": code_line,
                    "line": node.lineno
                }

        return None

    def _find_variable_for_object(self, obj_id: int) -> Optional[str]:
        """查找指向特定对象的变量名"""
        for name, var_info in self.variable_tracker.variables.items():
            if id(var_info["value"]) == obj_id:
                return name
        return None

    def _eval_node(self, node: ast.AST) -> Any:
        """
        计算AST节点的值

        【支持】
        - 常量（数字、字符串）
        - 变量名
        - 列表
        - 二元运算
        - 函数调用
        """
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            var_info = self.variable_tracker.get_variable_info(node.id)
            return var_info["value"] if var_info else None
        elif isinstance(node, ast.List):
            return [self._eval_node(elem) for elem in node.elts]
        elif isinstance(node, ast.ListComp):
            result = []
            for gen in node.generators:
                iter_obj = self._eval_node(gen.iter)
                if iter_obj is None:
                    continue
                for val in iter_obj:
                    if isinstance(gen.target, ast.Name):
                        self.variable_tracker.create_variable(gen.target.id, val)
                    result.append(self._eval_node(node.elt))
            return result
        elif isinstance(node, ast.Dict):
            return {
                self._eval_node(key): self._eval_node(value)
                for key, value in zip(node.keys, node.values)
            }
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                return left / right
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.USub):
                return -operand
        elif isinstance(node, ast.Subscript):
            obj = self._eval_node(node.value)
            idx = self._eval_node(node.slice)
            if isinstance(obj, list):
                return obj[idx] if 0 <= idx < len(obj) else None
        elif isinstance(node, ast.Call):
            args = [self._eval_node(arg) for arg in node.args]
            if isinstance(node.func, ast.Attribute):
                obj = self._eval_node(node.func.value)
                method_name = node.func.attr
                if hasattr(obj, method_name):
                    method = getattr(obj, method_name)
                    return method(*args)

        return None
