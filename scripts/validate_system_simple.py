#!/usr/bin/env python3
"""
Simple validation script for the Quality Gate System.
Tests all components to ensure they work correctly.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml


class QualitySystemValidator:
    """Validate all components of the quality gate system"""

    def __init__(self):
        self.root_dir = Path(".")
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def run_all_checks(self):
        """Run all validation checks"""
        print("=" * 60)
        print("VALIDATING QUALITY GATE SYSTEM")
        print("=" * 60)

        checks = [
            self.check_configuration_files,
            self.check_workflow_files,
            self.check_script_files,
            self.check_dependencies,
            self.check_documentation,
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                print(f"ERROR running {check.__name__}: {e}")
                self.failed += 1

        self.print_summary()

    def check_configuration_files(self):
        """Check all configuration files"""
        print("\n[1/5] Checking Configuration Files...")

        config_files = [
            "quality-gates-thresholds.yaml",
            "performance-thresholds.yaml",
            "security-thresholds.yaml",
            ".github/branch-protection-rules.yml",
            ".github/code-review.yml",
            ".github/environments/staging/environment.yml",
            ".github/environments/production/environment.yml",
        ]

        for filepath in config_files:
            full_path = self.root_dir / filepath
            if full_path.exists():
                try:
                    with open(full_path, "r") as f:
                        yaml.safe_load(f)
                    print(f"  OK: {filepath}")
                    self.passed += 1
                except Exception as e:
                    print(f"  ERROR: {filepath}: {e}")
                    self.failed += 1
            else:
                print(f"  WARNING: {filepath}: File not found")
                self.warnings += 1

    def check_workflow_files(self):
        """Check all workflow files"""
        print("\n[2/5] Checking Workflow Files...")

        workflow_files = [
            ".github/workflows/pr-quality-gates.yml",
            ".github/workflows/auto-fix.yml",
            ".github/workflows/auto-assign-reviewers.yml",
            ".github/workflows/emergency-fix.yml",
        ]

        for filepath in workflow_files:
            full_path = self.root_dir / filepath
            if full_path.exists():
                try:
                    with open(full_path, "r") as f:
                        yaml.safe_load(f)
                    print(f"  OK: {filepath}")
                    self.passed += 1
                except Exception as e:
                    print(f"  ERROR: {filepath}: {e}")
                    self.failed += 1
            else:
                print(f"  WARNING: {filepath}: File not found")
                self.warnings += 1

    def check_script_files(self):
        """Check all script files"""
        print("\n[3/5] Checking Script Files...")

        script_files = [
            "scripts/integrate_quality_gates.py",
            "scripts/monitor_quality_gates.py",
            "scripts/auto_fix_issues.py",
            "scripts/auto_label_pr.py",
            "scripts/pr_quality_report.py",
            "scripts/validate_system_simple.py",
        ]

        for filepath in script_files:
            full_path = self.root_dir / filepath
            if full_path.exists():
                try:
                    # Check Python syntax
                    result = subprocess.run(
                        [sys.executable, "-m", "py_compile", str(full_path)], capture_output=True, text=True
                    )

                    if result.returncode == 0:
                        print(f"  OK: {filepath}")
                        self.passed += 1
                    else:
                        print(f"  ERROR: {filepath}: Syntax error")
                        if result.stderr:
                            print(f"         {result.stderr[:100]}...")
                        self.failed += 1
                except Exception as e:
                    print(f"  ERROR: {filepath}: {e}")
                    self.failed += 1
            else:
                print(f"  WARNING: {filepath}: File not found")
                self.warnings += 1

    def check_dependencies(self):
        """Check required dependencies"""
        print("\n[4/5] Checking Dependencies...")

        required_packages = ["yaml", "json", "pathlib", "subprocess", "datetime", "collections"]  # pyyaml

        for package in required_packages:
            try:
                if package == "yaml":
                    import yaml as yaml_module
                else:
                    __import__(package)
                print(f"  OK: {package}")
                self.passed += 1
            except ImportError as e:
                print(f"  ERROR: {package}: {e}")
                self.failed += 1

        # Check Python version
        print(f"  INFO: Python {sys.version.split()[0]}")

    def check_documentation(self):
        """Check documentation files"""
        print("\n[5/5] Checking Documentation...")

        doc_files = ["CD_CI_质量门禁方案.md", "docs/QUALITY_GATES_ADOPTION_GUIDE.md"]

        for filepath in doc_files:
            full_path = self.root_dir / filepath
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding="utf-8", errors="ignore")
                    if len(content) > 100:  # Minimum content length
                        print(f"  OK: {filepath} ({len(content)} chars)")
                        self.passed += 1
                    else:
                        print(f"  WARNING: {filepath}: Very short content")
                        self.warnings += 1
                except Exception as e:
                    print(f"  ERROR: {filepath}: {e}")
                    self.failed += 1
            else:
                print(f"  WARNING: {filepath}: File not found")
                self.warnings += 1

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        total = self.passed + self.failed + self.warnings

        print(f"\nResults:")
        print(f"  Passed: {self.passed}")
        print(f"  Failed: {self.failed}")
        print(f"  Warnings: {self.warnings}")
        print(f"  Total Checks: {total}")

        if total > 0:
            pass_rate = (self.passed / total) * 100
            print(f"  Pass Rate: {pass_rate:.1f}%")

        print("\nStatus: ", end="")
        if self.failed == 0 and self.warnings == 0:
            print("ALL CHECKS PASSED - System is ready!")
        elif self.failed == 0:
            print("All critical checks passed. Review warnings.")
        else:
            print(f"{self.failed} critical checks failed. Fix these first.")

        # Generate validation report
        report = {
            "timestamp": os.path.getmtime(__file__) if os.path.exists(__file__) else None,
            "summary": {
                "passed": self.passed,
                "failed": self.failed,
                "warnings": self.warnings,
                "total": total,
                "pass_rate": pass_rate if total > 0 else 0,
            },
        }

        report_file = self.root_dir / "quality-system-validation-report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {report_file}")


def main():
    """Main validation function"""
    validator = QualitySystemValidator()
    validator.run_all_checks()

    # Exit with appropriate code
    if validator.failed > 0:
        print("\n[EXIT] Validation failed with errors")
        sys.exit(1)
    elif validator.warnings > 0:
        print("\n[EXIT] Validation completed with warnings")
        sys.exit(0)
    else:
        print("\n[EXIT] Validation successful!")
        sys.exit(0)


if __name__ == "__main__":
    main()
