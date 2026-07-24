#!/usr/bin/env python3
"""Convert security_graph.json to HTML traceability graph using Mermaid."""
import json
import sys
import argparse
from pathlib import Path


def convert(graph_file: str, output_file: str) -> None:
    with open(graph_file, "r", encoding="utf-8") as f:
        graph = json.load(f)

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    type_styles = {
        "requirement": ("req", "#4CAF50"),
        "security_assessment": ("assess", "#2196F3"),
        "attack_surface": ("surface", "#FF9800"),
        "threat": ("threat", "#F44336"),
        "security_check": ("check", "#9C27B0"),
        "security_test": ("test", "#00BCD4"),
        "finding": ("finding", "#795548"),
        "doc_chunk": ("doc", "#607D8B"),
    }

    mermaid_lines = ["graph TD"]

    for node in nodes:
        node_type = node.get("type", "unknown")
        node_id = node.get("id", "").replace("-", "_")
        name = node.get("name", node_id).replace('"', "'")
        prefix, color = type_styles.get(node_type, ("other", "#9E9E9E"))
        status = node.get("status", node.get("state", ""))
        label = f"{name}"
        if status:
            label += f" {status}"
        mermaid_lines.append(f'    {node_id}["{label}"]:::{prefix}')

    edge_labels = {
        "has_surface": "攻击面",
        "has_threat": "威胁",
        "traces_to": "追溯",
        "mapped_by": "映射",
        "covers": "覆盖",
        "checked_by": "检查",
        "published_as": "发布",
        "audited_by": "签核",
    }

    for edge in edges:
        src = edge.get("from", "").replace("-", "_")
        dst = edge.get("to", "").replace("-", "_")
        etype = edge.get("type", "")
        label = edge_labels.get(etype, etype)
        mermaid_lines.append(f"    {src} -->|{label}| {dst}")

    for prefix, color in type_styles.values():
        mermaid_lines.append(f"    classDef {prefix} fill:{color},color:white,stroke-width:2px")

    mermaid_code = "\n".join(mermaid_lines)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>secdesign 追溯图 - {graph.get('requirement_id', '')}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{ font-family: sans-serif; margin: 20px; background: #fafafa; }}
        h1 {{ color: #333; }}
        .mermaid {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <h1>secdesign 安全测试追溯图</h1>
    <p>需求编号: {graph.get('requirement_id', '')}</p>
    <div class="mermaid">
{mermaid_code}
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose' }});
    </script>
</body>
</html>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML graph written to {output_file} ({len(nodes)} nodes, {len(edges)} edges)")


def main():
    parser = argparse.ArgumentParser(description="Convert security_graph.json to HTML graph")
    parser.add_argument("--graph", required=True, help="Path to security_graph.json")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    args = parser.parse_args()
    convert(args.graph, args.output)


if __name__ == "__main__":
    main()
