#!/usr/bin/env python3
"""
安全修复脚本
用于自动修复安全检查发现的问题
"""

import logging
import os
import re
import sys
from typing import Any, Dict, List

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SecurityFixer:
    """安全修复器"""

    def __init__(self):
        """初始化修复器"""
        self.fixes_applied = []

    def fix_hardcoded_secrets(self) -> bool:
        """修复硬编码的密钥"""
        env_file = ".env"
        if not os.path.exists(env_file):
            logger.warning(f"未找到 {env_file} 文件")
            return False

        try:
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 需要修复的密钥模式
            secret_patterns = {
                "SECRET_KEY=": "SECRET_KEY=${SECRET_KEY}",
                "MAIL_PASSWORD=": "MAIL_PASSWORD=${MAIL_PASSWORD}",
                "MAIL_PASSWORD=": "MAIL_PASSWORD=${MAIL_PASSWORD}",
            }

            changes_made = False
            new_lines = []

            for line in content.split("\n"):
                original_line = line
                for pattern, replacement in secret_patterns.items():
                    if pattern in line:
                        # 检查是否已经是占位符
                        value = line.split("=", 1)[1].strip() if "=" in line else ""
                        if value and value not in ["", "changeme", "your-secret-key", "your-password"]:
                            # 替换为占位符
                            line = replacement
                            changes_made = True
                            logger.info(f"修复硬编码密钥: {pattern}")

                new_lines.append(line)

            if changes_made:
                # 备份原文件
                backup_file = f"{env_file}.backup"
                with open(backup_file, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"已创建备份: {backup_file}")

                # 写入修复后的文件
                with open(env_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines))

                self.fixes_applied.append(
                    {"type": "hardcoded_secrets", "description": "修复硬编码的密钥", "details": "将硬编码的密钥替换为占位符"}
                )
                return True
            else:
                logger.info("未发现需要修复的硬编码密钥")
                return False

        except Exception as e:
            logger.error(f"修复硬编码密钥失败: {e}")
            return False

    def fix_flask_environment(self) -> bool:
        """修复Flask环境配置"""
        env_file = ".env"
        if not os.path.exists(env_file):
            logger.warning(f"未找到 {env_file} 文件")
            return False

        try:
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()

            changes_made = False
            new_lines = []

            for line in content.split("\n"):
                original_line = line

                # 修复FLASK_ENV
                if line.strip().startswith("FLASK_ENV="):
                    current_value = line.split("=", 1)[1].strip() if "=" in line else ""
                    if current_value.lower() != "production":
                        line = "FLASK_ENV=production"
                        changes_made = True
                        logger.info(f"修复FLASK_ENV: {current_value} -> production")

                # 修复FLASK_DEBUG
                elif line.strip().startswith("FLASK_DEBUG="):
                    current_value = line.split("=", 1)[1].strip() if "=" in line else ""
                    if current_value not in ["0", "false", "False"]:
                        line = "FLASK_DEBUG=0"
                        changes_made = True
                        logger.info(f"修复FLASK_DEBUG: {current_value} -> 0")

                # 添加缺失的安全配置
                new_lines.append(line)

            # 添加缺失的安全配置
            security_configs = [
                "# Security Configuration",
                "SESSION_COOKIE_SECURE=true",
                "SESSION_COOKIE_HTTPONLY=true",
                "SESSION_COOKIE_SAMESITE=Lax",
                "PERMANENT_SESSION_LIFETIME=900  # 15 minutes",
            ]

            # 检查是否已存在这些配置
            existing_configs = [line.strip() for line in new_lines]
            for config in security_configs:
                if config not in existing_configs and not any(config.split()[0] in line for line in existing_configs if line):
                    new_lines.append(config)
                    changes_made = True
                    logger.info(f"添加安全配置: {config}")

            if changes_made:
                # 备份原文件
                backup_file = f"{env_file}.backup.flask"
                with open(backup_file, "w", encoding="utf-8") as f:
                    f.write(content)

                # 写入修复后的文件
                with open(env_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines))

                self.fixes_applied.append(
                    {
                        "type": "flask_environment",
                        "description": "修复Flask环境配置",
                        "details": "设置生产环境配置和安全Cookie设置",
                    }
                )
                return True
            else:
                logger.info("Flask环境配置已正确")
                return False

        except Exception as e:
            logger.error(f"修复Flask环境配置失败: {e}")
            return False

    def fix_database_config(self) -> bool:
        """修复数据库配置"""
        env_file = ".env"
        if not os.path.exists(env_file):
            logger.warning(f"未找到 {env_file} 文件")
            return False

        try:
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()

            changes_made = False
            new_lines = []
            has_database_url = False

            for line in content.split("\n"):
                original_line = line

                # 检查数据库URL
                if line.strip().startswith("DATABASE_URL="):
                    has_database_url = True
                    current_value = line.split("=", 1)[1].strip() if "=" in line else ""

                    # 如果是SQLite，添加注释建议使用PostgreSQL
                    if "sqlite:///" in current_value:
                        line = f"{line}  # 生产环境建议使用PostgreSQL with SSL"
                        changes_made = True
                        logger.info("添加数据库SSL建议注释")

                new_lines.append(line)

            # 如果没有DATABASE_URL，添加一个
            if not has_database_url:
                new_lines.append("")
                new_lines.append("# Database Configuration")
                new_lines.append("# DATABASE_URL=postgresql://user:password@localhost/dbname?sslmode=require")
                changes_made = True
                logger.info("添加数据库配置示例")

            if changes_made:
                # 备份原文件
                backup_file = f"{env_file}.backup.db"
                with open(backup_file, "w", encoding="utf-8") as f:
                    f.write(content)

                # 写入修复后的文件
                with open(env_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines))

                self.fixes_applied.append(
                    {"type": "database_config", "description": "修复数据库配置", "details": "添加SSL建议和配置示例"}
                )
                return True
            else:
                logger.info("数据库配置已正确")
                return False

        except Exception as e:
            logger.error(f"修复数据库配置失败: {e}")
            return False

    def create_security_readme(self) -> bool:
        """创建安全README文件"""
        readme_file = "SECURITY_README.md"

        try:
            content = """# 安全配置指南

## 重要安全注意事项

### 1. 环境变量管理
- 所有敏感信息必须通过环境变量设置
- 不要将密钥、密码等硬编码在代码中
- 使用不同的密钥用于开发、测试和生产环境

### 2. 生产环境配置
- 设置 `FLASK_ENV=production`
- 设置 `FLASK_DEBUG=0`
- 启用HTTPS和安全的Cookie设置
- 配置适当的CORS策略

### 3. 数据库安全
- 生产环境使用PostgreSQL或MySQL
- 启用SSL/TLS加密连接
- 定期备份数据库
- 使用强密码和最小权限原则

### 4. 密钥管理
- 使用强随机密钥：`openssl rand -hex 32`
- 定期轮换密钥（建议每90天）
- 使用密钥管理服务（如AWS KMS、Hashicorp Vault）

### 5. 监控和日志
- 启用安全日志记录
- 监控异常登录尝试
- 设置告警规则
- 定期审计日志

### 6. 依赖安全
- 定期更新依赖包
- 使用安全漏洞扫描工具
- 固定依赖版本

## 快速安全检查

运行安全检查脚本：
```bash
python scripts/simple_security_check.py
```

## 紧急联系人

- 安全负责人: security@example.com
- 系统管理员: admin@example.com

## 安全策略

请参考 `docs/SECURITY_REQUIREMENTS.md` 获取完整的安全策略。
"""

            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"已创建安全README文件: {readme_file}")

            self.fixes_applied.append(
                {"type": "security_readme", "description": "创建安全README文件", "details": f"创建了 {readme_file} 文件"}
            )
            return True

        except Exception as e:
            logger.error(f"创建安全README文件失败: {e}")
            return False

    def create_gitignore_entries(self) -> bool:
        """添加安全相关的.gitignore条目"""
        gitignore_file = ".gitignore"

        try:
            # 读取现有的.gitignore内容
            if os.path.exists(gitignore_file):
                with open(gitignore_file, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                content = ""

            # 需要添加的安全相关条目
            security_entries = [
                "",
                "# Security related",
                ".env",
                "*.key",
                "*.pem",
                "*.crt",
                "*.pfx",
                "secrets/",
                "credentials.json",
                "service-account-key.json",
                "*.backup",
                "*.backup.*",
                "# Logs (should be monitored but not committed)",
                "logs/*.log",
                "!logs/.gitkeep",
            ]

            # 检查哪些条目已经存在
            existing_lines = content.split("\n")
            entries_to_add = []

            for entry in security_entries:
                if entry.strip() and entry not in existing_lines:
                    # 检查是否以注释形式存在
                    if not any(entry.lstrip("#").strip() in line for line in existing_lines):
                        entries_to_add.append(entry)

            if entries_to_add:
                # 添加新条目
                with open(gitignore_file, "a", encoding="utf-8") as f:
                    f.write("\n" + "\n".join(entries_to_add))

                logger.info(f"在 {gitignore_file} 中添加了 {len(entries_to_add)} 个安全相关条目")

                self.fixes_applied.append(
                    {
                        "type": "gitignore_entries",
                        "description": "添加安全相关的.gitignore条目",
                        "details": f"添加了 {len(entries_to_add)} 个条目到 .gitignore",
                    }
                )
                return True
            else:
                logger.info(".gitignore中已包含所有安全相关条目")
                return False

        except Exception as e:
            logger.error(f"更新.gitignore失败: {e}")
            return False

    def run_all_fixes(self) -> Dict[str, Any]:
        """运行所有修复"""
        logger.info("开始安全修复...")

        results = {
            "hardcoded_secrets": self.fix_hardcoded_secrets(),
            "flask_environment": self.fix_flask_environment(),
            "database_config": self.fix_database_config(),
            "security_readme": self.create_security_readme(),
            "gitignore_entries": self.create_gitignore_entries(),
        }

        total_fixes = len(results)
        successful_fixes = sum(1 for result in results.values() if result)

        report = {
            "timestamp": self._get_timestamp(),
            "total_fixes": total_fixes,
            "successful_fixes": successful_fixes,
            "fixes_applied": self.fixes_applied,
            "results": results,
        }

        return report

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime

        return datetime.now().isoformat()

    def print_report(self, report: Dict[str, Any]):
        """打印修复报告"""
        print("=" * 80)
        print("安全修复报告")
        print("=" * 80)
        print()

        print(f"生成时间: {report['timestamp']}")
        print(f"尝试修复: {report['total_fixes']}")
        print(f"成功修复: {report['successful_fixes']}")
        print()

        print("修复结果:")
        for fix_type, success in report["results"].items():
            status = "[成功]" if success else "[失败]"
            print(f"  {fix_type}: {status}")
        print()

        if report["fixes_applied"]:
            print("应用的修复:")
            for i, fix in enumerate(report["fixes_applied"], 1):
                print(f"  {i}. {fix['description']}")
                print(f"     详情: {fix['details']}")
            print()

        print("下一步:")
        print("  1. 检查修复后的配置文件")
        print("  2. 更新实际的生产环境密钥")
        print("  3. 重新运行安全检查: python scripts/simple_security_check.py")
        print("  4. 部署前确保所有安全检查通过")
        print()
        print("=" * 80)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="安全修复工具")
    parser.add_argument(
        "--fix",
        choices=["all", "secrets", "flask", "database", "readme", "gitignore"],
        default="all",
        help="指定要修复的问题类型",
    )

    args = parser.parse_args()

    # 创建修复器
    fixer = SecurityFixer()

    # 运行指定的修复
    if args.fix == "all":
        report = fixer.run_all_fixes()
    elif args.fix == "secrets":
        result = fixer.fix_hardcoded_secrets()
        report = {
            "timestamp": fixer._get_timestamp(),
            "total_fixes": 1,
            "successful_fixes": 1 if result else 0,
            "fixes_applied": fixer.fixes_applied,
            "results": {"hardcoded_secrets": result},
        }
    elif args.fix == "flask":
        result = fixer.fix_flask_environment()
        report = {
            "timestamp": fixer._get_timestamp(),
            "total_fixes": 1,
            "successful_fixes": 1 if result else 0,
            "fixes_applied": fixer.fixes_applied,
            "results": {"flask_environment": result},
        }
    elif args.fix == "database":
        result = fixer.fix_database_config()
        report = {
            "timestamp": fixer._get_timestamp(),
            "total_fixes": 1,
            "successful_fixes": 1 if result else 0,
            "fixes_applied": fixer.fixes_applied,
            "results": {"database_config": result},
        }
    elif args.fix == "readme":
        result = fixer.create_security_readme()
        report = {
            "timestamp": fixer._get_timestamp(),
            "total_fixes": 1,
            "successful_fixes": 1 if result else 0,
            "fixes_applied": fixer.fixes_applied,
            "results": {"security_readme": result},
        }
    elif args.fix == "gitignore":
        result = fixer.create_gitignore_entries()
        report = {
            "timestamp": fixer._get_timestamp(),
            "total_fixes": 1,
            "successful_fixes": 1 if result else 0,
            "fixes_applied": fixer.fixes_applied,
            "results": {"gitignore_entries": result},
        }

    # 打印报告
    fixer.print_report(report)

    # 根据修复结果返回退出码
    if report["successful_fixes"] > 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
