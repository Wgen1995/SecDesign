# 审计日志规范（AUDIT_LOG_SPEC）

> 本文件定义 secdesign 套件的审计日志文件位置、Schema、签核点定义、版本标记规则与自动/人工返工计数机制。

## 1. 文件位置

```
.secdesign_output/{requirement_id}/json_file/audit_log.json
```

审计日志在 Phase0 初始化时创建，Phase7 发布时最终归档。interactive 模式下每次签核追加记录；auto 模式下 gates 数组为空。

## 2. Schema

### 2.1 完整示例

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

### 2.2 字段说明

**顶层字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| requirement_id | string | 需求唯一标识 |
| mode | string | 运行模式（auto/interactive） |
| gates | array | 签核记录数组（auto 模式为空） |
| manual_rework_count | object | 人工返工计数（按 phase 分计，无上限） |

**gates 数组元素字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| gate | string | 签核点标识：Gate-1 / Gate-2 / Gate-3 |
| phase | string | 对应 Phase：after-Phase4 / after-Phase6 / after-Phase7 |
| reviewer | string | 签核人（来自参数或环境变量 SECDESIGN_REVIEWER） |
| timestamp | string | ISO 8601 时间戳 |
| verdict | string | 裁决结果（见 §3） |
| artifact_version | string | 被审阅产物版本（见 §4） |
| comment | string | 签核意见 |
| manual_rework_triggered | boolean | 是否触发人工返工 |
| rework_target_phase | string/null | 返工目标 Phase（如触发返工，否则 null） |

## 3. 签核点定义

| 签核点 | phase 字段 | 审阅对象 | verdict 取值 | 人工返工目标 |
|--------|-----------|---------|-------------|-------------|
| Gate-1 | after-Phase4 | 覆盖率报告+攻击面/威胁清单 | pass / pass_with_suggestions / rework / terminate | rework → phase2 或 phase3 |
| Gate-2 | after-Phase6 | 评审报告+安全测试用例 | pass / pass_with_suggestions / rework / terminate | rework → phase5 |
| Gate-3 | after-Phase7 | 最终报告+全部产物+覆盖率摘要 | publish / not_publish | — |

### 3.1 verdict 取值说明

**Gate-1 / Gate-2**

| verdict | 含义 | 后续动作 |
|---------|------|---------|
| pass | 通过 | 继续下一 Phase |
| pass_with_suggestions | 带建议通过 | 继续下一 Phase，建议记录到 comment |
| rework | 返工 | 人工返工，计数 +1，重新调度返工目标 Phase |
| terminate | 终止 | 终止整个流程 |

**Gate-3**

| verdict | 含义 | 后续动作 |
|---------|------|---------|
| publish | 发布 | 执行发布，归档审计日志 |
| not_publish | 不发布 | 终止发布，保留产物但不归档 |

## 4. 版本标记规则

### 4.1 版本格式

```
v1 → v2 → v3 → ...
```

每次返工（自动或人工）递增版本号。

### 4.2 artifact_version 对应关系

| 产物 | 初始版本 | 返工时递增 |
|------|---------|-----------|
| security_spec.md | v1 | Phase3 每次返工 +1 |
| security_tests.json | v1 | Phase5 每次返工 +1 |

### 4.3 版本记录位置

- progress.json 的 `artifact_versions` 字段记录每个产物的当前版本
- audit_log.json 中每条 gate 记录的 `artifact_version` 字段记录被审阅时的版本

### 4.4 示例

```
首次生成 spec → v1
Gate-1 返工 → Phase3 重新生成 → v2
Gate-1 通过（审阅 v2）
首次生成 tests → v1
Gate-2 返工 → Phase5 重新生成 → v2
Gate-2 通过（审阅 v2）
Gate-3 发布（审阅 v2）
```

## 5. auto 模式行为

当 `mode == "auto"` 时：

- gates 数组为空：`"gates": []`
- 不暂停等待人工签核
- 自动按门控阈值判定（见 QUALITY_GATES.md）
- 自动返工计入 `rework_count`（progress.json）
- manual_rework_count 始终为 0：`"manual_rework_count": {"phase2": 0, "phase3": 0, "phase5": 0}`

## 6. 人工返工计数

### 6.1 独立计数

人工返工（interactive 模式下 verdict == "rework"）独立于自动返工计数：

| 计数类型 | 位置 | 上限 |
|---------|------|------|
| 自动返工 | progress.json → rework_count | 每阶段 2 次 |
| 人工返工 | audit_log.json → manual_rework_count | 无上限 |

### 6.2 计数规则

- 每次人工返工：`manual_rework_count[rework_target_phase]` +1
- 人工返工不计入自动返工的 2 次上限
- 人工返工后递增 artifact_version
- 人工返工记录在 gates 数组中（manual_rework_triggered == true）
- 按 phase 分计（phase2 / phase3 / phase5）

### 6.3 最终摘要引用

最终摘要中同时展示两类返工次数：

```
质量问题: 自动返工{auto_count}次 | 人工返工{manual_count}次
```
