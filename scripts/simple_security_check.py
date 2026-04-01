#!/usr/bin/env python3
"""
简化版安全检查脚本
不依赖外部库，用于基本安全配置检查
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityChecker:
    """安全检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.checks = []
        self.results = []
        self._load_checks()
    
    def _load_checks(self):
        """加载安全检查项"""
        self.checks = [
            {
                'id': 'check-001',
                'description': '检查.env文件中的硬编码密钥',
                'severity': 'critical',
                'function': self._check_hardcoded_secrets
            },
            {
                'id': 'check-002',
                'description': '检查Flask运行环境',
                'severity': 'high',
                'function': self._check_flask_environment
            },
            {
                'id': 'check-003',
                'description': '检查数据库SSL配置',
                'severity': 'high',
                'function': self._check_database_ssl
            },
            {
                'id': 'check-004',
                'description': '检查日志文件权限',
                'severity': 'medium',
                'function': self._check_log_permissions
            },
            {
                'id': 'check-005',
                'description': '检查开放端口',
                'severity': 'medium',
                'function': self._check_open_ports
            },
            {
                'id': 'check-006',
                'description': '检查依赖包安全',
                'severity': 'high',
                'function': self._check_dependencies
            },
            {
                'id': 'check-007',
                'description': '检查代码中的敏感信息',
                'severity': 'critical',
                'function': self._check_sensitive_info_in_code
            }
        ]
    
    def run_all_checks(self):
        """运行所有检查"""
        logger.info("开始安全检查...")
        
        for check in self.checks:
            logger.info(f"运行检查: {check['id']} - {check['description']}")
            try:
                result = check['function']()
                result['id'] = check['id']
                result['description'] = check['description']
                result['severity'] = check['severity']
                self.results.append(result)
            except Exception as e:
                logger.error(f"检查 {check['id']} 失败: {e}")
                self.results.append({
                    'id': check['id'],
                    'description': check['description'],
                    'severity': check['severity'],
                    'status': 'error',
                    'message': f'检查失败: {str(e)}'
                })
        
        return self._generate_report()
    
    def _check_hardcoded_secrets(self) -> Dict[str, Any]:
        """检查硬编码的密钥"""
        env_file = '.env'
        secrets_found = []
        
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查常见的密钥模式
            secret_patterns = [
                'SECRET_KEY=',
                'PASSWORD=',
                'API_KEY=',
                'TOKEN=',
                'ACCESS_KEY=',
                'SECRET_ACCESS_KEY=',
                'PRIVATE_KEY='
            ]
            
            for pattern in secret_patterns:
                if pattern in content:
                    # 提取具体的值
                    lines = content.split('\n')
                    for line in lines:
                        if pattern in line:
                            value = line.split('=', 1)[1].strip() if '=' in line else ''
                            # 检查是否是占位符
                            if value and value not in ['', 'changeme', 'your-secret-key', 'placeholder', 'your_password', 'your-password']:
                                # 检查是否是环境变量格式
                                if not (value.startswith('${') and value.endswith('}')):
                                    secrets_found.append({
                                        'pattern': pattern,
                                        'line': line.strip()
                                    })
        
        if secrets_found:
            return {
                'status': 'failed',
                'message': f'发现 {len(secrets_found)} 个可能的硬编码密钥',
                'details': secrets_found
            }
        else:
            return {
                'status': 'passed',
                'message': '未发现硬编码密钥',
                'details': []
            }
    
    def _check_flask_environment(self) -> Dict[str, Any]:
        """检查Flask运行环境"""
        flask_env = os.getenv('FLASK_ENV', 'development')
        debug_mode = os.getenv('FLASK_DEBUG', '1')
        
        issues = []
        
        if flask_env.strip().lower() != 'production':
            issues.append(f'运行环境应为production，当前为: {flask_env}')
        
        if debug_mode.strip() in ['1', 'true', 'True']:
            issues.append('调试模式已启用，生产环境应禁用')
        
        if issues:
            return {
                'status': 'failed',
                'message': 'Flask环境配置不安全',
                'details': issues
            }
        else:
            return {
                'status': 'passed',
                'message': 'Flask环境配置正确',
                'details': []
            }
    
    def _check_database_ssl(self) -> Dict[str, Any]:
        """检查数据库SSL配置"""
        db_url = os.getenv('DATABASE_URL', '')
        
        if not db_url:
            return {
                'status': 'warning',
                'message': '未设置DATABASE_URL环境变量',
                'details': []
            }
        
        # 检查是否启用SSL
        ssl_indicators = ['ssl=true', 'sslmode=require', 'sslmode=verify-full']
        ssl_enabled = any(indicator in db_url.lower() for indicator in ssl_indicators)
        
        if ssl_enabled:
            return {
                'status': 'passed',
                'message': '数据库连接已启用SSL',
                'details': [db_url]
            }
        else:
            return {
                'status': 'failed',
                'message': '数据库连接未启用SSL',
                'details': [db_url]
            }
    
    def _check_log_permissions(self) -> Dict[str, Any]:
        """检查日志文件权限"""
        log_dir = 'logs'
        issues = []
        
        if os.path.exists(log_dir):
            import stat
            
            for root, dirs, files in os.walk(log_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_stat = os.stat(file_path)
                        mode = stat.S_IMODE(file_stat.st_mode)
                        
                        # 检查权限是否过于宽松
                        if mode & 0o777 == 0o777:  # rwxrwxrwx
                            issues.append(f'文件权限过于宽松: {file_path} ({oct(mode)})')
                        
                        # 检查是否全局可写
                        if mode & 0o002:  # 其他用户可写
                            issues.append(f'文件全局可写: {file_path} ({oct(mode)})')
                    
                    except Exception as e:
                        issues.append(f'无法检查文件权限: {file_path} ({str(e)})')
        
        if issues:
            return {
                'status': 'failed',
                'message': f'发现 {len(issues)} 个日志文件权限问题',
                'details': issues[:5]  # 只显示前5个问题
            }
        else:
            return {
                'status': 'passed',
                'message': '日志文件权限配置正确',
                'details': []
            }
    
    def _check_open_ports(self) -> Dict[str, Any]:
        """检查开放端口"""
        try:
            # 使用netstat检查开放端口
            result = subprocess.run(
                'netstat -an | findstr LISTENING',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            open_ports = []
            for line in result.stdout.split('\n'):
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        address = parts[1]
                        open_ports.append(address)
            
            # 允许的端口
            allowed_ports = ['80', '443', '5000', '6379', '5432']
            suspicious_ports = []
            
            for port_info in open_ports:
                # 提取端口号
                if ':' in port_info:
                    port = port_info.split(':')[-1]
                    if port not in allowed_ports and port.isdigit():
                        suspicious_ports.append(port_info)
            
            if suspicious_ports:
                return {
                    'status': 'failed',
                    'message': f'发现 {len(suspicious_ports)} 个可疑开放端口',
                    'details': suspicious_ports[:10]  # 只显示前10个
                }
            else:
                return {
                    'status': 'passed',
                    'message': '端口配置正确',
                    'details': open_ports[:10]  # 只显示前10个
                }
                
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'端口检查失败: {str(e)}',
                'details': []
            }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """检查依赖包安全"""
        try:
            # 检查requirements.txt是否存在
            req_file = 'requirements.txt'
            if not os.path.exists(req_file):
                return {
                    'status': 'warning',
                    'message': '未找到requirements.txt文件',
                    'details': []
                }
            
            # 读取依赖
            with open(req_file, 'r') as f:
                dependencies = f.readlines()
            
            # 检查已知的不安全包
            insecure_packages = [
                'django==1.11',  # 旧版本可能有漏洞
                'flask<2.0',     # 旧版本
                'requests<2.20', # 旧版本
                'pyyaml<5.1',    # YAML漏洞
            ]
            
            found_insecure = []
            for dep in dependencies:
                dep = dep.strip()
                if dep and not dep.startswith('#'):
                    for insecure in insecure_packages:
                        if insecure in dep:
                            found_insecure.append(dep)
            
            if found_insecure:
                return {
                    'status': 'failed',
                    'message': f'发现 {len(found_insecure)} 个可能不安全的依赖',
                    'details': found_insecure
                }
            else:
                return {
                    'status': 'passed',
                    'message': '依赖包检查通过',
                    'details': [f'共检查 {len(dependencies)} 个依赖']
                }
                
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'依赖检查失败: {str(e)}',
                'details': []
            }
    
    def _check_sensitive_info_in_code(self) -> Dict[str, Any]:
        """检查代码中的敏感信息"""
        sensitive_patterns = [
            ('password', '密码'),
            ('secret', '密钥'),
            ('token', '令牌'),
            ('api_key', 'API密钥'),
            ('private_key', '私钥'),
            ('aws_access_key', 'AWS访问密钥'),
            ('database_password', '数据库密码')
        ]
        
        issues = []
        checked_files = 0
        
        # 检查Python文件
        for root, dirs, files in os.walk('.'):
            # 跳过一些目录
            if any(skip in root for skip in ['.git', '__pycache__', 'venv', '.venv', 'node_modules']):
                continue
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            for line_num, line in enumerate(lines, 1):
                                line_lower = line.lower()
                                for pattern, description in sensitive_patterns:
                                    if pattern in line_lower:
                                        # 检查是否是变量定义
                                        if '=' in line and not line.strip().startswith('#'):
                                            # 检查值是否是硬编码
                                            parts = line.split('=', 1)
                                            if len(parts) == 2:
                                                value = parts[1].strip()
                                                # 检查是否是字符串字面量
                                                if (value.startswith('"') and value.endswith('"')) or \
                                                   (value.startswith("'") and value.endswith("'")):
                                                    # 移除引号
                                                    inner_value = value[1:-1]
                                                    # 检查是否是占位符
                                                    if inner_value and inner_value not in ['', 'changeme', 'your_password', 'your-secret-key', 'placeholder']:
                                                        # 检查是否是环境变量格式
                                                        if not (inner_value.startswith('${') and inner_value.endswith('}')):
                                                            issues.append({
                                                                'file': file_path,
                                                                'line': line_num,
                                                                'pattern': pattern,
                                                                'description': description,
                                                                'code': line.strip()
                                                            })
                        
                        checked_files += 1
                        
                    except Exception as e:
                        logger.warning(f'无法检查文件 {file_path}: {e}')
        
        if issues:
            return {
                'status': 'failed',
                'message': f'在代码中发现 {len(issues)} 处可能的敏感信息',
                'details': issues[:5]  # 只显示前5个
            }
        else:
            return {
                'status': 'passed',
                'message': f'代码检查通过，检查了 {checked_files} 个文件',
                'details': []
            }
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成检查报告"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'passed')
        failed = sum(1 for r in self.results if r['status'] == 'failed')
        warning = sum(1 for r in self.results if r['status'] == 'warning')
        error = sum(1 for r in self.results if r['status'] == 'error')
        
        # 按严重程度统计
        severity_stats = {
            'critical': {'total': 0, 'failed': 0},
            'high': {'total': 0, 'failed': 0},
            'medium': {'total': 0, 'failed': 0}
        }
        
        for result in self.results:
            severity = result['severity']
            if severity in severity_stats:
                severity_stats[severity]['total'] += 1
                if result['status'] == 'failed':
                    severity_stats[severity]['failed'] += 1
        
        # 总体评估
        critical_failed = severity_stats['critical']['failed']
        high_failed = severity_stats['high']['failed']
        
        if critical_failed > 0:
            overall_status = 'CRITICAL_FAIL'
        elif high_failed > 0:
            overall_status = 'HIGH_FAIL'
        elif failed > 0:
            overall_status = 'FAIL'
        else:
            overall_status = 'PASS'
        
        # 生成建议
        recommendations = []
        if critical_failed > 0:
            recommendations.append('立即修复所有CRITICAL级别的失败检查')
        if high_failed > 0:
            recommendations.append('24小时内修复HIGH级别的失败检查')
        if warning > 0:
            recommendations.append('关注WARNING级别的检查结果')
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'summary': {
                'total_checks': total,
                'passed': passed,
                'failed': failed,
                'warning': warning,
                'error': error,
                'pass_percentage': (passed / total * 100) if total > 0 else 0
            },
            'severity_stats': severity_stats,
            'results': self.results,
            'recommendations': recommendations
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any], format: str = 'text'):
        """打印检查报告"""
        if format == 'json':
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            self._print_text_report(report)
    
    def _print_text_report(self, report: Dict[str, Any]):
        """打印文本格式报告"""
        print("=" * 80)
        print("安全检查报告")
        print("=" * 80)
        print()
        
        print(f"生成时间: {report['timestamp']}")
        print(f"总体状态: {report['overall_status']}")
        print()
        
        summary = report['summary']
        print("检查结果统计:")
        print(f"  总计: {summary['total_checks']}")
        print(f"  通过: {summary['passed']}")
        print(f"  失败: {summary['failed']}")
        print(f"  警告: {summary['warning']}")
        print(f"  错误: {summary['error']}")
        print(f"  通过率: {summary['pass_percentage']:.1f}%")
        print()
        
        print("按严重程度统计:")
        for severity, stats in report['severity_stats'].items():
            failed = stats['failed']
            total = stats['total']
            if total > 0:
                print(f"  {severity.upper()}: {failed}/{total} 失败")
        print()
        
        print("详细结果:")
        for result in report['results']:
            status_symbol = {
                'passed': '[PASS]',
                'failed': '[FAIL]',
                'warning': '[WARN]',
                'error': '[ERR]'
            }.get(result['status'], '[UNK]')
            
            print(f"  {status_symbol} [{result['severity'].upper()}] {result['id']}: {result['description']}")
            print(f"      状态: {result['status']} - {result['message']}")
            
            if 'details' in result and result['details']:
                details = result['details']
                if isinstance(details, list) and len(details) > 0:
                    print(f"      详情: {details[0]}")
                    if len(details) > 1:
                        print(f"           还有 {len(details)-1} 个详情...")
            print()
        
        if report['recommendations']:
            print("建议:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
            print()
        
        print("=" * 80)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='简化版安全检查工具')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='输出格式')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    # 创建检查器
    checker = SecurityChecker()
    
    # 运行检查
    report = checker.run_all_checks()
    
    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.format == 'json':
                json.dump(report, f, indent=2, ensure_ascii=False)
            else:
                checker._print_text_report(report)
        print(f"报告已保存到: {args.output}")
    else:
        checker.print_report(report, args.format)
    
    # 根据检查结果返回退出码
    if report['overall_status'] == 'CRITICAL_FAIL':
        sys.exit(1)
    elif report['overall_status'] == 'HIGH_FAIL':
        sys.exit(2)
    elif report['overall_status'] == 'FAIL':
        sys.exit(3)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()