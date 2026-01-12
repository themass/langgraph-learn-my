# SSR中转快速开始指南

## 🚀 5分钟快速部署

### 方案选择

- **有SSH访问权限** → **方案1: SSH隧道**（最简单）
- **有root权限，无SSH** → **方案2: iptables转发**（性能最好）
- **无root权限** → **方案3: socat转发**（最简单）
- **需要SSR专用方案** → **方案4: SSR客户端模式**（推荐）

---

## 📝 方案1: SSH隧道（推荐）

**在中转服务器（8.217.122.83）上执行：**

```bash
# 1. 安装 autossh
sudo apt-get install -y autossh  # Ubuntu/Debian
sudo yum install -y autossh       # CentOS/RHEL

# 2. 建立SSH隧道
autossh -M 20000 -f -N -L 8388:103.248.229.223:8388 root@103.248.229.223

# 3. 验证
netstat -tlnp | grep 8388
```

**配置SSR客户端：**
- 服务器地址: `8.217.122.83`
- 端口: `8388`
- 其他配置: 与原始SSR服务器相同

---

## 📝 方案2: iptables转发（高性能）

**在中转服务器上执行（需要root）：**

```bash
# 1. 启用IP转发
echo 1 > /proc/sys/net/ipv4/ip_forward
echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
sysctl -p

# 2. 配置iptables
iptables -t nat -A PREROUTING -p tcp --dport 8388 -j DNAT --to-destination 103.248.229.223:8388
iptables -t nat -A POSTROUTING -p tcp -d 103.248.229.223 --dport 8388 -j MASQUERADE
iptables -A FORWARD -p tcp -d 103.248.229.223 --dport 8388 -j ACCEPT
iptables -A FORWARD -p tcp -s 103.248.229.223 --sport 8388 -j ACCEPT

# 3. 保存规则
sudo netfilter-persistent save  # Ubuntu/Debian
sudo service iptables save      # CentOS/RHEL
```

**配置SSR客户端：**
- 服务器地址: `8.217.122.83`
- 端口: `8388`
- 其他配置: 与原始SSR服务器相同

---

## 📝 方案3: socat转发（简单）

**在中转服务器上执行：**

```bash
# 1. 安装 socat
sudo apt-get install -y socat  # Ubuntu/Debian
sudo yum install -y socat      # CentOS/RHEL

# 2. 建立转发
socat TCP-LISTEN:8388,fork,reuseaddr TCP:103.248.229.223:8388

# 3. 后台运行
nohup socat TCP-LISTEN:8388,fork,reuseaddr TCP:103.248.229.223:8388 > /dev/null 2>&1 &
```

**配置SSR客户端：**
- 服务器地址: `8.217.122.83`
- 端口: `8388`
- 其他配置: 与原始SSR服务器相同

---

## 📝 方案4: SSR客户端模式（推荐）

**详细步骤：** 查看 [方案4-安装配置指南.md](方案4-安装配置指南.md)

**快速流程：**
1. 在中转服务器安装SSR客户端（shadowsocksr-libev）
2. 配置SSR客户端连接到原始SSR服务器
3. 使用socat监听1025端口，转发到SSR客户端1080端口
4. 在本机配置SSR客户端连接到中转服务器

---

## ✅ 验证配置

### 1. 检查端口监听

```bash
netstat -tlnp | grep 8388
```

### 2. 测试连接

```bash
telnet 8.217.122.83 8388
```

### 3. 使用SSR客户端测试

在SSR客户端中添加服务器：
- 地址: `8.217.122.83`
- 端口: `8388`（或方案4中的1025）
- 其他配置与原始SSR服务器相同

---

## 🔧 常见问题

### 连接超时

```bash
# 检查防火墙
sudo ufw status          # Ubuntu
sudo firewall-cmd --list-all  # CentOS

# 开放端口
sudo ufw allow 8388/tcp  # Ubuntu

# 测试SSR服务器
ping 103.248.229.223
telnet 103.248.229.223 8388
```

### 速度慢

- 测试延迟：`ping 103.248.229.223`
- 检查带宽使用情况
- 考虑更换中转服务器

---

**最后更新**: 2024-12-27
