# secdesign — 安全测试设计框架 设计规格文档

> 版本: 1.1 | 日期: 2026-07-23 | 状态: 设计阶段（已审阅改进）

---

## 0. SKILL.md 入口编排器

### 0.1 套件根定位

本套件用相对套件根的路径引用知识库与规则库。

LLM 在每个子 Phase 第一次 Read 任何相对引用前必先用 Glob 工具定位套件根：

```
Glob pattern: **/secdesign/SKILL.md
```

第一个命中路径的父目录就是套件根。所有后续 Read 把套件根绝对路径前缀拼到原引用前。

### 0.2 参数收集

从 $ARGUMENTS 提取 requirement_id、requirement_name、mode、reviewer、scope、format、force。
如果未提供 requirement_id，向用户询问。

### 0.3 初始化工作目录

创建 `.secdesign_output/{requirement_id}/` 完整目录结构（见 §7 输出标准）。
初始化 security_graph.json、progress.json、audit_log.json。

### 0.4 调度 Phase 子 skill

按顺序调度9个 Phase，使用 Task 工具调用对应子 skill：

1. Phase0: requirement-provider — 需求获取
2. Phase0.5: security-prescreen — 需求安全预检
3. Phase1: attack-surface-identifier — 攻击面识别
4. Phase2: threat-mapper — 威胁映射
5. Phase3: security-spec-generator — 安全规格生成
6. Phase4: coverage-checker — 覆盖率检查
7. Phase5: security-test-generator — 安全测试用例生成
8. Phase6: security-review — 安全评审
9. Phase7: security-report-publisher — 安全报告+处置跟踪

每个 Phase 完成后：校验 MUST 输出文件是否存在 → 更新 progress.json。

### 0.5 汇总模板

```
安全测试设计完成！

需求: {requirement_id} "{requirement_name}"
模式: {mode} | 签核人: {reviewer} | 签核点: Gate-1{verdict} Gate-2{verdict} Gate-3{verdict}

攻击面: {n}个 | 威胁: {n}个 | 检查点: {n}个 | 测试用例: {n}个
覆盖率: 攻击面{p}% 威胁{p}% STRIDE{p}%
威胁分布: S1:{n} S2:{n} S3:{n} S4:{n}
质量问题: 自动返工{n}次 | 人工返工{n}次

输出目录: .secdesign_output/{requirement_id}/
产物: MD / JSON / CSV / Excel / SARIF / 追溯图(graph.html)
审计日志: .secdesign_output/{requirement_id}/json_file/audit_log.json
```

### 0.6 红线

- 不编造需求中没有的攻击面
- 不跳过质量门控
- 不并行写入 security_graph.json
- 每个 Phase 完成后必须校验 MUST 输出
- 返工不超过2次（自动），人工返工单独计数
- 不修改原始需求内容
- DREAD评分/覆盖率检查必须附理由
- 不阻塞用户强制继续（--force）

---

## 1. 项目定位

### 1.1 一句话描述

输入需求编号，自动完成 需求获取→安全预检→攻击面识别→威胁建模→安全规格→覆盖率检查→安全测试用例→评审→报告，产出可追溯的安全测试设计全链闭环。

### 1.2 核心价值

- **防漏**：每个攻击面必须有检测结果，不允许⬜未覆盖
- **可追溯**：漏洞→威胁→攻击面→需求全链可查（知识图谱）
- **标准化**：检查点来自行业标准(OWASP/CWE/STRIDE)，不靠LLM感觉判定
- **可进化**：攻击模式库支持社区贡献和自动沉淀

### 1.3 不做的事（边界）

- 不做白盒代码审计（其他工具的职责）
- 不做渗透测试执行（其他工具的职责）
- 不做合规扫描执行（其他工具的职责）
- 只做 **需求→攻击面→威胁→检查点→安全测试用例** 这一链

### 1.4 与相关项目的关系

```
secdesign (本项目)          白盒审计工具            渗透测试工具
需求→安全测试用例             代码→漏洞发现            渗透测试执行
       │                        │                      │
       └──安全规格──▶ scope参数 ──┘                      │
       └──安全测试用例──▶ 验证清单 ──────────────────────┘
```

secdesign 的输出可以驱动下游白盒审计工具的审计范围和安全测试的验证清单。

### 1.5 目标用户

| 角色 | 使用场景 | 主要消费产物 |
|------|---------|-------------|
| 安全设计工程师/SDL工程师 | 需求阶段做威胁建模，驱动安全设计 | 安全规格(威胁模型+检查点) |
| 安全测试工程师 | 从需求生成安全测试用例，执行验证 | 安全测试用例(MD/JSON) |
| 渗透测试工程师 | 用测试用例作为渗透范围和验证清单 | 测试用例+攻击模式库(KL-5) |
| 开发人员风险自测 | 编码前看检查点，编码后自测 | Excel检查点清单(处置跟踪表) |
| 项目经理 | 跟踪安全风险修复进度 | Excel处置跟踪表 |
| CI/CD Pipeline | 自动化安全门控 | SARIF(机器可读发现) |

### 1.6 .gitignore 指引

```
.secdesign-data/       # 需求原始数据（含敏感信息）
.secdesign_output/     # 生成产物（按需选择是否提交）
```

---

## 2. 安全知识全景

### 2.1 三层映射体系

安全分析的核心逻辑是三层映射：

```
攻击面(A) —STRIDE—▶ 威胁(T) —知识层—▶ 检查点(C)
(入口)              (可能遭遇什么)      (怎么检查/怎么修)
```

- **攻击面**：攻击者能接触到什么（从需求变更类型出发）
- **威胁**：每个攻击面可能遭遇什么（STRIDE六类威胁分类）
- **检查点**：怎么检查、怎么修（来自行业标准的知识层）

### 2.2 攻击面分类（第一层）

按**需求变更类型**组织，而非按漏洞类型组织。安全工程师的思维是"攻击者能接触到什么"。

```
A1 身份与认证
  A1.1 新增用户/账号
  A1.2 认证方式变更(密码/Token/MFA/OAuth/SAML)
  A1.3 会话管理
  A1.4 凭证存储与传输

A2 授权与访问控制
  A2.1 新增API接口(REST/RPC/gRPC/GraphQL)
  A2.2 权限模型变更(RBAC/ABAC/租户隔离)
  A2.3 资源所有权(IDOR/水平越权/垂直越权)
  A2.4 OpenAPI/外部接口

A3 数据流与输入
  A3.1 用户输入处理(表单/参数/Header/Cookie)
  A3.2 文件上传/下载
  A3.3 数据导入/导出(批量操作)
  A3.4 跨系统数据交换(消息队列/回调/Webhook)

A4 数据存储与保护
  A4.1 新增数据库/表
  A4.2 敏感数据存储(加密/脱敏/分级)
  A4.3 个人数据(PII)处理
  A4.4 日志与审计记录

A5 基础设施与配置
  A5.1 新增微服务/组件
  A5.2 新增端口/网络监听
  A5.3 配置文件/环境变量
  A5.4 证书/密钥管理
  A5.5 第三方依赖引入

A6 运行时环境
  A6.1 容器/镜像变更
  A6.2 K8s资源变更(Deployment/Service/RBAC/NetworkPolicy)
  A6.3 云资源配置(VPC/安全组/IAM策略/存储桶)
  A6.4 运维命令/脚本

A7 客户端与传输
  A7.1 新增界面/Web页面
  A7.2 客户端连接(数据库连接/SSH/代理)
  A7.3 通信协议与加密
  A7.4 前端安全(CSP/CORS/X-Frame-Options)

A8 业务逻辑
  A8.1 高危操作(二次认证/二次授权)
  A8.2 业务流程绕过
  A8.3 计费/配额/限流
  A8.4 竞态条件/幂等性
```

### 2.3 STRIDE威胁映射（第二层）

对每个攻击面子类，映射适用的STRIDE威胁类型：

| 攻击面子类 | S仿冒 | T篡改 | R抵赖 | I泄露 | D拒绝 | E提权 |
|-----------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| A1.1 新增用户 | ✓ | | ✓ | ✓ | ✓ | ✓ |
| A1.2 认证方式 | ✓ | ✓ | | ✓ | ✓ | ✓ |
| A1.3 会话管理 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A1.4 凭证存储 | ✓ | ✓ | | ✓ | | ✓ |
| A2.1 新增API | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A2.2 权限模型 | ✓ | | | ✓ | | ✓ |
| A2.3 资源所有权 | ✓ | | | ✓ | | ✓ |
| A2.4 外部接口 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A3.1 用户输入 | | ✓ | | ✓ | ✓ | ✓ |
| A3.2 文件上传下载 | | ✓ | ✓ | ✓ | ✓ | ✓ |
| A3.3 数据导入导出 | | ✓ | ✓ | ✓ | ✓ | ✓ |
| A3.4 跨系统交换 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A4.1 新增数据库 | ✓ | ✓ | | ✓ | | ✓ |
| A4.2 敏感数据存储 | | ✓ | | ✓ | | ✓ |
| A4.3 个人数据 | ✓ | | | ✓ | | |
| A4.4 日志审计 | | ✓ | ✓ | ✓ | | |
| A5.1 新增微服务 | ✓ | ✓ | | ✓ | ✓ | ✓ |
| A5.2 新增端口 | ✓ | | | ✓ | ✓ | |
| A5.3 配置文件 | | ✓ | | ✓ | | ✓ |
| A5.4 证书密钥 | ✓ | ✓ | | ✓ | | ✓ |
| A5.5 三方依赖 | ✓ | ✓ | | ✓ | ✓ | ✓ |
| A6.1 容器镜像 | ✓ | ✓ | | ✓ | ✓ | ✓ |
| A6.2 K8s资源 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A6.3 云资源 | ✓ | ✓ | | ✓ | ✓ | ✓ |
| A6.4 运维命令 | ✓ | ✓ | ✓ | ✓ | | ✓ |
| A7.1 新增界面 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A7.2 客户端连接 | ✓ | ✓ | | ✓ | | ✓ |
| A7.3 通信加密 | ✓ | ✓ | | ✓ | ✓ | |
| A7.4 前端安全 | | ✓ | | ✓ | ✓ | |
| A8.1 高危操作 | ✓ | ✓ | ✓ | ✓ | | ✓ |
| A8.2 业务流程 | | ✓ | | ✓ | ✓ | ✓ |
| A8.3 计费限流 | | | | | ✓ | ✓ |
| A8.4 竞态条件 | | ✓ | ✓ | ✓ | ✓ | ✓ |

### 2.4 检查点知识层（第三层）

7个可插拔的知识层，每个对应一个标准或规则库：

| 知识层 | 名称 | 来源 | 条目数 | 用途 |
|--------|------|------|--------|------|
| KL-1 | 安全设计Checklist | 行业安全设计实践 | ~150条 | Phase1 攻击面识别时做需求扫描 |
| KL-2 | STRIDE威胁模板 | 微软SDL + STRIDE标准 | ~112条 | Phase2 威胁建模时做STRIDE分析 |
| KL-3 | OWASP标准簇 | OWASP Top10 + ASVS + API Security Top10 | ~300条 | Phase3 安全规格生成时做检查点映射 |
| KL-4 | CWE弱点映射 | CWE Top25 + SANS Top25 | ~50条 | Phase5 测试用例生成时做弱点-测试映射 |
| KL-5 | 攻击模式库 | OWASP攻击模式 + 云原生攻击模式 | ~88条 | Phase2 威胁细化 + Phase5 测试设计 |
| KL-6 | 合规规则库 | 凭证/加密/随机数/密码/数据保护/信息泄露/会话管理 + 容器合规 | ~300条 | Phase4 覆盖率检查 + Phase5 合规测试 |
| KL-7 | 运行时安全检查 | OWASP WSTG + ATT&CK容器/云矩阵 | ~130条 | Phase5 渗透测试用例 + Phase6 攻击链验证 |

### 2.5 三层映射示例

```
A3.2 文件上传/下载
  ├─ T:文件内容注入
  │    ├─ KL-5: injection/xxe 攻击模式
  │    ├─ KL-4: CWE-434 不受限制的文件上传
  │    └─ KL-3: ASVS V12.1 文件上传验证
  ├─ T:文件名路径穿越
  │    ├─ KL-5: authz/path-traversal 攻击模式
  │    ├─ KL-4: CWE-22 路径穿越
  │    └─ KL-3: ASVS V12.2 文件名校验
  ├─ I:目录遍历读取
  │    ├─ KL-4: CWE-538 文件和目录信息暴露
  │    └─ KL-3: ASVS V1.1 访问控制
  ├─ D:大文件DoS
  │    ├─ KL-4: CWE-400 不受控制的资源消耗
  │    └─ KL-3: API4:2023 无限制资源消耗
  └─ E:上传脚本执行提权
       ├─ KL-5: injection/code-injection 攻击模式
       ├─ KL-4: CWE-94 代码注入
       └─ KL-3: ASVS V12.1 上传文件不可执行

A6.2 K8s资源变更
  ├─ S:伪造ServiceAccount身份
  │    ├─ KL-5: k8s-sa-exploit 攻击模式
  │    └─ KL-6: K8s G8.2 RBAC配置
  ├─ T:篡改ConfigMap/Secret
  │    ├─ KL-5: configmap-data-exposure 攻击模式
  │    └─ KL-6: K8s G8.1 Secret管理
  ├─ I:Secret明文暴露/etcd数据泄露
  │    ├─ KL-5: secret-exfil / etcd-data-exposure 攻击模式
  │    └─ KL-6: K8s G8.1 Secret加密
  ├─ D:资源请求无限制
  │    ├─ KL-5: resource-abuse / fork-bomb 攻击模式
  │    └─ KL-6: K8s G7.1 Pod安全
  └─ E:RBAC过度授权→容器逃逸
       ├─ KL-5: k8s-rbac-abuse / privileged-container-escape 攻击模式
       ├─ KL-4: CWE-269 不当权限管理
       └─ KL-6: K8s G7.1 Pod安全 + G8.2 RBAC
```

### 2.6 需求粒度自适应

不同粒度的需求命中不同知识层：

| 需求粒度 | scope值 | 命中攻击面 | 必须加载 | 按需加载 |
|---------|---------|-----------|---------|---------|
| 接口级 | interface | 1-2个子类 | KL-1, KL-3, KL-5 | KL-4, KL-7 |
| 功能级 | function | 3-5个子类 | KL-1~5 | KL-6, KL-7 |
| 模块级 | module | 5-10个子类 | KL-1~6 | KL-7 |
| 系统级 | system | 10+个子类 | KL-1~7 | — |

### 2.7 知识层进化机制

```
发现新攻击 → 写攻击模式(SKILL.md格式)
          → 映射到攻击面(Ax.x)
          → 映射STRIDE类型
          → 映射CWE/OWASP编号
          → 写入 KL-5 对应目录
          → 更新 _index.md

新标准发布 → 增加知识层目录(如 KL-8)
           → 更新 _index.md 总索引
           → 在映射表中追加条目
```

---

## 3. Pipeline 设计

### 3.1 总览

```
Phase0   requirement-provider       需求获取
Phase0.5 security-prescreen        需求安全预检
Phase1   attack-surface-identifier 攻击面识别
Phase2   threat-mapper              威胁映射
Phase3   security-spec-generator    安全规格生成
Phase4   coverage-checker           覆盖率检查
Phase5   security-test-generator    安全测试用例生成
Phase6   security-review            安全评审
Phase7   security-report-publisher  安全报告+处置跟踪
```

### 3.2 参数格式

| 名称 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| requirement_id | string | 是 | — | 需求唯一标识 |
| requirement_name | string | 否 | — | 需求名称（显示用） |
| mode | string | 否 | auto | auto / interactive |
| reviewer | string | 否 | env SECDESIGN_REVIEWER | 交互模式签核人 |
| scope | string | 否 | auto | interface / function / module / system / auto |
| format | string | 否 | all | md / json / csv / excel / graph / sarif / all / 组合 |
| force | boolean | 否 | false | 跳过 Phase0.5 预门 |

### 3.3 Phase0: requirement-provider

**功能**：根据需求编号获取需求详情和设计文档路径。

**接口合约**（适配器模式，可替换）：

```
输入: requirement_id (string)
输出: JSON {
  requirement_id,          // 必需
  requirement_name,        // 必需
  description,             // 必需，原始需求文本
  acceptance_criteria,     // 可选，验收标准
  scope,                   // 可选，需求粒度(interface/function/module/system)
  priority,                // 可选，优先级
  design_docs: [{          // 可选，设计文档列表
    name,                  // 文档名称
    path,                  // 文档路径（可访问）
    type                   // docx / pdf / md / xlsx / openapi
  }],
  custom_fields: {}        // 可选，自定义字段
}
```

**默认实现**：读取本地 JSON 文件 `.secdesign-data/{requirement_id}.json`，校验必需字段。

**MUST 输出**：
- `requirement_context/requirement_info.json`
- `json_file/security_graph.json`（含 requirement 节点）

### 3.4 Phase0.5: security-prescreen

**功能**：判定需求是否有安全面，判定粒度，选择知识层。

**输入**：`requirement_context/requirement_info.json`

**处理流程**：

1. 扫描 description 和 acceptance_criteria 中的安全关键词
2. 匹配 KL-1 的关键词索引
3. 判定需求粒度（scope 字段优先；缺失时根据描述复杂度自动判定）
4. 判定是否有安全面（无则快速通过）
5. 估算威胁数量（基于攻击面×STRIDE适用数）

**威胁数估算算法**：

```
estimated_threat_count = Σ(每个 matched_category 的 STRIDE 适用数)
范围表示：取 ±20% 浮动

示例：命中 A3.2(T,I,D,E=4) + A2.1(S,T,R,I,D,E=6) + A4.2(T,I,E=3) = 13
范围：13 × 0.8 = 10, 13 × 1.2 = 16 → "10-16"

阈值判定：
- ≤30：proceed（正常继续）
- >30：complex（建议拆分需求）
```

**关键词匹配规则**（部分示例，完整规则在 `rules/prescreen-keywords.md`）：

| 攻击面子类 | 匹配关键词 |
|-----------|-----------|
| A1.1 新增用户 | 注册、账号、用户、认证、登录、Signup、CreateUser |
| A1.4 凭证存储 | 密码、口令、密钥、Token、凭证、AK/SK、credential |
| A2.1 新增API | 接口、API、REST、RPC、端点、路由、Controller |
| A3.2 文件上传下载 | 上传、下载、附件、导入、导出、Upload、File |
| A5.1 新增微服务 | 微服务、容器、Docker、K8s、部署 |
| A6.2 K8s资源 | Pod、Deployment、Service、RBAC、NetworkPolicy |
| A8.1 高危操作 | 删除、重置、修改密码、二次认证、二次授权 |

**粒度自动判定规则**：

| 条件 | 判定粒度 |
|------|---------|
| 描述提及单个API或接口 | interface |
| 描述提及1-2个功能点 | function |
| 描述提及多个功能模块或3+功能点 | module |
| 描述提及架构变更/迁移/整体系统 | system |

**输出**：`requirement_context/security_prescreen.json`

```json
{
  "requirement_id": "REQ-001",
  "scope": "function",
  "has_security_surface": true,
  "matched_categories": ["A3.2", "A2.1", "A4.2"],
  "estimated_threat_count": "5-15",
  "recommended_knowledge_layers": ["KL-1", "KL-3", "KL-5"],
  "verdict": "proceed",
  "verdict_reason": "命中3个攻击面，预计5-15个威胁，建议加载KL-1/3/5"
}
```

**门控规则**：

| 条件 | verdict | 后续动作 |
|------|---------|---------|
| has_security_surface=false | skip | 跳过Phase1-2，Phase3标记"无安全面" |
| scope=system 且无design_docs | conditional | 提示补充架构文档，询问继续或暂停 |
| estimated_threat_count>30 | complex | 建议拆分需求，询问继续或拆分 |
| force=true | proceed | 跳过预检直接进入Phase1 |

**MUST 输出**：
- `requirement_context/security_prescreen.json`
- `json_file/security_graph.json`（含 security_assessment 节点）

### 3.5 Phase1: attack-surface-identifier

**功能**：扫描需求，识别命中的攻击面子类，展开KL-1检查点。

**输入**：
- `requirement_context/requirement_info.json`
- `requirement_context/security_prescreen.json`

**知识库**：`knowledge-bases/KL-1-checklist/`（每个攻击面子类一个文件）

**处理流程**：

1. 读取 security_prescreen.json 中的 matched_categories
2. 对每个命中的子类，读取对应的 KL-1 文件，展开检查点
3. 如果有 design_docs，执行文档处理流程（见下方），做补充匹配
4. 汇总所有攻击面和检查点

**设计文档处理流程**（有 design_docs 时执行）：

1. 文档转换：docx/pdf/xlsx → Markdown（保留标题层级）
2. 文档分块：按 H2/H3 标题切分，单块上限 800 字，每块提取 section_path + keywords
3. 补充匹配：用分块关键词扫描 KL-1 索引，识别 prescreen 未命中的攻击面
4. 输出 `design_doc_markdown/*.md` + `doc_chunks/doc_chunks.json`
5. 知识图谱追加 doc_chunk 节点 + traces_to 边（attack_surface → doc_chunk）

**doc_chunks.json 格式**：

```json
{
  "chunks": [
    {
      "id": "CHK-001",
      "source_doc": "auth-design.docx",
      "section_path": "3.2 认证流程",
      "content": "用户通过账号密码登录，支持OAuth2.0...",
      "keywords": ["认证", "登录", "OAuth", "密码"]
    }
  ]
}
```

**降级策略**：无设计文档时跳过文档处理，在安全规格风险章节标注"无设计文档追溯"

**KL-1文件格式**（以 A3.2 文件上传下载为例）：

```markdown
# A3.2 文件上传/下载

## 匹配关键词
上传、下载、附件、导入、导出、Upload、File、Avatar、Import、Export

## STRIDE适用
T(篡改)、I(泄露)、D(拒绝)、E(提权)

## 安全检查点

### 文件上传
- [ ] 文件类型校验（前台+后台都必须校验）
- [ ] 文件名校验（前后台），防止跨目录攻击（../）
- [ ] 文件大小限制
- [ ] 文件内容检测（病毒/Webshell/XXE）
- [ ] 上传后重命名（不保留原始文件名）
- [ ] 上传目录不可执行（无执行权限）
- [ ] 使用公共上传组件
- [ ] 上传操作记录审计日志
- [ ] 越权防护（只能上传/下载自己的文件）
- [ ] 下载临时文件及时清理

### 文件下载
- [ ] 下载文件类型为Excel需CSV防护
- [ ] 下载文件类型为HTML需XSS防护
- [ ] 下载操作记录审计日志
- [ ] 下载权限控制（防止越权下载他人文件）
- [ ] 下载临时文件及时清理
```

**输出**：`attack_surfaces/attack_surfaces.json`

```json
{
  "requirement_id": "REQ-001",
  "surfaces": [
    {
      "id": "AS-001",
      "category": "A3.2",
      "name": "文件上传/下载",
      "match_reason": "需求描述包含'上传附件'",
      "match_source": "prescreen",
      "stride_applicable": ["T", "I", "D", "E"],
      "checklist_items": [
        {"id": "CL-001", "item": "文件类型校验（前台+后台）", "phase": "design"},
        {"id": "CL-002", "item": "文件名校验防跨目录", "phase": "code"},
        {"id": "CL-003", "item": "文件大小限制", "phase": "design"},
        {"id": "CL-004", "item": "文件内容检测", "phase": "test"},
        {"id": "CL-005", "item": "上传后重命名", "phase": "code"},
        {"id": "CL-006", "item": "上传目录不可执行", "phase": "deploy"}
      ]
    }
  ],
  "summary": {
    "total_surfaces": 3,
    "total_checklist_items": 16,
    "scope": "function"
  }
}
```

**MUST 输出**：
- `attack_surfaces/attack_surfaces.json`
- `json_file/security_graph.json`（含 attack_surface 节点 + has_surface 边）

### 3.6 Phase2: threat-mapper

**功能**：对每个攻击面逐个套STRIDE，映射到KL-5攻击模式，生成威胁列表。

**输入**：
- `attack_surfaces/attack_surfaces.json`
- `requirement_context/requirement_info.json`

**知识库**：`knowledge-bases/KL-2-stride/` + `knowledge-bases/KL-5-attack-patterns/`

**处理流程**：

1. 对每个攻击面，遍历其 stride_applicable 中的每个STRIDE类型
2. 对每个STRIDE类型，从KL-2读取对应的威胁模板
3. 根据攻击面上下文细化威胁描述
4. 从KL-5映射具体攻击模式（按攻击面子类索引）
5. 映射CWE/OWASP编号
6. 用DREAD评分法做风险评级

**DREAD评分**（每个维度 1-5 分连续标尺）：

| 维度 | 1分 | 2分 | 3分 | 4分 | 5分 |
|------|-----|-----|-----|-----|-----|
| Damage(损害) | 无影响 | 轻微影响 | 部分数据泄露 | 大量数据泄露 | 全量数据泄露/RCE |
| Reproducibility(可复现) | 极难复现 | 需特殊条件 | 有条件复现 | 多数情况可复现 | 每次必现 |
| Exploitability(可利用性) | 需高权限+0day | 需高权限 | 需普通权限 | 需低权限 | 无需认证即可利用 |
| Affected users(影响范围) | 无影响用户 | 少数用户 | 部分租户 | 多数租户 | 全部租户 |
| Discoverability(可发现性) | 极难发现 | 难以发现 | 审计可发现 | 易于发现 | 公开接口可发现 |

**严重度映射**：总分25分制 → S1(20-25) / S2(12-19) / S3(6-11) / S4(0-5)

**云环境多租户放大规则**：
- 如果威胁影响跨租户数据隔离（A2.2/A2.3相关），affected_users 自动升级为5
- 如果威胁涉及云元数据服务(169.254.169.254)或AK/SK泄露，damage 自动升级为5
- 如果scope=system，所有S3级威胁至少升级为S2

**输出**：`threats/threats.json`

```json
{
  "requirement_id": "REQ-001",
  "threats": [
    {
      "id": "T-001",
      "surface_id": "AS-001",
      "stride_type": "T",
      "threat_name": "文件内容注入(Webshell/XXE)",
      "description": "上传恶意文件到服务器，通过文件内容注入实现代码执行",
      "attack_patterns": [
        {"layer": "KL-5", "id": "injection/xxe", "name": "XXE注入"},
        {"layer": "KL-5", "id": "injection/code-injection", "name": "代码注入"}
      ],
      "cwe": ["CWE-434", "CWE-79"],
      "owasp": ["A03-Injection", "A04-Insecure Design"],
      "dread": {
        "damage": 5,
        "reproducibility": 4,
        "exploitability": 3,
        "affected_users": 3,
        "discoverability": 4
      },
      "dread_total": 19,
      "severity": "S2",
      "mitigation": "文件类型白名单+内容检测+存储目录不可执行+重命名"
    }
  ],
  "summary": {
    "total_threats": 8,
    "by_severity": {"S1": 0, "S2": 3, "S3": 4, "S4": 1},
    "by_stride": {"S": 1, "T": 2, "R": 1, "I": 2, "D": 1, "E": 1}
  }
}
```

**MUST 输出**：
- `threats/threats.json`
- `json_file/security_graph.json`（含 threat 节点 + has_threat 边）

### 3.7 Phase3: security-spec-generator

**功能**：将威胁映射到KL-3/KL-4/KL-6的检查点，生成安全规格文档。

**输入**：
- `threats/threats.json`
- `attack_surfaces/attack_surfaces.json`
- `requirement_context/requirement_info.json`

**知识库**：`knowledge-bases/KL-3-owasp/` + `knowledge-bases/KL-4-cwe/` + `knowledge-bases/KL-6-compliance/`

**安全规格模板**（6章节）：

```
第1章: 需求安全概述
  1.1 基本信息（需求编号/名称/粒度/优先级）
  1.2 需求描述（原样引用）
  1.3 攻击面摘要（命中几个攻击面，预估威胁数）

第2章: 攻击面分析
  2.1 每个攻击面
    - 描述
    - 数据流（用户→处理→存储→输出）
    - 信任边界

第3章: 威胁模型
  3.1 每个威胁
    - STRIDE分类
    - 攻击路径（Source→...→Sink）
    - DREAD风险评级
    - 修复建议
  3.2 威胁汇总表

第4章: 安全检查点
  4.1 设计时检查点（架构/数据流/认证/授权）
  4.2 编码时检查点（输入校验/加密/日志/错误处理）
  4.3 测试时检查点（每个威胁对应的验证项）

第5章: 合规映射
  5.1 OWASP映射（每个检查点对应的OWASP Top10/ASVS条款）
  5.2 CWE映射（每个威胁对应的CWE编号）
  5.3 合规映射（每个检查点对应的合规规则）

第6章: 风险处置建议
  6.1 按严重度排序的风险清单
  6.2 每个风险的处置建议（修复/补偿控制/接受）
  6.3 验收标准
```

**输出**：
- `security_spec/security_spec.md`
- `security_spec/security_spec.json`
- `json_file/security_graph.json`（含 security_check 节点 + mapped_by 边）

### 3.8 Phase4: coverage-checker

**功能**：检查攻击面×威胁×检查点的覆盖率是否达标。

**输入**：
- `security_spec/security_spec.json`
- `attack_surfaces/attack_surfaces.json`
- `threats/threats.json`

**知识库**：`rules/coverage-rules.md`

**覆盖率检查规则**：

| 规则ID | 检查维度 | 计算方式 | 阈值 | 不达标动作 | 执行时机 |
|--------|---------|---------|------|-----------|---------|
| CVR-01 | 攻击面覆盖率 | 有检查点的攻击面数 / 总攻击面数 | ≥90% | 返工Phase3补检查点 | Phase4 |
| CVR-02 | 威胁检查点覆盖率 | 有检查点的威胁数 / 总威胁数 | ≥90% | 返工Phase3补检查点 | Phase4 |
| CVR-03 | STRIDE覆盖率 | 每个攻击面已分析STRIDE数 / 适用STRIDE数 | ≥80%（系统级100%） | 返工Phase2补威胁 | Phase4 |
| CVR-04 | 五态检查 | 所有攻击面的状态 | 无⬜ | 返工对应Phase | Phase4 |
| CVR-05 | 威胁测试用例覆盖率 | 有测试用例的威胁数 / 总威胁数 | ≥90% | 返工Phase5补用例 | Phase5后(Phase6前) |

**五态标记**（分两个阶段判定）：

**Phase4 后（检查点维度）**：

| 标记 | 含义 | 判定条件 |
|------|------|---------|
| ✅ | 已覆盖 | 攻击面有检查点 |
| ❌ | 未覆盖 | 攻击面无检查点 |
| ❓ | 待确认 | 需求不明确，无法判定 |
| ⬜ | 未评估 | 尚未执行Phase4 |

**Phase5 后（测试用例维度，在Phase4状态基础上升级）**：

| 标记 | 含义 | 判定条件 |
|------|------|---------|
| ✅ | 完全覆盖 | 攻击面有检查点 且 威胁有测试用例 |
| ⚠️ | 部分覆盖 | 攻击面有检查点 但 威胁缺测试用例 |
| ❌ | 未覆盖 | 攻击面无检查点 |
| ❓ | 待确认 | 需求不明确 |
| ⬜ | 未评估 | Phase7要求清零 |

**自动返工机制**：
- 返工次数上限：2次
- 返工目标Phase由finding决定（CVR-01/CVR-04→Phase3, CVR-03→Phase2）
- 每次返工记录到 audit_log.json

**输出**：
- `coverage/coverage_report.md`
- `coverage/coverage_findings.json`
- `json_file/security_graph.json`（含 finding 节点 + checked_by 边）

### 3.9 Phase5: security-test-generator

**功能**：将安全检查点转化为可执行的安全测试用例。

**输入**：
- `security_spec/security_spec.json`
- `threats/threats.json`
- `attack_surfaces/attack_surfaces.json`

**知识库**：`knowledge-bases/KL-4-cwe/` + `knowledge-bases/KL-5-attack-patterns/` + `knowledge-bases/KL-7-runtime/`

**安全测试用例模板**：

```markdown
## UC-{攻击面代号}-{序号} {测试名称}

| 字段 | 值 |
|------|-----|
| 用例编号 | UC-UPLOAD-001 |
| 关联威胁 | T-001(文件内容注入) |
| 攻击面 | AS-001(文件上传/下载) |
| CWE | CWE-434 |
| OWASP | A03-Injection |
| 严重程度 | S2-High |
| 攻击者角色 | 已认证普通用户 |

### 前置条件
- 已创建普通用户账号user_a
- 文件上传功能已部署且可访问

### 攻击步骤
1. 以user_a身份登录系统
2. 进入文件上传页面
3. 构造恶意文件(如test.jsp含Webshell代码: <%Runtime.getRuntime().exec(request.getParameter("cmd"));%>)
4. 修改HTTP请求中Content-Type为image/jpeg
5. 上传恶意文件，观察服务端响应

### 预期结果（安全行为）
- 服务端拒绝上传，返回400/415
- 审计日志记录非法上传尝试（含用户、时间、文件类型）
- 上传目录不存在.jsp文件

### 验证方法
- 断言HTTP响应状态码 ∈ {400, 415}
- 检查上传目录: find /upload-dir -name "*.jsp" 返回空
- 检查审计日志: 包含"非法文件类型"关键字

### 清理步骤
- 删除测试账号user_a
- 清理审计日志中的测试记录
```

**测试用例分类**（对齐OWASP WSTG）：

| 类别 | 前缀 | 示例 |
|------|------|------|
| 认证测试 | UC-AUTH- | 暴力破解、会话固定、MFA绕过 |
| 授权测试 | UC-AC- | IDOR、水平越权、垂直越权 |
| 输入处理 | UC-INP- | SQL注入、XSS、命令注入、XXE |
| 文件处理 | UC-FILE- | 文件上传、路径穿越、XXE via文件 |
| 加密测试 | UC-CRYP- | 弱加密、证书校验、明文传输 |
| 配置测试 | UC-CONF- | 默认配置、开放管理接口、CORS |
| 日志审计 | UC-LOG- | 日志完整性、操作可追溯 |
| 业务逻辑 | UC-BUS- | 流程绕过、竞态条件、计费绕过 |
| 容器安全 | UC-CONT- | 特权容器、RBAC滥用、网络策略绕过 |

**输出**：
- `security_tests/security_tests.md`
- `security_tests/security_tests.json`
- `json_file/security_graph.json`（含 security_test 节点 + covers 边）

### 3.10 Phase6: security-review

**功能**：评审安全测试用例的可执行性、可利用性和误报风险。

**输入**：
- `security_tests/security_tests.json`
- `security_spec/security_spec.json`

**评审维度**：

| 维度 | 检查项 | 判定方式 |
|------|--------|---------|
| 可执行性 | 步骤可操作、预期可验证、清理完整 | 规则+LLM裁决 |
| 可利用性 | 威胁是否有可利用的攻击路径 | LLM裁决+攻击模式匹配 |
| 误报风险 | 测试用例是否可能产生误报 | LLM裁决 |
| 攻击链 | 多个中低危威胁是否可串联（scope≥function时） | LLM推理 |

**攻击链验证**（scope≥function时启用）：
- 识别可串联的多个威胁
- 构建攻击链（如：未授权访问→敏感信息泄露→命令注入）
- 生成攻击链测试用例
- **边界说明**：secdesign 的攻击链是设计时分析（纸面推导），不执行实际攻击。执行时验证由渗透测试工具（如 GenCPT）负责，secdesign 的输出作为渗透测试的输入

**输出**：
- `review/review_report.md`
- `json_file/security_graph.json`（含 finding 节点）

### 3.11 Phase7: security-report-publisher

**功能**：多格式输出安全报告和处置跟踪表。

**输入**：全部Phase产出

**输出格式**：

| 格式 | 文件 | 内容 | 消费者 |
|------|------|------|--------|
| Markdown | security_report.md | 安全规格+威胁模型+测试用例 | 安全工程师 |
| Excel | security_tests.xlsx | 安全检查点清单+风险处置跟踪表 | 项目经理/开发 |
| SARIF | security_findings.sarif | 机器可读的安全发现 | CI/CD |
| JSON | security_graph.json | 全链追溯图谱 | 自动化Pipeline |
| HTML | security_graph.html | 可视化知识图谱 | 管理层 |

**处置跟踪表**（Excel中）：

| 检查点ID | 检查点描述 | 严重度 | 状态 | 责任人 | 计划完成 | 实际完成 | 验证结果 |
|---------|-----------|--------|------|--------|---------|---------|---------|
| CL-001 | 文件类型校验 | S2 | ⬜待修复 | | | | |
| CL-004 | 文件内容检测 | S2 | ⬜待修复 | | | | |

**审计日志**：`json_file/audit_log.json`（与testdesign格式一致）

**SARIF 输出 Schema 映射**：

SARIF (Static Analysis Results Interchange Format) 是 OASIS 标准，用于 CI/CD 集成。

```json
{
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "secdesign",
          "version": "1.1",
          "informationUri": "https://github.com/.../secdesign"
        }
      },
      "results": [
        {
          "ruleId": "CWE-434",
          "level": "error",
          "message": {
            "text": "不受限制的文件上传 — 文件类型校验缺失"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "requirement/REQ-001"
                }
              },
              "logicalLocations": [
                {
                  "fullyQualifiedName": "A3.2/attack_surface"
                }
              ]
            }
          ],
          "properties": {
            "threat_id": "T-001",
            "stride_type": "T",
            "dread_severity": "S2",
            "owasp": "A03-Injection",
            "checklist_id": "CL-001"
          }
        }
      ],
      "taxonomies": [
        {
          "name": "CWE",
          "rules": [
            {
              "id": "CWE-434",
              "name": "Unrestricted Upload of File with Dangerous Type"
            }
          ]
        }
      ]
    }
  ]
}
```

**SARIF level 映射**：S1→error, S2→error, S3→warning, S4→note

---

## 4. 知识图谱 Schema

### 4.1 节点类型

| type | 含义 | 写入Phase | 必需字段 |
|------|------|-----------|---------|
| requirement | 需求 | Phase0 | id, name, description, scope |
| security_assessment | 安全预检评估 | Phase0.5 | id, verdict, matched_categories |
| attack_surface | 攻击面 | Phase1 | id, category, name, checklist_items |
| threat | 威胁 | Phase2 | id, surface_id, stride_type, severity |
| security_check | 安全检查点 | Phase3 | id, threat_id, layer, check_item |
| security_test | 安全测试用例 | Phase5 | id, threat_id, test_name, steps, source |
| finding | 覆盖率/评审发现 | Phase4/6 | id, target_id, dimension, verdict |

**source 字段**（security_test 节点）：

| source 值 | 含义 |
|-----------|------|
| threat_derived | 从威胁模型直接推导 |
| llm_inferred | LLM 基于安全经验补充 |
| rule_based | 基于合规规则(KL-6)或运行时检查(KL-7)补充 |

### 4.2 边类型

| type | 含义 | 从 | 到 | 写入Phase |
|------|------|----|----|-----------|
| has_surface | 需求有攻击面 | requirement | attack_surface | Phase1 |
| has_threat | 攻击面有威胁 | attack_surface | threat | Phase2 |
| traces_to | 检查点追溯到需求 | security_check | requirement | Phase3 |
| mapped_by | 威胁由知识层映射 | threat | security_check | Phase3 |
| covers | 测试用例覆盖威胁 | security_test | threat | Phase5 |
| checked_by | 发现由检查产生 | finding | security_check | Phase4/6 |
| published_as | 测试用例发布为格式 | security_test | publish_node | Phase7 |
| audited_by | 需求被人工签核 | requirement | gate | Phase7 |

### 4.3 五态标记

每个 attack_surface 节点必须有 state 字段：

| 值 | 含义 | 判定 |
|----|------|------|
| ✅ | 已覆盖 | 有检查点+有测试用例 |
| ⚠️ | 部分覆盖 | 有检查点+缺测试用例 |
| ❌ | 未覆盖 | 无检查点 |
| ❓ | 待确认 | 需求不明确 |
| ⬜ | 未评估 | Phase7要求清零 |

---

## 5. 共享规范

本节定义跨Phase共享的输出标准、门控规范、适配器合约和审计日志规范，对齐 testdesign 的 shared/ 四文件体系。实现时应将本节内容拆分为独立的 `skills/shared/` 文件。

### 5.1 输出标准规范（OUTPUT_STANDARD）

**MUST 输入/输出表**：

| Phase | MUST 输入 | MUST 输出 |
|-------|----------|----------|
| Phase0 | requirement_id | requirement_context/requirement_info.json + security_graph.json(含 requirement 节点) |
| Phase0.5 | requirement_info.json | requirement_context/security_prescreen.json + security_graph.json(含 security_assessment 节点) |
| Phase1 | requirement_info.json + security_prescreen.json | attack_surfaces/attack_surfaces.json + design_doc_markdown/*.md + doc_chunks/doc_chunks.json + security_graph.json(含 attack_surface + doc_chunk 节点) |
| Phase2 | attack_surfaces.json + requirement_info.json | threats/threats.json + security_graph.json(含 threat 节点 + has_threat 边) |
| Phase3 | threats.json + attack_surfaces.json + requirement_info.json | security_spec/security_spec.md + security_spec.json + security_graph.json(含 security_check 节点 + mapped_by 边 + traces_to 边) |
| Phase4 | security_spec.json + attack_surfaces.json + threats.json | coverage/coverage_report.md + coverage_findings.json + security_graph.json(含 finding 节点 + checked_by 边) |
| Phase5 | security_spec.json + threats.json + attack_surfaces.json | security_tests/security_tests.md + security_tests.json + security_graph.json(含 security_test 节点 + covers 边) |
| Phase6 | security_tests.json + security_spec.json | review/review_report.md + security_graph.json(含 finding 节点) |
| Phase7 | security_tests.json + security_graph.json + audit_log.json | report/security_report.md + report/security_tests.xlsx + report/security_findings.sarif + report/security_graph.html + security_graph.json(含 published_as + audited_by 边) + audit_log.json(归档) |

**并发写入协议**：
- security_graph.json 使用追加写入模式（读取→追加→写回）
- 每个 Phase 对 security_graph.json 的写入是独占的
- Phase4 覆盖率检查和 Phase6 评审如需并行，各自写独立 findings 分片文件，全部完成后串行汇总合并到 graph

**BATCH_THRESHOLD（分批阈值）**：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| BATCH_THRESHOLD | 20 | 超过此数量时触发自适应分批 |

| Phase | 触发条件 | 分批方式 |
|-------|---------|---------|
| Phase2 | 攻击面数 > BATCH_THRESHOLD | 按攻击面分组并行威胁映射 |
| Phase5 | 威胁数 > BATCH_THRESHOLD | 按攻击面分组生成测试用例，追加写入后合并 |

### 5.2 质量门控规范（QUALITY_GATES）

（已在 §6 质量门控规范中定义，此处补充阈值汇总表）

**门控阈值汇总**：

| 门控 | 位置 | 阈值 | 返工目标 | 最大自动返工 |
|------|------|------|---------|-------------|
| Phase0.5 预门 | Phase0.5 后 | has_security_surface=false→skip; scope=system无文档→conditional; threat>30→complex; force=true→proceed | Phase0（补需求） | 不限（人工决定） |
| Phase4 门控 | Phase4 后 | CVR-01≥90%, CVR-02≥90%, CVR-03≥80%(system 100%), CVR-04无⬜ | Phase2或Phase3 | 2 次 |
| CVR-05 门控 | Phase5 后 | CVR-05≥90% | Phase5 | 2 次 |
| Phase6 门控 | Phase6 后 | 可执行性≥70% | Phase5 | 2 次 |

### 5.3 适配器接口合约（ADAPTER_CONTRACT）

（已在 §9 适配器接口中定义，含环境变量规范和LLM模型要求）

### 5.4 审计日志规范（AUDIT_LOG_SPEC）

（已在 §11 审计日志中定义，含签核点完整定义和版本标记规则）
- 版本格式：v1 → v2 → v3 → ...（每次返工递增）
- security_spec.md：Phase3 每次返工 +1
- security_tests.json：Phase5 每次返工 +1
- progress.json 的 artifact_versions 记录当前版本
- audit_log.json 中每条 gate 记录的 artifact_version 记录被审阅时的版本

**闭环校验**：Phase7 要求所有 attack_surface 和 threat 节点状态非 ⬜。

---

## 6. 质量门控规范

### 6.1 Phase0.5 安全预检门控

| 条件 | verdict | 后续动作 |
|------|---------|---------|
| has_security_surface=false | skip | 跳过Phase1-2 |
| scope=system 且无design_docs | conditional | 提示补充文档 |
| estimated_threat_count>30 | complex | 建议拆分 |
| force=true | proceed | 跳过预检 |

### 6.2 Phase4 覆盖率门控

| 规则 | 阈值 | 不达标动作 |
|------|------|-----------|
| CVR-01 攻击面覆盖率 | ≥90% | 返工Phase3 |
| CVR-02 威胁检查点覆盖率 | ≥90% | 返工Phase3 |
| CVR-03 STRIDE覆盖率 | ≥80%(系统级100%) | 返工Phase2 |
| CVR-04 五态检查 | 无⬜ | 返工对应Phase |
| CVR-05 威胁测试用例覆盖率 | ≥90% | 返工Phase5 |

### 6.3 自动返工

- 上限：2次
- 返工目标Phase由finding决定
- 每次返工记录到audit_log.json
- 2次返工后仍不达标：输出警告，继续执行（不阻断）

### 6.4 交互模式签核（mode=interactive）

| 签核点 | 时机 | 审阅对象 | verdict 取值 | 人工返工目标 |
|--------|------|---------|-------------|-------------|
| Gate-1 | Phase4后 | 覆盖率报告+攻击面/威胁清单 | pass / pass_with_suggestions / rework / terminate | rework → phase2或phase3 |
| Gate-2 | Phase6后 | 评审报告+安全测试用例 | pass / pass_with_suggestions / rework / terminate | rework → phase5 |
| Gate-3 | Phase7发布前 | 最终报告+全部产物+覆盖率摘要 | publish / not_publish | — |

**签核记录**：每次签核记录到 audit_log.json：reviewer/timestamp/verdict/artifact_version/comment/manual_rework_triggered/rework_target_phase。

**人工返工计数**：人工返工（verdict == "rework"）不计入自动返工的2次上限，单独计入 `manual_rework_count`（progress.json 和 audit_log.json 均记录，无上限）。人工返工后递增 artifact_version 并重新调度对应 Phase。

---

## 7. 输出标准

### 7.1 输出目录结构

```
.secdesign_output/{requirement_id}/
├── requirement_context/
│   ├── requirement_info.json       # Phase0
│   └── security_prescreen.json     # Phase0.5
├── design_doc/                     # Phase0 设计文档副本
├── attack_surfaces/
│   └── attack_surfaces.json        # Phase1
├── threats/
│   └── threats.json                # Phase2
├── security_spec/
│   ├── security_spec.md            # Phase3
│   └── security_spec.json          # Phase3
├── coverage/
│   ├── coverage_report.md          # Phase4
│   └── coverage_findings.json      # Phase4
├── security_tests/
│   ├── security_tests.md           # Phase5
│   └── security_tests.json         # Phase5
├── review/
│   └── review_report.md            # Phase6
├── report/
│   ├── security_report.md          # Phase7
│   ├── security_tests.xlsx         # Phase7
│   ├── security_findings.sarif     # Phase7
│   └── security_graph.html         # Phase7
└── json_file/
    ├── security_graph.json          # 全链知识图谱
    └── audit_log.json               # 审计日志
```

---

## 7.1 progress.json Schema

```json
{
  "requirement_id": "REQ-001",
  "current_phase": 0,
  "mode": "auto",
  "scope": "function",
  "rework_count": {
    "phase2": 0,
    "phase3": 0,
    "phase5": 0
  },
  "manual_rework_count": {
    "phase2": 0,
    "phase3": 0,
    "phase5": 0
  },
  "artifact_versions": {
    "security_spec": "v1",
    "security_tests": "v1"
  },
  "phases": {
    "phase0": "pending",
    "phase0.5": "pending",
    "phase1": "pending",
    "phase2": "pending",
    "phase3": "pending",
    "phase4": "pending",
    "phase5": "pending",
    "phase6": "pending",
    "phase7": "pending"
  }
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| current_phase | number | 当前执行Phase编号 |
| mode | string | 运行模式（auto/interactive） |
| scope | string | 需求粒度（interface/function/module/system） |
| rework_count | object | 自动返工计数（按phase分计，上限2） |
| manual_rework_count | object | 人工返工计数（按phase分计，无上限） |
| artifact_versions | object | 产物版本号（每次返工递增） |
| phases | object | 各Phase状态（pending/in_progress/completed/WARNING/forced_pass） |

---

## 8. 知识库目录结构

```
knowledge-bases/
├── _index.md                          # 总索引
│
├── KL-1-checklist/                    # 安全设计Checklist
│   ├── _index.md                      # 32子类索引+匹配关键词
│   ├── A1.1-new-user.md
│   ├── A1.2-auth-change.md
│   ├── A1.3-session-mgmt.md
│   ├── A1.4-credential-storage.md
│   ├── A2.1-new-api.md
│   ├── A2.2-permission-model.md
│   ├── A2.3-resource-ownership.md
│   ├── A2.4-external-api.md
│   ├── A3.1-user-input.md
│   ├── A3.2-file-upload-download.md
│   ├── A3.3-data-import-export.md
│   ├── A3.4-cross-system-exchange.md
│   ├── A4.1-new-database.md
│   ├── A4.2-sensitive-data-storage.md
│   ├── A4.3-personal-data.md
│   ├── A4.4-log-audit.md
│   ├── A5.1-new-microservice.md
│   ├── A5.2-new-port.md
│   ├── A5.3-config-file.md
│   ├── A5.4-certificate-key.md
│   ├── A5.5-third-party-dependency.md
│   ├── A6.1-container-image.md
│   ├── A6.2-k8s-resource.md
│   ├── A6.3-cloud-resource.md
│   ├── A6.4-ops-command.md
│   ├── A7.1-new-ui.md
│   ├── A7.2-client-connection.md
│   ├── A7.3-comm-encryption.md
│   ├── A7.4-frontend-security.md
│   ├── A8.1-high-risk-operation.md
│   ├── A8.2-business-logic-bypass.md
│   ├── A8.3-billing-rate-limit.md
│   └── A8.4-race-condition.md
│
├── KL-2-stride/                       # STRIDE威胁模板
│   ├── _index.md                      # 32子类×STRIDE映射表（即§2.3的完整表）
│   ├── spoofing.md                    # 每个STRIDE文件内按攻击面子类分节
│   ├── tampering.md                   # 例：tampering.md 含 A1.2/A1.3/.../A8.4 各节
│   ├── repudiation.md
│   ├── information-disclosure.md
│   ├── denial-of-service.md
│   └── elevation-of-privilege.md
│
├── KL-3-owasp/                        # OWASP标准簇
│   ├── _index.md
│   ├── top10.md                       # OWASP Top10 (2021)
│   ├── asvs.md                        # ASVS验证项(按域分类)
│   └── api-top10.md                   # API Security Top10
│
├── KL-4-cwe/                          # CWE弱点映射
│   ├── _index.md
│   └── top25.md                       # CWE/SANS Top25
│
├── KL-5-attack-patterns/              # 攻击模式库
│   ├── _index.md                      # 攻击模式索引(按攻击面分类)
│   ├── injection/                     # 注入类
│   ├── authz/                         # 授权类
│   ├── deser/                         # 反序列化类
│   ├── data/                          # 数据泄露类
│   ├── dos/                           # 拒绝服务类
│   ├── network/                       # 网络类
│   ├── escape/                        # 容器逃逸类
│   ├── persist/                       # 持久化类
│   └── supply/                        # 供应链类
│
├── KL-6-compliance/                   # 合规规则库
│   ├── _index.md
│   ├── G1-credential.md              # 凭证管理
│   ├── G2-crypto.md                  # 加密算法
│   ├── G3-random.md                  # 随机数
│   ├── G4-password.md                # 密码策略
│   ├── G5-data-protection.md         # 数据保护
│   ├── G6-info-leak.md               # 信息泄露
│   ├── G7-session.md                 # 会话管理
│   ├── k8s-compliance.md             # K8s合规
│   ├── docker-compliance.md          # Docker合规
│   └── containerd-compliance.md      # Containerd合规
│
├── KL-7-runtime/                      # 运行时安全检查
│   ├── _index.md
│   ├── wstg-index.md                 # OWASP WSTG测试项索引
│   └── attck-container-cloud.md      # ATT&CK容器/云矩阵
│
└── _evolution/                        # 进化机制
    ├── _index.md                      # 进化规则
    └── _learned/                      # 新发现的攻击模式
        └── .keep

rules/                                 # 规则文件目录
├── prescreen-keywords.md             # 32子类匹配关键词完整表
├── coverage-rules.md                 # CVR-01~05 覆盖率规则
├── review-rules.md                   # Phase6 评审维度规则
└── severity-rules.md                 # DREAD→S1-S4 严重度映射+云环境放大规则

scripts/                               # Python脚本目录
├── json_to_sarif.py                  # security_tests.json → SARIF格式
├── json_to_excel.py                  # security_tests.json → Excel处置跟踪表
├── json_to_csv.py                    # security_tests.json → CSV
└── graph_to_mermaid.py               # security_graph.json → HTML追溯图
```

### 每个KL-1文件的统一格式

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

### 每个攻击模式的统一格式

```markdown
## AP-XXXX 攻击模式名称

- **攻击面**: A{x}.{y}
- **STRIDE映射**: T+I
- **CWE**: CWE-XXX
- **OWASP**: A0X
- **前提条件**: 攻击者需要什么权限/位置
- **攻击路径**: Source → ... → Sink
- **影响**: 机密性/完整性/可用性
- **检查点**: 设计时/编码时/测试时分别检查什么
- **修复方案**: 纵深防御建议
- **参考**: CVE/OWASP/ATT&CK链接
```

---

## 附录A：KL-1 完整内容（32个攻击面子类的检查点）

### A1.1 新增用户/账号

- 匹配关键词：注册、账号、用户、认证、登录、Signup、CreateUser、Register
- STRIDE适用：S R I D E

**安全检查点：**
- [ ] 用户清单必须记录（谁创建了、什么时候、什么权限）（phase: design）
- [ ] 用户必须有认证机制（密码/Token/OAuth/SSO）（phase: design）
- [ ] 认证凭据需满足密码复杂度（≥8字符，至少两种字符类型）（phase: code）
- [ ] 若随机生成密码，需使用安全随机数生成器，不能硬编码（phase: code）
- [ ] 密码不能以任何形式明文存储，必须使用不可逆加密（bcrypt/scrypt/Argon2）（phase: code）
- [ ] 用户枚举防护（注册/登录/忘记密码的错误信息不应区分"用户不存在"和"密码错误"）（phase: test）
- [ ] 批量注册防护（速率限制/CAPTCHA/邀请码）（phase: test）

### A1.2 认证方式变更

- 匹配关键词：密码、Token、MFA、OAuth、SAML、SSO、认证、Auth、Login
- STRIDE适用：S T I D E

**安全检查点：**
- [ ] 认证必须强制TLS传输（phase: deploy）
- [ ] 暴力破解防护（速率限制、锁定策略、指数退避）（phase: design）
- [ ] 多因素认证（MFA）覆盖高敏感操作（phase: design）
- [ ] OAuth/SAML回调URL必须白名单校验（phase: code）
- [ ] Token过期机制（Access Token短过期 + Refresh Token轮换）（phase: code）
- [ ] 登录失败不泄露内部信息（不区分用户名/密码错误）（phase: test）

### A1.3 会话管理

- 匹配关键词：Session、Cookie、Token、JWT、会话、SessionID
- STRIDE适用：S T R I D E

**安全检查点：**
- [ ] SessionID使用安全随机数生成（phase: code）
- [ ] Cookie设置HttpOnly + Secure + SameSite（phase: code）
- [ ] 登录后必须重置SessionID（防会话固定）（phase: code）
- [ ] 会话超时机制（绝对超时+空闲超时）（phase: design）
- [ ] 单点登录/并发会话控制（phase: design）
- [ ] 注销时服务端销毁会话（phase: code）

### A1.4 凭证存储与传输

- 匹配关键词：密码、口令、密钥、Token、凭证、AK/SK、Credential、Secret、Key
- STRIDE适用：S T I E

**安全检查点：**
- [ ] 凭证不能硬编码在源代码中（phase: code）
- [ ] 凭证不能明文存储在配置文件中（phase: code）
- [ ] 凭证传输必须加密（TLS/信封加密）（phase: deploy）
- [ ] 凭证轮换机制（AK/SK定期轮换，不使用永久凭证）（phase: design）
- [ ] 凭证最小权限原则（AK/SK仅授予必需权限，禁止*/*授权）（phase: design）
- [ ] 临时凭证优先（STS/AssumeRole替代长期AK/SK）（phase: design）

### A2.1 新增API接口

- 匹配关键词：接口、API、REST、RPC、gRPC、GraphQL、端点、路由、Controller、Endpoint
- STRIDE适用：S T R I D E（全部适用）

**安全检查点：**
- [ ] 接口认证鉴权（每个端点必须有权限校验注解/中间件）（phase: code）
- [ ] 鉴权失败记录安全审计日志（phase: code）
- [ ] 接口基线刷新（新接口加入API安全基线）（phase: design）
- [ ] 参数校验（前后台双重校验：类型/长度/格式/范围）（phase: code）
- [ ] SQL注入防护（参数化查询/ORM，禁止字符串拼接SQL）（phase: code）
- [ ] 命令注入防护（禁止拼接用户输入到系统命令，使用参数化调用）（phase: code）
- [ ] 限流防护（API速率限制，防DoS/暴力破解）（phase: design）
- [ ] 越权防护（对象级权限校验，防IDOR）（phase: code）
- [ ] 响应脱敏（不泄露内部IP/版本/堆栈信息）（phase: code）
- [ ] 批量操作限制（分页+单次上限，防全量导出）（phase: design）

### A2.2 权限模型变更

- 匹配关键词：RBAC、ABAC、权限、角色、租户、隔离、Permission、Role、Tenant
- STRIDE适用：S I E

**安全检查点：**
- [ ] 最小权限原则（默认无权限，显式授权）（phase: design）
- [ ] 租户数据隔离（行级/库级隔离，跨租户不可访问）（phase: design）
- [ ] 权限变更审计日志（phase: code）
- [ ] 管理员权限分离（安全管理员≠系统管理员≠审计管理员）（phase: design）
- [ ] 权限缓存一致性（权限变更后立即生效，不依赖缓存过期）（phase: test）

### A2.3 资源所有权

- 匹配关键词：IDOR、越权、水平越权、垂直越权、所有权、Owner、Authorization
- STRIDE适用：S I E

**安全检查点：**
- [ ] 对象级访问控制（每个资源访问必须校验当前用户是否为所有者）（phase: code）
- [ ] 水平越权测试（用户A能否操作用户B的数据）（phase: test）
- [ ] 垂直越权测试（普通用户能否执行管理员操作）（phase: test）
- [ ] 资源ID不可预测（UUID替代自增ID，防止枚举遍历）（phase: design）
- [ ] 批量操作校验所有权（批量删除/导出时每个资源都需校验）（phase: code）

### A2.4 OpenAPI/外部接口

- 匹配关键词：OpenAPI、Swagger、外部接口、第三方接口、Webhook、回调
- STRIDE适用：S T R I D E

**安全检查点：**
- [ ] API文档包含分权分域说明（phase: design）
- [ ] 外部接口调用需认证（API Key/签名/Token）（phase: code）
- [ ] 入站数据校验（不信任外部输入，前后台校验）（phase: code）
- [ ] 出站数据脱敏（不向外部泄露内部信息）（phase: code）
- [ ] Webhook URL白名单+签名验证（phase: code）
- [ ] 外部接口超时和熔断（防级联故障）（phase: design）

### A3.1 用户输入处理

- 匹配关键词：表单、参数、Header、Cookie、输入、Input、Form、Parameter
- STRIDE适用：T I D E

**安全检查点：**
- [ ] 服务端输入校验（类型/长度/格式/范围/白名单）（phase: code）
- [ ] 输出编码（防XSS：HTML/JS/URL/CSS上下文分别编码）（phase: code）
- [ ] SQL注入防护（参数化查询）（phase: code）
- [ ] 命令注入防护（参数化调用，禁止拼接）（phase: code）
- [ ] XSS防护（输出编码+CSP头）（phase: code）
- [ ] CSRF防护（Token验证/SameSite Cookie）（phase: code）
- [ ] 文件路径校验（禁止../穿越，路径规范化）（phase: code）
- [ ] 正则DoS防护（避免回溯爆炸型正则，限制匹配时长）（phase: code）

### A3.2 文件上传/下载

- 匹配关键词：上传、下载、附件、导入、导出、Upload、File、Avatar、Import、Export
- STRIDE适用：T R I D E

**安全检查点：**

**文件上传：**
- [ ] 文件类型校验（前台+后台双重校验，白名单模式）（phase: code）
- [ ] 文件名校验（前后台校验，防跨目录攻击"../"，防特殊字符）（phase: code）
- [ ] 文件大小限制（前后台双重限制）（phase: code）
- [ ] 文件内容检测（Magic Bytes/病毒扫描/Webshell检测）（phase: code）
- [ ] 上传后重命名（不保留原始文件名，防文件名注入）（phase: code）
- [ ] 上传目录不可执行（无执行权限，独立存储分区）（phase: deploy）
- [ ] 使用公共上传组件（phase: design）
- [ ] 上传操作记录审计日志（phase: code）
- [ ] 越权防护（只能上传/下载自己的文件）（phase: code）

**文件下载：**
- [ ] 下载文件类型为Excel需CSV注入防护（phase: code）
- [ ] 下载文件类型为HTML需XSS防护（phase: code）
- [ ] 下载操作记录审计日志（phase: code）
- [ ] 下载权限控制（防止越权下载他人文件）（phase: code）
- [ ] 下载临时文件及时清理（phase: code）

### A3.3 数据导入/导出

- 匹配关键词：批量导入、批量导出、Excel、CSV、数据迁移、Batch、Bulk
- STRIDE适用：T R I D E

**安全检查点：**
- [ ] 导入数据校验（同A3.1用户输入处理规则）（phase: code）
- [ ] 导出数据脱敏（敏感字段按权限脱敏）（phase: code）
- [ ] 批量操作数量限制（分页+单次上限）（phase: design）
- [ ] 批量操作审计日志（记录操作人、时间、数据范围）（phase: code）
- [ ] CSV注入防护（导出CSV中公式前缀转义）（phase: code）

### A3.4 跨系统数据交换

- 匹配关键词：消息队列、MQ、Kafka、回调、Webhook、事件、Event、Notify
- STRIDE适用：S T R I D E

**安全检查点：**
- [ ] 消息认证（消息签名/HMAC，防伪造消息）（phase: code）
- [ ] 消息加密（敏感数据传输加密）（phase: code）
- [ ] 消息幂等性（重复消息不产生副作用）（phase: code）
- [ ] 消息审计日志（phase: code）
- [ ] 回调URL白名单+签名验证（phase: code）
- [ ] 消息队列访问控制（权限隔离，不同服务用不同Topic/Queue）（phase: design）

### A4.1 新增数据库/表

- 匹配关键词：数据库、表、RDS、MySQL、PostgreSQL、MongoDB、Database、Table
- STRIDE适用：S T I E

**安全检查点：**
- [ ] 数据库用户清单（最小权限原则，应用账号≠管理账号）（phase: deploy）
- [ ] 数据库连接加密（TLS）（phase: deploy）
- [ ] 数据库访问网络隔离（不暴露公网，VPC内访问）（phase: deploy）
- [ ] 账号密码修改指南（默认密码必须修改）（phase: deploy）
- [ ] SQL注入防护（参数化查询，禁止拼接）（phase: code）

### A4.2 敏感数据存储

- 匹配关键词：加密、脱敏、分级、密钥、KMS、Encrypt、Mask、Classify
- STRIDE适用：T I E

**安全检查点：**
- [ ] 敏感数据分类分级（公开/内部/机密/绝密）（phase: design）
- [ ] 机密及以上数据加密存储（信封加密/KMS托管密钥）（phase: code）
- [ ] 加密算法选择（AES-256-GCM/RSA-2048+，禁止DES/RC4/MD5/SHA1用于安全场景）（phase: code）
- [ ] 密钥管理（KMS托管，不硬编码，定期轮换）（phase: deploy）
- [ ] 数据脱敏（日志/界面/导出中的敏感字段脱敏显示）（phase: code）
- [ ] 修改场景防泄露（修改密码/密钥时，旧值不可回显）（phase: code）

### A4.3 个人数据(PII)处理

- 匹配关键词：电话、邮箱、姓名、地址、身份证、PII、GDPR、隐私、Privacy
- STRIDE适用：S I

**安全检查点：**
- [ ] 个人数据采集最小化（只采必需数据）（phase: design）
- [ ] 个人数据加密存储（phase: code）
- [ ] 个人数据访问审计（phase: code）
- [ ] 数据主体权利（查询/修改/删除/导出）（phase: design）
- [ ] 隐私政策告知（采集前告知用途并获得同意）（phase: design）

### A4.4 日志与审计记录

- 匹配关键词：日志、审计、Log、Audit、Trace、操作记录
- STRIDE适用：T R I

**安全检查点：**
- [ ] 日志不包含敏感信息（密码/Token/密钥不可出现在日志中）（phase: code）
- [ ] 安全相关操作必须记录审计日志（登录/权限变更/数据访问/配置修改）（phase: code）
- [ ] 日志完整性保护（日志文件权限≤640，防篡改）（phase: deploy）
- [ ] 日志保留周期（满足合规要求，通常≥180天）（phase: deploy）
- [ ] 日志格式规范（时间戳+操作人+操作类型+目标+结果）（phase: code）

### A5.1 新增微服务/组件

- 匹配关键词：微服务、容器、Docker、K8s、部署、服务、Microservice、Service、Deploy
- STRIDE适用：S T I D E

**安全检查点：**
- [ ] 服务间通信加密（mTLS/双向TLS）（phase: deploy）
- [ ] 服务认证（ServiceAccount/服务间Token校验）（phase: code）
- [ ] 配置文件不含明文密码（phase: code）
- [ ] 静态伺服安全（Manifest文件不可被前台直接查看）（phase: deploy）
- [ ] 健康检查端点不暴露内部信息（phase: code）

### A5.2 新增端口/网络监听

- 匹配关键词：端口、监听、Socket、网络、Port、Listen、Bind
- STRIDE适用：S I D

**安全检查点：**
- [ ] 通信矩阵更新（新增端口必须记录在通信矩阵中）（phase: design）
- [ ] 禁止全网监听（0.0.0.0:port → 绑定127.0.0.1或内网IP）（phase: code）
- [ ] 端口认证（新增端口必须有认证机制）（phase: code）
- [ ] 端口DoS防护（连接数限制+超时）（phase: code）
- [ ] 防火墙规则（仅开放必需端口）（phase: deploy）

### A5.3 配置文件/环境变量

- 匹配关键词：配置、Config、环境变量、ENV、Properties、YAML、ini
- STRIDE适用：T I E

**安全检查点：**
- [ ] 配置文件权限（400或600，目录700或750）（phase: deploy）
- [ ] 配置文件不含明文密码（使用KMS/Secret管理）（phase: code）
- [ ] 可修改配置文件需填写配置文件清单文档（phase: design）
- [ ] 环境变量不包含敏感信息（或使用Secret注入）（phase: deploy）
- [ ] 配置变更审计日志（phase: code）

### A5.4 证书/密钥管理

- 匹配关键词：证书、CA、TLS、SSL、密钥、Key、Certificate、x509
- STRIDE适用：S T I E

**安全检查点：**
- [ ] 存量预置证书基线检查（算法/有效期/权限）（phase: deploy）
- [ ] 证书文件权限（600，目录700）（phase: deploy）
- [ ] 证书算法强度（RSA≥2048/ECC≥256，禁止SHA1/MD5签名）（phase: code）
- [ ] 证书周期管理（到期前告警，自动续期机制）（phase: deploy）
- [ ] 私钥保护（不硬编码，KMS托管，传输加密）（phase: code）
- [ ] 服务端证书校验（客户端连接时必须校验服务端证书）（phase: code）

### A5.5 第三方依赖引入

- 匹配关键词：三方件、依赖、库、NPM、Maven、Pip、Dependency、Library、Package
- STRIDE适用：S T I D E

**安全检查点：**
- [ ] 依赖CVE扫描（SCA工具扫描已知漏洞）（phase: code）
- [ ] 依赖版本锁定（禁止使用latest，锁定具体版本）（phase: code）
- [ ] 依赖来源可信（官方仓库，禁止未验证的私有源）（phase: design）
- [ ] 开源软件版本信息不泄露（错误页面/响应头不暴露版本号）（phase: code）
- [ ] 依赖许可证合规（GPL/AGPL等传染性许可证审查）（phase: design）

### A6.1 容器/镜像变更

- 匹配关键词：Docker、镜像、Image、Container、Dockerfile、构建
- STRIDE适用：S T I D E

**安全检查点：**
- [ ] 镜像数字签名（防篡改，验证镜像完整性）（phase: deploy）
- [ ] 不使用latest标签（使用具体版本号或SHA256摘要）（phase: deploy）
- [ ] 镜像最小化（使用distroless/alpine基础镜像，减少攻击面）（phase: deploy）
- [ ] 镜像漏洞扫描（部署前扫描CVE）（phase: deploy）
- [ ] 不以root运行容器（securityContext.runAsNonRoot=true）（phase: deploy）
- [ ] 只读根文件系统（securityContext.readOnlyRootFilesystem=true）（phase: deploy）

### A6.2 K8s资源变更

- 匹配关键词：Pod、Deployment、Service、RBAC、NetworkPolicy、Namespace、Ingress
- STRIDE适用：S T R I D E（全部适用）

**安全检查点：**
- [ ] Pod安全标准（enforce: restricted，禁止privileged/hostPath/hostNetwork）（phase: deploy）
- [ ] RBAC最小权限（ServiceAccount仅授予必需权限，禁止*/*）（phase: deploy）
- [ ] NetworkPolicy限制（默认拒绝入站/出站，仅开放必需通信）（phase: deploy）
- [ ] Secret加密存储（etcd加密 + KMS集成）（phase: deploy）
- [ ] 资源请求/限制（CPU/Memory requests+limits，防资源耗尽）（phase: deploy）
- [ ] K8s审计日志开启（phase: deploy）
- [ ] 安全上下文约束（drop ALL capabilities，禁止特权升级）（phase: deploy）

### A6.3 云资源配置

- 匹配关键词：VPC、安全组、IAM、存储桶、OSS、S3、云资源、Cloud
- STRIDE适用：S T I D E

**安全检查点：**
- [ ] VPC隔离（资源部署在私有子网，仅ALB/NAT暴露公网）（phase: deploy）
- [ ] 安全组最小化（仅开放必需端口和来源IP）（phase: deploy）
- [ ] IAM最小权限（AK/SK仅授予必需操作，禁止*/*）（phase: deploy）
- [ ] 存储桶访问控制（禁止公开读写，启用服务端加密）（phase: deploy）
- [ ] 云元数据服务防护（IMDSv2，防SSRF获取AK/SK）（phase: deploy）
- [ ] 云资源标签（安全分级标签，便于审计）（phase: deploy）

### A6.4 运维命令/脚本

- 匹配关键词：运维、脚本、Cron、定时任务、运维命令、脚本执行、sudo、Script
- STRIDE适用：S T R I E

**安全检查点：**
- [ ] 脚本运行日志（所有脚本需记录运行日志，且有绕接能力）（phase: code）
- [ ] 公开命令文档（客户可使用的命令需写入公开文档）（phase: design）
- [ ] 删除注释代码（所有注释掉的代码需删除）（phase: code）
- [ ] 脚本文件权限（可执行但不可写，700或750）（phase: deploy）
- [ ] sudo提权控制（最小化sudo规则，禁止NOPASSWD:ALL）（phase: deploy）
- [ ] 命令参数不含明文密码（需交互式传入）（phase: code）
- [ ] 运维命令清单（所有运维命令需记录在清单中）（phase: design）

### A7.1 新增界面/Web页面

- 匹配关键词：页面、界面、Web、前端、UI、Page、View、HTML、JS
- STRIDE适用：S T R I D E

**安全检查点：**
- [ ] 页面访问认证鉴权（phase: code）
- [ ] XSS防护（输出编码 + CSP头 + HttpOnly Cookie）（phase: code）
- [ ] CSRF防护（Token验证 / SameSite Cookie）（phase: code）
- [ ] URL重定向防护（白名单校验，禁止外部跳转）（phase: code）
- [ ] 前后台参数校验（界面非手工输入+手工输入双重校验）（phase: code）
- [ ] 资源数量控制（增删改操作需数量限制）（phase: design）
- [ ] 口令输入框禁止自动补全（autocomplete=off）（phase: code）
- [ ] 口令不可明文显示（type=password，不可拷贝）（phase: code）

### A7.2 客户端连接

- 匹配关键词：数据库连接、SSH、代理、客户端、Client、Proxy、Connection
- STRIDE适用：S T I E

**安全检查点：**
- [ ] 校验服务端证书（TLS连接必须验证证书有效性）（phase: code）
- [ ] 通信矩阵更新（新增客户端端口范围记录）（phase: design）
- [ ] 密码加密存储（连接配置中密码加密，不回显明文）（phase: code）
- [ ] 连接测试携带信任证书（必须通过TLS连接）（phase: code）
- [ ] 修改IP/端口/用户名时清空密码字段（phase: code）
- [ ] 连接测试不泄露服务端版本信息等敏感信息（phase: code）

### A7.3 通信协议与加密

- 匹配关键词：HTTPS、TLS、SSL、加密传输、通信、通信加密、Protocol
- STRIDE适用：S T I D

**安全检查点：**
- [ ] 全链路TLS（客户端→网关→服务→数据库）（phase: deploy）
- [ ] TLS版本（禁止TLS1.0/1.1，最低TLS1.2，推荐TLS1.3）（phase: deploy）
- [ ] 加密套件（禁止弱加密：RC4/DES/3DES/MD5，推荐AES-GCM）（phase: deploy）
- [ ] 证书校验（双向验证或至少服务端验证）（phase: code）
- [ ] HSTS头（强制HTTPS连接）（phase: deploy）

### A7.4 前端安全

- 匹配关键词：CSP、CORS、X-Frame-Options、前端安全、点击劫持
- STRIDE适用：T I D

**安全检查点：**
- [ ] Content-Security-Policy头（限制脚本/样式/图片来源）（phase: deploy）
- [ ] CORS配置（限制Allow-Origin为可信域名，禁止*）（phase: code）
- [ ] X-Frame-Options头（DENY或SAMEORIGIN，防点击劫持）（phase: deploy）
- [ ] X-Content-Type-Options: nosniff（防MIME嗅探）（phase: deploy）
- [ ] Referer-Policy头（限制Referer泄露）（phase: deploy）

### A8.1 高危操作

- 匹配关键词：删除、重置、修改密码、二次认证、二次授权、敏感操作、Dangerous
- STRIDE适用：S T R I E

**安全检查点：**

**二次认证：**
- [ ] 涉及二次认证的业务接口必须携带ticket参数（phase: code）
- [ ] ticket参数需校验随机性和一致性（phase: code）
- [ ] ticket必须使用安全随机数生成器生成（phase: code）
- [ ] ticket必须一次性使用，使用后立即失效（phase: code）
- [ ] ticket必须设置超时时间（phase: code）

**二次授权：**
- [ ] 涉及二次授权的业务接口必须携带用户名、密码参数（phase: code）
- [ ] 二次授权调用平台接口校验用户名密码（phase: code）
- [ ] 授权通过和不通过均需记录审计日志（phase: code）

### A8.2 业务流程绕过

- 匹配关键词：流程、步骤、状态机、审批、Workflow、State、Bypass
- STRIDE适用：T I E

**安全检查点：**
- [ ] 关键流程步骤不可跳过（服务端校验流程状态，不信任客户端传参）（phase: code）
- [ ] 业务状态机完整性（非法状态转换必须拒绝）（phase: code）
- [ ] 审批流程不可绕过（审批人不可伪造，审批结果不可篡改）（phase: code）
- [ ] 交易/操作防重放（幂等Token/唯一请求ID）（phase: code）

### A8.3 计费/配额/限流

- 匹配关键词：计费、配额、限流、Rate Limit、Quota、Billing、Charge
- STRIDE适用：D E

**安全检查点：**
- [ ] API限流（全局限流+用户级限流+IP级限流）（phase: design）
- [ ] 资源配额限制（单用户/租户的资源使用上限）（phase: design）
- [ ] 大请求拦截（请求体大小限制，防DoS）（phase: code）
- [ ] 计费绕过防护（关键计费操作服务端校验，不信任客户端金额）（phase: code）

### A8.4 竞态条件/幂等性

- 匹配关键词：并发、竞态、幂等、Race Condition、Idempotent、Concurrent
- STRIDE适用：T R I D E

**安全检查点：**
- [ ] 关键操作幂等性（重复请求不产生副作用，使用唯一请求ID/Token）（phase: code）
- [ ] 并发操作加锁（分布式锁/数据库乐观锁/悲观锁）（phase: code）
- [ ] 余额/库存操作原子性（CAS或SELECT FOR UPDATE）（phase: code）
- [ ] 竞态条件测试（并发执行相同操作，验证数据一致性）（phase: test）

---

## 附录B：KL-2 STRIDE威胁模板种子

### Spoofing(仿冒) — 攻击者冒充合法身份

- 适用攻击面：A1.1/A1.2/A1.4/A2.1/A2.2/A2.4/A3.4/A4.1/A5.1/A5.2/A5.4/A5.5/A6.1/A6.2/A6.3/A6.4/A7.1/A7.2/A8.1
- 典型威胁：未认证访问、伪造Token、AK/SK泄露仿冒、会话劫持、伪造SAML断言
- 检查方式：尝试无Token/过期Token/他人Token访问API，观察是否被拒绝

### Tampering(篡改) — 攻击者修改数据或代码

- 适用攻击面：A1.2/A1.3/A1.4/A2.1/A2.4/A3.1/A3.2/A3.3/A3.4/A4.1/A4.2/A4.4/A5.1/A5.3/A5.4/A5.5/A6.1/A6.2/A6.3/A6.4/A7.1/A7.3/A7.4/A8.1/A8.2/A8.4
- 典型威胁：SQL注入、命令注入、XSS、参数篡改、配置篡改、镜像篡改
- 检查方式：注入攻击字符串，篡改请求参数，验证服务端是否过滤

### Repudiation(抵赖) — 攻击者否认执行过操作

- 适用攻击面：A1.1/A1.3/A2.1/A2.4/A3.2/A3.3/A3.4/A4.4/A6.2/A6.4/A8.1/A8.4
- 典型威胁：操作无审计日志、共享凭证无法追溯、日志可被篡改
- 检查方式：执行操作后检查审计日志是否完整记录，验证日志是否防篡改

### Information Disclosure(信息泄露) — 攻击者获取未授权信息

- 适用攻击面：A1.1/A1.2/A1.3/A1.4/A2.1/A2.2/A2.3/A2.4/A3.1/A3.2/A3.3/A3.4/A4.1/A4.2/A4.3/A4.4/A5.1/A5.2/A5.3/A5.4/A5.5/A6.1/A6.2/A6.3/A7.1/A7.2/A8.2/A8.4
- 典型威胁：错误信息泄露内部架构、SSRF读云元数据、日志打印密码、目录遍历、越权读取
- 检查方式：触发错误响应检查是否泄露内部信息，SSRF测试169.254.169.254

### Denial of Service(拒绝服务) — 攻击者使服务不可用

- 适用攻击面：A1.1/A1.2/A1.3/A2.1/A2.4/A3.1/A3.2/A3.3/A3.4/A5.1/A5.2/A5.5/A6.1/A6.2/A6.3/A7.1/A7.3/A8.3/A8.4
- 典型威胁：无限流API被打爆、大文件上传耗尽存储、ReDoS正则回溯、Fork Bomb、资源请求无限制
- 检查方式：超限请求测试、大报文/大Header测试、高并发测试

### Elevation of Privilege(提权) — 攻击者获得更高权限

- 适用攻击面：A1.1/A1.2/A1.3/A1.4/A2.1/A2.2/A2.3/A2.4/A3.1/A3.2/A3.4/A4.1/A4.2/A5.1/A5.3/A5.4/A5.5/A6.1/A6.2/A6.3/A6.4/A7.1/A8.1/A8.2/A8.3/A8.4
- 典型威胁：RBAC过度授权→创建特权Pod→容器逃逸、水平越权→垂直越权、sudo提权、上传Webshell执行
- 检查方式：低权限用户尝试执行高权限操作，容器内尝试访问宿主机资源

---

## 附录C：KL-3 OWASP标准簇种子

### OWASP Top 10 (2021)

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

### OWASP API Security Top 10 (2023)

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

### ASVS关键验证项（Level 1-2精选）

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

## 附录D：KL-4 CWE Top25种子

| 排名 | CWE | 名称 | 映射攻击面 | 映射OWASP |
|------|-----|------|-----------|----------|
| 1 | CWE-78 | OS命令注入 | A3.1/A2.1 | A03 |
| 2 | CWE-79 | XSS | A7.1/A3.1 | A03 |
| 3 | CWE-89 | SQL注入 | A2.1/A4.1 | A03 |
| 4 | CWE-94 | 代码注入 | A3.2/A3.1 | A03 |
| 5 | CWE-190 | 整数溢出 | A3.1 | A03 |
| 6 | CWE-200 | 信息暴露 | A4.4/A2.1 | A01 |
| 7 | CWE-22 | 路径穿越 | A3.2 | A01 |
| 8 | CWE-284 | 不当访问控制 | A2.2/A2.3 | A01 |
| 9 | CWE-295 | 证书校验不当 | A7.2/A7.3 | A02 |
| 10 | CWE-319 | 明文传输 | A7.3 | A02 |
| 11 | CWE-327 | 弱加密算法 | A4.2/A7.3 | A02 |
| 12 | CWE-330 | 不安全随机数 | A1.3/A8.1 | A02 |
| 13 | CWE-384 | 会话固定 | A1.3 | A07 |
| 14 | CWE-434 | 不受限制文件上传 | A3.2 | A03 |
| 15 | CWE-502 | 不安全反序列化 | A3.1/A5.5 | A08 |
| 16 | CWE-522 | 凭证保护不足 | A1.4/A4.2 | A02 |
| 17 | CWE-611 | XXE | A3.1/A3.2 | A03 |
| 18 | CWE-639 | 通过ID授权 | A2.3 | A01 |
| 19 | CWE-732 | 权限分配不当 | A5.3/A6.2 | A05 |
| 20 | CWE-798 | 硬编码凭证 | A1.4/A5.3 | A02 |
| 21 | CWE-862 | 缺少授权 | A2.1/A2.2 | A01 |
| 22 | CWE-918 | SSRF | A2.1/A7.2 | A10 |
| 23 | CWE-125 | 越界读取 | A3.1 | A01 |
| 24 | CWE-787 | 越界写入 | A3.1 | A03 |
| 25 | CWE-269 | 不当权限管理 | A2.2/A6.2 | A01 |

---

## 附录E：KL-5 攻击模式库种子（每类1-2个示例）

### injection/sql-injection

- **攻击面**: A2.1, A4.1
- **STRIDE映射**: T+I
- **CWE**: CWE-89
- **OWASP**: A03
- **前提条件**: 攻击者可访问含数据库查询的API端点
- **攻击路径**: 用户输入(Source: HTTP参数) → 字符串拼接SQL → 数据库执行(Sink: Statement.execute)
- **影响**: 机密性(数据泄露)+完整性(数据篡改)+可用性(删库)
- **检查点**: 设计时(参数化查询架构)、编码时(mybatis禁$、ORM使用)、测试时(单引号/UNION/OR 1=1测试)
- **修复方案**: 参数化查询/ORM/预编译语句 + WAF + 输入白名单校验
- **参考**: https://owasp.org/www-community/attacks/SQL_Injection

### injection/xxe

- **攻击面**: A3.1, A3.2
- **STRIDE映射**: T+I
- **CWE**: CWE-611
- **OWASP**: A03
- **前提条件**: 应用解析XML输入，且XML解析器启用外部实体
- **攻击路径**: XML输入(Source: HTTP Body/上传文件) → XML解析器 → 外部实体加载(Sink: DocumentBuilder/SAXParser)
- **影响**: 机密性(任意文件读取)+完整性(SSRF)
- **检查点**: 编码时(禁用DTD/外部实体)、测试时(发送含ENTITY的XML)
- **修复方案**: 禁用DTD和外部实体解析 + 白名单校验XML来源
- **参考**: https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing

### authz/idor

- **攻击面**: A2.3
- **STRIDE映射**: I+E
- **CWE**: CWE-639
- **OWASP**: A01
- **前提条件**: 攻击者有合法账号，API使用可预测的资源ID
- **攻击路径**: 修改API中的userId/orderId(Source: URL路径参数) → 服务端未校验所有权 → 返回他人数据(Sink: 数据库查询)
- **影响**: 机密性(跨用户数据泄露)
- **检查点**: 设计时(对象级权限架构)、编码时(每个CRUD校验ownerId)、测试时(替换ID访问他人资源)
- **修复方案**: 服务端校验资源所有权 + 使用不可预测ID(UUID) + ABAC策略
- **参考**: https://owasp.org/www-community/attacks/Forced_browsing

### authz/path-traversal

- **攻击面**: A3.2
- **STRIDE映射**: T+I
- **CWE**: CWE-22
- **OWASP**: A01
- **前提条件**: 应用处理文件路径且未严格校验
- **攻击路径**: 文件名参数(Source: HTTP参数) → 路径拼接 → 越界读取(Sink: File.readFile)
- **影响**: 机密性(任意文件读取)
- **检查点**: 编码时(路径规范化+白名单目录)、测试时(../穿越测试)
- **修复方案**: 路径规范化(realpath) + 白名单目录 + 拒绝含..的路径
- **参考**: https://owasp.org/www-community/attacks/Path_Traversal

### deser/java-deserialization

- **攻击面**: A3.1, A5.5
- **STRIDE映射**: T+E
- **CWE**: CWE-502
- **OWASP**: A08
- **前提条件**: 应用反序列化不可信数据，classpath含可利用链
- **攻击路径**: 序列化数据(Source: HTTP Body/Cookie/MQ) → ObjectInputStream.readObject() → 利用链触发(Sink: Runtime.exec)
- **影响**: 完整性+可用性(RCE)
- **检查点**: 编码时(白名单过滤/禁用ObjectInput)、测试时(ysoserial探测)
- **修复方案**: 白名单反序列化类 + Introspector过滤 + 升级依赖
- **参考**: https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data

### data/credential-exposure

- **攻击面**: A1.4, A4.2, A4.4
- **STRIDE映射**: I
- **CWE**: CWE-798, CWE-522, CWE-200
- **OWASP**: A02
- **前提条件**: 攻击者可访问日志/配置/错误信息
- **攻击路径**: 凭证硬编码(Source: 源代码/配置文件) → 日志打印/错误回显(Sink: 日志文件/HTTP响应)
- **影响**: 机密性(凭证泄露→系统被控)
- **检查点**: 编码时(禁止硬编码/日志脱敏)、测试时(搜索源码中的password=/key=)
- **修复方案**: KMS/Secret管理 + 日志脱敏 + 错误信息通用化
- **参考**: CWE-798

### dos/resource-abuse

- **攻击面**: A2.1, A8.3
- **STRIDE映射**: D
- **CWE**: CWE-400, CWE-770
- **OWASP**: API4
- **前提条件**: API无速率限制或资源配额
- **攻击路径**: 大量请求(Source: 自动化脚本) → 无限流服务端 → 资源耗尽(Sink: CPU/内存/连接池)
- **影响**: 可用性(服务不可用)
- **检查点**: 设计时(限流架构/配额设计)、编码时(速率限制中间件)、测试时(高并发压测)
- **修复方案**: API限流 + 连接池限制 + 超时设置 + 自动扩缩容
- **参考**: https://owasp.org/www-community/attacks/Denial_of_Service

### escape/privileged-container

- **攻击面**: A6.1, A6.2
- **STRIDE映射**: E+I
- **CWE**: CWE-269
- **OWASP**: A01
- **前提条件**: 攻击者可创建或进入privileged容器
- **攻击路径**: privileged Pod(Source: K8s部署配置) → mount宿主机磁盘 → chroot(Sink: 宿主机控制)
- **影响**: 完整性+机密性+可用性(宿主机完全控制)
- **检查点**: 设计时(Pod安全标准restricted)、部署时(审计privileged配置)、测试时(尝试mount/chroot)
- **修复方案**: Pod Security Standards enforce:restricted + OPA/Gatekeeper策略 + 运行时安全(Falco)
- **参考**: MITRE ATT&CK T1611

### network/ssrf

- **攻击面**: A2.1, A7.2
- **STRIDE映射**: I
- **CWE**: CWE-918
- **OWASP**: A10
- **前提条件**: 应用根据用户输入发起HTTP请求
- **攻击路径**: URL参数(Source: HTTP参数) → 服务端发起请求 → 内网访问/元数据(Sink: HttpClient.execute)
- **影响**: 机密性(内网信息/云AK-SK泄露)
- **检查点**: 编码时(URL白名单/禁止内网IP)、测试时(169.254.169.254/127.0.0.1/内网IP探测)
- **修复方案**: URL白名单+内网IP过滤+IMDSv2+出站网络限制
- **参考**: https://owasp.org/www-community/attacks/Server_Side_Request_Forgery

---

## 附录F：KL-6 合规规则库种子

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

## 附录G：KL-7 运行时安全检查种子

### OWASP WSTG关键测试项

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

### ATT&CK容器/云关键战术

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

## 9. 适配器接口

### 8.1 requirement-provider 适配器（Phase0）

与testdesign完全一致，可复用。

```
输入: requirement_id (string)
输出: JSON { requirement_id, requirement_name, description, scope, acceptance_criteria, design_docs, custom_fields }
```

### 8.2 security-report-publisher 适配器（Phase7）

可替换的发布适配器，默认输出本地文件，可替换为：
- 对接缺陷管理系统（JIRA/禅道）
- 对接安全平台
- 对接CI/CD Pipeline

```
输入: security_tests.json + security_graph.json + audit_log.json
输出: 发布到目标平台（默认=本地文件）
```

### 8.3 环境变量命名规范

所有外部系统认证和配置通过环境变量管理，不硬编码到 SKILL.md 或脚本中。

| 前缀 | 用途 |
|------|------|
| `SECDESIGN_REQ_*` | requirement-provider 适配器 |
| `SECDESIGN_PUB_*` | security-report-publisher 适配器 |
| `SECDESIGN_REVIEWER` | 交互模式默认签核人 |
| `SECDESIGN_MODE` | 默认运行模式（auto） |
| `SECDESIGN_FORMAT` | 默认输出格式（all） |
| `SECDESIGN_FORCE` | 跳过预门（false） |
| `SECDESIGN_SCOPE` | 默认需求粒度（auto） |
| `SECDESIGN_BATCH_THRESHOLD` | 分批阈值（默认20） |

**安全要求**：
- 环境变量不写入代码或配置文件
- 不在日志中输出 token 值
- `.secdesign-data/` 和 `.secdesign_output/` 目录应加入 `.gitignore`
- API token 通过环境变量传递，不通过命令行参数（避免进程列表泄露）

### 8.4 LLM 模型要求

LLM 模型由运行时管理，secdesign 套件不绑定特定模型。

**模型要求**：
- 支持长上下文（≥ 32K tokens），用于处理大需求文档和知识层加载
- 支持 JSON 结构化输出
- 支持中文理解与生成
- 具备安全领域知识（OWASP/CWE/STRIDE 等标准理解能力）
- 具备代码生成能力（用于生成测试数据和攻击 payload）

**不绑定声明**：secdesign 套件的 SKILL.md 中不引用任何具体模型名称。LLM 调用由运行时框架（opencode/Claude Code 等）自动选择当前会话模型。

---

## 10. 并发写入协议

与testdesign一致：
- security_graph.json 使用追加写入模式
- 每个 Phase 只追加自己负责的节点和边
- Phase4 覆盖率检查和 Phase6 评审如需并行，各自写独立 findings 分片文件，全部完成后串行汇总合并到 graph

---

## 11. 审计日志 Schema

与testdesign一致：

```json
{
  "requirement_id": "REQ-001",
  "mode": "interactive",
  "gates": [
    {
      "gate": "Gate-1",
      "phase": "after-Phase4",
      "reviewer": "zhang_san",
      "timestamp": "2026-07-23T14:30:00",
      "verdict": "pass",
      "artifact_version": "v1",
      "comment": "覆盖率达标，攻击面覆盖率92%",
      "manual_rework_triggered": false,
      "rework_target_phase": null
    },
    {
      "gate": "Gate-2",
      "phase": "after-Phase6",
      "reviewer": "zhang_san",
      "timestamp": "2026-07-23T16:45:00",
      "verdict": "pass_with_suggestions",
      "artifact_version": "v1",
      "comment": "可执行性达标，1条用例建议补充攻击payload",
      "manual_rework_triggered": false,
      "rework_target_phase": null
    },
    {
      "gate": "Gate-3",
      "phase": "after-Phase7",
      "reviewer": "zhang_san",
      "timestamp": "2026-07-23T17:20:00",
      "verdict": "publish",
      "artifact_version": "v1",
      "comment": "产物完整，同意发布",
      "manual_rework_triggered": false,
      "rework_target_phase": null
    }
  ],
  "manual_rework_count": {
    "phase2": 0,
    "phase3": 0,
    "phase5": 0
  }
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| requirement_id | string | 需求唯一标识 |
| mode | string | 运行模式（auto/interactive） |
| gates | array | 签核记录数组（auto模式为空） |
| manual_rework_count | object | 人工返工计数（按phase分计，无上限） |

**gates 数组元素字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| gate | string | 签核点标识：Gate-1 / Gate-2 / Gate-3 |
| phase | string | 对应Phase：after-Phase4 / after-Phase6 / after-Phase7 |
| reviewer | string | 签核人（来自参数或环境变量 SECDESIGN_REVIEWER） |
| timestamp | string | ISO 8601 时间戳 |
| verdict | string | 裁决结果（见 §6.4 签核点定义） |
| artifact_version | string | 被审阅产物版本 |
| comment | string | 签核意见 |
| manual_rework_triggered | boolean | 是否触发人工返工 |
| rework_target_phase | string/null | 返工目标Phase（如触发返工，否则null） |