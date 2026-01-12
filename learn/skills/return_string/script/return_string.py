"""
Anthropic Skill: 返回字符串
功能：返回一个字符串
"""


def main(message: str = None) -> str:
    """
    返回一个字符串的简单技能。
    
    Args:
        message: 可选的消息字符串。如果提供，将返回该消息；否则返回默认消息。
    
    Returns:
        str: 返回的字符串消息
    """
    if message:
        return message
    return "Hello from Simple Skill!"


if __name__ == "__main__":
    import sys
    
    # 从命令行参数获取消息（如果有）
    if len(sys.argv) > 1:
        message = sys.argv[1]
        result = main(message)
    else:
        result = main()
    
    print(result)
