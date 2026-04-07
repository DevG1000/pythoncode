#!/usr/bin/env python3
"""
Simple deployment verification
"""

import os
import sys

def check_file_exists(file_path):
    """Check if file exists"""
    if os.path.exists(file_path):
        return True, f"Found: {file_path}"
    else:
        return False, f"Missing: {file_path}"

def main():
    """Main verification"""
    print("Deployment Readiness Check")
    print("=" * 60)
    
    checks = []
    
    # Check workflow files
    workflow_files = [
        ".github/workflows/ci-cd-integrated-final.yml",
        ".github/workflows/pr-quality-gates.yml",
        ".github/workflows/auto-fix.yml",
        ".github/workflows/emergency-fix.yml"
    ]
    
    print("\nWorkflow Files:")
    for wf in workflow_files:
        passed, msg = check_file_exists(wf)
        status = "[OK]" if passed else "[MISSING]"
        print(f"  {status} {msg}")
        checks.append(passed)
    
    # Check quality gate scripts
    print("\nQuality Gate Scripts:")
    scripts = [
        "scripts/security_audit_simple.py",
        "scripts/solid_principles_checker.py",
        "scripts/quality_gate_evaluator.py",
        "scripts/quality_thresholds.yml"
    ]
    
    for script in scripts:
        passed, msg = check_file_exists(script)
        status = "[OK]" if passed else "[MISSING]"
        print(f"  {status} {msg}")
        checks.append(passed)
    
    # Check configuration files
    print("\nConfiguration Files:")
    configs = [
        ".github/branch-protection-rules.yml",
        ".github/environments/staging.yml",
        ".github/environments/production.yml",
        ".github/permissions.yml"
    ]
    
    for config in configs:
        passed, msg = check_file_exists(config)
        status = "[OK]" if passed else "[MISSING]"
        print(f"  {status} {msg}")
        checks.append(passed)
    
    # Summary
    print("\n" + "=" * 60)
    total = len(checks)
    passed = sum(checks)
    
    print(f"Summary: {passed}/{total} checks passed")
    
    if all(checks):
        print("\n[SUCCESS] All checks passed!")
        print("\nNext steps:")
        print("1. Install GitHub CLI: winget install --id GitHub.cli")
        print("2. Authenticate: gh auth login")
        print("3. Apply branch protection rules")
        print("4. Set up environment secrets")
        print("5. Configure teams and permissions")
        print("6. Run test deployment")
        return 0
    else:
        print("\n[FAILED] Some checks failed")
        print("Please fix missing files before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())