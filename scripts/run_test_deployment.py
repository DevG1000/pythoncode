#!/usr/bin/env python3
"""
测试部署脚本
运行完整的 CI/CD 管道测试
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime
from pathlib import Path

class TestDeployment:
    """运行测试部署"""
    
    def __init__(self):
        self.test_branch = f"test/deployment-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.report_file = f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        self.start_time = None
        self.workflow_run_id = None
        
    def check_prerequisites(self):
        """检查前提条件"""
        print("检查前提条件...")
        
        # 检查 git
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            print("[OK] Git 已安装")
        except:
            print("✗ Git 未安装")
            return False
        
        # 检查是否在 git 仓库中
        try:
            subprocess.run(["git", "status"], check=True, capture_output=True)
            print("[OK] 在 git 仓库中")
        except:
            print("✗ 不在 git 仓库中")
            return False
        
        # 检查 GitHub CLI
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("[OK] GitHub CLI 已安装")
            else:
                print("✗ GitHub CLI 未安装")
                return False
        except:
            print("✗ GitHub CLI 未安装")
            return False
        
        # 检查认证状态
        try:
            result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
            if "Logged in to github.com" in result.stdout:
                print("[OK] GitHub 已认证")
            else:
                print("✗ GitHub 未认证")
                return False
        except:
            print("✗ 无法检查认证状态")
            return False
        
        return True
    
    def create_test_branch(self):
        """创建测试分支"""
        print(f"\n创建测试分支: {self.test_branch}")
        
        try:
            # 确保在 develop 分支
            subprocess.run(["git", "checkout", "develop"], check=True, capture_output=True)
            
            # 拉取最新代码
            subprocess.run(["git", "pull", "origin", "develop"], check=True, capture_output=True)
            
            # 创建测试分支
            subprocess.run(["git", "checkout", "-b", self.test_branch], check=True, capture_output=True)
            
            # 创建测试文件
            test_content = f"""# Test Deployment {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated test deployment to verify the CI/CD pipeline.

## Test Details
- Branch: {self.test_branch}
- Timestamp: {datetime.now().isoformat()}
- Purpose: Validate complete pipeline functionality
- Tests: Quality gates, security scans, tests, build, deployment

## Changes
- Added this test file
- No functional changes to codebase

## Verification Checklist
- [ ] Quality gates assessment passes
- [ ] All tests pass
- [ ] Docker build succeeds
- [ ] Deployment to staging succeeds
- [ ] Smoke tests pass
"""
            
            with open("TEST_DEPLOYMENT.md", "w", encoding="utf-8") as f:
                f.write(test_content)
            
            # 提交更改
            subprocess.run(["git", "add", "TEST_DEPLOYMENT.md"], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"test: Automated deployment test {datetime.now().strftime('%Y%m%d')}"], 
                         check=True, capture_output=True)
            
            # 推送到远程
            subprocess.run(["git", "push", "origin", self.test_branch], check=True, capture_output=True)
            
            print("[OK] 测试分支创建成功")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ 创建测试分支失败: {e}")
            return False
    
    def trigger_workflow(self):
        """触发工作流"""
        print("\n触发 CI/CD 工作流...")
        
        try:
            # 触发工作流
            cmd = [
                "gh", "workflow", "run", ".github/workflows/ci-cd-integrated-final.yml",
                "--ref", self.test_branch,
                "--json", "id"
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            data = json.loads(result.stdout)
            self.workflow_run_id = str(data["id"])
            
            print(f"[OK] 工作流已触发: {self.workflow_run_id}")
            print(f"   查看进度: https://github.com/{self.get_repo_path()}/actions/runs/{self.workflow_run_id}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ 触发工作流失败: {e}")
            return False
    
    def get_repo_path(self):
        """获取仓库路径"""
        try:
            result = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner"], 
                                  capture_output=True, text=True)
            data = json.loads(result.stdout)
            return data["nameWithOwner"]
        except:
            return "OWNER/REPO"
    
    def monitor_workflow(self):
        """监控工作流执行"""
        print("\n监控工作流执行...")
        print("按 Ctrl+C 停止监控")
        
        self.start_time = time.time()
        
        try:
            while True:
                # 获取工作流状态
                cmd = ["gh", "run", "view", self.workflow_run_id, "--json", "status,conclusion"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    status = data.get("status", "unknown")
                    conclusion = data.get("conclusion", "none")
                    
                    elapsed = int(time.time() - self.start_time)
                    print(f"状态: {status}, 结论: {conclusion}, 运行时间: {elapsed}秒")
                    
                    if status == "completed":
                        if conclusion == "success":
                            print("\n[OK] 测试部署成功!")
                            return True
                        else:
                            print("\n[FAIL] 测试部署失败!")
                            self.show_failed_jobs()
                            return False
                
                time.sleep(30)  # 每30秒检查一次
                
        except KeyboardInterrupt:
            print("\n监控已停止")
            print(f"工作流仍在运行: {self.workflow_run_id}")
            return None
    
    def show_failed_jobs(self):
        """显示失败的作业"""
        print("\n失败的作业:")
        try:
            cmd = ["gh", "run", "view", self.workflow_run_id, "--json", "jobs"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            
            for job in data.get("jobs", []):
                if job.get("conclusion") == "failure":
                    print(f"  - {job.get('name')} (ID: {job.get('databaseId')})")
                    print(f"    开始时间: {job.get('startedAt')}")
                    print(f"    结束时间: {job.get('completedAt')}")
                    
                    # 获取作业日志
                    job_id = job.get('databaseId')
                    log_cmd = ["gh", "run", "view", self.workflow_run_id, "--log", "--job", str(job_id)]
                    log_result = subprocess.run(log_cmd, capture_output=True, text=True)
                    
                    # 显示最后10行日志
                    lines = log_result.stdout.strip().split('\n')
                    print("    最后日志:")
                    for line in lines[-10:]:
                        print(f"      {line}")
                    print()
                    
        except Exception as e:
            print(f"无法获取作业详情: {e}")
    
    def generate_report(self, success):
        """生成测试报告"""
        print(f"\n生成测试报告: {self.report_file}")
        
        try:
            with open(self.report_file, "w", encoding="utf-8") as f:
                f.write(f"# CI/CD 管道测试报告\n\n")
                f.write(f"## 测试信息\n")
                f.write(f"- **测试日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- **测试分支**: {self.test_branch}\n")
                f.write(f"- **工作流运行**: {self.workflow_run_id}\n")
                f.write(f"- **测试结果**: {'[OK] 成功' if success else '[FAIL] 失败'}\n")
                
                if self.start_time:
                    duration = int(time.time() - self.start_time)
                    f.write(f"- **总耗时**: {duration} 秒 ({duration//60} 分钟 {duration%60} 秒)\n")
                
                f.write(f"\n## 工作流详情\n")
                
                # 获取工作流详情
                cmd = ["gh", "run", "view", self.workflow_run_id, "--json", "name,headBranch,headSha,createdAt,updatedAt"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for key, value in data.items():
                        f.write(f"- **{key}**: {value}\n")
                
                f.write(f"\n## 作业结果\n")
                
                # 获取作业结果
                cmd = ["gh", "run", "view", self.workflow_run_id, "--json", "jobs"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for job in data.get("jobs", []):
                        name = job.get("name", "Unknown")
                        status = job.get("status", "unknown")
                        conclusion = job.get("conclusion", "none")
                        started = job.get("startedAt", "")
                        completed = job.get("completedAt", "")
                        
                        f.write(f"\n### {name}\n")
                        f.write(f"- 状态: {status}\n")
                        f.write(f"- 结论: {conclusion}\n")
                        if started and completed:
                            f.write(f"- 开始时间: {started}\n")
                            f.write(f"- 结束时间: {completed}\n")
                
                f.write(f"\n## 下一步\n")
                if success:
                    f.write(f"1. 测试通过，可以合并到 develop 分支\n")
                    f.write(f"2. 清理测试分支: `git branch -D {self.test_branch}`\n")
                    f.write(f"3. 删除远程分支: `git push origin --delete {self.test_branch}`\n")
                    f.write(f"4. 准备生产部署\n")
                else:
                    f.write(f"1. 检查失败原因\n")
                    f.write(f"2. 修复问题\n")
                    f.write(f"3. 重新运行测试\n")
                    f.write(f"4. 更新配置或代码\n")
                
                f.write(f"\n## 链接\n")
                f.write(f"- 工作流运行: https://github.com/{self.get_repo_path()}/actions/runs/{self.workflow_run_id}\n")
                f.write(f"- 测试分支: https://github.com/{self.get_repo_path()}/tree/{self.test_branch}\n")
            
            print(f"[OK] 报告已生成: {self.report_file}")
            
        except Exception as e:
            print(f"✗ 生成报告失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        print("\n清理资源...")
        
        # 切换回 develop 分支
        try:
            subprocess.run(["git", "checkout", "develop"], check=True, capture_output=True)
            print("[OK] 已切换回 develop 分支")
        except:
            print("✗ 无法切换分支")
        
        # 询问是否删除测试分支
        response = input(f"\n是否删除测试分支 '{self.test_branch}'? (y/n): ").strip().lower()
        if response == 'y':
            try:
                # 删除本地分支
                subprocess.run(["git", "branch", "-D", self.test_branch], check=True, capture_output=True)
                print("[OK] 本地分支已删除")
                
                # 删除远程分支
                subprocess.run(["git", "push", "origin", "--delete", self.test_branch], check=True, capture_output=True)
                print("[OK] 远程分支已删除")
                
            except subprocess.CalledProcessError as e:
                print(f"✗ 删除分支失败: {e}")
        else:
            print("测试分支保留")
    
    def run(self):
        """运行完整测试"""
        print("=" * 60)
        print("CI/CD 管道测试部署")
        print("=" * 60)
        
        # 检查前提条件
        if not self.check_prerequisites():
            print("\n[FAIL] 前提条件检查失败")
            return False
        
        # 创建测试分支
        if not self.create_test_branch():
            return False
        
        # 触发工作流
        if not self.trigger_workflow():
            return False
        
        # 监控工作流
        result = self.monitor_workflow()
        if result is None:
            print("测试被用户中断")
            return False
        
        # 生成报告
        self.generate_report(result)
        
        # 清理
        self.cleanup()
        
        return result

def main():
    """主函数"""
    tester = TestDeployment()
    
    try:
        success = tester.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()