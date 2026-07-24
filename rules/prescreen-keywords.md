# 预检关键词表（prescreen-keywords）

> 来源：secdesign_spec.md §3.4 + 附录A
> 用途：Phase0.5 security-prescreen 扫描需求 description 和 acceptance_criteria，匹配 KL-1 攻击面子类。

---

## 匹配规则

1. **大小写不敏感**：匹配时忽略中英文大小写差异（如 `api` 命中 `API`、`docker` 命中 `Docker`）。
2. **部分匹配**：关键词作为子串匹配需求文本（如 `上传` 命中 `文件上传功能`、`Upload` 命中 `FileUpload`）。
3. **中英文双语**：每个子类同时提供中文名词和英文关键词，任一命中即判定该子类命中。
4. **多关键词命中**：同一子类的任意一个关键词命中即判定该子类命中（OR 逻辑）。
5. **多子类命中**：需求可同时命中多个攻击面子类，全部记入 `matched_categories`。

---

## 32个攻击面子类完整匹配关键词表

| 攻击面子类 | 中文名词 | 英文关键词 |
|-----------|---------|-----------|
| A1.1 新增用户/账号 | 注册、账号、用户、认证、登录 | Signup、CreateUser、Register |
| A1.2 认证方式变更 | 密码、Token、MFA、OAuth、SAML、SSO、认证 | Auth、Login |
| A1.3 会话管理 | Session、Cookie、Token、JWT、会话 | SessionID |
| A1.4 凭证存储与传输 | 密码、口令、密钥、Token、凭证、AK/SK | Credential、Secret、Key |
| A2.1 新增API接口 | 接口、API、REST、RPC、gRPC、GraphQL、端点、路由 | Controller、Endpoint |
| A2.2 权限模型变更 | RBAC、ABAC、权限、角色、租户、隔离 | Permission、Role、Tenant |
| A2.3 资源所有权 | IDOR、越权、水平越权、垂直越权、所有权 | Owner、Authorization |
| A2.4 OpenAPI/外部接口 | OpenAPI、Swagger、外部接口、第三方接口、Webhook、回调 | — |
| A3.1 用户输入处理 | 表单、参数、Header、Cookie、输入 | Input、Form、Parameter |
| A3.2 文件上传/下载 | 上传、下载、附件、导入、导出 | Upload、File、Avatar、Import、Export |
| A3.3 数据导入/导出 | 批量导入、批量导出、Excel、CSV、数据迁移 | Batch、Bulk |
| A3.4 跨系统数据交换 | 消息队列、MQ、Kafka、回调、Webhook、事件 | Event、Notify |
| A4.1 新增数据库/表 | 数据库、表、RDS、MySQL、PostgreSQL、MongoDB | Database、Table |
| A4.2 敏感数据存储 | 加密、脱敏、分级、密钥、KMS | Encrypt、Mask、Classify |
| A4.3 个人数据(PII)处理 | 电话、邮箱、姓名、地址、身份证、PII、GDPR、隐私 | Privacy |
| A4.4 日志与审计记录 | 日志、审计、操作记录 | Log、Audit、Trace |
| A5.1 新增微服务/组件 | 微服务、容器、Docker、K8s、部署、服务 | Microservice、Service、Deploy |
| A5.2 新增端口/网络监听 | 端口、监听、Socket、网络 | Port、Listen、Bind |
| A5.3 配置文件/环境变量 | 配置、环境变量 | Config、ENV、Properties、YAML、ini |
| A5.4 证书/密钥管理 | 证书、CA、TLS、SSL、密钥 | Key、Certificate、x509 |
| A5.5 第三方依赖引入 | 三方件、依赖、库、NPM、Maven、Pip | Dependency、Library、Package |
| A6.1 容器/镜像变更 | Docker、镜像、构建 | Image、Container、Dockerfile |
| A6.2 K8s资源变更 | Pod、Deployment、Service、RBAC、NetworkPolicy、Namespace、Ingress | — |
| A6.3 云资源配置 | VPC、安全组、IAM、存储桶、OSS、S3、云资源 | Cloud |
| A6.4 运维命令/脚本 | 运维、脚本、Cron、定时任务、运维命令、脚本执行、sudo | Script |
| A7.1 新增界面/Web页面 | 页面、界面、Web、前端、UI | Page、View、HTML、JS |
| A7.2 客户端连接 | 数据库连接、SSH、代理、客户端 | Client、Proxy、Connection |
| A7.3 通信协议与加密 | HTTPS、TLS、SSL、加密传输、通信、通信加密 | Protocol |
| A7.4 前端安全 | CSP、CORS、X-Frame-Options、前端安全、点击劫持 | — |
| A8.1 高危操作 | 删除、重置、修改密码、二次认证、二次授权、敏感操作 | Dangerous |
| A8.2 业务流程绕过 | 流程、步骤、状态机、审批 | Workflow、State、Bypass |
| A8.3 计费/配额/限流 | 计费、配额、限流 | Rate Limit、Quota、Billing、Charge |
| A8.4 竞态条件/幂等性 | 并发、竞态、幂等 | Race Condition、Idempotent、Concurrent |

---

## 威胁数估算算法

命中子类后，根据每个子类的 STRIDE 适用数估算威胁总数：

```
estimated_threat_count = Σ(每个 matched_category 的 STRIDE 适用数)
范围表示：取 ±20% 浮动

示例：命中 A3.2(T,R,I,D,E=5) + A2.1(S,T,R,I,D,E=6) + A4.2(T,I,E=3) = 14
范围：14 × 0.8 = 11, 14 × 1.2 = 17 → "11-17"

阈值判定：
- ≤30：proceed（正常继续）
- >30：complex（建议拆分需求）
```

各子类 STRIDE 适用数速查（用于估算）：

| 子类 | S | T | R | I | D | E | 合计 |
|------|---|---|---|---|---|---|------|
| A1.1 | ✓ | | ✓ | ✓ | ✓ | ✓ | 5 |
| A1.2 | ✓ | ✓ | | ✓ | ✓ | ✓ | 5 |
| A1.3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 6 |
| A1.4 | ✓ | ✓ | | ✓ | | ✓ | 4 |
| A2.1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 6 |
| A2.2 | ✓ | | | ✓ | | ✓ | 3 |
| A2.3 | ✓ | | | ✓ | | ✓ | 3 |
| A2.4 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 6 |
| A3.1 | | ✓ | | ✓ | ✓ | ✓ | 4 |
| A3.2 | | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| A3.3 | | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| A3.4 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 6 |
| A4.1 | ✓ | ✓ | | ✓ | | ✓ | 4 |
| A4.2 | | ✓ | | ✓ | | ✓ | 3 |
| A4.3 | ✓ | | | ✓ | | | 2 |
| A4.4 | | ✓ | ✓ | ✓ | | | 3 |
| A5.1 | ✓ | ✓ | | ✓ | ✓ | ✓ | 5 |
| A5.2 | ✓ | | | ✓ | ✓ | | 3 |
| A5.3 | | ✓ | | ✓ | | ✓ | 3 |
| A5.4 | ✓ | ✓ | | ✓ | | ✓ | 4 |
| A5.5 | ✓ | ✓ | | ✓ | ✓ | ✓ | 5 |
| A6.1 | ✓ | ✓ | | ✓ | ✓ | ✓ | 5 |
| A6.2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 6 |
| A6.3 | ✓ | ✓ | | ✓ | ✓ | ✓ | 5 |
| A6.4 | ✓ | ✓ | ✓ | ✓ | | ✓ | 5 |
| A7.1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 6 |
| A7.2 | ✓ | ✓ | | ✓ | | ✓ | 4 |
| A7.3 | ✓ | ✓ | | ✓ | ✓ | | 4 |
| A7.4 | | ✓ | | ✓ | ✓ | | 3 |
| A8.1 | ✓ | ✓ | ✓ | ✓ | | ✓ | 5 |
| A8.2 | | ✓ | | ✓ | ✓ | ✓ | 4 |
| A8.3 | | | | | ✓ | ✓ | 2 |
| A8.4 | | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
