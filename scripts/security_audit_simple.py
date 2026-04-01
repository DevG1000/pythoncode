#!/usr/bin/env python3
"""
简化版安全审计脚本
不依赖外部YAML库，使用内置配置
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    required: bool
    severity: Severity
    status: CheckStatus = CheckStatus.SKIPPED
    message: str = ""
    details: Optional[Dict[str, Any]] = None
    
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
    
    def __init__(self):
        """初始化审计器"""
        self.checks: List[SecurityCheck] = []
        self.load_default_checks()
        
    def load_default_checks(self):
        """加载默认安全检查配置"""
        default_checks = [
            {
                'id': 'env-001',
                'description': '检查环境变量配置',
                'check': '检查FLASK_ENV是否为production',
                'required': True,
                'severity': Severity.CRITICAL
            },
            {
                'id': 'env-002',
                'description': '检查硬编码密钥',
                'check': '检查.env文件中是否有硬编码的密钥',
                'required': True,
                'severity': Severity.CRITICAL
            },
            {
                'id': 'app-001',
                'description': '检查应用安全配置',
                'check': '检查Flask安全配置',
                'required': True,
                'severity': Severity.HIGH
            },
            {
                'id': 'data-001',
                'description': '检查数据库安全',
                'check': '检查数据库连接是否使用SSL',
                'required': True,
                'severity': Severity.HIGH
            },
            {
                'id': 'net-001',
                'description': '检查网络端口',
                'check': '检查开放端口配置',
                'required': False,
                'severity': Severity.MEDIUM
            },
            {
                'id': 'file-001',
                'description': '检查文件权限',
                'check': '检查关键文件权限',
                'required': False,
                'severity': Severity.MEDIUM
            },
            {
                'id': 'log-001',
                'description': '检查日志配置',
                'check': '检查日志目录和权限',
                'required': False,
                'severity': Severity.LOW
            }
        ]
        
        for check_data in default_checks:
            check = SecurityCheck(
                id=check_data['id'],
                description=check_data['description'],
                check=check_data['check'],
                required=check_data['required'],
                severity=check_data['severity']
            )
            self.checks.append(check)
            
        logger.info(f"已加载 {len(self.checks)} 个安全检查项")
    
    def run_check(self, check: SecurityCheck) -> CheckStatus:
        """运行单个安全检查"""
        try:
            logger.info(f"运行检查: {check.id} - {check.description}")
            
            # 根据检查ID执行不同的验证
            if check.id == 'env-001':
                return self._run_env_check(check)
            elif check.id == 'env-002':
                return self._run_hardcoded_check(check)
            elif check.id == 'app-001':
                return self._run_app_check(check)
            elif check.id == 'data-001':
                return self._run_db_check(check)
            elif check.id == 'net-001':
                return self._run_network_check(check)
            elif check.id == 'file-001':
                return self._run_file_check(check)
            elif check.id == 'log-001':
                return self._run_log_check(check)
            else:
                check.status = CheckStatus.SKIPPED
                check.message = "未实现的具体检查逻辑"
                return CheckStatus.SKIPPED
                
        except Exception as e:
            logger.error(f"检查 {check.id} 执行失败: {e}")
            check.status = CheckStatus.FAILED
            check.message = f"执行异常: {str(e)}"
            return CheckStatus.FAILED
    
    def _run_env_check(self, check: SecurityCheck) -> CheckStatus:
        """检查环境变量配置"""
        flask_env = os.getenv('FLASK_ENV', 'development')
        if flask_env.lower() == 'production':
            check.status = CheckStatus.PASSED
            check.message = f"运行环境配置正确: {flask_env}"
            return CheckStatus.PASSED
        else:
            check.status = CheckStatus.FAILED
            check.message = f"运行环境应为production，当前为: {flask_env}"
            return CheckStatus.FAILED
    
    def _run_hardcoded_check(self, check: SecurityCheck) -> CheckStatus:
        """检查硬编码密钥"""
        env_file = '.env'
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含硬编码的密钥模式
                hardcoded_patterns = [
                    'SECRET_KEY=',
                    'PASSWORD=',
                    'API_KEY=',
                    'TOKEN='
                ]
                
                found_hardcoded = []
                found_placeholder = []
                
                for pattern in hardcoded_patterns:
                    if pattern in content:
                        lines = content.split('\n')
                        for line in lines:
                            if pattern in line:
                                value = line.split('=', 1)[1].strip()
                                if not value or value in ['changeme', 'your-secret-key', 'placeholder', '']:
                                    found_placeholder.append(pattern)
                                else:
                                    found_hardcoded.append(f"{pattern}{value[:10]}...")
                
                if found_hardcoded:
                    check.status = CheckStatus.FAILED
                    check.message = f"发现硬编码密钥: {', '.join(found_hardcoded)}"
                    check.details = {'hardcoded_keys': found_hardcoded}
                    return CheckStatus.FAILED
                elif found_placeholder:
                    check.status = CheckStatus.WARNING
                    check.message = f"发现占位符密钥: {', '.join(found_placeholder)}"
                    check.details = {'placeholder_keys': found_placeholder}
                    return CheckStatus.WARNING
                else:
                    check.status = CheckStatus.PASSED
                    check.message = "未发现硬编码密钥"
                    return CheckStatus.PASSED
                    
            except Exception as e:
                check.status = CheckStatus.WARNING
                check.message = f"读取.env文件失败: {str(e)}"
                return CheckStatus.WARNING
        else:
            check.status = CheckStatus.PASSED
            check.message = "未找到.env文件，可能使用环境变量"
            return CheckStatus.PASSED
    
    def _run_app_check(self, check: SecurityCheck) -> CheckStatus:
        """检查应用安全配置"""
        try:
            # 检查Flask配置
            from api.config import Config
            
            security_configs = [
                ('SECRET_KEY', '密钥配置'),
                ('SESSION_COOKIE_SECURE', '安全Cookie配置'),
                ('SESSION_COOKIE_HTTPONLY', 'HTTPOnly Cookie配置'),
                ('SESSION_COOKIE_SAMESITE', 'SameSite Cookie配置')
            ]
            
            missing_configs = []
            for config_name, description in security_configs:
                if not hasattr(Config, config_name):
                    missing_configs.append(description)
            
            if missing_configs:
                check.status = CheckStatus.FAILED
                check.message = f"缺少安全配置: {', '.join(missing_configs)}"
                return CheckStatus.FAILED
            else:
                check.status = CheckStatus.PASSED
                check.message = "应用安全配置完整"
                return CheckStatus.PASSED
                
        except ImportError:
            check.status = CheckStatus.WARNING
            check.message = "无法导入Config模块"
            return CheckStatus.WARNING
        except Exception as e:
            check.status = CheckStatus.WARNING
            check.message = f"检查应用配置失败: {str(e)}"
            return CheckStatus.WARNING
    
    def _run_db_check(self, check: SecurityCheck) -> CheckStatus:
        """检查数据库安全"""
        db_url = os.getenv('DATABASE_URL', '')
        if db_url:
            if 'ssl=true' in db_url.lower() or 'sslmode=require' in db_url.lower():
                check.status = CheckStatus.PASSED
                check.message = "数据库连接已启用SSL"
                return CheckStatus.PASSED
            else:
                check.status = CheckStatus.FAILED
                check.message = "数据库连接未启用SSL"
                check.details = {'db_url': db_url[:50] + '...' if len(db_url) > 50 else db_url}
                return CheckStatus.FAILED
        else:
            check.status = CheckStatus.WARNING
            check.message = "未配置DATABASE_URL环境变量"
            return CheckStatus.WARNING
    
    def _run_network_check(self, check: SecurityCheck) -> CheckStatus:
        """检查网络端口"""
        try:
            # 使用netstat检查开放端口
            result = subprocess.run(
                ['netstat', '-an'],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode != 0:
                check.status = CheckStatus.SKIPPED
                check.message = "网络端口检查被跳过"
                return CheckStatus.SKIPPED
            
            # 解析开放端口
            listening_ports = []
            for line in result.stdout.split('\n'):
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        address = parts[1]
                        if ':' in address:
                            port = address.split(':')[-1]
                            listening_ports.append(port)
            
            # 允许的端口
            allowed_ports = ['80', '443', '5000', '6379', '5432', '3306']
            suspicious_ports = [p for p in listening_ports if p not in allowed_ports and p.isdigit()]
            
            if not suspicious_ports:
                check.status = CheckStatus.PASSED
                check.message = f"端口配置正确，开放端口: {', '.join(listening_ports[:5])}"
                check.details = {'listening_ports': listening_ports}
                return CheckStatus.PASSED
            else:
                check.status = CheckStatus.WARNING
                check.message = f"发现可疑开放端口: {', '.join(suspicious_ports)}"
                check.details = {'listening_ports': listening_ports, 'suspicious_ports': suspicious_ports}
                return CheckStatus.WARNING
                
        except Exception as e:
            check.status = CheckStatus.SKIPPED
            check.message = f"端口检查失败: {str(e)}"
            return CheckStatus.SKIPPED
    
    def _run_file_check(self, check: SecurityCheck) -> CheckStatus:
        """检查文件权限"""
        critical_files = [
            '.env',
            'config.py',
            'api/config.py',
            'requirements.txt'
        ]
        
        insecure_files = []
        for file_path in critical_files:
            if os.path.exists(file_path):
                try:
                    import stat
                    file_stat = os.stat(file_path)
                    mode = stat.S_IMODE(file_stat.st_mode)
                    
                    # 检查文件权限是否过于宽松
                    if mode & 0o777 == 0o777:  # rwxrwxrwx
                        insecure_files.append(f"{file_path} (权限: {oct(mode)})")
                except Exception:
                    pass
        
        if not insecure_files:
            check.status = CheckStatus.PASSED
            check.message = "关键文件权限配置正确"
            return CheckStatus.PASSED
        else:
            check.status = CheckStatus.WARNING
            check.message = f"发现权限过于宽松的文件: {', '.join(insecure_files)}"
            check.details = {'insecure_files': insecure_files}
            return CheckStatus.WARNING
    
    def _run_log_check(self, check: SecurityCheck) -> CheckStatus:
        """检查日志配置"""
        log_dir = 'logs'
        if os.path.exists(log_dir):
            try:
                import stat
                dir_stat = os.stat(log_dir)
                mode = stat.S_IMODE(dir_stat.st_mode)
                
                # 检查目录权限
                if mode & 0o777 == 0o777:  # rwxrwxrwx
                    check.status = CheckStatus.WARNING
                    check.message = f"日志目录权限过于宽松: {oct(mode)}"
                    return CheckStatus.WARNING
                else:
                    check.status = CheckStatus.PASSED
                    check.message = "日志目录权限配置正确"
                    return CheckStatus.PASSED
                    
            except Exception as e:
                check.status = CheckStatus.SKIPPED
                check.message = f"检查日志目录失败: {str(e)}"
                return CheckStatus.SKIPPED
        else:
            check.status = CheckStatus.WARNING
            check.message = "日志目录不存在"
            return CheckStatus.WARNING
    
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
                'total': len(severity_checks),
                'passed': severity_passed,
                'passed_percentage': (severity_passed / len(severity_checks) * 100) if severity_checks else 0
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
            environment=os.getenv('FLASK_ENV', 'unknown'),
            total_checks=total,
            passed_checks=passed,
            failed_checks=failed,
            warning_checks=warning,
            skipped_checks=skipped,
            checks=self.checks,
            summary={
                'overall_status': overall_status,
                'pass_percentage': (passed / total * 100) if total > 0 else 0,
                'severity_stats': severity_stats,
                'critical_failed': len(failed_critical),
                'high_failed': len(failed_high)
            },
            recommendations=recommendations
        )
        
        return report
    
    def save_report(self, report: AuditReport, format: str = 'json'):
        """保存审计报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"security-audit-report-{timestamp}"
        
        if format == 'json':
            filename += '.json'
            # 转换为可序列化的字典
            report_dict = self._report_to_dict(report)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
        else:
            filename += '.txt'
            self._save_text_report(report, filename)
        
        logger.info(f"审计报告已保存: {filename}")
        return filename
    
    def _report_to_dict(self, report: AuditReport) -> dict:
        """将报告转换为可序列化的字典"""
        checks_list = []
        for check in report.checks:
            check_dict = {
                'id': check.id,
                'description': check.description,
                'check': check.check,
                'required': check.required,
                'severity': check.severity.value,
                'status': check.status.value,
                'message': check.message,
                'details': check.details
            }
            checks_list.append(check_dict)
        
        return {
            'timestamp': report.timestamp,
            'environment': report.environment,
            'total_checks': report.total_checks,
            'passed_checks': report.passed_checks,
            'failed_checks': report.failed_checks,
            'warning_checks': report.warning_checks,
            'skipped_checks': report.skipped_checks,
            'checks': checks_list,
            'summary': report.summary,
            'recommendations': report.recommendations
        }
    
    def _save_text_report(self, report: AuditReport, filename: str):
        """保存文本格式报告"""
        with open(filename, 'w', encoding='utf-8') as f:
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
            for severity, stats in report.summary['severity_stats'].items():
                f.write(f"  {severity.upper()}: {stats['passed']}/{stats['total']} "
                       f"({stats['passed_percentage']:.1f}%)\n")
            
            f.write("\n详细检查结果:\n")
            for check in report.checks:
                status_text = {
                    CheckStatus.PASSED: '[PASS]',
                    CheckStatus.FAILED: '[FAIL]',
                    CheckStatus.WARNING: '[WARN]',
                    CheckStatus.SKIPPED: '[SKIP]'
                }.get(check.status, '[UNKNOWN]')
                
                f.write(f"\n{status_text} [{check.severity.value.upper()}] {check.id}: {check.description}\n")
                f.write(f"   状态: {check.status.value}\n")
                f.write(f"   消息: {check.message}\n")
            
            f.write("\n建议:\n")
            for i, rec in enumerate(report.recommendations, 1):
                f.write(f"  {i}. {rec}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='安全审计工具')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                       help='报告输出格式')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    # 创建审计器
    auditor = SecurityAuditor()
    
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
    
    # 输出详细结果
    print("\n详细结果:")
    for check in report.checks:
        status_text = {
            CheckStatus.PASSED: '[PASS]',
            CheckStatus.FAILED: '[FAIL]',
            CheckStatus.WARNING: '[WARN]',
            CheckStatus.SKIPPED: '[SKIP]'
        }.get(check.status, '[UNKNOWN]')
        
        print(f"{status_text} {check.id}: {check.description}")
        print(f"  状态: {check.status.value} - {check.message}")
    
    # 如果有严重失败，返回非零退出码
    if report.summary['critical_failed'] > 0:
        sys.exit(1)
    elif report.summary['high_failed'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()