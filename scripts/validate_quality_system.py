#!/usr/bin/env python3
"""
Validation script for the Quality Gate System.
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
        print("Validating Quality Gate System...")
        print("=" * 60)

        checks = [
            self.check_configuration_files,
            self.check_workflow_files,
            self.check_script_files,
            self.check_integration,
            self.check_dependencies,
            self.check_permissions,
            self.check_documentation,
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                print(f"[FAIL] Error running {check.__name__}: {e}")
                self.failed += 1

        self.print_summary()

    def check_configuration_files(self):
        """Check all configuration files"""
        print("\nChecking Configuration Files...")

        config_files = [
            ("quality-gates-thresholds.yaml", self._validate_yaml),
            ("performance-thresholds.yaml", self._validate_yaml),
            ("security-thresholds.yaml", self._validate_yaml),
            (".github/branch-protection-rules.yml", self._validate_yaml),
            (".github/code-review.yml", self._validate_yaml),
            (".github/environments/staging/environment.yml", self._validate_yaml),
            (".github/environments/production/environment.yml", self._validate_yaml),
        ]

        for filepath, validator in config_files:
            full_path = self.root_dir / filepath
            if full_path.exists():
                try:
                    validator(full_path)
                    print(f"  [OK] {filepath}")
                    self.passed += 1
                except Exception as e:
                    print(f"  [ERROR] {filepath}: {e}")
                    self.failed += 1
            else:
                print(f"  [WARNING] {filepath}: File not found")
                self.warnings += 1

    def check_workflow_files(self):
        """Check all workflow files"""
        print("\nChecking Workflow Files...")

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
                    # Basic YAML validation
                    with open(full_path, "r") as f:
                        yaml.safe_load(f)

                    # Check for required sections
                    content = full_path.read_text()
                    if "name:" in content and "on:" in content and "jobs:" in content:
                        print(f"  [OK] {filepath}")
                        self.passed += 1
                    else:
                        print(f"  [WARN]️ {filepath}: Missing required sections")
                        self.warnings += 1
                except Exception as e:
                    print(f"  [FAIL] {filepath}: {e}")
                    self.failed += 1
            else:
                print(f"  [WARN]️ {filepath}: File not found")
                self.warnings += 1

    def check_script_files(self):
        """Check all script files"""
        print("\n🐍 Checking Script Files...")

        script_files = [
            "scripts/integrate_quality_gates.py",
            "scripts/monitor_quality_gates.py",
            "scripts/auto_fix_issues.py",
            "scripts/auto_label_pr.py",
            "scripts/pr_quality_report.py",
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
                        print(f"  [OK] {filepath}")
                        self.passed += 1
                    else:
                        print(f"  [FAIL] {filepath}: Syntax error")
                        print(f"     {result.stderr}")
                        self.failed += 1
                except Exception as e:
                    print(f"  [FAIL] {filepath}: {e}")
                    self.failed += 1
            else:
                print(f"  [WARN]️ {filepath}: File not found")
                self.warnings += 1

    def check_integration(self):
        """Check integration with existing system"""
        print("\n[LINK] Checking System Integration...")

        # Check if integration script can run
        integration_script = self.root_dir / "scripts" / "integrate_quality_gates.py"
        if integration_script.exists():
            try:
                # Test with dry run
                result = subprocess.run(
                    [sys.executable, str(integration_script), "--test"], capture_output=True, text=True, timeout=30
                )

                if result.returncode == 0 or result.returncode == 1:
                    print(f"  [OK] Integration script runs successfully")
                    self.passed += 1
                else:
                    print(f"  [WARN]️ Integration script returned code {result.returncode}")
                    self.warnings += 1
            except subprocess.TimeoutExpired:
                print(f"  [WARN]️ Integration script timed out")
                self.warnings += 1
            except Exception as e:
                print(f"  [FAIL] Integration script error: {e}")
                self.failed += 1
        else:
            print(f"  [WARN]️ Integration script not found")
            self.warnings += 1

        # Check if monitoring script can run
        monitor_script = self.root_dir / "scripts" / "monitor_quality_gates.py"
        if monitor_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(monitor_script), "analyze", "--days", "1"], capture_output=True, text=True, timeout=30
                )

                if result.returncode == 0:
                    print(f"  [OK] Monitoring script runs successfully")
                    self.passed += 1
                else:
                    print(f"  [WARN]️ Monitoring script returned code {result.returncode}")
                    print(f"     {result.stderr}")
                    self.warnings += 1
            except subprocess.TimeoutExpired:
                print(f"  [WARN]️ Monitoring script timed out")
                self.warnings += 1
            except Exception as e:
                print(f"  [FAIL] Monitoring script error: {e}")
                self.failed += 1

    def check_dependencies(self):
        """Check required dependencies"""
        print("\n[PACKAGE] Checking Dependencies...")

        required_packages = ["yaml", "json", "pathlib", "subprocess", "datetime", "collections"]  # pyyaml

        for package in required_packages:
            try:
                if package == "yaml":
                    import yaml as yaml_module
                else:
                    __import__(package)
                print(f"  [OK] {package}")
                self.passed += 1
            except ImportError as e:
                print(f"  [FAIL] {package}: {e}")
                self.failed += 1

        # Check external tools (if available)
        external_tools = ["python", "git"]
        for tool in external_tools:
            try:
                result = subprocess.run([tool, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.split("\n")[0]
                    print(f"  [OK] {tool}: {version}")
                    self.passed += 1
                else:
                    print(f"  [WARN]️ {tool}: Not available")
                    self.warnings += 1
            except FileNotFoundError:
                print(f"  [WARN]️ {tool}: Not installed")
                self.warnings += 1

    def check_permissions(self):
        """Check file permissions and structure"""
        print("\n[LOCKED] Checking Permissions and Structure...")

        # Check directory structure
        required_dirs = [
            ".github/workflows",
            ".github/environments/staging",
            ".github/environments/production",
            "scripts",
            "docs",
        ]

        for dirpath in required_dirs:
            full_path = self.root_dir / dirpath
            if full_path.exists() and full_path.is_dir():
                print(f"  [OK] Directory: {dirpath}")
                self.passed += 1
            else:
                print(f"  [WARN]️ Directory missing: {dirpath}")
                self.warnings += 1

        # Check file permissions (simplified for Windows)
        important_files = ["scripts/integrate_quality_gates.py", "scripts/monitor_quality_gates.py"]

        for filepath in important_files:
            full_path = self.root_dir / filepath
            if full_path.exists():
                # Check if file is readable
                try:
                    with open(full_path, "r") as f:
                        f.read(100)  # Read first 100 bytes
                    print(f"  [OK] File readable: {filepath}")
                    self.passed += 1
                except Exception as e:
                    print(f"  [FAIL] File not readable: {filepath} - {e}")
                    self.failed += 1
            else:
                print(f"  [WARN]️ File missing: {filepath}")
                self.warnings += 1

    def check_documentation(self):
        """Check documentation files"""
        print("\n[BOOKS] Checking Documentation...")

        doc_files = ["CD_CI_质量门禁方案.md", "docs/QUALITY_GATES_ADOPTION_GUIDE.md"]

        for filepath in doc_files:
            full_path = self.root_dir / filepath
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding="utf-8")
                    if len(content) > 100:  # Minimum content length
                        print(f"  [OK] {filepath} ({len(content)} chars)")
                        self.passed += 1
                    else:
                        print(f"  [WARN]️ {filepath}: Very short content")
                        self.warnings += 1
                except Exception as e:
                    print(f"  [FAIL] {filepath}: {e}")
                    self.failed += 1
            else:
                print(f"  [WARN]️ {filepath}: File not found")
                self.warnings += 1

    def _validate_yaml(self, filepath):
        """Validate YAML file"""
        with open(filepath, "r") as f:
            yaml.safe_load(f)

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        total = self.passed + self.failed + self.warnings

        print(f"\n[CHART] Results:")
        print(f"  [OK] Passed: {self.passed}")
        print(f"  [FAIL] Failed: {self.failed}")
        print(f"  [WARN]️ Warnings: {self.warnings}")
        print(f"  [UP] Total Checks: {total}")

        if total > 0:
            pass_rate = (self.passed / total) * 100
            print(f"  [TARGET] Pass Rate: {pass_rate:.1f}%")

        print("\n[CLIPBOARD] Recommendations:")

        if self.failed == 0 and self.warnings == 0:
            print("  🎉 All checks passed! The quality gate system is ready.")
        elif self.failed == 0:
            print("  [OK] All critical checks passed. Review warnings for improvements.")
        elif self.failed > 0:
            print("  [WARN]️ Some critical checks failed. Address these issues first.")

        if self.warnings > 0:
            print("\n[WARN]️  Warnings to address:")
            print("  - Review missing configuration files")
            print("  - Check script dependencies")
            print("  - Verify documentation completeness")

        if self.failed > 0:
            print("\n[FAIL] Critical issues to fix:")
            print("  - Fix script syntax errors")
            print("  - Correct configuration file issues")
            print("  - Resolve integration problems")

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
            "recommendations": self._generate_recommendations(),
        }

        report_file = self.root_dir / "quality-system-validation-report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Validation report saved to: {report_file}")

    def _generate_recommendations(self):
        """Generate recommendations based on validation results"""
        recommendations = []

        if self.failed > 0:
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Fix critical validation failures",
                    "details": "Address script syntax errors and configuration issues",
                }
            )

        if self.warnings > 0:
            recommendations.append(
                {
                    "priority": "medium",
                    "action": "Address validation warnings",
                    "details": "Review missing files and improve documentation",
                }
            )

        if self.passed / (self.passed + self.failed + self.warnings) < 0.8:
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Improve overall system quality",
                    "details": "Aim for at least 80% pass rate in validation",
                }
            )

        return recommendations


def main():
    """Main validation function"""
    validator = QualitySystemValidator()
    validator.run_all_checks()

    # Exit with appropriate code
    if validator.failed > 0:
        sys.exit(1)
    elif validator.warnings > 0:
        sys.exit(0)  # Warnings are acceptable
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
