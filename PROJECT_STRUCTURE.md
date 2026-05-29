# 代码可视化分析器 - 项目结构与知识点

## 一、项目概述

这是一个用于可视化分析Python和C/C++代码的Web应用，帮助初学者理解代码执行过程、内存布局和变量变化。

---

## 二、项目结构

```
project/
│
├── backend/                          # 后端 (Python FastAPI)
│   ├── start.py                      # 启动脚本
│   ├── requirements.txt              # Python依赖
│   │
│   └── app/                          # 应用主目录
│       ├── main.py                   # FastAPI入口
│       ├── config.py                 # 配置文件
│       │
│       ├── api/                      # API路由
│       │   ├── auth.py               # 用户认证API
│       │   ├── file.py               # 文件管理API
│       │   ├── parse.py              # 代码解析API
│       │   ├── record.py             # 分析记录API
│       │   └── visualize.py          # 可视化API
│       │
│       ├── core/                     # 核心解析器
│       │   ├── python_parser.py      # Python代码解析器
│       │   ├── c_parser.py           # C/C++代码解析器
│       │   └ visual_generator.py     # 可视化数据生成器
│       │
│       ├── db/                       # 数据库
│       │   └ models.py               # 数据模型
│       │
│       └ utils/                      # 工具模块
│       │   ├── auth.py               # 认证工具
│       │   ├── file_helper.py        # 文件助手
│       │   └ logger.py               # 日志工具
│       │
│       └── static/                   # 静态文件存储
│       └ logs/                       # 日志文件
│
├── frontend/                         # 前端 (Vue 3)
│   ├── package.json                  # Node依赖
│   ├── vite.config.js                # Vite配置
│   │
│   └ src/                            # 源代码
│       ├── main.js                   # Vue入口
│       ├── app.vue                   # 根组件
│       ├── style.css                 # 全局样式
│       │
│       ├── api/                      # API调用
│       │   └ index.js                # Axios配置
│       │
│       ├── components/               # 组件
│       │   ├── Navbar.vue            # 导航栏
│       │   └ ControlBar.vue          # 控制条
│       │
│       ├── views/                    # 页面
│       │   ├── Home.vue              # 首页
│       │   ├── PythonAnalysis.vue    # Python分析
│       │   ├── CAnalysis.vue         # C分析
│       │   ├── Files.vue             # 文件管理
│       │   ├── History.vue           # 历史记录
│       │   ├── Login.vue             # 登录
│       │   └ Register.vue            # 注册
│       │
│       ├── router/                   # 路由
│       │   └ index.js                # Vue Router
│       │
│       └ store/                      # 状态管理
│       │   └ index.js                # Pinia/Vuex
│
├── .env                              # 环境变量
├── .env.example                      # 环境变量示例
└── docker-compose.yml                # Docker配置
```

---

## 三、技术栈与知识点

### 1. 后端技术栈

| 技术 | 用途 | 学习要点 |
|------|------|----------|
| **FastAPI** | Web框架 | 路由、依赖注入、Pydantic验证 |
| **SQLAlchemy** | ORM数据库 | 模型定义、关系映射、会话管理 |
| **JWT** | 用户认证 | 令牌生成、验证、过期处理 |
| **bcrypt** | 密码加密 | 安全存储、加盐哈希 |
| **AST** | Python解析 | 抽象语法树、节点遍历 |
| **正则表达式** | C语言解析 | 模式匹配、语法识别 |

### 2. 前端技术栈

| 技术 | 用途 | 学习要点 |
|------|------|----------|
| **Vue 3** | 前端框架 | 组合式API、响应式、组件 |
| **Vite** | 构建工具 | 快速开发、热更新 |
| **Element Plus** | UI组件库 | 表单、表格、弹窗 |
| **Axios** | HTTP请求 | 拦截器、认证、错误处理 |
| **Vue Router** | 路由管理 | 导航守卫、动态路由 |

### 3. 核心知识点详解

#### 3.1 AST (抽象语法树)

```python
# AST是Python代码的树形表示
# 每个节点代表一个语法元素

import ast

code = "a = 10 + 20"
tree = ast.parse(code)

# tree.body[0] 是 ast.Assign 节点
# ast.Assign.targets 是赋值目标（变量名）
# ast.Assign.value 是赋值值（表达式）
```

**节点类型：**
- `ast.Assign`: 赋值语句 (a = 10)
- `ast.Name`: 变量名
- `ast.Constant`: 常量值
- `ast.List`: 列表
- `ast.BinOp`: 二元运算

#### 3.2 JWT认证流程

```
用户登录流程:
1. 用户提交用户名和密码
2. 后端验证密码
3. 生成JWT令牌（包含用户信息）
4. 返回令牌给前端
5. 前端存储令牌（localStorage）
6. 后续请求携带令牌
7. 后端验证令牌，提取用户信息
```

#### 3.3 内存地址模拟

```python
# Python内存追踪
id(obj)      # 获取对象唯一标识
hex(id(obj)) # 转换为十六进制地址

# C语言内存模拟
0x100000     # 起始地址
+4           # int占4字节
0x100004     # 下一个变量地址
```

#### 3.4 深浅拷贝原理

```python
import copy

original = [[1, 2], [3, 4]]

# 浅拷贝：外层新地址，内层共享
shallow = copy.copy(original)
# shallow的新地址，但[1,2]和[3,4]共享

# 深拷贝：完全独立
deep = copy.deepcopy(original)
# 所有对象都是新地址
```

---

## 四、API接口说明

### 认证接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/auth/register` | POST | 用户注册 |
| `/auth/login` | POST | 用户登录 |
| `/auth/profile` | GET | 获取用户信息 |

### 解析接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/parse/python` | POST | 解析Python代码 |
| `/parse/c` | POST | 解析C代码 |
| `/parse/copy-comparison` | POST | 深浅拷贝对比 |

### 文件接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/files/upload` | POST | 上传文件 |
| `/files` | GET | 获取文件列表 |
| `/files/{id}` | DELETE | 删除文件 |

---

## 五、启动方式

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python start.py
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

---

## 六、学习建议

1. **初学者路径**：
   - 先看 `config.py` 理解配置
   - 再看 `models.py` 理解数据模型
   - 然后看 `auth.py` 理解认证
   - 最后看解析器理解核心功能

2. **进阶学习**：
   - 研究AST解析原理
   - 学习JWT认证机制
   - 理解前后端分离架构

3. **实践建议**：
   - 尝试添加新的解析功能
   - 扩展可视化展示方式
   - 添加更多语言支持