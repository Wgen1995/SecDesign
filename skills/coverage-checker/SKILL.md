---
name: coverage-checker
description: Use when checking attack surface x threat x checkpoint coverage rates. Runs CVR-01~04 rules with auto-rework mechanism, tracks five-state markers, and gates per QUALITY_GATES.md.
---

# 覆盖率检查 (Phase4)

## 概述

检查攻击面×威胁×检查点的覆盖率是否达标。执行 CVR-01~04 覆盖率规则，更新攻击面五态标记，判定门控。不达标时触发自动返工（上限 2 次），返工目标 Phase 由 finding 决定。

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
| MUST 输入 | `security_spec/security_spec.json` + `attack_surfaces/attack_surfaces.json` + `threats/threats.json` |
| MUST 输出 | `coverage/coverage_report.md` + `coverage/coverage_findings.json` + `json_file/security_graph.json`（含 finding 节点 + checked_by 边） |

## 知识库引用

- `{套件根}/rules/coverage-rules.md`（CVR-01~05 覆盖率规则）

## 覆盖率检查规则

| 规则ID | 检查维度 | 计算方式 | 阈值 | 不达标动作 | 执行时机 |
|--------|---------|---------|------|-----------|---------|
| CVR-01 | 攻击面覆盖率 | 有检查点的攻击面数 / 总攻击面数 | ≥ 90% | 返工 Phase3 补检查点 | Phase4 |
| CVR-02 | 威胁检查点覆盖率 | 有检查点的威胁数 / 总威胁数 | ≥ 90% | 返工 Phase3 补检查点 | Phase4 |
| CVR-03 | STRIDE覆盖率 | 每个攻击面已分析STRIDE数 / 适用STRIDE数 | ≥ 80%（系统级 100%） | 返工 Phase2 补威胁 | Phase4 |
| CVR-04 | 五态检查 | 所有攻击面的状态 | 无 ⬜ | 返工对应 Phase | Phase4 |
| CVR-05 | 威胁测试用例覆盖率 | 有测试用例的威胁数 / 总威胁数 | ≥ 90% | 返工 Phase5 补用例 | Phase5 后（Phase6 前） |

**注意**：CVR-05 在 Phase5 后、Phase6 前执行。本 Phase 执行 CVR-01~04，CVR-05 由 Phase5 完成后触发。

## 五态标记

分两个阶段判定。本 Phase 执行 Phase4 后（检查点维度）的判定：

### Phase4 后（检查点维度）

| 标记 | 含义 | 判定条件 |
|------|------|---------|
| ✅ | 已覆盖 | 攻击面有检查点 |
| ❌ | 未覆盖 | 攻击面无检查点 |
| ❓ | 待确认 | 需求不明确，无法判定 |
| ⬜ | 未评估 | 尚未执行 Phase4 |

### Phase5 后（测试用例维度，在 Phase4 状态基础上升级）

| 标记 | 含义 | 判定条件 |
|------|------|---------|
| ✅ | 完全覆盖 | 攻击面有检查点 且 威胁有测试用例 |
| ⚠️ | 部分覆盖 | 攻击面有检查点 但 威胁缺测试用例 |
| ❌ | 未覆盖 | 攻击面无检查点 |
| ❓ | 待确认 | 需求不明确 |
| ⬜ | 未评估 | Phase7 要求清零 |

## 处理流程

1. 读取 `.secdesign_output/{requirement_id}/security_spec/security_spec.json`
2. 读取 `.secdesign_output/{requirement_id}/attack_surfaces/attack_surfaces.json`
3. 读取 `.secdesign_output/{requirement_id}/threats/threats.json`
4. 读取 `{套件根}/rules/coverage-rules.md`
5. 读取 `{套件根}/skills/shared/QUALITY_GATES.md` §2 门控阈值
6. 逐条执行 CVR-01~04 检查：
   - CVR-01：统计有检查点的攻击面数 / 总攻击面数
   - CVR-02：统计有检查点的威胁数 / 总威胁数
   - CVR-03：对每个攻击面，统计已分析 STRIDE 数 / 适用 STRIDE 数
   - CVR-04：检查所有攻击面状态，⬜ 为不达标
7. 更新攻击面五态标记（✅/❌/❓）
8. 记录 findings 到 coverage_findings.json
9. 生成 coverage_report.md
10. 判定门控（依据 QUALITY_GATES.md §2.2）

## 自动返工机制

- 返工次数上限：2 次
- 返工目标 Phase 由 finding 决定：
  - CVR-01/CVR-02/CVR-04 → Phase3
  - CVR-03 → Phase2
- 每次返工记录到 audit_log.json
- 2 次返工后仍不达标：标记 WARNING，继续执行（不阻断）

### 返工流程

1. 读取 progress.json，将对应 `rework_count.{phase}` +1
2. 递增 security_spec.md 的 artifact_version（v1 → v2 → v3）
3. 将 coverage_findings 中 severity == "major" 的问题作为返工输入传递给目标 Phase
4. 重新调度目标 Phase → Phase4
5. 重新检查门控

## 输出格式

coverage_findings.json：

```json
{
  "requirement_id": "REQ-001",
  "findings": [
    {
      "id": "f-cvr-01",
      "rule_id": "CVR-01",
      "severity": "major",
      "target": "AS-002",
      "dimension": "coverage",
      "verdict": "fail",
      "description": "攻击面 AS-002 无检查点",
      "suggestion": "返工 Phase3 补充 AS-002 的安全检查点"
    }
  ],
  "summary": {
    "cvr_01": {"rate": 92, "threshold": 90, "verdict": "pass"},
    "cvr_02": {"rate": 88, "threshold": 90, "verdict": "fail"},
    "cvr_03": {"rate": 85, "threshold": 80, "verdict": "pass"},
    "cvr_04": {"verdict": "pass"}
  }
}
```

## 更新知识图谱

读取 `.secdesign_output/{requirement_id}/json_file/security_graph.json`，追加：

**finding 节点**：

```json
{
  "id": "f-cvr-01",
  "type": "finding",
  "target_id": "as-002",
  "dimension": "coverage",
  "verdict": "fail",
  "rule_id": "CVR-01",
  "severity": "major",
  "status": "❌"
}
```

**checked_by 边**（finding → security_check 或 attack_surface）：

```json
{
  "from": "f-cvr-01",
  "to": "as-002",
  "type": "checked_by",
  "attrs": { "rule": "CVR-01" }
}
```

同时更新 attack_surface 节点的 state 字段（⬜ → ✅/❌/❓）。

写回 security_graph.json（独占写入，参考 OUTPUT_STANDARD.md §7）。

## 更新 progress.json

- 门控通过 → `phases.phase4` = `"completed"`
- 触发返工 → `phases.phase4` = `"rework"`，`rework_count.phase2` 或 `rework_count.phase3` +1
- WARNING → `phases.phase4` = `"WARNING"`

## 红线

- CVR-01~04 必须逐一检查，不可跳过
- 每条 finding 必须引用具体的攻击面/威胁/检查点 ID
- 五态标记必须更新到 security_graph.json 的 attack_surface 节点
- **禁止并行写 security_graph.json**：findings 写入 coverage_findings.json 后串行汇总到 graph
- 返工输入仅传递 severity == "major" 的问题，minor/info 不触发返工
- CVR-05 不在本 Phase 执行（在 Phase5 后由 Phase5 触发自检）
