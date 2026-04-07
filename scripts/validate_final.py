#!/usr/bin/env python3
"""
Final validation script for the Quality Gate System.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml


def check_file_exists(filepath):
    """Check if file exists and is readable"""
    full_path = Path(filepath)
    if not full_path.exists():
        return False, f"File not found: {filepath}"

    try:
        # Try to read with different encodings
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(full_path, "r", encoding=encoding) as f:
                    f.read(100)  # Read first 100 bytes
                return True, f"File readable: {filepath}"
            except UnicodeDecodeError:
                continue
        return False, f"Cannot read file with any encoding: {filepath}"
    except Exception as e:
        return False, f"Error reading file: {filepath} - {e}"


def check_yaml_file(filepath):
    """Check if YAML file is valid"""
    full_path = Path(filepath)
    if not full_path.exists():
        return False, f"File not found: {filepath}"

    try:
        # Try multiple encodings
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        content = None

        for encoding in encodings:
            try:
                with open(full_path, "r", encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if not content:
            return False, f"Cannot read YAML file: {filepath}"

        # Parse YAML
        yaml.safe_load(content)
        return True, f"Valid YAML: {filepath}"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {filepath} - {e}"
    except Exception as e:
        return False, f"Error: {filepath} - {e}"


def check_python_script(filepath):
    """Check if Python script has valid syntax"""
    full_path = Path(filepath)
    if not full_path.exists():
        return False, f"File not found: {filepath}"

    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(full_path)], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            return True, f"Valid Python: {filepath}"
        else:
            error_msg = result.stderr[:100] if result.stderr else "Unknown error"
            return False, f"Invalid Python: {filepath} - {error_msg}"
    except subprocess.TimeoutExpired:
        return False, f"Timeout checking Python: {filepath}"
    except Exception as e:
        return False, f"Error checking Python: {filepath} - {e}"


def main():
    """Main validation function"""
    print("=" * 70)
    print("FINAL VALIDATION - QUALITY GATE SYSTEM")
    print("=" * 70)

    passed = 0
    failed = 0
    warnings = 0

    # Configuration files
    print("\n[1] Configuration Files:")
    config_files = [
        "quality-gates-thresholds.yaml",
        "performance-thresholds.yaml",
        "security-thresholds.yaml",
        ".github/branch-protection-rules.yml",
        ".github/code-review.yml",
    ]

    for filepath in config_files:
        success, message = check_yaml_file(filepath)
        if success:
            print(f"  [OK] {message}")
            passed += 1
        else:
            print(f"  [ERROR] {message}")
            failed += 1

    # Workflow files
    print("\n[2] Workflow Files:")
    workflow_files = [
        ".github/workflows/pr-quality-gates.yml",
        ".github/workflows/auto-fix.yml",
        ".github/workflows/auto-assign-reviewers.yml",
        ".github/workflows/emergency-fix.yml",
    ]

    for filepath in workflow_files:
        success, message = check_yaml_file(filepath)
        if success:
            print(f"  [OK] {message}")
            passed += 1
        else:
            print(f"  [ERROR] {message}")
            failed += 1

    # Script files
    print("\n[3] Script Files:")
    script_files = [
        "scripts/integrate_quality_gates.py",
        "scripts/monitor_quality_gates.py",
        "scripts/auto_fix_issues.py",
        "scripts/auto_label_pr.py",
        "scripts/pr_quality_report.py",
    ]

    for filepath in script_files:
        success, message = check_python_script(filepath)
        if success:
            print(f"  [OK] {message}")
            passed += 1
        else:
            print(f"  [ERROR] {message}")
            failed += 1

    # Documentation files
    print("\n[4] Documentation Files:")
    doc_files = ["CD_CI_质量门禁方案.md", "docs/QUALITY_GATES_ADOPTION_GUIDE.md"]

    for filepath in doc_files:
        success, message = check_file_exists(filepath)
        if success:
            print(f"  [OK] {message}")
            passed += 1
        else:
            print(f"  [ERROR] {message}")
            failed += 1

    # Directory structure
    print("\n[5] Directory Structure:")
    required_dirs = [".github/workflows", ".github/environments/staging", ".github/environments/production", "scripts", "docs"]

    for dirpath in required_dirs:
        full_path = Path(dirpath)
        if full_path.exists() and full_path.is_dir():
            print(f"  [OK] Directory exists: {dirpath}")
            passed += 1
        else:
            print(f"  [WARNING] Directory missing: {dirpath}")
            warnings += 1

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    total = passed + failed + warnings

    print(f"\nResults:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Warnings: {warnings}")
    print(f"  Total Checks: {total}")

    if total > 0:
        pass_rate = (passed / total) * 100
        print(f"  Pass Rate: {pass_rate:.1f}%")

    print(f"\nPython Version: {sys.version.split()[0]}")

    # Generate report
    report = {
        "validation": {
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "total": total,
            "pass_rate": pass_rate if total > 0 else 0,
        },
        "system": {"python_version": sys.version, "platform": sys.platform},
        "files_checked": {
            "configurations": config_files,
            "workflows": workflow_files,
            "scripts": script_files,
            "documentation": doc_files,
        },
    }

    with open("validation-report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: validation-report.json")

    # Final status
    if failed == 0:
        print("\n[SUCCESS] VALIDATION SUCCESSFUL!")
        print("The Quality Gate System is ready for use.")
        return 0
    else:
        print(f"\n[WARNING] VALIDATION COMPLETED WITH {failed} FAILURES")
        print("Please fix the reported issues before using the system.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
