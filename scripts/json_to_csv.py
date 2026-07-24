#!/usr/bin/env python3
"""Convert security_tests.json to CSV (UTF-8 with BOM)."""
import json
import csv
import sys
import argparse


def convert(tests_file: str, output_file: str) -> None:
    with open(tests_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    headers = [
        "用例编号", "测试名称", "关联威胁", "攻击面", "CWE", "OWASP",
        "严重度", "攻击者角色", "前置条件", "攻击步骤", "预期结果", "验证方法"
    ]

    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for test in data.get("test_cases", []):
            cwe_raw = test.get("cwe", "")
            cwe_str = ", ".join(cwe_raw) if isinstance(cwe_raw, list) else cwe_raw
            owasp_raw = test.get("owasp", "")
            owasp_str = ", ".join(owasp_raw) if isinstance(owasp_raw, list) else owasp_raw
            writer.writerow([
                test.get("id", ""),
                test.get("test_name", ""),
                test.get("threat_id", ""),
                test.get("surface_id", test.get("attack_surface", "")),
                cwe_str,
                owasp_str,
                test.get("severity", ""),
                test.get("attacker_role", ""),
                "; ".join(test.get("preconditions", [])),
                " | ".join(test.get("attack_steps", [])),
                "; ".join(test.get("expected_result", test.get("expected_results", []))),
                "; ".join(test.get("verification", [])),
            ])

    print(f"CSV written to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Convert security_tests.json to CSV")
    parser.add_argument("--tests", required=True, help="Path to security_tests.json")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    args = parser.parse_args()
    convert(args.tests, args.output)


if __name__ == "__main__":
    main()
