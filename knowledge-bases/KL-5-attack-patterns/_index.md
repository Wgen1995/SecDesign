# KL-5 攻击模式库 索引

> 来源：secdesign_spec.md 附录E + §7 + §2.7
> 用途：Phase2 threat-mapper 威胁细化 + Phase5 security-test-generator 测试设计。

---

## 9个子目录说明

| 子目录 | 类别 | 说明 | 种子攻击模式数 |
|--------|------|------|--------------|
| injection/ | 注入类 | SQL注入、XXE、代码注入等 | 2 |
| authz/ | 授权类 | IDOR、路径穿越等 | 2 |
| deser/ | 反序列化类 | Java反序列化等 | 1 |
| data/ | 数据泄露类 | 凭证暴露等 | 1 |
| dos/ | 拒绝服务类 | 资源滥用等 | 1 |
| network/ | 网络类 | SSRF等 | 1 |
| escape/ | 容器逃逸类 | 特权容器逃逸等 | 1 |
| persist/ | 持久化类 | 后门Pod/DaemonSet等 | 0（待填充） |
| supply/ | 供应链类 | 依赖投毒等 | 0（待填充） |

---

## 攻击模式统一格式

每个攻击模式文件遵循以下格式：

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

---

## 种子攻击模式索引

### injection/sql-injection
- **攻击面**: A2.1, A4.1
- **STRIDE映射**: T+I
- **CWE**: CWE-89
- **OWASP**: A03
- **攻击路径**: 用户输入(Source: HTTP参数) → 字符串拼接SQL → 数据库执行(Sink: Statement.execute)
- **影响**: 机密性(数据泄露)+完整性(数据篡改)+可用性(删库)

### injection/xxe
- **攻击面**: A3.1, A3.2
- **STRIDE映射**: T+I
- **CWE**: CWE-611
- **OWASP**: A03
- **攻击路径**: XML输入(Source: HTTP Body/上传文件) → XML解析器 → 外部实体加载(Sink: DocumentBuilder/SAXParser)
- **影响**: 机密性(任意文件读取)+完整性(SSRF)

### authz/idor
- **攻击面**: A2.3
- **STRIDE映射**: I+E
- **CWE**: CWE-639
- **OWASP**: A01
- **攻击路径**: 修改API中的userId/orderId(Source: URL路径参数) → 服务端未校验所有权 → 返回他人数据(Sink: 数据库查询)
- **影响**: 机密性(跨用户数据泄露)

### authz/path-traversal
- **攻击面**: A3.2
- **STRIDE映射**: T+I
- **CWE**: CWE-22
- **OWASP**: A01
- **攻击路径**: 文件名参数(Source: HTTP参数) → 路径拼接 → 越界读取(Sink: File.readFile)
- **影响**: 机密性(任意文件读取)

### deser/java-deserialization
- **攻击面**: A3.1, A5.5
- **STRIDE映射**: T+E
- **CWE**: CWE-502
- **OWASP**: A08
- **攻击路径**: 序列化数据(Source: HTTP Body/Cookie/MQ) → ObjectInputStream.readObject() → 利用链触发(Sink: Runtime.exec)
- **影响**: 完整性+可用性(RCE)

### data/credential-exposure
- **攻击面**: A1.4, A4.2, A4.4
- **STRIDE映射**: I
- **CWE**: CWE-798, CWE-522, CWE-200
- **OWASP**: A02
- **攻击路径**: 凭证硬编码(Source: 源代码/配置文件) → 日志打印/错误回显(Sink: 日志文件/HTTP响应)
- **影响**: 机密性(凭证泄露→系统被控)

### dos/resource-abuse
- **攻击面**: A2.1, A8.3
- **STRIDE映射**: D
- **CWE**: CWE-400, CWE-770
- **OWASP**: API4
- **攻击路径**: 大量请求(Source: 自动化脚本) → 无限流服务端 → 资源耗尽(Sink: CPU/内存/连接池)
- **影响**: 可用性(服务不可用)

### escape/privileged-container
- **攻击面**: A6.1, A6.2
- **STRIDE映射**: E+I
- **CWE**: CWE-269
- **OWASP**: A01
- **攻击路径**: privileged Pod(Source: K8s部署配置) → mount宿主机磁盘 → chroot(Sink: 宿主机控制)
- **影响**: 完整性+机密性+可用性(宿主机完全控制)

### network/ssrf
- **攻击面**: A2.1, A7.2
- **STRIDE映射**: I
- **CWE**: CWE-918
- **OWASP**: A10
- **攻击路径**: URL参数(Source: HTTP参数) → 服务端发起请求 → 内网访问/元数据(Sink: HttpClient.execute)
- **影响**: 机密性(内网信息/云AK-SK泄露)

---

## 进化机制

新发现的攻击模式通过进化机制写入 KL-5：

```
发现新攻击 → 写攻击模式(上述统一格式)
           → 映射到攻击面(Ax.x)
           → 映射STRIDE类型
           → 映射CWE/OWASP编号
           → 写入 KL-5 对应子目录
           → 更新本 _index.md
```

新攻击模式存放于 [_evolution/_learned/](_learned/)，经审核后迁移到对应子目录。

---

> **注**：本文件为种子索引。9个子目录下的完整攻击模式文件由 Plan 2 填充。persist/ 和 supply/ 子目录尚无种子内容。
