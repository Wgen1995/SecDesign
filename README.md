# secdesign — 安全测试设计框架

输入需求编号，自动完成 需求获取→安全预检→攻击面识别→威胁建模→安全规格→覆盖率检查→安全测试用例→评审→报告，产出可追溯的安全测试设计全链闭环。

---

## 核心价值

| 价值 | 说明 |
|------|------|
| **防漏** | 每个攻击面必须有检测结果，不允许未覆盖 |
| **可追溯** | 漏洞→威胁→攻击面→需求全链可查（知识图谱） |
| **标准化** | 检查点来自行业标准（OWASP/CWE/STRIDE），不靠 LLM 感觉判定 |
| **可进化** | 攻击模式库支持社区贡献和自动沉淀 |

---

## 不做的事（边界）

- 不做白盒代码审计（其他工具的职责）
- 不做渗透测试执行（其他工具的职责）
- 不做合规扫描执行（其他工具的职责）
- 只做 **需求→攻击面→威胁→检查点→安全测试用例** 这一链

secdesign 的输出可以驱动下游白盒审计工具的审计范围和安全测试的验证清单。

---

## Pipeline 流水线

```
Phase0     requirement-provider       需求获取
Phase0.5   security-prescreen         需求安全预检
Phase1     attack-surface-identifier  攻击面识别
Phase2     threat-mapper              威胁映射
Phase3     security-spec-generator    安全规格生成
Phase4     coverage-checker           覆盖率检查
Phase5     security-test-generator    安全测试用例生成
Phase6     security-review            安全评审
Phase7     security-report-publisher  安全报告 + 处置跟踪
```

三层映射核心逻辑：

```
攻击面(A) —STRIDE—▶ 威胁(T) —知识层—▶ 检查点(C)
(入口)              (可能遭遇什么)      (怎么检查/怎么修)
```

---

## 快速开始

### 1. 准备需求数据 JSON

在项目根目录创建 `.secdesign-data/{requirement_id}.json`：

```json
{
  "requirement_id": "REQ-001",
  "requirement_name": "用户登录功能",
  "description": "新增用户名密码登录，支持短信验证码二次认证...",
  "acceptance_criteria": "用户可通过手机号+验证码登录；密码错误5次锁定账户...",
  "scope": "function",
  "priority": "P0",
  "design_docs": [
    {
      "name": "登录模块设计文档",
      "path": "docs/login-design.md",
      "type": "md"
    }
  ],
  "custom_fields": {}
}
```

### 2. 运行

```
/secdesign REQ-001
```

可选参数：

```
/secdesign REQ-001 mode=interactive reviewer=zhangsan scope=function format=all
```

### 3. 查看输出

所有产物输出到 `.secdesign_output/{requirement_id}/` 目录：

```
.secdesign_output/REQ-001/
├── requirement_context/        # Phase0/0.5 需求上下文
├── design_doc/                 # Phase0 设计文档副本
├── attack_surfaces/            # Phase1 攻击面
├── threats/                    # Phase2 威胁
├── security_spec/              # Phase3 安全规格
├── coverage/                   # Phase4 覆盖率报告
├── security_tests/             # Phase5 安全测试用例
├── review/                     # Phase6 评审报告
├── report/                     # Phase7 最终报告（MD/Excel/SARIF/HTML）
└── json_file/                  # 知识图谱 + 审计日志
```

---

## 需求数据 JSON 格式

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `requirement_id` | string | 是 | 需求唯一标识 |
| `requirement_name` | string | 是 | 需求名称（显示用） |
| `description` | string | 是 | 原始需求文本 |
| `acceptance_criteria` | string | 否 | 验收标准 |
| `scope` | string | 否 | 需求粒度：`interface` / `function` / `module` / `system` |
| `priority` | string | 否 | 优先级 |
| `design_docs` | array | 否 | 设计文档列表 |
| `design_docs[].name` | string | — | 文档名称 |
| `design_docs[].path` | string | — | 文档路径（可访问） |
| `design_docs[].type` | string | — | 文档类型：`docx` / `pdf` / `md` / `xlsx` / `openapi` |
| `custom_fields` | object | 否 | 自定义字段 |

默认实现读取本地 JSON 文件 `.secdesign-data/{requirement_id}.json`，可通过适配器模式替换为 Jira/其他需求平台对接。

---

## 目标用户

| 角色 | 使用场景 | 主要消费产物 |
|------|---------|-------------|
| 安全设计工程师 / SDL 工程师 | 需求阶段做威胁建模，驱动安全设计 | 安全规格（威胁模型 + 检查点） |
| 安全测试工程师 | 从需求生成安全测试用例，执行验证 | 安全测试用例（MD/JSON） |
| 渗透测试工程师 | 用测试用例作为渗透范围和验证清单 | 测试用例 + 攻击模式库（KL-5） |
| 开发人员风险自测 | 编码前看检查点，编码后自测 | Excel 检查点清单（处置跟踪表） |
| 项目经理 | 跟踪安全风险修复进度 | Excel 处置跟踪表 |
| CI/CD Pipeline | 自动化安全门控 | SARIF（机器可读发现） |

---

## 知识层概览

7 个可插拔的知识层，每个对应一个标准或规则库：

| 知识层 | 名称 | 来源 | 条目数 | 用途 |
|--------|------|------|--------|------|
| KL-1 | 安全设计 Checklist | 行业安全设计实践 | ~150 条 | Phase1 攻击面识别时做需求扫描 |
| KL-2 | STRIDE 威胁模板 | 微软 SDL + STRIDE 标准 | ~112 条 | Phase2 威胁建模时做 STRIDE 分析 |
| KL-3 | OWASP 标准簇 | OWASP Top10 + ASVS + API Security Top10 | ~300 条 | Phase3 安全规格生成时做检查点映射 |
| KL-4 | CWE 弱点映射 | CWE Top25 + SANS Top25 | ~50 条 | Phase5 测试用例生成时做弱点-测试映射 |
| KL-5 | 攻击模式库 | OWASP 攻击模式 + 云原生攻击模式 | ~88 条 | Phase2 威胁细化 + Phase5 测试设计 |
| KL-6 | 合规规则库 | 凭证/加密/随机数/密码/数据保护/信息泄露/会话管理 + 容器合规 | ~300 条 | Phase4 覆盖率检查 + Phase5 合规测试 |
| KL-7 | 运行时安全检查 | OWASP WSTG + ATT&CK 容器/云矩阵 | ~130 条 | Phase5 渗透测试用例 + Phase6 攻击链验证 |

需求粒度自适应：不同粒度的需求命中不同知识层。

| 需求粒度 | scope 值 | 命中攻击面 | 必须加载 | 按需加载 |
|---------|---------|-----------|---------|---------|
| 接口级 | `interface` | 1-2 个子类 | KL-1, KL-3, KL-5 | KL-4, KL-7 |
| 功能级 | `function` | 3-5 个子类 | KL-1~5 | KL-6, KL-7 |
| 模块级 | `module` | 5-10 个子类 | KL-1~6 | KL-7 |
| 系统级 | `system` | 10+ 个子类 | KL-1~7 | — |

---

## 参数说明

| 名称 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `requirement_id` | string | 是 | — | 需求唯一标识 |
| `requirement_name` | string | 否 | — | 需求名称（显示用） |
| `mode` | string | 否 | `auto` | `auto` / `interactive` |
| `reviewer` | string | 否 | env `SECDESIGN_REVIEWER` | 交互模式签核人 |
| `scope` | string | 否 | `auto` | `interface` / `function` / `module` / `system` / `auto` |
| `format` | string | 否 | `all` | `md` / `json` / `csv` / `excel` / `graph` / `sarif` / `all` / 组合 |
| `force` | boolean | 否 | `false` | 跳过 Phase0.5 预门 |

---

## 目录结构

```
secdesign/
├── SKILL.md                              # 入口编排器（任务2填充）
├── README.md                             # 本文件
├── .gitignore
│
├── skills/                               # 子 skill 目录
│   ├── shared/                           # 共享规范（OUTPUT_STANDARD/QUALITY_GATES/ADAPTER_CONTRACT/AUDIT_LOG_SPEC）
│   ├── requirement-provider/             # Phase0
│   ├── security-prescreen/               # Phase0.5
│   ├── attack-surface-identifier/        # Phase1
│   ├── threat-mapper/                    # Phase2
│   ├── security-spec-generator/          # Phase3
│   ├── coverage-checker/                 # Phase4
│   ├── security-test-generator/          # Phase5
│   ├── security-review/                  # Phase6
│   └── security-report-publisher/        # Phase7
│
├── knowledge-bases/                      # 知识库（7层 + 进化）
│   ├── KL-1-checklist/                   # 安全设计 Checklist（32子类）
│   ├── KL-2-stride/                      # STRIDE 威胁模板
│   ├── KL-3-owasp/                       # OWASP 标准簇
│   ├── KL-4-cwe/                         # CWE 弱点映射
│   ├── KL-5-attack-patterns/             # 攻击模式库
│   │   ├── injection/                    # 注入类
│   │   ├── authz/                        # 授权类
│   │   ├── deser/                        # 反序列化类
│   │   ├── data/                         # 数据泄露类
│   │   ├── dos/                          # 拒绝服务类
│   │   ├── network/                      # 网络类
│   │   ├── escape/                       # 容器逃逸类
│   │   ├── persist/                      # 持久化类
│   │   └── supply/                       # 供应链类
│   ├── KL-6-compliance/                  # 合规规则库
│   ├── KL-7-runtime/                     # 运行时安全检查
│   └── _evolution/                       # 进化机制
│       └── _learned/                     # 新发现的攻击模式
│
├── rules/                                # 规则文件
│   ├── prescreen-keywords.md             # 32子类匹配关键词
│   ├── coverage-rules.md                 # CVR-01~05 覆盖率规则
│   ├── review-rules.md                   # Phase6 评审维度规则
│   └── severity-rules.md                 # DREAD→S1-S4 严重度映射
│
├── scripts/                              # Python 脚本
│   ├── json_to_sarif.py                  # JSON → SARIF
│   ├── json_to_excel.py                  # JSON → Excel 处置跟踪表
│   └── json_to_csv.py                    # JSON → CSV
│
├── skills/
│   ├── shared/                           # 共享规范
│   ├── requirement-provider/             # Phase0
│   ├── security-prescreen/               # Phase0.5
│   ├── attack-surface-identifier/        # Phase1
│   ├── threat-mapper/                    # Phase2
│   ├── security-spec-generator/          # Phase3
│   ├── coverage-checker/                 # Phase4
│   ├── security-test-generator/          # Phase5
│   ├── security-review/                  # Phase6
│   ├── security-report-publisher/        # Phase7
│   └── graph-viz/                        # 图谱可视化生成器
│       ├── SKILL.md                      # 技能说明
│       ├── generate_viz.py               # security_graph.json → 交互式 HTML（Cytoscape.js，离线模式）
│       └── template.html                 # HTML 模板
│
└── agents/                               # Agent 定义
    └── secdesign-supervisor.md           # 监督 agent
```

---

## 输出产物格式

| 格式 | 说明 | 消费者 |
|------|------|--------|
| MD | 人类可读报告 | 安全工程师、开发人员 |
| JSON | 机器可读结构化数据 | CI/CD、下游工具 |
| CSV | 表格形式测试用例 | 测试团队 |
| Excel | 处置跟踪表（含状态跟踪列） | 项目经理、开发人员 |
| SARIF | 标准化安全发现格式 | CI/CD Pipeline |
| Graph (HTML) | 知识图谱可视化追溯图 | 安全工程师、审计 |
