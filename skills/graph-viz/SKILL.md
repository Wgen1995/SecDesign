---
name: graph-viz
description: >
  安全测试追溯图谱可视化生成器（可选能力）。读取 .secdesign_output/{requirement_id}/
  下的 security_graph.json，生成交互式 HTML 可视化文件，支持在线/离线两种模式。
  使用场景：Phase7 完成后生成可视化报告，或任意时刻查看追溯图谱。
  不使用场景：security_graph.json 为空或不存在。
---

# 知识图谱可视化生成（可选）

## §0 套件根定位

同入口 SKILL.md §0。本技能的参考文件位于 `{套件根}/skills/graph-viz/`。

## 定位

**可选能力**，不阻塞 Pipeline。Phase7 完成后自动调用，也可手动调用。

## 执行方式

### 方式一：直接运行 Python 脚本（推荐，100% 复现）

```bash
# 默认：离线模式（推荐，约 520KB，完全自包含）
python3 {套件根}/skills/graph-viz/generate_viz.py -g {output_dir}/json_file/security_graph.json --offline

# 在线模式（约 170KB，需联网）
python3 {套件根}/skills/graph-viz/generate_viz.py -g {output_dir}/json_file/security_graph.json --online

# 自定义输出路径和标题
python3 {套件根}/skills/graph-viz/generate_viz.py -g {output_dir}/json_file/security_graph.json --offline -o {output_dir}/report/security_graph_viz.html -t "安全测试追溯图"
```

> **推荐使用 `--offline` 离线模式**：cytoscape.js 内嵌在 HTML 中，不依赖网络，文件可发送给任何人。

### 方式二：LLM 直接生成（当脚本不可用时）

当 Python 环境不可用或需要定制时，LLM 参考 `template.html` 直接生成 HTML。

## 参考文件

| 文件 | 作用 |
|------|------|
| `skills/graph-viz/template.html` | HTML 模板——完整的 CSS 样式、Cytoscape.js 图逻辑、交互功能 |
| `skills/graph-viz/generate_viz.py` | Python 生成脚本——读取 JSON、注入数据到模板 |
| `skills/graph-viz/example_output.html` | 已验证示例输出 |

## 数据前提

**所有数据由 secdesign Pipeline 生成，格式固定。** 可视化的职责是忠实展示追溯图谱。

### 数据源

| 文件 | 内容 | 格式 |
|------|------|------|
| `json_file/security_graph.json` | 知识图谱（节点+边） | `{requirement_id, version, nodes:[], edges:[]}` |
| `progress.json` | Phase 状态 | `{current_phase, mode, phases:{...}}` |
| `attack_surfaces/attack_surfaces.json` | 攻击面详情 | `{surfaces:[{id,category,name,...}]}` |
| `threats/threats.json` | 威胁详情 | `{threats:[{id,surface_id,stride_type,severity,...}]}` |

### 节点类型（10 种）

| type | 含义 | 形状 | 颜色 | 特殊标记 |
|------|------|------|------|---------|
| requirement | 需求 | round-rectangle | #4CAF50 | 根节点 |
| security_assessment | 安全预检 | round-rectangle | #2196F3 | verdict 着色 |
| attack_surface | 攻击面 | ellipse | #FF9800 | state 五态着色（✅⚠️❌❓⬜） |
| doc_chunk | 文档分块 | rectangle | #607D8B | 虚线边框（辅助节点） |
| threat | 威胁 | diamond | 按 severity 着色 | STRIDE 类型标签 |
| security_check | 安全检查点 | hexagon | #9C27B0 | KL 层级标签 |
| finding | 覆盖率发现 | round-rectangle | 按 verdict 着色 | 红色发光（未覆盖） |
| security_test | 测试用例 | vee | #00BCD4 | source 图标（📄威胁推导/🧠LLM补充/📋规则补充） |
| publish_node | 发布产物 | rectangle | #6e7681 | Phase7 产物 |
| gate | 签核节点 | round-rectangle | #58a6ff | ⚙️auto自动门控 / 👤interactive人工签核 |

### 边类型（9 种）

| type | 含义 | 线型 | 颜色 | 说明 |
|------|------|------|------|------|
| has_surface | 需求→攻击面 | 实线 | #4CAF50 | 粗线 |
| traces_to | 攻击面→文档片段 | 虚线 | #607D8B | 细线 |
| has_threat | 攻击面→威胁 | 实线 | #FF9800 | 中线 |
| mapped_by | 威胁→检查点 | 实线 | #9C27B0 | 中线，标签显示 KL 层级 |
| traces_to_req | 检查点→需求 | 虚线 | #4CAF50 | 细线（回溯边） |
| covers | 测试用例→威胁 | 实线 | #00BCD4 | 中线 |
| checked_by | 发现→检查点 | 点线 | 按 verdict | 细线 |
| published_as | 测试用例→发布产物 | 虚线 | #6e7681 | 细线 |
| audited_by | 需求→签核记录 | 点线 | #58a6ff | 细线 |

### 五态着色（attack_surface 节点）

| state | 颜色 | 说明 |
|-------|------|------|
| ✅ | #38a169 绿色 | 已覆盖（有检查点+有测试用例） |
| ⚠️ | #d29922 橙色 | 部分覆盖（有检查点+缺测试用例） |
| ❌ | #f85149 红色 | 未覆盖（无检查点） |
| ❓ | #58a6ff 蓝色 | 待确认 |
| ⬜ | #6e7681 灰色 | 未评估 |

### 严重度着色（threat 节点）

| severity | 颜色 | 说明 |
|----------|------|------|
| S1 | #f85149 红色 | 严重（DREAD 20-25） |
| S2 | #d29922 橙色 | 高（DREAD 12-19） |
| S3 | #e3b341 黄色 | 中（DREAD 6-11） |
| S4 | #768390 灰色 | 低（DREAD 0-5） |

### STRIDE 类型图标

| STRIDE | 图标 | 说明 |
|--------|------|------|
| S | 🎭 | Spoofing 仿冒 |
| T | ✏️ | Tampering 篡改 |
| R | 📝 | Repudiation 抵赖 |
| I | 👁️ | Information Disclosure 信息泄露 |
| D | 🚫 | Denial of Service 拒绝服务 |
| E | ⬆️ | Elevation of Privilege 提权 |

## 页面布局（从上到下）

1. **统计栏**：需求编号 / 节点数 / 边数 / 攻击面数 / 威胁数 / 检查点数 / 测试用例数 / 覆盖率 / 模式
2. **Phase 时间轴**：Phase0→0.5→1→2→3→4→5→6→7，点击高亮该 Phase 产出的节点和边
3. **工具栏**：节点类型过滤 / STRIDE 过滤 / 严重度过滤 / 搜索 / 布局切换
4. **主图区**（flex:1）+ **右侧面板**（400px）
5. **图例**：左下角浮动，可折叠

## 交互功能

- **点击节点**：右侧面板显示属性 + 入出边列表（可点击跳转）
- **点击边**：右侧面板显示边详情
- **悬停**：tooltip 显示摘要
- **双击 attack_surface 节点**：高亮该攻击面的完整追溯链（→威胁→检查点→测试用例）
- **点击 Phase 时间轴**：高亮该 Phase 产出的节点和边，其余淡化
- **过滤工具栏**：节点类型/STRIDE/严重度复选框过滤 + 搜索 + 布局切换
- **覆盖率面板**：右侧底部显示覆盖率矩阵（攻击面×五态统计）
- **威胁分布面板**：右侧显示 S1/S2/S3/S4 分布 + STRIDE 分布

## 参数说明

| 参数 | 简写 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--graph` | `-g` | 是 | — | security_graph.json 路径 |
| `--output` | `-o` | 否 | `{graph_dir}/../report/security_graph_viz.html` | 输出 HTML 路径 |
| `--offline` | — | 否 | 否 | 离线模式：内嵌 cytoscape.js（推荐） |
| `--online` | — | 否 | 是 | 在线模式：CDN（默认） |
| `--title` | `-t` | 否 | 自动生成 | HTML 页面标题 |

## 在 Pipeline 中的集成

Phase7 完成后，入口 SKILL.md 追加执行：

```bash
python3 {套件根}/skills/graph-viz/generate_viz.py -g {output_dir}/json_file/security_graph.json --offline -o {output_dir}/report/security_graph_viz.html
```

生成成功后输出路径：`{output_dir}/report/security_graph_viz.html`

此步为可选能力，失败不阻塞 Pipeline。

## 红线

- 不修改原始 security_graph.json
- 不丢弃任何节点或边（完整展示）
- 未知节点/边类型用兜底样式，不崩溃
- 离线模式优先（可发送给任何人）
