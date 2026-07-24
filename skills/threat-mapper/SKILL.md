---
name: threat-mapper
description: Use when mapping STRIDE threats to each attack surface, linking KL-5 attack patterns, and scoring risk with DREAD. Applies cloud multi-tenant amplification rules and severity mapping.
---

# 威胁映射 (Phase2)

## 概述

对每个攻击面逐个套 STRIDE，映射 KL-5 攻击模式，生成威胁列表。每个威胁记录 STRIDE 分类、攻击路径、CWE/OWASP 编号、DREAD 评分和严重度。为 Phase3 安全规格生成提供威胁输入。

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
| MUST 输入 | `attack_surfaces/attack_surfaces.json` + `requirement_context/requirement_info.json` |
| MUST 输出 | `threats/threats.json` + `json_file/security_graph.json`（含 threat 节点 + has_threat 边） |

## 知识库引用

- `{套件根}/knowledge-bases/KL-2-stride/`（6 个 STRIDE 文件，每个文件内按攻击面子类分节）
- `{套件根}/knowledge-bases/KL-5-attack-patterns/`（攻击模式库，按攻击面分类索引）
- `{套件根}/rules/severity-rules.md`（DREAD→S1-S4 严重度映射 + 云环境放大规则）

## 处理流程

1. 读取 `.secdesign_output/{requirement_id}/attack_surfaces/attack_surfaces.json`
2. 读取 `.secdesign_output/{requirement_id}/requirement_context/requirement_info.json`
3. 读取 `{套件根}/knowledge-bases/KL-2-stride/` 下的 STRIDE 模板文件
4. 读取 `{套件根}/knowledge-bases/KL-5-attack-patterns/_index.md`（攻击模式索引）
5. 对每个攻击面，遍历其 `stride_applicable` 中的每个 STRIDE 类型：
   - 从 KL-2 读取对应的威胁模板（如 `tampering.md` 中 A3.2 节）
   - 根据攻击面上下文细化威胁描述
   - 从 KL-5 映射具体攻击模式（按攻击面子类索引）
   - 映射 CWE/OWASP 编号
   - 用 DREAD 评分法做风险评级
6. 汇总所有威胁，输出 threats.json

## DREAD 评分

每个维度 1-5 分连续标尺：

| 维度 | 1分 | 2分 | 3分 | 4分 | 5分 |
|------|-----|-----|-----|-----|-----|
| Damage(损害) | 无影响 | 轻微影响 | 部分数据泄露 | 大量数据泄露 | 全量数据泄露/RCE |
| Reproducibility(可复现) | 极难复现 | 需特殊条件 | 有条件复现 | 多数情况可复现 | 每次必现 |
| Exploitability(可利用性) | 需高权限+0day | 需高权限 | 需普通权限 | 需低权限 | 无需认证即可利用 |
| Affected users(影响范围) | 无影响用户 | 少数用户 | 部分租户 | 多数租户 | 全部租户 |
| Discoverability(可发现性) | 极难发现 | 难以发现 | 审计可发现 | 易于发现 | 公开接口可发现 |

## 严重度映射

总分 25 分制：

| 总分 | 严重度 |
|------|--------|
| 20-25 | S1（严重） |
| 12-19 | S2（高） |
| 6-11 | S3（中） |
| 0-5 | S4（低） |

## 云环境多租户放大规则

依据 `{套件根}/rules/severity-rules.md`：

- 如果威胁影响跨租户数据隔离（A2.2/A2.3 相关），affected_users 自动升级为 5
- 如果威胁涉及云元数据服务(169.254.169.254)或 AK/SK 泄露，damage 自动升级为 5
- 如果 scope == system，所有 S3 级威胁至少升级为 S2

## 自适应分批

当攻击面数 > BATCH_THRESHOLD（默认 20，见 OUTPUT_STANDARD.md §8）时：

- 按攻击面分组并行威胁映射
- 各分组写入独立 threats 分片
- 全部完成后合并为 threats.json

用户不感知需求大小，Phase 内部自动分批。

## 输出格式

threats.json：

```json
{
  "requirement_id": "REQ-001",
  "threats": [
    {
      "id": "T-001",
      "surface_id": "AS-001",
      "stride_type": "T",
      "threat_name": "文件内容注入(Webshell/XXE)",
      "description": "上传恶意文件到服务器，通过文件内容注入实现代码执行",
      "attack_patterns": [
        {"layer": "KL-5", "id": "injection/xxe", "name": "XXE注入"},
        {"layer": "KL-5", "id": "injection/code-injection", "name": "代码注入"}
      ],
      "cwe": ["CWE-434", "CWE-79"],
      "owasp": ["A03-Injection", "A04-Insecure Design"],
      "dread": {
        "damage": 5,
        "reproducibility": 4,
        "exploitability": 3,
        "affected_users": 3,
        "discoverability": 4
      },
      "dread_total": 19,
      "severity": "S2",
      "mitigation": "文件类型白名单+内容检测+存储目录不可执行+重命名"
    }
  ],
  "summary": {
    "total_threats": 8,
    "by_severity": {"S1": 0, "S2": 3, "S3": 4, "S4": 1},
    "by_stride": {"S": 1, "T": 2, "R": 1, "I": 2, "D": 1, "E": 1}
  }
}
```

## 更新知识图谱

读取 `.secdesign_output/{requirement_id}/json_file/security_graph.json`，追加：

**threat 节点**：

```json
{
  "id": "t-001",
  "type": "threat",
  "surface_id": "as-001",
  "stride_type": "T",
  "severity": "S2",
  "name": "文件内容注入(Webshell/XXE)",
  "status": "⬜"
}
```

**has_threat 边**（attack_surface → threat）：

```json
{
  "from": "as-001",
  "to": "t-001",
  "type": "has_threat"
}
```

写回 security_graph.json（独占写入，参考 OUTPUT_STANDARD.md §7）。

## 更新 progress.json

将 `phases.phase2` 状态改为 `"completed"`。

## 红线

- 每个攻击面的每个 stride_applicable 类型必须至少生成 1 个威胁
- 威胁描述必须结合攻击面上下文细化，不直接复制 KL-2 模板原文
- 攻击模式必须从 KL-5 映射，不靠 LLM 自行编造
- DREAD 评分必须附评分理由（每维度记录判定依据）
- 严重度映射必须基于 rules/severity-rules.md，不自行调整阈值
- 云环境放大规则必须显式应用（在 threat 中记录 amplification_applied 字段）
