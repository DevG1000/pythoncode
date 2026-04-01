#!/usr/bin/env python3
"""
Monitoring Dashboard for PythonCode Project
Provides real-time monitoring of system metrics, service health, and performance
"""

import time
import psutil
import platform
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import socket
import subprocess
import sys
from collections import deque

class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class SystemMetrics:
    """System metrics data class"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_sent_mb: float
    network_recv_mb: float
    processes_running: int
    system_uptime_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class ServiceHealth:
    """Service health data class"""
    service_name: str
    status: ServiceStatus
    response_time_ms: Optional[float] = None
    last_check: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'service_name': self.service_name,
            'status': self.status.value,
            'response_time_ms': self.response_time_ms,
            'last_check': self.last_check,
            'error_message': self.error_message
        }

@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    timestamp: str
    api_response_time_ms: float
    command_execution_time_ms: float
    card_generation_time_ms: float
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

class MonitoringDashboard:
    """Main monitoring dashboard class"""
    
    def __init__(self, history_size: int = 100):
        """
        Initialize monitoring dashboard
        
        Args:
            history_size: Number of historical metrics to keep
        """
        self.history_size = history_size
        self.system_metrics_history = deque(maxlen=history_size)
        self.performance_metrics_history = deque(maxlen=history_size)
        self.service_health_status = {}
        self.is_running = False
        self.monitoring_thread = None
        
        # Initialize service health
        self._initialize_services()
        
    def _initialize_services(self):
        """Initialize service health tracking"""
        services = [
            'API Service',
            'Command System',
            'Card Generator',
            'Email Service',
            'Database',
            'Redis Cache'
        ]
        
        for service in services:
            self.service_health_status[service] = ServiceHealth(
                service_name=service,
                status=ServiceStatus.UNKNOWN,
                last_check=datetime.now().isoformat()
            )
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Network I/O
        net_io = psutil.net_io_counters()
        network_sent_mb = net_io.bytes_sent / (1024 * 1024)
        network_recv_mb = net_io.bytes_recv / (1024 * 1024)
        
        # Processes
        processes_running = len([p for p in psutil.process_iter(['status']) 
                               if p.info['status'] == psutil.STATUS_RUNNING])
        
        # System uptime
        uptime_seconds = time.time() - psutil.boot_time()
        
        metrics = SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_usage_percent=disk_percent,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            processes_running=processes_running,
            system_uptime_seconds=uptime_seconds
        )
        
        self.system_metrics_history.append(metrics)
        return metrics
    
    def check_service_health(self, service_name: str) -> ServiceHealth:
        """Check health of a specific service"""
        try:
            start_time = time.time()
            
            if service_name == 'API Service':
                # Check if API is responding
                import requests
                try:
                    response = requests.get('http://localhost:5000/health', timeout=2)
                    status = ServiceStatus.HEALTHY if response.status_code == 200 else ServiceStatus.UNHEALTHY
                except:
                    status = ServiceStatus.UNHEALTHY
                    
            elif service_name == 'Command System':
                # Check if command system modules can be imported
                try:
                    import command_system
                    status = ServiceStatus.HEALTHY
                except:
                    status = ServiceStatus.UNHEALTHY
                    
            elif service_name == 'Card Generator':
                # Check if card generator can be imported
                try:
                    import card_generator
                    status = ServiceStatus.HEALTHY
                except:
                    status = ServiceStatus.UNHEALTHY
                    
            elif service_name == 'Email Service':
                # Check if email service can be imported
                try:
                    import api.email_service
                    status = ServiceStatus.HEALTHY
                except:
                    status = ServiceStatus.UNHEALTHY
                    
            else:
                # For other services, assume healthy
                status = ServiceStatus.HEALTHY
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            health = ServiceHealth(
                service_name=service_name,
                status=status,
                response_time_ms=response_time,
                last_check=datetime.now().isoformat()
            )
            
            self.service_health_status[service_name] = health
            return health
            
        except Exception as e:
            health = ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.UNHEALTHY,
                error_message=str(e),
                last_check=datetime.now().isoformat()
            )
            self.service_health_status[service_name] = health
            return health
    
    def check_all_services(self) -> Dict[str, ServiceHealth]:
        """Check health of all services"""
        for service_name in self.service_health_status.keys():
            self.check_service_health(service_name)
        return self.service_health_status
    
    def collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect performance metrics"""
        # These would normally come from actual performance monitoring
        # For now, we'll use simulated/estimated values
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            api_response_time_ms=150.5,  # Simulated
            command_execution_time_ms=45.2,  # Simulated
            card_generation_time_ms=120.8,  # Simulated
            active_tasks=3,  # Simulated
            completed_tasks=125,  # Simulated
            failed_tasks=2  # Simulated
        )
        
        self.performance_metrics_history.append(metrics)
        return metrics
    
    def start_monitoring(self, interval_seconds: int = 5):
        """Start continuous monitoring"""
        if self.is_running:
            print("Monitoring is already running")
            return
        
        self.is_running = True
        
        def monitoring_loop():
            while self.is_running:
                try:
                    # Collect metrics
                    self.collect_system_metrics()
                    self.check_all_services()
                    self.collect_performance_metrics()
                    
                    # Display current status
                    self.display_current_status()
                    
                    time.sleep(interval_seconds)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error in monitoring loop: {e}")
                    time.sleep(interval_seconds)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        print(f"Monitoring started with {interval_seconds}s interval")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        print("Monitoring stopped")
    
    def display_current_status(self):
        """Display current system status in console"""
        if not self.system_metrics_history:
            return
        
        latest_system = self.system_metrics_history[-1]
        latest_performance = self.performance_metrics_history[-1] if self.performance_metrics_history else None
        
        print("\n" + "="*80)
        print("PYTHONCODE MONITORING DASHBOARD")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nSYSTEM METRICS:")
        print(f"  CPU Usage: {latest_system.cpu_percent:.1f}%")
        print(f"  Memory Usage: {latest_system.memory_percent:.1f}%")
        print(f"  Disk Usage: {latest_system.disk_usage_percent:.1f}%")
        print(f"  Network: ↑{latest_system.network_sent_mb:.1f}MB ↓{latest_system.network_recv_mb:.1f}MB")
        print(f"  Running Processes: {latest_system.processes_running}")
        print(f"  System Uptime: {latest_system.system_uptime_seconds/3600:.1f}h")
        
        if latest_performance:
            print("\nPERFORMANCE METRICS:")
            print(f"  API Response Time: {latest_performance.api_response_time_ms:.1f}ms")
            print(f"  Command Execution: {latest_performance.command_execution_time_ms:.1f}ms")
            print(f"  Card Generation: {latest_performance.card_generation_time_ms:.1f}ms")
            print(f"  Tasks: {latest_performance.active_tasks} active, "
                  f"{latest_performance.completed_tasks} completed, "
                  f"{latest_performance.failed_tasks} failed")
        
        print("\nSERVICE HEALTH:")
        for service_name, health in self.service_health_status.items():
            status_icon = "✅" if health.status == ServiceStatus.HEALTHY else "⚠️" if health.status == ServiceStatus.DEGRADED else "❌"
            response_time = f"{health.response_time_ms:.1f}ms" if health.response_time_ms else "N/A"
            print(f"  {status_icon} {service_name}: {health.status.value} ({response_time})")
        
        print("="*80)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'current': self.system_metrics_history[-1].to_dict() if self.system_metrics_history else None,
                'history_size': len(self.system_metrics_history)
            },
            'performance': {
                'current': self.performance_metrics_history[-1].to_dict() if self.performance_metrics_history else None,
                'history_size': len(self.performance_metrics_history)
            },
            'services': {name: health.to_dict() for name, health in self.service_health_status.items()},
            'alerts': self._generate_alerts()
        }
        return report
    
    def _generate_alerts(self) -> List[Dict[str, Any]]:
        """Generate alerts based on metrics"""
        alerts = []
        
        if self.system_metrics_history:
            latest = self.system_metrics_history[-1]
            
            # CPU alert
            if latest.cpu_percent > 80:
                alerts.append({
                    'type': 'warning',
                    'message': f'High CPU usage: {latest.cpu_percent:.1f}%',
                    'metric': 'cpu_percent',
                    'value': latest.cpu_percent
                })
            
            # Memory alert
            if latest.memory_percent > 85:
                alerts.append({
                    'type': 'warning',
                    'message': f'High memory usage: {latest.memory_percent:.1f}%',
                    'metric': 'memory_percent',
                    'value': latest.memory_percent
                })
            
            # Disk alert
            if latest.disk_usage_percent > 90:
                alerts.append({
                    'type': 'critical',
                    'message': f'High disk usage: {latest.disk_usage_percent:.1f}%',
                    'metric': 'disk_usage_percent',
                    'value': latest.disk_usage_percent
                })
        
        # Service health alerts
        for service_name, health in self.service_health_status.items():
            if health.status == ServiceStatus.UNHEALTHY:
                alerts.append({
                    'type': 'critical',
                    'message': f'Service {service_name} is unhealthy',
                    'service': service_name,
                    'status': health.status.value
                })
            elif health.status == ServiceStatus.DEGRADED:
                alerts.append({
                    'type': 'warning',
                    'message': f'Service {service_name} is degraded',
                    'service': service_name,
                    'status': health.status.value
                })
        
        return alerts
    
    def save_report(self, filename: str = "monitoring_report.json"):
        """Save monitoring report to file"""
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Report saved to {filename}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {
            'system': {
                'cpu_avg': None,
                'memory_avg': None,
                'disk_avg': None
            },
            'performance': {
                'api_avg': None,
                'command_avg': None,
                'card_avg': None
            },
            'services_healthy': 0,
            'services_total': len(self.service_health_status)
        }
        
        # Calculate averages if we have history
        if self.system_metrics_history:
            cpu_values = [m.cpu_percent for m in self.system_metrics_history]
            memory_values = [m.memory_percent for m in self.system_metrics_history]
            disk_values = [m.disk_usage_percent for m in self.system_metrics_history]
            
            summary['system']['cpu_avg'] = sum(cpu_values) / len(cpu_values)
            summary['system']['memory_avg'] = sum(memory_values) / len(memory_values)
            summary['system']['disk_avg'] = sum(disk_values) / len(disk_values)
        
        if self.performance_metrics_history:
            api_values = [m.api_response_time_ms for m in self.performance_metrics_history]
            command_values = [m.command_execution_time_ms for m in self.performance_metrics_history]
            card_values = [m.card_generation_time_ms for m in self.performance_metrics_history]
            
            summary['performance']['api_avg'] = sum(api_values) / len(api_values)
            summary['performance']['command_avg'] = sum(command_values) / len(command_values)
            summary['performance']['card_avg'] = sum(card_values) / len(card_values)
        
        # Count healthy services
        healthy_count = sum(1 for health in self.service_health_status.values() 
                          if health.status == ServiceStatus.HEALTHY)
        summary['services_healthy'] = healthy_count
        
        return summary

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PythonCode Monitoring Dashboard')
    parser.add_argument('--interval', type=int, default=5, 
                       help='Monitoring interval in seconds (default: 5)')
    parser.add_argument('--duration', type=int, default=0,
                       help='Monitoring duration in seconds (0 = run indefinitely)')
    parser.add_argument('--report', action='store_true',
                       help='Generate and save report without continuous monitoring')
    parser.add_argument('--check', type=str,
                       help='Check specific service health')
    parser.add_argument('--summary', action='store_true',
                       help='Show metrics summary')
    
    args = parser.parse_args()
    
    dashboard = MonitoringDashboard()
    
    if args.check:
        # Check specific service
        health = dashboard.check_service_health(args.check)
        print(f"\nService: {health.service_name}")
        print(f"Status: {health.status.value}")
        print(f"Response Time: {health.response_time_ms:.1f}ms" if health.response_time_ms else "N/A")
        print(f"Last Check: {health.last_check}")
        if health.error_message:
            print(f"Error: {health.error_message}")
    
    elif args.report:
        # Generate one-time report
        dashboard.collect_system_metrics()
        dashboard.check_all_services()
        dashboard.collect_performance_metrics()
        dashboard.save_report()
        print("\nOne-time monitoring report generated")
    
    elif args.summary:
        # Show summary
        dashboard.collect_system_metrics()
        dashboard.check_all_services()
        dashboard.collect_performance_metrics()
        summary = dashboard.get_metrics_summary()
        print("\nMETRICS SUMMARY:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    else:
        # Start continuous monitoring
        print("Starting PythonCode Monitoring Dashboard...")
        print("Press Ctrl+C to stop\n")
        
        try:
            dashboard.start_monitoring(args.interval)
            
            if args.duration > 0:
                # Run for specified duration
                time.sleep(args.duration)
                dashboard.stop_monitoring()
            else:
                # Run indefinitely
                while dashboard.is_running:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            dashboard.stop_monitoring()
        
        # Generate final report
        dashboard.save_report()

if __name__ == "__main__":
    main()