---
name: attack-surface-identifier
description: Use when scanning requirements to identify matched attack surface subclasses and expand KL-1 checklist items. Handles design doc conversion, chunking, and supplementary keyword matching.
---

# 攻击面识别 (Phase1)

## 概述

扫描需求，识别命中的攻击面子类，展开 KL-1 检查点。如果有设计文档，执行文档转换→分块→补充匹配流程，识别预检未命中的攻击面。输出攻击面清单和检查点列表，为 Phase2 威胁映射提供输入。

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
| MUST 输入 | `requirement_context/requirement_info.json` + `requirement_context/security_prescreen.json` |
| MUST 输出 | `attack_surfaces/attack_surfaces.json` + `design_doc_markdown/*.md` + `doc_chunks/doc_chunks.json` + `json_file/security_graph.json`（含 attack_surface 节点 + has_surface 边） |

## 知识库引用

- `{套件根}/knowledge-bases/KL-1-checklist/`（每个攻击面子类一个文件，如 `A3.2-file-upload-download.md`）
- `{套件根}/knowledge-bases/KL-1-checklist/_index.md`（32 子类索引 + 匹配关键词）

## 处理流程

1. 读取 `.secdesign_output/{requirement_id}/requirement_context/security_prescreen.json`，获取 `matched_categories`
2. 对每个命中的子类，读取对应的 KL-1 文件（如 `knowledge-bases/KL-1-checklist/A3.2-file-upload-download.md`），展开检查点
3. 如果 requirement_info.json 中有 design_docs，执行文档处理流程（见下方），做补充匹配
4. 汇总所有攻击面和检查点，输出 attack_surfaces.json

## 设计文档处理流程

有 design_docs 时执行：

1. **文档转换**：docx/pdf/xlsx → Markdown（保留标题层级）；md 直接复制；openapi 转为接口清单 Markdown
2. **文档分块**：按 H2/H3 标题切分，单块上限 800 字（中文按字符计），超长时按段落二次切分；每块提取 section_path + keywords
3. **补充匹配**：用分块关键词扫描 KL-1 索引，识别 prescreen 未命中的攻击面
4. **输出**：`design_doc_markdown/*.md` + `doc_chunks/doc_chunks.json`
5. **知识图谱追加**：doc_chunk 节点 + traces_to 边（attack_surface → doc_chunk）

### 分块规则

| 规则项 | 要求 |
|--------|------|
| 分块边界 | H2 (`##`) / H3 (`###`) 标题 |
| 单块上限 | 800 字（超长按段落二次切分） |
| section_path | 从根到当前标题的层级路径 |
| keywords | LLM 抽取 3-5 个关键词 |

### doc_chunks.json 格式

```json
{
  "chunks": [
    {
      "id": "chk-001",
      "source_doc": "upload_design.docx",
      "section_path": "3.2 文件上传流程",
      "content": "用户通过前端页面上传文件，后端校验文件类型和大小，存储到独立分区...",
      "keywords": ["上传", "文件类型", "校验", "存储"]
    }
  ]
}
```

### 降级策略

无设计文档时跳过文档处理，生成空 chunks `{"requirement_id": "...", "chunks": []}`，在安全规格风险章节标注"无设计文档追溯"。

## KL-1 文件格式

以 A3.2 文件上传下载为例：

```markdown
# A3.2 文件上传/下载

## 匹配关键词
上传、下载、附件、导入、导出、Upload、File、Avatar、Import、Export

## STRIDE适用
T(篡改)、I(泄露)、D(拒绝)、E(提权)

## 安全检查点

### 文件上传
- [ ] 文件类型校验（前台+后台都必须校验）
- [ ] 文件名校验（前后台），防止跨目录攻击（../）
- [ ] 文件大小限制
- [ ] 文件内容检测（病毒/Webshell/XXE）
- [ ] 上传后重命名（不保留原始文件名）
- [ ] 上传目录不可执行（无执行权限）
...

### 文件下载
- [ ] 下载文件类型为Excel需CSV防护
- [ ] 下载文件类型为HTML需XSS防护
...
```

每个检查点标注 phase（design/code/test/deploy），用于 Phase3 安全规格分章节归类。

## 输出格式

attack_surfaces.json：

```json
{
  "requirement_id": "REQ-001",
  "surfaces": [
    {
      "id": "AS-001",
      "category": "A3.2",
      "name": "文件上传/下载",
      "match_reason": "需求描述包含'上传附件'",
      "match_source": "prescreen",
      "stride_applicable": ["T", "I", "D", "E"],
      "checklist_items": [
        {"id": "CL-001", "item": "文件类型校验（前台+后台）", "phase": "design"},
        {"id": "CL-002", "item": "文件名校验防跨目录", "phase": "code"},
        {"id": "CL-003", "item": "文件大小限制", "phase": "design"},
        {"id": "CL-004", "item": "文件内容检测", "phase": "test"},
        {"id": "CL-005", "item": "上传后重命名", "phase": "code"},
        {"id": "CL-006", "item": "上传目录不可执行", "phase": "deploy"}
      ]
    }
  ],
  "summary": {
    "total_surfaces": 3,
    "total_checklist_items": 16,
    "scope": "function"
  }
}
```

## 更新知识图谱

读取 `.secdesign_output/{requirement_id}/json_file/security_graph.json`，追加：

**attack_surface 节点**：

```json
{
  "id": "as-001",
  "type": "attack_surface",
  "category": "A3.2",
  "name": "文件上传/下载",
  "checklist_items": ["CL-001", "CL-002", "CL-003"],
  "state": "⬜"
}
```

**has_surface 边**（requirement → attack_surface）：

```json
{
  "from": "req-{requirement_id}",
  "to": "as-001",
  "type": "has_surface"
}
```

**doc_chunk 节点**（有设计文档时）：

```json
{
  "id": "chk-001",
  "type": "doc_chunk",
  "name": "文件上传流程片段",
  "status": "✅",
  "source_doc": "upload_design.docx",
  "location": "3.2 文件上传流程"
}
```

**traces_to 边**（attack_surface → doc_chunk）：

```json
{
  "from": "as-001",
  "to": "chk-001",
  "type": "traces_to",
  "attrs": { "relevance": "high" }
}
```

写回 security_graph.json（独占写入，参考 OUTPUT_STANDARD.md §7）。

## 更新 progress.json

将 `phases.phase1` 状态改为 `"completed"`。

## 红线

- 不编造需求中没有的攻击面（匹配必须基于关键词或文档内容）
- 检查点必须来自 KL-1 文件，不靠 LLM 自行编造
- 每个检查点必须标注 phase（design/code/test/deploy）
- 文档转换失败不阻塞：记录日志，跳过该文档，继续处理其他文档
- 无设计文档时必须生成空 chunks，不能省略 doc_chunks.json 文件
- attack_surface 节点的 state 初始为 ⬜（未评估），由后续 Phase 更新
