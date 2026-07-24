# 覆盖率规则（coverage-rules）

> 来源：secdesign_spec.md §3.8 + §6.2 + §6.3 + §4.3
> 用途：Phase4 coverage-checker 检查攻击面×威胁×检查点的覆盖率是否达标；Phase5 后追加测试用例维度覆盖率检查。

---

## CVR-01~05 完整规则定义表

| 规则ID | 检查维度 | 计算方式 | 阈值 | 不达标动作 | 执行时机 |
|--------|---------|---------|------|-----------|---------|
| CVR-01 | 攻击面覆盖率 | 有检查点的攻击面数 / 总攻击面数 | ≥90% | 返工Phase3补检查点 | Phase4 |
| CVR-02 | 威胁检查点覆盖率 | 有检查点的威胁数 / 总威胁数 | ≥90% | 返工Phase3补检查点 | Phase4 |
| CVR-03 | STRIDE覆盖率 | 每个攻击面已分析STRIDE数 / 适用STRIDE数 | ≥80%（系统级100%） | 返工Phase2补威胁 | Phase4 |
| CVR-04 | 五态检查 | 所有攻击面的状态 | 无⬜ | 返工对应Phase | Phase4 |
| CVR-05 | 威胁测试用例覆盖率 | 有测试用例的威胁数 / 总威胁数 | ≥90% | 返工Phase5补用例 | Phase5后(Phase6前) |

---

## 五态标记定义

五态标记分两个阶段判定，Phase5 后在 Phase4 状态基础上升级。

### Phase4 后（检查点维度）

| 标记 | 含义 | 判定条件 |
|------|------|---------|
| ✅ | 已覆盖 | 攻击面有检查点 |
| ❌ | 未覆盖 | 攻击面无检查点 |
| ❓ | 待确认 | 需求不明确，无法判定 |
| ⬜ | 未评估 | 尚未执行Phase4 |

### Phase5 后（测试用例维度，在Phase4状态基础上升级）

| 标记 | 含义 | 判定条件 |
|------|------|---------|
| ✅ | 完全覆盖 | 攻击面有检查点 且 威胁有测试用例 |
| ⚠️ | 部分覆盖 | 攻击面有检查点 但 威胁缺测试用例 |
| ❌ | 未覆盖 | 攻击面无检查点 |
| ❓ | 待确认 | 需求不明确 |
| ⬜ | 未评估 | Phase7要求清零 |

---

## 自动返工机制

- **返工次数上限**：2次
- **返工目标Phase由finding决定**：
  - CVR-01 攻击面覆盖率不达标 → 返工 Phase3（补检查点）
  - CVR-02 威胁检查点覆盖率不达标 → 返工 Phase3（补检查点）
  - CVR-03 STRIDE覆盖率不达标 → 返工 Phase2（补威胁）
  - CVR-04 五态检查有⬜ → 返工对应Phase（由⬜所在阶段决定）
  - CVR-05 威胁测试用例覆盖率不达标 → 返工 Phase5（补用例）
- **每次返工记录到 audit_log.json**
- **2次返工后仍不达标**：输出警告，继续执行（不阻断）

---

## 返工流程（5步）

```
1. 读 progress.json
   → 获取当前 rework_count 和 artifact_versions

2. 递增版本
   → rework_count[目标phase] += 1
   → artifact_versions[对应产物] 版本递增（v1 → v2 → v3）

3. 传递 findings
   → 将 coverage_findings.json 中不达标的 finding 传递给目标 Phase
   → 目标 Phase 据此补充缺失内容

4. 重新调度
   → 重新执行目标 Phase 及其后续 Phase（如返工Phase2则Phase2-4重跑）
   → 目标 Phase 完成后重新执行覆盖率检查

5. 重新检查
   → 再次执行 CVR-01~05 检查
   → 若仍不达标且未达上限，重复步骤2-5
   → 若达上限仍不达标，输出警告并继续
```

---

## 返工目标Phase映射

| 不达标规则 | 返工目标Phase | 需重跑的Phase链 | 版本递增产物 |
|-----------|--------------|----------------|-------------|
| CVR-01 攻击面覆盖率 | Phase3 | Phase3 → Phase4 | security_spec |
| CVR-02 威胁检查点覆盖率 | Phase3 | Phase3 → Phase4 | security_spec |
| CVR-03 STRIDE覆盖率 | Phase2 | Phase2 → Phase3 → Phase4 | threats, security_spec |
| CVR-04 五态检查 | 对应Phase | 由⬜所在阶段决定 | 对应产物 |
| CVR-05 威胁测试用例覆盖率 | Phase5 | Phase5 → Phase6 | security_tests |

---

## 系统级特殊阈值

| scope | CVR-03 阈值 | 说明 |
|-------|------------|------|
| interface | ≥80% | 接口级 |
| function | ≥80% | 功能级 |
| module | ≥80% | 模块级 |
| system | **100%** | 系统级要求STRIDE全覆盖 |

---

## 输出产物

- `coverage/coverage_report.md` — 覆盖率报告（含CVR-01~05各项结果）
- `coverage/coverage_findings.json` — 不达标finding清单（供返工使用）
- `json_file/security_graph.json` — 含 finding 节点 + checked_by 边
