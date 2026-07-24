#!/usr/bin/env python3
"""Convert security_tests.json to SARIF 2.1.0 format."""
import json
import sys
import argparse
from pathlib import Path


def convert(tests_file: str, graph_file: str, output_file: str) -> None:
    with open(tests_file, "r", encoding="utf-8") as f:
        tests = json.load(f)
    with open(graph_file, "r", encoding="utf-8") as f:
        graph = json.load(f)

    severity_to_level = {"S1": "error", "S2": "error", "S3": "warning", "S4": "note"}

    results = []
    rules = {}
    for test in tests.get("test_cases", []):
        cwe_raw = test.get("cwe", "CWE-Unknown")
        if isinstance(cwe_raw, list):
            cwe = cwe_raw[0] if cwe_raw else "CWE-Unknown"
        else:
            cwe = cwe_raw
        severity = test.get("severity", "S3")
        rule_id = cwe
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": test.get("cwe_name", cwe),
            }
        owasp_raw = test.get("owasp", "")
        if isinstance(owasp_raw, list):
            owasp_str = ", ".join(owasp_raw)
        else:
            owasp_str = owasp_raw
        surface = test.get("surface_id", test.get("attack_surface", ""))
        results.append({
            "ruleId": rule_id,
            "level": severity_to_level.get(severity, "warning"),
            "message": {"text": test.get("test_name", "")},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": f"requirement/{graph.get('requirement_id', 'unknown')}"
                    }
                },
                "logicalLocations": [{
                    "fullyQualifiedName": f"{surface}/attack_surface"
                }]
            }],
            "properties": {
                "threat_id": test.get("threat_id", ""),
                "stride_type": test.get("stride_type", ""),
                "dread_severity": severity,
                "owasp": owasp_str,
                "checklist_id": test.get("checklist_id", ""),
            }
        })

    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "secdesign",
                    "version": "1.1",
                    "informationUri": "https://github.com/secdesign"
                }
            },
            "results": results,
            "taxonomies": [{
                "name": "CWE",
                "rules": list(rules.values())
            }]
        }]
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sarif, f, indent=2, ensure_ascii=False)
    print(f"SARIF written to {output_file} ({len(results)} results)")


def main():
    parser = argparse.ArgumentParser(description="Convert security_tests.json to SARIF")
    parser.add_argument("--tests", required=True, help="Path to security_tests.json")
    parser.add_argument("--graph", required=True, help="Path to security_graph.json")
    parser.add_argument("--output", required=True, help="Output SARIF file path")
    args = parser.parse_args()
    convert(args.tests, args.graph, args.output)


if __name__ == "__main__":
    main()
