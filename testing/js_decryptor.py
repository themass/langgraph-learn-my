#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript解密工具
解密XOR加密的JavaScript代码
"""

def decrypt_xor(encrypted_text, key=128):
    """
    XOR解密函数
    对应JavaScript中的: String.fromCharCode(128^r.charCodeAt(i))
    
    Args:
        encrypted_text: 加密的文本
        key: XOR密钥，默认128
    
    Returns:
        解密后的文本
    """
    decrypted = ""
    for char in encrypted_text:
        # 获取字符的ASCII码
        char_code = ord(char)
        # 执行XOR操作
        decrypted_char_code = key ^ char_code
        # 转换回字符
        decrypted += chr(decrypted_char_code)
    return decrypted


def main():
    """主函数"""
    print("🔓 JavaScript解密工具")
    print("=" * 50)
    
    # 加密的文本
    encrypted_text = "éæ¨­±¡½½§íõçõá±¶®ãæä¬íõçõá²²®ãæä¬íõçõá²¶®ãæä¬íõçõáµ°®ãæä¬íõçõáµµ®ãæä¬íõçõá¹µ®ãæä¬íõçõá±µ®ãæä¬íõçõá²µ®ãæä¬íõçõáµ²®ãæä¬íõçõá¹²®ãæä¬íõçõá²³®ãæä¬íõçõá±²®ãæä¬¹±ñõáîêé®ãïí¬íõçõá±·®ãæä¬íõçõá¶²®ãæä¬íõçõá·¸®ãæä§®éîäåøÏæ¨÷éîäï÷®ìïãáôéïî®èïóôîáíå©©ûãïîóô äð ½ îå÷ ÄÐìáùåò¨ûãïîôáéîåòº äïãõíåîô®çåôÅìåíåîôÂùÉä¨§äðìáùåò§©¬ìáîçº §úè­ãî§¬öéäåïº ûõòìº §èôôðóº¯¯¸°±µ®ï¹èø³æ­ó¸êáíòíôðóµ®óâó¯°¯å¶¯·¹¯´æ¯±á³¸´å¶¹µã·åµµµ³â²åá±³áá·á¯ãèõîëìéóôß÷®í³õ¸¿ö½±·µ¹¶³¶³¶¸­°ðÒÄÆÖëËëáöÌÂÔÊïíÔÓÓô¥²ÆÁÈÇë³æÚÌÈä÷ÚÅøéïÎõëÕÍ¥³Ä§¬ôùðåº §áõôï§ý¬ôèåíåº§£ææ°°´¶§¬áõôïðìáùºôòõåý©»éæ¨¯íïâéìå¯é®ôåóô¨÷éîäï÷®îáöéçáôïò®õóåòÁçåîô©©ûäð®ôåíðìáôå®öéäåï×òáð®áääÅöåîôÌéóôåîåò¨§ãìéãë§¬æõîãôéïî¨©ûéæ¨äð®öéäåï®ðáõóåä©ûäð®ðìáù¨©»ýéæ¨äð®ãïîôòïììåò®éóÓèï÷¨©©ûäð®ãïîôòïììåò®óåôÁõôïÈéäå¨©»ýý©»äð®ïî¨§ðìáù§¬æõîãôéïî¨©ûäð®ãïîôòïììåò®óåôÁõôïÈéäå¨©»ý©»äð®ïî¨§ðáõóå§¬æõîãôéïî¨©ûäð®ãïîôòïììåò®óåôÁõôïÈéäå¨©»ý©»ý¤¨§®äðìáùåò­éãïî®äðìáùåò­æõìì­éãïî§©®òåíïöåÁôôò¨§äáôá­âáììïïî§©»ý"
    
    print(f"🔒 加密文本长度: {len(encrypted_text)} 字符")
    print(f"🔑 使用XOR密钥: 128")
    
    # 解密
    try:
        decrypted_text = decrypt_xor(encrypted_text, 128)
        print(f"\n✅ 解密成功!")
        print("=" * 50)
        print("📄 解密后的内容:")
        print("-" * 50)
        print(decrypted_text)
        print("-" * 50)
        
        # 保存解密结果
        with open("decrypted_js.txt", "w", encoding="utf-8") as f:
            f.write(decrypted_text)
        print(f"\n💾 解密结果已保存到: decrypted_js.txt")
        
        # 分析解密后的内容
        print(f"\n🔍 内容分析:")
        if "video" in decrypted_text.lower():
            print("  ✅ 包含视频相关关键词")
        if "url" in decrypted_text.lower():
            print("  ✅ 包含URL相关关键词")
        if "http" in decrypted_text.lower():
            print("  ✅ 包含HTTP链接")
        if "m3u8" in decrypted_text.lower():
            print("  ✅ 包含M3U8流媒体链接")
        if "mp4" in decrypted_text.lower():
            print("  ✅ 包含MP4视频链接")
        
    except Exception as e:
        print(f"❌ 解密失败: {e}")


def test_decrypt_function():
    """测试解密函数"""
    print("\n🧪 测试解密函数:")
    
    # 测试简单的加密文本
    test_text = "Hello World"
    print(f"原始文本: {test_text}")
    
    # 模拟加密过程
    encrypted = ""
    for char in test_text:
        encrypted += chr(128 ^ ord(char))
    
    print(f"加密后: {encrypted}")
    
    # 解密
    decrypted = decrypt_xor(encrypted, 128)
    print(f"解密后: {decrypted}")
    
    if test_text == decrypted:
        print("✅ 解密函数工作正常")
    else:
        print("❌ 解密函数有问题")


if __name__ == "__main__":
    main()
    test_decrypt_function()
