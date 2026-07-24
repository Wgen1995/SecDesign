# 知识库总索引（_index.md）

> 来源：secdesign_spec.md §2.4 + §2.7
> 用途：secdesign 安全知识全景总入口，索引7个可插拔知识层 + 进化机制。

---

## 7个知识层总表

| 知识层 | 名称 | 来源 | 条目数 | 用途 |
|--------|------|------|--------|------|
| KL-1 | 安全设计Checklist | 行业安全设计实践 | ~150条 | Phase1 攻击面识别时做需求扫描 |
| KL-2 | STRIDE威胁模板 | 微软SDL + STRIDE标准 | ~112条 | Phase2 威胁建模时做STRIDE分析 |
| KL-3 | OWASP标准簇 | OWASP Top10 + ASVS + API Security Top10 | ~300条 | Phase3 安全规格生成时做检查点映射 |
| KL-4 | CWE弱点映射 | CWE Top25 + SANS Top25 | ~50条 | Phase5 测试用例生成时做弱点-测试映射 |
| KL-5 | 攻击模式库 | OWASP攻击模式 + 云原生攻击模式 | ~88条 | Phase2 威胁细化 + Phase5 测试设计 |
| KL-6 | 合规规则库 | 凭证/加密/随机数/密码/数据保护/信息泄露/会话管理 + 容器合规 | ~300条 | Phase4 覆盖率检查 + Phase5 合规测试 |
| KL-7 | 运行时安全检查 | OWASP WSTG + ATT&CK容器/云矩阵 | ~130条 | Phase5 渗透测试用例 + Phase6 攻击链验证 |

---

## 三层映射体系

```
攻击面分类（KL-1，第一层）
  ├─ STRIDE威胁映射（KL-2，第二层）
  │    ├─ 检查点知识层（KL-3/KL-4/KL-6，第三层）
  │    ├─ 攻击模式库（KL-5）
  │    └─ 运行时检查（KL-7）
```

每个攻击面子类 → 映射适用的 STRIDE 威胁 → 映射到检查点/攻击模式/运行时检查。

---

## 需求粒度自适应

不同粒度的需求命中不同知识层：

| 需求粒度 | scope值 | 命中攻击面 | 必须加载 | 按需加载 |
|---------|---------|-----------|---------|---------|
| 接口级 | interface | 1-2个子类 | KL-1, KL-3, KL-5 | KL-4, KL-7 |
| 功能级 | function | 3-5个子类 | KL-1~5 | KL-6, KL-7 |
| 模块级 | module | 5-10个子类 | KL-1~6 | KL-7 |
| 系统级 | system | 10+个子类 | KL-1~7 | — |

---

## 进化机制

```
发现新攻击 → 写攻击模式(SKILL.md格式)
           → 映射到攻击面(Ax.x)
           → 映射STRIDE类型
           → 映射CWE/OWASP编号
           → 写入 KL-5 对应目录
           → 更新 _index.md

新标准发布 → 增加知识层目录(如 KL-8)
            → 更新 _index.md 总索引
            → 在映射表中追加条目
```

详见：[_evolution/_index.md](_evolution/_index.md)

---

## 目录链接

| 目录 | 说明 | 索引文件 |
|------|------|---------|
| [KL-1-checklist/](KL-1-checklist/_index.md) | 安全设计Checklist（32子类） | KL-1-checklist/_index.md |
| [KL-2-stride/](KL-2-stride/_index.md) | STRIDE威胁模板 | KL-2-stride/_index.md |
| [KL-3-owasp/](KL-3-owasp/_index.md) | OWASP标准簇 | KL-3-owasp/_index.md |
| [KL-4-cwe/](KL-4-cwe/_index.md) | CWE弱点映射 | KL-4-cwe/_index.md |
| [KL-5-attack-patterns/](KL-5-attack-patterns/_index.md) | 攻击模式库 | KL-5-attack-patterns/_index.md |
| [KL-6-compliance/](KL-6-compliance/_index.md) | 合规规则库 | KL-6-compliance/_index.md |
| [KL-7-runtime/](KL-7-runtime/_index.md) | 运行时安全检查 | KL-7-runtime/_index.md |
| [_evolution/](_evolution/_index.md) | 进化机制 | _evolution/_index.md |

---

> **注**：本文件为种子索引，完整知识层内容由 Plan 2 填充。当前各 KL 目录仅含 _index.md 桩文件。
