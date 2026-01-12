---
name: append-suffix-skill
description: 给参数增加一个字符串后缀并返回
---

# Append Suffix Skill

这是一个简单的 Anthropic Skill，功能是给输入的字符串参数添加一个后缀并返回。

## 功能说明

当激活此技能时，Claude 会将输入的字符串参数与指定的后缀拼接，然后返回结果。

## 使用方法

激活此技能后，Claude 会执行以下操作：

1. 接收输入的字符串参数
2. 接收后缀参数（可选，默认为 "_suffix"）
3. 将字符串和后缀拼接
4. 返回拼接后的结果

## 参数说明

- `text`: 要添加后缀的字符串（必需）
- `suffix`: 要添加的后缀字符串（可选，默认为 "_suffix"）

## 示例

**示例 1：使用默认后缀**
```
使用 append-suffix-skill，text 为 "hello"
```
返回：`"hello_suffix"`

**示例 2：使用自定义后缀**
```
使用 append-suffix-skill，text 为 "hello"，suffix 为 "_world"
```
返回：`"hello_world"`

**示例 3：使用空后缀**
```
使用 append-suffix-skill，text 为 "hello"，suffix 为 ""
```
返回：`"hello"`

## 实现

技能的核心逻辑在 `script/append_suffix.py` 文件中实现。
