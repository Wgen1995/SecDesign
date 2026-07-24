# 输出标准规范（OUTPUT_STANDARD）

> 本文件定义 secdesign 套件的输出目录结构、文件命名规范、知识图谱 Schema、节点/边类型、五态标记、source 字段、MUST 输入/输出表、并发写入协议与分批阈值。

## 1. 输出目录结构

每个需求的工作目录 `.secdesign_output/{requirement_id}/` 包含以下子目录与文件：

```
.secdesign_output/{requirement_id}/
├── requirement_context/        # Phase0/0.5 输出：需求信息与安全预检
│   ├── requirement_info.json   # Phase0
│   └── security_prescreen.json # Phase0.5
├── design_doc/                 # Phase0 输出：原始设计文档副本
├── design_doc_markdown/        # Phase1 输出：转换后的 Markdown 文档
│   └── *.md
├── doc_chunks/                 # Phase1 输出：文档分块（补充匹配检索单元）
│   └── doc_chunks.json
├── attack_surfaces/            # Phase1 输出：攻击面识别
│   └── attack_surfaces.json
├── threats/                    # Phase2 输出：威胁映射
│   └── threats.json
├── security_spec/              # Phase3 输出：安全规格
│   ├── security_spec.md
│   └── security_spec.json
├── coverage/                   # Phase4 输出：覆盖率检查
│   ├── coverage_report.md
│   └── coverage_findings.json
├── security_tests/             # Phase5 输出：安全测试用例
│   ├── security_tests.md
│   └── security_tests.json
├── review/                     # Phase6 输出：安全评审
│   └── review_report.md
├── report/                     # Phase7 输出：多格式报告
│   ├── security_report.md
│   ├── security_tests.xlsx
│   ├── security_findings.sarif
│   └── security_graph_viz.html
└── json_file/                  # 全链结构化数据
    ├── security_graph.json     # 知识图谱（各 Phase 追加）
    └── audit_log.json          # 审计日志
```

## 2. 文件命名规范

| 规范项 | 要求 |
|--------|------|
| 文本编码 | UTF-8 无 BOM（CSV 文件例外：UTF-8 **with** BOM，兼容 Excel 直接打开） |
| 日期格式 | ISO 8601：`YYYY-MM-DD`（日期）、`YYYY-MM-DDTHH:mm:ss`（时间戳） |
| 文件命名 | snake_case，小写字母+下划线，不含空格 |
| JSON 格式 | 2 空格缩进，UTF-8，键名 snake_case |
| Markdown | UTF-8，使用 ATX 标题（`#`），代码块标注语言 |

## 3. security_graph.json Schema（version 1.1）

知识图谱是 secdesign 套件的核心数据载体，记录需求→攻击面→威胁→检查点→测试用例→发现的完整推导链。

### 3.1 顶层结构

```json
{
  "requirement_id": "REQ-001",
  "version": "1.1",
  "nodes": [
    { "id": "req-001", "type": "requirement", "name": "文件上传功能", "description": "...", "scope": "function" },
    { "id": "asm-001", "type": "security_assessment", "verdict": "proceed", "matched_categories": ["A3.2", "A2.1"] },
    { "id": "as-001", "type": "attack_surface", "category": "A3.2", "name": "文件上传/下载", "checklist_items": [], "state": "✅" },
    { "id": "t-001", "type": "threat", "surface_id": "as-001", "stride_type": "T", "severity": "S2" },
    { "id": "sc-001", "type": "security_check", "threat_id": "t-001", "layer": "KL-3", "check_item": "ASVS V12.1 文件上传验证" },
    { "id": "st-001", "type": "security_test", "threat_id": "t-001", "test_name": "UC-FILE-001 恶意文件上传", "steps": [], "source": "threat_derived" },
    { "id": "f-001", "type": "finding", "target_id": "as-001", "dimension": "coverage", "verdict": "pass" }
  ],
  "edges": [
    { "from": "req-001", "to": "as-001", "type": "has_surface" },
    { "from": "as-001", "to": "t-001", "type": "has_threat" },
    { "from": "sc-001", "to": "req-001", "type": "traces_to" },
    { "from": "t-001", "to": "sc-001", "type": "mapped_by" },
    { "from": "st-001", "to": "t-001", "type": "covers" },
    { "from": "f-001", "to": "sc-001", "type": "checked_by" },
    { "from": "st-001", "to": "pub-sarif-001", "type": "published_as", "attrs": { "format": "sarif" } },
    { "from": "req-001", "to": "gate-1", "type": "audited_by", "attrs": { "gate": "Gate-1", "verdict": "pass" } }
  ]
}
```

### 3.2 节点类型（10 种）

| type | 含义 | 写入 Phase | 必需字段 |
|------|------|-----------|---------|
| requirement | 需求 | Phase0 | id, name, description, scope |
| security_assessment | 安全预检评估 | Phase0.5 | id, verdict, matched_categories |
| attack_surface | 攻击面 | Phase1 | id, category, name, checklist_items, state |
| doc_chunk | 设计文档分块 | Phase1 | id, source_doc, section_path, keywords |
| threat | 威胁 | Phase2 | id, surface_id, stride_type, severity |
| security_check | 安全检查点 | Phase3 | id, threat_id, layer, check_item |
| finding | 覆盖率/评审发现 | Phase4/6 | id, target_id, dimension, verdict |
| security_test | 安全测试用例 | Phase5 | id, threat_id, test_name, steps, source |
| publish_node | 发布产物 | Phase7 | id, type, format, file, status |
| gate | 签核节点 | Phase7 | id, type, gate, verdict, mode, status |

### 3.3 边类型（9 种）

| type | 含义 | 从 | 到 | 写入 Phase |
|------|------|----|----|-----------|
| has_surface | 需求有攻击面 | requirement | attack_surface | Phase1 |
| traces_to | 攻击面追溯到文档片段 | attack_surface | doc_chunk | Phase1 |
| has_threat | 攻击面有威胁 | attack_surface | threat | Phase2 |
| mapped_by | 威胁由知识层映射 | threat | security_check | Phase3 |
| traces_to_req | 检查点追溯到需求 | security_check | requirement | Phase3 |
| covers | 测试用例覆盖威胁 | security_test | threat | Phase5 |
| checked_by | 发现由检查产生 | finding | security_check | Phase4/6 |
| published_as | 测试用例发布为格式 | security_test | publish_node | Phase7 |
| audited_by | 需求被人工签核 | requirement | gate | Phase7 |

**注**：`traces_to` 用于攻击面→文档片段追溯（Phase1），`traces_to_req` 用于检查点→需求追溯（Phase3），两者语义不同。

## 4. source 字段

security_test 节点的 `source` 字段标记推导来源：

| source 值 | 含义 |
|-----------|------|
| threat_derived | 从威胁模型直接推导 |
| llm_inferred | LLM 基于安全经验补充 |
| rule_based | 基于合规规则(KL-6)或运行时检查(KL-7)补充 |

## 5. 五态标记

每个 attack_surface 节点必须有 `state` 字段，分两个阶段判定。

### 5.1 Phase4 后（检查点维度）

| 标记 | 含义 | 判定条件 |
|------|------|---------|
| ✅ | 已覆盖 | 攻击面有检查点 |
| ❌ | 未覆盖 | 攻击面无检查点 |
| ❓ | 待确认 | 需求不明确，无法判定 |
| ⬜ | 未评估 | 尚未执行 Phase4 |

### 5.2 Phase5 后（测试用例维度，在 Phase4 状态基础上升级）

| 标记 | 含义 | 判定条件 |
|------|------|---------|
| ✅ | 完全覆盖 | 攻击面有检查点 且 威胁有测试用例 |
| ⚠️ | 部分覆盖 | 攻击面有检查点 但 威胁缺测试用例 |
| ❌ | 未覆盖 | 攻击面无检查点 |
| ❓ | 待确认 | 需求不明确 |
| ⬜ | 未评估 | Phase7 要求清零 |

**闭环校验**：Phase7 要求所有 attack_surface 和 threat 节点状态非 ⬜。

## 6. MUST 输入/输出表

| Phase | MUST 输入 | MUST 输出 |
|-------|----------|----------|
| Phase0 | requirement_id | requirement_context/requirement_info.json + json_file/security_graph.json(含 requirement 节点) |
| Phase0.5 | requirement_info.json | requirement_context/security_prescreen.json + json_file/security_graph.json(含 security_assessment 节点) |
| Phase1 | requirement_info.json + security_prescreen.json | attack_surfaces/attack_surfaces.json + design_doc_markdown/*.md + doc_chunks/doc_chunks.json + json_file/security_graph.json(含 attack_surface 节点 + has_surface 边) |
| Phase2 | attack_surfaces.json + requirement_info.json | threats/threats.json + json_file/security_graph.json(含 threat 节点 + has_threat 边) |
| Phase3 | threats.json + attack_surfaces.json + requirement_info.json | security_spec/security_spec.md + security_spec.json + json_file/security_graph.json(含 security_check 节点 + mapped_by 边 + traces_to 边) |
| Phase4 | security_spec.json + attack_surfaces.json + threats.json | coverage/coverage_report.md + coverage_findings.json + json_file/security_graph.json(含 finding 节点 + checked_by 边) |
| Phase5 | security_spec.json + threats.json + attack_surfaces.json | security_tests/security_tests.md + security_tests.json + json_file/security_graph.json(含 security_test 节点 + covers 边) |
| Phase6 | security_tests.json + security_spec.json | review/review_report.md + json_file/security_graph.json(含 finding 节点) |
| Phase7 | security_tests.json + security_graph.json + audit_log.json | report/security_report.md + report/security_tests.xlsx + report/security_findings.sarif + report/security_graph_viz.html + json_file/security_graph.json(含 published_as + audited_by 边) + json_file/audit_log.json(归档) |

## 7. 并发写入协议

### 7.1 追加写入模式

security_graph.json 使用追加写入模式（读取→追加→写回）。每个 Phase 对 security_graph.json 的写入是独占的，禁止并行写入。

### 7.2 Phase4/6 并行→串行汇总

Phase4 覆盖率检查和 Phase6 评审如需并行，各自写独立 findings 分片文件：

- Phase4 → `coverage/coverage_findings.json`
- Phase6 → `review/review_findings.json`（如启用）

全部完成后，**串行汇总**：
1. 读取 security_graph.json
2. 合并各 findings 分片中的 finding 节点到 nodes 数组
3. 合并对应的 checked_by 边到 edges 数组
4. 写回 security_graph.json

### 7.3 其他 Phase 独占写入

除上述并行场景外，所有 Phase 对 security_graph.json 的写入是独占的（读取→追加→写回）。

## 8. BATCH_THRESHOLD（分批阈值）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| BATCH_THRESHOLD | 20 | 超过此数量时触发自适应分批 |

### 分批策略

| Phase | 触发条件 | 分批方式 |
|-------|---------|---------|
| Phase2 | 攻击面数 > BATCH_THRESHOLD | 按攻击面分组并行威胁映射 |
| Phase5 | 威胁数 > BATCH_THRESHOLD | 按攻击面分组生成测试用例，追加写入后合并 |

用户不感知需求大小，Phase 内部自动分批。BATCH_THRESHOLD 可通过环境变量 `SECDESIGN_BATCH_THRESHOLD` 覆盖。
