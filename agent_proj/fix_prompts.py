#!/usr/bin/env python3
"""
批量修复 agent_proj/graph/nodes 中所有使用 f-string + chain.invoke({}) 的文件
将 f-string 变量转换为 Prompt 模板变量
"""

import re
from pathlib import Path

def fix_progress_check():
    """修复 progress_check.py"""
    file_path = Path("agent_proj/graph/nodes/progress_check.py")
    content = file_path.read_text()
    
    # 替换 human prompt 中的 f-string
    old_pattern = r'(\("human", f"""原始目标: \{topic\}.*?\{findings_summary\}\n\n评估并输出JSON:\n\{\{"on_track".*?\}\}\""")'
    
    new_content = content.replace(
        '        ("human", f"""原始目标: {topic}',
        '        ("human", """原始目标: {topic}'
    ).replace(
        '{plan_summary}',
        '{plan_summary}'
    ).replace(
        '{current_idx}/{len(plan)}',
        '{current_idx}/{total_plan}'
    ).replace(
        '{findings_summary}',
        '{findings_summary}'
    ).replace(
        '    chain = prompt | llm\n    result = chain.invoke({})',
        '''    chain = prompt | llm
    result = chain.invoke({
        "topic": topic,
        "plan_summary": plan_summary,
        "current_idx": current_idx,
        "total_plan": len(plan),
        "findings_summary": findings_summary
    })'''
    )
    
    file_path.write_text(new_content)
    print(f"✅ Fixed {file_path}")

# 由于需要手动修复每个文件，这里先给出修复模板
if __name__ == "__main__":
    print("开始批量修复...")
    print("提示：由于每个文件的 Prompt 结构不同，建议手动修复")
    print("通用原则：")
    print("1. 将 f-string 中的 {变量} 改为普通模板变量 {变量}")
    print("2. 在 chain.invoke() 中传入变量字典")
    print("3. 确保 JSON 示例中的 {} 使用 {{}} 转义")
