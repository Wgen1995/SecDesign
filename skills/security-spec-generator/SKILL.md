---
name: security-spec-generator
description: Use when mapping threats to KL-3/KL-4/KL-6 checkpoints and generating security specification document. Fills 6-chapter template with attack surface analysis, threat model, and compliance mapping.
---

# 安全规格生成 (Phase3)

## 概述

将威胁映射到 KL-3/KL-4/KL-6 的检查点，生成安全规格文档。规格包含 6 个章节：需求安全概述、攻击面分析、威胁模型、安全检查点、合规映射、风险处置建议。为 Phase4 覆盖率检查提供输入。

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
| MUST 输入 | `threats/threats.json` + `attack_surfaces/attack_surfaces.json` + `requirement_context/requirement_info.json` |
| MUST 输出 | `security_spec/security_spec.md` + `security_spec/security_spec.json` + `json_file/security_graph.json`（含 security_check 节点 + mapped_by 边 + traces_to 边） |

## 知识库引用

- `{套件根}/knowledge-bases/KL-3-owasp/`（OWASP Top10 + ASVS + API Security Top10）
- `{套件根}/knowledge-bases/KL-4-cwe/`（CWE/SANS Top25）
- `{套件根}/knowledge-bases/KL-6-compliance/`（凭证/加密/随机数/密码/数据保护/信息泄露/会话管理 + 容器合规）

## 处理流程

1. 读取 `.secdesign_output/{requirement_id}/threats/threats.json`
2. 读取 `.secdesign_output/{requirement_id}/attack_surfaces/attack_surfaces.json`
3. 读取 `.secdesign_output/{requirement_id}/requirement_context/requirement_info.json`
4. 读取 KL-3/KL-4/KL-6 知识库文件
5. 对每个威胁，映射到 KL-3（OWASP 检查点）、KL-4（CWE 弱点）、KL-6（合规规则）
6. 按 6 章节模板填充安全规格
7. 输出 security_spec.md 和 security_spec.json
8. 更新知识图谱：追加 security_check 节点 + mapped_by 边 + traces_to 边

## 安全规格模板（6 章节）

```
第1章: 需求安全概述
  1.1 基本信息（需求编号/名称/粒度/优先级）
  1.2 需求描述（原样引用）
  1.3 攻击面摘要（命中几个攻击面，预估威胁数）

第2章: 攻击面分析
  2.1 每个攻击面
    - 描述
    - 数据流（用户→处理→存储→输出）
    - 信任边界

第3章: 威胁模型
  3.1 每个威胁
    - STRIDE分类
    - 攻击路径（Source→...→Sink）
    - DREAD风险评级
    - 修复建议
  3.2 威胁汇总表

第4章: 安全检查点
  4.1 设计时检查点（架构/数据流/认证/授权）
  4.2 编码时检查点（输入校验/加密/日志/错误处理）
  4.3 测试时检查点（每个威胁对应的验证项）

第5章: 合规映射
  5.1 OWASP映射（每个检查点对应的OWASP Top10/ASVS条款）
  5.2 CWE映射（每个威胁对应的CWE编号）
  5.3 合规映射（每个检查点对应的合规规则）

第6章: 风险处置建议
  6.1 按严重度排序的风险清单
  6.2 每个风险的处置建议（修复/补偿控制/接受）
  6.3 验收标准
```

## 输出格式

security_spec.json（结构化数据，与 .md 对应）：

```json
{
  "requirement_id": "REQ-001",
  "version": "v1",
  "security_checks": [
    {
      "id": "SC-001",
      "threat_id": "T-001",
      "layer": "KL-3",
      "check_item": "ASVS V12.1 文件上传验证",
      "owasp": "A04-Insecure Design",
      "phase": "design",
      "description": "文件上传必须进行类型白名单校验和内容检测",
      "compliance": ["KL-6 G5-数据保护"]
    }
  ],
  "summary": {
    "total_checks": 24,
    "by_layer": {"KL-3": 12, "KL-4": 8, "KL-6": 4},
    "by_phase": {"design": 10, "code": 8, "test": 4, "deploy": 2}
  }
}
```

## 更新知识图谱

读取 `.secdesign_output/{requirement_id}/json_file/security_graph.json`，追加：

**security_check 节点**：

```json
{
  "id": "sc-001",
  "type": "security_check",
  "threat_id": "t-001",
  "layer": "KL-3",
  "check_item": "ASVS V12.1 文件上传验证",
  "status": "✅"
}
```

**mapped_by 边**（threat → security_check）：

```json
{
  "from": "t-001",
  "to": "sc-001",
  "type": "mapped_by"
}
```

**traces_to 边**（security_check → requirement）：

```json
{
  "from": "sc-001",
  "to": "req-{requirement_id}",
  "type": "traces_to"
}
```

写回 security_graph.json（独占写入，参考 OUTPUT_STANDARD.md §7）。

## 更新 progress.json

将 `phases.phase3` 状态改为 `"completed"`，并在 `artifact_versions` 中记录 `security_spec: "v1"`（首次生成）。

## 红线

- 第1章需求描述必须原样引用，不修改、不摘要
- 检查点必须来自 KL-3/KL-4/KL-6 知识库，不靠 LLM 自行编造
- 每个威胁至少映射 1 个检查点
- 检查点必须标注 phase（design/code/test/deploy），与第4章分节对应
- 无设计文档时在第6章风险章节标注"无设计文档追溯"
- 风险处置建议必须按严重度排序（S1 优先）
