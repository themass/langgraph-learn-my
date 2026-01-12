"""
测试 append-suffix-skill 的简单脚本
"""
import subprocess
import sys
import os


def test_skill():
    """测试 append-suffix-skill"""
    script_path = os.path.join(os.path.dirname(__file__), "append_suffix.py")
    
    print("🧪 测试 append-suffix-skill\n")
    
    # 测试1: 使用默认后缀
    print("测试1: text='hello'（使用默认后缀 '_suffix'）")
    result = subprocess.run(
        [sys.executable, script_path, "hello"],
        capture_output=True,
        text=True
    )
    print(f"✅ 结果: {result.stdout.strip()}\n")
    
    # 测试2: 使用自定义后缀
    print("测试2: text='hello', suffix='_world'")
    result = subprocess.run(
        [sys.executable, script_path, "hello", "_world"],
        capture_output=True,
        text=True
    )
    print(f"✅ 结果: {result.stdout.strip()}\n")
    
    # 测试3: 使用空后缀
    print("测试3: text='hello', suffix=''（空后缀）")
    result = subprocess.run(
        [sys.executable, script_path, "hello", ""],
        capture_output=True,
        text=True
    )
    print(f"✅ 结果: {result.stdout.strip()}\n")
    
    # 测试4: 使用中文
    print("测试4: text='你好', suffix='_世界'")
    result = subprocess.run(
        [sys.executable, script_path, "你好", "_世界"],
        capture_output=True,
        text=True
    )
    print(f"✅ 结果: {result.stdout.strip()}\n")
    
    print("✅ 所有测试完成！")


if __name__ == "__main__":
    test_skill()
