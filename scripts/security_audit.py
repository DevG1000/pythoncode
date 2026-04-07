#!/usr/bin/env python3
"""
安全审计脚本
用于自动化安全配置检查和合规性验证
"""

import json
import logging
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import yaml

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Severity(Enum):
    """安全检查严重程度"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CheckStatus(Enum):
    """检查状态"""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class SecurityCheck:
    """安全检查项"""

    id: str
    description: str
    check: str
    command: str
    required: bool
    severity: Severity
    status: CheckStatus = CheckStatus.SKIPPED
    message: str = ""
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class AuditReport:
    """审计报告"""

    timestamp: str
    environment: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    skipped_checks: int
    checks: List[SecurityCheck]
    summary: Dict[str, Any]
    recommendations: List[str]


class SecurityAuditor:
    """安全审计器"""

    def __init__(self, config_path: str = "config/security-checklist.yaml"):
        """初始化审计器"""
        self.config_path = config_path
        self.checks: List[SecurityCheck] = []
        self.load_config()

    def load_config(self):
        """加载安全检查配置"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            for category, check_list in config.get("checks", {}).items():
                for check_data in check_list:
                    check = SecurityCheck(
                        id=check_data["id"],
                        description=check_data["description"],
                        check=check_data["check"],
                        command=check_data["command"],
                        required=check_data["required"],
                        severity=Severity(check_data["severity"]),
                    )
                    self.checks.append(check)

            logger.info(f"已加载 {len(self.checks)} 个安全检查项")

        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            sys.exit(1)

    def run_check(self, check: SecurityCheck) -> CheckStatus:
        """运行单个安全检查"""
        try:
            logger.info(f"运行检查: {check.id} - {check.description}")

            # 根据检查类型执行不同的验证
            if check.id.startswith("auth-"):
                return self._run_auth_check(check)
            elif check.id.startswith("data-"):
                return self._run_data_check(check)
            elif check.id.startswith("app-"):
                return self._run_app_check(check)
            elif check.id.startswith("net-"):
                return self._run_network_check(check)
            elif check.id.startswith("container-"):
                return self._run_container_check(check)
            elif check.id.startswith("monitor-"):
                return self._run_monitor_check(check)
            elif check.id.startswith("comp-"):
                return self._run_compliance_check(check)
            else:
                return self._run_generic_check(check)

        except Exception as e:
            logger.error(f"检查 {check.id} 执行失败: {e}")
            check.status = CheckStatus.FAILED
            check.message = f"执行异常: {str(e)}"
            return CheckStatus.FAILED

    def _run_auth_check(self, check: SecurityCheck) -> CheckStatus:
        """运行身份认证检查"""
        if check.id == "auth-001":
            # 检查密码策略
            from api.config import Config

            if hasattr(Config, "PASSWORD_MIN_LENGTH"):
                min_length = Config.PASSWORD_MIN_LENGTH
                if min_length >= 12:
                    check.status = CheckStatus.PASSED
                    check.message = f"密码最小长度配置正确: {min_length}字符"
                    return CheckStatus.PASSED
                else:
                    check.status = CheckStatus.FAILED
                    check.message = f"密码最小长度不足12字符: {min_length}字符"
                    return CheckStatus.FAILED
            else:
                check.status = CheckStatus.FAILED
                check.message = "未找到密码策略配置"
                return CheckStatus.FAILED

        elif check.id == "auth-002":
            # 检查会话超时
            from api.config import Config

            if hasattr(Config, "SESSION_TIMEOUT"):
                timeout = Config.SESSION_TIMEOUT
                if timeout <= 900:  # 15分钟 = 900秒
                    check.status = CheckStatus.PASSED
                    check.message = f"会话超时配置正确: {timeout}秒"
                    return CheckStatus.PASSED
                else:
                    check.status = CheckStatus.FAILED
                    check.message = f"会话超时过长: {timeout}秒"
                    return CheckStatus.FAILED
            else:
                check.status = CheckStatus.FAILED
                check.message = "未找到会话超时配置"
                return CheckStatus.FAILED

        return CheckStatus.SKIPPED

    def _run_data_check(self, check: SecurityCheck) -> CheckStatus:
        """运行数据安全检查"""
        if check.id == "data-001":
            # 检查数据库SSL
            db_url = os.getenv("DATABASE_URL", "")
            if "ssl=true" in db_url.lower() or "sslmode=require" in db_url.lower():
                check.status = CheckStatus.PASSED
                check.message = "数据库连接已启用SSL"
                return CheckStatus.PASSED
            else:
                check.status = CheckStatus.FAILED
                check.message = "数据库连接未启用SSL"
                return CheckStatus.FAILED

        elif check.id == "data-003":
            # 检查密钥存储
            env_file = ".env"
            if os.path.exists(env_file):
                with open(env_file, "r") as f:
                    content = f.read()
                    # 检查是否包含硬编码的密钥模式
                    hardcoded_patterns = ["SECRET_KEY=", "PASSWORD=", "API_KEY=", "TOKEN="]
                    for pattern in hardcoded_patterns:
                        if pattern in content:
                            # 检查值是否是示例或占位符
                            lines = content.split("\n")
                            for line in lines:
                                if pattern in line:
                                    value = line.split("=", 1)[1].strip()
                                    if not value or value in ["changeme", "your-secret-key", "placeholder"]:
                                        check.status = CheckStatus.WARNING
                                        check.message = f"发现占位符密钥: {pattern}"
                                        return CheckStatus.WARNING
                                    else:
                                        check.status = CheckStatus.FAILED
                                        check.message = f"发现硬编码密钥: {pattern}"
                                        return CheckStatus.FAILED

                    check.status = CheckStatus.PASSED
                    check.message = "未发现硬编码密钥"
                    return CheckStatus.PASSED
            else:
                check.status = CheckStatus.PASSED
                check.message = "未找到.env文件，可能使用环境变量"
                return CheckStatus.PASSED

        return CheckStatus.SKIPPED

    def _run_app_check(self, check: SecurityCheck) -> CheckStatus:
        """运行应用安全检查"""
        if check.id == "app-003":
            # 检查错误处理配置
            flask_env = os.getenv("FLASK_ENV", "development")
            if flask_env.lower() == "production":
                check.status = CheckStatus.PASSED
                check.message = f"运行环境配置正确: {flask_env}"
                return CheckStatus.PASSED
            else:
                check.status = CheckStatus.FAILED
                check.message = f"运行环境应为production，当前为: {flask_env}"
                return CheckStatus.FAILED

        return CheckStatus.SKIPPED

    def _run_network_check(self, check: SecurityCheck) -> CheckStatus:
        """运行网络安全检查"""
        if check.id == "net-001":
            # 检查开放端口
            try:
                result = subprocess.run(["netstat", "-tulpn"], capture_output=True, text=True, shell=True)

                open_ports = []
                for line in result.stdout.split("\n"):
                    if "LISTEN" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            address = parts[3]
                            open_ports.append(address)

                # 允许的端口
                allowed_ports = ["80", "443", "5000", "6379", "5432"]
                suspicious_ports = []

                for port_info in open_ports:
                    port = port_info.split(":")[-1]
                    if port not in allowed_ports and port.isdigit():
                        suspicious_ports.append(port)

                if not suspicious_ports:
                    check.status = CheckStatus.PASSED
                    check.message = "端口配置正确"
                    check.details = {"open_ports": open_ports}
                    return CheckStatus.PASSED
                else:
                    check.status = CheckStatus.FAILED
                    check.message = f"发现可疑开放端口: {suspicious_ports}"
                    check.details = {"open_ports": open_ports, "suspicious_ports": suspicious_ports}
                    return CheckStatus.FAILED

            except Exception as e:
                check.status = CheckStatus.WARNING
                check.message = f"端口检查失败: {str(e)}"
                return CheckStatus.WARNING

        return CheckStatus.SKIPPED

    def _run_container_check(self, check: SecurityCheck) -> CheckStatus:
        """运行容器安全检查"""
        if check.id == "container-001":
            # 检查容器用户
            try:
                result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)

                containers = result.stdout.strip().split("\n")
                if not containers:
                    check.status = CheckStatus.SKIPPED
                    check.message = "未找到运行中的容器"
                    return CheckStatus.SKIPPED

                non_root_containers = []
                root_containers = []

                for container in containers:
                    if container:
                        user_result = subprocess.run(
                            ["docker", "inspect", "--format", "{{.Config.User}}", container], capture_output=True, text=True
                        )
                        user = user_result.stdout.strip()
                        if user and user != "root" and user != "0":
                            non_root_containers.append(container)
                        else:
                            root_containers.append(container)

                if not root_containers:
                    check.status = CheckStatus.PASSED
                    check.message = "所有容器均以非root用户运行"
                    check.details = {"containers": non_root_containers}
                    return CheckStatus.PASSED
                else:
                    check.status = CheckStatus.FAILED
                    check.message = f"发现以root用户运行的容器: {root_containers}"
                    check.details = {"non_root_containers": non_root_containers, "root_containers": root_containers}
                    return CheckStatus.FAILED

            except Exception as e:
                check.status = CheckStatus.WARNING
                check.message = f"容器检查失败: {str(e)}"
                return CheckStatus.WARNING

        return CheckStatus.SKIPPED

    def _run_monitor_check(self, check: SecurityCheck) -> CheckStatus:
        """运行监控检查"""
        if check.id == "monitor-001":
            # 检查日志配置
            log_dir = "logs"
            if os.path.exists(log_dir):
                # 检查日志文件权限
                import stat

                for root, dirs, files in os.walk(log_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_stat = os.stat(file_path)
                        mode = stat.S_IMODE(file_stat.st_mode)

                        # 检查文件权限是否过于宽松
                        if mode & 0o777 == 0o777:  # rwxrwxrwx
                            check.status = CheckStatus.FAILED
                            check.message = f"发现权限过于宽松的日志文件: {file_path}"
                            check.details = {"file": file_path, "permissions": oct(mode)}
                            return CheckStatus.FAILED

                check.status = CheckStatus.PASSED
                check.message = "日志目录权限配置正确"
                return CheckStatus.PASSED
            else:
                check.status = CheckStatus.WARNING
                check.message = "日志目录不存在"
                return CheckStatus.WARNING

        return CheckStatus.SKIPPED

    def _run_compliance_check(self, check: SecurityCheck) -> CheckStatus:
        """运行合规性检查"""
        if check.id == "comp-001":
            # 检查数据保留策略
            from api.config import Config

            retention_configs = [
                ("USER_DATA_RETENTION_DAYS", 30, "用户数据保留"),
                ("LOG_RETENTION_DAYS", 180, "日志数据保留"),
                ("AUDIT_LOG_RETENTION_DAYS", 365, "审计日志保留"),
            ]

            missing_configs = []
            for config_name, min_days, description in retention_configs:
                if hasattr(Config, config_name):
                    days = getattr(Config, config_name)
                    if days < min_days:
                        check.status = CheckStatus.FAILED
                        check.message = f"{description}期限不足{min_days}天: {days}天"
                        return CheckStatus.FAILED
                else:
                    missing_configs.append(config_name)

            if missing_configs:
                check.status = CheckStatus.WARNING
                check.message = f"缺少数据保留配置: {missing_configs}"
                return CheckStatus.WARNING
            else:
                check.status = CheckStatus.PASSED
                check.message = "数据保留策略配置正确"
                return CheckStatus.PASSED

        return CheckStatus.SKIPPED

    def _run_generic_check(self, check: SecurityCheck) -> CheckStatus:
        """运行通用检查"""
        # 这里可以添加通用的检查逻辑
        check.status = CheckStatus.SKIPPED
        check.message = "未实现的具体检查逻辑"
        return CheckStatus.SKIPPED

    def run_all_checks(self) -> AuditReport:
        """运行所有安全检查"""
        logger.info("开始安全审计...")

        for check in self.checks:
            self.run_check(check)

        return self.generate_report()

    def generate_report(self) -> AuditReport:
        """生成审计报告"""
        total = len(self.checks)
        passed = sum(1 for c in self.checks if c.status == CheckStatus.PASSED)
        failed = sum(1 for c in self.checks if c.status == CheckStatus.FAILED)
        warning = sum(1 for c in self.checks if c.status == CheckStatus.WARNING)
        skipped = sum(1 for c in self.checks if c.status == CheckStatus.SKIPPED)

        # 按严重程度统计
        severity_stats = {}
        for severity in Severity:
            severity_checks = [c for c in self.checks if c.severity == severity]
            severity_passed = sum(1 for c in severity_checks if c.status == CheckStatus.PASSED)
            severity_stats[severity.value] = {
                "total": len(severity_checks),
                "passed": severity_passed,
                "passed_percentage": (severity_passed / len(severity_checks) * 100) if severity_checks else 0,
            }

        # 生成建议
        recommendations = []
        failed_critical = [c for c in self.checks if c.severity == Severity.CRITICAL and c.status == CheckStatus.FAILED]
        if failed_critical:
            recommendations.append("立即修复所有CRITICAL级别的失败检查")

        failed_high = [c for c in self.checks if c.severity == Severity.HIGH and c.status == CheckStatus.FAILED]
        if failed_high:
            recommendations.append("24小时内修复HIGH级别的失败检查")

        # 总体评估
        overall_status = "PASS" if failed == 0 else "FAIL"
        if failed_critical:
            overall_status = "CRITICAL_FAIL"

        report = AuditReport(
            timestamp=datetime.now().isoformat(),
            environment=os.getenv("FLASK_ENV", "unknown"),
            total_checks=total,
            passed_checks=passed,
            failed_checks=failed,
            warning_checks=warning,
            skipped_checks=skipped,
            checks=self.checks,
            summary={
                "overall_status": overall_status,
                "pass_percentage": (passed / total * 100) if total > 0 else 0,
                "severity_stats": severity_stats,
                "critical_failed": len(failed_critical),
                "high_failed": len(failed_high),
            },
            recommendations=recommendations,
        )

        return report

    def save_report(self, report: AuditReport, format: str = "json"):
        """保存审计报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"security-audit-report-{timestamp}"

        if format == "json":
            filename += ".json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(asdict(report), f, indent=2, ensure_ascii=False)
        elif format == "yaml":
            filename += ".yaml"
            with open(filename, "w", encoding="utf-8") as f:
                yaml.dump(asdict(report), f, default_flow_style=False, allow_unicode=True)
        else:
            filename += ".txt"
            self._save_text_report(report, filename)

        logger.info(f"审计报告已保存: {filename}")
        return filename

    def _save_text_report(self, report: AuditReport, filename: str):
        """保存文本格式报告"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("安全审计报告\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"生成时间: {report.timestamp}\n")
            f.write(f"环境: {report.environment}\n")
            f.write(f"总体状态: {report.summary['overall_status']}\n")
            f.write(f"通过率: {report.summary['pass_percentage']:.1f}%\n\n")

            f.write("检查结果统计:\n")
            f.write(f"  总计: {report.total_checks}\n")
            f.write(f"  通过: {report.passed_checks}\n")
            f.write(f"  失败: {report.failed_checks}\n")
            f.write(f"  警告: {report.warning_checks}\n")
            f.write(f"  跳过: {report.skipped_checks}\n\n")

            f.write("按严重程度统计:\n")
            for severity, stats in report.summary["severity_stats"].items():
                f.write(f"  {severity.upper()}: {stats['passed']}/{stats['total']} " f"({stats['passed_percentage']:.1f}%)\n")

            f.write("\n失败检查详情:\n")
            for check in report.checks:
                if check.status == CheckStatus.FAILED:
                    f.write(f"  [{check.severity.value.upper()}] {check.id}: {check.description}\n")
                    f.write(f"      原因: {check.message}\n")

            f.write("\n建议:\n")
            for i, rec in enumerate(report.recommendations, 1):
                f.write(f"  {i}. {rec}\n")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="安全审计工具")
    parser.add_argument("--config", default="config/security-checklist.yaml", help="安全检查配置文件路径")
    parser.add_argument("--format", choices=["json", "yaml", "text"], default="json", help="报告输出格式")
    parser.add_argument(
        "--severity", choices=["critical", "high", "medium", "low", "all"], default="all", help="检查严重程度过滤"
    )
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 创建审计器
    auditor = SecurityAuditor(args.config)

    # 按严重程度过滤
    if args.severity != "all":
        target_severity = Severity(args.severity)
        auditor.checks = [c for c in auditor.checks if c.severity == target_severity]

    # 运行审计
    report = auditor.run_all_checks()

    # 保存报告
    if args.output:
        filename = args.output
    else:
        filename = auditor.save_report(report, args.format)

    # 输出摘要
    print("\n安全审计完成!")
    print(f"总体状态: {report.summary['overall_status']}")
    print(f"通过率: {report.summary['pass_percentage']:.1f}%")
    print(f"报告文件: {filename}")

    # 如果有严重失败，返回非零退出码
    if report.summary["critical_failed"] > 0:
        sys.exit(1)
    elif report.summary["high_failed"] > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
