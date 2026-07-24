# 知识层进化机制（_evolution/_index.md）

> 来源：secdesign_spec.md §2.7
> 用途：定义知识层自我进化规则，支持新攻击模式沉淀和新标准扩展。

---

## 进化规则

### 规则1：发现新攻击模式

```
发现新攻击 → 写攻击模式(SKILL.md格式)
           → 映射到攻击面(Ax.x)
           → 映射STRIDE类型
           → 映射CWE/OWASP编号
           → 写入 KL-5 对应目录
           → 更新 KL-5/_index.md
```

#### 新攻击模式统一格式

```markdown
## AP-XXXX 攻击模式名称

- **攻击面**: A{x}.{y}
- **STRIDE映射**: T+I
- **CWE**: CWE-XXX
- **OWASP**: A0X
- **前提条件**: 攻击者需要什么权限/位置
- **攻击路径**: Source → ... → Sink
- **影响**: 机密性/完整性/可用性
- **检查点**: 设计时/编码时/测试时分别检查什么
- **修复方案**: 纵深防御建议
- **参考**: CVE/OWASP/ATT&CK链接
```

### 规则2：新标准发布

```
新标准发布 → 增加知识层目录(如 KL-8)
            → 更新 _index.md 总索引
            → 在映射表中追加条目
```

#### 扩展步骤

1. 在 `knowledge-bases/` 下创建新目录（如 `KL-8-newstandard/`）
2. 创建 `_index.md` 种子索引
3. 更新 `knowledge-bases/_index.md` 总表（追加行）
4. 更新 `knowledge-bases/_index.md` 目录链接表
5. 在三层映射表中追加条目

---

## _learned/ 目录说明

`_learned/` 目录存放新发现的攻击模式，由进化机制自动写入。

### 工作流程

1. 新攻击模式首先写入 `_learned/` 目录（文件名格式：`AP-XXXX-name.md`）
2. 经人工审核后，迁移到 KL-5 对应子目录（injection/authz/deser/data/dos/network/escape/persist/supply）
3. 更新 KL-5/_index.md 索引

### 目录结构

```
_evolution/
├── _index.md              # 本文件（进化规则）
└── _learned/              # 新发现的攻击模式
    └── .keep              # 占位文件
```

---

## 进化触发条件

| 触发条件 | 进化动作 |
|---------|---------|
| Phase6 评审发现未覆盖的新攻击路径 | 写入 _learned/ → 审核 → 迁移到 KL-5 |
| 渗透测试发现新型攻击 | 写入 _learned/ → 审核 → 迁移到 KL-5 |
| OWASP/CWE 发布新版本标准 | 更新 KL-3/KL-4 对应文件 |
| 新合规标准发布 | 增加 KL 目录 → 更新总索引 |

---

> **注**：进化机制为可选能力，默认不自动触发。需人工确认后执行迁移。
