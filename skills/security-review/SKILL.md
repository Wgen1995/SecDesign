---
name: security-review
description: Use when reviewing security test cases for executability, exploitability, false positive risk, and attack chains. Gates on executability >= 70% with Phase5 rework per QUALITY_GATES.md.
---

# 安全评审 (Phase6)

## 概述

评审安全测试用例的可执行性、可利用性和误报风险。对 scope ≥ function 的需求启用攻击链验证（设计时分析，非执行时验证）。依据可执行性得分判定门控，不达标时返工 Phase5。

## 套件根定位

首次执行前用 Glob 工具定位套件根：

```
Glob pattern: **/secdesign/SKILL.md
```

第一个命中路径的父目录即为套件根。

## MUST 输入/输出

参考 `{套件根}/skills/shared/OUTPUT_STANDARD.md` §6：

| 项目 | 内容 |
|------|------|
| MUST 输入 | `security_tests/security_tests.json` + `security_spec/security_spec.json` |
| MUST 输出 | `review/review_report.md` + `json_file/security_graph.json`（含 finding 节点） |

## 知识库引用

- `{套件根}/rules/review-rules.md`（评审维度规则）
- `{套件根}/skills/shared/QUALITY_GATES.md` §4 门控阈值

## 评审维度

| 维度 | 检查项 | 判定方式 |
|------|--------|---------|
| 可执行性 | 步骤可操作、预期可验证、清理完整 | 规则+LLM裁决 |
| 可利用性 | 威胁是否有可利用的攻击路径 | LLM裁决+攻击模式匹配 |
| 误报风险 | 测试用例是否可能产生误报 | LLM裁决 |
| 攻击链 | 多个中低危威胁是否可串联（scope ≥ function 时） | LLM推理 |

### 可执行性检查项

- 步骤可操作：每步是具体动作，无模糊表述（如"适当操作""合理输入"）
- 预期可验证：预期安全行为可观察、可量化、可判定 pass/fail
- 清理完整：清理步骤能恢复测试前状态，不残留测试数据

### 可利用性检查项

- 威胁有明确攻击路径（Source → ... → Sink）
- 攻击 payload 可构造（来自 KL-5 攻击模式）
- 攻击者角色合理（权限/位置与威胁场景匹配）

### 误报风险检查项

- 预期结果是否过于宽泛（可能导致多种行为都"通过"）
- 验证方法是否依赖特定环境（环境差异导致误报）
- 测试数据是否可能触发非目标行为（连带效应）

## 攻击链验证

scope ≥ function 时启用：

1. 识别可串联的多个威胁
2. 构建攻击链（如：未授权访问→敏感信息泄露→命令注入）
3. 生成攻击链测试用例
4. 记录攻击链到 review_report.md

**边界说明**：secdesign 的攻击链是设计时分析（纸面推导），不执行实际攻击。执行时验证由渗透测试工具（如 GenCPT）负责，secdesign 的输出作为渗透测试的输入。

## 处理流程

1. 读取 `.secdesign_output/{requirement_id}/security_tests/security_tests.json`
2. 读取 `.secdesign_output/{requirement_id}/security_spec/security_spec.json`
3. 读取 `{套件根}/rules/review-rules.md`
4. 读取 `{套件根}/skills/shared/QUALITY_GATES.md` §4 门控阈值
5. 按四维逐条评审每个测试用例：
   - 可执行性：检查步骤/预期/清理
   - 可利用性：检查攻击路径和 payload
   - 误报风险：检查预期宽泛性和环境依赖
   - 攻击链（scope ≥ function）：识别可串联威胁，构建攻击链
6. 每个问题记录：维度 + severity（major/minor/info）+ 问题描述 + 改进建议
7. 生成 `review/review_report.md`
8. 判定门控（可执行性 ≥ 70%）

## 门控判定

依据 `{套件根}/skills/shared/QUALITY_GATES.md` §4.2：

| 条件 | 动作 |
|------|------|
| 可执行性 ≥ 70% | 门控通过，继续 Phase7 |
| 可执行性 < 70% 且 phase5 返工次数 < 2 | 返工 Phase5，返工次数 +1 |
| 可执行性 < 70% 且 phase5 返工次数 ≥ 2 | 标记 WARNING，继续 Phase7 |

## 返工流程

依据 QUALITY_GATES.md §4：

1. 读取 progress.json，将 `rework_count.phase5` +1
2. 递增 security_tests.json 的 artifact_version
3. 将可执行性 findings 中 severity == "major" 的问题作为返工输入传递给 Phase5
4. 重新调度 Phase5 → Phase6
5. 重新检查门控

## 输出格式

review_report.md：

```markdown
# 安全评审报告

## 基本信息

| 项目 | 内容 |
|------|------|
| 需求编号 | REQ-001 |
| 测试用例总数 | 15 |
| 评审时间 | 2026-07-23T16:45:00 |

## 可执行性评审（阈值 ≥ 70%）

| 检查项 | 通过数 | 总数 | 通过率 |
|--------|--------|------|--------|
| 步骤可操作 | 14 | 15 | 93.3% |
| 预期可验证 | 15 | 15 | 100% |
| 清理完整 | 13 | 15 | 86.7% |
| **汇总** | 42 | 45 | **93.3%** |

### 可执行性问题清单

| 问题ID | 用例编号 | 检查项 | 严重级别 | 问题描述 | 改进建议 |
|--------|---------|--------|---------|---------|---------|
| F-EX-01 | UC-FILE-003 | 步骤可操作 | minor | 步骤3"构造恶意文件"未给出具体payload | 明确为test.jsp含<%Runtime.exec()%> |

## 可利用性评审（记录）

| 检查项 | 结果 |
|--------|------|
| 攻击路径完整性 | 100% (15/15) |
| Payload可构造性 | 93.3% (14/15) |
| 攻击者角色合理性 | 100% (15/15) |

## 误报风险评审（记录）

| 检查项 | 结果 |
|--------|------|
| 预期宽泛风险 | 1 条（UC-LOG-001 预期"日志正确"过于宽泛） |
| 环境依赖风险 | 0 条 |
| 连带效应风险 | 0 条 |

## 攻击链分析（scope ≥ function 时）

| 攻击链ID | 串联威胁 | 攻击路径 | 影响 |
|----------|---------|---------|------|
| CHAIN-01 | T-003→T-001→T-005 | 未授权访问→文件上传→命令执行 | RCE |

## 汇总得分

| 维度 | 得分 | 阈值 | 判定 |
|------|------|------|------|
| 可执行性 | 93.3% | ≥ 70% | ✅ 通过 |
| 可利用性 | 97.8% | — | — |
| 误报风险 | 记录 | — | — |
| 攻击链 | 1 条 | — | — |
```

## 更新知识图谱

读取 `.secdesign_output/{requirement_id}/json_file/security_graph.json`，追加：

**finding 节点**（dimension 标四维之一）：

```json
{
  "id": "f-rev-01",
  "type": "finding",
  "target_id": "st-003",
  "dimension": "executability",
  "verdict": "fail",
  "severity": "minor",
  "rule_id": null,
  "status": "⚠️"
}
```

**checked_by 边**（finding → security_test）：

```json
{
  "from": "f-rev-01",
  "to": "st-003",
  "type": "checked_by",
  "attrs": { "rule": "executability" }
}
```

写回 security_graph.json（独占写入，参考 OUTPUT_STANDARD.md §7）。

## 更新 progress.json

- 门控通过 → `phases.phase6` = `"completed"`
- 触发返工 → `phases.phase6` = `"rework"`，`rework_count.phase5` +1
- WARNING → `phases.phase6` = `"WARNING"`

## 红线

- 四维必须逐一检查，不可跳过
- 问题必须标明所属维度（executability / exploitability / false_positive / attack_chain）
- 改进建议必须具体可操作（指明修改哪个用例的哪个字段）
- 攻击链验证是设计时分析，不执行实际攻击
- 可执行性 findings 中 severity == "major" 的问题作为返工输入，minor/info 不触发返工
- dimension 字段使用英文（executability/exploitability/false_positive/attack_chain），与 finding 节点一致
