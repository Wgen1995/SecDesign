## AP-0009 SSRF(服务端请求伪造)

- **攻击面**: A2.1, A7.2
- **STRIDE映射**: I
- **CWE**: CWE-918
- **OWASP**: A10
- **前提条件**: 应用根据用户输入发起HTTP请求
- **攻击路径**: URL参数(Source: HTTP参数) → 服务端发起请求 → 内网访问/元数据(Sink: HttpClient.execute)
- **影响**: 机密性(内网信息/云AK-SK泄露)
- **检查点**: 编码时(URL白名单/禁止内网IP)、测试时(169.254.169.254/127.0.0.1/内网IP探测)
- **修复方案**: URL白名单+内网IP过滤+IMDSv2+出站网络限制
- **参考**: https://owasp.org/www-community/attacks/Server_Side_Request_Forgery
