# 适配器接口合约（ADAPTER_CONTRACT）

> 本文件定义 secdesign 套件的两个可插拔适配器接口合约、默认实现、替换步骤，以及环境变量命名规范和 LLM 模型要求。

## 1. requirement-provider 适配器（Phase0）

### 1.1 接口合约

```
输入: requirement_id (string)
输出: JSON {
  requirement_id,          // 必需，需求唯一标识
  requirement_name,        // 必需，需求名称
  description,             // 必需，原始需求文本
  acceptance_criteria,     // 可选，验收标准
  scope,                   // 可选，需求粒度(interface/function/module/system)
  priority,                // 可选，优先级
  design_docs: [{          // 可选，设计文档列表
    name,                  // 文档名称
    path,                  // 文档路径（可访问）
    type                   // docx/pdf/md/xlsx/openapi
  }],
  custom_fields: {}        // 可选，自定义字段
}
```

**必需字段校验**：输出 JSON 必须包含 `requirement_id`、`requirement_name`、`description` 三个字段。字段缺失时向用户提示并终止流程。

### 1.2 默认实现

读取本地 JSON 文件：

1. 读取项目目录下 `.secdesign-data/{requirement_id}.json`
2. 校验 JSON 包含必需字段：requirement_id, requirement_name, description
3. 如果字段缺失，向用户提示并终止
4. 将内容写入 `.secdesign_output/{requirement_id}/requirement_context/requirement_info.json`
5. 更新 security_graph.json：添加 requirement 节点

### 1.3 替换步骤

| 步骤 | 操作 |
|------|------|
| 1 | 修改 `skills/requirement-provider/SKILL.md` |
| 2 | 将"读本地 JSON 文件"替换为目标平台 API 调用逻辑 |
| 3 | 保持输出格式不变（必需字段 + 可选字段） |
| 4 | 配置认证环境变量（见 §3） |
| 5 | 验证输出 JSON 通过必需字段校验 |

### 1.4 配置示例

```bash
# 默认实现：无需配置
# 替换实现：配置平台认证
export SECDESIGN_REQ_PROVIDER=jira
export SECDESIGN_REQ_API_URL=https://your-jira.example.com/api
export SECDESIGN_REQ_API_TOKEN=your_token
```

## 2. security-report-publisher 适配器（Phase7）

### 2.1 接口合约

```
输入: security_tests.json + security_graph.json + audit_log.json
输出: 发布到目标平台（默认=本地文件）
```

可替换的发布目标：
- 对接缺陷管理系统（JIRA/禅道）
- 对接安全平台
- 对接 CI/CD Pipeline

### 2.2 默认实现

本地文件输出 + 脚本转换：

1. 读取 `json_file/security_graph.json` 和 `security_tests/security_tests.json`
2. 生成 Markdown 报告：写入 `report/security_report.md`（安全规格+威胁模型+测试用例）
3. 生成 Excel 处置跟踪表：调用 `scripts/json_to_excel.py`，写入 `report/security_tests.xlsx`
4. 生成 SARIF：调用 `scripts/json_to_sarif.py`，写入 `report/security_findings.sarif`
5. 生成追溯图：调用 `python3 {套件根}/skills/graph-viz/generate_viz.py -g json_file/security_graph.json --offline -o report/security_graph_viz.html`
6. 闭环校验：所有 attack_surface 和 threat 节点状态非 ⬜
7. 归档审计日志：`json_file/audit_log.json`

### 2.3 替换目标

| 替换目标 | 说明 |
|---------|------|
| JIRA/禅道 | 将安全发现推送为缺陷工单，severity 映射为工单优先级 |
| 安全平台 | 将安全测试用例和发现发布到企业安全管理平台 |
| CI/CD Pipeline | 输出 SARIF 供 CI/CD 门控消费，阻断不达标构建 |

### 2.4 替换步骤

| 步骤 | 操作 |
|------|------|
| 1 | 修改 `skills/security-report-publisher/SKILL.md` |
| 2 | 在本地文件输出后追加平台 API 推送逻辑 |
| 3 | 保持本地文件输出不变（作为本地备份） |
| 4 | 配置认证环境变量（见 §3） |

### 2.5 配置示例

```bash
# 默认实现：无需配置
# 替换实现：配置平台认证
export SECDESIGN_PUB_PROVIDER=jira
export SECDESIGN_PUB_API_URL=https://your-jira.example.com/api
export SECDESIGN_PUB_API_TOKEN=your_token
export SECDESIGN_PUB_PROJECT_ID=123
```

## 3. 环境变量命名规范

所有外部系统认证和配置通过环境变量管理，不硬编码到 SKILL.md 或脚本中。

### 3.1 环境变量列表

| 变量 | 默认 | 说明 |
|------|------|------|
| `SECDESIGN_REQ_*` | — | requirement-provider 适配器（API URL/TOKEN 等） |
| `SECDESIGN_PUB_*` | — | security-report-publisher 适配器（API URL/TOKEN 等） |
| `SECDESIGN_REVIEWER` | current_user | interactive 模式签核人 |
| `SECDESIGN_MODE` | auto | 默认运行模式 |
| `SECDESIGN_FORMAT` | all | 默认输出格式 |
| `SECDESIGN_FORCE` | false | 是否跳过预门 |
| `SECDESIGN_SCOPE` | auto | 默认需求粒度 |
| `SECDESIGN_BATCH_THRESHOLD` | 20 | 分批阈值 |

### 3.2 安全要求

- 环境变量不写入代码或配置文件
- 不在日志中输出 token 值
- `.secdesign-data/` 和 `.secdesign_output/` 目录应加入 `.gitignore`
- API token 通过环境变量传递，不通过命令行参数（避免进程列表泄露）

## 4. LLM 模型要求

LLM 模型由运行时管理，secdesign 套件不绑定特定模型。

### 4.1 模型要求

| 要求 | 说明 |
|------|------|
| 长上下文 | ≥ 32K tokens，用于处理大需求文档和知识层加载 |
| JSON 结构化输出 | 支持输出 JSON 格式的结构化数据 |
| 中文理解与生成 | 支持中文安全术语和文档生成 |
| 安全领域知识 | 具备 OWASP/CWE/STRIDE 等标准理解能力 |
| 代码生成 | 用于生成测试数据和攻击 payload |

### 4.2 不绑定声明

secdesign 套件的 SKILL.md 中不引用任何具体模型名称。LLM 调用由运行时框架（opencode/Claude Code 等）自动选择当前会话模型。
