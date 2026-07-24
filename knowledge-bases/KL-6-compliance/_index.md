# KL-6 合规规则库 索引

> 来源：secdesign_spec.md 附录F
> 用途：Phase4 coverage-checker 覆盖率检查 + Phase5 security-test-generator 合规测试。

---

## 10个子文件说明

| 文件 | 规则组 | 说明 | 种子规则数 |
|------|--------|------|-----------|
| G1-credential.md | G1 凭证管理 | 硬编码密码、明文存储、加密、传输 | 4 |
| G2-crypto.md | G2 加密算法 | 禁用弱加密、AES模式 | 3 |
| G3-random.md | G3 随机数 | CSPRNG、安全随机数 | 2 |
| G4-password.md | G4 密码策略 | 长度、复杂度、历史 | 3 |
| G5-data-protection.md | G5 数据保护 | 日志脱敏、错误信息、传输加密 | 3 |
| G6-info-leak.md | G6 信息泄露 | 目录列表、版本信息、调试信息 | 3 |
| G7-session.md | G7 会话管理 | Cookie属性、会话固定、超时 | 3 |
| k8s-compliance.md | K8s合规 | Pod安全、RBAC、Secret、网络策略、资源限制 | 5 |
| docker-compliance.md | Docker合规 | 镜像安全、运行时配置 | 0（待填充） |
| containerd-compliance.md | Containerd合规 | 容器运行时安全配置 | 0（待填充） |

---

## 合规规则格式

每条合规规则遵循以下格式：

```markdown
| 规则ID | 规则 | CWE | 检查方式 |
|--------|------|-----|---------|
| G1-01 | 规则描述 | CWE-XXX | 检查方式说明 |
```

---

## 种子规则索引

### G1 凭证管理

| 规则ID | 规则 | CWE | 检查方式 |
|--------|------|-----|---------|
| G1-01 | 禁止硬编码密码 | CWE-798 | 源码搜索password=/passwd=/pwd= |
| G1-02 | 禁止明文存储密码 | CWE-259 | 数据库字段检查是否加密 |
| G1-03 | 密码必须使用不可逆加密 | CWE-261 | 检查是否使用bcrypt/scrypt/Argon2 |
| G1-04 | 凭证必须加密传输 | CWE-319 | 检查是否全链路TLS |

### G2 加密算法

| 规则ID | 规则 | CWE | 检查方式 |
|--------|------|-----|---------|
| G2-01 | 禁止使用DES/3DES/RC4 | CWE-327 | 源码搜索DES/RC4/Blowfish |
| G2-02 | 禁止使用MD5/SHA1用于安全场景 | CWE-328 | 源码搜索MD5/SHA1(密码/签名场景) |
| G2-03 | AES必须使用GCM/CBC+HMAC模式 | CWE-327 | 检查AES模式 |

### G3 随机数

| 规则ID | 规则 | CWE | 检查方式 |
|--------|------|-----|---------|
| G3-01 | 安全场景必须使用CSPRNG | CWE-330 | 源码搜索Math.random()/Random(安全场景) |
| G3-02 | Token/SessionID必须使用安全随机数 | CWE-338 | 检查生成方式 |

### G4 密码策略

| 规则ID | 规则 | CWE | 检查方式 |
|--------|------|-----|---------|
| G4-01 | 密码最小长度≥8字符 | CWE-521 | 配置检查 |
| G4-02 | 密码复杂度(至少两种字符类型) | CWE-521 | 配置检查 |
| G4-03 | 新密码不能与旧密码相同 | CWE-521 | 功能测试 |

### G5 数据保护

| 规则ID | 规则 | CWE | 检查方式 |
|--------|------|-----|---------|
| G5-01 | 日志不包含敏感信息 | CWE-532 | 日志文件搜索password/token/key |
| G5-02 | 错误响应不泄露内部信息 | CWE-209 | 触发500错误检查响应体 |
| G5-03 | 敏感数据传输加密 | CWE-319 | 抓包检查是否TLS |

### G6 信息泄露

| 规则ID | 规则 | CWE | 检查方式 |
|--------|------|-----|---------|
| G6-01 | 禁止目录列表 | CWE-538 | 访问目录URL检查是否返回列表 |
| G6-02 | 禁止版本信息泄露 | CWE-200 | HTTP响应头/错误页面检查 |
| G6-03 | 响应不包含调试信息 | CWE-497 | 生产环境检查堆栈跟踪 |

### G7 会话管理

| 规则ID | 规则 | CWE | 检查方式 |
|--------|------|-----|---------|
| G7-01 | Cookie设置HttpOnly+Secure+SameSite | CWE-1004 | 抓包检查Set-Cookie头 |
| G7-02 | 登录后重置SessionID | CWE-384 | 登录前后对比SessionID |
| G7-03 | 会话超时机制 | CWE-613 | 空闲超时+绝对超时测试 |

### 容器合规种子（K8s）

| 规则组 | 规则示例 | 映射攻击面 |
|--------|---------|-----------|
| Pod安全 | 禁止privileged/hostPath/hostNetwork/hostPID/hostIPC | A6.2 |
| RBAC | 禁止*/*授权，SA最小权限 | A6.2 |
| Secret管理 | Secret加密存储，etcd加密 | A6.2 |
| 网络策略 | 默认拒绝入站出站，仅开放必需 | A6.2 |
| 资源限制 | CPU/Memory requests+limits必须设置 | A6.2 |

---

> **注**：本文件为种子索引。10个子文件的完整内容由 Plan 2 填充。docker-compliance.md 和 containerd-compliance.md 尚无种子内容。
