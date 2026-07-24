---
name: security-test-generator
description: Use when converting security checkpoints to executable security test cases. Maps to KL-4/KL-5/KL-7, classifies by 9 categories, supports adaptive batching, and triggers CVR-05 self-check.
---

# 安全测试用例生成 (Phase5)

## 概述

将安全检查点转化为可执行的安全测试用例。每个测试用例包含攻击步骤、预期安全行为、验证方法和清理步骤。按 9 类前缀分类，标记 source 字段。生成后自检 CVR-05 威胁测试用例覆盖率。

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
| MUST 输入 | `security_spec/security_spec.json` + `threats/threats.json` + `attack_surfaces/attack_surfaces.json` |
| MUST 输出 | `security_tests/security_tests.md` + `security_tests/security_tests.json` + `json_file/security_graph.json`（含 security_test 节点 + covers 边） |

## 知识库引用

- `{套件根}/knowledge-bases/KL-4-cwe/`（CWE 弱点映射，用于弱点-测试映射）
- `{套件根}/knowledge-bases/KL-5-attack-patterns/`（攻击模式库，用于测试设计）
- `{套件根}/knowledge-bases/KL-7-runtime/`（运行时安全检查，OWASP WSTG + ATT&CK 容器/云矩阵）

## 安全测试用例模板

```markdown
## UC-{攻击面代号}-{序号} {测试名称}

| 字段 | 值 |
|------|-----|
| 用例编号 | UC-UPLOAD-001 |
| 关联威胁 | T-001(文件内容注入) |
| 攻击面 | AS-001(文件上传/下载) |
| CWE | CWE-434 |
| OWASP | A03-Injection |
| 严重程度 | S2-High |
| 攻击者角色 | 已认证普通用户 |
| source | threat_derived |

### 前置条件
- 已创建普通用户账号user_a
- 文件上传功能已部署且可访问

### 攻击步骤
1. 以user_a身份登录系统
2. 进入文件上传页面
3. 构造恶意文件(如test.jsp含Webshell代码)
4. 修改HTTP请求中Content-Type为image/jpeg
5. 上传恶意文件，观察服务端响应

### 预期结果（安全行为）
- 服务端拒绝上传，返回400/415
- 审计日志记录非法上传尝试（含用户、时间、文件类型）
- 上传目录不存在.jsp文件

### 验证方法
- 断言HTTP响应状态码 ∈ {400, 415}
- 检查上传目录: find /upload-dir -name "*.jsp" 返回空
- 检查审计日志: 包含"非法文件类型"关键字

### 清理步骤
- 删除测试账号user_a
- 清理审计日志中的测试记录
```

## 测试用例分类

对齐 OWASP WSTG：

| 类别 | 前缀 | 示例 |
|------|------|------|
| 认证测试 | UC-AUTH- | 暴力破解、会话固定、MFA绕过 |
| 授权测试 | UC-AC- | IDOR、水平越权、垂直越权 |
| 输入处理 | UC-INP- | SQL注入、XSS、命令注入、XXE |
| 文件处理 | UC-FILE- | 文件上传、路径穿越、XXE via文件 |
| 加密测试 | UC-CRYP- | 弱加密、证书校验、明文传输 |
| 配置测试 | UC-CONF- | 默认配置、开放管理接口、CORS |
| 日志审计 | UC-LOG- | 日志完整性、操作可追溯 |
| 业务逻辑 | UC-BUS- | 流程绕过、竞态条件、计费绕过 |
| 容器安全 | UC-CONT- | 特权容器、RBAC滥用、网络策略绕过 |

## source 字段

依据 OUTPUT_STANDARD.md §4：

| source 值 | 含义 | 使用场景 |
|-----------|------|---------|
| threat_derived | 从威胁模型直接推导 | 威胁有明确攻击路径的测试用例 |
| llm_inferred | LLM 基于安全经验补充 | 补充的边界场景和组合攻击 |
| rule_based | 基于合规规则(KL-6)或运行时检查(KL-7)补充 | 合规测试和运行时验证用例 |

## 处理流程

1. 读取 `.secdesign_output/{requirement_id}/security_spec/security_spec.json`
2. 读取 `.secdesign_output/{requirement_id}/threats/threats.json`
3. 读取 `.secdesign_output/{requirement_id}/attack_surfaces/attack_surfaces.json`
4. 读取 KL-4/KL-5/KL-7 知识库文件
5. 对每个威胁，根据其攻击模式和 CWE 设计测试用例：
   - 从 KL-5 获取攻击 payload 和攻击步骤模板
   - 从 KL-4 获取弱点验证方法
   - 从 KL-7 获取运行时检查项
   - 按测试用例模板填充字段
6. 编号：UC-{攻击面代号}-{序号}（如 UC-FILE-001、UC-FILE-002）
7. 标记每条测试用例的 source 字段
8. 保存到 `security_tests/security_tests.md` 和 `security_tests/security_tests.json`
9. **CVR-05 自检**：统计有测试用例的威胁数 / 总威胁数，不达标时触发返工

## 自适应分批

当威胁数 > BATCH_THRESHOLD（默认 20，见 OUTPUT_STANDARD.md §8）时：

- 按攻击面分组并行生成测试用例
- 各分组追加写入 tests.jsonl（每行一个用例 JSON）
- 全部完成后合并为 security_tests.json

用户不感知需求大小，Phase 内部自动分批。

## CVR-05 触发说明

生成测试用例后，自检威胁测试用例覆盖率（CVR-05）：

- CVR-05 = 有测试用例的威胁数 / 总威胁数
- 阈值 ≥ 90%
- 不达标且 phase5 返工次数 < 2：返工 Phase5 补用例
- 不达标且 phase5 返工次数 ≥ 2：标记 WARNING，继续 Phase6

返工流程依据 QUALITY_GATES.md §3.3。

## 输出格式

security_tests.json：

```json
{
  "requirement_id": "REQ-001",
  "version": "v1",
  "test_cases": [
    {
      "id": "UC-FILE-001",
      "threat_id": "T-001",
      "surface_id": "AS-001",
      "test_name": "恶意文件上传(Webshell)",
      "category": "UC-FILE",
      "cwe": ["CWE-434"],
      "owasp": ["A03-Injection"],
      "severity": "S2",
      "attacker_role": "已认证普通用户",
      "source": "threat_derived",
      "preconditions": ["已创建普通用户账号user_a", "文件上传功能已部署且可访问"],
      "attack_steps": ["以user_a身份登录", "进入文件上传页面", "构造恶意文件test.jsp", "上传恶意文件"],
      "expected_result": ["服务端拒绝上传返回400/415", "审计日志记录非法上传", "上传目录不存在.jsp文件"],
      "verification": ["断言HTTP状态码∈{400,415}", "检查上传目录无.jsp", "检查审计日志含非法文件类型"],
      "cleanup": ["删除测试账号user_a", "清理审计日志测试记录"]
    }
  ],
  "summary": {
    "total_cases": 15,
    "by_category": {"UC-AUTH": 2, "UC-AC": 3, "UC-INP": 4, "UC-FILE": 3, "UC-CRYP": 1, "UC-CONF": 1, "UC-LOG": 1},
    "by_source": {"threat_derived": 10, "llm_inferred": 3, "rule_based": 2},
    "cvr_05": {"covered_threats": 8, "total_threats": 8, "rate": 100, "verdict": "pass"}
  }
}
```

## 更新知识图谱

读取 `.secdesign_output/{requirement_id}/json_file/security_graph.json`，追加：

**security_test 节点**：

```json
{
  "id": "st-001",
  "type": "security_test",
  "threat_id": "t-001",
  "test_name": "UC-FILE-001 恶意文件上传",
  "source": "threat_derived",
  "status": "✅"
}
```

**covers 边**（security_test → threat）：

```json
{
  "from": "st-001",
  "to": "t-001",
  "type": "covers"
}
```

同时更新 attack_surface 节点的 state 字段（Phase4 后的 ✅/❌/❓ → Phase5 后的 ✅/⚠️/❌/❓）。

写回 security_graph.json（独占写入，参考 OUTPUT_STANDARD.md §7）。

## 更新 progress.json

- CVR-05 通过 → `phases.phase5` = `"completed"`，`artifact_versions.security_tests` = `"v1"`
- CVR-05 触发返工 → `phases.phase5` = `"rework"`，`rework_count.phase5` +1
- WARNING → `phases.phase5` = `"WARNING"`

## 红线

- 每个威胁至少生成 1 个测试用例（CVR-05 ≥ 90%）
- 攻击步骤必须可操作：每步是具体动作，不使用模糊表述
- 预期结果必须可验证：可观察、可量化、可判定 pass/fail
- 每条测试用例必须标记 source 字段（三选一）
- 验证方法必须具体（断言 HTTP 状态码、检查文件、检查日志等）
- 清理步骤必须完整（不残留测试数据）
- 测试用例分类必须使用 9 类前缀之一
