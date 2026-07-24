## AP-0005 Java反序列化

- **攻击面**: A3.1, A5.5
- **STRIDE映射**: T+E
- **CWE**: CWE-502
- **OWASP**: A08
- **前提条件**: 应用反序列化不可信数据，classpath含可利用链
- **攻击路径**: 序列化数据(Source: HTTP Body/Cookie/MQ) → ObjectInputStream.readObject() → 利用链触发(Sink: Runtime.exec)
- **影响**: 完整性+可用性(RCE)
- **检查点**: 编码时(白名单过滤/禁用ObjectInput)、测试时(ysoserial探测)
- **修复方案**: 白名单反序列化类 + Introspector过滤 + 升级依赖
- **参考**: https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data
