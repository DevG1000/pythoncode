#!/usr/bin/env python3
"""
Test Staging Deployment Script
Tests the staging deployment workflow and configuration
"""

import argparse
import json
import os
import subprocess
import sys
import yaml
from datetime import datetime
from pathlib import Path


def run_command(command, description=None):
    """Run a shell command"""
    if description:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {description}")
        print(f"  Command: {command}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                if line:
                    print(f"  Output: {line}")

        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                if line:
                    print(f"  Error: {line}")

        return result.returncode == 0, result.stdout, result.stderr

    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False, "", str(e)


def test_github_cli():
    """Test GitHub CLI installation and authentication"""
    print("\n" + "=" * 60)
    print("Testing GitHub CLI...")
    print("=" * 60)
    
    tests = [
        ("gh --version", "Check GitHub CLI version"),
        ("gh auth status", "Check authentication status"),
    ]
    
    all_passed = True
    for cmd, desc in tests:
        success, stdout, stderr = run_command(cmd, desc)
        if success:
            print(f"  [PASS] {desc}")
        else:
            print(f"  [FAIL] {desc}")
            all_passed = False
    
    return all_passed


def test_staging_environment():
    """Test staging environment configuration"""
    print("\n" + "=" * 60)
    print("Testing staging environment...")
    print("=" * 60)
    
    tests = [
        ("gh api repos/DevG1000/pythoncode/environments/staging", "Check staging environment exists"),
        ("gh variable list --env staging", "List staging environment variables"),
        ("gh secret list --env staging", "List staging environment secrets"),
    ]
    
    all_passed = True
    for cmd, desc in tests:
        success, stdout, stderr = run_command(cmd, desc)
        if success:
            print(f"  [OK] {desc}")
            if "variable" in desc.lower() and stdout:
                print(f"    Found variables: {len(stdout.strip().split(chr(10)))}")
            elif "secret" in desc.lower() and stdout:
                print(f"    Found secrets: {len(stdout.strip().split(chr(10)))}")
        else:
            print(f"  [FAIL] {desc}")
            all_passed = False
    
    return all_passed


def test_workflow_configuration():
    """Test CI/CD workflow configuration"""
    print("\n" + "=" * 60)
    print("Testing workflow configuration...")
    print("=" * 60)
    
    workflow_file = ".github/workflows/ci-cd-integrated-final.yml"
    
    if not Path(workflow_file).exists():
        print(f"  [FAIL] Workflow file not found: {workflow_file}")
        return False
    
    try:
        with open(workflow_file, 'r') as f:
            workflow_content = f.read()
        
        checks = [
            ("Workflow contains 'environment: staging'", "environment: staging" in workflow_content),
            ("Workflow contains 'deploy-staging' job", "deploy-staging:" in workflow_content),
            ("Workflow uses staging environment variables", "vars.ENVIRONMENT" in workflow_content or "vars.LOG_LEVEL" in workflow_content),
            ("Workflow uses staging secrets", "secrets.STAGING_" in workflow_content),
        ]
        
        all_passed = True
        for check_desc, check_result in checks:
            if check_result:
                print(f"  [OK] {check_desc}")
            else:
                print(f"  [FAIL] {check_desc}")
                all_passed = False
        
        # Parse YAML to check structure
        try:
            workflow_yaml = yaml.safe_load(workflow_content)
            jobs = workflow_yaml.get('jobs', {})
            
            if 'deploy-staging' in jobs:
                deploy_job = jobs['deploy-staging']
                print(f"  [OK] Found deploy-staging job")
                
                # Check environment
                env = deploy_job.get('environment')
                if env == 'staging':
                    print(f"  [OK] deploy-staging uses staging environment")
                else:
                    print(f"  [FAIL] deploy-staging environment: {env}")
                    all_passed = False
                
                # Check environment variables
                env_vars = deploy_job.get('env', {})
                if env_vars:
                    print(f"  [OK] deploy-staging has {len(env_vars)} environment variables")
                else:
                    print(f"  [WARN] deploy-staging has no environment variables")
            else:
                print(f"  [FAIL] deploy-staging job not found")
                all_passed = False
                
        except yaml.YAMLError as e:
            print(f"  [FAIL] Error parsing YAML: {e}")
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"  [FAIL] Error reading workflow file: {e}")
        return False


def test_deployment_scripts():
    """Test deployment scripts"""
    print("\n" + "=" * 60)
    print("Testing deployment scripts...")
    print("=" * 60)
    
    scripts = [
        "scripts/deploy_staging.py",
        "scripts/verify_staging_deployment.py",
        "scripts/manage_staging_env.ps1",
        "scripts/setup_staging_env_windows.bat",
    ]
    
    all_passed = True
    for script in scripts:
        if Path(script).exists():
            print(f"  [OK] {script}")
            
            # Check if script is executable (Python scripts)
            if script.endswith('.py'):
                success, stdout, stderr = run_command(f"python {script} --help", f"Test {script}")
                if success:
                    print(f"    [OK] Script runs successfully")
                else:
                    print(f"    [WARN] Script help test failed")
        else:
            print(f"  [FAIL] {script} not found")
            all_passed = False
    
    return all_passed


def test_dry_run_deployment():
    """Test dry run deployment"""
    print("\n" + "=" * 60)
    print("Testing dry run deployment...")
    print("=" * 60)
    
    # Set test environment variables
    test_env = {
        "ENVIRONMENT": "staging",
        "LOG_LEVEL": "DEBUG",
        "API_URL": "https://api.staging.pythoncode.com",
        "STAGING_DATABASE_URL": "postgresql://test:test@localhost:5432/test",
        "STAGING_REDIS_URL": "redis://localhost:6379/0",
        "STAGING_API_KEY": "test_api_key_123",
    }
    
    # Save original environment
    original_env = os.environ.copy()
    
    try:
        # Update environment
        os.environ.update(test_env)
        
        # Run dry run deployment
        print("Running dry run deployment...")
        success, stdout, stderr = run_command(
            "python scripts/deploy_staging.py --dry-run --verbose",
            "Dry run staging deployment"
        )
        
        if success:
            print("  [OK] Dry run deployment completed successfully")
            
            # Check for artifacts
            artifacts = [".env.staging", "deployment-summary.json"]
            for artifact in artifacts:
                if Path(artifact).exists():
                    print(f"  [OK] Artifact created: {artifact}")
                    
                    if artifact == "deployment-summary.json":
                        try:
                            with open(artifact, 'r') as f:
                                summary = json.load(f)
                            print(f"    Deployment status: {summary.get('status', 'N/A')}")
                            print(f"    Environment: {summary.get('environment', 'N/A')}")
                        except Exception as e:
                            print(f"    [WARN] Error reading {artifact}: {e}")
                else:
                    print(f"  [WARN] Artifact not created: {artifact}")
        else:
            print("  [FAIL] Dry run deployment failed")
            return False
        
        # Clean up artifacts
        for artifact in artifacts:
            if Path(artifact).exists():
                Path(artifact).unlink()
                print(f"  Cleaned up: {artifact}")
        
        return success
        
    except Exception as e:
        print(f"  [FAIL] Error during dry run: {e}")
        return False
        
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def generate_test_report():
    """Generate test report"""
    print("\n" + "=" * 60)
    print("Generating test report...")
    print("=" * 60)
    
    test_results = {
        "github_cli": test_github_cli(),
        "staging_environment": test_staging_environment(),
        "workflow_configuration": test_workflow_configuration(),
        "deployment_scripts": test_deployment_scripts(),
        "dry_run_deployment": test_dry_run_deployment(),
    }
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "environment": "staging",
        "test_type": "deployment_configuration",
        "results": test_results,
        "summary": {
            "total_tests": len(test_results),
            "passed_tests": sum(1 for result in test_results.values() if result),
            "failed_tests": sum(1 for result in test_results.values() if not result),
        }
    }
    
    # Save report
    report_file = "staging-deployment-test-report.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"  [OK] Test report saved to {report_file}")
        
        # Print summary
        print(f"\n  Test Summary:")
        print(f"    Total tests: {report['summary']['total_tests']}")
        print(f"    Passed: {report['summary']['passed_tests']}")
        print(f"    Failed: {report['summary']['failed_tests']}")
        
        return report_file
        
    except Exception as e:
        print(f"  [FAIL] Error saving test report: {e}")
        return None


def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description="Test staging deployment configuration")
    parser.add_argument("--skip-dry-run", action="store_true", help="Skip dry run deployment test")
    parser.add_argument("--output", "-o", default="staging-deployment-test-report.json", 
                       help="Output report file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("STAGING DEPLOYMENT CONFIGURATION TEST")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Override dry run test if requested
    if args.skip_dry_run:
        print("[WARN] Dry run deployment test will be skipped")
        # Monkey patch the test function to return True
        import types
        test_dry_run_deployment = lambda: True
    
    # Generate test report
    report_file = generate_test_report()
    
    # Final verdict
    print("\n" + "=" * 60)
    print("TEST RESULT")
    print("=" * 60)
    
    if report_file and Path(report_file).exists():
        try:
            with open(report_file, 'r') as f:
                report = json.load(f)
            
            failed_tests = report["summary"]["failed_tests"]
            passed_tests = report["summary"]["passed_tests"]
            
            if failed_tests == 0:
                print("[OK] ALL TESTS PASSED")
                print(f"   {passed_tests} test(s) passed successfully")
                print("\n[OK] Staging deployment configuration is ready!")
                print("   Next: Run actual deployment with GitHub Actions")
                return_code = 0
            else:
                print("[FAIL] SOME TESTS FAILED")
                print(f"   {failed_tests} test(s) failed, {passed_tests} passed")
                print("\n[WARN] Staging deployment configuration needs attention")
                print("   Check the failed tests above")
                return_code = 1
            
            print(f"\nReport saved to: {report_file}")
            print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            sys.exit(return_code)
            
        except Exception as e:
            print(f"[FAIL] Error reading test report: {e}")
            sys.exit(1)
    else:
        print("[FAIL] Test report not generated")
        sys.exit(1)


if __name__ == "__main__":
    main()