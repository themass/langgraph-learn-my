"""
测试 return-string-skill 的简单脚本
"""
import subprocess
import sys
import os


def test_skill():
    """测试 return-string-skill"""
    script_path = os.path.join(os.path.dirname(__file__), "return_string.py")
    
    print("🧪 测试 return-string-skill\n")
    
    # 测试1: 无参数（使用默认值）
    print("测试1: 无参数（使用默认值）")
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True
    )
    print(f"✅ 结果: {result.stdout.strip()}\n")
    
    # 测试2: 传入自定义消息
    print("测试2: 传入自定义消息 '这是我的测试消息'")
    result = subprocess.run(
        [sys.executable, script_path, "这是我的测试消息"],
        capture_output=True,
        text=True
    )
    print(f"✅ 结果: {result.stdout.strip()}\n")
    
    print("✅ 所有测试完成！")


if __name__ == "__main__":
    test_skill()
