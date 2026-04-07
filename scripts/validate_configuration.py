#!/usr/bin/env python3
"""
Configuration validation script for Git CI/CD Quality Gate System
Validates all configuration files and workflow definitions
"""

import os
import sys
import yaml
import json
from pathlib import Path

def validate_yaml_file(file_path):
    """Validate YAML file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        return True, "Valid YAML"
    except yaml.YAMLError as e:
        return False, f"YAML syntax error: {str(e)}"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def validate_workflow_structure(file_path):
    """Validate GitHub Actions workflow structure"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
        
        errors = []
        
        # Check required fields
        if 'name' not in workflow:
            errors.append("Missing 'name' field")
        
        if 'on' not in workflow and '"on"' not in workflow:
            errors.append("Missing 'on' field (trigger configuration)")
        
        if 'jobs' not in workflow:
            errors.append("Missing 'jobs' field")
        else:
            # Check job structure
            for job_name, job_config in workflow['jobs'].items():
                if 'runs-on' not in job_config:
                    errors.append(f"Job '{job_name}' missing 'runs-on' field")
                if 'steps' not in job_config:
                    errors.append(f"Job '{job_name}' missing 'steps' field")
        
        return len(errors) == 0, errors if errors else ["Valid workflow structure"]
    
    except Exception as e:
        return False, [f"Error validating workflow: {str(e)}"]

def validate_branch_protection(file_path):
    """Validate branch protection rules"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        
        errors = []
        
        # Check if this is the custom format (has 'rules' key)
        if 'rules' in rules:
            # Custom format - check each rule
            for rule in rules.get('rules', []):
                if 'pattern' not in rule:
                    errors.append(f"Rule missing 'pattern' field")
                if 'protection_settings' not in rule:
                    errors.append(f"Rule for pattern '{rule.get('pattern', 'unknown')}' missing 'protection_settings'")
                else:
                    settings = rule['protection_settings']
                    if 'required_status_checks' not in settings:
                        errors.append(f"Rule '{rule.get('pattern', 'unknown')}' missing 'required_status_checks'")
                    if 'enforce_admins' not in settings:
                        errors.append(f"Rule '{rule.get('pattern', 'unknown')}' missing 'enforce_admins'")
                    if 'required_pull_request_reviews' not in settings:
                        errors.append(f"Rule '{rule.get('pattern', 'unknown')}' missing 'required_pull_request_reviews'")
                    if 'restrictions' not in settings:
                        errors.append(f"Rule '{rule.get('pattern', 'unknown')}' missing 'restrictions'")
            
            if not errors:
                return True, ["Valid custom branch protection format"]
        
        # Check if this is the direct GitHub API format
        elif 'required_status_checks' in rules:
            # Direct GitHub API format
            if 'strict' not in rules['required_status_checks']:
                errors.append("Missing 'strict' field in required_status_checks")
            if 'contexts' not in rules['required_status_checks']:
                errors.append("Missing 'contexts' field in required_status_checks")
            
            if 'enforce_admins' not in rules:
                errors.append("Missing 'enforce_admins' field")
            
            if 'required_pull_request_reviews' not in rules:
                errors.append("Missing 'required_pull_request_reviews' field")
            else:
                if 'required_approving_review_count' not in rules['required_pull_request_reviews']:
                    errors.append("Missing 'required_approving_review_count' field")
            
            if 'restrictions' not in rules:
                errors.append("Missing 'restrictions' field")
            
            if not errors:
                return True, ["Valid GitHub API branch protection format"]
        
        else:
            errors.append("Unknown branch protection format. Expected either custom 'rules' format or direct GitHub API format")
        
        return len(errors) == 0, errors if errors else ["Valid branch protection rules"]
    
    except Exception as e:
        return False, [f"Error validating branch protection: {str(e)}"]

def check_required_scripts():
    """Check if required quality gate scripts exist"""
    required_scripts = [
        'scripts/security_audit_simple.py',
        'scripts/solid_principles_checker.py',
        'scripts/quality_gate_evaluator.py',
        'scripts/quality_thresholds.yml'
    ]
    
    missing = []
    for script in required_scripts:
        if not os.path.exists(script):
            missing.append(script)
    
    return len(missing) == 0, missing if missing else ["All required scripts exist"]

def validate_workflow_dependencies():
    """Validate workflow dependencies and job relationships"""
    workflows_dir = Path('.github/workflows')
    workflows = list(workflows_dir.glob('*.yml'))
    
    errors = []
    
    for workflow_file in workflows:
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow = yaml.safe_load(f)
            
            if 'jobs' in workflow:
                for job_name, job_config in workflow['jobs'].items():
                    if 'needs' in job_config:
                        needs = job_config['needs']
                        if isinstance(needs, list):
                            for needed_job in needs:
                                if needed_job not in workflow['jobs']:
                                    errors.append(f"Workflow '{workflow_file.name}': Job '{job_name}' depends on non-existent job '{needed_job}'")
        
        except Exception as e:
            errors.append(f"Error parsing {workflow_file.name}: {str(e)}")
    
    return len(errors) == 0, errors if errors else ["Valid workflow dependencies"]

def main():
    """Main validation function"""
    print("Validating Git CI/CD Quality Gate System Configuration")
    print("=" * 60)
    
    validation_results = []
    
    # 1. Validate workflow files
    print("\nValidating workflow files...")
    workflows = [
        '.github/workflows/ci-cd-new.yml',
        '.github/workflows/pr-quality-gates.yml',
        '.github/workflows/auto-fix.yml',
        '.github/workflows/emergency-fix.yml',
        '.github/workflows/auto-assign-reviewers.yml'
    ]
    
    for workflow in workflows:
        if os.path.exists(workflow):
            yaml_valid, yaml_msg = validate_yaml_file(workflow)
            struct_valid, struct_msg = validate_workflow_structure(workflow)
            
            status = "[OK]" if (yaml_valid and struct_valid) else "[ERROR]"
            print(f"  {status} {workflow}")
            
            if not yaml_valid:
                validation_results.append(f"{workflow}: {yaml_msg}")
            if not struct_valid:
                validation_results.append(f"{workflow}: {struct_msg}")
        else:
            print(f"  [WARNING] {workflow} (not found)")
            validation_results.append(f"{workflow}: File not found")
    
    # 2. Validate branch protection rules
    print("\nValidating branch protection rules...")
    bp_file = '.github/branch-protection-rules.yml'
    if os.path.exists(bp_file):
        valid, msg = validate_branch_protection(bp_file)
        status = "[OK]" if valid else "[ERROR]"
        print(f"  {status} {bp_file}")
        if not valid:
            validation_results.extend([f"{bp_file}: {m}" for m in msg])
    else:
        print(f"  [WARNING] {bp_file} (not found)")
        validation_results.append(f"{bp_file}: File not found")
    
    # 3. Check required scripts
    print("\nChecking required scripts...")
    scripts_valid, scripts_msg = check_required_scripts()
    status = "[OK]" if scripts_valid else "[ERROR]"
    print(f"  {status} Required scripts")
    if not scripts_valid:
        validation_results.extend([f"Missing script: {m}" for m in scripts_msg])
    
    # 4. Validate workflow dependencies
    print("\nValidating workflow dependencies...")
    deps_valid, deps_msg = validate_workflow_dependencies()
    status = "[OK]" if deps_valid else "[ERROR]"
    print(f"  {status} Workflow dependencies")
    if not deps_valid:
        validation_results.extend([f"Dependency error: {m}" for m in deps_msg])
    
    # 5. Summary
    print("\n" + "=" * 60)
    print("Validation Summary:")
    
    if validation_results:
        print("[FAILED] Validation failed with the following issues:")
        for result in validation_results:
            print(f"  * {result}")
        return 1
    else:
        print("[PASSED] All validations passed!")
        print("\nConfiguration is ready for deployment.")
        print("\nNext steps:")
        print("1. Rename 'ci-cd-new.yml' to 'ci-cd.yml' (after resolving file lock)")
        print("2. Apply branch protection rules using GitHub CLI")
        print("3. Test the integrated CI/CD pipeline")
        return 0

if __name__ == "__main__":
    sys.exit(main())