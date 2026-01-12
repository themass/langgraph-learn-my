# ProAgent: Production-Grade Industry Research Agent

ProAgent 是一个基于 **LangGraph** 构建的生产级行业研究智能体。采用 **Plan-and-Execute**、**ReAct** 和 **Chain-of-Thought (CoT)** 三范式融合架构，并集成了完善的质量门控机制。

![系统架构](docs/proagent_full_workflow_1768138558668.png)

## ✨ 核心特性

- **三范式融合**: 
    - **Planner**: 全局规划，分解复杂任务
    - **Executor (ReAct)**: 动态执行，工具调用与反馈循环
    - **Analyst (CoT)**: 深度分析，多步推理生成报告
- **生产级质量门控**:
    - **Input Validation**: 输入过滤与安全检查
    - **Progress Check**: 执行过程中的动态评估与重规划
    - **Reflection**: 推理自动反思与修正
    - **Uncertainty Handling**: 结果置信度评估
    - **Result Validation**: 最终输出的格式与质量验证
- **容错与恢复**: 完整的错误捕获与重试机制

## 🚀 快速启动

### 1. 环境准备

确保 Python 版本 >= 3.10。

```bash
# 克隆项目 (假设已下载)
cd /path/to/langgraph-learn/agent_proj

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key 和数据库

项目默认使用 **Kimi (Moonshot AI)** 模型。

1. 创建 `.env` 文件（参考下方模板）

2. **LLM API 配置**：
   ```ini
   # LLM API (支持 Kimi / OpenAI)
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   OPENAI_BASE_URL=https://api.moonshot.cn/v1  # 如果使用 Kimi
   ```

3. **搜索工具配置**：
   ```ini
   # Search Tool
   TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxx
   ```

4. **数据库配置（可选，仅 main_db.py 需要）**：

   **推荐方式：分开配置（自动处理密码特殊字符）**
   ```ini
   DB_USER=your_username
   DB_PASSWORD=your_p@ssw0rd!    # 可以包含 @, :, / 等特殊字符
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=proagent
   DB_DRIVER=mysql+aiomysql      # 可选，默认为 mysql+aiomysql
   ```

   **传统方式：完整 URL（密码有特殊字符时会失败）**
   ```ini
   DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/proagent
   ```

   **注意**：
   - ✅ 推荐使用分开配置方式，程序会自动转义密码中的特殊字符
   - MySQL 版本必须 >= 8.0（需要 CTE 支持）
   - 确保数据库已创建：
     ```sql
     CREATE DATABASE proagent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     ```

### 3. 运行项目

ProAgent 支持两种运行模式：

#### 模式 A: 快速体验 (内存模式)
无需数据库，直接运行，适合开发与测试。
```bash
python agent_proj/main.py
```

#### 模式 B: 生产级运行 (带数据库持久化)

**选项 1: 本地 SQLite (推荐，无需配置)**
适合需要持久化但不想配置远程数据库的场景。
```bash
python agent_proj/main_local_db.py
```

**选项 2: 远程 MySQL (需 MySQL 8.0+)**
连接 MySQL 数据库，支持断点续传和状态查询。
注意: 仅支持 MySQL 8.0 或以上版本 (需支持 CTE)。
```bash
# 1. 确保 .env 中已配置 DATABASE_URL (MySQL 8.0+)
# 2. 运行数据库启动脚本
python agent_proj/main_db.py
```

## 🧪 验证方法

运行 `main_db.py` 后：
1. **连接数据库**: 控制台显示 `✅ DB Connected`。
2. **执行流程**: 看到各节点 (Planner -> Executor -> Analyst) 的日志输出。
3. **验证持久化**: 程序结束时会再次从数据库读取状态，显示 `✅ Retrieved State from DB`，证明数据已保存。

**注意**: 本地 Redis 服务主要用于未来扩展 (如缓存)，当前流程主要依赖 MySQL 进行状态管理。如果您使用 Docker，确保 Redis 容器正在运行 (`docker ps` 查看)。

**示例输出指标**:
```text
【质量指标】
- 整体置信度: 0.85
- 推理置信度: 0.90
- 验证评分: 8.5/10
- 重试次数: 0/2
```

## 📂 项目结构

```text
agent_proj/
├── main.py                 # 测试入口脚本
├── requirements.txt        # 项目依赖
├── .env                    # 配置文件 (需创建)
├── graph/                  # 核心图逻辑
│   ├── state.py            # 状态定义 (AgentState)
│   ├── workflow.py         # 图构建与路由逻辑
│   └── nodes/              # 节点实现
│       ├── planner.py      # L1 规划
│       ├── executor.py     # L2 执行 (ReAct)
│       ├── analyst.py      # L3 分析 (CoT)
│       ├── ...             # 验证与辅助节点
├── tools.py                # 工具定义 (Search, Scrape, Finance)
└── utils.py                # 通用工具 (LLM Factory)
```

## 📚 文档资源

- [架构设计文档](design.md): 详细的系统架构与节点设计
- [范式对比分析](docs/agent_systems_comparison.md): ProAgent 与其他框架的对比