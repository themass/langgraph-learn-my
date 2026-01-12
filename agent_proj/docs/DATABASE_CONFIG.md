# 数据库配置指南

## 🎯 问题说明

当数据库密码包含特殊字符（如 `@`, `:`, `/`, `?`, `#`, `[`, `]` 等）时，使用传统的连接字符串会导致解析失败。

**错误示例**：
```ini
# ❌ 密码包含 @ 符号，会被误解析为 host 分隔符
DATABASE_URL=mysql+aiomysql://user:p@ssw0rd@localhost:3306/proagent
```

上述配置会被解析为：
- 用户名：`user`
- 密码：`p`
- 主机：`ssw0rd@localhost` ❌ 错误！

---

## ✅ 解决方案

### 方案 1：分开配置（推荐）

在 `.env` 文件中使用独立配置项，程序会自动处理密码的 URL 编码：

```ini
# 数据库配置（推荐）
DB_USER=myuser
DB_PASSWORD=my_p@ssw0rd!#$%^&*()    # 可以包含任何特殊字符
DB_HOST=localhost
DB_PORT=3306
DB_NAME=proagent
DB_DRIVER=mysql+aiomysql            # 可选，默认为 mysql+aiomysql
```

**优点**：
- ✅ 自动转义密码中的特殊字符
- ✅ 配置清晰易读
- ✅ 修改单个参数方便

---

### 方案 2：完整 URL（仅密码无特殊字符时）

如果密码不包含特殊字符，可以直接使用完整的连接字符串：

```ini
# 数据库配置（传统方式）
DATABASE_URL=mysql+aiomysql://myuser:simplepassword@localhost:3306/proagent
```

**限制**：
- ⚠️ 密码不能包含特殊字符
- ⚠️ 需要手动 URL 编码密码

---

## 📝 配置优先级

程序按以下优先级查找配置：

1. **DATABASE_URL**（如果存在，直接使用）
2. **独立配置项**（DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME）

**建议**：仅使用其中一种方式，避免混淆。

---

## 🔧 特殊字符 URL 编码对照表

如果您坚持使用 `DATABASE_URL`，需要手动编码密码中的特殊字符：

| 字符 | URL 编码 | 示例 |
|------|----------|------|
| `@`  | `%40`    | `p@ss` → `p%40ss` |
| `:`  | `%3A`    | `p:ss` → `p%3Ass` |
| `/`  | `%2F`    | `p/ss` → `p%2Fss` |
| `?`  | `%3F`    | `p?ss` → `p%3Fss` |
| `#`  | `%23`    | `p#ss` → `p%23ss` |
| `&`  | `%26`    | `p&ss` → `p%26ss` |
| `=`  | `%3D`    | `p=ss` → `p%3Dss` |
| `+`  | `%2B`    | `p+ss` → `p%2Bss` |
| ` `  | `%20`    | `p ss` → `p%20ss` |

**示例**：
```ini
# 原始密码: my_p@ss:w0rd!
# URL 编码后: my_p%40ss%3Aw0rd!
DATABASE_URL=mysql+aiomysql://user:my_p%40ss%3Aw0rd!@localhost:3306/proagent
```

但这样很容易出错，**强烈推荐使用方案 1**！

---

## 🧪 测试配置

完成配置后，可以运行测试脚本验证连接：

```bash
cd /Users/liguoqing/work/langgraph-learn/agent_proj
python debug_db.py
```

如果看到 `✅ DB Connected`，说明配置成功！

---

## 🚀 运行 ProAgent

配置完成后，运行数据库持久化版本：

```bash
python agent_proj/main_db.py
```

**预期输出**：
```
================================================================================
ProAgent with MySQL Persistence
================================================================================

[1] Validating Database Configuration...
✅ Configuration Loaded

[2] Connecting to Database...
📊 数据库连接: mysql+aiomysql://***:***@localhost:3306/proagent
✅ DB Connected & Tables checked

[3] Compiling Graph with Persistence...
✅ Graph Compiled
...
```

---

## ❓ 常见问题

### Q1: 为什么不直接在 DATABASE_URL 中使用密码？

**A**: 因为 URL 规范要求特殊字符必须编码，手动编码容易出错。独立配置项可以自动处理编码，更安全可靠。

### Q2: 我可以同时配置两种方式吗？

**A**: 可以，但 `DATABASE_URL` 会优先使用。建议只配置一种，避免混淆。

### Q3: 如何验证密码是否正确编码？

**A**: 使用 Python 测试：
```python
from urllib.parse import quote_plus
password = "my_p@ss:w0rd!"
encoded = quote_plus(password)
print(encoded)  # my_p%40ss%3Aw0rd%21
```

### Q4: 支持哪些数据库？

**A**: 当前仅支持 **MySQL 8.0+**（需要 CTE 支持）。未来可能支持 PostgreSQL。

---

## 📚 相关文档

- [ProAgent README](ReadMe.md)
- [架构设计文档](design.md)
- [LangGraph Checkpoint MySQL 文档](https://python.langchain.com/docs/langgraph/checkpointers/mysql)
