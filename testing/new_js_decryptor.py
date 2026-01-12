#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新的JavaScript解密工具
解密新提供的XOR加密JavaScript代码
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


def extract_video_links(js_code):
    """
    从JavaScript代码中提取视频链接
    
    Args:
        js_code: JavaScript代码字符串
    
    Returns:
        提取到的视频链接列表
    """
    import re
    
    video_links = []
    
    # 查找M3U8链接
    m3u8_pattern = r'https?://[^"\s<>]+\.m3u8[^"\s<>]*'
    m3u8_matches = re.findall(m3u8_pattern, js_code, re.IGNORECASE)
    video_links.extend(m3u8_matches)
    
    # 查找MP4链接
    mp4_pattern = r'https?://[^"\s<>]+\.mp4[^"\s<>]*'
    mp4_matches = re.findall(mp4_pattern, js_code, re.IGNORECASE)
    video_links.extend(mp4_matches)
    
    # 查找其他视频格式
    other_video_pattern = r'https?://[^"\s<>]+\.(webm|avi|mov|flv|mkv|ts)[^"\s<>]*'
    other_matches = re.findall(other_video_pattern, js_code, re.IGNORECASE)
    video_links.extend(other_matches)
    
    # 去重
    video_links = list(set(video_links))
    
    return video_links


def main():
    """主函数"""
    print("🔓 新的JavaScript解密工具")
    print("=" * 60)
    
    # 新的加密文本
    encrypted_text = "éæ¨­±¡½½§íõçõá±¶®ãæä¬íõçõá²²®ãæä¬íõçõá²¶®ãæä¬íõçõáµ°®ãæä¬íõçõáµµ®ãæä¬íõçõá¹µ®ãæä¬íõçõá±µ®ãæä¬íõçõá²µ®ãæä¬íõçõáµ²®ãæä¬íõçõá¹²®ãæä¬íõçõá²³®ãæä¬íõçõá±²®ãæä¬¹±ñõáîêé®ãïí¬íõçõá±·®ãæä¬íõçõá¶²®ãæä¬íõçõá·¸®ãæä§®éîäåøÏæ¨÷éîäï÷®ìïãáôéïî®èïóôîáíå©©ûãïîóô äð ½ îå÷ ÄÐìáùåò¨ûãïîôáéîåòº äïãõíåîô®çåôÅìåíåîôÂùÉä¨§äðìáùåò§©¬ìáîçº §úè­ãî§¬öéäåïº ûõòìº §èôôðóº¯¯¸°±µ®ï¹èø³æ­ó¸êáíòíôðóµ®óâó¯¹¯°´¯ææ¯¹±¯å²æäá¹·¹´·²¹³·²äãá·æ±¶µä±ä¯ãèõîëìéóôß÷®í³õ¸¿ö½±·µ¹¶³·µ³±­ÉÁ¥²ÂðÓ·óêÈç³ñÚÏâíòù°ÈúëöæøÊÃ¸òÓñÊìÆÁáÂùÙ±ðâ÷¥³Ä§¬ôùðåº §áõôï§ý¬ôèåíåº§£ææ°°´¶§¬áõôïðìáùºôòõåý©»éæ¨¯íïâéìå¯é®ôåóô¨÷éîäï÷®îáöéçáôïò®õóåòÁçåîô©©ûäð®ôåíðìáôå®öéäåï×òáð®áääÅöåîôÌéóôåîåò¨§ãìéãë§¬æõîãôéïî¨©ûéæ¨äð®öéäåï®ðáõóåä©ûäð®ðìáù¨©»ýéæ¨äð®ãïîôòïììåò®éóÓèï÷¨©©ûäð®ãïîôòïììåò®óåôÁõôïÈéäå¨©»ýý©»äð®ïî¨§ðìáù§¬æõîãôéïî¨©ûäð®ãïîôòïììåò®óåôÁõôïÈéäå¨©»ý©»äð®ïî¨§ðáõóå§¬æõîãôéïî¨©ûäð®ãïîôòïììåò®óåôÁõôïÈéäå¨©»ý©»ý¤¨§®äðìáùåò­éãïî®äðìáùåò­æõìì­éãïî§©®òåíïöåÁôôò¨§äáôá­âáììïïî§©»ý"
    
    print(f"🔒 加密文本长度: {len(encrypted_text)} 字符")
    print(f"🔑 使用XOR密钥: 128")
    
    # 解密
    try:
        decrypted_text = decrypt_xor(encrypted_text, 128)
        print(f"\n✅ 解密成功!")
        print("=" * 60)
        print("📄 解密后的内容:")
        print("-" * 60)
        print(decrypted_text)
        print("-" * 60)
        
        # 保存解密结果
        with open("new_decrypted_js.txt", "w", encoding="utf-8") as f:
            f.write(decrypted_text)
        print(f"\n💾 解密结果已保存到: new_decrypted_js.txt")
        
        # 提取视频链接
        print(f"\n🎬 提取视频链接...")
        video_links = extract_video_links(decrypted_text)
        
        if video_links:
            print(f"✅ 找到 {len(video_links)} 个视频链接:")
            for i, link in enumerate(video_links, 1):
                print(f"{i}. {link}")
        else:
            print("❌ 未找到视频链接")
        
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
        if "dplayer" in decrypted_text.lower():
            print("  ✅ 包含DPlayer播放器")
        if "autoplay" in decrypted_text.lower():
            print("  ✅ 包含自动播放设置")
        
        # 查找特定的配置信息
        import re
        
        # 查找DPlayer配置
        dp_config_match = re.search(r'new DPlayer\(\{([^}]+)\}', decrypted_text)
        if dp_config_match:
            print(f"\n🎮 DPlayer配置:")
            print(f"  {dp_config_match.group(1)}")
        
        # 查找视频URL
        video_url_match = re.search(r"url:\s*'([^']+)'", decrypted_text)
        if video_url_match:
            video_url = video_url_match.group(1)
            print(f"\n🎬 视频URL:")
            print(f"  {video_url}")
        
        # 查找域名列表
        domain_match = re.search(r"'([^']*\.cfd[^']*)'", decrypted_text)
        if domain_match:
            domains = domain_match.group(1).split(',')
            print(f"\n🌐 支持的域名 ({len(domains)} 个):")
            for domain in domains:
                print(f"  - {domain}")
        
    except Exception as e:
        print(f"❌ 解密失败: {e}")


if __name__ == "__main__":
    main()
