# Anthropic Skills 示例

这是一个简单的 Anthropic Skill 实现示例，演示如何创建一个返回字符串的 skill。

## 📋 功能说明

这是一个符合 Anthropic Skills 官方规范的 skill，功能是返回一个字符串。

## 📁 文件结构

```
learn/skills/
├── return_string/              # return-string-skill 目录（每个 skill 一个目录）
│   ├── SKILL.md                # return-string-skill 定义文件（必需）
│   └── script/                 # 脚本目录（官方规范）
│       ├── return_string.py    # return-string-skill 实现脚本
│       └── test_skill.py       # return-string-skill 测试脚本
├── append_suffix/              # append-suffix-skill 目录（每个 skill 一个目录）
│   ├── SKILL.md                # append-suffix-skill 定义文件（必需）
│   └── script/                 # 脚本目录（官方规范）
│       ├── append_suffix.py    # append-suffix-skill 实现脚本
│       └── test_append_suffix.py # append-suffix-skill 测试脚本
└── README.md                   # 文档说明
```

**重要说明：**
- ✅ **每个 skill 必须有一个独立的目录**
- ✅ **每个 skill 目录中必须有一个 `SKILL.md` 文件**
- ✅ `SKILL.md` 文件必须包含 front matter 元数据（name, description）
- ✅ **脚本文件应放在 `script/` 目录中**（官方规范）
- ✅ 资源文件可以放在 `resources/` 目录中（可选）

## 🚀 快速开始

### 1. Skill 文件说明

**SKILL.md** - Skill 定义文件（必需）
- 包含 skill 的元数据（name, description）
- 描述 skill 的功能和使用方法
- 提供使用示例

**return_string.py** - Skill 实现脚本（可选）
- 包含实际的实现逻辑
- 可以独立运行或作为模块导入

### 2. 测试 Skills

**测试 return-string-skill:**

```bash
# 直接运行 Python 脚本
python return_string/script/return_string.py
# 输出: Hello from Simple Skill!

# 传入自定义消息
python return_string/script/return_string.py "自定义消息"
# 输出: 自定义消息
```

**测试 append-suffix-skill:**

```bash
# 使用默认后缀
python append_suffix/script/append_suffix.py "hello"
# 输出: hello_suffix

# 使用自定义后缀
python append_suffix/script/append_suffix.py "hello" "_world"
# 输出: hello_world
```

## 📖 Anthropic Skills 规范

根据 Anthropic Skills 官方规范，skill 的实现需要遵循以下要求：

### 1. 创建 SKILL.md 文件

SKILL.md 文件必须包含：

```markdown
---
name: skill-name
description: Skill 的简短描述
---

# Skill 名称

Skill 的详细说明...
```

### 2. 元数据字段

- `name`: Skill 的唯一标识符（必需）
- `description`: Skill 的功能描述（必需）

### 3. 可选文件

- Python 脚本：实现具体的功能逻辑
- 资源文件：Skill 需要的其他文件
- 配置文件：Skill 的配置信息

### 4. 目录结构

**标准结构（每个 skill 一个独立目录）：**

```
skills/
├── skill-name/          # skill 目录（必需）
│   ├── SKILL.md        # Skill 定义文件（必需）
│   ├── script/         # 脚本目录（官方规范）
│   │   ├── script.py   # 实现脚本
│   │   └── tool.py     # 工具脚本
│   └── resources/      # 资源文件目录（可选）
│       └── data.txt    # 资源文件
└── README.md           # 文档说明
```

**Anthropic Skills 规范要求：**
- ✅ **每个 skill 必须有一个独立的目录**
- ✅ **每个 skill 目录中必须有一个 `SKILL.md` 文件**
- ✅ `SKILL.md` 文件名必须包含 "SKILL"（不区分大小写）
- ✅ **脚本文件应放在 `script/` 目录中**（官方规范）
- ✅ 资源文件可以放在 `resources/` 目录中（可选）
- ✅ 推荐使用小写字母和连字符命名目录（如 `skill-name`）

## 🔧 在 Cursor IDE 中使用

### 方式1：直接使用

在 Cursor IDE 中，可以直接引用 skill：

```
使用 return-string-skill
```

### 方式2：通过 API 使用

如果通过 Anthropic API 使用，需要将 skill 目录上传并注册。

## 📝 Skill 特点

- ✅ 符合 Anthropic Skills 官方规范
- ✅ 包含必需的 SKILL.md 文件
- ✅ 清晰的元数据定义
- ✅ 详细的文档说明
- ✅ 可选的实现脚本
- ✅ 简单易用

## 🎯 使用示例

### return-string-skill 示例

**示例 1：使用默认消息**

```
使用 return-string-skill
```

**返回：** `"Hello from Simple Skill!"`

**示例 2：使用自定义消息**

```
使用 return-string-skill，消息为 "这是我的自定义消息"
```

**返回：** `"这是我的自定义消息"`

### append-suffix-skill 示例

**示例 1：使用默认后缀**

```
使用 append-suffix-skill，text 为 "hello"
```

**返回：** `"hello_suffix"`

**示例 2：使用自定义后缀**

```
使用 append-suffix-skill，text 为 "hello"，suffix 为 "_world"
```

**返回：** `"hello_world"`

## 📚 参考资源

- [Anthropic Skills 官方文档](https://docs.anthropic.com/claude/docs/skills)
- [Anthropic API 文档](https://docs.anthropic.com/claude/reference)
