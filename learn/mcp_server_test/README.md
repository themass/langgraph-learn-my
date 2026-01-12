# MCP Server Demo

这是一个简单的 MCP (Model Context Protocol) 服务器示例，演示如何发布 MCP 服务并通过客户端调用，以及在 Cursor IDE 中集成 MCP 服务。

## 📁 文件说明

- `server.py` - MCP 服务器（stdio 模式）
- `server_http.py` - MCP HTTP/SSE 服务器（HTTP 发布模式）
- `client.py` - 测试客户端（stdio 模式）
- `client_http.py` - HTTP 客户端（调用发布的 HTTP 服务）
- `requirements.txt` - Python 依赖包

## 🎯 两种使用方式对比

### 方式一：stdio 模式（进程间通信）

**适用场景：**
- ✅ 本地开发环境
- ✅ Cursor IDE 集成（推荐）
- ✅ 单机使用
- ✅ 简单快速集成

**特点：**
- 🔹 通过标准输入输出（stdin/stdout）通信
- 🔹 无需网络，性能更好
- 🔹 配置简单，直接运行 Python 脚本
- 🔹 适合本地开发和测试

**使用文件：**
- 服务器：`server.py`
- 客户端：`client.py`

### 方式二：HTTP/SSE 模式（网络服务）

**适用场景：**
- ✅ 需要远程访问
- ✅ 多客户端共享服务
- ✅ 跨机器调用
- ✅ 生产环境部署
- ✅ 需要服务发现和负载均衡

**特点：**
- 🔹 通过 HTTP/SSE 协议通信
- 🔹 可以远程访问
- 🔹 支持多客户端同时连接
- 🔹 可以部署到云服务器
- 🔹 需要网络连接

**使用文件：**
- 服务器：`server_http.py`
- 客户端：`client_http.py`

## 🚀 快速开始

### 1. 安装依赖

```bash
cd learn/mcp_server_test
pip install -r requirements.txt
```

### 2. 测试服务器

#### 测试 stdio 模式（本地测试）

```bash
python3 client.py
```

**预期输出：**
```
Connecting to server at: /path/to/server.py
Available tools: ['test_output_name']
Calling tool 'test_output_name' with name='World'...
Tool Result: testOutputWorld
```

#### 测试 HTTP 模式（发布服务）

**步骤 1: 启动 HTTP 服务器**

```bash
python3 server_http.py
```

服务器将在 `http://localhost:8000` 启动，SSE 端点为 `http://localhost:8000/sse`

**步骤 2: 在另一个终端运行 HTTP 客户端**

```bash
python3 client_http.py
```

**预期输出：**
```
🔗 Connecting to MCP server at: http://localhost:8000/sse
✅ Available tools: ['test_output_name']
🔧 Calling tool 'test_output_name' with name='World'...
✅ Tool Result: testOutputWorld
```

---

## 📋 方式一：stdio 模式配置（Cursor 集成）

### 适用场景

- ✅ **本地开发**：在本地机器上使用 Cursor IDE
- ✅ **单用户使用**：个人开发环境
- ✅ **快速集成**：最简单快速的集成方式
- ✅ **性能优先**：无需网络开销，响应更快

### 配置步骤

#### 步骤 1: 获取路径信息

```bash
# 获取 Python 路径
which python3
# 输出示例：/usr/local/bin/python3

# 获取服务器脚本绝对路径
cd learn/mcp_server_test
pwd
# 输出示例：/Users/yourname/work/langgraph-learn/learn/mcp_server_test
# 完整路径：/Users/yourname/work/langgraph-learn/learn/mcp_server_test/server.py
```

#### 步骤 2: 在 Cursor 中配置

1. **打开 Cursor 设置**
   - 快捷键：`Cmd + ,` (macOS) 或 `Ctrl + ,` (Windows/Linux)
   - 或点击左下角齿轮图标 → **Settings**

2. **找到 MCP 配置**
   - 在设置搜索框中输入 `MCP`
   - 或导航到 **Features** → **MCP**

3. **添加新服务器**
   - 点击 **Add New MCP Server** 或 **+** 按钮

4. **填写配置信息**
   ```
   Name: Test Server
   Type: stdio
   Command: python3
   Args: /Users/yourname/work/langgraph-learn/learn/mcp_server_test/server.py
   ```
   
   ⚠️ **重要提示：**
   - **Command** 字段：填写 `python3` 或 Python 的完整路径
   - **Args** 字段：填写 `server.py` 的**绝对路径**（不要使用相对路径！）
   - 路径中不要有空格或特殊字符

5. **保存配置**
   - 点击 **Save** 或 **Add**
   - 等待几秒钟，服务器状态应该变为**绿色**（✅）

#### 步骤 3: 验证集成

配置成功后，在 Cursor Chat 中测试：

```
请使用 test_output_name 工具，参数 name="Cursor"
```

或者更自然的对话：

```
帮我测试一下 MCP 服务器，名字用 "Hello"
```

### 配置示例

**macOS/Linux 配置示例：**
```
Name: Test Server
Type: stdio
Command: python3
Args: /Users/liguoqing/work/langgraph-learn/learn/mcp_server_test/server.py
```

**Windows 配置示例：**
```
Name: Test Server
Type: stdio
Command: python
Args: C:\Users\yourname\work\langgraph-learn\learn\mcp_server_test\server.py
```

### 优势

- ✅ **配置简单**：只需配置 Python 路径和脚本路径
- ✅ **性能优秀**：进程间通信，无网络延迟
- ✅ **安全性高**：本地运行，不暴露网络端口
- ✅ **资源占用少**：无需额外的 HTTP 服务器进程

---

## 🌐 方式二：HTTP/SSE 模式配置（发布服务）

### 适用场景

- ✅ **远程访问**：需要从其他机器访问服务
- ✅ **多客户端**：多个客户端需要共享同一个服务
- ✅ **生产部署**：部署到云服务器或容器
- ✅ **服务发现**：需要服务注册和发现机制
- ✅ **负载均衡**：需要多实例负载均衡

### 配置步骤

#### 步骤 1: 启动 HTTP 服务器

```bash
python3 server_http.py
```

服务器将：
- 监听 `http://0.0.0.0:8000`（所有网络接口）
- SSE 端点：`http://localhost:8000/sse`
- 健康检查：`http://localhost:8000/health`

**输出示例：**
```
🚀 Starting MCP HTTP/SSE Server...
📡 Server will be available at: http://localhost:8000
🔌 SSE endpoint: http://localhost:8000/sse
按 Ctrl+C 停止服务器
```

#### 步骤 2: 使用 HTTP 客户端调用

**方式 A: 使用 Python 客户端**

```bash
# 在另一个终端运行
python3 client_http.py
```

**方式 B: 在 Cursor 中配置 SSE 服务器**

1. **打开 Cursor 设置** → **Features** → **MCP**

2. **添加 SSE 服务器**
   ```
   Name: Test Server HTTP
   Type: sse
   URL: http://localhost:8000/sse
   ```

3. **保存配置**

   ⚠️ **注意**：确保 HTTP 服务器正在运行，否则连接会失败。

#### 步骤 3: 自定义配置

**修改端口**

编辑 `server_http.py`：

```python
# 默认端口 8000，可以修改为其他端口
mcp.run(transport="sse", port=9000)
```

**修改客户端连接地址**

编辑 `client_http.py`：

```python
# 修改服务器地址
server_url = "http://your-server-ip:8000/sse"
```

### 部署到生产环境

#### 使用 uvicorn 部署

```bash
uvicorn server_http:mcp --host 0.0.0.0 --port 8000
```

#### 使用 gunicorn 部署（多进程）

```bash
# 安装 gunicorn
pip install gunicorn

# 启动多进程服务
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server_http:mcp --bind 0.0.0.0:8000
```

#### 使用 systemd 管理服务（Linux）

创建服务文件 `/etc/systemd/system/mcp-server.service`：

```ini
[Unit]
Description=MCP HTTP Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/mcp_server_test
ExecStart=/usr/bin/python3 server_http.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable mcp-server
sudo systemctl start mcp-server
```

#### Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server_http.py .

EXPOSE 8000
CMD ["python3", "server_http.py"]
```

构建和运行：

```bash
docker build -t mcp-server .
docker run -p 8000:8000 mcp-server
```

### 优势

- ✅ **远程访问**：可以从任何地方访问服务
- ✅ **多客户端**：支持多个客户端同时连接
- ✅ **可扩展**：可以部署多个实例进行负载均衡
- ✅ **标准化**：使用标准 HTTP 协议，易于集成

---

## 🔧 故障排查

### stdio 模式问题

#### 问题 1: 服务器状态显示红色（❌）

**可能原因：**
- Python 路径不正确
- server.py 文件路径错误
- 缺少依赖包

**解决方法：**
```bash
# 1. 检查 Python 路径
which python3

# 2. 检查文件是否存在
ls -la /path/to/server.py

# 3. 重新安装依赖
pip install -r requirements.txt

# 4. 手动测试服务器
python3 /path/to/server.py
# 如果正常，应该会等待 stdin 输入（这是正常的）
```

#### 问题 2: 配置格式错误

如果看到错误：
```
Server "Command" must have either a command (for stdio) or url (for SSE)
```

**解决方法：**
- 确保 Type 选择的是 `stdio`
- 确保 Command 字段填写的是 `python3`（或完整路径）
- 确保 Args 字段填写的是 server.py 的**绝对路径**

### HTTP/SSE 模式问题

#### 问题 1: HTTP 客户端连接失败

**可能原因：**
- HTTP 服务器未启动
- 端口被占用
- 防火墙阻止连接
- URL 配置错误

**解决方法：**
```bash
# 1. 检查服务器是否运行
curl http://localhost:8000/health

# 2. 检查端口是否被占用
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 3. 确保服务器正在运行
python3 server_http.py

# 4. 检查防火墙设置
# macOS: 系统设置 → 防火墙
# Linux: sudo ufw allow 8000
```

#### 问题 2: SSE 连接超时

**可能原因：**
- 服务器地址不正确
- 网络连接问题
- 服务器未正确启动

**解决方法：**
- 检查服务器地址是否正确（`http://localhost:8000/sse`）
- 确保服务器正在运行
- 检查网络连接

### 通用问题

#### 问题 3: 找不到工具

**可能原因：**
- 服务器未正确启动
- 工具名称拼写错误
- 服务器版本不匹配

**解决方法：**
- 检查 Cursor 的 MCP 日志
- 确认工具名称是 `test_output_name`（注意下划线）
- 重启 Cursor IDE 或 HTTP 服务器

---

## 📝 添加新工具

要添加新工具，编辑 `server.py` 或 `server_http.py`：

```python
@mcp.tool()
def your_new_tool(param: str) -> str:
    """
    你的工具描述
    
    Args:
        param: 参数说明
    """
    return "处理结果"
```

保存后：
- **stdio 模式**: 重启 Cursor IDE
- **HTTP 模式**: 重启 HTTP 服务器

新工具会自动出现。

---

## 📚 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [Cursor 官方文档](https://docs.cursor.com/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)

## ✅ 配置检查清单

### stdio 模式（Cursor 集成）
- [ ] 已安装依赖 (`pip install -r requirements.txt`)
- [ ] 客户端测试通过 (`python3 client.py`)
- [ ] 获取了 Python 和 server.py 的绝对路径
- [ ] 在 Cursor 中添加了服务器配置
- [ ] 服务器状态显示为绿色（✅）
- [ ] 可以在 Cursor Chat 中调用工具

### HTTP/SSE 模式（发布服务）
- [ ] 已安装依赖（包括 uvicorn）
- [ ] HTTP 服务器启动成功 (`python3 server_http.py`)
- [ ] HTTP 客户端测试通过 (`python3 client_http.py`)
- [ ] 可以在 Cursor 中添加 SSE 服务器配置（可选）
- [ ] 如果需要远程访问，配置了防火墙规则

配置完成后，你就可以使用 MCP 工具了！🎉
