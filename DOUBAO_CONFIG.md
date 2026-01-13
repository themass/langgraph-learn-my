# 豆包 AI 配置说明

## 配置步骤

在项目根目录创建或编辑 `.env` 文件，添加以下配置：

```bash
# 豆包 AI (DoubaoAI) 配置
DOUBAO_API_KEY=e8995123-8a55-4529-ae57-cd3f5fbd5eaf
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3/
DOUBAO_MODEL=ep-20240527113904-mrr8p
DOUBAO_TEMPERATURE=0.2
DOUBAO_TOP_P=0.9
```

## 快速配置命令

```bash
# 在项目根目录执行
cat >> .env << 'EOF'

# 豆包 AI 配置
DOUBAO_API_KEY=e8995123-8a55-4529-ae57-cd3f5fbd5eaf
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3/
DOUBAO_MODEL=ep-20240527113904-mrr8p
DOUBAO_TEMPERATURE=0.2
DOUBAO_TOP_P=0.9
EOF
```

## 配置说明

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `DOUBAO_API_KEY` | 豆包 AI 的 API Key（必填） | - |
| `DOUBAO_BASE_URL` | API 端点地址 | `https://ark.cn-beijing.volces.com/api/v3/` |
| `DOUBAO_MODEL` | 模型端点 ID | `ep-20240527113904-mrr8p` |
| `DOUBAO_TEMPERATURE` | 温度参数 (0-1) | `0.2` |
| `DOUBAO_TOP_P` | Top P 参数 (0-1) | `0.9` |

## 验证配置

配置完成后，运行任意项目验证：

```bash
# 测试 agent_proj
cd agent_proj
python main_local_db.py

# 测试 agent_test
cd agent_test
python 01_cot_chain_of_thought.py
```

如果配置正确，程序会正常运行并调用豆包 AI 的 API。
