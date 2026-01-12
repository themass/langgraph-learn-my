package com.example.strongswan;

/**
 * strongSwan Android 集成示例
 * 
 * 这个类提供了与 strongSwan 原生库的 JNI 接口
 */
public class StrongSwanNative {
    
    // 加载原生库
    static {
        try {
            System.loadLibrary("strongswan_integration");
            System.loadLibrary("strongswan");
            System.loadLibrary("charon");
            System.loadLibrary("ipsec");
            System.loadLibrary("androidbridge");
        } catch (UnsatisfiedLinkError e) {
            throw new RuntimeException("Failed to load strongSwan native libraries", e);
        }
    }
    
    /**
     * 初始化 strongSwan
     * @return true 如果初始化成功，false 否则
     */
    public static native boolean initialize();
    
    /**
     * 清理 strongSwan 资源
     */
    public static native void cleanup();
    
    /**
     * 检查 strongSwan 是否已初始化
     * @return true 如果已初始化，false 否则
     */
    public static native boolean isInitialized();
    
    /**
     * 获取 strongSwan 版本信息
     * @return 版本字符串
     */
    public static native String getVersion();
    
    /**
     * 连接到 VPN 服务器
     * @param server 服务器地址
     * @param port 服务器端口
     * @param username 用户名
     * @param password 密码
     * @return 0 如果连接成功，-1 如果失败
     */
    public static native int connect(String server, int port, String username, String password);
    
    /**
     * 断开 VPN 连接
     * @return 0 如果断开成功，-1 如果失败
     */
    public static native int disconnect();
    
    /**
     * 获取连接状态
     * @return 0 = 已连接, 1 = 连接中, 2 = 已断开, -1 = 错误
     */
    public static native int getConnectionStatus();
}
