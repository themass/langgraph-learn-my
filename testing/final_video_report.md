# 🎬 视频链接提取成功报告

## 📋 任务完成情况

✅ **任务完成**: 成功从加密的JavaScript代码中提取出视频链接

## 🔓 解密过程

### 1. 识别加密方式
- 发现JavaScript代码使用了XOR加密
- 加密函数: `String.fromCharCode(128^r.charCodeAt(i))`
- 密钥: 128

### 2. 解密实现
```python
def decrypt_xor(encrypted_text, key=128):
    decrypted = ""
    for char in encrypted_text:
        char_code = ord(char)
        decrypted_char_code = key ^ char_code
        decrypted += chr(decrypted_char_code)
    return decrypted
```

### 3. 解密结果
成功解密出完整的JavaScript代码，包含DPlayer视频播放器配置。

## 🎯 提取的视频链接

### 主要M3U8播放列表
```
https://8015.o9hx3f-s8jamrmtps5.sbs/0/e6/79/4f/1a384e695c7e5553b2ea13aa7a/chunklist_w.m3u8?v=1759636368-0pRDFVkKkavLBTJomTSSt%2FAHGk3fZLHdwZExioNukUM%3D
```

### 视频信息
- **类型**: HLS (HTTP Live Streaming)
- **域名**: 8015.o9hx3f-s8jamrmtps5.sbs
- **协议**: HTTPS
- **状态**: ✅ 可访问 (HTTP 200)
- **内容类型**: application/vnd.apple.mpegurl

### 视频片段
- **总片段数**: 374个
- **片段格式**: .ts (Transport Stream)
- **片段示例**:
  - chunklist_w0.ts
  - chunklist_w1.ts
  - chunklist_w2.ts
  - ... (共374个片段)

## 🎮 播放器配置

### DPlayer配置
```javascript
const dp = new DPlayer({
    container: document.getElementById('dplayer'),
    lang: 'zh-cn',
    video: {
        url: 'https://8015.o9hx3f-s8jamrmtps5.sbs/0/e6/79/4f/1a384e695c7e5553b2ea13aa7a/chunklist_w.m3u8?v=1759636368-0pRDFVkKkavLBTJomTSSt%2FAHGk3fZLHdwZExioNukUM%3D',
        type: 'auto'
    },
    theme: '#ff0046',
    autoplay: true
});
```

### 支持的域名
- mugua16.cfd
- mugua22.cfd
- mugua26.cfd
- mugua50.cfd
- mugua55.cfd
- mugua95.cfd
- mugua15.cfd
- mugua25.cfd
- mugua52.cfd
- mugua92.cfd
- mugua23.cfd
- mugua12.cfd
- **91quanji.com**
- mugua17.cfd
- mugua62.cfd
- mugua78.cfd

## 📁 生成的文件

1. **decrypted_js.txt** - 解密后的JavaScript代码
2. **playlist.m3u8** - M3U8播放列表文件
3. **video_segments.txt** - 所有视频片段链接
4. **complete_video_analysis.json** - 完整分析结果
5. **video_links_analysis.json** - 视频链接分析

## 🎬 如何使用视频链接

### 方法1: 直接播放
使用支持HLS的播放器打开M3U8链接：
- **VLC Media Player**
- **PotPlayer**
- **MPV**
- **IINA** (macOS)

### 方法2: 下载视频
```bash
# 使用ffmpeg下载
ffmpeg -i "https://8015.o9hx3f-s8jamrmtps5.sbs/0/e6/79/4f/1a384e695c7e5553b2ea13aa7a/chunklist_w.m3u8?v=1759636368-0pRDFVkKkavLBTJomTSSt%2FAHGk3fZLHdwZExioNukUM%3D" -c copy output.mp4
```

### 方法3: 在线播放
将M3U8链接粘贴到支持HLS的在线播放器中。

## 🔧 技术细节

### 加密算法
- **类型**: XOR加密
- **密钥**: 128
- **实现**: JavaScript `String.fromCharCode(128^r.charCodeAt(i))`

### 视频技术
- **流媒体协议**: HLS (HTTP Live Streaming)
- **视频格式**: MPEG-TS
- **播放器**: DPlayer
- **编码**: 自动检测

### 安全措施
- 域名白名单验证
- 时间戳验证 (v参数)
- 签名验证 (包含加密签名)

## ✅ 总结

**任务完成度**: 100%

成功完成了以下工作：
1. ✅ 识别并解密了XOR加密的JavaScript代码
2. ✅ 提取出了完整的视频M3U8播放列表链接
3. ✅ 验证了链接的可访问性
4. ✅ 解析了M3U8文件，获取了374个视频片段
5. ✅ 生成了完整的分析报告和文件

**最终结果**: 成功获取了 `https://www.a3m5m.com/s/video/shipin/1044455` 页面的视频链接！

---

*报告生成时间: 2024年*
*工具: Python + requests + BeautifulSoup + 自定义XOR解密*
