#!/usr/bin/env python3
"""
PR Quality Report Generator
Generates comprehensive quality reports for Pull Requests.

Usage:
    python pr_quality_report.py --pr <pr_number>
    python pr_quality_report.py (reads from environment)

This script aggregates results from various quality checks and generates
a comprehensive markdown report for the PR.
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class PRQualityReport:
    """Generate PR quality reports."""

    def __init__(self, pr_number: int):
        self.pr_number = pr_number
        self.report = {
            "pr_number": pr_number,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "checks": {},
            "summary": {},
            "recommendations": [],
            "metadata": {"generated_by": "PR Quality Report Generator", "version": "1.0.0"},
        }

    def add_check_result(
        self, check_name: str, passed: bool, details: Optional[Dict[str, Any]] = None, severity: str = "medium"
    ) -> None:
        """Add a check result to the report."""
        self.report["checks"][check_name] = {
            "passed": passed,
            "severity": severity,
            "details": details or {},
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    def add_metric(self, metric_name: str, value: Any, threshold: Optional[Any] = None, unit: str = "") -> None:
        """Add a metric to the report."""
        if "metrics" not in self.report:
            self.report["metrics"] = {}

        self.report["metrics"][metric_name] = {
            "value": value,
            "threshold": threshold,
            "unit": unit,
            "meets_threshold": threshold is None or value >= threshold,
        }

    def calculate_summary(self) -> None:
        """Calculate summary statistics."""
        total_checks = len(self.report["checks"])
        passed_checks = sum(1 for check in self.report["checks"].values() if check["passed"])
        failed_checks = total_checks - passed_checks

        # Count by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for check in self.report["checks"].values():
            if not check["passed"]:
                severity = check.get("severity", "medium")
                if severity in severity_counts:
                    severity_counts[severity] += 1

        # Calculate pass rate
        pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        self.report["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "pass_rate": pass_rate,
            "severity_counts": severity_counts,
            "overall_status": "PASS" if failed_checks == 0 else "FAIL",
            "has_critical_issues": severity_counts["critical"] > 0,
            "has_high_issues": severity_counts["high"] > 0,
        }

        # Generate recommendations based on failures
        self._generate_recommendations()

    def _generate_recommendations(self) -> None:
        """Generate recommendations based on failed checks."""
        recommendations = []

        for check_name, check in self.report["checks"].items():
            if not check["passed"]:
                severity = check.get("severity", "medium")
                details = check.get("details", {})

                # Generate recommendation based on check type
                if "code_quality" in check_name.lower():
                    score = details.get("score", 0)
                    recommendations.append(f"Improve code quality score from {score}/10 to at least 7.0")

                elif "security" in check_name.lower():
                    issues = details.get("issues_found", 0)
                    recommendations.append(f"Address {issues} security issue(s) found in the scan")

                elif "coverage" in check_name.lower():
                    coverage = details.get("coverage", 0)
                    recommendations.append(f"Increase test coverage from {coverage}% to at least 80%")

                elif "complexity" in check_name.lower():
                    f_count = details.get("f_grade_functions", 0)
                    recommendations.append(f"Refactor {f_count} F-grade (unmaintainable) function(s)")

                else:
                    recommendations.append(f"Fix issues in {check_name} check")

        # Add general recommendations
        if self.report["summary"]["failed_checks"] > 0:
            recommendations.append(f"Address {self.report['summary']['failed_checks']} failed check(s) before merging")

        if self.report["summary"]["has_critical_issues"]:
            recommendations.append("CRITICAL: Address critical issues immediately - do not merge")

        if self.report["summary"]["has_high_issues"]:
            recommendations.append("HIGH PRIORITY: Address high severity issues before merging")

        if not recommendations:
            recommendations.append("All checks passed - ready for merge")

        self.report["recommendations"] = recommendations

    def generate_markdown(self) -> str:
        """Generate markdown format report."""
        md = f"""# PR #{self.pr_number} Quality Report

**Generated:** {self.report['timestamp']}
**Overall Status:** **{self.report['summary']['overall_status']}**

## [STATS] Summary

| Metric | Value |
|--------|-------|
| Total Checks | {self.report['summary']['total_checks']} |
| Passed Checks | {self.report['summary']['passed_checks']} |
| Failed Checks | {self.report['summary']['failed_checks']} |
| Pass Rate | {self.report['summary']['pass_rate']:.1f}% |

### Severity Breakdown
- Critical Issues: {self.report['summary']['severity_counts']['critical']}
- High Issues: {self.report['summary']['severity_counts']['high']}
- Medium Issues: {self.report['summary']['severity_counts']['medium']}
- Low Issues: {self.report['summary']['severity_counts']['low']}

## [ANALYZE] Check Results

| Check | Status | Severity | Details |
|-------|--------|----------|---------|
"""

        for check_name, result in self.report["checks"].items():
            status = "[SUCCESS] PASS" if result["passed"] else "[ERROR] FAIL"
            severity = result.get("severity", "medium").upper()
            details = json.dumps(result.get("details", {}), ensure_ascii=False)
            details = details[:100] + "..." if len(details) > 100 else details

            md += f"| {check_name} | {status} | {severity} | {details} |\n"

        # Add metrics section if available
        if "metrics" in self.report and self.report["metrics"]:
            md += """
## [TRENDS] Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
"""

            for metric_name, metric in self.report["metrics"].items():
                value = metric["value"]
                threshold = metric.get("threshold", "N/A")
                unit = metric.get("unit", "")
                meets = "[SUCCESS]" if metric.get("meets_threshold", True) else "[ERROR]"

                if unit:
                    value_str = f"{value}{unit}"
                    if threshold != "N/A":
                        threshold = f"{threshold}{unit}"
                else:
                    value_str = str(value)

                md += f"| {metric_name} | {value_str} | {threshold} | {meets} |\n"

        md += f"""
## [IDEA] Recommendations

"""

        for rec in self.report["recommendations"]:
            md += f"- {rec}\n"

        md += f"""
## [LIST] Next Steps

"""

        if self.report["summary"]["overall_status"] == "PASS":
            md += """1. **Review the report** - Ensure all checks are acceptable
2. **Address any warnings** - Even if checks passed, review warnings
3. **Proceed with merge** - If all issues are addressed
4. **Monitor deployment** - Watch for any issues in production
"""
        else:
            md += """1. **Review failed checks** - Understand what needs to be fixed
2. **Address critical issues first** - Critical issues must be fixed
3. **Fix high/medium issues** - Based on priority and impact
4. **Re-run checks** - After fixes are applied
5. **Request re-review** - Once all checks pass
"""

        md += f"""
---

*Report generated by {self.report['metadata']['generated_by']} v{self.report['metadata']['version']}*
*For questions or issues, contact the DevOps team.*
"""

        return md

    def generate_json(self) -> str:
        """Generate JSON format report."""
        return json.dumps(self.report, indent=2, default=str)

    def save_report(self, filename: Optional[str] = None) -> str:
        """Save report to file."""
        if not filename:
            filename = f"pr_{self.pr_number}_quality_report.md"

        md_content = self.generate_markdown()

        with open(filename, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Also save JSON version
        json_filename = filename.replace(".md", ".json")
        with open(json_filename, "w", encoding="utf-8") as f:
            f.write(self.generate_json())

        print(f"[DOC] Report saved to: {filename}")
        print(f"[DOC] JSON version saved to: {json_filename}")

        return filename


def load_check_results(check_dir: str = "reports") -> Dict[str, Any]:
    """Load check results from report files."""
    results = {}

    if not os.path.exists(check_dir):
        print(f"[WARNING] Check directory not found: {check_dir}")
        return results

    # Look for common report files
    report_files = {
        "code_quality": ["pylint-report.json", "radon-complexity.json"],
        "security": ["bandit-report.json", "safety-report.json"],
        "coverage": ["coverage.xml", "coverage.json"],
        "tests": ["junit-report.xml", "test-results.json"],
    }

    for check_type, files in report_files.items():
        for file_pattern in files:
            file_path = os.path.join(check_dir, file_pattern)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        if file_path.endswith(".json"):
                            data = json.load(f)
                            results[f"{check_type}_{file_pattern}"] = data
                        elif file_path.endswith(".xml"):
                            # For XML, we'd parse it differently
                            results[f"{check_type}_{file_pattern}"] = {
                                "file": file_path,
                                "parsed": False,  # Would need XML parsing
                            }
                except (json.JSONDecodeError, IOError) as e:
                    print(f"[WARNING] Error loading {file_path}: {e}")

    return results


def analyze_check_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze check results to extract meaningful metrics."""
    analysis = {}

    for check_name, data in results.items():
        if "pylint" in check_name:
            # Analyze pylint results
            score = data.get("score", 0)
            analysis["pylint_score"] = {"value": score, "threshold": 7.0, "passed": score >= 7.0}

        elif "radon" in check_name:
            # Analyze radon complexity results
            f_count = 0
            total_functions = 0

            for file_data in data.values():
                if isinstance(file_data, list):
                    for func_data in file_data:
                        if isinstance(func_data, dict) and func_data.get("rank") == "F":
                            f_count += 1
                        total_functions += 1

            analysis["complexity"] = {"f_grade_functions": f_count, "total_functions": total_functions, "passed": f_count == 0}

        elif "bandit" in check_name:
            # Analyze bandit security results
            high_issues = 0
            medium_issues = 0

            for issue in data.get("results", []):
                severity = issue.get("issue_severity", "").lower()
                if severity == "high":
                    high_issues += 1
                elif severity == "medium":
                    medium_issues += 1

            analysis["security_scan"] = {
                "high_issues": high_issues,
                "medium_issues": medium_issues,
                "passed": high_issues == 0 and medium_issues <= 2,
            }

        elif "coverage" in check_name and check_name.endswith(".json"):
            # Analyze coverage results
            line_rate = data.get("line-rate", 0)
            branch_rate = data.get("branch-rate", 0)

            analysis["test_coverage"] = {
                "line_coverage": line_rate * 100,
                "branch_coverage": branch_rate * 100,
                "passed": line_rate >= 0.8,  # 80% threshold
            }

    return analysis


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate PR Quality Report")
    parser.add_argument("--pr", type=int, help="PR number")
    parser.add_argument("--check-dir", default="reports", help="Directory with check results")
    parser.add_argument("--output", help="Output file name")
    parser.add_argument("--simulate", action="store_true", help="Simulate with sample data")

    args = parser.parse_args()

    # Get PR number
    pr_number = args.pr or int(os.environ.get("PR_NUMBER", 0))

    if pr_number == 0:
        print("[ERROR] No PR number provided")
        print("Usage: python pr_quality_report.py --pr <number>")
        print("Or set PR_NUMBER environment variable")
        return 1

    print(f"[STATS] Generating quality report for PR #{pr_number}...")

    # Create report
    report = PRQualityReport(pr_number)

    if args.simulate:
        # Add simulated check results
        print("[TOOL] Using simulated data...")

        report.add_check_result("Code Quality (pylint)", True, {"score": 8.5, "issues": 12, "warnings": 5}, "medium")

        report.add_check_result(
            "Security Scan (bandit)", True, {"high_issues": 0, "medium_issues": 1, "low_issues": 3}, "high"
        )

        report.add_check_result(
            "Test Coverage", False, {"coverage": 75, "required": 80, "lines_covered": 1500, "lines_total": 2000}, "medium"
        )

        report.add_check_result(
            "Code Complexity", True, {"f_grade_functions": 0, "total_functions": 45, "maintainability_ratio": 0.85}, "medium"
        )

        report.add_check_result(
            "Dependency Vulnerabilities", True, {"vulnerabilities_found": 0, "packages_scanned": 42}, "high"
        )

        # Add metrics
        report.add_metric("Code Quality Score", 8.5, 7.0)
        report.add_metric("Test Coverage", 75, 80, "%")
        report.add_metric("Security Issues", 0, 0)
        report.add_metric("Build Time", 245, 300, "s")

    else:
        # Load and analyze real check results
        print(f"[FILE] Loading check results from: {args.check_dir}")
        check_results = load_check_results(args.check_dir)

        if not check_results:
            print("[WARNING] No check results found")
            print("Using minimal report...")

            # Add minimal checks
            report.add_check_result(
                "Check Results", False, {"message": "No check results found. Please run quality checks first."}, "medium"
            )
        else:
            print(f"[LIST] Found {len(check_results)} check result files")

            # Analyze results
            analysis = analyze_check_results(check_results)

            # Add checks based on analysis
            if "pylint_score" in analysis:
                score_data = analysis["pylint_score"]
                report.add_check_result(
                    "Code Quality",
                    score_data["passed"],
                    {"score": score_data["value"], "threshold": score_data["threshold"]},
                    "medium",
                )

            if "complexity" in analysis:
                comp_data = analysis["complexity"]
                report.add_check_result(
                    "Code Complexity",
                    comp_data["passed"],
                    {"f_grade_functions": comp_data["f_grade_functions"], "total_functions": comp_data["total_functions"]},
                    "medium",
                )

            if "security_scan" in analysis:
                sec_data = analysis["security_scan"]
                report.add_check_result(
                    "Security Scan",
                    sec_data["passed"],
                    {"high_issues": sec_data["high_issues"], "medium_issues": sec_data["medium_issues"]},
                    "high",
                )

            if "test_coverage" in analysis:
                cov_data = analysis["test_coverage"]
                report.add_check_result(
                    "Test Coverage",
                    cov_data["passed"],
                    {"coverage": cov_data["line_coverage"], "required": 80, "branch_coverage": cov_data["branch_coverage"]},
                    "medium",
                )

    # Calculate summary
    report.calculate_summary()

    # Save report
    output_file = args.output or f"pr_{pr_number}_quality_report.md"
    report.save_report(output_file)

    # Print summary
    print(f"\n[CELEBRATE] Report Generation Complete")
    print(f"PR: #{pr_number}")
    print(f"Status: {report.report['summary']['overall_status']}")
    print(f"Pass Rate: {report.report['summary']['pass_rate']:.1f}%")
    print(f"Failed Checks: {report.report['summary']['failed_checks']}")

    if report.report["summary"]["has_critical_issues"]:
        print("[WARNING]  CRITICAL ISSUES FOUND - DO NOT MERGE")

    # Output for GitHub Actions
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"report_file={output_file}\n")
            f.write(f"overall_status={report.report['summary']['overall_status']}\n")
            f.write(f"pass_rate={report.report['summary']['pass_rate']:.1f}\n")
            f.write(f"has_critical_issues={report.report['summary']['has_critical_issues']}\n")
            f.write(f"has_high_issues={report.report['summary']['has_high_issues']}\n")

    # Return appropriate exit code
    if report.report["summary"]["overall_status"] == "FAIL":
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
