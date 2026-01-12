---
name: return-string-skill
description: 一个简单的技能，返回一个字符串
---

# Return String Skill

这是一个简单的 Anthropic Skill，功能是返回一个字符串。

## 功能说明

当激活此技能时，Claude 将返回一个字符串。如果提供了自定义消息，将返回该消息；否则返回默认消息。

## 使用方法

激活此技能后，Claude 会执行以下操作：

1. 如果用户提供了消息参数，返回该消息
2. 如果没有提供参数，返回默认消息："Hello from Simple Skill!"

## 示例

**示例 1：使用默认消息**
```
使用 return-string-skill
```
返回：`"Hello from Simple Skill!"`

**示例 2：使用自定义消息**
```
使用 return-string-skill，消息为 "这是我的自定义消息"
```
返回：`"这是我的自定义消息"`

## 实现

技能的核心逻辑在 `script/return_string.py` 文件中实现。
