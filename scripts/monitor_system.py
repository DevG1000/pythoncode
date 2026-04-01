#!/usr/bin/env python3
"""
系统监控脚本
用于监控系统资源、应用状态和安全事件
"""

import os
import sys
import time
import json
import logging
import smtplib
import requests
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, config_file: str = 'config/monitoring-config.yaml'):
        """初始化监控器"""
        self.config_file = config_file
        self.config = self.load_config()
        self.metrics_history: Dict[str, List[Dict]] = {}
        
    def load_config(self) -> Dict[str, Any]:
        """加载监控配置"""
        default_config = {
            'monitoring': {
                'interval': 300,
                'alerts': {
                    'email': {
                        'enabled': False,
                        'smtp_server': 'smtp.gmail.com',
                        'smtp_port': 587,
                        'username': '',
                        'password': '',
                        'from_address': 'monitoring@pythoncode.com',
                        'to_addresses': ['admin@example.com']
                    }
                },
                'metrics': {
                    'system': {
                        'cpu_threshold': 80,
                        'memory_threshold': 85,
                        'disk_threshold': 90
                    },
                    'application': {
                        'response_time_threshold': 5000,
                        'error_rate_threshold': 5
                    }
                }
            }
        }
        
        # TODO: 从YAML文件加载配置
        # 暂时使用默认配置
        return default_config
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'application': {},
            'security': {}
        }
        
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics['system']['cpu_percent'] = cpu_percent
            
            # 内存使用率
            memory = psutil.virtual_memory()
            metrics['system']['memory_percent'] = memory.percent
            metrics['system']['memory_used_gb'] = memory.used / (1024**3)
            metrics['system']['memory_total_gb'] = memory.total / (1024**3)
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            metrics['system']['disk_percent'] = disk.percent
            metrics['system']['disk_used_gb'] = disk.used / (1024**3)
            metrics['system']['disk_total_gb'] = disk.total / (1024**3)
            
            # 网络IO
            net_io = psutil.net_io_counters()
            metrics['system']['net_bytes_sent'] = net_io.bytes_sent
            metrics['system']['net_bytes_recv'] = net_io.bytes_recv
            
            # 进程信息
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    process_info = proc.info
                    if process_info['cpu_percent'] > 0 or process_info['memory_percent'] > 0:
                        processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            metrics['system']['top_processes'] = sorted(
                processes,
                key=lambda x: x.get('cpu_percent', 0),
                reverse=True
            )[:10]
            
            logger.info(f"系统指标收集完成: CPU={cpu_percent}%, 内存={memory.percent}%, 磁盘={disk.percent}%")
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
            metrics['system']['error'] = str(e)
        
        return metrics
    
    def check_application_health(self) -> Dict[str, Any]:
        """检查应用健康状态"""
        health = {
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'checks': []
        }
        
        # 检查API健康端点
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=10)
            health['checks'].append({
                'name': 'api_health',
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds() * 1000,
                'status_code': response.status_code
            })
            
            if response.status_code == 200:
                health_data = response.json()
                health['status'] = health_data.get('status', 'unknown')
                health['details'] = health_data
            else:
                health['status'] = 'unhealthy'
                
        except requests.RequestException as e:
            health['checks'].append({
                'name': 'api_health',
                'status': 'unreachable',
                'error': str(e)
            })
            health['status'] = 'unreachable'
        
        # 检查数据库连接
        try:
            import psycopg2
            db_url = os.getenv('DATABASE_URL', '')
            if db_url:
                conn = psycopg2.connect(db_url, connect_timeout=5)
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
                conn.close()
                
                health['checks'].append({
                    'name': 'database',
                    'status': 'healthy'
                })
            else:
                health['checks'].append({
                    'name': 'database',
                    'status': 'not_configured'
                })
                
        except Exception as e:
            health['checks'].append({
                'name': 'database',
                'status': 'unhealthy',
                'error': str(e)
            })
        
        # 检查Redis连接
        try:
            # Redis检查暂时跳过，避免依赖问题
            # import redis
            # redis_host = os.getenv('REDIS_HOST', 'localhost')
            # redis_port = int(os.getenv('REDIS_PORT', '6379'))
            # redis_password = os.getenv('REDIS_PASSWORD', '')
            # 
            # r = redis.Redis(
            #     host=redis_host,
            #     port=redis_port,
            #     password=redis_password if redis_password else None,
            #     socket_connect_timeout=5
            # )
            # r.ping()
            
            health['checks'].append({
                'name': 'redis',
                'status': 'skipped',
                'message': 'Redis检查已跳过'
            })
            
            health['checks'].append({
                'name': 'redis',
                'status': 'healthy'
            })
            
        except Exception as e:
            health['checks'].append({
                'name': 'redis',
                'status': 'unhealthy',
                'error': str(e)
            })
        
        logger.info(f"应用健康检查完成: 状态={health['status']}")
        return health
    
    def check_security_metrics(self) -> Dict[str, Any]:
        """检查安全指标"""
        security = {
            'timestamp': datetime.now().isoformat(),
            'checks': [],
            'alerts': []
        }
        
        # 检查失败登录
        try:
            log_file = 'logs/security.log'
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 统计最近1小时的失败登录
                one_hour_ago = datetime.now() - timedelta(hours=1)
                failed_logins = 0
                
                for line in lines[-1000:]:  # 检查最近1000行
                    if 'LOGIN_FAILED' in line:
                        # 解析时间戳（简化处理）
                        try:
                            log_time_str = line.split(' - ')[0]
                            log_time = datetime.fromisoformat(log_time_str.replace(' ', 'T'))
                            if log_time > one_hour_ago:
                                failed_logins += 1
                        except:
                            pass
                
                security['checks'].append({
                    'name': 'failed_logins',
                    'count': failed_logins,
                    'period': '1h'
                })
                
                # 检查阈值
                threshold = 10  # 默认阈值
                if failed_logins > threshold:
                    security['alerts'].append({
                        'name': 'high_failed_logins',
                        'severity': 'warning',
                        'message': f'过去1小时失败登录次数过高: {failed_logins}次',
                        'threshold': threshold,
                        'current_value': failed_logins
                    })
                    
        except Exception as e:
            logger.error(f"检查失败登录失败: {e}")
        
        # 检查文件权限
        critical_files = ['.env', 'config.py', 'api/config.py']
        insecure_files = []
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                try:
                    import stat
                    file_stat = os.stat(file_path)
                    mode = stat.S_IMODE(file_stat.st_mode)
                    
                    # 检查权限是否过于宽松
                    if mode & 0o777 == 0o777:  # rwxrwxrwx
                        insecure_files.append({
                            'file': file_path,
                            'permissions': oct(mode)
                        })
                except Exception:
                    pass
        
        security['checks'].append({
            'name': 'file_permissions',
            'insecure_files': insecure_files
        })
        
        if insecure_files:
            security['alerts'].append({
                'name': 'insecure_file_permissions',
                'severity': 'critical',
                'message': f'发现权限过于宽松的文件: {len(insecure_files)}个',
                'files': insecure_files
            })
        
        logger.info(f"安全指标检查完成: 告警={len(security['alerts'])}个")
        return security
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查指标阈值"""
        alerts = []
        
        try:
            # 检查CPU阈值
            cpu_percent = metrics['system'].get('cpu_percent', 0)
            cpu_threshold = self.config['monitoring']['metrics']['system']['cpu_threshold']
            
            if cpu_percent > cpu_threshold:
                alerts.append({
                    'name': 'high_cpu_usage',
                    'severity': 'warning',
                    'message': f'CPU使用率过高: {cpu_percent}% (阈值: {cpu_threshold}%)',
                    'metric': 'cpu_percent',
                    'current_value': cpu_percent,
                    'threshold': cpu_threshold
                })
            
            # 检查内存阈值
            memory_percent = metrics['system'].get('memory_percent', 0)
            memory_threshold = self.config['monitoring']['metrics']['system']['memory_threshold']
            
            if memory_percent > memory_threshold:
                alerts.append({
                    'name': 'high_memory_usage',
                    'severity': 'warning',
                    'message': f'内存使用率过高: {memory_percent}% (阈值: {memory_threshold}%)',
                    'metric': 'memory_percent',
                    'current_value': memory_percent,
                    'threshold': memory_threshold
                })
            
            # 检查磁盘阈值
            disk_percent = metrics['system'].get('disk_percent', 0)
            disk_threshold = self.config['monitoring']['metrics']['system']['disk_threshold']
            
            if disk_percent > disk_threshold:
                alerts.append({
                    'name': 'high_disk_usage',
                    'severity': 'critical',
                    'message': f'磁盘使用率过高: {disk_percent}% (阈值: {disk_threshold}%)',
                    'metric': 'disk_percent',
                    'current_value': disk_percent,
                    'threshold': disk_threshold
                })
                
        except Exception as e:
            logger.error(f"检查阈值失败: {e}")
        
        return alerts
    
    def send_alert_email(self, alert: Dict[str, Any]):
        """发送告警邮件"""
        try:
            email_config = self.config['monitoring']['alerts']['email']
            
            if not email_config['enabled']:
                return
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = email_config['from_address']
            msg['To'] = ', '.join(email_config['to_addresses'])
            msg['Subject'] = f"[PythonCode Monitor] {alert['severity'].upper()}: {alert['name']}"
            
            # 邮件正文
            body = f"""
告警详情:
------------
名称: {alert['name']}
级别: {alert['severity']}
时间: {datetime.now().isoformat()}
消息: {alert['message']}

当前值: {alert.get('current_value', 'N/A')}
阈值: {alert.get('threshold', 'N/A')}

请及时处理。
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # 发送邮件
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
            
            logger.info(f"告警邮件已发送: {alert['name']}")
            
        except Exception as e:
            logger.error(f"发送告警邮件失败: {e}")
    
    def save_metrics(self, metrics: Dict[str, Any]):
        """保存指标数据"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d')
            metrics_file = f'logs/metrics_{timestamp}.json'
            
            # 读取现有数据
            data = []
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = []
            
            # 添加新数据
            data.append(metrics)
            
            # 保存数据（保留最近1000条记录）
            if len(data) > 1000:
                data = data[-1000:]
            
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"指标数据已保存: {metrics_file}")
            
        except Exception as e:
            logger.error(f"保存指标数据失败: {e}")
    
    def generate_report(self, metrics: Dict[str, Any], health: Dict[str, Any], security: Dict[str, Any]) -> Dict[str, Any]:
        """生成监控报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'system_status': 'healthy',
                'application_status': health['status'],
                'security_status': 'secure' if not security['alerts'] else 'alert'
            },
            'metrics': metrics,
            'health': health,
            'security': security,
            'recommendations': []
        }
        
        # 生成建议
        cpu_percent = metrics['system'].get('cpu_percent', 0)
        if cpu_percent > 70:
            report['recommendations'].append('CPU使用率较高，建议优化应用性能或增加资源')
        
        memory_percent = metrics['system'].get('memory_percent', 0)
        if memory_percent > 80:
            report['recommendations'].append('内存使用率较高，建议检查内存泄漏或增加内存')
        
        if security['alerts']:
            report['recommendations'].append('发现安全告警，请立即处理')
        
        if health['status'] != 'healthy':
            report['recommendations'].append('应用健康状态异常，请检查服务')
        
        return report
    
    def run_monitoring_cycle(self):
        """运行监控周期"""
        logger.info("开始监控周期...")
        
        try:
            # 收集指标
            metrics = self.collect_system_metrics()
            health = self.check_application_health()
            security = self.check_security_metrics()
            
            # 检查阈值
            system_alerts = self.check_thresholds(metrics)
            all_alerts = system_alerts + security['alerts']
            
            # 发送告警
            for alert in all_alerts:
                logger.warning(f"告警: {alert['severity']} - {alert['message']}")
                self.send_alert_email(alert)
            
            # 生成报告
            report = self.generate_report(metrics, health, security)
            
            # 保存数据
            self.save_metrics({
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'health': health,
                'security': security,
                'alerts': all_alerts
            })
            
            # 输出摘要
            print(f"\n监控摘要 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):")
            print(f"系统状态: CPU={metrics['system'].get('cpu_percent', 0)}%, "
                  f"内存={metrics['system'].get('memory_percent', 0)}%, "
                  f"磁盘={metrics['system'].get('disk_percent', 0)}%")
            print(f"应用状态: {health['status']}")
            print(f"安全状态: 告警={len(all_alerts)}个")
            
            if all_alerts:
                print("\n告警列表:")
                for alert in all_alerts:
                    print(f"  [{alert['severity']}] {alert['name']}: {alert['message']}")
            
            logger.info("监控周期完成")
            
        except Exception as e:
            logger.error(f"监控周期执行失败: {e}")
    
    def run_continuous(self, interval: int = 300):
        """持续运行监控"""
        logger.info(f"开始持续监控，间隔: {interval}秒")
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(float(interval))
                
        except KeyboardInterrupt:
            logger.info("监控已停止")
        except Exception as e:
            logger.error(f"监控运行失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='系统监控脚本')
    parser.add_argument('--once', action='store_true',
                       help='运行一次监控')
    parser.add_argument('--interval', type=int, default=300,
                       help='监控间隔（秒）')
    parser.add_argument('--config', default='config/monitoring-config.yaml',
                       help='监控配置文件路径')
    
    args = parser.parse_args()
    
    # 创建监控器
    monitor = SystemMonitor(args.config)
    
    # 运行监控
    if args.once:
        monitor.run_monitoring_cycle()
    else:
        monitor.run_continuous(args.interval)


if __name__ == '__main__':
    main()