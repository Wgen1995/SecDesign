---
name: requirement-provider
description: Use when fetching requirement details and design document paths by requirement ID. Default implementation reads from local JSON file; replace to integrate with external platforms.
---

# 需求信息获取 (Phase0)

## 概述

根据需求编号获取需求详情和设计文档路径。这是 secdesign 流水线的第一个 Phase，负责将外部需求来源转换为套件内部统一的需求信息文件，为后续攻击面识别和威胁建模提供输入。

## 套件根定位

首次执行前用 Glob 工具定位套件根：

```
Glob pattern: **/secdesign/SKILL.md
```

第一个命中路径的父目录即为套件根。后续所有相对引用（如 `skills/shared/ADAPTER_CONTRACT.md`、`knowledge-bases/`）需拼接套件根绝对路径前缀。

## 接口合约

读取 `{套件根}/skills/shared/ADAPTER_CONTRACT.md` 获取完整接口合约。

输入：requirement_id (string)
输出：`.secdesign_output/{requirement_id}/requirement_context/requirement_info.json`

## MUST 输入/输出

参考 `{套件根}/skills/shared/OUTPUT_STANDARD.md` §6：

| 项目 | 内容 |
|------|------|
| MUST 输入 | requirement_id (string) |
| MUST 输出 | `requirement_context/requirement_info.json` + `json_file/security_graph.json`（含 requirement 节点） |

## 默认实现

1. 读取项目目录下 `.secdesign-data/{requirement_id}.json`
2. 校验 JSON 包含必需字段：requirement_id, requirement_name, description
3. 如果字段缺失，向用户提示具体缺失字段并终止流程
4. 将内容写入 `.secdesign_output/{requirement_id}/requirement_context/requirement_info.json`
5. 更新 security_graph.json：添加 requirement 节点

## 输出格式

requirement_info.json：

```json
{
  "requirement_id": "REQ-001",
  "requirement_name": "文件上传功能",
  "description": "实现用户头像和附件上传，支持图片和文档，限制文件大小和类型。",
  "acceptance_criteria": "1. 支持jpg/png/pdf上传\n2. 单文件≤10MB\n3. 上传后可下载预览",
  "scope": "function",
  "priority": "High",
  "design_docs": [
    {
      "name": "upload_design.docx",
      "path": "/docs/upload_design.docx",
      "type": "docx"
    }
  ],
  "custom_fields": {}
}
```

**必需字段校验**：输出 JSON 必须包含 `requirement_id`、`requirement_name`、`description` 三个字段。字段缺失时向用户提示并终止流程。`acceptance_criteria`、`scope`、`priority`、`design_docs`、`custom_fields` 为可选字段，缺失时不阻塞流程。

## 更新知识图谱

读取 `.secdesign_output/{requirement_id}/json_file/security_graph.json`，追加：

```json
{
  "id": "req-{requirement_id}",
  "type": "requirement",
  "name": "{requirement_name}",
  "description": "{description}",
  "scope": "{scope}",
  "status": "✅"
}
```

写回 security_graph.json（独占写入，参考 OUTPUT_STANDARD.md §7）。

## 更新 progress.json

将 `phases.phase0` 状态改为 `"completed"`。

## 红线

- 输出 JSON 必须包含 requirement_id, requirement_name, description 三个必需字段
- design_docs 中的 path 必须是可访问的文件路径
- 不编造需求内容（缺失字段标注为"需求未明确"而非自行补充）
- 不修改原始需求文本的 description 字段

## 替换指南

参见 `{套件根}/skills/shared/ADAPTER_CONTRACT.md` §1。替换步骤：

| 步骤 | 操作 |
|------|------|
| 1 | 修改本 SKILL.md 的"默认实现"章节 |
| 2 | 将"读本地 JSON 文件"替换为目标平台 API 调用逻辑 |
| 3 | 保持输出格式不变（必需字段 + 可选字段） |
| 4 | 配置认证环境变量（见 ADAPTER_CONTRACT.md §3） |
| 5 | 验证输出 JSON 通过必需字段校验 |
