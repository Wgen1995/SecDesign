# KL-1 安全设计Checklist 索引

> 来源：secdesign_spec.md §2.2 + 附录A
> 用途：Phase1 attack-surface-identifier 扫描需求，识别命中的攻击面子类，展开KL-1检查点。

---

## 32个攻击面子类索引表

| 编号 | 名称 | 文件名 | 匹配关键词摘要 | STRIDE适用 |
|------|------|--------|--------------|-----------|
| A1.1 | 新增用户/账号 | A1.1-new-user.md | 注册、账号、用户、认证、登录 | S R I D E |
| A1.2 | 认证方式变更 | A1.2-auth-change.md | 密码、Token、MFA、OAuth、SAML、SSO | S T I D E |
| A1.3 | 会话管理 | A1.3-session-mgmt.md | Session、Cookie、Token、JWT、会话 | S T R I D E |
| A1.4 | 凭证存储与传输 | A1.4-credential-storage.md | 密码、口令、密钥、Token、凭证、AK/SK | S T I E |
| A2.1 | 新增API接口 | A2.1-new-api.md | 接口、API、REST、RPC、gRPC、GraphQL | S T R I D E |
| A2.2 | 权限模型变更 | A2.2-permission-model.md | RBAC、ABAC、权限、角色、租户、隔离 | S I E |
| A2.3 | 资源所有权 | A2.3-resource-ownership.md | IDOR、越权、水平越权、垂直越权、所有权 | S I E |
| A2.4 | OpenAPI/外部接口 | A2.4-external-api.md | OpenAPI、Swagger、外部接口、Webhook、回调 | S T R I D E |
| A3.1 | 用户输入处理 | A3.1-user-input.md | 表单、参数、Header、Cookie、输入 | T I D E |
| A3.2 | 文件上传/下载 | A3.2-file-upload-download.md | 上传、下载、附件、导入、导出 | T R I D E |
| A3.3 | 数据导入/导出 | A3.3-data-import-export.md | 批量导入、批量导出、Excel、CSV | T R I D E |
| A3.4 | 跨系统数据交换 | A3.4-cross-system-exchange.md | 消息队列、MQ、Kafka、回调、Webhook | S T R I D E |
| A4.1 | 新增数据库/表 | A4.1-new-database.md | 数据库、表、RDS、MySQL、PostgreSQL | S T I E |
| A4.2 | 敏感数据存储 | A4.2-sensitive-data-storage.md | 加密、脱敏、分级、密钥、KMS | T I E |
| A4.3 | 个人数据(PII)处理 | A4.3-personal-data.md | 电话、邮箱、姓名、地址、身份证、PII | S I |
| A4.4 | 日志与审计记录 | A4.4-log-audit.md | 日志、审计、Log、Audit、Trace | T R I |
| A5.1 | 新增微服务/组件 | A5.1-new-microservice.md | 微服务、容器、Docker、K8s、部署 | S T I D E |
| A5.2 | 新增端口/网络监听 | A5.2-new-port.md | 端口、监听、Socket、网络 | S I D |
| A5.3 | 配置文件/环境变量 | A5.3-config-file.md | 配置、Config、环境变量、ENV、YAML | T I E |
| A5.4 | 证书/密钥管理 | A5.4-certificate-key.md | 证书、CA、TLS、SSL、密钥、x509 | S T I E |
| A5.5 | 第三方依赖引入 | A5.5-third-party-dependency.md | 三方件、依赖、库、NPM、Maven、Pip | S T I D E |
| A6.1 | 容器/镜像变更 | A6.1-container-image.md | Docker、镜像、Image、Container、Dockerfile | S T I D E |
| A6.2 | K8s资源变更 | A6.2-k8s-resource.md | Pod、Deployment、Service、RBAC、NetworkPolicy | S T R I D E |
| A6.3 | 云资源配置 | A6.3-cloud-resource.md | VPC、安全组、IAM、存储桶、OSS、S3 | S T I D E |
| A6.4 | 运维命令/脚本 | A6.4-ops-command.md | 运维、脚本、Cron、定时任务、sudo | S T R I E |
| A7.1 | 新增界面/Web页面 | A7.1-new-ui.md | 页面、界面、Web、前端、UI | S T R I D E |
| A7.2 | 客户端连接 | A7.2-client-connection.md | 数据库连接、SSH、代理、客户端 | S T I E |
| A7.3 | 通信协议与加密 | A7.3-comm-encryption.md | HTTPS、TLS、SSL、加密传输、通信 | S T I D |
| A7.4 | 前端安全 | A7.4-frontend-security.md | CSP、CORS、X-Frame-Options、点击劫持 | T I D |
| A8.1 | 高危操作 | A8.1-high-risk-operation.md | 删除、重置、修改密码、二次认证、二次授权 | S T R I E |
| A8.2 | 业务流程绕过 | A8.2-business-logic-bypass.md | 流程、步骤、状态机、审批 | T I E |
| A8.3 | 计费/配额/限流 | A8.3-billing-rate-limit.md | 计费、配额、限流、Rate Limit | D E |
| A8.4 | 竞态条件/幂等性 | A8.4-race-condition.md | 并发、竞态、幂等、Race Condition | T R I D E |

---

## KL-1文件统一格式

每个 KL-1 文件（如 `A1.1-new-user.md`）遵循以下格式：

```markdown
# A{x}.{y} {攻击面名称}

## 匹配关键词
关键词1、关键词2、Keyword1、Keyword2

## STRIDE适用
S/T/R/I/D/E（标记适用项）

## 安全检查点

### 子类1标题
- [ ] 检查点1（phase: design/code/test/deploy）
- [ ] 检查点2（phase: ...）

### 子类2标题
- [ ] 检查点3
...

## 关联知识层
- KL-3: 对应的OWASP条目
- KL-5: 对应的攻击模式
- KL-6: 对应的合规规则
```

---

## 攻击面分类总览（8大类）

| 大类 | 编号范围 | 子类数 |
|------|---------|--------|
| A1 身份与认证 | A1.1-A1.4 | 4 |
| A2 授权与访问控制 | A2.1-A2.4 | 4 |
| A3 数据流与输入 | A3.1-A3.4 | 4 |
| A4 数据存储与保护 | A4.1-A4.4 | 4 |
| A5 基础设施与配置 | A5.1-A5.5 | 5 |
| A6 运行时环境 | A6.1-A6.4 | 4 |
| A7 客户端与传输 | A7.1-A7.4 | 4 |
| A8 业务逻辑 | A8.1-A8.4 | 4 |

---

> **注**：本文件为种子索引。32个 KL-1 文件的完整检查点内容由 Plan 2 从附录A逐个填充。
