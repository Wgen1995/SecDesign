# Docker 合规

> 来源：CIS Docker Benchmark v1.6.0（知识补充）
> 用途：Phase4 覆盖率检查 + Phase5 容器合规测试（Docker维度）
> 覆盖维度：镜像安全、运行时安全、网络隔离、资源限制、文件系统、能力管理、SELinux/AppArmor、审计

---

## 规则

| 规则ID | 规则 | CWE | 检查方式 | 严重度 |
|--------|------|-----|---------|--------|
| DOCKER-01 | 容器以非root用户运行 | CWE-269 | 检查 `USER` 指令/`docker run --user` | S1 |
| DOCKER-02 | 禁止 `--privileged` 运行容器 | CWE-269 | 检查 `docker inspect` Privileged 字段 | S1 |
| DOCKER-03 | 最小化能力集，禁用危险能力 | CWE-269 | 检查 CapAdd/CapDrop（禁SETUID/SETGID/SYS_ADMIN等） | S2 |
| DOCKER-04 | 镜像使用可信基础镜像并扫描漏洞 | CWE-1104 | 检查基础镜像来源 + `docker scout/trivy` 扫描 | S2 |
| DOCKER-05 | 设置资源限制(CPU/Memory/PIDs) | CWE-770 | 检查 `--memory`/`--cpu-quota`/`--pids-limit` | S3 |
| DOCKER-06 | 容器文件系统只读 | CWE-732 | 检查 `--read-only` 与 `--tmpfs` 挂载 | S3 |
| DOCKER-07 | 禁止挂载Docker socket/敏感宿主路径 | CWE-269 | 检查 `Binds`/`Mounts` 中 `/var/run/docker.sock`、`/etc`、`/root` | S1 |
| DOCKER-08 | 启用 SELinux/AppArmor 强制访问控制 | CWE-732 | 检查 `--security-opt` apparmor/seccomp profile | S2 |
| DOCKER-09 | 网络隔离，禁止host网络模式 | CWE-284 | 检查 `NetworkMode`（禁host，用自定义bridge/overlay） | S2 |
| DOCKER-10 | Docker daemon审计日志启用 | CWE-778 | 检查 `/etc/audit/audit.rules` 中 dockerd 规则 | S3 |

## 检查流程

1. 对每个运行容器执行 `docker inspect <container>`，读取 `.Config.User`，确认非空且非 root（UID≠0）
2. 检查 `.HostConfig.Privileged`，确认所有容器均为 `false`
3. 检查 `.HostConfig.CapAdd` 与 `.HostAdd`，确认未添加危险能力（SETUID/SETGID/SYS_ADMIN/NET_ADMIN/SYS_PTRACE/CHOWN/FOWNER）；确认 `CapDrop` 至少 drop `ALL` 后按需 add
4. 检查 Dockerfile `FROM` 基础镜像来源是否为官方/可信仓库；运行 `trivy image`/`docker scout cves` 扫描镜像漏洞
5. 检查 `.HostConfig.Memory`、`.HostConfig.NanoCpus`/`CpuQuota`、`.HostConfig.PidsLimit` 是否均设置
6. 检查 `.HostConfig.ReadonlyRootfs` 为 `true`；需要写入的路径通过 `--tmpfs` 或命名卷挂载
7. 检查 `.Mounts`，确认未挂载 `/var/run/docker.sock`、`/etc`、`/root`、`/proc`、`/sys` 等敏感宿主路径
8. 检查 `.HostConfig.SecurityOpt`，确认包含 `apparmor=docker-default` 或自定义 profile，`seccomp` 未设为 `unconfined`
9. 检查 `.HostConfig.NetworkMode`，确认非 `host`；推荐自定义 bridge/overlay 网络隔离
10. 检查宿主 auditd 配置，确认存在 `-w /usr/bin/dockerd -p wa` 等审计规则；检查 dockerd `--log-level` 与日志驱动

## 关联攻击面

- A6.1: 容器运行时 — root + privileged + docker.sock 挂载直接导致容器逃逸（KL-5: escape/privileged-container）
- A6.1: 容器运行时 — 危险能力(SYS_ADMIN/SYS_PTRACE)突破容器边界
- A6.2: K8s配置 — Docker 网络host模式使容器与宿主共享网络栈（KL-5: network/ssrf 关联）
- A4.4: 配置文件 — 漏洞镜像引入供应链风险
