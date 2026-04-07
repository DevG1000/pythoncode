#!/usr/bin/env python3
"""
安全监控脚本
实时监控系统安全状态和异常行为
"""

import json
import logging
import os
import smtplib
import sys
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class SecurityEvent:
    """安全事件"""

    id: str
    timestamp: str
    event_type: str
    severity: str  # critical, high, medium, low
    source: str
    description: str
    details: Dict[str, Any]
    status: str = "new"  # new, investigating, resolved


@dataclass
class AlertRule:
    """告警规则"""

    id: str
    name: str
    condition: str
    severity: str
    action: str
    cooldown: int  # 冷却时间（秒）
    last_triggered: Optional[datetime] = None


class SecurityMonitor:
    """安全监控器"""

    def __init__(self, config_path: str = "config/security-monitor.yaml"):
        """初始化监控器"""
        self.config_path = config_path
        self.events: List[SecurityEvent] = []
        self.alert_rules: List[AlertRule] = []
        self.metrics: Dict[str, Any] = defaultdict(int)
        self.event_queue = deque(maxlen=1000)
        self.running = False
        self.load_config()

    def load_config(self):
        """加载监控配置"""
        try:
            # 这里可以加载YAML配置
            # 暂时使用硬编码规则
            self.alert_rules = [
                AlertRule(
                    id="rule-001",
                    name="频繁登录失败",
                    condition="login_failures > 10 in 5 minutes",
                    severity="high",
                    action="block_ip",
                    cooldown=300,
                ),
                AlertRule(
                    id="rule-002",
                    name="异常API访问",
                    condition="api_errors > 50 in 1 minute",
                    severity="medium",
                    action="alert_admin",
                    cooldown=60,
                ),
                AlertRule(
                    id="rule-003",
                    name="敏感操作审计",
                    condition="sensitive_operation detected",
                    severity="critical",
                    action="immediate_response",
                    cooldown=0,
                ),
                AlertRule(
                    id="rule-004",
                    name="资源异常使用",
                    condition="cpu_usage > 90% for 5 minutes",
                    severity="high",
                    action="scale_up",
                    cooldown=300,
                ),
            ]
            logger.info(f"已加载 {len(self.alert_rules)} 个告警规则")

        except Exception as e:
            logger.error(f"加载配置失败: {e}")

    def start(self):
        """启动监控"""
        self.running = True
        logger.info("安全监控已启动")

        # 启动监控线程
        threads = [
            threading.Thread(target=self._monitor_logs, daemon=True),
            threading.Thread(target=self._monitor_metrics, daemon=True),
            threading.Thread(target=self._process_alerts, daemon=True),
            threading.Thread(target=self._generate_reports, daemon=True),
        ]

        for thread in threads:
            thread.start()

        # 主循环
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """停止监控"""
        self.running = False
        logger.info("安全监控已停止")

    def _monitor_logs(self):
        """监控日志文件"""
        log_files = ["logs/app.log", "logs/access.log", "logs/error.log", "logs/security.log"]

        last_positions = {}

        while self.running:
            for log_file in log_files:
                if not os.path.exists(log_file):
                    continue

                try:
                    # 获取文件当前位置
                    current_position = last_positions.get(log_file, 0)
                    file_size = os.path.getsize(log_file)

                    if file_size < current_position:
                        # 文件被截断或重新创建
                        current_position = 0

                    if file_size > current_position:
                        # 读取新内容
                        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                            f.seek(current_position)
                            new_lines = f.readlines()
                            last_positions[log_file] = f.tell()

                        # 分析新日志
                        for line in new_lines:
                            self._analyze_log_line(log_file, line.strip())

                except Exception as e:
                    logger.error(f"监控日志文件失败 {log_file}: {e}")

            time.sleep(5)  # 每5秒检查一次

    def _analyze_log_line(self, log_file: str, line: str):
        """分析日志行"""
        # 检测登录失败
        if "login failed" in line.lower() or "authentication failed" in line.lower():
            self._record_login_failure(line)

        # 检测敏感操作
        sensitive_keywords = ["password change", "privilege escalation", "admin access", "delete user", "export data"]
        for keyword in sensitive_keywords:
            if keyword in line.lower():
                self._record_sensitive_operation(keyword, line)

        # 检测SQL注入尝试
        sql_patterns = ["' OR '1'='1", " UNION SELECT ", " DROP TABLE ", " SELECT * FROM "]
        for pattern in sql_patterns:
            if pattern in line.upper():
                self._record_sql_injection_attempt(pattern, line)

        # 检测XSS尝试
        xss_patterns = ["<script>", "javascript:", "onerror=", "onload="]
        for pattern in xss_patterns:
            if pattern in line.lower():
                self._record_xss_attempt(pattern, line)

    def _record_login_failure(self, log_line: str):
        """记录登录失败"""
        # 提取IP地址（简化示例）
        import re

        ip_match = re.search(r"\d+\.\d+\.\d+\.\d+", log_line)
        ip = ip_match.group() if ip_match else "unknown"

        event_id = f"login_fail_{int(time.time())}"
        event = SecurityEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type="login_failure",
            severity="medium",
            source=ip,
            description="登录失败尝试",
            details={"log_line": log_line, "ip_address": ip, "count": self.metrics[f"login_failures_{ip}"] + 1},
        )

        self.events.append(event)
        self.event_queue.append(event)
        self.metrics[f"login_failures_{ip}"] += 1
        self.metrics["total_login_failures"] += 1

        logger.info(f"检测到登录失败: {ip}")

    def _record_sensitive_operation(self, operation: str, log_line: str):
        """记录敏感操作"""
        event_id = f"sensitive_op_{int(time.time())}"
        event = SecurityEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type="sensitive_operation",
            severity="high",
            source="application",
            description=f"敏感操作: {operation}",
            details={"operation": operation, "log_line": log_line, "timestamp": datetime.now().isoformat()},
        )

        self.events.append(event)
        self.event_queue.append(event)
        self.metrics["sensitive_operations"] += 1

        logger.warning(f"检测到敏感操作: {operation}")

    def _record_sql_injection_attempt(self, pattern: str, log_line: str):
        """记录SQL注入尝试"""
        event_id = f"sql_injection_{int(time.time())}"
        event = SecurityEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type="sql_injection",
            severity="critical",
            source="attacker",
            description="SQL注入尝试",
            details={"pattern": pattern, "log_line": log_line, "timestamp": datetime.now().isoformat()},
        )

        self.events.append(event)
        self.event_queue.append(event)
        self.metrics["sql_injection_attempts"] += 1

        logger.error(f"检测到SQL注入尝试: {pattern}")

    def _record_xss_attempt(self, pattern: str, log_line: str):
        """记录XSS尝试"""
        event_id = f"xss_attempt_{int(time.time())}"
        event = SecurityEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type="xss_attempt",
            severity="high",
            source="attacker",
            description="XSS攻击尝试",
            details={"pattern": pattern, "log_line": log_line, "timestamp": datetime.now().isoformat()},
        )

        self.events.append(event)
        self.event_queue.append(event)
        self.metrics["xss_attempts"] += 1

        logger.error(f"检测到XSS攻击尝试: {pattern}")

    def _monitor_metrics(self):
        """监控系统指标"""
        import psutil

        while self.running:
            try:
                # CPU使用率
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics["cpu_usage"] = cpu_percent

                # 内存使用率
                memory = psutil.virtual_memory()
                self.metrics["memory_usage"] = memory.percent

                # 磁盘使用率
                disk = psutil.disk_usage("/")
                self.metrics["disk_usage"] = disk.percent

                # 网络连接
                connections = psutil.net_connections()
                self.metrics["active_connections"] = len(connections)

                # 进程数
                self.metrics["process_count"] = len(psutil.pids())

                # 检查资源异常
                if cpu_percent > 90:
                    self._record_resource_alert("high_cpu", f"CPU使用率过高: {cpu_percent}%")

                if memory.percent > 90:
                    self._record_resource_alert("high_memory", f"内存使用率过高: {memory.percent}%")

                if disk.percent > 90:
                    self._record_resource_alert("high_disk", f"磁盘使用率过高: {disk.percent}%")

            except Exception as e:
                logger.error(f"监控指标失败: {e}")

            time.sleep(30)  # 每30秒收集一次指标

    def _record_resource_alert(self, alert_type: str, message: str):
        """记录资源告警"""
        event_id = f"resource_alert_{int(time.time())}"
        event = SecurityEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=alert_type,
            severity="medium",
            source="system",
            description=message,
            details={"alert_type": alert_type, "message": message, "timestamp": datetime.now().isoformat()},
        )

        self.events.append(event)
        self.event_queue.append(event)

        logger.warning(f"资源告警: {message}")

    def _process_alerts(self):
        """处理告警"""
        while self.running:
            try:
                # 检查登录失败告警
                self._check_login_failure_alerts()

                # 检查资源告警
                self._check_resource_alerts()

                # 检查其他告警规则
                for rule in self.alert_rules:
                    self._evaluate_rule(rule)

            except Exception as e:
                logger.error(f"处理告警失败: {e}")

            time.sleep(10)  # 每10秒检查一次告警

    def _check_login_failure_alerts(self):
        """检查登录失败告警"""
        # 获取最近5分钟的登录失败
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        recent_failures = [
            e
            for e in self.events
            if e.event_type == "login_failure" and datetime.fromisoformat(e.timestamp) > five_minutes_ago
        ]

        # 按IP统计
        ip_counts = defaultdict(int)
        for event in recent_failures:
            ip = event.details.get("ip_address", "unknown")
            ip_counts[ip] += 1

        # 检查是否有IP超过阈值
        for ip, count in ip_counts.items():
            if count > 10:  # 5分钟内超过10次失败
                # 检查冷却时间
                rule = next((r for r in self.alert_rules if r.id == "rule-001"), None)
                if rule and self._can_trigger_alert(rule):
                    self._trigger_alert(rule, {"ip_address": ip, "failure_count": count, "time_window": "5 minutes"})
                    rule.last_triggered = datetime.now()

    def _check_resource_alerts(self):
        """检查资源告警"""
        # 检查CPU使用率
        cpu_usage = self.metrics.get("cpu_usage", 0)
        if cpu_usage > 90:
            # 检查是否持续5分钟
            rule = next((r for r in self.alert_rules if r.id == "rule-004"), None)
            if rule and self._can_trigger_alert(rule):
                self._trigger_alert(rule, {"metric": "cpu_usage", "value": cpu_usage, "threshold": 90})
                rule.last_triggered = datetime.now()

    def _evaluate_rule(self, rule: AlertRule):
        """评估告警规则"""
        # 这里可以根据规则条件进行评估
        # 简化实现，实际需要更复杂的规则引擎
        pass

    def _can_trigger_alert(self, rule: AlertRule) -> bool:
        """检查是否可以触发告警（冷却时间）"""
        if rule.cooldown == 0:
            return True

        if rule.last_triggered is None:
            return True

        elapsed = (datetime.now() - rule.last_triggered).total_seconds()
        return elapsed >= rule.cooldown

    def _trigger_alert(self, rule: AlertRule, context: Dict[str, Any]):
        """触发告警"""
        logger.warning(f"触发告警: {rule.name} - {rule.severity}")

        # 记录告警事件
        event_id = f"alert_{rule.id}_{int(time.time())}"
        event = SecurityEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type="alert_triggered",
            severity=rule.severity,
            source="security_monitor",
            description=f"告警触发: {rule.name}",
            details={
                "rule_id": rule.id,
                "rule_name": rule.name,
                "severity": rule.severity,
                "context": context,
                "action": rule.action,
            },
        )

        self.events.append(event)

        # 执行告警动作
        self._execute_alert_action(rule, context)

    def _execute_alert_action(self, rule: AlertRule, context: Dict[str, Any]):
        """执行告警动作"""
        if rule.action == "block_ip":
            ip = context.get("ip_address")
            if ip:
                self._block_ip(ip)

        elif rule.action == "alert_admin":
            self._send_admin_alert(rule, context)

        elif rule.action == "immediate_response":
            self._immediate_response(rule, context)

        elif rule.action == "scale_up":
            self._scale_resources()

    def _block_ip(self, ip: str):
        """阻塞IP地址"""
        logger.info(f"阻塞IP地址: {ip}")
        # 实际实现可能需要调用防火墙API或修改iptables规则
        # 这里只是记录日志
        with open("logs/blocked_ips.log", "a") as f:
            f.write(f"{datetime.now().isoformat()} - BLOCKED: {ip}\n")

    def _send_admin_alert(self, rule: AlertRule, context: Dict[str, Any]):
        """发送管理员告警"""
        try:
            # 配置邮件发送
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", 587))
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")
            admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")

            if not all([smtp_user, smtp_password]):
                logger.warning("邮件配置不完整，跳过发送告警邮件")
                return

            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = admin_email
            msg["Subject"] = f"安全告警: {rule.name} - {rule.severity.upper()}"

            body = f"""
安全告警通知

规则名称: {rule.name}
严重程度: {rule.severity}
触发时间: {datetime.now().isoformat()}
            
上下文信息:
{json.dumps(context, indent=2, ensure_ascii=False)}
            
请立即检查系统安全状态。
            
此邮件由安全监控系统自动发送。
            """

            msg.attach(MIMEText(body, "plain", "utf-8"))

            # 发送邮件
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

            logger.info(f"已发送管理员告警邮件: {rule.name}")

        except Exception as e:
            logger.error(f"发送告警邮件失败: {e}")

    def _immediate_response(self, rule: AlertRule, context: Dict[str, Any]):
        """立即响应"""
        logger.critical(f"立即响应告警: {rule.name}")
        # 这里可以执行紧急响应操作，如：
        # - 隔离受影响系统
        # - 启动应急响应流程
        # - 通知安全团队

    def _scale_resources(self):
        """扩展资源"""
        logger.info("触发资源扩展")
        # 这里可以调用云服务API扩展资源

    def _generate_reports(self):
        """生成报告"""
        while self.running:
            try:
                # 每小时生成一次报告
                time.sleep(3600)

                report = self._create_hourly_report()
                self._save_report(report)

                # 每天生成一次详细报告
                if datetime.now().hour == 0:  # 午夜
                    daily_report = self._create_daily_report()
                    self._save_report(daily_report, "daily")

            except Exception as e:
                logger.error(f"生成报告失败: {e}")

    def _create_hourly_report(self) -> Dict[str, Any]:
        """创建小时报告"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_events = [e for e in self.events if datetime.fromisoformat(e.timestamp) > one_hour_ago]

        return {
            "timestamp": datetime.now().isoformat(),
            "period": "hourly",
            "event_count": len(recent_events),
            "event_summary": self._summarize_events(recent_events),
            "metrics": dict(self.metrics),
            "alerts_triggered": len([e for e in recent_events if e.event_type == "alert_triggered"]),
        }

    def _create_daily_report(self) -> Dict[str, Any]:
        """创建日报"""
        one_day_ago = datetime.now() - timedelta(days=1)
        daily_events = [e for e in self.events if datetime.fromisoformat(e.timestamp) > one_day_ago]

        return {
            "timestamp": datetime.now().isoformat(),
            "period": "daily",
            "event_count": len(daily_events),
            "event_summary": self._summarize_events(daily_events),
            "top_ips": self._get_top_ips(daily_events),
            "security_metrics": self._calculate_security_metrics(daily_events),
            "recommendations": self._generate_recommendations(daily_events),
        }

    def _summarize_events(self, events: List[SecurityEvent]) -> Dict[str, int]:
        """汇总事件"""
        summary = defaultdict(int)
        for event in events:
            summary[event.event_type] += 1
        return dict(summary)

    def _get_top_ips(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """获取Top IP地址"""
        ip_counts = defaultdict(int)
        for event in events:
            if event.source and event.source != "unknown":
                ip_counts[event.source] += 1

        return [{"ip": ip, "count": count} for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]]

    def _calculate_security_metrics(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """计算安全指标"""
        critical_events = [e for e in events if e.severity == "critical"]
        high_events = [e for e in events if e.severity == "high"]

        return {
            "critical_events": len(critical_events),
            "high_events": len(high_events),
            "attack_attempts": len([e for e in events if "injection" in e.event_type or "attempt" in e.event_type]),
            "successful_attacks": 0,  # 需要更复杂的检测
            "mean_time_to_detect": 0,  # 需要时间戳计算
            "mean_time_to_respond": 0,  # 需要响应时间记录
        }

    def _generate_recommendations(self, events: List[SecurityEvent]) -> List[str]:
        """生成建议"""
        recommendations = []

        # 检查登录失败
        login_failures = [e for e in events if e.event_type == "login_failure"]
        if len(login_failures) > 100:
            recommendations.append("考虑实施账户锁定策略或CAPTCHA验证")

        # 检查攻击尝试
        attack_attempts = [e for e in events if "injection" in e.event_type or "attempt" in e.event_type]
        if attack_attempts:
            recommendations.append("加强Web应用防火墙规则")

        # 检查资源使用
        if self.metrics.get("cpu_usage", 0) > 80:
            recommendations.append("考虑优化应用性能或扩展计算资源")

        return recommendations

    def _save_report(self, report: Dict[str, Any], report_type: str = "hourly"):
        """保存报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/security-{report_type}-{timestamp}.json"

        os.makedirs("reports", exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"已保存安全报告: {filename}")

    def get_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        return {
            "running": self.running,
            "events_count": len(self.events),
            "queue_size": len(self.event_queue),
            "metrics": dict(self.metrics),
            "last_alert": self.events[-1].timestamp if self.events else None,
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="安全监控工具")
    parser.add_argument("--config", default="config/security-monitor.yaml", help="监控配置文件路径")
    parser.add_argument("--daemon", action="store_true", help="以守护进程模式运行")
    parser.add_argument("--status", action="store_true", help="显示监控状态")
    parser.add_argument("--report", choices=["hourly", "daily"], help="生成报告")

    args = parser.parse_args()

    monitor = SecurityMonitor(args.config)

    if args.status:
        status = monitor.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return

    if args.report:
        if args.report == "hourly":
            report = monitor._create_hourly_report()
        else:
            report = monitor._create_daily_report()

        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    if args.daemon:
        # 守护进程模式
        import daemon
        import daemon.pidfile

        pidfile = "/tmp/security-monitor.pid"

        with daemon.DaemonContext(
            pidfile=daemon.pidfile.PIDLockFile(pidfile),
            stdout=open("/tmp/security-monitor.out", "w"),
            stderr=open("/tmp/security-monitor.err", "w"),
        ):
            monitor.start()
    else:
        # 前台运行
        try:
            monitor.start()
        except KeyboardInterrupt:
            monitor.stop()


if __name__ == "__main__":
    main()
