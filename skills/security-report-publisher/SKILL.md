---
name: security-report-publisher
description: Use when publishing security reports in multiple formats (MD/Excel/SARIF/JSON/HTML) with remediation tracking table, closure validation, Gate-3 sign-off, and audit log archiving.
---

# 安全报告发布 (Phase7)

## 概述

多格式输出安全报告和处置跟踪表。读取全部 Phase 产物，生成 Markdown/Excel/SARIF/JSON/HTML 五种格式，执行闭环校验（所有 attack_surface 和 threat 节点状态非 ⬜），完成 Gate-3 签核（interactive 模式），归档审计日志。

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
| MUST 输入 | `security_tests/security_tests.json` + `json_file/security_graph.json` + `json_file/audit_log.json` |
| MUST 输出 | `report/security_report.md` + `report/security_tests.xlsx` + `report/security_findings.sarif` + `report/security_graph_viz.html` + `json_file/security_graph.json`（含 published_as + audited_by 边） + `json_file/audit_log.json`（归档） |

## 输出格式表

| 格式 | 文件 | 内容 | 消费者 |
|------|------|------|--------|
| Markdown | security_report.md | 安全规格+威胁模型+测试用例 | 安全工程师 |
| Excel | security_tests.xlsx | 安全检查点清单+风险处置跟踪表 | 项目经理/开发 |
| SARIF | security_findings.sarif | 机器可读的安全发现 | CI/CD |
| CSV | security_tests.csv | 安全测试用例清单(UTF-8 with BOM) | 导入TestLink/禅道 |
| JSON | security_graph.json | 全链追溯图谱 | 自动化Pipeline |
| HTML | security_graph_viz.html | 交互式追溯图谱（Cytoscape.js） | 管理层 |

## 处理流程

1. 读取 `{套件根}/skills/shared/ADAPTER_CONTRACT.md` §2（security-report-publisher 接口合约）
2. 读取 `{套件根}/scripts/` 下脚本路径：json_to_sarif.py / json_to_excel.py / json_to_csv.py
   读取 `{套件根}/skills/graph-viz/SKILL.md`（图谱可视化生成器）
3. 读取全部 Phase 产物：
   - `.secdesign_output/{requirement_id}/security_spec/security_spec.md` + `.json`
   - `.secdesign_output/{requirement_id}/threats/threats.json`
   - `.secdesign_output/{requirement_id}/attack_surfaces/attack_surfaces.json`
   - `.secdesign_output/{requirement_id}/security_tests/security_tests.json`
   - `.secdesign_output/{requirement_id}/json_file/security_graph.json`
   - `.secdesign_output/{requirement_id}/json_file/audit_log.json`
4. 按 format 参数生成对应格式：
   - `md`：合并安全规格+威胁模型+测试用例为 `report/security_report.md`
   - `excel`：调用 `scripts/json_to_excel.py`，写入 `report/security_tests.xlsx`（含处置跟踪表）
   - `sarif`：调用 `scripts/json_to_sarif.py`，写入 `report/security_findings.sarif`
   - `csv`：调用 `scripts/json_to_csv.py`，写入 `report/security_tests.csv`（UTF-8 with BOM）
   - `json`：security_graph.json 作为输入已存在，无需重新生成
   - `graph`：调用 `python3 {套件根}/skills/graph-viz/generate_viz.py -g json_file/security_graph.json --offline -o report/security_graph_viz.html`（交互式追溯图，离线模式）
   - `all`：生成上述全部格式
   - 组合（如 `md,excel`）：生成指定格式
5. **闭环校验**：读取 security_graph.json，确认所有 attack_surface 和 threat 节点状态非 ⬜
6. 追加 published_as 边到 security_graph.json
7. **Gate 签核节点生成**：读取 audit_log.json 的 gates 数组，为每个 Gate 生成节点 + audited_by 边
   - Gate-1（Phase4后）：覆盖率签核，verdict: pass/pass_with_suggestions/rework/terminate
   - Gate-2（Phase6后）：评审签核，verdict: pass/pass_with_suggestions/rework/terminate
   - Gate-3（Phase7发布前）：发布签核，verdict: publish/not_publish
   - auto 模式：gate 节点标注 `mode: "auto"`（自动门控通过）
   - interactive 模式：gate 节点标注 `mode: "interactive"`（人工签核）
8. **Gate-3 签核**（interactive 模式）：展示最终报告+全部产物+覆盖率摘要，等待 reviewer 签核
9. 归档 audit_log.json

## SARIF 输出 Schema 映射

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

**SARIF level 映射**：

| 严重度 | SARIF level |
|--------|-------------|
| S1 | error |
| S2 | error |
| S3 | warning |
| S4 | note |

## 处置跟踪表

Excel 中的处置跟踪表（8 列）：

| 检查点ID | 检查点描述 | 严重度 | 状态 | 责任人 | 计划完成 | 实际完成 | 验证结果 |
|---------|-----------|--------|------|--------|---------|---------|---------|
| CL-001 | 文件类型校验 | S2 | ⬜待修复 | | | | |
| CL-004 | 文件内容检测 | S2 | ⬜待修复 | | | | |

## 闭环校验

依据 OUTPUT_STANDARD.md §5：

```
读取 security_graph.json
遍历 nodes，对 type == "attack_surface" 或 "threat" 的节点：
  state = node.get("state", node.get("status", ""))
  if state == "⬜":
    记录到未处理节点列表
if 未处理节点列表非空:
  终止发布，输出未处理节点清单
else:
  校验通过，继续发布
```

## Gate-3 签核

依据 `{套件根}/skills/shared/QUALITY_GATES.md` §6.1 和 `{套件根}/skills/shared/AUDIT_LOG_SPEC.md` §3：

| 签核点 | 时机 | 审阅对象 | verdict 取值 |
|--------|------|---------|-------------|
| Gate-3 | Phase7 发布前 | 最终报告+全部产物+覆盖率摘要 | publish / not_publish |

- **interactive 模式**：展示最终报告和全部产物，等待 reviewer 签核
  - verdict == "publish"：执行发布，归档审计日志，生成 gate 节点 + audited_by 边
  - verdict == "not_publish"：终止发布，保留产物但不归档，不生成 gate 节点
- **auto 模式**：自动判定为 publish，不暂停等待签核，生成 gate 节点（标注 `mode: "auto"`）+ audited_by 边

签核记录追加到 audit_log.json 的 gates 数组。

## 更新知识图谱

读取 `.secdesign_output/{requirement_id}/json_file/security_graph.json`，追加：

**published_as 边**（security_test → publish_node）：

```json
{
  "from": "st-001",
  "to": "pub-sarif-001",
  "type": "published_as",
  "attrs": { "format": "sarif" }
}
```

**audited_by 边**（requirement → gate，Gate 签核后追加，auto 和 interactive 模式均生成）：

```json
{
  "from": "req-{requirement_id}",
  "to": "gate-1",
  "type": "audited_by",
  "attrs": { "gate": "Gate-1", "verdict": "pass", "mode": "auto" }
}
{
  "from": "req-{requirement_id}",
  "to": "gate-2",
  "type": "audited_by",
  "attrs": { "gate": "Gate-2", "verdict": "pass", "mode": "auto" }
}
{
  "from": "req-{requirement_id}",
  "to": "gate-3",
  "type": "audited_by",
  "attrs": { "gate": "Gate-3", "verdict": "publish", "mode": "auto" }
}
```

**gate 节点格式**：

```json
{
  "id": "gate-1",
  "type": "gate",
  "gate": "Gate-1",
  "verdict": "pass",
  "mode": "auto",
  "status": "✅"
}
```

- `mode: "auto"` — 自动门控通过，无人工签核
- `mode: "interactive"` — 人工签核，verdict 由 reviewer 决定

写回 security_graph.json（独占写入，参考 OUTPUT_STANDARD.md §7）。

## 审计日志归档

依据 `{套件根}/skills/shared/AUDIT_LOG_SPEC.md` §1，audit_log.json 在 Phase7 发布时最终归档：

- interactive 模式：Gate-3 签核记录已写入 gates 数组，本 Phase 确认归档完整性
- auto 模式：gates 数组为空，本 Phase 确认归档完整性

## 更新 progress.json

将 `phases.phase7` 状态改为 `"completed"`。

## 红线

- 闭环校验必须通过（所有 attack_surface 和 threat 节点状态非 ⬜），失败则终止发布
- format 参数控制输出格式：未请求的格式不生成
- graph 渲染失败不阻塞其他格式生成（记录日志，继续其他格式）
- SARIF level 映射必须严格遵循 S1/S2→error, S3→warning, S4→note
- 处置跟踪表必须包含 8 列（检查点ID/描述/严重度/状态/责任人/计划完成/实际完成/验证结果）
- audit_log.json 归档前确认 gates 数组完整性（interactive 模式需含 Gate-1/2/3 记录）
- published_as 边的 attrs.format 值与实际生成的格式一致
- 不阻塞用户强制继续（--force 时闭环校验失败仍可发布，但标注 WARNING）
