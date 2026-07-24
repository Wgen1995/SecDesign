# K8s 合规

> 来源：secdesign_spec.md 附录F "容器合规种子（K8s）"
> 基准：CIS Kubernetes Benchmark
> 用途：Phase4 覆盖率检查 + Phase5 容器合规测试（K8s维度）

---

## 规则

| 规则ID | 规则 | CWE | 检查方式 | 严重度 |
|--------|------|-----|---------|--------|
| K8S-01 | 禁止privileged/hostPath/hostNetwork/hostPID/hostIPC | CWE-269 | 检查Pod Security Standards / Pod spec | S1 |
| K8S-02 | 禁止*/*授权，SA最小权限 | CWE-250 | 检查RBAC Role/ClusterRole绑定 | S2 |
| K8S-03 | Secret加密存储，etcd加密 | CWE-312 | 检查etcd加密配置/EncryptionConfiguration | S2 |
| K8S-04 | 默认拒绝入站出站，仅开放必需 | CWE-284 | 检查NetworkPolicy覆盖 | S2 |
| K8S-05 | CPU/Memory requests+limits必须设置 | CWE-770 | 检查Pod资源声明 | S3 |

## 检查流程

1. 审计 Pod/Deployment/DaemonSet/StatefulSet/CronJob 的 `securityContext`，确认 `privileged: false`、`hostNetwork: false`、`hostPID: false`、`hostIPC: false`、无 `hostPath` 挂载
2. 检查集群 Pod Security Standards admission 模式（baseline/restricted），确认 restricted 为 enforce 级别
3. 列出所有 Role/ClusterRole 与 RoleBinding/ClusterRoleBinding，检查是否存在 `verbs: ["*"] resources: ["*"]` 的过度授权；确认 ServiceAccount 遵循最小权限
4. 检查 kube-apiserver `--encryption-provider-config`，确认 etcd 静态加密已启用；验证 Secret 在 etcd 中为密文
5. 审计 NetworkPolicy 覆盖率，确认存在 default-deny 基线策略，仅显式开放必需流量
6. 检查所有 Pod 的 `resources.requests` 与 `resources.limits`（CPU+Memory）是否均设置
7. 补充检查：容器 `runAsNonRoot: true`、`readOnlyRootFilesystem: true`、`allowPrivilegeEscalation: false`

## 关联攻击面

- A6.2: K8s配置 — privileged Pod 直接导致容器逃逸（KL-5: escape/privileged-container）
- A6.2: K8s配置 — 过度 RBAC 授权导致横向移动与权限提升
- A6.2: K8s配置 — 未加密 Secret 导致 etcd 拖库后凭证泄露
- A6.2: K8s配置 — 缺失网络策略使攻击者Pod可直达内网服务（KL-5: network/ssrf 关联）
