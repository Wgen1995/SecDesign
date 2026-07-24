---
name: security-prescreen
description: Use when determining if a requirement has a security surface, assessing granularity, and selecting knowledge layers. Scans keywords, matches KL-1 index, estimates threat count, and gates per QUALITY_GATES.md.
---

# 需求安全预检 (Phase0.5)

## 概述

判定需求是否有安全面，判定需求粒度（scope），选择需要加载的知识层，估算威胁数量。这是需求进入攻击面识别前的第一道门控，目的是尽早识别无安全面的需求（快速通过）和过于复杂的需求（建议拆分）。

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
| MUST 输入 | `requirement_context/requirement_info.json` |
| MUST 输出 | `requirement_context/security_prescreen.json` + `json_file/security_graph.json`（含 security_assessment 节点） |

## 处理流程

1. 读取 `.secdesign_output/{requirement_id}/requirement_context/requirement_info.json`
2. 读取 `{套件根}/rules/prescreen-keywords.md`（32 子类匹配关键词完整表）
3. 扫描 description 和 acceptance_criteria 中的安全关键词
4. 匹配 KL-1 的关键词索引（`knowledge-bases/KL-1-checklist/_index.md`），记录命中的攻击面子类
5. 判定需求粒度（scope 字段优先；缺失时根据描述复杂度自动判定）
6. 判定是否有安全面（matched_categories 为空则 has_security_surface=false）
7. 估算威胁数量（基于攻击面×STRIDE 适用数）
8. 选择推荐知识层（依据粒度，参考 §2.6 粒度自适应表）
9. 判定门控裁决（依据 QUALITY_GATES.md §1.2）
10. 输出 security_prescreen.json

## 关键词匹配规则

完整规则在 `{套件根}/rules/prescreen-keywords.md`。部分示例：

| 攻击面子类 | 匹配关键词 |
|-----------|-----------|
| A1.1 新增用户 | 注册、账号、用户、认证、登录、Signup、CreateUser |
| A1.4 凭证存储 | 密码、口令、密钥、Token、凭证、AK/SK、credential |
| A2.1 新增API | 接口、API、REST、RPC、端点、路由、Controller |
| A3.2 文件上传下载 | 上传、下载、附件、导入、导出、Upload、File |
| A5.1 新增微服务 | 微服务、容器、Docker、K8s、部署 |
| A6.2 K8s资源 | Pod、Deployment、Service、RBAC、NetworkPolicy |
| A8.1 高危操作 | 删除、重置、修改密码、二次认证、二次授权 |

## 粒度自动判定规则

scope 字段存在时直接使用；缺失时按以下规则自动判定：

| 条件 | 判定粒度 |
|------|---------|
| 描述提及单个 API 或接口 | interface |
| 描述提及 1-2 个功能点 | function |
| 描述提及多个功能模块或 3+ 功能点 | module |
| 描述提及架构变更/迁移/整体系统 | system |

## 威胁数估算算法

```
estimated_threat_count = Σ(每个 matched_category 的 STRIDE 适用数)
范围表示：取 ±20% 浮动
```

示例：命中 A3.2(T,I,D,E=4) + A2.1(S,T,R,I,D,E=6) + A4.2(T,I,E=3) = 13
范围：13 × 0.8 = 10, 13 × 1.2 = 16 → "10-16"

阈值判定：
- ≤30：proceed（正常继续）
- \>30：complex（建议拆分需求）

## 知识层选择

依据粒度自适应（参考规格 §2.6）：

| 需求粒度 | scope 值 | 必须加载 | 按需加载 |
|---------|---------|---------|---------|
| 接口级 | interface | KL-1, KL-3, KL-5 | KL-4, KL-7 |
| 功能级 | function | KL-1~5 | KL-6, KL-7 |
| 模块级 | module | KL-1~6 | KL-7 |
| 系统级 | system | KL-1~7 | — |

## 输出格式

security_prescreen.json：

```json
{
  "requirement_id": "REQ-001",
  "scope": "function",
  "has_security_surface": true,
  "matched_categories": ["A3.2", "A2.1", "A4.2"],
  "estimated_threat_count": "10-16",
  "recommended_knowledge_layers": ["KL-1", "KL-2", "KL-3", "KL-4", "KL-5"],
  "verdict": "proceed",
  "verdict_reason": "命中3个攻击面，预计10-16个威胁，建议加载KL-1~5"
}
```

## 门控规则

依据 `{套件根}/skills/shared/QUALITY_GATES.md` §1.2：

| 条件 | verdict | 后续动作 |
|------|---------|---------|
| has_security_surface == false | skip | 跳过 Phase1-2，Phase3 标记"无安全面" |
| scope == system 且无 design_docs | conditional | 提示补充架构文档，询问继续或暂停 |
| estimated_threat_count > 30 | complex | 建议拆分需求，询问继续或拆分 |
| force == true | proceed | 跳过预检直接进入 Phase1 |

## 更新知识图谱

读取 `.secdesign_output/{requirement_id}/json_file/security_graph.json`，追加：

```json
{
  "id": "asm-{requirement_id}",
  "type": "security_assessment",
  "verdict": "proceed",
  "matched_categories": ["A3.2", "A2.1", "A4.2"],
  "scope": "function",
  "status": "✅"
}
```

写回 security_graph.json（独占写入，参考 OUTPUT_STANDARD.md §7）。

## 更新 progress.json

- verdict == "proceed" → `phases.phase0.5` = `"completed"`
- verdict == "skip" → `phases.phase0.5` = `"completed"`，`phases.phase1` 和 `phase2` 标记为 `"skipped"`
- verdict == "conditional" 且用户选择继续 → `phases.phase0.5` = `"completed"`
- verdict == "conditional" 且用户选择暂停 → `phases.phase0.5` = `"terminated"`
- verdict == "complex" 且用户选择拆分 → `phases.phase0.5` = `"terminated"`，提示拆分后重新运行
- force == true → `phases.phase0.5` = `"forced_pass"`

## 红线

- 不修改原始需求内容（requirement_info.json 由 Phase0 产出，本 Phase 只读取）
- 关键词匹配必须基于 rules/prescreen-keywords.md，不靠 LLM 感觉判定
- matched_categories 为空时 has_security_surface 必须为 false
- 威胁数估算必须附计算依据（记录每个命中子类的 STRIDE 适用数）
- 不阻塞用户强制继续（force == true 时无条件放行）
- scope 字段优先于自动判定，不覆盖用户显式指定的 scope
