#!/usr/bin/env python3
"""
PythonCode 团队快速设置脚本（简化版）
用于快速配置团队协作环境
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def print_banner():
    """打印团队设置横幅"""
    print("=" * 60)
    print("PythonCode 团队设置工具")
    print("版本: 1.0 | 2026-03-26")
    print("=" * 60)


def check_prerequisites():
    """检查前置条件"""
    print("\n检查前置条件...")

    prerequisites = {
        "Python 3.9+": check_python_version(),
        "Git": check_git_installed(),
        "项目目录结构": check_project_structure(),
    }

    all_ok = True
    for name, status in prerequisites.items():
        if status:
            print(f"  [OK] {name}")
        else:
            print(f"  [FAIL] {name}")
            all_ok = False

    return all_ok


def check_python_version():
    """检查Python版本"""
    try:
        version = sys.version_info
        return version.major == 3 and version.minor >= 9
    except:
        return False


def check_git_installed():
    """检查Git是否安装"""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except:
        return False


def check_project_structure():
    """检查项目结构"""
    project_root = Path.cwd()
    required_dirs = ["api", "command_system", "card_generator", "tests"]
    for dir_name in required_dirs:
        if not (project_root / dir_name).exists():
            return False
    return True


def setup_development_environment():
    """设置开发环境"""
    print("\n设置开发环境...")

    project_root = Path.cwd()

    # 创建虚拟环境
    print("1. 创建Python虚拟环境...")
    venv_path = project_root / "venv"
    if not venv_path.exists():
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("  [OK] 虚拟环境创建成功")
    else:
        print("  [OK] 虚拟环境已存在")

    # 安装依赖
    print("2. 安装项目依赖...")
    requirements_files = ["requirements.txt", "requirements-dev.txt"]
    for req_file in requirements_files:
        if (project_root / req_file).exists():
            pip_cmd = (
                [str(project_root / "venv" / "Scripts" / "python"), "-m", "pip", "install", "-r", req_file]
                if os.name == "nt"
                else [str(project_root / "venv" / "bin" / "python"), "-m", "pip", "install", "-r", req_file]
            )

            try:
                subprocess.run(pip_cmd, check=True)
                print(f"  [OK] 安装 {req_file} 成功")
            except subprocess.CalledProcessError:
                print(f"  [FAIL] 安装 {req_file} 失败")


def generate_team_summary():
    """生成团队设置摘要"""
    print("\n生成团队设置摘要...")

    summary = {
        "project": "PythonCode",
        "version": "1.0",
        "team_structure": {
            "project_manager": 1,
            "solution_architect": 1,
            "business_analyst": 1,
            "backend_developer": 2,
            "frontend_developer": 1,
            "qa_engineer": 1,
            "devops_engineer": 1,
        },
        "total_team_size": 8,
        "setup_completed": True,
        "timestamp": "2026-03-26",
    }

    summary_path = Path.cwd() / "team_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"  [OK] 团队摘要已生成: {summary_path}")

    # 打印摘要
    print("\n" + "=" * 50)
    print("团队设置摘要")
    print("=" * 50)
    print(f"项目: {summary['project']}")
    print(f"版本: {summary['version']}")
    print(f"团队规模: {summary['total_team_size']} 人")
    print("\n角色分配:")
    for role, count in summary["team_structure"].items():
        role_name = role.replace("_", " ").title()
        print(f"  {role_name}: {count} 人")
    print("=" * 50)


def print_next_steps():
    """打印下一步操作"""
    print("\n" + "=" * 50)
    print("团队设置完成！")
    print("=" * 50)
    print("\n下一步操作:")
    print("1. 激活虚拟环境:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Linux/Mac: source venv/bin/activate")
    print("2. 运行测试验证环境:")
    print("   pytest tests/")
    print("3. 查看团队文档:")
    print("   - TEAM_STRUCTURE.md (团队组织结构)")
    print("   - ROLE_DETAILS.md (角色详细职责)")
    print("   - TEAM_WORKFLOW.md (团队工作流程)")
    print("   - .github/TEAM_CONFIG.yml (团队配置文件)")
    print("4. 设置开发工具:")
    print("   - 安装VS Code扩展: Python, GitLens, Docker")
    print("   - 配置代码格式化: Black, isort")
    print("   - 设置代码检查: flake8, mypy")
    print("=" * 50)


def main():
    """主函数"""
    print_banner()

    # 检查前置条件
    if not check_prerequisites():
        print("\n错误: 前置条件检查失败，请解决上述问题后重试")
        sys.exit(1)

    # 设置开发环境
    setup_development_environment()

    # 生成团队摘要
    generate_team_summary()

    # 打印下一步操作
    print_next_steps()


if __name__ == "__main__":
    main()
