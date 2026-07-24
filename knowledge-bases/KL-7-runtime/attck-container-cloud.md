# MITRE ATT&CK 容器/云矩阵

> 来源：secdesign_spec.md 附录G
> 用途：Phase6 security-review 攻击链验证与运行时检测规则映射。
> 检测建议基于 MITRE ATT&CK for Containers 公开知识库。

---

## 战术与技术映射

| 战术 | 关键技术 | 映射攻击面 | 检测建议 |
|------|---------|-----------|---------|
| Initial Access | 暴露的API/Dashboard | A2.1/A5.2 | 监控对 kubelet/API/Dashboard 管理端口的未授权外部连接与异常源 IP。 |
| Execution | 容器内命令执行 | A6.1/A6.2 | 监控 kubectl exec/docker exec 调用与容器内异常进程派生行为。 |
| Persistence | 后门Pod/DaemonSet/Webhook | A6.2 | 监控异常 Pod、DaemonSet、MutatingWebhookConfiguration 与定时任务创建事件。 |
| Privilege Escalation | privileged容器/RBAC滥用 | A6.2 | 监控 privileged 容器创建、hostPath 挂载与向高权限角色绑定 RoleBinding 的行为。 |
| Defense Evasion | 清除日志/禁用安全策略 | A4.4/A6.2 | 监控审计日志删除/篡改、NetworkPolicy 与准入控制策略被禁用或删除事件。 |
| Credential Access | Secret窃取/etcd数据泄露 | A1.4/A6.2 | 监控批量 Secret 读取、直接访问 etcd 与异常 ServiceAccount Token 使用。 |
| Lateral Movement | 网络策略绕过/ServiceAccount窃取 | A6.2 | 监控 NetworkPolicy 违规、跨命名空间异常访问与 SA Token 被复用于其他工作负载。 |
| Exfiltration | DNS外泄/云存储外传 | A6.3 | 监控异常 DNS 流量（高吞吐、长子域名隧道）与出站到云存储的未预期大流量传输。 |

---

## 按攻击面分组

### A1 身份与认证
- Credential Access: Secret窃取/etcd数据泄露（A1.4/A6.2）

### A2 授权与访问控制
- Initial Access: 暴露的API/Dashboard（A2.1/A5.2）

### A4 审计与日志
- Defense Evasion: 清除日志/禁用安全策略（A4.4/A6.2）

### A5 配置与运维
- Initial Access: 暴露的API/Dashboard（A2.1/A5.2）

### A6 运行时环境
- Execution: 容器内命令执行（A6.1/A6.2）
- Persistence: 后门Pod/DaemonSet/Webhook（A6.2）
- Privilege Escalation: privileged容器/RBAC滥用（A6.2）
- Defense Evasion: 禁用安全策略（A4.4/A6.2）
- Credential Access: etcd数据泄露（A1.4/A6.2）
- Lateral Movement: 网络策略绕过/ServiceAccount窃取（A6.2）
- Exfiltration: DNS外泄/云存储外传（A6.3）

---

> **注**：跨攻击面映射的战术在其关联的每个攻击面分组下重复列出，以便按攻击面检索时覆盖完整。共 8 条战术，覆盖 5 个攻击面分组；A6 运行时环境为容器/云攻击的主战场（7/8 战术涉及）。
