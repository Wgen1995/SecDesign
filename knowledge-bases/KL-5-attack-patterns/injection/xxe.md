## AP-0002 XXE注入

- **攻击面**: A3.1, A3.2
- **STRIDE映射**: T+I
- **CWE**: CWE-611
- **OWASP**: A03
- **前提条件**: 应用解析XML输入，且XML解析器启用外部实体
- **攻击路径**: XML输入(Source: HTTP Body/上传文件) → XML解析器 → 外部实体加载(Sink: DocumentBuilder/SAXParser)
- **影响**: 机密性(任意文件读取)+完整性(SSRF)
- **检查点**: 编码时(禁用DTD/外部实体)、测试时(发送含ENTITY的XML)
- **修复方案**: 禁用DTD和外部实体解析 + 白名单校验XML来源
- **参考**: https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing
