# 🎬 视频链接解密对比报告

## 📋 任务完成情况

✅ **任务完成**: 成功解密了两个不同的加密JavaScript代码，提取出两个不同的视频链接

## 🔓 解密过程总结

### 加密方式识别
- **加密算法**: XOR加密
- **密钥**: 128
- **JavaScript函数**: `String.fromCharCode(128^r.charCodeAt(i))`
- **Python解密函数**: 
```python
def decrypt_xor(encrypted_text, key=128):
    decrypted = ""
    for char in encrypted_text:
        char_code = ord(char)
        decrypted_char_code = key ^ char_code
        decrypted += chr(decrypted_char_code)
    return decrypted
```

## 🎯 提取的视频链接对比

### 第一个视频链接
```
https://8015.o9hx3f-s8jamrmtps5.sbs/0/e6/79/4f/1a384e695c7e5553b2ea13aa7a/chunklist_w.m3u8?v=1759636368-0pRDFVkKkavLBTJomTSSt%2FAHGk3fZLHdwZExioNukUM%3D
```

**详细信息**:
- **路径**: `/0/e6/79/4f/1a384e695c7e5553b2ea13aa7a/`
- **视频片段数**: 374个
- **M3U8文件大小**: 36,630字符
- **状态**: ✅ 可访问 (HTTP 200)

### 第二个视频链接
```
https://8015.o9hx3f-s8jamrmtps5.sbs/9/04/ff/91/e2fda9794729372dca7f165d1d/chunklist_w.m3u8?v=1759637531-IA%2BpS7sjHg3qZObmry0HzkvfxJC8rSqJlFAaByY1pbw%3D
```

**详细信息**:
- **路径**: `/9/04/ff/91/e2fda9794729372dca7f165d1d/`
- **视频片段数**: 395个
- **M3U8文件大小**: 38,688字符
- **状态**: ✅ 可访问 (HTTP 200)

## 📊 对比分析

### 相同点
- ✅ 使用相同的域名: `8015.o9hx3f-s8jamrmtps5.sbs`
- ✅ 使用相同的协议: HTTPS
- ✅ 都是HLS流媒体格式 (.m3u8)
- ✅ 都使用DPlayer播放器
- ✅ 都支持相同的16个域名
- ✅ 都包含时间戳和签名验证

### 不同点
| 项目 | 第一个链接 | 第二个链接 |
|------|------------|------------|
| 路径 | `/0/e6/79/4f/` | `/9/04/ff/91/` |
| 视频ID | `1a384e695c7e5553b2ea13aa7a` | `e2fda9794729372dca7f165d1d` |
| 时间戳 | `1759636368` | `1759637531` |
| 签名 | `0pRDFVkKkavLBTJomTSSt/AHGk3fZLHdwZExioNukUM=` | `IA+pS7sjHg3qZObmry0HzkvfxJC8rSqJlFAaByY1pbw=` |
| 视频片段数 | 374个 | 395个 |
| 文件大小 | 36,630字符 | 38,688字符 |

## 🎮 播放器配置

两个链接都使用相同的DPlayer配置：

```javascript
const dp = new DPlayer({
    container: document.getElementById('dplayer'),
    lang: 'zh-cn',
    video: {
        url: '[视频链接]',
        type: 'auto'
    },
    theme: '#ff0046',
    autoplay: true
});
```

## 🌐 支持的域名列表

两个链接都支持以下16个域名：
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

### 第一个视频链接相关文件
- `decrypted_js.txt` - 解密后的JavaScript代码
- `playlist.m3u8` - M3U8播放列表文件
- `video_segments.txt` - 374个视频片段链接
- `complete_video_analysis.json` - 完整分析结果

### 第二个视频链接相关文件
- `new_decrypted_js.txt` - 解密后的JavaScript代码
- `new_playlist.m3u8` - M3U8播放列表文件
- `new_video_segments.txt` - 395个视频片段链接
- `new_complete_video_analysis.json` - 完整分析结果

## 🎬 如何使用视频链接

### 方法1: 直接播放
使用支持HLS的播放器打开M3U8链接：
- **VLC Media Player**
- **PotPlayer**
- **MPV**
- **IINA** (macOS)

### 方法2: 下载视频
```bash
# 下载第一个视频
ffmpeg -i "https://8015.o9hx3f-s8jamrmtps5.sbs/0/e6/79/4f/1a384e695c7e5553b2ea13aa7a/chunklist_w.m3u8?v=1759636368-0pRDFVkKkavLBTJomTSSt%2FAHGk3fZLHdwZExioNukUM%3D" -c copy video1.mp4

# 下载第二个视频
ffmpeg -i "https://8015.o9hx3f-s8jamrmtps5.sbs/9/04/ff/91/e2fda9794729372dca7f165d1d/chunklist_w.m3u8?v=1759637531-IA%2BpS7sjHg3qZObmry0HzkvfxJC8rSqJlFAaByY1pbw%3D" -c copy video2.mp4
```

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
1. ✅ 识别并解密了两个XOR加密的JavaScript代码
2. ✅ 提取出了两个不同的视频M3U8播放列表链接
3. ✅ 验证了两个链接的可访问性
4. ✅ 解析了两个M3U8文件，分别获取了374和395个视频片段
5. ✅ 生成了完整的对比分析报告

**最终结果**: 
- **第一个视频链接**: 374个片段，36,630字符的M3U8文件
- **第二个视频链接**: 395个片段，38,688字符的M3U8文件

**两个都是有效的HLS流媒体链接，可以在支持HLS的播放器中播放！** 🎯

---

*报告生成时间: 2024年*
*工具: Python + requests + 自定义XOR解密*
