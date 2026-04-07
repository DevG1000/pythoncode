#!/usr/bin/env python3
"""
Integrated CI/CD Pipeline Test Script
Tests the complete quality gate system end-to-end
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any

class PipelineTester:
    """Test the integrated CI/CD pipeline"""
    
    def __init__(self):
        self.results = {
            "overall": {"passed": True, "tests_run": 0, "tests_passed": 0},
            "tests": [],
            "warnings": [],
            "errors": []
        }
    
    def test_workflow_files_exist(self) -> bool:
        """Test that all required workflow files exist"""
        test_name = "Workflow Files Exist"
        required_files = [
            ".github/workflows/ci-cd-new.yml",
            ".github/workflows/pr-quality-gates.yml",
            ".github/workflows/auto-fix.yml",
            ".github/workflows/emergency-fix.yml",
            ".github/workflows/auto-assign-reviewers.yml",
            ".github/workflows/scheduled-tests.yml",
            ".github/workflows/release.yml"
        ]
        
        missing = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing.append(file_path)
        
        passed = len(missing) == 0
        message = "All workflow files exist" if passed else f"Missing files: {missing}"
        
        self.record_test(test_name, passed, message)
        return passed
    
    def test_workflow_yaml_syntax(self) -> bool:
        """Test that all workflow YAML files have valid syntax"""
        test_name = "Workflow YAML Syntax"
        
        workflows_dir = Path(".github/workflows")
        workflows = list(workflows_dir.glob("*.yml"))
        
        errors = []
        for workflow_file in workflows:
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                errors.append(f"{workflow_file.name}: {str(e)}")
        
        passed = len(errors) == 0
        message = "All workflow YAML files have valid syntax" if passed else f"YAML errors: {errors}"
        
        self.record_test(test_name, passed, message)
        return passed
    
    def test_quality_gate_scripts(self) -> bool:
        """Test that quality gate scripts exist and are executable"""
        test_name = "Quality Gate Scripts"
        
        required_scripts = [
            "scripts/security_audit_simple.py",
            "scripts/solid_principles_checker.py",
            "scripts/quality_gate_evaluator.py",
            "scripts/quality_thresholds.yml"
        ]
        
        missing = []
        for script in required_scripts:
            if not os.path.exists(script):
                missing.append(script)
        
        passed = len(missing) == 0
        message = "All quality gate scripts exist" if passed else f"Missing scripts: {missing}"
        
        self.record_test(test_name, passed, message)
        return passed
    
    def test_branch_protection_config(self) -> bool:
        """Test branch protection configuration"""
        test_name = "Branch Protection Configuration"
        
        config_files = [
            ".github/branch-protection-rules.yml",
            ".github/branch-protection-api.yml"
        ]
        
        existing = []
        for config_file in config_files:
            if os.path.exists(config_file):
                existing.append(config_file)
        
        passed = len(existing) > 0
        message = f"Branch protection config exists: {existing}" if passed else "No branch protection configuration found"
        
        self.record_test(test_name, passed, message)
        return passed
    
    def test_environment_configs(self) -> bool:
        """Test environment configurations"""
        test_name = "Environment Configurations"
        
        env_dir = Path(".github/environments")
        env_files = list(env_dir.glob("*.yml")) if env_dir.exists() else []
        
        required_envs = ["staging", "production"]
        existing_envs = [f.stem for f in env_files]
        
        missing = [env for env in required_envs if env not in existing_envs]
        
        passed = len(missing) == 0
        message = f"Environment configs exist: {existing_envs}" if passed else f"Missing environment configs: {missing}"
        
        self.record_test(test_name, passed, message)
        return passed
    
    def test_permissions_config(self) -> bool:
        """Test permissions configuration"""
        test_name = "Permissions Configuration"
        
        permissions_file = ".github/permissions.yml"
        
        if os.path.exists(permissions_file):
            try:
                with open(permissions_file, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                passed = True
                message = "Permissions configuration is valid YAML"
            except yaml.YAMLError as e:
                passed = False
                message = f"Permissions YAML error: {str(e)}"
        else:
            passed = False
            message = "Permissions configuration file not found"
        
        self.record_test(test_name, passed, message)
        return passed
    
    def test_ci_cd_integration(self) -> bool:
        """Test CI/CD pipeline integration"""
        test_name = "CI/CD Pipeline Integration"
        
        ci_cd_file = ".github/workflows/ci-cd-new.yml"
        
        if not os.path.exists(ci_cd_file):
            self.record_test(test_name, False, "CI/CD pipeline file not found")
            return False
        
        try:
            with open(ci_cd_file, 'r', encoding='utf-8') as f:
                workflow = yaml.safe_load(f)
            
            # Check for quality gates job
            jobs = workflow.get('jobs', {})
            has_quality_gates = 'quality-gates-assessment' in jobs
            
            # Check job dependencies
            quality_gates_job = jobs.get('quality-gates-assessment', {})
            needs = quality_gates_job.get('needs', [])
            has_dependencies = 'security-audit' in needs and 'lint-and-format' in needs
            
            passed = has_quality_gates and has_dependencies
            message = "CI/CD pipeline has integrated quality gates with proper dependencies" if passed else "CI/CD pipeline missing quality gates integration"
            
            self.record_test(test_name, passed, message)
            return passed
            
        except Exception as e:
            self.record_test(test_name, False, f"Error reading CI/CD pipeline: {str(e)}")
            return False
    
    def test_workflow_triggers(self) -> bool:
        """Test workflow trigger configurations"""
        test_name = "Workflow Triggers"
        
        workflows_dir = Path(".github/workflows")
        workflows = list(workflows_dir.glob("*.yml"))
        
        errors = []
        for workflow_file in workflows:
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow = yaml.safe_load(f)
                
                # Check for trigger configuration
                # GitHub Actions accepts both 'on' and '"on"' (quoted for YAML compatibility)
                # In YAML, 'on:' (without quotes) is parsed as boolean True
                has_trigger = False
                if isinstance(workflow, dict):
                    # Check for boolean True key (when 'on:' is unquoted)
                    if True in workflow:
                        has_trigger = True
                    else:
                        # Check for string key 'on' or '"on"'
                        for key in workflow.keys():
                            if isinstance(key, str) and key.strip('"\'') == 'on':
                                has_trigger = True
                                break
                
                if not has_trigger:
                    errors.append(f"{workflow_file.name}: Missing trigger configuration")
                
            except Exception as e:
                errors.append(f"{workflow_file.name}: Error - {str(e)}")
        
        passed = len(errors) == 0
        message = "All workflows have trigger configurations" if passed else f"Trigger errors: {errors}"
        
        self.record_test(test_name, passed, message)
        return passed
    
    def test_validation_script(self) -> bool:
        """Test the configuration validation script"""
        test_name = "Configuration Validation"
        
        validation_script = "scripts/validate_configuration.py"
        
        if not os.path.exists(validation_script):
            self.record_test(test_name, False, "Validation script not found")
            return False
        
        try:
            # Run the validation script
            import subprocess
            result = subprocess.run(
                [sys.executable, validation_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            passed = result.returncode == 0
            message = "Configuration validation passed" if passed else f"Validation failed: {result.stderr[:200]}"
            
            self.record_test(test_name, passed, message)
            return passed
            
        except Exception as e:
            self.record_test(test_name, False, f"Error running validation script: {str(e)}")
            return False
    
    def record_test(self, name: str, passed: bool, message: str) -> None:
        """Record test result"""
        test_result = {
            "name": name,
            "passed": passed,
            "message": message
        }
        self.results["tests"].append(test_result)
        self.results["overall"]["tests_run"] += 1
        if passed:
            self.results["overall"]["tests_passed"] += 1
        else:
            self.results["overall"]["passed"] = False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        print("Running Integrated CI/CD Pipeline Tests")
        print("=" * 50)
        
        tests = [
            self.test_workflow_files_exist,
            self.test_workflow_yaml_syntax,
            self.test_quality_gate_scripts,
            self.test_branch_protection_config,
            self.test_environment_configs,
            self.test_permissions_config,
            self.test_ci_cd_integration,
            self.test_workflow_triggers,
            self.test_validation_script
        ]
        
        for test_func in tests:
            test_func()
        
        return self.results
    
    def print_summary(self) -> None:
        """Print test summary"""
        print("\n" + "=" * 50)
        print("Test Summary")
        print("=" * 50)
        
        overall = self.results["overall"]
        print(f"\nOverall Status: {'PASS' if overall['passed'] else 'FAIL'}")
        print(f"Tests Run: {overall['tests_run']}")
        print(f"Tests Passed: {overall['tests_passed']}")
        print(f"Tests Failed: {overall['tests_run'] - overall['tests_passed']}")
        
        print("\nDetailed Results:")
        print("-" * 50)
        
        for test in self.results["tests"]:
            status = "[PASS]" if test["passed"] else "[FAIL]"
            print(f"\n{status} {test['name']}")
            print(f"  {test['message']}")
        
        if self.results["warnings"]:
            print("\n[WARNING] Warnings:")
            for warning in self.results["warnings"]:
                print(f"  * {warning}")
        
        if self.results["errors"]:
            print("\n[ERROR] Errors:")
            for error in self.results["errors"]:
                print(f"  * {error}")
        
        print("\n" + "=" * 50)
        
        if overall['passed']:
            print("[SUCCESS] All tests passed! The CI/CD pipeline is ready for deployment.")
            print("\nNext steps:")
            print("1. Rename 'ci-cd-new.yml' to 'ci-cd.yml'")
            print("2. Apply branch protection rules using GitHub CLI")
            print("3. Set up environment secrets in GitHub")
            print("4. Configure teams and permissions in GitHub organization")
            print("5. Run a test deployment to verify everything works")
        else:
            print("[FAILED] Some tests failed. Please fix the issues before deployment.")
            print("\nCheck the detailed results above for specific issues to fix.")

def main():
    """Main function"""
    tester = PipelineTester()
    results = tester.run_all_tests()
    tester.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if results["overall"]["passed"] else 1)

if __name__ == "__main__":
    main()