# 🔧 ProAgent 环境配置指南

## 📋 概述

ProAgent 使用 `.env` 文件集中管理所有环境配置，包括 LLM API Key、数据库配置等。

## 🚀 快速开始

### 1. 复制配置模板

```bash
cd /Users/liguoqing/work/langgraph-learn
cp .env.example .env
```

### 2. 编辑 `.env` 文件

使用任何文本编辑器打开 `.env` 文件，填入您的实际配置：

```bash
nano .env
# 或
vim .env
# 或
code .env  # 使用 VS Code
```

### 3. 必填配置

**最少需要配置以下项才能运行：**

```bash
# Moonshot AI API Key (必填)
MOONSHOT_API_KEY=your_actual_api_key_here
```

获取 API Key: https://platform.moonshot.cn/console/api-keys

## 📝 配置详解

### 1. LLM 配置

#### Moonshot AI (Kimi) - 推荐

```bash
# Moonshot AI API Key (必填)
MOONSHOT_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# Moonshot AI Base URL (可选，已有默认值)
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1

# 默认 LLM 模型 (可选)
# 可选值: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
DEFAULT_LLM_MODEL=moonshot-v1-32k

# LLM 默认温度 (可选，范围 0-1)
DEFAULT_LLM_TEMPERATURE=0.3
```

**模型选择建议：**
- `moonshot-v1-8k`: 适合简单任务，速度快
- `moonshot-v1-32k`: 适合复杂任务，推荐使用
- `moonshot-v1-128k`: 适合超长上下文任务

#### OpenAI (可选)

如果您想使用 OpenAI 而不是 Moonshot：

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# OpenAI Base URL
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 2. 工具配置

#### Tavily 搜索工具 (可选)

Tavily 用于市场数据搜索。如果不配置，`search_market_data` 工具将不可用。

```bash
# Tavily API Key
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxx
```

获取 API Key: https://tavily.com/

### 3. 数据库配置 (可选)

如果需要使用 MySQL 持久化 (主要用于 `main_db.py`)：

#### 方式 1: 使用完整的 DATABASE_URL (推荐)

```bash
DATABASE_URL=mysql+aiomysql://username:password@host:port/database
```

**示例：**
```bash
DATABASE_URL=mysql+aiomysql://agent_user:mypassword@localhost:3306/proagent
```

#### 方式 2: 使用独立配置项

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=agent_user
DB_PASSWORD=agent_password
DB_NAME=proagent
DB_DRIVER=mysql+aiomysql
```

**注意：** 
- 如果同时配置了 `DATABASE_URL` 和独立配置项，将优先使用 `DATABASE_URL`
- 密码中的特殊字符需要 URL 编码（如果使用 `DATABASE_URL`）

### 4. 其他配置

```bash
# 项目环境
ENVIRONMENT=development  # 或 production

# 是否启用调试模式
DEBUG=true
```

## 📂 配置文件说明

### `.env` - 实际配置文件

- 包含敏感信息（API Key、密码等）
- **已被 `.gitignore` 忽略，不会提交到 Git**
- 每个开发者/部署环境需要单独配置

### `.env.example` - 配置模板

- 不包含敏感信息，只有占位符
- **会被提交到 Git**
- 用于团队成员快速创建自己的 `.env`

## 🔍 验证配置

### 方法 1: 运行测试脚本

```bash
cd /Users/liguoqing/work/langgraph-learn/agent_proj
python -c "from utils import get_llm; llm = get_llm(); print('✅ LLM 配置正确')"
```

### 方法 2: 运行主程序

```bash
# 使用 SQLite 持久化（不需要数据库配置）
python main_local_db.py

# 使用 MySQL 持久化（需要数据库配置）
python main_db.py
```

如果配置正确，程序会正常启动；如果配置错误，会看到清晰的错误提示。

## ❌ 常见错误

### 错误 1: 未找到 API Key

```
ValueError: 未找到 LLM API Key！
请在项目根目录的 .env 文件中配置:
  MOONSHOT_API_KEY=your_api_key_here
```

**解决方案：**
1. 确认 `.env` 文件存在于项目根目录
2. 确认 `MOONSHOT_API_KEY` 已正确配置
3. 确认没有多余的空格或引号

### 错误 2: Tavily API Key 未配置

```
Error: TAVILY_API_KEY not found!
请在项目根目录的 .env 文件中配置:
  TAVILY_API_KEY=your_api_key_here
```

**解决方案：**
1. 如果不需要搜索功能，可以忽略此错误
2. 如果需要搜索功能，到 https://tavily.com/ 获取 API Key

### 错误 3: 数据库连接失败

```
请配置数据库连接！
方式 1: DATABASE_URL=mysql+aiomysql://user:pass@host:port/dbname
...
```

**解决方案：**
1. 使用 `main_local_db.py` 代替 `main_db.py`（使用 SQLite，无需数据库配置）
2. 或配置 MySQL 数据库连接信息

## 🔒 安全建议

### 1. 保护 `.env` 文件

- ❌ **绝对不要**将 `.env` 文件提交到 Git
- ✅ 确认 `.gitignore` 包含 `.env`
- ✅ 定期检查是否误提交了 `.env`

```bash
# 检查 .env 是否被 Git 忽略
git status --ignored | grep .env
```

### 2. API Key 权限控制

- 为不同环境使用不同的 API Key
- 定期轮换 API Key
- 限制 API Key 的权限和配额

### 3. 生产环境配置

生产环境建议使用环境变量或密钥管理服务（如 AWS Secrets Manager）：

```bash
# 示例：在生产环境设置环境变量
export MOONSHOT_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
export DATABASE_URL="mysql+aiomysql://user:pass@host:port/db"
```

## 📚 代码使用示例

### 获取 LLM 实例

```python
from agent_proj.utils import get_llm

# 使用默认配置（从 .env 读取）
llm = get_llm()

# 自定义配置
llm = get_llm(temperature=0.7, model_name="moonshot-v1-32k")
```

### 使用工具

```python
from agent_proj.tools import search_market_data

# 调用搜索工具（需要配置 TAVILY_API_KEY）
result = search_market_data.invoke({"query": "2024年AI市场规模"})
print(result)
```

## 🆘 获取帮助

如果遇到配置问题：

1. 查看错误提示信息（已包含详细的解决方案）
2. 检查 `.env` 文件格式是否正确
3. 验证 API Key 是否有效
4. 查看本文档的"常见错误"部分

## 📝 配置示例

### 最小配置（仅 LLM）

```bash
# .env
MOONSHOT_API_KEY=sk-3uBciWtEHczi2zM9IdC0gz5pfyGeCbW4mz8dJGG8bUUDZrf3
```

### 完整配置（所有功能）

```bash
# .env
# LLM 配置
MOONSHOT_API_KEY=sk-3uBciWtEHczi2zM9IdC0gz5pfyGeCbW4mz8dJGG8bUUDZrf3
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
DEFAULT_LLM_MODEL=moonshot-v1-32k
DEFAULT_LLM_TEMPERATURE=0.3

# 工具配置
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxx

# 数据库配置
DATABASE_URL=mysql+aiomysql://agent_user:password@localhost:3306/proagent

# 其他配置
ENVIRONMENT=development
DEBUG=true
```

---

**最后更新**: 2026-01-13  
**维护者**: ProAgent Team  
**版本**: 1.0.0
