# VSCode Mermaid 预览插件安装指南

## 方法 1：通过 VSCode 界面安装（推荐）

1. **打开 VSCode**

2. **打开扩展市场**:
   - 点击左侧活动栏的扩展图标 (或按 `Cmd+Shift+X`)

3. **搜索插件**:
   - 在搜索框输入: `Markdown Preview Mermaid Support`

4. **安装插件**:
   - 找到插件 **"Markdown Preview Mermaid Support"** (作者: Matt Bierner)
   - 点击 `Install` 按钮

5. **启用预览**:
   - 打开 `design.md` 文件
   - 按 `Cmd+Shift+V` 打开预览窗口
   - 现在可以看到渲染后的 Mermaid 图形

---

## 方法 2：通过命令行安装

```bash
code --install-extension bierner.markdown-mermaid
```

---

## 验证安装

打开预览窗口后，你应该能看到：
- **架构图**: 显示分层的系统组件
- **工作流图**: 显示 Router、Planner、Executor、Analyst 的交互流程

如果看到的是代码块而非图形，请重启 VSCode。

---

## 替代方案

如果不想安装插件，可以在线查看：
1. 访问 https://mermaid.live
2. 复制 Mermaid 代码块内容粘贴到编辑器
3. 即可实时预览

---

## 其他支持 Markdown 图表的方式

除了 Mermaid，还有以下选择：

| 方案 | 格式 | 优点 | 缺点 |
|:---|:---|:---|:---|
| **Mermaid** | 文本 (Markdown) | 版本可控、易修改 | 需插件支持 |
| **PlantUML** | 文本 | 功能强大、UML 标准 | 语法复杂 |
| **Draw.io** | 图形编辑 | 所见即所得 | 非文本格式 |
| **Graphviz** | DOT 语言 | 自动布局 | 学习曲线陡 |

对于本项目，**Mermaid** 是最佳选择，因为它集成度高、语法简洁。
