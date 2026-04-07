#!/usr/bin/env python3
"""
验证部署就绪状态
检查所有配置是否完整，准备生产部署
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime

class DeploymentVerifier:
    """验证部署就绪状态"""
    
    def __init__(self):
        self.results = {
            "overall": {"ready": True, "checks_passed": 0, "checks_total": 0},
            "checks": [],
            "warnings": [],
            "next_steps": []
        }
    
    def check_workflow_files(self):
        """Check workflow files"""
        check_name = "Workflow Files Configuration"
        
        required_files = [
            ".github/workflows/ci-cd-integrated-final.yml",
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
        message = "All workflow files configured" if passed else f"Missing files: {missing}"
        
        self.record_check(check_name, passed, message)
        return passed
    
    def check_quality_gate_scripts(self):
        """Check quality gate scripts"""
        check_name = "Quality Gate Scripts"
        
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
        message = "All quality gate scripts ready" if passed else f"Missing scripts: {missing}"
        
        self.record_check(check_name, passed, message)
        return passed
    
    def check_configuration_files(self):
        """检查配置文件"""
        check_name = "配置文件"
        
        config_files = [
            ".github/branch-protection-rules.yml",
            ".github/branch-protection-api.yml",
            ".github/environments/staging.yml",
            ".github/environments/production.yml",
            ".github/permissions.yml"
        ]
        
        missing = []
        for config in config_files:
            if not os.path.exists(config):
                missing.append(config)
        
        passed = len(missing) == 0
        message = "所有配置文件已就绪" if passed else f"缺少配置文件: {missing}"
        
        self.record_check(check_name, passed, message)
        return passed
    
    def check_validation_scripts(self):
        """检查验证脚本"""
        check_name = "验证工具"
        
        validation_scripts = [
            "scripts/validate_configuration.py",
            "scripts/test_integrated_pipeline.py",
            "scripts/verify_deployment_readiness.py"
        ]
        
        missing = []
        for script in validation_scripts:
            if not os.path.exists(script):
                missing.append(script)
        
        passed = len(missing) == 0
        message = "所有验证工具已就绪" if passed else f"缺少验证工具: {missing}"
        
        self.record_check(check_name, passed, message)
        return passed
    
    def check_deployment_docs(self):
        """检查部署文档"""
        check_name = "部署文档"
        
        deployment_docs = [
            "phase3_deployment_summary.md",
            "scripts/deploy_branch_protection.md",
            "scripts/setup_environment_secrets.md",
            "scripts/setup_teams_permissions.md",
            "scripts/test_deployment_guide.md"
        ]
        
        missing = []
        for doc in deployment_docs:
            if not os.path.exists(doc):
                missing.append(doc)
        
        passed = len(missing) == 0
        message = "所有部署文档已就绪" if passed else f"缺少文档: {missing}"
        
        self.record_check(check_name, passed, message)
        return passed
    
    def check_yaml_syntax(self):
        """检查 YAML 语法"""
        check_name = "YAML 语法"
        
        yaml_files = []
        # 检查所有 .yml 文件
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(('.yml', '.yaml')):
                    yaml_files.append(os.path.join(root, file))
        
        errors = []
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                errors.append(f"{yaml_file}: {str(e)}")
        
        passed = len(errors) == 0
        message = "所有 YAML 文件语法正确" if passed else f"YAML 语法错误: {errors[:3]}"  # 只显示前3个错误
        
        self.record_check(check_name, passed, message)
        return passed
    
    def check_workflow_integration(self):
        """检查工作流集成"""
        check_name = "工作流集成"
        
        ci_cd_file = ".github/workflows/ci-cd-integrated-final.yml"
        
        if not os.path.exists(ci_cd_file):
            self.record_check(check_name, False, "集成工作流文件不存在")
            return False
        
        try:
            with open(ci_cd_file, 'r', encoding='utf-8') as f:
                workflow = yaml.safe_load(f)
            
            # 检查是否包含质量门作业
            jobs = workflow.get('jobs', {})
            has_quality_gates = 'quality-gates-assessment' in jobs
            
            # 检查作业依赖
            quality_gates_job = jobs.get('quality-gates-assessment', {})
            needs = quality_gates_job.get('needs', [])
            has_dependencies = 'security-audit' in needs and 'lint-and-format' in needs
            
            passed = has_quality_gates and has_dependencies
            message = "工作流集成正确" if passed else "工作流集成不完整"
            
            self.record_check(check_name, passed, message)
            return passed
            
        except Exception as e:
            self.record_check(check_name, False, f"检查工作流集成失败: {str(e)}")
            return False
    
    def record_check(self, name, passed, message):
        """记录检查结果"""
        check = {
            "name": name,
            "passed": passed,
            "message": message
        }
        self.results["checks"].append(check)
        self.results["overall"]["checks_total"] += 1
        if passed:
            self.results["overall"]["checks_passed"] += 1
        else:
            self.results["overall"]["ready"] = False
    
    def run_all_checks(self):
        """运行所有检查"""
        print("Verify Deployment Readiness")
        print("=" * 60)
        
        checks = [
            self.check_workflow_files,
            self.check_quality_gate_scripts,
            self.check_configuration_files,
            self.check_validation_scripts,
            self.check_deployment_docs,
            self.check_yaml_syntax,
            self.check_workflow_integration
        ]
        
        for check_func in checks:
            check_func()
        
        return self.results
    
    def generate_next_steps(self):
        """生成下一步操作"""
        next_steps = []
        
        # 基于检查结果生成建议
        if not os.path.exists(".github/workflows/ci-cd.yml"):
            next_steps.append("1. 重命名 'ci-cd-integrated-final.yml' 为 'ci-cd.yml'")
        
        next_steps.append("2. 安装和配置 GitHub CLI")
        next_steps.append("3. 应用分支保护规则")
        next_steps.append("4. 设置 GitHub 环境密钥")
        next_steps.append("5. 配置团队和权限")
        next_steps.append("6. 运行测试部署")
        next_steps.append("7. 监控和优化性能")
        
        self.results["next_steps"] = next_steps
    
    def print_report(self):
        """打印报告"""
        print("\n" + "=" * 60)
        print("Deployment Readiness Report")
        print("=" * 60)
        
        overall = self.results["overall"]
        status = "[READY]" if overall["ready"] else "[NOT READY]"
        
        print(f"\nOverall Status: {status}")
        print(f"Checks Passed: {overall['checks_passed']}/{overall['checks_total']}")
        
        print("\nDetailed Check Results:")
        print("-" * 60)
        
        for check in self.results["checks"]:
            status_icon = "[PASS]" if check["passed"] else "[FAIL]"
            print(f"\n{status_icon} {check['name']}")
            print(f"   {check['message']}")
        
        if self.results["warnings"]:
            print("\n[WARNING] Warnings:")
            for warning in self.results["warnings"]:
                print(f"  * {warning}")
        
        print("\n" + "=" * 60)
        
        if overall["ready"]:
            print("[SUCCESS] All checks passed! System is ready for deployment.")
        else:
            print("[FAILED] Some checks failed, please fix issues first.")
        
        # 生成下一步建议
        self.generate_next_steps()
        
        print("\nNext Steps:")
        print("-" * 60)
        for step in self.results["next_steps"]:
            print(f"  {step}")
        
        print("\n" + "=" * 60)
        
        # 保存报告
        self.save_report()
    
    def save_report(self):
        """保存报告到文件"""
        report_file = f"deployment-readiness-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"Report saved: {report_file}")
        except Exception as e:
            print(f"保存报告失败: {e}")

def main():
    """主函数"""
    verifier = DeploymentVerifier()
    results = verifier.run_all_checks()
    verifier.print_report()
    
    # 退出代码
    sys.exit(0 if results["overall"]["ready"] else 1)

if __name__ == "__main__":
    main()