# SSR 中转设计方案与实施手册

本指南提供了将低延迟 VPS (Node B) 作为中继节点，连接高延迟 SSR 落地节点 (Node A) 的完整设计方案与操作步骤。

---

## 1. 方案设计与可行性分析

### 1.1 设计目标
通过中转机 (Node B: 8.217.122.83) 优化用户到落地机 (Node A: 103.248.229.223) 的网络延迟。

### 1.2 链路逻辑
`[用户本地]` -> `[Node B]` -> `[Node A]` -> `[目标网站]`
*   **出口 IP**: 最终出口依然是 Node A 的 IP。
*   **兼容性**: 方案工作在物理转发层，完美兼容 SSR 所有的加密与混淆协议。

---

## 2. 实施步骤 (Iptables)

在 **Node B** 执行：

1.  **开启转发**: `sysctl -w net.ipv4.ip_forward=1`
2.  **配置 DNAT (目标转换)**:
    ```bash
    iptables -t nat -A PREROUTING -p tcp --dport 1025 -j DNAT --to-destination 103.248.229.223:1025
    iptables -t nat -A PREROUTING -p udp --dport 1025 -j DNAT --to-destination 103.248.229.223:1025
    ```
3.  **配置 MASQUERADE (源地址伪装)**:
    ```bash
    iptables -t nat -A POSTROUTING -p tcp -d 103.248.229.223 --dport 1025 -j MASQUERADE
    iptables -t nat -A POSTROUTING -p udp -d 103.248.229.223 --dport 1025 -j MASQUERADE
    ```

---

## 3. 常见问题 (QA)

*   **Q: 为什么找不到监听端口？**
    *   **A**: Iptables 在内核层转发数据包，不经过应用层，所以没有任何进程在监听。这是正常的。
*   **Q: 本地如何测试？**
    *   **A**: Mac 终端执行 `nc -vz 8.217.122.83 1025`。若显示 `succeeded` 则表示转发已通。
*   **Q: 如果 Iptables 不生效怎么办？**
    *   **A**: 请确保 Node A 的安全组允许了 Node B 的 IP 访问，或者尝试使用 **Realm** 工具进行软件转发。
