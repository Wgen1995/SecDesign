---
name: secdesign
description: Use when performing end-to-end security test design from a requirement ID. Automatically generates attack surface analysis, threat model, security specification, and executable security test cases with coverage tracking, traceability graph, and audit logging.
---

# AI安全测试设计

输入需求编号，自动完成 需求获取→安全预检→攻击面识别→威胁建模→安全规格→覆盖率检查→安全测试用例→评审→报告。

## §0 套件根定位

本套件用相对套件根的路径引用知识库与规则库。

LLM 在每个子 Phase 第一次 Read 任何相对引用前必先用 Glob 工具定位套件根：

```
Glob pattern: **/secdesign/SKILL.md
```

第一个命中路径的父目录就是套件根。所有后续 Read 把套件根绝对路径前缀拼到原引用前。

## 参数格式

| 名称 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| requirement_id | string | 是 | — | 需求唯一标识 |
| requirement_name | string | 否 | — | 需求名称（显示用） |
| mode | string | 否 | auto | `auto`/`interactive` |
| reviewer | string | 否 | env `SECDESIGN_REVIEWER` | 交互模式签核人 |
| scope | string | 否 | auto | `interface`/`function`/`module`/`system`/`auto` |
| format | string | 否 | all | `md`/`json`/`csv`/`excel`/`graph`/`sarif`/`all`/组合 |
| force | boolean | 否 | false | 跳过 Phase0.5 预门 |

## 第一步：参数收集

从 $ARGUMENTS 提取 requirement_id、requirement_name、mode、reviewer、scope、format、force。
如果未提供 requirement_id，向用户询问。

## 第二步：初始化工作目录

创建 `.secdesign_output/{requirement_id}/` 完整目录结构：

```
.secdesign_output/{requirement_id}/
├── requirement_context/
├── design_doc/
├── design_doc_markdown/
├── doc_chunks/
├── attack_surfaces/
├── threats/
├── security_spec/
├── coverage/
├── security_tests/
├── review/
├── report/
└── json_file/
```

初始化 security_graph.json：

```json
{
  "requirement_id": "{requirement_id}",
  "version": "1.1",
  "nodes": [],
  "edges": []
}
```

初始化 progress.json：

```json
{
  "requirement_id": "{requirement_id}",
  "current_phase": 0,
  "mode": "{mode}",
  "scope": "{scope}",
  "rework_count": {"phase2": 0, "phase3": 0, "phase5": 0},
  "manual_rework_count": {"phase2": 0, "phase3": 0, "phase5": 0},
  "artifact_versions": {"security_spec": "v1", "security_tests": "v1"},
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

初始化 audit_log.json：

```json
{
  "requirement_id": "{requirement_id}",
  "mode": "{mode}",
  "gates": [],
  "manual_rework_count": {"phase2": 0, "phase3": 0, "phase5": 0}
}
```

## 第三步：调度 Phase 子 skill

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

每个 Phase 完成后：
1. 校验 MUST 输出文件是否存在
2. 更新 progress.json

## 第四步：质量门控

**Phase0.5 完成后**：读取 `requirement_context/security_prescreen.json`，按 verdict 判定。
- verdict == "skip" → 跳过 Phase1-2，Phase3 标记"无安全面"
- verdict == "conditional" → 提示补充架构文档，询问继续或暂停
- verdict == "complex" → 建议拆分需求，询问继续或拆分
- verdict == "proceed" 或 force == true → 继续 Phase1

**Phase4 完成后**：读取 coverage 报告，检查 CVR-01~04。
- CVR-01 攻击面覆盖率 < 90% 且 phase3 返工次数 < 2 → 返工 Phase3
- CVR-02 威胁检查点覆盖率 < 90% 且 phase3 返工次数 < 2 → 返工 Phase3
- CVR-03 STRIDE覆盖率 < 80%（系统级 < 100%）且 phase2 返工次数 < 2 → 返工 Phase2
- CVR-04 存在 ⬜ 未评估 → 返工对应 Phase
- 超过2次则标记 WARNING 继续

**Phase5 完成后**：检查 CVR-05 威胁测试用例覆盖率。
- CVR-05 < 90% 且 phase5 返工次数 < 2 → 返工 Phase5
- 超过2次则标记 WARNING 继续

**Phase6 完成后**：读取 `review/review_report.md`，判定可执行性。
- 可执行性 < 70% 且 phase5 返工次数 < 2 → 返工 Phase5
- 超过2次则标记 WARNING 继续

门控阈值定义在 skills/shared/QUALITY_GATES.md。

## 第五步：人工签核点（仅 interactive 模式）

如果 mode == "interactive"，在以下位置暂停等待用户裁决：

**Gate-1（Phase4 完成后）**：展示覆盖率报告+攻击面/威胁清单，询问 [1]通过 [2]带建议通过 [3]返工 [4]终止
**Gate-2（Phase6 完成后）**：展示评审报告+安全测试用例，询问 [1]通过 [2]带建议通过 [3]返工 [4]终止
**Gate-3（Phase7 发布前）**：展示最终报告+全部产物+覆盖率摘要，询问 [1]发布 [2]不发布

每次签核记录到 audit_log.json：reviewer/timestamp/verdict/artifact_version/comment/manual_rework_triggered/rework_target_phase。
人工返工不计入自动返工的2次计数，单独计入 manual_rework_count。
签核点完整定义见 skills/shared/AUDIT_LOG_SPEC.md。

## 第六步：汇总

读取 security_graph.json，统计：
- 攻击面数量、威胁数量、检查点数量、测试用例数量
- 覆盖率（攻击面覆盖率、威胁覆盖率、STRIDE覆盖率）
- 威胁分布（S1/S2/S3/S4）
- 质量问题数量（自动返工 + 人工返工）

输出最终摘要：

```
安全测试设计完成！

需求: {requirement_id} "{requirement_name}"
模式: {mode} | 签核人: {reviewer} | 签核点: Gate-1{verdict} Gate-2{verdict} Gate-3{verdict}

攻击面: {n}个 | 威胁: {n}个 | 检查点: {n}个 | 测试用例: {n}个
覆盖率: 攻击面{p}% 威胁{p}% STRIDE{p}%
威胁分布: S1:{n} S2:{n} S3:{n} S4:{n}
质量问题: 自动返工{n}次 | 人工返工{n}次

输出目录: .secdesign_output/{requirement_id}/
产物: MD / JSON / CSV / Excel / SARIF / 追溯图(security_graph_viz.html)
审计日志: .secdesign_output/{requirement_id}/json_file/audit_log.json
```

## 红线

- 不编造需求中没有的攻击面
- 不跳过质量门控
- 不并行写入 security_graph.json
- 每个 Phase 完成后必须校验 MUST 输出
- 返工不超过2次（自动），人工返工单独计数
- 不修改原始需求内容
- DREAD评分/覆盖率检查必须附理由
- 不阻塞用户强制继续（--force）
