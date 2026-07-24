# OWASP API Security Top 10 (2023)

> 来源：secdesign_spec.md 附录C
> 用途：Phase3 security-spec-generator 将API威胁映射到OWASP API检查点。

## 映射表

| 编号 | 类别 | 安全检查点映射 |
|------|------|---------------|
| API1 | BOPLA(属性级越权) | A2.2/A2.3 批量赋值/过度暴露 |
| API2 | Broken Authentication | A1.2 弱Token/密钥管理 |
| API3 | BOLA(对象级越权) | A2.3 IDOR |
| API4 | Unrestricted Resource Consumption | A8.3 无限流/批量操作 |
| API5 | Broken Function Level Authz | A2.2 垂直越权 |
| API6 | Unrestricted Business Flows | A8.2 业务逻辑绕过 |
| API7 | SSRF | A2.1/A7.2 |
| API8 | Security Misconfiguration | A5.2/A5.3 |
| API9 | Improper Inventory | A5.5 第三方API管理 |
| API10 | Unsafe Consumption | A2.4 信任外部API响应 |

---

## 条目详解

### API1 BOPLA（属性级越权 / Broken Object Property Level Authorization）

API 暴露或返回过多对象属性，攻击者通过批量赋值（Mass Assignment）写入非预期字段，或读取过度暴露的敏感属性越权。映射攻击面 A2.2 权限模型 / A2.3 资源所有权，对应 CWE-915/CWE-639。

### API2 Broken Authentication（认证失效）

API 认证机制失效，Token/密钥管理薄弱，攻击者冒充合法身份调用 API。映射攻击面 A1.2 认证方式，对应 CWE-287/CWE-798。

### API3 BOLA（对象级越权 / Broken Object Level Authorization）

对象级访问控制失效，攻击者通过 IDOR 访问或操作他人对象资源。映射攻击面 A2.3 资源所有权，对应 CWE-639/CWE-284。

### API4 Unrestricted Resource Consumption（资源消耗不受限）

API 缺乏限流/配额/批量操作限制，攻击者耗尽服务器资源。映射攻击面 A8.3 计费限流，对应 CWE-770/CWE-400。

### API5 Broken Function Level Authorization（功能级授权失效）

功能级访问控制失效，普通用户可执行管理员功能（垂直越权）。映射攻击面 A2.2 权限模型，对应 CWE-862/CWE-285。

### API6 Unrestricted Access to Sensitive Business Flows（业务流程不受限）

API 业务流程可被绕过或滥用，如跳过支付、绕过限额、自动化薅羊毛。映射攻击面 A8.2 业务流程绕过，对应 CWE-840/CWE-837。

### API7 SSRF（服务端请求伪造）

API 发起未经验证的服务端请求，可探测内网或读取云元数据。映射攻击面 A2.1 新增API / A7.2 客户端连接，对应 CWE-918。

### API8 Security Misconfiguration（安全配置错误）

API 安全配置不当，默认配置/不必要功能/明文配置/CORS 等。映射攻击面 A5.2 端口 / A5.3 配置，对应 CWE-732/CWE-16。

### API9 Improper Inventory Management（资产盘点不当）

API 资产管理缺失，影子 API/废弃端点/第三方 API 未纳管，攻击者利用未受保护的旧版本端点。映射攻击面 A5.5 三方依赖，对应 CWE-1188/CWE-918。

### API10 Unsafe Consumption of APIs（不安全消费 API）

信任并消费外部/第三方 API 响应而未充分校验，攻击者通过伪造外部服务响应渗透应用。映射攻击面 A2.4 外部接口，对应 CWE-345/CWE-20。
