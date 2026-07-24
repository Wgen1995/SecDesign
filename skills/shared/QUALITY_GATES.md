# 质量门控规范（QUALITY_GATES）

> 本文件定义 secdesign 套件的全部质量门控阈值、裁决规则、返工流程与人工签核机制。

## 1. Phase0.5 安全预检门控

### 1.1 检查条件

Phase0.5 扫描需求描述与验收标准中的安全关键词，匹配 KL-1 索引，判定是否有安全面、需求粒度、估算威胁数量。

### 1.2 裁决规则

| 条件 | verdict | 后续动作 |
|------|---------|---------|
| has_security_surface == false | skip | 跳过 Phase1-2，Phase3 标记"无安全面" |
| scope == system 且无 design_docs | conditional | 提示补充架构文档，询问继续或暂停 |
| estimated_threat_count > 30 | complex | 建议拆分需求，询问继续或拆分 |
| force == true | proceed | 跳过预检直接进入 Phase1 |

### 1.3 强制继续

当 `force == true` 时，跳过 Phase0.5 预门直接进入 Phase1，在 progress.json 中标记 `phase0.5: "forced_pass"`，并在最终摘要中标注 WARNING。

## 2. Phase4 覆盖率门控

### 2.1 覆盖率检查规则

| 规则ID | 检查维度 | 计算方式 | 阈值 | 不达标动作 | 执行时机 |
|--------|---------|---------|------|-----------|---------|
| CVR-01 | 攻击面覆盖率 | 有检查点的攻击面数 / 总攻击面数 | ≥ 90% | 返工 Phase3 补检查点 | Phase4 |
| CVR-02 | 威胁检查点覆盖率 | 有检查点的威胁数 / 总威胁数 | ≥ 90% | 返工 Phase3 补检查点 | Phase4 |
| CVR-03 | STRIDE覆盖率 | 每个攻击面已分析STRIDE数 / 适用STRIDE数 | ≥ 80%（系统级 100%） | 返工 Phase2 补威胁 | Phase4 |
| CVR-04 | 五态检查 | 所有攻击面的状态 | 无 ⬜ | 返工对应 Phase | Phase4 |

### 2.2 返工规则

| 条件 | 动作 |
|------|------|
| CVR-01~04 全部达标 | 门控通过，继续 Phase5 |
| CVR-01/CVR-02 不达标 且 phase3 返工次数 < 2 | 返工 Phase3，返工次数 +1 |
| CVR-03 不达标 且 phase2 返工次数 < 2 | 返工 Phase2，返工次数 +1 |
| CVR-04 存在 ⬜ 且对应 Phase 返工次数 < 2 | 返工对应 Phase，返工次数 +1 |
| 任一不达标 且对应返工次数 ≥ 2 | 标记 WARNING，继续 Phase5 |

### 2.3 返工流程

1. 读取 progress.json，将对应 `rework_count.{phase}` +1
2. 递增 security_spec.md 的 artifact_version（v1 → v2 → v3）
3. 将 coverage_findings 中 severity == "major" 的问题作为返工输入传递给目标 Phase
4. 重新调度目标 Phase → Phase4
5. 重新检查门控

## 3. CVR-05 门控（Phase5 后）

### 3.1 检查规则

| 规则ID | 检查维度 | 计算方式 | 阈值 | 不达标动作 | 执行时机 |
|--------|---------|---------|------|-----------|---------|
| CVR-05 | 威胁测试用例覆盖率 | 有测试用例的威胁数 / 总威胁数 | ≥ 90% | 返工 Phase5 补用例 | Phase5 后（Phase6 前） |

### 3.2 返工规则

| 条件 | 动作 |
|------|------|
| CVR-05 ≥ 90% | 门控通过，继续 Phase6 |
| CVR-05 < 90% 且 phase5 返工次数 < 2 | 返工 Phase5，返工次数 +1 |
| CVR-05 < 90% 且 phase5 返工次数 ≥ 2 | 标记 WARNING，继续 Phase6 |

### 3.3 返工流程

1. 读取 progress.json，将 `rework_count.phase5` +1
2. 递增 security_tests.json 的 artifact_version
3. 将缺失测试用例的威胁清单作为返工输入传递给 Phase5
4. 重新调度 Phase5 → CVR-05 检查
5. 重新检查门控

## 4. Phase6 评审门控

### 4.1 评审维度

| 维度 | 检查项 | 判定方式 |
|------|--------|---------|
| 可执行性 | 步骤可操作、预期可验证、清理完整 | 规则+LLM裁决 |
| 可利用性 | 威胁是否有可利用的攻击路径 | LLM裁决+攻击模式匹配 |
| 误报风险 | 测试用例是否可能产生误报 | LLM裁决 |
| 攻击链 | 多个中低危威胁是否可串联（scope ≥ function 时） | LLM推理 |

### 4.2 返工规则

| 条件 | 动作 |
|------|------|
| 可执行性 ≥ 70% | 门控通过，继续 Phase7 |
| 可执行性 < 70% 且 phase5 返工次数 < 2 | 返工 Phase5，返工次数 +1 |
| 可执行性 < 70% 且 phase5 返工次数 ≥ 2 | 标记 WARNING，继续 Phase7 |

## 5. 自动返工

### 5.1 上限与目标

- 自动返工次数上限：每阶段 2 次
- 返工目标 Phase 由 finding 决定：
  - CVR-01/CVR-02/CVR-04 → Phase3
  - CVR-03 → Phase2
  - CVR-05/Phase6可执行性 → Phase5
- 每次返工记录到 audit_log.json

### 5.2 超限处理

2 次返工后仍不达标：
1. 不再触发自动返工
2. 在 progress.json 中标记对应 phase 为 `WARNING`
3. 继续执行下一 Phase（不阻断）
4. 在最终摘要中标注 WARNING 及具体维度/问题
5. 审计日志记录 WARNING 状态

## 6. 交互模式签核（mode == interactive）

### 6.1 签核点

| 签核点 | 时机 | 审阅对象 | verdict 取值 | 人工返工目标 |
|--------|------|---------|-------------|-------------|
| Gate-1 | Phase4 后 | 覆盖率报告+攻击面/威胁清单 | pass / pass_with_suggestions / rework / terminate | rework → phase2 或 phase3 |
| Gate-2 | Phase6 后 | 评审报告+安全测试用例 | pass / pass_with_suggestions / rework / terminate | rework → phase5 |
| Gate-3 | Phase7 发布前 | 最终报告+全部产物+覆盖率摘要 | publish / not_publish | — |

### 6.2 签核记录字段

每次签核记录到 audit_log.json 的 gates 数组，字段定义见 AUDIT_LOG_SPEC.md §2.2：
reviewer / timestamp / verdict / artifact_version / comment / manual_rework_triggered / rework_target_phase

### 6.3 人工返工计数

人工返工（verdict == "rework"）独立于自动返工计数：
- 不计入自动返工的 2 次上限
- 单独计入 `manual_rework_count`（progress.json 和 audit_log.json 均记录，无上限）
- 人工返工后递增 artifact_version 并重新调度对应 Phase
- 按 phase 分计（phase2 / phase3 / phase5）

## 7. WARNING 处理

当自动返工超过 2 次上限时：

1. 不再触发自动返工
2. 在 progress.json 中标记对应 phase 为 `WARNING`
3. 继续执行下一 Phase
4. 在最终摘要中标注 WARNING 及具体维度/问题
5. 审计日志记录 WARNING 状态

## 8. 门控阈值汇总

| 门控 | 位置 | 阈值 | 返工目标 | 最大自动返工 |
|------|------|------|---------|-------------|
| Phase0.5 预门 | Phase0.5 后 | has_security_surface=false→skip; scope=system无文档→conditional; threat>30→complex; force=true→proceed | Phase0（补需求） | 不限（人工决定） |
| Phase4 门控 | Phase4 后 | CVR-01≥90%, CVR-02≥90%, CVR-03≥80%(system 100%), CVR-04无⬜ | Phase2 或 Phase3 | 2 次 |
| CVR-05 门控 | Phase5 后 | CVR-05≥90% | Phase5 | 2 次 |
| Phase6 门控 | Phase6 后 | 可执行性≥70% | Phase5 | 2 次 |
