## AP-0008 特权容器逃逸

- **攻击面**: A6.1, A6.2
- **STRIDE映射**: E+I
- **CWE**: CWE-269
- **OWASP**: A01
- **前提条件**: 攻击者可创建或进入privileged容器
- **攻击路径**: privileged Pod(Source: K8s部署配置) → mount宿主机磁盘 → chroot(Sink: 宿主机控制)
- **影响**: 完整性+机密性+可用性(宿主机完全控制)
- **检查点**: 设计时(Pod安全标准restricted)、部署时(审计privileged配置)、测试时(尝试mount/chroot)
- **修复方案**: Pod Security Standards enforce:restricted + OPA/Gatekeeper策略 + 运行时安全(Falco)
- **参考**: MITRE ATT&CK T1611
