#!/usr/bin/env python3
"""
Auto-fix script for common code issues
This script is used by the auto-fix workflow to automatically fix:
- Code formatting (black)
- Import sorting (isort)
- Lint issues (autopep8)
- Security issue detection

Usage:
    python auto_fix_issues.py [--scope SCOPE] [--dry-run]

Options:
    --scope SCOPE    Scope of fixes: all, formatting, linting, imports, security
    --dry-run        Dry run (no changes)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def run_command(cmd: str, cwd: str = None) -> Dict[str, Any]:
    """Run a command and return result."""
    try:
        # Use bytes capture first, then decode with error handling
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=False)  # Capture as bytes

        # Decode output with error handling
        def decode_with_fallback(data: bytes) -> str:
            if not data:
                return ""
            try:
                return data.decode("utf-8")
            except UnicodeDecodeError:
                # Fallback to latin-1 which can decode any byte
                return data.decode("latin-1", errors="replace")

        stdout = decode_with_fallback(result.stdout)
        stderr = decode_with_fallback(result.stderr)

        return {"success": result.returncode == 0, "returncode": result.returncode, "stdout": stdout, "stderr": stderr}
    except Exception as e:
        return {"success": False, "error": str(e), "returncode": -1}


def check_tool_available(tool_name: str) -> bool:
    """Check if a command-line tool is available."""
    # Try different methods to check tool availability
    commands = []

    if os.name == "nt":  # Windows
        commands = [f"where {tool_name}", f"{tool_name} --version", f"python -m {tool_name} --version"]
    else:  # Linux/Mac
        commands = [f"which {tool_name}", f"{tool_name} --version", f"python -m {tool_name} --version"]

    for cmd in commands:
        result = run_command(cmd)
        if result["success"] and result["returncode"] == 0:
            return True

    return False


def fix_code_formatting(dry_run: bool = False) -> List[str]:
    """Fix code formatting using black and isort."""
    print("[FIX] Fixing code formatting...")

    fixes_applied = []

    # Check if black is available
    if not check_tool_available("black"):
        print("  [WARNING] 'black' tool not found. Skipping code formatting.")
        print("  [INFO] Install with: pip install black")
        return fixes_applied

    # Format code with black
    if dry_run:
        cmd = "python -m black --check --diff ."
        print("  Checking code formatting with black...")
    else:
        cmd = "python -m black ."
        print("  Formatting code with black...")

    result = run_command(cmd)
    if result["success"]:
        if dry_run:
            if result["stdout"]:
                print("  [WARNING] Formatting issues found (dry run)")
            else:
                print("  [OK] Code formatting check passed")
        else:
            print("  [OK] Code formatted with black")
            fixes_applied.append("black_formatting")
    else:
        error_msg = result.get("stderr", "Unknown error")
        if "is not recognized" in error_msg or "command not found" in error_msg:
            print(f"  [WARNING] 'black' command failed. Make sure it's installed: pip install black")
        else:
            print(f"  [ERROR] Code formatting failed: {error_msg[:200]}")

    # Check if isort is available
    if not check_tool_available("isort"):
        print("  [WARNING] 'isort' tool not found. Skipping import sorting.")
        print("  [INFO] Install with: pip install isort")
        return fixes_applied

    # Sort imports with isort
    if dry_run:
        cmd = "python -m isort --check-only --diff ."
        print("  Checking import sorting with isort...")
    else:
        cmd = "python -m isort ."
        print("  Sorting imports with isort...")

    result = run_command(cmd)
    if result["success"]:
        if dry_run:
            if result["stdout"]:
                print("  [WARNING] Import sorting issues found (dry run)")
            else:
                print("  [OK] Import sorting check passed")
        else:
            print("  [OK] Imports sorted with isort")
            fixes_applied.append("import_sorting")
    else:
        error_msg = result.get("stderr", "Unknown error")
        if "is not recognized" in error_msg or "command not found" in error_msg:
            print(f"  [WARNING] 'isort' command failed. Make sure it's installed: pip install isort")
        else:
            print(f"  [ERROR] Import sorting failed: {error_msg[:200]}")

    return fixes_applied


def fix_lint_issues(dry_run: bool = False) -> List[str]:
    """Fix lint issues using autopep8."""
    print("[CHECK] Fixing lint issues...")

    fixes_applied = []

    if dry_run:
        # Check for lint issues with flake8
        if not check_tool_available("flake8"):
            print("  [WARNING] 'flake8' tool not found. Skipping lint check.")
            print("  [INFO] Install with: pip install flake8")
            return fixes_applied

        cmd = "python -m flake8 --count --statistics ."
        print("  Checking for lint issues with flake8...")

        result = run_command(cmd)
        if result["success"]:
            if result["stdout"] and "0" not in result["stdout"]:
                print(f"  [WARNING] Lint issues found: {result['stdout'].strip()}")
            else:
                print("  [OK] Lint check passed")
        else:
            error_msg = result.get("stderr", "Unknown error")
            if "is not recognized" in error_msg or "command not found" in error_msg:
                print(f"  [WARNING] 'flake8' command failed. Make sure it's installed: pip install flake8")
            else:
                print(f"  [ERROR] Lint check failed: {error_msg[:200]}")
    else:
        # Auto-fix lint issues with autopep8
        if not check_tool_available("autopep8"):
            print("  [WARNING] 'autopep8' tool not found. Skipping lint fixing.")
            print("  [INFO] Install with: pip install autopep8")
            return fixes_applied

        cmd = "python -m autopep8 --in-place --recursive --aggressive ."
        print("  Fixing lint issues with autopep8...")

        result = run_command(cmd)
        if result["success"]:
            print("  [OK] Lint issues fixed with autopep8")
            fixes_applied.append("lint_fixes")
        else:
            error_msg = result.get("stderr", "Unknown error")
            if "is not recognized" in error_msg or "command not found" in error_msg:
                print(f"  [WARNING] 'autopep8' command failed. Make sure it's installed: pip install autopep8")
            else:
                print(f"  [ERROR] Lint fixing failed: {error_msg[:200]}")

    return fixes_applied


def check_security_issues() -> List[str]:
    """Check for security issues (read-only)."""
    print("[SECURITY] Checking security issues...")

    issues_found = []

    # Run bandit security scan
    if not check_tool_available("bandit"):
        print("  [WARNING] 'bandit' tool not found. Skipping security scan.")
        print("  [INFO] Install with: pip install bandit")
    else:
        print("  Running bandit security scan...")
        result = run_command("python -m bandit -r . -f json")

        if result["success"]:
            try:
                data = json.loads(result["stdout"])
                metrics = data.get("metrics", {})
                severity_counts = metrics.get("SEVERITY", {})

                if severity_counts.get("HIGH", 0) > 0:
                    print(f"  [WARNING] Found {severity_counts['HIGH']} high severity security issues")
                    issues_found.append(f"high_security_issues:{severity_counts['HIGH']}")

                if severity_counts.get("MEDIUM", 0) > 0:
                    print(f"  [WARNING] Found {severity_counts['MEDIUM']} medium severity security issues")

            except json.JSONDecodeError:
                print("  [WARNING] Could not parse security scan results")
        else:
            error_msg = result.get("stderr", "Unknown error")
            if "is not recognized" in error_msg or "command not found" in error_msg:
                print(f"  [WARNING] 'bandit' command failed. Make sure it's installed: pip install bandit")
            else:
                print(f"  [ERROR] Security scan failed: {error_msg[:200]}")

    # Check for hardcoded secrets
    print("  Checking for hardcoded secrets...")
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'key\s*=\s*["\'][^"\']+["\']',
        r'credential\s*=\s*["\'][^"\']+["\']',
    ]

    secret_files = []

    for root, dirs, files in os.walk("."):
        # Skip certain directories
        skip_dirs = [".git", "__pycache__", "node_modules", ".venv", "venv"]
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if file.endswith((".py", ".js", ".ts", ".java", ".yml", ".yaml", ".json")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                        # Skip if it's a test file or contains test data
                        if "test" in filepath.lower() or "example" in filepath.lower():
                            continue

                        for pattern in secret_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                # Check if it's in a comment or string literal
                                lines = content.split("\n")
                                for i, line in enumerate(lines, 1):
                                    if re.search(pattern, line, re.IGNORECASE):
                                        # Skip if it's in a comment
                                        if not line.strip().startswith("#"):
                                            secret_files.append(f"{filepath}:{i}")
                                            print(f"  [WARNING] Potential hardcoded secret in {filepath}:{i}")
                                            issues_found.append(f"hardcoded_secret:{filepath}:{i}")
                                break
                except (UnicodeDecodeError, IOError):
                    continue

    if secret_files:
        print(f"  Found {len(secret_files)} potential hardcoded secrets")
    else:
        print("  [OK] No hardcoded secrets found")

    return issues_found


def check_dependency_vulnerabilities() -> List[str]:
    """Check for dependency vulnerabilities."""
    print("[DEPENDENCY] Checking dependency vulnerabilities...")

    issues_found = []

    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("  [WARNING] No requirements.txt found")
        return issues_found

    # Try to run safety check
    if not check_tool_available("safety"):
        print("  [WARNING] 'safety' tool not found. Skipping dependency check.")
        print("  [INFO] Install with: pip install safety")
        return issues_found

    print("  Running safety check...")
    result = run_command("python -m safety check --json")

    if result["success"]:
        try:
            data = json.loads(result["stdout"])
            vulnerabilities = data.get("vulnerabilities", [])

            if vulnerabilities:
                print(f"  [WARNING] Found {len(vulnerabilities)} dependency vulnerabilities")
                for vuln in vulnerabilities[:5]:  # Show first 5
                    print(f"    - {vuln.get('package_name', 'Unknown')}: {vuln.get('advisory', 'No details')}")

                if len(vulnerabilities) > 5:
                    print(f"    ... and {len(vulnerabilities) - 5} more")

                issues_found.append(f"dependency_vulnerabilities:{len(vulnerabilities)}")
            else:
                print("  [OK] No dependency vulnerabilities found")
        except json.JSONDecodeError:
            print("  [WARNING] Could not parse safety check results")
    else:
        error_msg = result.get("stderr", "Unknown error")
        if "is not recognized" in error_msg or "command not found" in error_msg:
            print(f"  [WARNING] 'safety' command failed. Make sure it's installed: pip install safety")
        else:
            print(f"  [ERROR] Safety check failed: {error_msg[:200]}")

    return issues_found

    # Try to run safety check
    print("  Running safety check...")
    result = run_command("safety check --json")

    if result["success"]:
        try:
            data = json.loads(result["stdout"])
            vulnerabilities = data.get("vulnerabilities", [])

            if vulnerabilities:
                print(f"  [WARNING] Found {len(vulnerabilities)} dependency vulnerabilities")
            else:
                print("  [OK] No dependency vulnerabilities found")
        except json.JSONDecodeError:
            print("  [WARNING] Could not parse safety check results")
    else:
        print("  [WARNING] Safety check failed or not installed")

    return issues_found


def generate_report(fixes_applied: List[str], issues_found: List[str], dry_run: bool = False) -> Dict[str, Any]:
    """Generate a report of fixes and issues."""
    import datetime

    # Use timezone-aware UTC datetime
    try:
        # Python 3.11+ with UTC timezone
        utc_now = datetime.datetime.now(datetime.UTC)
    except AttributeError:
        # Fallback for older Python versions
        utc_now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    report = {
        "timestamp": utc_now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dry_run": dry_run,
        "fixes_applied": fixes_applied,
        "issues_found": issues_found,
        "summary": {
            "total_fixes": len(fixes_applied),
            "total_issues": len(issues_found),
            "status": "PASS" if len(issues_found) == 0 else "WARNING",
        },
    }

    return report


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Auto-fix code issues")
    parser.add_argument(
        "--scope",
        default="all",
        choices=["all", "formatting", "linting", "imports", "security"],
        help="Scope of fixes to apply",
    )
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes)")
    parser.add_argument("--output", default="auto-fix-report.json", help="Output report file")

    args = parser.parse_args()

    print("=" * 60)
    print("Auto-fix Script")
    print("=" * 60)
    print(f"Scope: {args.scope}")
    print(f"Dry run: {args.dry_run}")
    print("-" * 60)

    all_fixes = []
    all_issues = []

    # Run fixes based on scope
    if args.scope in ["all", "formatting", "imports"]:
        fixes = fix_code_formatting(args.dry_run)
        all_fixes.extend(fixes)
        print()

    if args.scope in ["all", "linting"]:
        fixes = fix_lint_issues(args.dry_run)
        all_fixes.extend(fixes)
        print()

    if args.scope in ["all", "security"]:
        issues = check_security_issues()
        all_issues.extend(issues)
        print()

        issues = check_dependency_vulnerabilities()
        all_issues.extend(issues)
        print()

    # Generate report
    report = generate_report(all_fixes, all_issues, args.dry_run)

    # Save report to file
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("-" * 60)
    print("[SUMMARY] Auto-fix Summary")
    print("-" * 60)

    if args.dry_run:
        print("[DRY RUN] DRY RUN - No changes were made")

    print(f"Fixes that would be/applied: {len(all_fixes)}")
    if all_fixes:
        for fix in all_fixes:
            print(f"  [FIX] {fix}")

    print(f"Issues found: {len(all_issues)}")
    if all_issues:
        for issue in all_issues:
            print(f"  [ISSUE] {issue}")

    print("-" * 60)

    if report["summary"]["status"] == "PASS":
        print("[SUCCESS] All checks passed")
    else:
        print("[WARNING] Issues found that require attention")

    print(f"Report saved to: {args.output}")
    print("=" * 60)

    # Output for GitHub Actions
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"fixes_applied={json.dumps(all_fixes)}\n")
            f.write(f"issues_found={json.dumps(all_issues)}\n")
            f.write(f"has_fixes={str(len(all_fixes) > 0).lower()}\n")
            f.write(f"has_issues={str(len(all_issues) > 0).lower()}\n")

    # Return appropriate exit code
    if args.dry_run:
        # For dry runs, we don't fail - just report
        return 0
    else:
        # For actual runs, fail if there are security issues
        security_issues = [i for i in all_issues if "high_security_issues" in i or "hardcoded_secret" in i]
        if security_issues:
            return 1
        else:
            return 0


if __name__ == "__main__":
    sys.exit(main())
