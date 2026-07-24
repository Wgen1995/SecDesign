# secdesign 核心框架实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 从 secdesign_spec.md 规格创建可运行的最小 Skill 套件框架，包含入口编排器、9个Phase子skill、共享规范、规则文件、脚本和知识层桩文件。

**架构：** opencode Skill 套件，LLM 语义执行。SKILL.md 是 LLM 指令文件（非程序代码），scripts/ 下的 Python 脚本仅做格式转换。知识层在 Plan 2 填充完整内容，Plan 1 只建桩文件。

**技术栈：** Markdown（SKILL指令）+ Python（格式转换脚本）+ JSON（数据载体）

**规格参考：** `secdesign_spec.md`（v1.1，已审阅改进，2280行）

---

## 文件结构

### 创建的文件（共 30 个）

```
secdesign/
├── SKILL.md                              # 任务1：入口编排器（§0）
├── README.md                             # 任务1：用户文档
├── .gitignore                            # 任务1：忽略输出目录
├── skills/
│   ├── shared/
│   │   ├── OUTPUT_STANDARD.md            # 任务2：输出标准（§5.1 + §7）
│   │   ├── QUALITY_GATES.md              # 任务2：质量门控（§5.2 + §6）
│   │   ├── ADAPTER_CONTRACT.md           # 任务2：适配器合约（§5.3 + §9）
│   │   └── AUDIT_LOG_SPEC.md             # 任务2：审计日志（§5.4 + §11）
│   ├── requirement-provider/SKILL.md     # 任务3：Phase0
│   ├── security-prescreen/SKILL.md       # 任务3：Phase0.5
│   ├── attack-surface-identifier/SKILL.md # 任务4：Phase1
│   ├── threat-mapper/SKILL.md            # 任务4：Phase2
│   ├── security-spec-generator/SKILL.md  # 任务5：Phase3
│   ├── coverage-checker/SKILL.md         # 任务5：Phase4
│   ├── security-test-generator/SKILL.md  # 任务6：Phase5
│   ├── security-review/SKILL.md          # 任务6：Phase6
│   └── security-report-publisher/SKILL.md # 任务7：Phase7
├── rules/
│   ├── prescreen-keywords.md             # 任务8：预检关键词
│   ├── coverage-rules.md                 # 任务8：覆盖率规则
│   ├── review-rules.md                   # 任务8：评审规则
│   └── severity-rules.md                 # 任务8：严重度规则
├── scripts/
│   ├── json_to_sarif.py                  # 任务9：SARIF格式转换
│   ├── json_to_excel.py                  # 任务9：Excel格式转换
│   ├── json_to_csv.py                    # 任务9：CSV格式转换
│   └── graph_to_mermaid.py               # 任务9：HTML追溯图
├── knowledge-bases/                      # 任务10：桩文件
│   ├── _index.md
│   ├── KL-1-checklist/_index.md
│   ├── KL-2-stride/_index.md
│   ├── KL-3-owasp/_index.md
│   ├── KL-4-cwe/_index.md
│   ├── KL-5-attack-patterns/_index.md
│   ├── KL-6-compliance/_index.md
│   ├── KL-7-runtime/_index.md
│   └── _evolution/_index.md
└── agents/
    └── secdesign-supervisor.md           # 任务11：交互模式协调
```

### 文件职责

| 文件 | 职责 | 内容来源 |
|------|------|---------|
| SKILL.md | 套件入口，参数收集，Phase调度，门控，汇总 | spec §0 |
| skills/shared/*.md | 跨Phase共享的输出标准、门控、适配器、审计规范 | spec §5 |
| skills/*/SKILL.md | 各Phase的LLM执行指令（输入→处理→输出） | spec §3 |
| rules/*.md | 规则文件，LLM读取后执行检查 | spec §3.4/3.8/3.10/3.6 |
| scripts/*.py | 格式转换脚本，bash调用，无业务逻辑 | spec §3.11 |
| knowledge-bases/*/​_index.md | 知识层索引桩文件，Plan 2填充完整内容 | spec §7 |

---

## 任务 1：目录骨架 + README + .gitignore

**文件：**
- 创建：`secdesign/SKILL.md`（任务2填充内容，此处先建目录）
- 创建：`secdesign/README.md`
- 创建：`secdesign/.gitignore`

- [ ] **步骤 1：创建完整目录结构**

```bash
cd /Users/wgen/Sectest/secdesign
mkdir -p skills/shared
mkdir -p skills/requirement-provider
mkdir -p skills/security-prescreen
mkdir -p skills/attack-surface-identifier
mkdir -p skills/threat-mapper
mkdir -p skills/security-spec-generator
mkdir -p skills/coverage-checker
mkdir -p skills/security-test-generator
mkdir -p skills/security-review
mkdir -p skills/security-report-publisher
mkdir -p rules
mkdir -p scripts
mkdir -p knowledge-bases/KL-1-checklist
mkdir -p knowledge-bases/KL-2-stride
mkdir -p knowledge-bases/KL-3-owasp
mkdir -p knowledge-bases/KL-4-cwe
mkdir -p knowledge-bases/KL-5-attack-patterns/injection
mkdir -p knowledge-bases/KL-5-attack-patterns/authz
mkdir -p knowledge-bases/KL-5-attack-patterns/deser
mkdir -p knowledge-bases/KL-5-attack-patterns/data
mkdir -p knowledge-bases/KL-5-attack-patterns/dos
mkdir -p knowledge-bases/KL-5-attack-patterns/network
mkdir -p knowledge-bases/KL-5-attack-patterns/escape
mkdir -p knowledge-bases/KL-5-attack-patterns/persist
mkdir -p knowledge-bases/KL-5-attack-patterns/supply
mkdir -p knowledge-bases/KL-6-compliance
mkdir -p knowledge-bases/KL-7-runtime
mkdir -p knowledge-bases/_evolution/_learned
mkdir -p agents
```

- [ ] **步骤 2：创建 .gitignore**

```
.secdesign-data/
.secdesign_output/
__pycache__/
*.pyc
.DS_Store
```

- [ ] **步骤 3：创建 README.md**

基于 spec §1 项目定位 + §1.5 目标用户 + 快速开始示例。内容包括：一句话描述、核心价值、9 Phase流水线图、快速开始（准备需求数据→运行→查看输出）、目标用户表、知识层概览、参数说明、目录结构。

- [ ] **步骤 4：验证目录结构**

```bash
find . -type d | sort
```
预期：列出所有创建的目录，无报错。

---

## 任务 2：SKILL.md 入口编排器 + skills/shared/ 四文件

**文件：**
- 创建：`secdesign/SKILL.md`
- 创建：`secdesign/skills/shared/OUTPUT_STANDARD.md`
- 创建：`secdesign/skills/shared/QUALITY_GATES.md`
- 创建：`secdesign/skills/shared/ADAPTER_CONTRACT.md`
- 创建：`secdesign/skills/shared/AUDIT_LOG_SPEC.md`

- [ ] **步骤 1：创建 SKILL.md（入口编排器）**

从 spec §0 提取内容。格式对齐 testdesign/SKILL.md：
- YAML frontmatter（name: secdesign, description: ...）
- §0 套件根定位（Glob pattern: **/secdesign/SKILL.md）
- 参数格式表（§3.2）
- 第一步：参数收集
- 第二步：初始化工作目录（完整目录结构 + security_graph.json + progress.json + audit_log.json 初始化JSON）
- 第三步：调度 Phase 子 skill（9个Phase顺序 + Task工具调用）
- 第四步：质量门控（Phase0.5后 + Phase4后 + CVR-05后 + Phase6后）
- 第五步：人工签核点（Gate-1/2/3，仅interactive模式）
- 第六步：汇总模板
- 红线（§0.6）

- [ ] **步骤 2：创建 OUTPUT_STANDARD.md**

从 spec §5.1 + §7 提取：
- 输出目录结构（§7.1）
- 文件命名规范（UTF-8无BOM，CSV例外，ISO 8601日期，snake_case，JSON 2空格缩进）
- security_graph.json Schema（§4.1 节点类型 + §4.2 边类型 + §4.3 五态标记）
- source 字段（§4.1 security_test节点）
- MUST 输入/输出表（§5.1 完整9行）
- 并发写入协议（§10）
- BATCH_THRESHOLD（§5.1，默认20）

- [ ] **步骤 3：创建 QUALITY_GATES.md**

从 spec §6 + §5.2 提取：
- §6.1 Phase0.5 安全预检门控（verdict表）
- §6.2 Phase4 覆盖率门控（CVR-01~05 + 阈值表）
- §6.3 自动返工（上限2次 + 返工流程）
- §6.4 交互模式签核（Gate-1/2/3 + verdict取值 + 人工返工计数）
- WARNING 处理（2次后不阻断）
- 门控阈值汇总表（§5.2）

- [ ] **步骤 4：创建 ADAPTER_CONTRACT.md**

从 spec §9 + §5.3 提取：
- §9.1 requirement-provider 适配器（接口合约 + 默认实现 + 替换步骤 + 配置示例）
- §9.2 security-report-publisher 适配器（接口合约 + 默认实现 + 替换步骤）
- §9.3 环境变量命名规范（SECDESIGN_* 前缀表 + 安全要求）
- §9.4 LLM 模型要求（长上下文 + JSON输出 + 中文 + 安全知识 + 不绑定声明）

- [ ] **步骤 5：创建 AUDIT_LOG_SPEC.md**

从 spec §11 + §5.4 提取：
- 文件位置
- Schema完整示例（含Gate-1/2/3三条记录）
- 字段说明（顶层 + gates数组元素）
- 签核点定义（Gate-1/2/3的phase/审阅对象/verdict取值/人工返工目标）
- verdict取值说明（Gate-1/2: pass/pass_with_suggestions/rework/terminate; Gate-3: publish/not_publish）
- 版本标记规则（v1→v2→v3 + artifact_version对应关系）
- auto模式行为（gates为空 + manual_rework_count为0）
- 人工返工计数（独立计数 + 无上限）

- [ ] **步骤 6：验证5个文件创建正确**

```bash
ls -la SKILL.md skills/shared/
wc -l SKILL.md skills/shared/*.md
```
预期：5个文件存在，SKILL.md > 100行，每个shared文件 > 50行。

---

## 任务 3：Phase0 + Phase0.5 子 skill

**文件：**
- 创建：`secdesign/skills/requirement-provider/SKILL.md`（Phase0）
- 创建：`secdesign/skills/security-prescreen/SKILL.md`（Phase0.5）

- [ ] **步骤 1：创建 requirement-provider/SKILL.md（Phase0）**

从 spec §3.3 提取。格式：
- YAML frontmatter（name: requirement-provider, description: Phase0 需求获取）
- 功能描述
- 接口合约（输入requirement_id → 输出JSON）
- 默认实现（读取 .secdesign-data/{id}.json + 校验必需字段）
- 处理流程（读取→校验→写入requirement_info.json→更新security_graph.json）
- MUST 输出（requirement_context/requirement_info.json + security_graph.json含requirement节点）
- 套件根定位（Glob pattern引用）
- 红线

- [ ] **步骤 2：创建 security-prescreen/SKILL.md（Phase0.5）**

从 spec §3.4 提取。格式：
- YAML frontmatter（name: security-prescreen, description: Phase0.5 需求安全预检）
- 功能描述
- 输入/输出
- 处理流程（扫描关键词 → 匹配KL-1索引 → 判定粒度 → 判定安全面 → 估算威胁数）
- 关键词匹配规则（引用 rules/prescreen-keywords.md）
- 粒度自动判定规则（4条）
- 威胁数估算算法（Σ STRIDE适用数 ± 20%）
- 输出JSON格式（security_prescreen.json完整示例）
- 门控规则（skip/conditional/complex/proceed）
- MUST 输出

- [ ] **步骤 3：验证**

```bash
ls -la skills/requirement-provider/SKILL.md skills/security-prescreen/SKILL.md
```
预期：2个文件存在。

---

## 任务 4：Phase1 + Phase2 子 skill

**文件：**
- 创建：`secdesign/skills/attack-surface-identifier/SKILL.md`（Phase1）
- 创建：`secdesign/skills/threat-mapper/SKILL.md`（Phase2）

- [ ] **步骤 1：创建 attack-surface-identifier/SKILL.md（Phase1）**

从 spec §3.5 提取。格式：
- YAML frontmatter
- 功能：扫描需求，识别命中的攻击面子类，展开KL-1检查点
- 输入/输出
- 知识库引用（knowledge-bases/KL-1-checklist/）
- 处理流程（4步：读取matched_categories → 展开KL-1 → 文档处理流程 → 汇总）
- 设计文档处理流程（转换→分块→补充匹配→输出doc_chunks.json，含完整流程和JSON格式）
- KL-1文件格式说明（引用spec中的A3.2示例）
- 输出JSON格式（attack_surfaces.json完整示例）
- 降级策略（无文档时跳过）
- MUST 输出

- [ ] **步骤 2：创建 threat-mapper/SKILL.md（Phase2）**

从 spec §3.6 提取。格式：
- YAML frontmatter
- 功能：对每个攻击面套STRIDE，映射KL-5攻击模式，生成威胁列表
- 输入/输出
- 知识库引用（KL-2-stride/ + KL-5-attack-patterns/）
- 处理流程（6步：遍历STRIDE → 读KL-2模板 → 细化描述 → 映射KL-5 → 映射CWE/OWASP → DREAD评分）
- DREAD评分（1-5连续标尺，5维度表）
- 严重度映射（25分制 → S1/S2/S3/S4）
- 云环境多租户放大规则（3条）
- 输出JSON格式（threats.json完整示例）
- MUST 输出

- [ ] **步骤 3：验证**

```bash
ls -la skills/attack-surface-identifier/SKILL.md skills/threat-mapper/SKILL.md
```
预期：2个文件存在。

---

## 任务 5：Phase3 + Phase4 子 skill

**文件：**
- 创建：`secdesign/skills/security-spec-generator/SKILL.md`（Phase3）
- 创建：`secdesign/skills/coverage-checker/SKILL.md`（Phase4）

- [ ] **步骤 1：创建 security-spec-generator/SKILL.md（Phase3）**

从 spec §3.7 提取。格式：
- YAML frontmatter
- 功能：将威胁映射到KL-3/KL-4/KL-6检查点，生成安全规格文档
- 输入/输出
- 知识库引用（KL-3-owasp/ + KL-4-cwe/ + KL-6-compliance/）
- 安全规格模板（6章节完整大纲）
- 处理流程（读取威胁 → 映射KL-3/4/6 → 按模板生成6章节 → 输出MD+JSON）
- 输出（security_spec.md + security_spec.json + 图谱更新）
- MUST 输出

- [ ] **步骤 2：创建 coverage-checker/SKILL.md（Phase4）**

从 spec §3.8 提取。格式：
- YAML frontmatter
- 功能：检查攻击面×威胁×检查点的覆盖率
- 输入/输出
- 知识库引用（rules/coverage-rules.md）
- 覆盖率检查规则（CVR-01~05完整表，含执行时机列）
- 五态标记（Phase4后检查点维度 + Phase5后测试用例维度，两阶段表）
- 自动返工机制（上限2次 + 返工目标Phase + 记录audit_log）
- CVR-05执行时机说明（Phase5后Phase6前执行）
- 输出（coverage_report.md + coverage_findings.json + 图谱更新）
- MUST 输出

- [ ] **步骤 3：验证**

```bash
ls -la skills/security-spec-generator/SKILL.md skills/coverage-checker/SKILL.md
```
预期：2个文件存在。

---

## 任务 6：Phase5 + Phase6 子 skill

**文件：**
- 创建：`secdesign/skills/security-test-generator/SKILL.md`（Phase5）
- 创建：`secdesign/skills/security-review/SKILL.md`（Phase6）

- [ ] **步骤 1：创建 security-test-generator/SKILL.md（Phase5）**

从 spec §3.9 提取。格式：
- YAML frontmatter
- 功能：将安全检查点转化为可执行的安全测试用例
- 输入/输出
- 知识库引用（KL-4-cwe/ + KL-5-attack-patterns/ + KL-7-runtime/）
- 安全测试用例模板（完整Markdown模板：字段表+前置条件+攻击步骤+预期结果+验证方法+清理步骤）
- 测试用例分类（9类前缀表：UC-AUTH/AC/INP/FILE/CRYP/CONF/LOG/BUS/CONT）
- source字段说明（threat_derived/llm_inferred/rule_based）
- 自适应分批（威胁数>BATCH_THRESHOLD时按攻击面分组）
- CVR-05触发说明（生成后自检威胁测试用例覆盖率）
- 输出（security_tests.md + security_tests.json + 图谱更新）
- MUST 输出

- [ ] **步骤 2：创建 security-review/SKILL.md（Phase6）**

从 spec §3.10 提取。格式：
- YAML frontmatter
- 功能：评审安全测试用例的可执行性、可利用性和误报风险
- 输入/输出
- 评审维度（4维表：可执行性/可利用性/误报风险/攻击链）
- 攻击链验证（scope≥function时启用 + 边界说明：设计时分析 vs GenCPT执行时验证）
- 门控（可执行性≥70%，返工Phase5，上限2次）
- 输出（review_report.md + 图谱更新）
- MUST 输出

- [ ] **步骤 3：验证**

```bash
ls -la skills/security-test-generator/SKILL.md skills/security-review/SKILL.md
```
预期：2个文件存在。

---

## 任务 7：Phase7 子 skill

**文件：**
- 创建：`secdesign/skills/security-report-publisher/SKILL.md`（Phase7）

- [ ] **步骤 1：创建 security-report-publisher/SKILL.md（Phase7）**

从 spec §3.11 提取。格式：
- YAML frontmatter
- 功能：多格式输出安全报告和处置跟踪表
- 输入/输出
- 输出格式表（5格式：MD/Excel/SARIF/JSON/HTML，含文件名/内容/消费者）
- SARIF输出Schema映射（完整JSON示例 + level映射：S1/S2→error, S3→warning, S4→note）
- 处置跟踪表（Excel中的8列表）
- 处理流程（读取全部产物 → 生成各格式 → 调用scripts/*.py → 闭环校验 → 归档audit_log）
- Gate-3签核（interactive模式，publish/not_publish）
- 闭环校验（所有attack_surface和threat节点状态非⬜）
- 审计日志归档
- MUST 输出

- [ ] **步骤 2：验证**

```bash
ls -la skills/security-report-publisher/SKILL.md
```
预期：文件存在。

---

## 任务 8：rules/ 四个规则文件

**文件：**
- 创建：`secdesign/rules/prescreen-keywords.md`
- 创建：`secdesign/rules/coverage-rules.md`
- 创建：`secdesign/rules/review-rules.md`
- 创建：`secdesign/rules/severity-rules.md`

- [ ] **步骤 1：创建 prescreen-keywords.md**

从 spec §3.4 + 附录A 提取。内容：
- 32个攻击面子类的完整匹配关键词表（从附录A每个子类的"匹配关键词"行提取）
- 格式：| 攻击面子类 | 中文关键词 | 英文关键词 |
- 匹配规则说明（大小写不敏感，部分匹配，中英文双语）

- [ ] **步骤 2：创建 coverage-rules.md**

从 spec §3.8 提取。内容：
- CVR-01~05 完整规则定义（规则ID/检查维度/计算方式/阈值/不达标动作/执行时机）
- 五态标记定义（两阶段：Phase4后检查点维度 + Phase5后测试用例维度）
- 自动返工机制（上限2次 + 返工目标Phase映射 + audit_log记录）
- 返工流程（5步：读progress → 递增版本 → 传递findings → 重新调度 → 重新检查）

- [ ] **步骤 3：创建 review-rules.md**

从 spec §3.10 提取。内容：
- 4维评审规则（可执行性/可利用性/误报风险/攻击链）
- 每维的检查项和判定方式
- 可执行性阈值（≥70%）
- 攻击链验证规则（scope≥function时启用 + 构建规则）
- 返工规则（可执行性<70% → 返工Phase5，上限2次）

- [ ] **步骤 4：创建 severity-rules.md**

从 spec §3.6 提取。内容：
- DREAD评分标尺（5维度 × 1-5分完整表）
- 严重度映射（25分制 → S1(20-25)/S2(12-19)/S3(6-11)/S4(0-5)）
- 云环境多租户放大规则（3条：跨租户→affected_users=5, AK/SK→damage=5, system级S3→S2）
- SARIF level映射（S1/S2→error, S3→warning, S4→note）

- [ ] **步骤 5：验证**

```bash
ls -la rules/
wc -l rules/*.md
```
预期：4个文件，每个 > 30行。

---

## 任务 9：scripts/ 四个 Python 脚本

**文件：**
- 创建：`secdesign/scripts/json_to_sarif.py`
- 创建：`secdesign/scripts/json_to_excel.py`
- 创建：`secdesign/scripts/json_to_csv.py`
- 创建：`secdesign/scripts/graph_to_mermaid.py`

- [ ] **步骤 1：创建 json_to_sarif.py**

功能：读取 security_tests.json + security_graph.json → 输出 SARIF 2.1.0 格式。

```python
#!/usr/bin/env python3
"""Convert security_tests.json to SARIF 2.1.0 format."""
import json
import sys
import argparse
from pathlib import Path


def convert(tests_file: str, graph_file: str, output_file: str) -> None:
    with open(tests_file, "r", encoding="utf-8") as f:
        tests = json.load(f)
    with open(graph_file, "r", encoding="utf-8") as f:
        graph = json.load(f)

    severity_to_level = {"S1": "error", "S2": "error", "S3": "warning", "S4": "note"}

    results = []
    rules = {}
    for test in tests.get("test_cases", []):
        cwe = test.get("cwe", "CWE-Unknown")
        severity = test.get("severity", "S3")
        rule_id = cwe
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": test.get("cwe_name", cwe),
            }
        results.append({
            "ruleId": rule_id,
            "level": severity_to_level.get(severity, "warning"),
            "message": {"text": test.get("test_name", "")},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": f"requirement/{graph.get('requirement_id', 'unknown')}"
                    }
                },
                "logicalLocations": [{
                    "fullyQualifiedName": f"{test.get('attack_surface', '')}/attack_surface"
                }]
            }],
            "properties": {
                "threat_id": test.get("threat_id", ""),
                "stride_type": test.get("stride_type", ""),
                "dread_severity": severity,
                "owasp": test.get("owasp", ""),
                "checklist_id": test.get("checklist_id", ""),
            }
        })

    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "secdesign",
                    "version": "1.1",
                    "informationUri": "https://github.com/secdesign"
                }
            },
            "results": results,
            "taxonomies": [{
                "name": "CWE",
                "rules": list(rules.values())
            }]
        }]
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sarif, f, indent=2, ensure_ascii=False)
    print(f"SARIF written to {output_file} ({len(results)} results)")


def main():
    parser = argparse.ArgumentParser(description="Convert security_tests.json to SARIF")
    parser.add_argument("--tests", required=True, help="Path to security_tests.json")
    parser.add_argument("--graph", required=True, help="Path to security_graph.json")
    parser.add_argument("--output", required=True, help="Output SARIF file path")
    args = parser.parse_args()
    convert(args.tests, args.graph, args.output)


if __name__ == "__main__":
    main()
```

- [ ] **步骤 2：验证 json_to_sarif.py**

```bash
python3 -c "
import json, tempfile, os, sys
sys.path.insert(0, 'scripts')
from json_to_sarif import convert
tests = {'test_cases': [{'test_name': 'SQL注入测试', 'cwe': 'CWE-89', 'severity': 'S2', 'threat_id': 'T-001', 'stride_type': 'T', 'owasp': 'A03', 'attack_surface': 'A2.1'}]}
graph = {'requirement_id': 'REQ-001'}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(tests, f); tests_path = f.name
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(graph, f); graph_path = f.name
out = tempfile.mktemp(suffix='.sarif')
convert(tests_path, graph_path, out)
with open(out) as f: result = json.load(f)
assert result['version'] == '2.1.0'
assert len(result['runs'][0]['results']) == 1
assert result['runs'][0]['results'][0]['level'] == 'error'
print('PASS: json_to_sarif.py')
os.unlink(tests_path); os.unlink(graph_path); os.unlink(out)
"
```
预期：PASS: json_to_sarif.py

- [ ] **步骤 3：创建 json_to_excel.py**

功能：读取 security_tests.json → 输出 Excel 处置跟踪表。依赖 openpyxl。

```python
#!/usr/bin/env python3
"""Convert security_tests.json to Excel tracking sheet."""
import json
import sys
import argparse
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
except ImportError:
    print("ERROR: openpyxl not installed. Run: pip install openpyxl", file=sys.stderr)
    sys.exit(1)


def convert(tests_file: str, output_file: str) -> None:
    with open(tests_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    wb = Workbook()
    ws = wb.active
    ws.title = "安全检查点清单"

    headers = ["检查点ID", "检查点描述", "关联威胁", "CWE", "OWASP", "严重度", "状态", "责任人", "计划完成", "实际完成", "验证结果"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.font = Font(bold=True, color="FFFFFF")

    for test in data.get("test_cases", []):
        ws.append([
            test.get("checklist_id", ""),
            test.get("test_name", ""),
            test.get("threat_id", ""),
            test.get("cwe", ""),
            test.get("owasp", ""),
            test.get("severity", ""),
            "⬜待修复",
            "", "", "", ""
        ])

    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["G"].width = 12

    wb.save(output_file)
    print(f"Excel written to {output_file} ({ws.max_row - 1} rows)")


def main():
    parser = argparse.ArgumentParser(description="Convert security_tests.json to Excel")
    parser.add_argument("--tests", required=True, help="Path to security_tests.json")
    parser.add_argument("--output", required=True, help="Output Excel file path")
    args = parser.parse_args()
    convert(args.tests, args.output)


if __name__ == "__main__":
    main()
```

- [ ] **步骤 4：验证 json_to_excel.py**

```bash
pip install openpyxl -q 2>/dev/null; python3 -c "
import json, tempfile, os, sys
sys.path.insert(0, 'scripts')
from json_to_excel import convert
tests = {'test_cases': [{'test_name': '文件上传校验', 'cwe': 'CWE-434', 'severity': 'S2', 'threat_id': 'T-001', 'checklist_id': 'CL-001'}]}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(tests, f); tests_path = f.name
out = tempfile.mktemp(suffix='.xlsx')
convert(tests_path, out)
from openpyxl import load_workbook
wb = load_workbook(out)
ws = wb.active
assert ws.max_row == 2
assert ws.cell(1, 1).value == '检查点ID'
assert ws.cell(2, 6).value == 'S2'
print('PASS: json_to_excel.py')
os.unlink(tests_path); os.unlink(out)
"
```
预期：PASS: json_to_excel.py

- [ ] **步骤 5：创建 json_to_csv.py**

功能：读取 security_tests.json → 输出 CSV（UTF-8 with BOM）。

```python
#!/usr/bin/env python3
"""Convert security_tests.json to CSV (UTF-8 with BOM)."""
import json
import csv
import sys
import argparse


def convert(tests_file: str, output_file: str) -> None:
    with open(tests_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    headers = [
        "用例编号", "测试名称", "关联威胁", "攻击面", "CWE", "OWASP",
        "严重度", "攻击者角色", "前置条件", "攻击步骤", "预期结果", "验证方法"
    ]

    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for test in data.get("test_cases", []):
            writer.writerow([
                test.get("id", ""),
                test.get("test_name", ""),
                test.get("threat_id", ""),
                test.get("attack_surface", ""),
                test.get("cwe", ""),
                test.get("owasp", ""),
                test.get("severity", ""),
                test.get("attacker_role", ""),
                "; ".join(test.get("preconditions", [])),
                " | ".join(test.get("attack_steps", [])),
                "; ".join(test.get("expected_results", [])),
                "; ".join(test.get("verification", [])),
            ])

    print(f"CSV written to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Convert security_tests.json to CSV")
    parser.add_argument("--tests", required=True, help="Path to security_tests.json")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    args = parser.parse_args()
    convert(args.tests, args.output)


if __name__ == "__main__":
    main()
```

- [ ] **步骤 6：验证 json_to_csv.py**

```bash
python3 -c "
import json, tempfile, os, sys, csv
sys.path.insert(0, 'scripts')
from json_to_csv import convert
tests = {'test_cases': [{'id': 'UC-FILE-001', 'test_name': '文件上传Webshell', 'cwe': 'CWE-434', 'severity': 'S2'}]}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(tests, f); tests_path = f.name
out = tempfile.mktemp(suffix='.csv')
convert(tests_path, out)
with open(out, encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    rows = list(reader)
assert len(rows) == 2
assert rows[0][0] == '用例编号'
assert rows[1][0] == 'UC-FILE-001'
print('PASS: json_to_csv.py')
os.unlink(tests_path); os.unlink(out)
"
```
预期：PASS: json_to_csv.py

- [ ] **步骤 7：创建 graph_to_mermaid.py**

功能：读取 security_graph.json → 输出 HTML 追溯图（Mermaid 渲染）。

```python
#!/usr/bin/env python3
"""Convert security_graph.json to HTML traceability graph using Mermaid."""
import json
import sys
import argparse
from pathlib import Path


def convert(graph_file: str, output_file: str) -> None:
    with open(graph_file, "r", encoding="utf-8") as f:
        graph = json.load(f)

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    type_styles = {
        "requirement": ("req", "#4CAF50"),
        "security_assessment": ("assess", "#2196F3"),
        "attack_surface": ("surface", "#FF9800"),
        "threat": ("threat", "#F44336"),
        "security_check": ("check", "#9C27B0"),
        "security_test": ("test", "#00BCD4"),
        "finding": ("finding", "#795548"),
        "doc_chunk": ("doc", "#607D8B"),
    }

    mermaid_lines = ["graph TD"]

    for node in nodes:
        node_type = node.get("type", "unknown")
        node_id = node.get("id", "").replace("-", "_")
        name = node.get("name", node_id).replace('"', "'")
        prefix, color = type_styles.get(node_type, ("other", "#9E9E9E"))
        status = node.get("status", node.get("state", ""))
        label = f"{name}"
        if status:
            label += f" {status}"
        mermaid_lines.append(f'    {node_id}["{label}"]:::{prefix}')

    edge_labels = {
        "has_surface": "攻击面",
        "has_threat": "威胁",
        "traces_to": "追溯",
        "mapped_by": "映射",
        "covers": "覆盖",
        "checked_by": "检查",
        "published_as": "发布",
        "audited_by": "签核",
    }

    for edge in edges:
        src = edge.get("from", "").replace("-", "_")
        dst = edge.get("to", "").replace("-", "_")
        etype = edge.get("type", "")
        label = edge_labels.get(etype, etype)
        mermaid_lines.append(f"    {src} -->|{label}| {dst}")

    for prefix, color in type_styles.values():
        mermaid_lines.append(f"    classDef {prefix} fill:{color},color:white,stroke-width:2px")

    mermaid_code = "\n".join(mermaid_lines)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>secdesign 追溯图 - {graph.get('requirement_id', '')}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{ font-family: sans-serif; margin: 20px; background: #fafafa; }}
        h1 {{ color: #333; }}
        .mermaid {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <h1>secdesign 安全测试追溯图</h1>
    <p>需求编号: {graph.get('requirement_id', '')}</p>
    <div class="mermaid">
{mermaid_code}
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose' }});
    </script>
</body>
</html>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML graph written to {output_file} ({len(nodes)} nodes, {len(edges)} edges)")


def main():
    parser = argparse.ArgumentParser(description="Convert security_graph.json to HTML graph")
    parser.add_argument("--graph", required=True, help="Path to security_graph.json")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    args = parser.parse_args()
    convert(args.graph, args.output)


if __name__ == "__main__":
    main()
```

- [ ] **步骤 8：验证 graph_to_mermaid.py**

```bash
python3 -c "
import json, tempfile, os, sys
sys.path.insert(0, 'scripts')
from graph_to_mermaid import convert
graph = {
    'requirement_id': 'REQ-001',
    'nodes': [
        {'id': 'req-001', 'type': 'requirement', 'name': '文件上传功能', 'status': '✅'},
        {'id': 'as-001', 'type': 'attack_surface', 'name': 'A3.2文件上传', 'status': '✅'},
        {'id': 't-001', 'type': 'threat', 'name': '文件内容注入', 'status': '⚠️'}
    ],
    'edges': [
        {'from': 'req-001', 'to': 'as-001', 'type': 'has_surface'},
        {'from': 'as-001', 'to': 't-001', 'type': 'has_threat'}
    ]
}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(graph, f); graph_path = f.name
out = tempfile.mktemp(suffix='.html')
convert(graph_path, out)
with open(out) as f: html = f.read()
assert 'mermaid' in html
assert 'req_001' in html
assert 'graph TD' in html
print('PASS: graph_to_mermaid.py')
os.unlink(graph_path); os.unlink(out)
"
```
预期：PASS: graph_to_mermaid.py

---

## 任务 10：knowledge-bases/ 桩文件 + _index.md

**文件：**
- 创建：`secdesign/knowledge-bases/_index.md`
- 创建：`secdesign/knowledge-bases/KL-1-checklist/_index.md`
- 创建：`secdesign/knowledge-bases/KL-2-stride/_index.md`
- 创建：`secdesign/knowledge-bases/KL-3-owasp/_index.md`
- 创建：`secdesign/knowledge-bases/KL-4-cwe/_index.md`
- 创建：`secdesign/knowledge-bases/KL-5-attack-patterns/_index.md`
- 创建：`secdesign/knowledge-bases/KL-6-compliance/_index.md`
- 创建：`secdesign/knowledge-bases/KL-7-runtime/_index.md`
- 创建：`secdesign/knowledge-bases/_evolution/_index.md`
- 创建：`secdesign/knowledge-bases/_evolution/_learned/.keep`

- [ ] **步骤 1：创建 knowledge-bases/_index.md（总索引）**

从 spec §2.4 提取。内容：7个知识层总表（KL-1~KL-7，名称/来源/条目数/用途）+ 进化机制说明（§2.7）+ 目录链接。

- [ ] **步骤 2：创建 KL-1-checklist/_index.md**

从 spec §2.2 + 附录A 提取。内容：32个子类索引表（编号/名称/文件名/匹配关键词摘要/STRIDE适用）+ KL-1文件统一格式说明。

- [ ] **步骤 3：创建 KL-2-stride/_index.md**

从 spec §2.3 + 附录B 提取。内容：32子类×STRIDE完整映射表（即§2.3的表）+ 6个STRIDE文件说明 + 每个STRIDE的适用攻击面列表。

- [ ] **步骤 4：创建 KL-3-owasp/_index.md**

从 spec 附录C 提取。内容：OWASP Top10映射表 + API Security Top10映射表 + ASVS验证项表 + 3个子文件说明。

- [ ] **步骤 5：创建 KL-4-cwe/_index.md**

从 spec 附录D 提取。内容：CWE Top25完整表（排名/CWE/名称/映射攻击面/映射OWASP）+ top25.md文件说明。

- [ ] **步骤 6：创建 KL-5-attack-patterns/_index.md**

从 spec 附录E + §7 提取。内容：9个子目录说明（injection/authz/deser/data/dos/network/escape/persist/supply）+ 攻击模式统一格式 + 种子攻击模式索引（附录E的9个攻击模式）。

- [ ] **步骤 7：创建 KL-6-compliance/_index.md**

从 spec 附录F 提取。内容：10个子文件说明（G1~G7 + k8s/docker/containerd）+ 合规规则格式 + 种子规则索引（附录F的规则表）。

- [ ] **步骤 8：创建 KL-7-runtime/_index.md**

从 spec 附录G 提取。内容：WSTG测试项索引表 + ATT&CK容器/云战术表 + 2个子文件说明。

- [ ] **步骤 9：创建 _evolution/_index.md**

从 spec §2.7 提取。内容：进化规则（发现新攻击→写模式→映射→写入KL-5→更新索引 + 新标准→增加KL目录→更新总索引）+ _learned/目录说明。

- [ ] **步骤 10：创建 _learned/.keep**

```
# 此目录存放新发现的攻击模式，由进化机制自动写入
```

- [ ] **步骤 11：验证全部桩文件**

```bash
find knowledge-bases/ -name "*.md" -o -name ".keep" | sort
```
预期：10个文件存在。

---

## 任务 11：agents/secdesign-supervisor.md

**文件：**
- 创建：`secdesign/agents/secdesign-supervisor.md`

- [ ] **步骤 1：创建 secdesign-supervisor.md**

交互模式签核协调 agent。内容：
- 角色描述（交互模式下协调Gate-1/2/3签核）
- 职责（展示审阅对象 → 询问裁决 → 记录audit_log → 处理返工/终止）
- Gate-1/2/3 审阅对象和verdict取值（引用QUALITY_GATES.md）
- 签核记录格式（引用AUDIT_LOG_SPEC.md）
- 人工返工计数规则

- [ ] **步骤 2：验证**

```bash
ls -la agents/secdesign-supervisor.md
```
预期：文件存在。

---

## 任务 12：端到端验证

- [ ] **步骤 1：创建演示需求数据**

```bash
mkdir -p .secdesign-data
```

创建 `.secdesign-data/REQ-DEMO-001.json`：

```json
{
  "requirement_id": "REQ-DEMO-001",
  "requirement_name": "文件上传功能",
  "description": "实现用户头像上传功能。支持 jpg/png/gif 格式，最大 5MB。上传后显示在用户资料页。",
  "acceptance_criteria": "1. 支持 jpg/png/gif 格式\n2. 最大 5MB\n3. 上传后显示头像\n4. 可重新上传替换",
  "scope": "interface",
  "priority": "Medium",
  "design_docs": []
}
```

- [ ] **步骤 2：验证目录结构完整性**

```bash
echo "=== 检查所有必需文件 ===" && \
for f in SKILL.md README.md .gitignore \
         skills/shared/OUTPUT_STANDARD.md \
         skills/shared/QUALITY_GATES.md \
         skills/shared/ADAPTER_CONTRACT.md \
         skills/shared/AUDIT_LOG_SPEC.md \
         skills/requirement-provider/SKILL.md \
         skills/security-prescreen/SKILL.md \
         skills/attack-surface-identifier/SKILL.md \
         skills/threat-mapper/SKILL.md \
         skills/security-spec-generator/SKILL.md \
         skills/coverage-checker/SKILL.md \
         skills/security-test-generator/SKILL.md \
         skills/security-review/SKILL.md \
         skills/security-report-publisher/SKILL.md \
         rules/prescreen-keywords.md \
         rules/coverage-rules.md \
         rules/review-rules.md \
         rules/severity-rules.md \
         scripts/json_to_sarif.py \
         scripts/json_to_excel.py \
         scripts/json_to_csv.py \
         scripts/graph_to_mermaid.py \
         knowledge-bases/_index.md \
         knowledge-bases/KL-1-checklist/_index.md \
         knowledge-bases/KL-2-stride/_index.md \
         knowledge-bases/KL-3-owasp/_index.md \
         knowledge-bases/KL-4-cwe/_index.md \
         knowledge-bases/KL-5-attack-patterns/_index.md \
         knowledge-bases/KL-6-compliance/_index.md \
         knowledge-bases/KL-7-runtime/_index.md \
         knowledge-bases/_evolution/_index.md \
         agents/secdesign-supervisor.md; do
  if [ -f "$f" ]; then echo "✅ $f"; else echo "❌ MISSING: $f"; fi
done
```
预期：全部 ✅，无 ❌。

- [ ] **步骤 3：验证4个脚本可执行**

```bash
for script in scripts/*.py; do
  python3 -c "import sys; sys.path.insert(0, 'scripts'); exec(open('$script').read())" 2>&1 | head -1
  echo "✅ $script 可加载"
done
```
预期：4个脚本均可加载。

- [ ] **步骤 4：统计文件数和总行数**

```bash
echo "=== 文件统计 ===" && \
find . -name "*.md" -not -path "./.secdesign-*" -not -path "./docs/*" | wc -l && \
echo "MD files" && \
find . -name "*.py" -not -path "./.secdesign-*" | wc -l && \
echo "PY files" && \
find . -name "*.md" -not -path "./.secdesign-*" -not -path "./docs/*" -exec cat {} + | wc -l && \
echo "total MD lines"
```
预期：~35 MD files, 4 PY files, ~3000+ total MD lines。

- [ ] **步骤 5：Commit（如已初始化git）**

```bash
git init 2>/dev/null; git add -A && git commit -m "feat: secdesign 核心框架 — 9 Phase skills + shared + rules + scripts + 知识层桩"
```

---

## 自检结果

### 规格覆盖度

| 规格章节 | 覆盖任务 | 状态 |
|---------|---------|------|
| §0 SKILL.md入口 | 任务2 | ✅ |
| §1 项目定位 | 任务1 README | ✅ |
| §2 安全知识全景 | 任务10 _index.md桩文件 | ✅（桩，Plan 2填充） |
| §3 Pipeline设计（9 Phase） | 任务3-7 | ✅ |
| §4 知识图谱Schema | 任务2 OUTPUT_STANDARD | ✅ |
| §5 共享规范 | 任务2 shared/4文件 | ✅ |
| §6 质量门控 | 任务2 QUALITY_GATES | ✅ |
| §7 输出标准 | 任务2 OUTPUT_STANDARD | ✅ |
| §8 知识库目录 | 任务10 桩文件 | ✅（桩，Plan 2填充） |
| §9 适配器接口 | 任务2 ADAPTER_CONTRACT | ✅ |
| §10 并发写入协议 | 任务2 OUTPUT_STANDARD | ✅ |
| §11 审计日志 | 任务2 AUDIT_LOG_SPEC | ✅ |
| 附录A-G 知识层内容 | Plan 2 | ⏳（不在本计划范围） |

### 占位符扫描

无 TODO/待定/TBD。知识层桩文件的 _index.md 包含种子内容（从附录提取），完整内容在 Plan 2 填充。

### 类型一致性

- security_graph.json 节点/边类型在 OUTPUT_STANDARD.md、各Phase SKILL.md、scripts 中一致使用
- CVR-01~05 规则ID在 coverage-checker/SKILL.md、rules/coverage-rules.md、QUALITY_GATES.md 中一致
- Gate-1/2/3 在 SKILL.md、QUALITY_GATES.md、AUDIT_LOG_SPEC.md、agents/supervisor.md 中一致
- 环境变量 SECDESIGN_* 在 ADAPTER_CONTRACT.md、SKILL.md 中一致
