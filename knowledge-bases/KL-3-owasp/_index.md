# KL-3 OWASP标准簇 索引

> 来源：secdesign_spec.md 附录C
> 用途：Phase3 security-spec-generator 将威胁映射到OWASP检查点，生成安全规格文档。

---

## OWASP Top 10 (2021) 映射表

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

## OWASP API Security Top 10 (2023) 映射表

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

## ASVS关键验证项（Level 1-2精选）

| ASVS编号 | 验证项 | 映射攻击面 |
|---------|--------|-----------|
| V1.1 | 访问控制架构文档 | A2.2 |
| V2.1 | 认证架构 | A1.2 |
| V2.2 | 通用认证安全 | A1.1/A1.2 |
| V3.1 | 会话管理 | A1.3 |
| V4.1 | 通用访问控制 | A2.1/A2.2 |
| V4.2 | 操作级访问控制 | A2.2/A2.3 |
| V5.1 | 输入验证架构 | A3.1 |
| V5.3 | 输出编码/注入防护 | A3.1 |
| V6.1 | 加密架构 | A4.2/A7.3 |
| V7.1 | 日志架构 | A4.4 |
| V8.1 | 通用数据保护 | A4.2 |
| V9.1 | 通信安全架构 | A7.3 |
| V12.1 | 文件上传 | A3.2 |
| V13.1 | RESTful Web服务 | A2.1 |

---

## 3个子文件说明

| 文件 | 内容 | 条目数 |
|------|------|--------|
| top10.md | OWASP Top 10 (2021) 完整条目 + 检查点映射 | 10 |
| api-top10.md | OWASP API Security Top 10 (2023) 完整条目 + 检查点映射 | 10 |
| asvs.md | ASVS验证项（按域分类，Level 1-2精选） | ~14 |

---

> **注**：本文件为种子索引。3个子文件的完整内容由 Plan 2 填充。
