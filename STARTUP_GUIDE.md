# 代码可视化分析器 - 启动指南

## 🚀 项目状态

✅ **后端服务**: 运行中 (http://localhost:9999)  
✅ **前端服务**: 运行中 (http://localhost:5173)  

---

## 一、快速启动

### 方式一：使用已有运行服务

当前服务已启动，直接访问：

| 服务 | 地址 |
|------|------|
| 前端应用 | http://localhost:5173 |
| 后端API | http://localhost:9999 |
| API文档 | http://localhost:9999/docs |

---

### 方式二：手动启动（每次重启）

#### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
python start.py
```

#### 2. 启动前端（新开终端）

```bash
cd frontend
npm install
npm run dev
```

---

## 二、环境要求

### 基础环境

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| Python | >= 3.8 | 后端语言 |
| Node.js | >= 18 | 前端构建 |
| pip | 最新版 | Python包管理 |
| npm | 最新版 | Node包管理 |

### 关键端口

| 端口 | 用途 | 是否可改 |
|------|------|----------|
| 9999 | 后端API | 可在启动脚本中修改 |
| 5173 | 前端开发服务器 | Vite默认端口 |

---

## 三、服务说明

### 后端服务

**启动日志示例：**
```
Starting Code Analysis Visualizer Backend...
INFO:     Uvicorn running on http://0.0.0.0:9999
INFO:     Database initialized successfully
```

**功能模块：**
- `/auth/` - 用户注册登录
- `/parse/` - 代码解析（Python/C）
- `/files/` - 文件上传管理
- `/records/` - 分析历史记录
- `/visualize/` - 可视化数据生成

**API文档：**  
访问 http://localhost:9999/docs 查看交互式API文档

### 前端服务

**启动日志示例：**
```
VITE v5.4.21  ready in 923 ms
Local:   http://localhost:5173/
```

**页面功能：**
- **首页** - 项目介绍和入口
- **Python分析** - Python代码可视化
- **C语言分析** - C/C++代码可视化
- **文件管理** - 上传和管理代码文件
- **历史记录** - 查看分析历史

---

## 四、使用步骤

### 1. 注册登录

1. 打开 http://localhost:5173
2. 点击右上角"注册"按钮
3. 创建账号后登录

### 2. 分析Python代码

1. 进入"Python分析"页面
2. 在编辑器中输入代码：
   ```python
   a = 10
   b = 20
   c = a + b
   ```
3. 点击"解析"按钮
4. 使用播放/暂停按钮查看执行过程

### 3. 分析C代码

1. 进入"C语言分析"页面
2. 输入C代码：
   ```c
   int main() {
       int x = 100;
       int y = 200;
       int z = x + y;
   }
   ```
3. 点击"解析"按钮查看内存布局

### 4. 上传文件分析

1. 进入"文件管理"页面
2. 点击"上传文件"
3. 选择 `.py` 或 `.c` 文件
4. 点击分析按钮

---

## 五、目录结构

```
project/
├── backend/                    # 后端服务
│   ├── start.py               # 启动脚本
│   ├── requirements.txt        # Python依赖
│   └── app/                   # 应用代码
│       ├── main.py            # 入口文件
│       ├── config.py          # 配置文件
│       ├── api/               # API路由
│       ├── core/              # 核心解析器
│       ├── db/                # 数据库模型
│       └── utils/             # 工具模块
│
├── frontend/                   # 前端应用
│   ├── package.json           # Node依赖
│   ├── vite.config.js         # Vite配置
│   └── src/                   # 源代码
│       ├── main.js            # Vue入口
│       ├── components/        # Vue组件
│       ├── views/             # 页面视图
│       ├── router/            # 路由配置
│       └── api/               # API调用
```

---

## 六、常见问题排查

### 问题1：端口被占用

**现象：**
```
Error: listen EADDRINUSE: address already in use :::9999
```

**解决：**
```bash
# Windows查找占用端口的进程
netstat -ano | findstr :9999

# 结束进程（将PID替换为实际进程号）
taskkill /F /PID <PID>
```

### 问题2：依赖安装失败

**现象：**
```
ERROR: Could not install packages due to an OSError
```

**解决：**
```bash
# 更新pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：前端无法连接后端

**现象：**
```
Failed to fetch: http://127.0.0.1:9999/api/xxx
```

**检查项：**
1. 确认后端服务已启动
2. 检查端口是否正确（默认9999）
3. 检查防火墙是否阻止连接

### 问题4：数据库初始化失败

**现象：**
```
Failed to initialize database: xxx
```

**解决：**
```bash
# 确保data目录存在且可写
mkdir -p backend/data
```

---

## 七、技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | ^0.100 | Web框架 |
| SQLAlchemy | ^2.0 | ORM数据库 |
| python-jose | ^3.3 | JWT认证 |
| passlib | ^1.7 | 密码加密 |
| uvicorn | ^0.23 | ASGI服务器 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3 | 前端框架 |
| Vite | 5 | 构建工具 |
| Element Plus | ^2.3 | UI组件 |
| Axios | ^1.5 | HTTP客户端 |
| Vue Router | ^4 | 路由管理 |

---

## 八、停止服务

### 停止后端
按 `Ctrl+C` 停止后端终端

### 停止前端  
按 `Ctrl+C` 停止前端终端

---

## 九、开发模式说明

### 热重载

后端和前端都支持热重载：
- **后端**: 修改代码自动重启
- **前端**: 修改代码自动刷新页面

### 日志查看

后端日志会输出到：
- 控制台
- `backend/app/logs/app.log` 文件

---

## 📞 联系方式

如有问题，请查看项目文档：
- [项目结构文档](PROJECT_STRUCTURE.md)