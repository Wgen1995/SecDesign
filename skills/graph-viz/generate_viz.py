#!/usr/bin/env python3
"""
secdesign Security Graph Visualizer Generator

从 security_graph.json 读取节点和边，生成交互式 HTML 可视化文件。

用法:
  python3 generate_viz.py --graph path/to/security_graph.json [--output path] [--offline]
  python3 generate_viz.py -g .secdesign_output/REQ-001/json_file/security_graph.json --offline

参数:
  --graph, -g     security_graph.json 路径                                 [必填]
  --output, -o    输出 HTML 文件路径                                        [默认: {graph_dir}/../report/security_graph_viz.html]
  --offline       离线模式：内嵌 cytoscape.min.js（文件约 520KB）
  --online        在线模式：使用 CDN 加载 cytoscape（默认，文件约 170KB）
  --title, -t     HTML 页面标题                                             [默认: 自动生成]

示例:
  # 离线模式（推荐）
  python3 generate_viz.py -g .secdesign_output/REQ-001/json_file/security_graph.json --offline

  # 自定义输出
  python3 generate_viz.py -g security_graph.json -o viz.html -t "安全测试追溯图"
"""

import argparse
import json
import os
import sys
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(SCRIPT_DIR, "template.html")
CYTOSCAPE_CDN = "https://unpkg.com/cytoscape@3.30.2/dist/cytoscape.min.js"
CYTOSCAPE_CDN_TAG = f'<script src="{CYTOSCAPE_CDN}"></script>'


def read_graph(graph_file):
    with open(graph_file, "r", encoding="utf-8") as f:
        return json.load(f)


def read_progress(graph_dir):
    progress_path = os.path.join(graph_dir, "..", "progress.json")
    if os.path.isfile(progress_path):
        with open(progress_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def download_cytoscape():
    print("[INFO] 下载 cytoscape.js (离线模式)...")
    try:
        req = urllib.request.Request(CYTOSCAPE_CDN, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            js_content = resp.read().decode('utf-8')
        print(f"[INFO] 下载完成: {len(js_content)} bytes")
        return js_content
    except Exception as e:
        print(f"[WARN] 下载失败: {e}, 回退到在线模式")
        return None


def generate(graph_file, output, offline, title=None):
    print(f"[INFO] 图谱文件: {graph_file}")
    graph_data = read_graph(graph_file)
    node_count = len(graph_data.get("nodes", []))
    edge_count = len(graph_data.get("edges", []))
    print(f"[INFO] 节点: {node_count}, 边: {edge_count}")

    if node_count == 0:
        print("[ERROR] 无节点数据，无法生成可视化")
        sys.exit(1)

    graph_dir = os.path.dirname(os.path.abspath(graph_file))
    progress = read_progress(graph_dir)
    graph_data["progress"] = progress

    if not os.path.isfile(TEMPLATE_FILE):
        print(f"[ERROR] 模板文件不存在: {TEMPLATE_FILE}")
        sys.exit(1)
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()

    data_js = "const graphData = " + json.dumps(graph_data, ensure_ascii=False) + ";"
    html = template.replace("__GRAPH_DATA__", data_js)

    if offline:
        js_content = download_cytoscape()
        if js_content:
            lib_tag = f'<script>\n{js_content}\n</script>'
        else:
            lib_tag = CYTOSCAPE_CDN_TAG
    else:
        lib_tag = CYTOSCAPE_CDN_TAG
    html = html.replace("__CYTOSCAPE_LIB__", lib_tag)

    if title:
        html = html.replace("__TITLE__", title)
    else:
        req_id = graph_data.get("requirement_id", "unknown")
        html = html.replace("__TITLE__", f"secdesign 安全追溯图 — {req_id}")

    os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html)

    file_size = os.path.getsize(output)
    mode_label = "离线" if offline else "在线"
    print(f"[OK] 生成完成: {output}")
    print(f"     模式: {mode_label} | 大小: {file_size / 1024:.0f} KB")
    print(f"     节点: {node_count} / 边: {edge_count}")


def main():
    parser = argparse.ArgumentParser(
        description="secdesign 安全追溯图谱可视化生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--graph", "-g", required=True, help="security_graph.json 路径")
    parser.add_argument("--output", "-o", default=None, help="输出 HTML 文件路径")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--offline", action="store_true", help="离线模式：内嵌 cytoscape.min.js")
    mode_group.add_argument("--online", action="store_true", help="在线模式：使用 CDN（默认）")
    parser.add_argument("--title", "-t", default=None, help="HTML 页面标题")

    args = parser.parse_args()
    graph_file = os.path.abspath(args.graph)
    if not os.path.isfile(graph_file):
        print(f"[ERROR] 图谱文件不存在: {graph_file}")
        sys.exit(1)

    if args.output:
        output = os.path.abspath(args.output)
    else:
        graph_dir = os.path.dirname(graph_file)
        output = os.path.join(graph_dir, "..", "report", "security_graph_viz.html")
        output = os.path.normpath(output)

    generate(graph_file, output, args.offline, args.title)


if __name__ == "__main__":
    main()
