# -*- coding: utf-8 -*-
"""
【C/C++代码解析器 - c_parser.py】
================================
这个文件用于解析C/C++代码，模拟内存布局。

【学习要点】
1. C语言内存模型：
   - 栈内存：局部变量自动分配
   - 堆内存：malloc手动分配，free释放
   - 指针：存储内存地址的变量
   
2. 数据类型大小：
   - char: 1字节
   - short: 2字节
   - int: 4字节
   - long: 8字节
   - float: 4字节
   - double: 8字节
   
3. 正则表达式解析：使用re模块匹配C语法

【核心功能】
- 解析变量声明和赋值
- 模拟内存地址分配
- 处理数组声明
- 处理指针操作
- 处理malloc/free动态内存
"""

from typing import List, Dict, Any
import re

# ============================================
# 【内存块类】
# ============================================
class MemoryBlock:
    """
    内存块 - 表示一个内存单元
    
    【属性】
    - address: 内存地址（十六进制）
    - size: 占用大小（字节）
    - value: 存储的值
    - var_type: 变量类型
    - is_pointer: 是否是指针
    - points_to: 指针指向的地址
    
    【用途】
    模拟C语言中的内存单元，用于可视化内存布局
    """
    
    def __init__(self, address: str, size: int, value, var_type: str):
        self.address = address
        self.size = size
        self.value = value
        self.var_type = var_type
        self.is_pointer = False
        self.points_to = None

# ============================================
# 【C解析器类】
# ============================================
class CParser:
    """
    C/C++代码解析器
    
    【核心功能】
    1. 解析C代码，识别变量声明和赋值
    2. 模拟内存地址分配
    3. 追踪变量变化历史
    4. 支持数组、指针、动态内存
    
    【使用示例】
    parser = CParser()
    result = parser.parse_code("int main() { int a = 10; }")
    
    【工作流程】
    1. 初始化内存模拟器
    2. 解析代码行
    3. 处理声明、赋值、malloc、free
    4. 记录每步状态
    5. 返回结果
    """
    
    def __init__(self):
        """初始化解析器状态"""
        self.steps = []  # 执行步骤
        self.memory = {}  # 内存状态字典
        self.variable_history = []  # 变量历史
        
        # 内存地址模拟：从0x100000开始分配
        self.next_address = 0x100000
        
        # 指针大小：64位系统指针占8字节
        self.pointer_size = 8
        
        # 数据类型大小映射（字节）
        self.type_sizes = {
            'char': 1,    # 字符类型
            'short': 2,   # 短整型
            'int': 4,     # 整型
            'long': 8,    # 长整型
            'float': 4,   # 单精度浮点
            'double': 8   # 双精度浮点
        }
    
    def _allocate_memory(self, var_type: str, is_pointer: bool = False) -> str:
        """
        分配模拟内存地址
        
        【参数】
        - var_type: 变量类型
        - is_pointer: 是否是指针
        
        【返回】
        - 十六进制地址字符串
        
        【工作原理】
        1. 根据类型确定占用大小
        2. 分配地址
        3. 更新下一个可用地址
        """
        # 指针固定占8字节，否则按类型大小
        size = self.type_sizes.get(var_type, 4) if not is_pointer else self.pointer_size
        
        # 获取当前地址并转换为十六进制
        address = hex(self.next_address)
        
        # 更新下一个可用地址
        self.next_address += size
        
        return address
    
    def parse_code(self, code: str) -> Dict[str, Any]:
        """
        解析C代码
        
        【参数】
        - code: C代码字符串
        
        【返回】
        - 解析结果字典
        
        【异常处理】
        解析失败返回 {"error": "错误信息"}
        """
        # 重置状态
        self.steps = []
        self.memory = {}
        self.variable_history = []
        self.next_address = 0x100000
        
        try:
            self._parse_code(code)
        except Exception as e:
            return {"error": str(e)}
        
        return {
            "steps": self.steps,
            "memory": self.memory,
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
        遍历memory字典，记录每个变量的信息
        """
        state = {"step": step_num, "description": description, "variables": {}}
        
        for name, info in self.memory.items():
            state["variables"][name] = {
                "value": info.get("value"),
                "address": info.get("address"),
                "type": info.get("type"),
                "is_list": info.get("is_array", False),
                "is_dict": False,
                "nested": info.get("is_array", False) and info.get("elements")
            }
            
            # 如果是数组，记录元素信息
            if info.get("is_array") and info.get("elements"):
                state["variables"][name]["elements"] = info["elements"]
        
        self.variable_history.append(state)
    
    def _parse_code(self, code: str):
        """
        内部解析方法
        
        【工作流程】
        1. 按行分割代码
        2. 检测main函数
        3. 处理每行语句
        4. 跳过注释
        """
        lines = code.strip().split('\n')
        step_num = 0
        
        # 记录初始状态
        self._record_state(step_num, "Initial state")
        step_num += 1
        
        # 是否在main函数内
        in_main = False
        brace_count = 0  # 大括号计数
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测main函数开始
            if 'int main' in line:
                in_main = True
                brace_count = 0
                continue
            
            # 跳过单行注释
            if line.startswith('//'):
                continue
            
            # 跳过多行注释
            if '/*' in line and '*/' in line:
                continue
            
            # 计算大括号
            if '{' in line:
                brace_count += line.count('{')
            
            if '}' in line:
                brace_count -= line.count('}')
                if brace_count <= 0:
                    in_main = False
                    continue
            
            # 不在main函数内则跳过
            if not in_main:
                continue
            
            # 分割语句（处理一行多条语句）
            statements = self._split_statements(line)
            for stmt in statements:
                stmt = stmt.strip()
                if not stmt or stmt.startswith('//'):
                    continue
                
                # 处理赋值语句
                if '=' in stmt:
                    self._parse_assignment(stmt, step_num)
                    step_num += 1
                # 处理声明语句
                elif self._is_declaration(stmt):
                    self._parse_declaration(stmt, step_num)
                    step_num += 1
                # 处理malloc动态分配
                elif 'malloc' in stmt.lower():
                    self._parse_malloc(stmt, step_num)
                    step_num += 1
                # 处理free释放
                elif 'free' in stmt.lower():
                    self._parse_free(stmt, step_num)
                    step_num += 1
    
    def _split_statements(self, line: str) -> List[str]:
        """
        分割一行中的多条语句
        
        【示例】
        "int a = 10; int b = 20;" -> ["int a = 10", "int b = 20"]
        
        【处理】
        以分号分割，但要注意括号内的分号不算
        """
        statements = []
        current = []
        paren_count = 0
        
        for char in line:
            if char == '(' and paren_count == 0 and current and current[-1] != '=':
                paren_count += 1
                current.append(char)
            elif char == '(':
                paren_count += 1
                current.append(char)
            elif char == ')':
                paren_count -= 1
                current.append(char)
            elif char == ';' and paren_count == 0:
                # 分号且不在括号内，分割语句
                statements.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        
        if current:
            statements.append(''.join(current).strip())
        
        return [s for s in statements if s]
    
    def _is_declaration(self, stmt: str) -> bool:
        """
        判断是否是声明语句
        
        【示例】
        "int a" -> True
        "a = 10" -> False
        
        【判断依据】
        以类型关键字开头
        """
        type_keywords = ['int', 'char', 'float', 'double', 'long', 'short', 'void']
        for keyword in type_keywords:
            if stmt.startswith(keyword + ' ') or stmt.startswith(keyword + '*'):
                return True
        return False
    
    def _parse_declaration(self, stmt: str, step_num: int):
        """
        解析变量声明
        
        【示例】
        int a = 10;
        int *p = NULL;
        int arr[5] = {1, 2, 3, 4, 5};
        
        【处理】
        1. 使用正则匹配类型、指针星号、变量名
        2. 分配内存地址
        3. 处理数组声明
        4. 记录状态
        """
        stmt = stmt.rstrip(';')
        
        # 正则匹配：类型 + 指针星号 + 变量名
        type_pattern = r'(const\s+)?(unsigned\s+)?(int|char|float|double|long|short|void)\s*(\*+)?\s*(\w+)'
        match = re.match(type_pattern, stmt)
        if not match:
            return
        
        const = match.group(1)      # const修饰符
        unsigned = match.group(2)   # unsigned修饰符
        base_type = match.group(3)  # 基本类型
        ptr_stars = match.group(4) or ''  # 指针星号
        var_name = match.group(5)   # 变量名
        
        is_pointer = len(ptr_stars) > 0
        address = self._allocate_memory(base_type, is_pointer)
        
        # 解析初始值
        value = None
        if '=' in stmt:
            parts = stmt.split('=', 1)
            right_part = parts[1].strip()
            value = self._eval_expression(right_part)
        
        # 处理数组声明
        if '[' in stmt and ']' in stmt:
            array_match = re.search(r'\[(\d*)\]', stmt)
            if array_match:
                size = int(array_match.group(1)) if array_match.group(1) else 0
                self._parse_array_declaration(var_name, base_type, size, stmt, step_num)
                return
        
        # 存储变量信息
        self.memory[var_name] = {
            "value": value,
            "address": address,
            "type": base_type + ('*' * len(ptr_stars)) if is_pointer else base_type,
            "is_pointer": is_pointer,
            "is_array": False
        }
        
        self._record_state(step_num, f"Declare: {stmt};")
        self.steps.append({
            "type": "declare",
            "name": var_name,
            "value": value,
            "address": address,
            "code": stmt + ';'
        })
    
    def _parse_array_declaration(self, var_name: str, base_type: str, size: int, stmt: str, step_num: int):
        """
        解析数组声明
        
        【示例】
        int arr[5] = {1, 2, 3, 4, 5};
        
        【处理】
        1. 分配连续内存
        2. 解析初始值
        3. 记录每个元素信息
        """
        address = self._allocate_memory(base_type, False)
        
        elements = []
        values = []
        
        # 解析初始值列表
        if '=' in stmt:
            parts = stmt.split('=', 1)
            right_part = parts[1].strip()
            if '{' in right_part and '}' in right_part:
                values_str = right_part[right_part.find('{')+1:right_part.find('}')]
                values = [self._eval_expression(v.strip()) for v in values_str.split(',')]
        
        # 创建元素信息
        for i in range(size):
            elem_value = values[i] if i < len(values) else 0
            elements.append({
                "index": i,
                "value": elem_value,
                # 数组元素地址连续
                "address": hex(int(address, 16) + i * self.type_sizes.get(base_type, 4)),
                "type": base_type
            })
        
        self.memory[var_name] = {
            "value": values,
            "address": address,
            "type": f"{base_type}[{size}]",
            "is_pointer": False,
            "is_array": True,
            "elements": elements
        }
        
        self._record_state(step_num, f"Array Declare: {stmt};")
        self.steps.append({
            "type": "array_declare",
            "name": var_name,
            "size": size,
            "elements": elements,
            "code": stmt + ';'
        })
    
    def _parse_assignment(self, stmt: str, step_num: int):
        """
        解析赋值语句
        
        【示例】
        a = 20;
        arr[0] = 100;
        *p = 10;
        """
        stmt = stmt.rstrip(';')
        
        if '=' not in stmt:
            return
        
        parts = stmt.split('=', 1)
        left = parts[0].strip()
        right = parts[1].strip()
        
        # 如果左边是声明，调用声明处理
        if self._is_declaration(left):
            self._parse_declaration(stmt, step_num)
            return
        
        # 处理数组元素赋值：arr[0] = 100
        array_match = re.match(r'(\w+)\[(\d+)\]', left)
        if array_match:
            var_name = array_match.group(1)
            index = int(array_match.group(2))
            value = self._eval_expression(right)
            
            if var_name in self.memory and self.memory[var_name].get("is_array"):
                elements = self.memory[var_name]["elements"]
                if index < len(elements):
                    old_value = elements[index]["value"]
                    elements[index]["value"] = value
                    self.memory[var_name]["value"][index] = value
            
            self._record_state(step_num, f"Assign: {stmt};")
            self.steps.append({
                "type": "array_assign",
                "name": f"{var_name}[{index}]",
                "value": value,
                "code": stmt + ';'
            })
            return
        
        # 处理指针赋值：*p = 10
        if '*' in left:
            ptr_name = left.replace('*', '').strip()
            value = self._eval_expression(right)
            
            if ptr_name in self.memory:
                self.memory[ptr_name]["points_to"] = value
            
            self._record_state(step_num, f"Pointer Assign: {stmt};")
            self.steps.append({
                "type": "pointer_assign",
                "name": ptr_name,
                "points_to": value,
                "code": stmt + ';'
            })
            return
        
        # 普通变量赋值
        var_name = left.strip()
        value = self._eval_expression(right)
        
        old_value = None
        if var_name in self.memory:
            old_value = self.memory[var_name]["value"]
        
        # 如果变量不存在，创建新变量
        if var_name not in self.memory:
            address = self._allocate_memory("int")
            self.memory[var_name] = {
                "value": value,
                "address": address,
                "type": "int",
                "is_pointer": False,
                "is_array": False
            }
        else:
            self.memory[var_name]["value"] = value
        
        self._record_state(step_num, f"Assign: {stmt};")
        self.steps.append({
            "type": "assign",
            "name": var_name,
            "old_value": old_value,
            "new_value": value,
            "code": stmt + ';'
        })
    
    def _parse_malloc(self, stmt: str, step_num: int):
        """
        解析malloc动态内存分配
        
        【示例】
        p = malloc(100);
        
        【功能】
        模拟堆内存分配，记录分配大小
        """
        match = re.match(r'(\w+)\s*=\s*malloc\s*\(\s*(\d+)\s*\)', stmt)
        if match:
            var_name = match.group(1)
            size = int(match.group(2))
            
            address = self._allocate_memory("void", True)
            self.memory[var_name] = {
                "value": address,
                "address": address,
                "type": "void*",
                "is_pointer": True,
                "is_array": False,
                "allocated_size": size
            }
            
            self._record_state(step_num, f"Malloc: {stmt};")
            self.steps.append({
                "type": "malloc",
                "name": var_name,
                "size": size,
                "address": address,
                "code": stmt + ';'
            })
    
    def _parse_free(self, stmt: str, step_num: int):
        """
        解析free释放内存
        
        【示例】
        free(p);
        
        【功能】
        从memory字典中删除变量，模拟释放内存
        """
        match = re.match(r'free\s*\(\s*(\w+)\s*\)', stmt)
        if match:
            var_name = match.group(1)
            
            if var_name in self.memory:
                del self.memory[var_name]
            
            self._record_state(step_num, f"Free: {stmt};")
            self.steps.append({
                "type": "free",
                "name": var_name,
                "code": stmt + ';'
            })
    
    def _eval_expression(self, expr: str) -> Any:
        """
        计算表达式值
        
        【支持】
        - 整数
        - 浮点数
        - 十六进制数
        - 变量引用
        - 算术运算
        """
        expr = expr.strip()
        
        try:
            # 整数
            if expr.isdigit():
                return int(expr)
            # 浮点数
            if '.' in expr and all(c.isdigit() or c == '.' for c in expr):
                return float(expr)
            # 十六进制
            if expr.startswith('0x') or expr.startswith('0X'):
                return int(expr, 16)
            # 变量引用
            if expr in self.memory:
                return self.memory[expr].get("value")
            
            # 算术表达式
            tokens = self._tokenize_expression(expr)
            if tokens:
                return self._evaluate_tokens(tokens)
            
            return expr
        except Exception:
            return expr
    
    def _tokenize_expression(self, expr: str) -> List[Any]:
        """
        将表达式分割为token
        
        【示例】
        "a + b * 2" -> ["a", "+", "b", "*", "2"]
        """
        tokens = []
        current = []
        
        for char in expr:
            if char in '+-*/':
                if current:
                    tokens.append(''.join(current))
                    current = []
                tokens.append(char)
            elif char.isspace():
                if current:
                    tokens.append(''.join(current))
                    current = []
            else:
                current.append(char)
        
        if current:
            tokens.append(''.join(current))
        
        return tokens
    
    def _evaluate_tokens(self, tokens: List[str]) -> Any:
        """
        计算token列表
        
        【算法】
        使用栈和运算符优先级计算表达式
        """
        if not tokens:
            return None
        
        values = []
        ops = []
        
        # 运算符优先级
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        
        for token in tokens:
            if token in precedence:
                # 处理优先级
                while ops and precedence[ops[-1]] >= precedence[token]:
                    self._apply_op(values, ops)
                ops.append(token)
            else:
                try:
                    if token in self.memory:
                        values.append(self.memory[token].get("value", 0))
                    else:
                        values.append(int(token))
                except ValueError:
                    return None
        
        while ops:
            self._apply_op(values, ops)
        
        return values[0] if values else None
    
    def _apply_op(self, values: List[int], ops: List[str]):
        """
        应用运算符
        
        【功能】
        从栈中取出两个值和一个运算符，计算结果
        """
        if len(values) < 2 or not ops:
            return
        
        b = values.pop()
        a = values.pop()
        op = ops.pop()
        
        if op == '+':
            values.append(a + b)
        elif op == '-':
            values.append(a - b)
        elif op == '*':
            values.append(a * b)
        elif op == '/':
            if b != 0:
                values.append(a // b)
            else:
                values.append(0)