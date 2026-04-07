#!/usr/bin/env python3
"""
检查 GitHub CLI 安装状态
"""

import subprocess
import sys

def check_gh_installation():
    """检查 GitHub CLI 是否安装"""
    print("检查 GitHub CLI 安装状态...")
    print("=" * 50)
    
    try:
        # 尝试运行 gh --version
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("[OK] GitHub CLI installed")
            print(f"Version:\n{result.stdout}")
            return True
        else:
            print("[ERROR] GitHub CLI installation issue")
            return False
            
    except FileNotFoundError:
        print("[ERROR] GitHub CLI not installed")
        return False
    except subprocess.TimeoutExpired:
        print("[WARNING] Check timeout, may be installing")
        return False
    except Exception as e:
        print(f"[ERROR] Check failed: {e}")
        return False

def check_gh_authentication():
    """检查 GitHub CLI 认证状态"""
    print("\n检查 GitHub CLI 认证状态...")
    
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            if "Logged in to github.com" in result.stdout:
                print("[OK] GitHub CLI 已认证")
                # 提取用户名
                for line in result.stdout.split('\n'):
                    if "Logged in to github.com as" in line:
                        username = line.split("as ")[1].split(" ")[0]
                        print(f"   用户名: {username}")
                        return True, username
            else:
                print("[FAIL] GitHub CLI 未认证")
                return False, None
        else:
            print("[FAIL] 认证检查失败")
            return False, None
            
    except Exception as e:
        print(f"[FAIL] 认证检查时出错: {e}")
        return False, None

def provide_installation_instructions():
    """提供安装指南"""
    print("\n" + "=" * 50)
    print("GitHub CLI 安装指南")
    print("=" * 50)
    
    print("\n请选择安装方法:")
    print("1. 使用 winget (推荐 - Windows)")
    print("2. 使用 Chocolatey (Windows)")
    print("3. 手动下载安装")
    print("4. 使用 Scoop (Windows)")
    
    print("\n方法 1: 使用 winget")
    print("  ```powershell")
    print("  # 以管理员身份运行 PowerShell")
    print("  winget install --id GitHub.cli")
    print("  ```")
    
    print("\n方法 2: 使用 Chocolatey")
    print("  ```powershell")
    print("  # 以管理员身份运行 PowerShell")
    print("  choco install gh -y")
    print("  ```")
    
    print("\n方法 3: 手动下载")
    print("  1. 访问: https://github.com/cli/cli/releases")
    print("  2. 下载 gh_*_windows_amd64.msi")
    print("  3. 运行安装程序")
    print("  4. 重启终端")
    
    print("\n安装后，请运行认证:")
    print("  ```bash")
    print("  gh auth login")
    print("  ```")

def provide_next_steps(is_installed, is_authenticated, username=None):
    """提供下一步指导"""
    print("\n" + "=" * 50)
    print("下一步操作")
    print("=" * 50)
    
    if not is_installed:
        print("[FAIL] 请先安装 GitHub CLI")
        provide_installation_instructions()
        return
    
    if not is_authenticated:
        print("[WARN]️  GitHub CLI 已安装但未认证")
        print("\n请运行认证:")
        print("  ```bash")
        print("  gh auth login")
        print("  ```")
        print("\n按照提示完成认证流程")
        return
    
    # 已安装并认证
    print("[OK] GitHub CLI 已安装并认证")
    print(f"   用户名: {username}")
    
    print("\n现在可以执行部署步骤:")
    print("1. 应用分支保护规则")
    print("   ```bash")
    print("   # 设置变量")
    print("   OWNER=\"your-github-username\"")
    print("   REPO=\"pythoncode\"")
    print("   ```")
    
    print("\n2. 设置环境密钥")
    print("   ```bash")
    print("   gh secret set DOCKER_USERNAME --repo $OWNER/$REPO --body \"yourdockeruser\"")
    print("   ```")
    
    print("\n3. 配置团队和权限")
    print("   ```bash")
    print("   gh api --method POST /orgs/$ORG/teams \\")
    print("     -f '{\"name\":\"backend-team\",\"description\":\"Backend team\",\"privacy\":\"closed\"}'")
    print("   ```")
    
    print("\n4. 运行测试部署")
    print("   ```bash")
    print("   gh workflow run \".github/workflows/ci-cd-integrated-final.yml\" --ref develop")
    print("   ```")
    
    print("\n详细指南请查看:")
    print("  - scripts/deploy_branch_protection.md")
    print("  - scripts/setup_environment_secrets.md")
    print("  - scripts/setup_teams_permissions.md")
    print("  - scripts/test_deployment_guide.md")

def main():
    """主函数"""
    print("GitHub CLI 状态检查")
    print("=" * 60)
    
    # 检查安装
    is_installed = check_gh_installation()
    
    # 检查认证
    is_authenticated = False
    username = None
    if is_installed:
        is_authenticated, username = check_gh_authentication()
    
    # 提供指导
    provide_next_steps(is_installed, is_authenticated, username)
    
    # 退出代码
    if is_installed and is_authenticated:
        print("\n[OK] 系统准备就绪，可以开始部署")
        sys.exit(0)
    else:
        print("\n[FAIL] 请先完成 GitHub CLI 安装和认证")
        sys.exit(1)

if __name__ == "__main__":
    main()