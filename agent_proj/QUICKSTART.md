# 🚀 快速开始 - 执行步骤

## 📋 完整操作流程

---

## 第一步：配置环境文件

### 1.1 创建 .env 文件

```bash
cd /Users/liguoqing/work/langgraph-learn/agent_proj

# 创建 .env 文件
cat > .env << 'EOF'
# LLM API 配置
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.moonshot.cn/v1

# 数据库配置（推荐方式 - 支持密码特殊字符）
DB_USER=root
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=3306
DB_NAME=proagent

# 搜索工具（可选）
TAVILY_API_KEY=tvly-your-key-here
EOF
```

### 1.2 编辑配置文件

```bash
# 使用 nano 编辑
nano .env

# 或使用 vim
vim .env
```

**需要修改的配置**：
- `OPENAI_API_KEY`: 您的 API Key（如果已经硬编码可以不改）
- `DB_USER`: 数据库用户名（例如：`root`）
- `DB_PASSWORD`: 数据库密码（**可以包含 @ 等特殊字符**）
- `DB_HOST`: 数据库主机（例如：`8.217.122.83`）
- `DB_PORT`: 数据库端口（例如：`6666`）
- `DB_NAME`: 数据库名称（例如：`test` 或 `proagent`）

**示例配置**：
```ini
DB_USER=root
DB_PASSWORD=Themass@5296
DB_HOST=8.217.122.83
DB_PORT=6666
DB_NAME=test
```

---

## 第二步：创建数据库（如果还没有）

```bash
# 连接到 MySQL
mysql -h 8.217.122.83 -P 6666 -u root -p

# 在 MySQL 中执行
CREATE DATABASE IF NOT EXISTS proagent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 或者如果使用 test 数据库，跳过此步骤
```

---

## 第三步：测试数据库连接

```bash
cd /Users/liguoqing/work/langgraph-learn/agent_proj

# 方式 1: 使用测试工具（推荐）
python test_db_config.py

# 方式 2: 使用调试工具（更详细）
python debug_db.py

# 方式 3: 检查 MySQL 版本
python check_mysql_version.py
```

**预期输出**：
```
✅ 配置加载成功
✅ 数据库连接成功
✅ 表结构就绪
```

如果看到 ❌ 错误，根据提示修复配置。

---

## 第四步：运行 ProAgent

### 选项 A：使用内存模式（快速测试，不需要数据库）

```bash
cd /Users/liguoqing/work/langgraph-learn
python agent_proj/main.py
```

### 选项 B：使用 SQLite 本地数据库

```bash
python agent_proj/main_local_db.py
```

### 选项 C：使用 MySQL 数据库（生产级）⭐ **推荐**

```bash
python agent_proj/main_db.py
```

---

## 第五步：（可选）启动 API 服务器

如果需要通过 API 访问：

```bash
cd /Users/liguoqing/work/langgraph-learn/agent_proj
python server/app.py
```

API 将在 `http://localhost:8000` 启动

---

## 📊 快速命令参考

```bash
# 进入项目目录
cd /Users/liguoqing/work/langgraph-learn/agent_proj

# 1. 测试数据库
python test_db_config.py

# 2. 运行主程序（MySQL 模式）
python main_db.py

# 3. 查看帮助文档
cat docs/DATABASE_CONFIG.md
cat docs/SUPPLEMENTARY_FIX.md
```

---

## 🔧 常见问题

### Q1: 没有 .env 文件怎么办？
**A**: 按照第一步创建即可，或者复制模板：
```bash
cp .env.example .env  # 如果有模板的话
# 或直接创建新的（见上方命令）
```

### Q2: 数据库连接失败？
**A**: 依次检查：
1. 数据库服务是否运行
2. 用户名密码是否正确
3. 主机和端口是否正确
4. 防火墙/安全组是否允许访问
5. 运行 `python debug_db.py` 查看详细错误

### Q3: 密码包含特殊字符会有问题吗？
**A**: 不会！现在支持任何特殊字符（`@`, `:`, `/`, `#`, `!` 等）

### Q4: 必须使用 MySQL 吗？
**A**: 不是，您可以选择：
- 内存模式：`python main.py`（无需数据库）
- SQLite 模式：`python main_local_db.py`（无需配置）
- MySQL 模式：`python main_db.py`（生产级，需配置）

---

## ✅ 成功标志

### 测试工具成功输出
```
✅ 配置加载成功
✅ 数据库连接成功
✅ 表结构就绪
✅ 所有测试通过！
```

### 主程序成功输出
```
================================================================================
ProAgent with MySQL Persistence
================================================================================

[1] Validating Database Configuration...
✅ Configuration Loaded

[2] Connecting to Database...
📊 数据库连接: mysql+aiomysql://***:***@8.217.122.83:6666/test
✅ DB Connected & Tables checked

[3] Compiling Graph with Persistence...
✅ Graph Compiled
```

---

## 📚 相关文档

- **配置指南**: `docs/DATABASE_CONFIG.md`
- **修复说明**: `docs/SUPPLEMENTARY_FIX.md`
- **项目说明**: `ReadMe.md`

---

## 🎯 最简单的测试流程

```bash
# 1. 进入目录
cd /Users/liguoqing/work/langgraph-learn/agent_proj

# 2. 创建并编辑 .env（填入您的数据库配置）
nano .env

# 3. 测试连接
python test_db_config.py

# 4. 运行程序
python main_db.py
```

就这么简单！🚀
