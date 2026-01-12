import streamlit as st  # 导入 Streamlit 并简写为 st

# 1. 页面标题与文本
st.title("我的第一个 Streamlit 应用")  # 一级标题
st.subheader("副标题：基础演示")        # 二级标题
st.text("这是一个简单的文本内容")       # 普通文本
st.markdown("**Markdown 格式文本**：支持加粗、列表等")  # Markdown 语法

# 2. 交互组件：按钮
if st.button("点击我"):
    st.success("按钮被点击啦！")  # 成功提示框

# 3. 数据展示：Pandas DataFrame
import pandas as pd
data = pd.DataFrame({
    "姓名": ["张三", "李四", "王五"],
    "年龄": [25, 30, 35],
    "城市": ["北京", "上海", "广州"]
})
st.dataframe(data)  # 交互式表格（支持排序、筛选）

# 4. 数据可视化：Matplotlib 图表
import matplotlib.pyplot as plt
plt.figure(figsize=(8, 4))
plt.bar(data["姓名"], data["年龄"], color="skyblue")
plt.title("年龄分布柱状图")
st.pyplot(plt)  # 渲染 Matplotlib 图表