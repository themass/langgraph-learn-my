"""
Anthropic Skill: 添加字符串后缀
功能：给参数增加一个字符串后缀并返回
"""


def main(text: str, suffix: str = "_suffix") -> str:
    """
    给输入的字符串参数添加一个后缀并返回。
    
    Args:
        text: 要添加后缀的字符串（必需）
        suffix: 要添加的后缀字符串（可选，默认为 "_suffix"）
    
    Returns:
        str: 拼接后的字符串
    """
    return text + suffix


if __name__ == "__main__":
    import sys
    
    # 从命令行参数获取参数
    if len(sys.argv) < 2:
        print("错误: 至少需要提供一个 text 参数")
        print("用法: python append_suffix.py <text> [suffix]")
        sys.exit(1)
    
    text = sys.argv[1]
    suffix = sys.argv[2] if len(sys.argv) > 2 else "_suffix"
    
    result = main(text, suffix)
    print(result)
