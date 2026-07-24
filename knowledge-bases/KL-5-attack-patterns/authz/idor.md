## AP-0003 IDOR(不安全直接对象引用)

- **攻击面**: A2.3
- **STRIDE映射**: I+E
- **CWE**: CWE-639
- **OWASP**: A01
- **前提条件**: 攻击者有合法账号，API使用可预测的资源ID
- **攻击路径**: 修改API中的userId/orderId(Source: URL路径参数) → 服务端未校验所有权 → 返回他人数据(Sink: 数据库查询)
- **影响**: 机密性(跨用户数据泄露)
- **检查点**: 设计时(对象级权限架构)、编码时(每个CRUD校验ownerId)、测试时(替换ID访问他人资源)
- **修复方案**: 服务端校验资源所有权 + 使用不可预测ID(UUID) + ABAC策略
- **参考**: https://owasp.org/www-community/attacks/Forced_browsing
