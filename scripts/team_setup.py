#!/usr/bin/env python3
"""
PythonCode 团队快速设置脚本
用于快速配置团队协作环境
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Any


class TeamSetup:
    """团队设置工具类"""
    
    def __init__(self, config_path: str = ".github/TEAM_CONFIG.yml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.project_root = Path.cwd()
        
    def load_config(self) -> Dict[str, Any]:
        """加载团队配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"错误: 配置文件 {self.config_path} 不存在")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"错误: 配置文件格式错误: {e}")
            sys.exit(1)
    
    def print_banner(self):
        """打印团队设置横幅"""
        banner = """
        ╔══════════════════════════════════════════════════════╗
        ║               PythonCode 团队设置工具                ║
        ║                版本: 1.0 | 2026-03-26                ║
        ╚══════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_prerequisites(self):
        """检查前置条件"""
        print("检查前置条件...")
        
        prerequisites = {
            "Python 3.9+": self.check_python_version(),
            "Git": self.check_git_installed(),
            "Docker": self.check_docker_installed(),
            "项目目录": self.check_project_structure(),
        }
        
        all_ok = True
        for name, status in prerequisites.items():
            if status:
                print(f"  [OK] {name}")
            else:
                print(f"  [FAIL] {name}")
                all_ok = False
        
        return all_ok
    
    def check_python_version(self) -> bool:
        """检查Python版本"""
        try:
            version = sys.version_info
            return version.major == 3 and version.minor >= 9
        except:
            return False
    
    def check_git_installed(self) -> bool:
        """检查Git是否安装"""
        try:
            subprocess.run(["git", "--version"], 
                          capture_output=True, 
                          check=True)
            return True
        except:
            return False
    
    def check_docker_installed(self) -> bool:
        """检查Docker是否安装"""
        try:
            subprocess.run(["docker", "--version"], 
                          capture_output=True, 
                          check=True)
            return True
        except:
            return False
    
    def check_project_structure(self) -> bool:
        """检查项目结构"""
        required_dirs = ["api", "command_system", "card_generator", "tests"]
        for dir_name in required_dirs:
            if not (self.project_root / dir_name).exists():
                return False
        return True
    
    def setup_development_environment(self):
        """设置开发环境"""
        print("\n设置开发环境...")
        
        # 创建虚拟环境
        print("1. 创建Python虚拟环境...")
        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            subprocess.run([sys.executable, "-m", "venv", "venv"])
            print("  ✓ 虚拟环境创建成功")
        else:
            print("  ✓ 虚拟环境已存在")
        
        # 安装依赖
        print("2. 安装项目依赖...")
        requirements_files = ["requirements.txt", "requirements-dev.txt"]
        for req_file in requirements_files:
            if (self.project_root / req_file).exists():
                pip_cmd = [
                    str(self.project_root / "venv" / "Scripts" / "python"),
                    "-m", "pip", "install", "-r", req_file
                ] if os.name == "nt" else [
                    str(self.project_root / "venv" / "bin" / "python"),
                    "-m", "pip", "install", "-r", req_file
                ]
                
                try:
                    subprocess.run(pip_cmd, check=True)
                    print(f"  [OK] 安装 {req_file} 成功")
                except subprocess.CalledProcessError:
                    print(f"  [FAIL] 安装 {req_file} 失败")
    
    def setup_git_hooks(self):
        """设置Git钩子"""
        print("\n设置Git钩子...")
        
        git_hooks_dir = self.project_root / ".git" / "hooks"
        if not git_hooks_dir.exists():
            git_hooks_dir.mkdir(parents=True)
        
        # 创建pre-commit钩子
        pre_commit_content = """#!/bin/bash
# PythonCode项目预提交钩子

echo "运行代码检查..."

# 运行black检查
python -m black --check .

# 运行isort检查
python -m isort --check-only .

# 运行flake8检查
python -m flake8 .

# 运行mypy类型检查
python -m mypy .

# 运行pytest测试
python -m pytest tests/ -m "not slow"

echo "代码检查完成"
"""
        
        pre_commit_path = git_hooks_dir / "pre-commit"
        with open(pre_commit_path, 'w', encoding='utf-8') as f:
            f.write(pre_commit_content)
        
        # 设置执行权限
        if os.name != "nt":  # Unix-like系统
            pre_commit_path.chmod(0o755)
        
        print("  ✓ Git钩子设置完成")
    
    def setup_vscode_settings(self):
        """设置VS Code工作区配置"""
        print("\n设置VS Code工作区配置...")
        
        vscode_dir = self.project_root / ".vscode"
        if not vscode_dir.exists():
            vscode_dir.mkdir()
        
        # 设置文件
        settings = {
            "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe" if os.name == "nt" else "${workspaceFolder}/venv/bin/python",
            "python.linting.enabled": True,
            "python.linting.flake8Enabled": True,
            "python.formatting.provider": "black",
            "python.sortImports.args": ["--profile", "black"],
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            },
            "files.exclude": {
                "**/__pycache__": True,
                "**/.pytest_cache": True,
                "**/.mypy_cache": True,
                "**/.coverage": True,
                "**/htmlcov": True
            }
        }
        
        settings_path = vscode_dir / "settings.json"
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        
        # 扩展推荐
        extensions = {
            "recommendations": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.black-formatter",
                "ms-python.isort",
                "eamodio.gitlens",
                "ms-azuretools.vscode-docker",
                "humao.rest-client"
            ]
        }
        
        extensions_path = vscode_dir / "extensions.json"
        with open(extensions_path, 'w', encoding='utf-8') as f:
            json.dump(extensions, f, indent=2)
        
        print("  ✓ VS Code配置设置完成")
    
    def setup_docker_environment(self):
        """设置Docker环境"""
        print("\n设置Docker环境...")
        
        # 检查docker-compose文件
        compose_files = ["docker-compose.yml", "docker-compose.dev.yml"]
        for file in compose_files:
            if (self.project_root / file).exists():
                print(f"  ✓ {file} 已存在")
            else:
                print(f"  ⚠ {file} 不存在，请手动创建")
    
    def generate_team_report(self):
        """生成团队设置报告"""
        print("\n生成团队设置报告...")
        
        report = {
            "project": self.config.get("project", "PythonCode"),
            "version": self.config.get("version", "1.0"),
            "team_size": sum(role.get("count", 0) for role in self.config.get("roles", {}).values()),
            "roles": {name: role.get("count", 0) for name, role in self.config.get("roles", {}).items()},
            "tools": self.config.get("tools", {}),
            "setup_completed": True,
            "timestamp": "2026-03-26"
        }
        
        report_path = self.project_root / "team_setup_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"  ✓ 团队报告已生成: {report_path}")
        
        # 打印摘要
        print("\n" + "="*50)
        print("团队设置摘要")
        print("="*50)
        print(f"项目: {report['project']}")
        print(f"版本: {report['version']}")
        print(f"团队规模: {report['team_size']} 人")
        print("\n角色分配:")
        for role, count in report['roles'].items():
            print(f"  {role}: {count} 人")
        print("\n主要工具:")
        for category, tools in report['tools'].items():
            print(f"  {category}: {', '.join(tools.keys())}")
        print("="*50)
    
    def setup_github_actions(self):
        """设置GitHub Actions工作流"""
        print("\n设置GitHub Actions工作流...")
        
        workflows_dir = self.project_root / ".github" / "workflows"
        if not workflows_dir.exists():
            workflows_dir.mkdir(parents=True)
        
        # CI工作流
        ci_workflow = """name: PythonCode CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
      - name: Run black
        run: black --check .
      - name: Run isort
        run: isort --check-only .
      - name: Run flake8
        run: flake8 .
      - name: Run mypy
        run: mypy .

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run bandit
        run: bandit -r .
      - name: Run safety
        run: safety check
"""
        
        ci_path = workflows_dir / "ci.yml"
        with open(ci_path, 'w', encoding='utf-8') as f:
            f.write(ci_workflow)
        
        print("  ✓ GitHub Actions工作流设置完成")
    
    def run(self):
        """运行团队设置"""
        self.print_banner()
        
        # 检查前置条件
        if not self.check_prerequisites():
            print("\n错误: 前置条件检查失败，请解决上述问题后重试")
            sys.exit(1)
        
        # 设置步骤
        steps = [
            ("设置开发环境", self.setup_development_environment),
            ("设置Git钩子", self.setup_git_hooks),
            ("设置VS Code配置", self.setup_vscode_settings),
            ("设置Docker环境", self.setup_docker_environment),
            ("设置GitHub Actions", self.setup_github_actions),
            ("生成团队报告", self.generate_team_report),
        ]
        
        for step_name, step_func in steps:
            try:
                step_func()
            except Exception as e:
                print(f"  ✗ {step_name} 失败: {e}")
        
        print("\n" + "="*50)
        print("团队设置完成！")
        print("="*50)
        print("\n下一步:")
        print("1. 激活虚拟环境:")
        print("   Windows: venv\\Scripts\\activate")
        print("   Linux/Mac: source venv/bin/activate")
        print("2. 运行测试: pytest")
        print("3. 启动开发服务: docker-compose up -d")
        print("4. 查看团队文档:")
        print("   - TEAM_STRUCTURE.md (团队结构)")
        print("   - ROLE_DETAILS.md (角色职责)")
        print("   - TEAM_WORKFLOW.md (工作流程)")
        print("="*50)


def main():
    """主函数"""
    setup = TeamSetup()
    setup.run()


if __name__ == "__main__":
    main()