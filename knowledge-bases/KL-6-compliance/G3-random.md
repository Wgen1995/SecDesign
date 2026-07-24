# G3 随机数

> 来源：secdesign_spec.md 附录F
> 用途：Phase4 覆盖率检查 + Phase5 合规测试（随机数安全性维度）

---

## 规则

| 规则ID | 规则 | CWE | 检查方式 | 严重度 |
|--------|------|-----|---------|--------|
| G3-01 | 安全场景必须使用CSPRNG | CWE-330 | 源码搜索Math.random()/Random(安全场景) | S2 |
| G3-02 | Token/SessionID必须使用安全随机数 | CWE-338 | 检查生成方式 | S1 |

## 检查流程

1. 全局搜索 `Math.random()`、`java.util.Random`、`Math/rand`、`random.random()` 等非安全随机源
2. 确认上述调用是否出现在令牌生成、会话ID、密码重置token、CSRF token 等安全场景
3. 审查 Token/SessionID 生成逻辑，确认使用 `SecureRandom`/`os.urandom`/`crypto.randomBytes` 等CSPRNG
4. 检查随机数熵源是否充足（避免固定种子/可预测种子）
5. 验证生成的 Token 长度≥128位，且具备足够命名空间避免碰撞

## 关联攻击面

- A1.3: 会话管理 — 可预测 SessionID 导致会话劫持
- A1.4: 凭证存储 — 可预测的密码重置 token 导致账号接管
- A2.1: API入口 — 可预测的 API token 导致越权访问
