#!/usr/bin/env python
"""
Comprehensive Quality Checks Script
Runs all quality checks and generates a consolidated report.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "returncode": -1}


def check_pylint():
    """Run pylint code quality check"""
    print("Running pylint code quality check...")

    cmd = "python -m pylint api/ command_system/ card_generator/ --exit-zero --output-format=json"
    result = run_command(cmd)

    if result["success"]:
        try:
            pylint_data = json.loads(result["stdout"])

            # Calculate score
            score = 0
            if pylint_data:
                # Pylint returns a list of messages, need to calculate score differently
                # For now, we'll run a separate command to get the score
                score_cmd = (
                    "python -m pylint api/ command_system/ card_generator/ --exit-zero | grep 'Your code has been rated at'"
                )
                score_result = run_command(score_cmd)
                if score_result["success"]:
                    import re

                    match = re.search(r"(\d+\.\d+)/10", score_result["stdout"])
                    if match:
                        score = float(match.group(1))

            return {
                "tool": "pylint",
                "score": score,
                "passed": score >= 7.0,
                "threshold": 7.0,
                "details": {
                    "total_messages": len(pylint_data),
                    "error_messages": len([m for m in pylint_data if m.get("type") == "error"]),
                    "warning_messages": len([m for m in pylint_data if m.get("type") == "warning"]),
                    "refactor_messages": len([m for m in pylint_data if m.get("type") == "refactor"]),
                    "convention_messages": len([m for m in pylint_data if m.get("type") == "convention"]),
                },
            }
        except json.JSONDecodeError:
            return {"tool": "pylint", "score": 0, "passed": False, "threshold": 7.0, "error": "Failed to parse pylint output"}
    else:
        return {
            "tool": "pylint",
            "score": 0,
            "passed": False,
            "threshold": 7.0,
            "error": result.get("error", "Command failed"),
        }


def check_bandit():
    """Run bandit security check"""
    print("Running bandit security check...")

    cmd = "bandit -r api/ command_system/ card_generator/ -f json"
    result = run_command(cmd)

    if result["success"] or result["returncode"] in [0, 1]:  # Bandit returns 1 when issues found
        try:
            bandit_data = json.loads(result["stdout"])

            # Count issues by severity
            metrics = bandit_data.get("metrics", {})
            totals = metrics.get("_totals", {}).get("SEVERITY", {})

            high_issues = totals.get("HIGH", 0)
            medium_issues = totals.get("MEDIUM", 0)
            low_issues = totals.get("LOW", 0)

            return {
                "tool": "bandit",
                "high_issues": high_issues,
                "medium_issues": medium_issues,
                "low_issues": low_issues,
                "passed": high_issues == 0,
                "threshold": 0,  # No high severity issues allowed
                "details": {
                    "total_issues": high_issues + medium_issues + low_issues,
                    "files_scanned": len(bandit_data.get("results", [])),
                    "confidence_levels": metrics.get("_totals", {}).get("CONFIDENCE", {}),
                },
            }
        except json.JSONDecodeError:
            return {
                "tool": "bandit",
                "high_issues": 999,
                "passed": False,
                "threshold": 0,
                "error": "Failed to parse bandit output",
            }
    else:
        return {
            "tool": "bandit",
            "high_issues": 999,
            "passed": False,
            "threshold": 0,
            "error": result.get("error", "Command failed"),
        }


def check_radon():
    """Run radon complexity check"""
    print("Running radon complexity check...")

    cmd = "python -m radon cc api/ command_system/ card_generator/ -s -j"
    result = run_command(cmd)

    if result["success"]:
        try:
            radon_data = json.loads(result["stdout"])

            # Count complexity grades
            a_count = b_count = c_count = d_count = e_count = f_count = 0

            for file_data in radon_data.values():
                for item in file_data:
                    grade = item.get("grade", "")
                    if grade == "A":
                        a_count += 1
                    elif grade == "B":
                        b_count += 1
                    elif grade == "C":
                        c_count += 1
                    elif grade == "D":
                        d_count += 1
                    elif grade == "E":
                        e_count += 1
                    elif grade == "F":
                        f_count += 1

            total = a_count + b_count + c_count + d_count + e_count + f_count
            maintainable = a_count + b_count
            maintainability_ratio = maintainable / total if total > 0 else 1.0

            return {
                "tool": "radon",
                "maintainability_ratio": maintainability_ratio,
                "unmaintainable_functions": f_count,
                "passed": f_count == 0 and maintainability_ratio >= 0.7,
                "threshold": "F=0, ratio>=0.7",
                "details": {
                    "total_functions": total,
                    "grade_a": a_count,
                    "grade_b": b_count,
                    "grade_c": c_count,
                    "grade_d": d_count,
                    "grade_e": e_count,
                    "grade_f": f_count,
                },
            }
        except json.JSONDecodeError:
            return {
                "tool": "radon",
                "maintainability_ratio": 0,
                "unmaintainable_functions": 999,
                "passed": False,
                "threshold": "F=0, ratio>=0.7",
                "error": "Failed to parse radon output",
            }
    else:
        return {
            "tool": "radon",
            "maintainability_ratio": 0,
            "unmaintainable_functions": 999,
            "passed": False,
            "threshold": "F=0, ratio>=0.7",
            "error": result.get("error", "Command failed"),
        }


def check_test_coverage():
    """Run test coverage check"""
    print("Running test coverage check...")

    cmd = "python -m pytest tests/ -v --cov=api --cov=command_system --cov=card_generator --cov-report=json"
    result = run_command(cmd)

    if result["success"]:
        try:
            # Find coverage.json file
            coverage_file = Path("coverage.json")
            if coverage_file.exists():
                with open(coverage_file, "r") as f:
                    coverage_data = json.load(f)

                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)

                return {
                    "tool": "pytest-coverage",
                    "coverage_percent": total_coverage,
                    "passed": total_coverage >= 80.0,
                    "threshold": 80.0,
                    "details": {
                        "total_statements": coverage_data.get("totals", {}).get("covered_statements", 0),
                        "missing_statements": coverage_data.get("totals", {}).get("missing_statements", 0),
                        "excluded_statements": coverage_data.get("totals", {}).get("excluded_statements", 0),
                    },
                }
            else:
                return {
                    "tool": "pytest-coverage",
                    "coverage_percent": 0,
                    "passed": False,
                    "threshold": 80.0,
                    "error": "Coverage file not found",
                }
        except Exception as e:
            return {"tool": "pytest-coverage", "coverage_percent": 0, "passed": False, "threshold": 80.0, "error": str(e)}
    else:
        return {
            "tool": "pytest-coverage",
            "coverage_percent": 0,
            "passed": False,
            "threshold": 80.0,
            "error": "Test execution failed",
        }


def check_design_principles():
    """Run design principles check"""
    print("Running design principles check...")

    cmd = "python scripts/check_design_principles.py --output /tmp/design_principles.json"
    result = run_command(cmd)

    if result["success"]:
        try:
            design_file = Path("/tmp/design_principles.json")
            if design_file.exists():
                with open(design_file, "r") as f:
                    design_data = json.load(f)

                total_score = design_data.get("total_score", 0)

                return {
                    "tool": "design-principles",
                    "total_score": total_score,
                    "passed": total_score >= 60,
                    "threshold": 60,
                    "details": {
                        "srp_score": design_data.get("srp_score", 0),
                        "ocp_score": design_data.get("ocp_score", 0),
                        "lsp_score": design_data.get("lsp_score", 0),
                        "isp_score": design_data.get("isp_score", 0),
                        "dip_score": design_data.get("dip_score", 0),
                    },
                }
            else:
                return {
                    "tool": "design-principles",
                    "total_score": 0,
                    "passed": False,
                    "threshold": 60,
                    "error": "Design principles file not found",
                }
        except Exception as e:
            return {"tool": "design-principles", "total_score": 0, "passed": False, "threshold": 60, "error": str(e)}
    else:
        return {
            "tool": "design-principles",
            "total_score": 0,
            "passed": False,
            "threshold": 60,
            "error": "Design principles check failed",
        }


def generate_report(checks):
    """Generate consolidated quality report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": checks,
        "summary": {
            "total_checks": len(checks),
            "passed_checks": sum(1 for c in checks if c.get("passed", False)),
            "failed_checks": sum(1 for c in checks if not c.get("passed", False)),
            "overall_status": "PASS" if all(c.get("passed", False) for c in checks) else "FAIL",
        },
    }

    return report


def print_summary(report):
    """Print human-readable summary"""
    print("\n" + "=" * 60)
    print("QUALITY CHECKS SUMMARY")
    print("=" * 60)

    checks = report["checks"]
    summary = report["summary"]

    print(f"\nTotal checks: {summary['total_checks']}")
    print(f"Passed: {summary['passed_checks']}")
    print(f"Failed: {summary['failed_checks']}")
    print(f"Overall status: {summary['overall_status']}")

    print("\nDetailed Results:")
    print("-" * 40)

    for check in checks:
        tool = check["tool"]
        passed = check.get("passed", False)
        status = "PASS" if passed else "FAIL"

        print(f"\n{tool}: {status}")

        # Tool-specific details
        if tool == "pylint":
            score = check.get("score", 0)
            threshold = check.get("threshold", 0)
            print(f"  Score: {score}/10 (threshold: {threshold})")

        elif tool == "bandit":
            high_issues = check.get("high_issues", 0)
            threshold = check.get("threshold", 0)
            print(f"  High severity issues: {high_issues} (threshold: {threshold})")

        elif tool == "radon":
            ratio = check.get("maintainability_ratio", 0)
            f_count = check.get("unmaintainable_functions", 0)
            print(f"  Maintainability ratio: {ratio:.2%}")
            print(f"  Unmaintainable functions: {f_count}")

        elif tool == "pytest-coverage":
            coverage = check.get("coverage_percent", 0)
            threshold = check.get("threshold", 0)
            print(f"  Test coverage: {coverage:.1f}% (threshold: {threshold}%)")

        elif tool == "design-principles":
            score = check.get("total_score", 0)
            threshold = check.get("threshold", 0)
            print(f"  SOLID principles score: {score}/100 (threshold: {threshold})")

        # Print error if any
        if "error" in check:
            print(f"  Error: {check['error']}")

    print("\n" + "=" * 60)
    print(f"OVERALL: {summary['overall_status']}")
    print("=" * 60)


def main():
    """Main function"""
    print("Starting comprehensive quality checks...")

    # Run all checks
    checks = [check_pylint(), check_bandit(), check_radon(), check_test_coverage(), check_design_principles()]

    # Generate report
    report = generate_report(checks)

    # Print summary
    print_summary(report)

    # Save report to file
    output_file = "quality-checks-report.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: {output_file}")

    # Exit with appropriate code
    if report["summary"]["overall_status"] == "PASS":
        print("\n[OK] All quality checks passed!")
        return 0
    else:
        print("\n[FAIL] Some quality checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
