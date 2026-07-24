# OWASP Top 10 (2021)

> 来源：secdesign_spec.md 附录C
> 用途：Phase3 security-spec-generator 将威胁映射到OWASP检查点，生成安全规格文档。

## 映射表

| 编号 | 类别 | 安全检查点映射 |
|------|------|---------------|
| A01 | Broken Access Control | A2.2/A2.3 越权/IDOR |
| A02 | Cryptographic Failures | A1.4/A4.2/A7.3 凭证/数据/通信加密 |
| A03 | Injection | A2.1/A3.1 SQL/命令/代码注入 |
| A04 | Insecure Design | A8.1/A8.2 缺少二次认证/流程绕过 |
| A05 | Security Misconfiguration | A5.2/A5.3/A7.4 默认配置/明文密码/CORS |
| A06 | Vulnerable Components | A5.5 三方件CVE |
| A07 | Auth Failures | A1.1/A1.2 暴力破解/会话固定 |
| A08 | Data Integrity Failures | A5.5/A8.4 CI/CD投毒/反序列化 |
| A09 | Logging Failures | A4.4 日志缺失/日志注入 |
| A10 | SSRF | A2.1/A7.2 内网探测/云元数据 |

---

## 条目详解

### A01 Broken Access Control（访问控制失效）

用户可越权执行超出其权限的操作或访问数据，包括水平/垂直越权与IDOR。2021年从第5位上升至第1位，OWASP统计94%应用存在某种形式的访问控制失效。映射攻击面 A2.2 权限模型 / A2.3 资源所有权，对应 CWE-284/CWE-862/CWE-639。

### A02 Cryptographic Failures（加密失效）

敏感数据因弱加密、明文传输或弱密钥管理而暴露（原 A02 Sensitive Data Exposure 更名）。涵盖凭证/数据/通信加密全链路。映射攻击面 A1.4 凭证 / A4.2 敏感数据 / A7.3 通信加密，对应 CWE-327/CWE-319/CWE-522。

### A03 Injection（注入）

不可信数据被解释为命令或查询，包括 SQL/命令/代码/XSS 注入（2021年将 XSS 合并入注入类）。映射攻击面 A2.1 新增API / A3.1 用户输入，对应 CWE-78/CWE-89/CWE-94/CWE-79。

### A04 Insecure Design（不安全设计）

缺少安全控制的设计缺陷，需在架构层引入威胁建模和安全设计模式，而非仅靠补丁修补实现缺陷。映射攻击面 A8.1 高危操作 / A8.2 业务流程绕过，对应缺少二次认证/流程绕过等设计层风险。

### A05 Security Misconfiguration（安全配置错误）

默认配置、开放云存储、详细错误信息、不必要功能、CORS 配置不当等。映射攻击面 A5.2 端口 / A5.3 配置 / A7.4 前端安全，对应 CWE-732/CWE-611/CWE-942。

### A06 Vulnerable Components（易受攻击组件）

依赖已知 CVE 漏洞的第三方组件或过时版本。映射攻击面 A5.5 三方依赖，对应 CWE-1104/CWE-1395，需 SCA 扫描与版本锁定。

### A07 Auth Failures（认证失效）

认证与身份识别机制失效，攻击者通过自动化攻击冒充身份（原 A07 Broken Authentication 更名）。映射攻击面 A1.1 新增用户 / A1.2 认证方式，对应 CWE-287/CWE-307/CWE-384。

### A08 Data Integrity Failures（数据完整性失效）

软件与数据完整性未校验，包括 CI/CD 管道投毒与不安全反序列化（原 A08 Insecure Deserialization 扩展）。映射攻击面 A5.5 三方依赖 / A8.4 竞态条件，对应 CWE-502/CWE-494。

### A09 Logging Failures（日志与监控失效）

安全日志与监控缺失，无法检测或响应违规。映射攻击面 A4.4 日志审计，对应 CWE-778/CWE-117，需记录安全事件并告警。

### A10 SSRF（服务端请求伪造）

服务端发起未经验证的请求，可探测内网或读取云元数据获取 AK/SK。映射攻击面 A2.1 新增API / A7.2 客户端连接，对应 CWE-918，需白名单与 IMDSv2 防护。
