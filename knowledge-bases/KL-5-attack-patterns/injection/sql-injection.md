## AP-0001 SQL注入

- **攻击面**: A2.1, A4.1
- **STRIDE映射**: T+I
- **CWE**: CWE-89
- **OWASP**: A03
- **前提条件**: 攻击者可访问含数据库查询的API端点
- **攻击路径**: 用户输入(Source: HTTP参数) → 字符串拼接SQL → 数据库执行(Sink: Statement.execute)
- **影响**: 机密性(数据泄露)+完整性(数据篡改)+可用性(删库)
- **检查点**: 设计时(参数化查询架构)、编码时(mybatis禁$、ORM使用)、测试时(单引号/UNION/OR 1=1测试)
- **修复方案**: 参数化查询/ORM/预编译语句 + WAF + 输入白名单校验
- **参考**: https://owasp.org/www-community/attacks/SQL_Injection
