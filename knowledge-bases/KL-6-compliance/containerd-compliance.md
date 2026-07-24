# Containerd 合规

> 来源：CIS Containerd Benchmark v1.0.0（知识补充）
> 用途：Phase4 覆盖率检查 + Phase5 容器合规测试（Containerd维度）
> 覆盖维度：容器运行时配置、镜像验证、网络隔离、进程隔离、资源限制、审计日志、SELinux、命名空间

---

## 规则

| 规则ID | 规则 | CWE | 检查方式 | 严重度 |
|--------|------|-----|---------|--------|
| CTR-01 | 容器以非root用户运行 | CWE-269 | 检查 `ctr run --rdzimage` 的 user / OCI spec `.process.user` | S1 |
| CTR-02 | 禁止特权容器（`--privileged`） | CWE-269 | 检查 `ctr`/`nerdctl` 是否启用 `--privileged` | S1 |
| CTR-03 | 启用镜像签名验证（content trust） | CWE-347 | 检查 containerd config `image` 层是否启用签名校验/校验策略 | S2 |
| CTR-04 | 容器网络隔离，使用命名网络命名空间 | CWE-284 | 检查 OCI spec `.linux.namespaces` 含 network namespace | S2 |
| CTR-05 | 设置资源限制(CPU/Memory/PIDs) | CWE-770 | 检查 OCI spec `.linux.resources` cgroup 配置 | S3 |
| CTR-06 | 启用审计日志（containerd + container） | CWE-778 | 检查 auditd 对 `containerd`/`runc` 的审计规则 | S3 |
| CTR-07 | 启用 SELinux/AppArmor 强制访问控制 | CWE-732 | 检查 OCI spec `.linux.maskedPaths`/`.linux.selinuxLabel` | S2 |
| CTR-08 | 容器命名空间隔离（PID/IPC/UTS/Network均独立） | CWE-269 | 检查 OCI spec `.linux.namespaces` 完整性 | S2 |

## 检查流程

1. 读取容器 OCI spec（`ctr containers info` 或 `/run/containerd/io.containerd.runtime.v2.task/`），确认 `.process.user.uid != 0`
2. 检查 `ctr run` / `nerdctl run` 调用是否含 `--privileged`；检查 `.linux.resources` 未赋予全部能力
3. 检查 containerd config.toml `[plugins."io.containerd.grpc.v1.cri"]` 或镜像层是否启用签名校验（cosign/notation/`image` 层校验策略）
4. 检查 OCI spec `.linux.namespaces`，确认含 `type: network` 独立网络命名空间（非 host）
5. 检查 `.linux.resources.memory`、`.linux.resources.cpu`、`.linux.resources.pids.limit` 是否均设置
6. 检查宿主 `/etc/audit/audit.rules`，确认存在对 `/usr/bin/containerd`、`/usr/bin/runc`、`/usr/local/bin/containerd` 的 `-w` 审计规则
7. 检查 `.linux.selinuxLabel` 或 `.annotations` 中 apparmor profile；确认 `.linux.maskedPaths` 覆盖 `/proc/*` 敏感路径
8. 检查 `.linux.namespaces` 完整性：PID/IPC/UTS/Network/User 命名空间均独立（非 host 共享）
9. 补充检查：containerd daemon 运行账号（非root）、config.toml 权限（644，owner root）、socket 权限

## 关联攻击面

- A6.1: 容器运行时 — 特权容器 + 共享命名空间直接导致逃逸（KL-5: escape/privileged-container）
- A6.1: 容器运行时 — 未验证镜像签名引入供应链投毒风险
- A6.2: K8s配置 — 共享网络命名空间使容器可直达宿主网络（KL-5: network/ssrf 关联）
- A4.4: 配置文件 — 缺失审计日志导致攻击行为无法溯源
