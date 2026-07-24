# KL-7 运行时安全检查 索引

> 来源：secdesign_spec.md 附录G
> 用途：Phase5 security-test-generator 渗透测试用例 + Phase6 security-review 攻击链验证。

---

## OWASP WSTG关键测试项索引表

| WSTG编号 | 测试项 | 映射攻击面 |
|---------|--------|-----------|
| WSTG-ATHN-01 | 凭证传输测试 | A1.2/A7.3 |
| WSTG-ATHN-03 | 暴力破解测试 | A1.1/A1.2 |
| WSTG-ATHN-07 | 会话固定测试 | A1.3 |
| WSTG-SESS-02 | Cookie属性测试 | A1.3 |
| WSTG-SESS-06 | 会话超时测试 | A1.3 |
| WSTG-ATHZ-01 | 目录遍历测试 | A2.1 |
| WSTG-ATHZ-02 | 水平越权测试 | A2.3 |
| WSTG-ATHZ-04 | 垂直越权测试 | A2.2 |
| WSTG-INPV-01 | SQL注入测试 | A2.1/A3.1 |
| WSTG-INPV-02 | 命令注入测试 | A3.1 |
| WSTG-INPV-05 | XSS测试 | A7.1/A3.1 |
| WSTG-INPV-11 | 文件上传测试 | A3.2 |
| WSTG-CONF-05 | 管理界面测试 | A5.2 |
| WSTG-CONF-07 | 限流测试 | A8.3 |
| WSTG-CRYP-01 | TLS配置测试 | A7.3 |
| WSTG-CRYP-03 | 敏感数据传输测试 | A7.3 |

---

## ATT&CK容器/云关键战术表

| 战术 | 关键技术 | 映射攻击面 |
|------|---------|-----------|
| Initial Access | 暴露的API/Dashboard | A2.1/A5.2 |
| Execution | 容器内命令执行 | A6.1/A6.2 |
| Persistence | 后门Pod/DaemonSet/Webhook | A6.2 |
| Privilege Escalation | privileged容器/RBAC滥用 | A6.2 |
| Defense Evasion | 清除日志/禁用安全策略 | A4.4/A6.2 |
| Credential Access | Secret窃取/etcd数据泄露 | A1.4/A6.2 |
| Lateral Movement | 网络策略绕过/ServiceAccount窃取 | A6.2 |
| Exfiltration | DNS外泄/云存储外传 | A6.3 |

---

## 2个子文件说明

| 文件 | 内容 | 条目数 |
|------|------|--------|
| wstg-index.md | OWASP WSTG 测试项索引（按攻击面分类） | ~16 |
| attck-container-cloud.md | MITRE ATT&CK 容器/云矩阵（按战术分类） | ~8 |

---

> **注**：本文件为种子索引。2个子文件的完整内容（含测试方法详述）由 Plan 2 填充。
