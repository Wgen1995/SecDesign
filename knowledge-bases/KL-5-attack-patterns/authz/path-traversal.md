## AP-0004 路径穿越

- **攻击面**: A3.2
- **STRIDE映射**: T+I
- **CWE**: CWE-22
- **OWASP**: A01
- **前提条件**: 应用处理文件路径且未严格校验
- **攻击路径**: 文件名参数(Source: HTTP参数) → 路径拼接 → 越界读取(Sink: File.readFile)
- **影响**: 机密性(任意文件读取)
- **检查点**: 编码时(路径规范化+白名单目录)、测试时(../穿越测试)
- **修复方案**: 路径规范化(realpath) + 白名单目录 + 拒绝含..的路径
- **参考**: https://owasp.org/www-community/attacks/Path_Traversal
