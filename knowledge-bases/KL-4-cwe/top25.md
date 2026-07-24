# CWE Top 25 弱点映射

> 来源：secdesign_spec.md 附录D
> 用途：Phase5 security-test-generator 做弱点-测试映射，为每个威胁关联CWE编号。

## 完整映射表

| 排名 | CWE | 名称 | 映射攻击面 | 映射OWASP |
|------|-----|------|-----------|----------|
| 1 | CWE-78 | OS命令注入 | A3.1/A2.1 | A03 |
| 2 | CWE-79 | XSS | A7.1/A3.1 | A03 |
| 3 | CWE-89 | SQL注入 | A2.1/A4.1 | A03 |
| 4 | CWE-94 | 代码注入 | A3.2/A3.1 | A03 |
| 5 | CWE-190 | 整数溢出 | A3.1 | A03 |
| 6 | CWE-200 | 信息暴露 | A4.4/A2.1 | A01 |
| 7 | CWE-22 | 路径穿越 | A3.2 | A01 |
| 8 | CWE-284 | 不当访问控制 | A2.2/A2.3 | A01 |
| 9 | CWE-295 | 证书校验不当 | A7.2/A7.3 | A02 |
| 10 | CWE-319 | 明文传输 | A7.3 | A02 |
| 11 | CWE-327 | 弱加密算法 | A4.2/A7.3 | A02 |
| 12 | CWE-330 | 不安全随机数 | A1.3/A8.1 | A02 |
| 13 | CWE-384 | 会话固定 | A1.3 | A07 |
| 14 | CWE-434 | 不受限制文件上传 | A3.2 | A03 |
| 15 | CWE-502 | 不安全反序列化 | A3.1/A5.5 | A08 |
| 16 | CWE-522 | 凭证保护不足 | A1.4/A4.2 | A02 |
| 17 | CWE-611 | XXE | A3.1/A3.2 | A03 |
| 18 | CWE-639 | 通过ID授权 | A2.3 | A01 |
| 19 | CWE-732 | 权限分配不当 | A5.3/A6.2 | A05 |
| 20 | CWE-798 | 硬编码凭证 | A1.4/A5.3 | A02 |
| 21 | CWE-862 | 缺少授权 | A2.1/A2.2 | A01 |
| 22 | CWE-918 | SSRF | A2.1/A7.2 | A10 |
| 23 | CWE-125 | 越界读取 | A3.1 | A01 |
| 24 | CWE-787 | 越界写入 | A3.1 | A03 |
| 25 | CWE-269 | 不当权限管理 | A2.2/A6.2 | A01 |

---

## 条目详解

### #1 CWE-78 OS命令注入（Improper Neutralization of Special Elements used in an OS Command）

软件构造提交给命令解释器的命令时使用了来自外部输入的不完整数据，导致攻击者注入并执行任意操作系统命令。
- 测试建议：注入 `;`/`|`/`$()` 等命令分隔符与参数化调用对比，验证服务端是否过滤拼接。

### #2 CWE-79 跨站脚本（XSS）

软件在生成网页时未对用户输入做充分校验或转义，导致攻击者注入恶意脚本在受害者浏览器上下文执行。
- 测试建议：反射/存储/DOM 三型分别构造 payload，验证输出编码与 CSP 头。

### #3 CWE-89 SQL注入（Improper Neutralization of Special Elements used in an SQL Command）

软件构造 SQL 命令时使用了来自外部不可信输入的数据，导致攻击者执行任意 SQL 读取/篡改/删除数据。
- 测试建议：注入 `'`/`--`/`UNION`，对比参数化查询与拼接查询行为。

### #4 CWE-94 代码注入（Improper Control of Generation of Code）

软件动态构造或评估代码时使用了来自外部输入的数据，导致攻击者注入并执行任意代码（如 eval/exec）。
- 测试建议：注入语言特定求值 payload（`{{7*7}}`/`__import__`），验证是否被求值执行。

### #5 CWE-190 整数溢出或环绕（Integer Overflow/Wrap-around）

计算结果超出可表示范围且未正确处理，导致意外行为、缓冲区溢出或逻辑绕过。
- 测试建议：输入边界极值（INT_MAX+1、负数、超大长度），验证溢出处理。

### #6 CWE-200 敏感信息暴露（Exposure of Sensitive Information to an Unauthorized Actor）

产品向未授权方暴露了敏感信息，如错误信息泄露内部架构、版本、堆栈或用户数据。
- 测试建议：触发错误响应、枚举接口，验证是否泄露内部信息。

### #7 CWE-22 路径穿越（Path Traversal）

软件使用外部输入构造路径时未做限制，导致攻击者访问目标目录之外的路径（`../` 序列）。
- 测试建议：注入 `../`/`..%2f`/绝对路径，验证路径规范化与白名单。

### #8 CWE-284 不当访问控制（Improper Access Control）

软件未对主体执行适当的访问控制，允许攻击者执行越权操作或访问本应受限资源。
- 测试建议：水平/垂直越权测试，验证每个资源/功能的权限校验。

### #9 CWE-295 证书校验不当（Improper Certificate Validation）

软件未正确校验证书（链/有效期/主机名），导致中间人攻击或接受伪造证书。
- 测试建议：使用过期/自签名/主机名不匹配证书连接，验证是否被拒绝。

### #10 CWE-319 敏感信息明文传输（Cleartext Transmission of Sensitive Information）

敏感信息以明文传输，可被网络窃听者读取。
- 测试建议：抓包确认全链路 TLS，验证无 HTTP 明文敏感传输。

### #11 CWE-327 使用已破解或高风险加密算法（Use of a Broken or Risky Cryptographic Algorithm）

使用了已被破解或存在风险的加密算法（DES/RC4/MD5/SHA1 用于安全场景）。
- 测试建议：检查算法/套件配置，验证禁用弱算法并使用 AES-GCM/RSA-2048+。

### #12 CWE-330 使用不充分随机数（Use of Insufficiently Random Values）

使用不充分的随机数生成（如伪随机/固定种子），导致 Token/SessionID/ticket 可预测。
- 测试建议：采集大量生成值分析可预测性，验证使用 CSPRNG。

### #13 CWE-384 会话固定（Session Fixation）

攻击者强制固定会话标识，登录后该标识不变，从而劫持用户会话。
- 测试建议：登录前后对比 SessionID，验证登录后重置会话。

### #14 CWE-434 不受限制危险类型文件上传（Unrestricted Upload of File with Dangerous Type）

未限制上传文件类型，允许上传可执行文件（Webshell）等危险类型。
- 测试建议：上传 `.php`/`.jsp`/`.html`/图片马，验证类型白名单与内容检测。

### #15 CWE-502 不可信数据反序列化（Deserialization of Untrusted Data）

反序列化不可信数据，可导致远程代码执行或权限提升。
- 测试建议：构造恶意序列化 payload，验证是否启用白名单/签名校验。

### #16 CWE-522 凭证保护不足（Insufficiently Protected Credentials）

凭证未得到充分保护（明文存储/弱哈希/明文传输），可被提取或破解。
- 测试建议：检查凭证存储与传输，验证 bcrypt/Argon2 + TLS。

### #17 CWE-611 XXE（Improper Restriction of XML External Entity Reference）

XML 解析器处理外部实体引用不当，导致文件读取/SSRF/拒绝服务。
- 测试建议：提交含外部实体的 XML，验证 DTD/外部实体被禁用。

### #18 CWE-639 通过用户可控键绕过授权（IDOR）

系统通过用户可控 ID 授权资源访问，未校验所有权，导致通过 ID 枚举越权访问他人资源。
- 测试建议：替换资源 ID 为他人 ID，验证对象级所有权校验。

### #19 CWE-732 关键资源权限分配不当（Incorrect Permission Assignment for Critical Resource）

关键资源（配置/密钥/脚本）权限分配不当，允许未授权读取或修改。
- 测试建议：检查文件/目录权限，验证配置≤600、目录≤750。

### #20 CWE-798 使用硬编码凭证（Use of Hard-coded Credentials）

硬编码凭证在源码/配置中，无法轮换且可被提取。
- 测试建议：源码/配置/镜像扫描凭证，验证使用 KMS/Secret 注入。

### #21 CWE-862 缺少授权（Missing Authorization）

对本应受限的功能缺少授权检查，允许任意用户访问。
- 测试建议：无认证/低权限调用敏感端点，验证授权缺失。

### #22 CWE-918 SSRF（Server-Side Request Forgery）

服务端根据用户输入发起请求，可探测内网或访问云元数据获取凭证。
- 测试建议：注入内网地址/169.254.169.254，验证白名单与 IMDSv2。

### #23 CWE-125 越界读取（Out-of-bounds Read）

读取缓冲区边界之外的数据，导致信息泄露或崩溃。
- 测试建议：边界长度输入触发的读取，验证长度校验与内存安全。

### #24 CWE-787 越界写入（Out-of-bounds Write）

写入缓冲区边界之外的数据，导致内存破坏、代码执行或崩溃。
- 测试建议：超大/负长度输入触发的写入，验证边界检查。

### #25 CWE-269 不当权限管理（Improper Privilege Management）

权限管理不当，导致权限提升（如过度授权、sudo 滥用、特权容器逃逸）。
- 测试建议：低权限尝试高权限操作、容器内访问宿主资源，验证最小权限与隔离。
