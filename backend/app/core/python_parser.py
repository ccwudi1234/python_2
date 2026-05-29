# -*- coding: utf-8 -*-
"""
【Python代码解析器 - python_parser.py】
================================
这个文件是核心解析器，用于分析Python代码并追踪变量变化。

【学习要点】
1. AST (Abstract Syntax Tree): Python抽象语法树
   - ast.parse(): 将代码字符串转换为AST树
   - ast.Assign: 赋值语句节点
   - ast.Name: 变量名节点
   - ast.Constant: 常量节点
   
2. 内存追踪: 模拟内存地址分配
   - id(): Python内置函数，获取对象唯一标识
   - hex(): 将数字转换为十六进制字符串
   
3. 代码执行模拟: 不真正执行代码，而是解析AST

【核心功能】
- 解析Python代码，生成执行步骤
- 追踪变量的值、类型、内存地址变化
- 支持列表、字典等复杂数据结构
- 支持浅拷贝、深拷贝分析
"""

import ast
import copy
from typing import List, Dict, Any, Optional

# ============================================
# 【内存追踪器类】
# ============================================
class MemoryTracker:
    """
    内存追踪器 - 模拟内存地址分配
    
    【功能】
    - 为每个对象分配模拟的内存地址
    - 追踪对象的引用计数
    - 当引用计数为0时，释放对象
    
    【学习要点】
    Python的内存管理：
    - 每个对象有唯一的id（内存地址）
    - 引用计数：有多少变量指向这个对象
    - 当引用计数为0，对象被垃圾回收
    
    【示例】
    tracker = MemoryTracker()
    addr = tracker.get_address([1, 2, 3])  # 获取列表的模拟地址
    """
    
    def __init__(self):
        """初始化：创建空的对象字典"""
        self.objects = {}  # 存储所有被追踪的对象
    
    def get_address(self, obj):
        """
        获取对象的模拟内存地址
        
        【参数】
        - obj: 要追踪的对象
        
        【返回】
        - 十六进制格式的地址字符串
        
        【工作原理】
        1. 使用id(obj)获取Python内部的对象标识
        2. 如果是新对象，创建地址记录
        3. 如果是已存在对象，增加引用计数
        """
        obj_id = id(obj)  # Python内置函数，获取对象唯一标识
        
        if obj_id not in self.objects:
            # 新对象：创建记录
            self.objects[obj_id] = {
                "address": hex(obj_id),  # 转换为十六进制，如 0x7f8a3c
                "type": type(obj).__name__,  # 对象类型，如 'list', 'int'
                "ref_count": 1  # 引用计数初始为1
            }
        else:
            # 已存在对象：增加引用计数
            self.objects[obj_id]["ref_count"] += 1
        
        return self.objects[obj_id]["address"]
    
    def dereference(self, obj):
        """
        减少对象的引用计数
        
        【用途】
        当变量被重新赋值或删除时，减少旧对象的引用计数
        
        【垃圾回收模拟】
        当引用计数为0时，从追踪字典中删除对象
        （模拟Python的垃圾回收机制）
        """
        obj_id = id(obj)
        if obj_id in self.objects:
            self.objects[obj_id]["ref_count"] -= 1
            if self.objects[obj_id]["ref_count"] <= 0:
                del self.objects[obj_id]  # 引用计数为0，释放对象

# ============================================
# 【Python解析器类】
# ============================================
class PythonParser:
    """
    Python代码解析器
    
    【核心功能】
    1. 解析Python代码，生成AST树
    2. 遍历AST，模拟代码执行
    3. 追踪每一步的变量状态
    4. 生成可视化数据
    
    【使用示例】
    parser = PythonParser()
    result = parser.parse_code("a = 10\\nb = 20")
    # result包含：steps（执行步骤）、variable_history（变量历史）
    
    【工作流程】
    1. 初始化状态
    2. 解析代码生成AST
    3. 遍历AST节点
    4. 处理每种类型的节点（赋值、表达式等）
    5. 记录每步的变量状态
    6. 返回结果
    """
    
    def __init__(self):
        """初始化解析器状态"""
        self.steps = []  # 存储执行步骤
        self.variable_history = []  # 存储变量变化历史
        self.memory_tracker = MemoryTracker()  # 内存追踪器
        self.globals = {}  # 模拟的全局变量字典
    
    def parse_code(self, code: str) -> Dict[str, Any]:
        """
        解析Python代码
        
        【参数】
        - code: Python代码字符串
        
        【返回】
        - 包含解析结果的字典：
          {
            "steps": [...],  # 执行步骤列表
            "variable_history": [...],  # 变量历史
            "success": True  # 是否成功
          }
        
        【异常处理】
        如果代码有语法错误，返回 {"error": "错误信息"}
        """
        # 重置状态
        self.steps = []
        self.variable_history = []
        self.memory_tracker = MemoryTracker()
        self.globals = {}
        
        # 解析代码生成AST树
        try:
            tree = ast.parse(code)  # 将代码字符串转换为AST
        except Exception as e:
            # 语法错误，返回错误信息
            return {"error": str(e)}
        
        # 记录初始状态（所有变量为空）
        self._record_state(0, "Initial state")
        
        # 遍历AST树的每个节点
        step_index = 1
        for node in tree.body:  # tree.body是代码中的语句列表
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
        记录当前步骤的变量状态
        
        【参数】
        - step_num: 步骤编号
        - description: 步骤描述
        
        【功能】
        遍历所有变量，记录每个变量的详细信息：
        - 值
        - 内存地址
        - 类型
        - 是否是列表/字典
        - 元素信息（如果是列表）
        """
        state = {"step": step_num, "description": description, "variables": {}}
        
        for name, value in self.globals.items():
            state["variables"][name] = self._get_var_info(name, value)
        
        self.variable_history.append(state)
    
    def _get_var_info(self, name: str, value: Any) -> Dict:
        """
        获取变量的详细信息
        
        【参数】
        - name: 变量名
        - value: 变量值
        
        【返回】
        - 包含变量信息的字典
        
        【信息内容】
        - value: 变量的值（字符串形式）
        - address: 内存地址
        - type: 数据类型
        - is_list/is_dict: 是否是列表/字典
        - elements/items: 元素/键值对信息
        """
        info = {
            "value": self._format_value(value),
            "address": self.memory_tracker.get_address(value),
            "type": type(value).__name__,
            "is_list": isinstance(value, list),
            "is_dict": isinstance(value, dict),
            "nested": isinstance(value, (list, dict))
        }
        
        # 处理列表类型
        if isinstance(value, list):
            info["elements"] = []
            for i, elem in enumerate(value):
                elem_info = {
                    "index": i,
                    "value": self._format_value(elem),
                    "address": self.memory_tracker.get_address(elem),
                    "type": type(elem).__name__
                }
                
                # 处理嵌套列表（二维数组）
                if isinstance(elem, list):
                    elem_info["nested_elements"] = []
                    for j, nested in enumerate(elem):
                        elem_info["nested_elements"].append({
                            "index": j,
                            "value": self._format_value(nested),
                            "address": self.memory_tracker.get_address(nested),
                            "type": type(nested).__name__
                        })
                
                info["elements"].append(elem_info)
        
        # 处理字典类型
        elif isinstance(value, dict):
            info["items"] = []
            for k, v in value.items():
                info["items"].append({
                    "key": {
                        "value": self._format_value(k),
                        "address": self.memory_tracker.get_address(k),
                        "type": type(k).__name__
                    },
                    "value": {
                        "value": self._format_value(v),
                        "address": self.memory_tracker.get_address(v),
                        "type": type(v).__name__
                    }
                })
        
        return info
    
    def _format_value(self, value):
        """
        格式化变量值
        
        【参数】
        - value: 变量值
        
        【返回】
        - 字符串形式的值
        
        【处理】
        - 字符串：使用repr()保留引号
        - 长字符串：截断显示
        - 其他类型：使用repr()
        """
        if isinstance(value, str):
            if len(value) > 50:
                return repr(value[:47] + "...")  # 截断长字符串
            return repr(value)  # repr()会保留引号
        return repr(value)
    
    def _process_node(self, node, code: str, step_num: int) -> Optional[Dict]:
        """
        处理AST节点
        
        【参数】
        - node: AST节点
        - code: 原始代码字符串
        - step_num: 步骤编号
        
        【返回】
        - 步骤信息字典，或None
        
        【节点类型处理】
        - ast.Assign: 赋值语句 (a = 10)
        - ast.AnnAssign: 类型注解赋值 (a: int = 10)
        - ast.Expr: 表达式语句 (print(a))
        - ast.Import: 导入语句 (import math)
        """
        code_line = ast.get_source_segment(code, node)  # 获取节点的源代码
        
        if isinstance(node, ast.Assign):
            return self._process_assign(node, code_line, step_num)
        elif isinstance(node, ast.AnnAssign):
            return self._process_ann_assign(node, code_line, step_num)
        elif isinstance(node, ast.Expr):
            return self._process_expr(node, code_line, step_num)
        elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            return self._process_import(node, code_line, step_num)
        
        return None
    
    def _process_import(self, node, code_line: str, step_num: int) -> Optional[Dict]:
        """
        处理导入语句
        
        【示例】
        import math
        from copy import deepcopy
        
        【功能】
        模拟导入模块，将模块存入globals字典
        """
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.globals[alias.asname or alias.name] = __import__(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = __import__(node.module, fromlist=[])
            for alias in node.names:
                self.globals[alias.asname or alias.name] = getattr(module, alias.name, None)
        
        self._record_state(step_num, f"Import: {code_line}")
        
        return {
            "type": "import",
            "code": code_line,
            "line": node.lineno
        }
    
    def _process_assign(self, node: ast.Assign, code_line: str, step_num: int) -> Optional[Dict]:
        """
        处理赋值语句
        
        【示例】
        a = 10
        b = [1, 2, 3]
        lst[0] = 100  # 列表元素赋值
        
        【功能】
        1. 解析赋值目标（变量名）
        2. 计算赋值值
        3. 更新globals字典
        4. 追踪内存地址变化
        5. 记录状态
        """
        targets = []  # 存储赋值目标信息
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                # 简单变量赋值：a = 10
                var_name = target.id  # 变量名
                value = self._eval_node(node.value)  # 计算值
                old_value = self.globals.get(var_name)  # 获取旧值
                
                # 如果变量已有值，减少旧值的引用计数
                if old_value is not None:
                    self.memory_tracker.dereference(old_value)
                
                # 更新变量
                self.globals[var_name] = value
                
                targets.append({
                    "name": var_name,
                    "old_address": self.memory_tracker.get_address(old_value) if old_value is not None else None,
                    "new_address": self.memory_tracker.get_address(value)
                })
            
            elif isinstance(target, ast.Subscript):
                # 列表元素赋值：lst[0] = 100
                base_name = None
                if isinstance(target.value, ast.Name):
                    base_name = target.value.id
                
                idx = self._eval_node(target.slice)  # 索引
                value = self._eval_node(node.value)  # 新值
                
                if base_name and base_name in self.globals:
                    base_obj = self.globals[base_name]
                    if isinstance(base_obj, list) and isinstance(idx, int):
                        old_val = base_obj[idx] if 0 <= idx < len(base_obj) else None
                        base_obj[idx] = value
                        
                        targets.append({
                            "name": f"{base_name}[{idx}]",
                            "old_address": self.memory_tracker.get_address(old_val) if old_val is not None else None,
                            "new_address": self.memory_tracker.get_address(value)
                        })
        
        self._record_state(step_num, f"Assign: {code_line}")
        
        return {
            "type": "assign",
            "targets": targets,
            "code": code_line,
            "line": node.lineno
        }
    
    def _process_ann_assign(self, node: ast.AnnAssign, code_line: str, step_num: int) -> Optional[Dict]:
        """
        处理类型注解赋值
        
        【示例】
        a: int = 10
        b: list = [1, 2, 3]
        
        【功能】
        与普通赋值类似，但带有类型注解
        """
        if node.value and isinstance(node.target, ast.Name):
            var_name = node.target.id
            value = self._eval_node(node.value)
            old_value = self.globals.get(var_name)
            
            if old_value is not None:
                self.memory_tracker.dereference(old_value)
            
            self.globals[var_name] = value
            
            self._record_state(step_num, f"Declare: {code_line}")
            
            return {
                "type": "declare",
                "targets": [{
                    "name": var_name,
                    "old_address": self.memory_tracker.get_address(old_value) if old_value is not None else None,
                    "new_address": self.memory_tracker.get_address(value)
                }],
                "code": code_line,
                "line": node.lineno
            }
        return None
    
    def _process_expr(self, node: ast.Expr, code_line: str, step_num: int) -> Optional[Dict]:
        """
        处理表达式语句
        
        【示例】
        lst.append(10)
        print(a)
        
        【功能】
        处理函数调用表达式
        """
        if isinstance(node.value, ast.Call):
            return self._process_call(node.value, code_line, step_num)
        return None
    
    def _process_call(self, node: ast.Call, code_line: str, step_num: int) -> Optional[Dict]:
        """
        处理函数调用
        
        【示例】
        lst.append(10)
        copy.copy(lst)
        deepcopy(lst)
        
        【功能】
        1. 解析函数名和参数
        2. 执行函数调用
        3. 记录结果
        
        【支持的函数】
        - list.append()
        - list.extend()
        - list.copy()
        - copy.copy()  浅拷贝
        - copy.deepcopy()  深拷贝
        """
        func_name = None
        args = []
        
        if isinstance(node.func, ast.Attribute):
            # 方法调用：obj.method()
            obj = self._eval_node(node.func.value)
            method_name = node.func.attr
            args = [self._eval_node(arg) for arg in node.args]
            
            if isinstance(obj, list):
                if method_name == "append":
                    obj.append(args[0])
                    self._record_state(step_num, f"List append: {code_line}")
                    return {
                        "type": "list_method",
                        "method": "append",
                        "code": code_line,
                        "line": node.lineno
                    }
                elif method_name == "extend":
                    obj.extend(args[0])
                    self._record_state(step_num, f"List extend: {code_line}")
                    return {
                        "type": "list_method",
                        "method": "extend",
                        "code": code_line,
                        "line": node.lineno
                    }
                elif method_name == "copy":
                    new_list = copy.copy(obj)
                    return {
                        "type": "copy",
                        "method": "shallow",
                        "code": code_line,
                        "line": node.lineno,
                        "new_address": self.memory_tracker.get_address(new_list)
                    }
        
        elif isinstance(node.func, ast.Name):
            # 函数调用：func()
            func_name = node.func.id
            args = [self._eval_node(arg) for arg in node.args]
            
            if func_name == "list":
                if args:
                    return {
                        "type": "list_creation",
                        "code": code_line,
                        "line": node.lineno
                    }
            elif func_name == "copy":
                if args:
                    result = copy.copy(args[0])
                    return {
                        "type": "copy",
                        "method": "shallow",
                        "code": code_line,
                        "line": node.lineno,
                        "new_address": self.memory_tracker.get_address(result)
                    }
            elif func_name == "deepcopy":
                if args:
                    result = copy.deepcopy(args[0])
                    return {
                        "type": "copy",
                        "method": "deep",
                        "code": code_line,
                        "line": node.lineno,
                        "new_address": self.memory_tracker.get_address(result)
                    }
        
        return None
    
    def _eval_node(self, node: ast.AST) -> Any:
        """
        计算AST节点的值
        
        【参数】
        - node: AST节点
        
        【返回】
        - 节点的计算值
        
        【支持的节点类型】
        - ast.Constant: 常量（数字、字符串）
        - ast.Name: 变量名
        - ast.List: 列表
        - ast.Dict: 字典
        - ast.BinOp: 二元运算（加减乘除）
        - ast.Subscript: 下标访问
        - ast.Call: 函数调用
        """
        if isinstance(node, ast.Constant):
            return node.value
        
        elif isinstance(node, ast.Name):
            return self.globals.get(node.id)
        
        elif isinstance(node, ast.List):
            return [self._eval_node(elem) for elem in node.elts]
        
        elif isinstance(node, ast.ListComp):
            # 列表推导式：[x for x in range(10)]
            result = []
            for gen in node.generators:
                iter_obj = self._eval_node(gen.iter)
                if iter_obj is None:
                    continue
                for val in iter_obj:
                    if isinstance(gen.target, ast.Name):
                        self.globals[gen.target.id] = val
                    result.append(self._eval_node(node.elt))
            return result
        
        elif isinstance(node, ast.Dict):
            return {
                self._eval_node(key): self._eval_node(value)
                for key, value in zip(node.keys, node.values)
            }
        
        elif isinstance(node, ast.BinOp):
            # 二元运算
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
            elif isinstance(node.op, ast.Mod):
                return left % right
        
        elif isinstance(node, ast.UnaryOp):
            # 一元运算
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.USub):
                return -operand
            elif isinstance(node.op, ast.UAdd):
                return +operand
        
        elif isinstance(node, ast.Subscript):
            # 下标访问：lst[0], dict['key']
            obj = self._eval_node(node.value)
            idx = self._eval_node(node.slice)
            if isinstance(obj, list):
                return obj[idx] if 0 <= idx < len(obj) else None
            elif isinstance(obj, dict):
                return obj.get(idx)
        
        elif isinstance(node, ast.Call):
            # 函数调用
            args = [self._eval_node(arg) for arg in node.args]
            if isinstance(node.func, ast.Attribute):
                obj = self._eval_node(node.func.value)
                method_name = node.func.attr
                if hasattr(obj, method_name):
                    method = getattr(obj, method_name)
                    return method(*args)
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in self.globals:
                    func = self.globals[func_name]
                    return func(*args)
                elif func_name == "list":
                    if args:
                        return list(args[0])
        
        return None