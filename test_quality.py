#!/usr/bin/env python
"""
Quick quality test to check current state
"""

import subprocess
import json
import os

def run_command(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_pylint():
    """Check pylint score"""
    print("Checking pylint score...")
    cmd = "python -m pylint api/ command_system/ card_generator/ --exit-zero | findstr 'Your code has been rated at'"
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0 and stdout:
        # Extract score
        import re
        match = re.search(r'(\d+\.\d+)/10', stdout)
        if match:
            score = float(match.group(1))
            print(f"Pylint score: {score}/10")
            return score >= 7.0, score
    return False, 0

def check_bandit():
    """Check bandit security"""
    print("Checking bandit security...")
    cmd = "bandit -r api/ command_system/ card_generator/ -f json"
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode in [0, 1]:  # Bandit returns 1 when issues found
        try:
            data = json.loads(stdout)
            metrics = data.get('metrics', {})
            totals = metrics.get('_totals', {}).get('SEVERITY', {})
            high_issues = totals.get('HIGH', 0)
            print(f"High severity issues: {high_issues}")
            return high_issues == 0, high_issues
        except:
            pass
    return False, 999

def check_design_principles():
    """Check design principles"""
    print("Checking design principles...")
    # Count issues from the checker output
    cmd = "python check_design_principles.py"
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0:
        # Count issues from output
        issues = 0
        lines = stdout.split('\n')
        for line in lines:
            if '原则问题 (' in line:
                # Extract number from "SRP原则问题 (8个):"
                import re
                match = re.search(r'\((\d+)个\)', line)
                if match:
                    issues += int(match.group(1))
        
        print(f"Design principle issues: {issues}")
        
        # Calculate score: 20 - min(issues, 10) * 2
        score = max(0, 20 - min(issues, 10) * 2)
        passed = issues <= 5  # Allow up to 5 issues
        return passed, score
    return False, 0

def main():
    """Main function"""
    print("=" * 60)
    print("QUICK QUALITY CHECK")
    print("=" * 60)
    
    results = []
    
    # Check pylint
    pylint_passed, pylint_score = check_pylint()
    results.append(("Pylint", pylint_passed, f"{pylint_score}/10"))
    
    # Check bandit
    bandit_passed, bandit_issues = check_bandit()
    results.append(("Bandit", bandit_passed, f"{bandit_issues} high issues"))
    
    # Check design principles
    design_passed, design_score = check_design_principles()
    results.append(("Design Principles", design_passed, f"{design_score}/20"))
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed, details in results:
        status = "PASS" if passed else "FAIL"
        print(f"{name:20} {status:10} {details}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL CHECKS PASSED!")
    else:
        print("SOME CHECKS FAILED")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())