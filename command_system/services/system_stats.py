"""
System Statistics Service
Responsibility: Collect and provide system statistics
"""

import logging
import psutil
from typing import Dict, Any
from datetime import datetime
from ..async_tasks import get_async_stats

logger = logging.getLogger(__name__)


class SystemStatsService:
    """Collects and provides system statistics"""
    
    def __init__(self):
        """Initialize system stats service"""
        self.stats_id = f"stats_{int(datetime.now().timestamp())}"
        self.start_time = datetime.now()
        logger.info(f"[STATS] System Stats Service启动: {self.stats_id}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive system statistics
        
        Returns:
            System statistics dictionary
        """
        logger.info(f"[STATS] 获取系统统计信息")
        
        try:
            # Get async task stats
            async_stats = get_async_stats()
            
            # Get system resource stats
            system_stats = self._get_system_resource_stats()
            
            # Get process stats
            process_stats = self._get_process_stats()
            
            # Combine all stats
            stats = {
                'service_id': self.stats_id,
                'service_start_time': self.start_time.isoformat(),
                'current_time': datetime.now().isoformat(),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                'async_tasks': async_stats,
                'system_resources': system_stats,
                'process_info': process_stats,
                'status': 'healthy'
            }
            
            logger.info(f"[STATS] 系统统计信息获取完成")
            return stats
            
        except Exception as e:
            logger.error(f"[STATS] 获取系统统计信息失败: {e}")
            return {
                'service_id': self.stats_id,
                'status': 'error',
                'error': str(e),
                'current_time': datetime.now().isoformat()
            }
    
    def _get_system_resource_stats(self) -> Dict[str, Any]:
        """Get system resource statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory usage
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk usage
            disk = psutil.disk_usage('.')
            
            # Network
            net_io = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency_current': cpu_freq.current if cpu_freq else None,
                    'frequency_min': cpu_freq.min if cpu_freq else None,
                    'frequency_max': cpu_freq.max if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            }
        except Exception as e:
            logger.warning(f"[STATS] 获取系统资源统计失败: {e}")
            return {
                'error': str(e),
                'status': 'partial'
            }
    
    def _get_process_stats(self) -> Dict[str, Any]:
        """Get current process statistics"""
        try:
            process = psutil.Process()
            
            with process.oneshot():
                cpu_times = process.cpu_times()
                memory_info = process.memory_info()
                memory_percent = process.memory_percent()
                create_time = process.create_time()
                num_threads = process.num_threads()
                
                # Get open files count
                try:
                    open_files = len(process.open_files())
                except (psutil.AccessDenied, psutil.ZombieProcess):
                    open_files = None
                
                # Get connections count
                try:
                    connections = len(process.connections())
                except (psutil.AccessDenied, psutil.ZombieProcess):
                    connections = None
            
            return {
                'pid': process.pid,
                'name': process.name(),
                'status': process.status(),
                'create_time': datetime.fromtimestamp(create_time).isoformat(),
                'cpu_times': {
                    'user': cpu_times.user,
                    'system': cpu_times.system,
                    'children_user': cpu_times.children_user,
                    'children_system': cpu_times.children_system
                },
                'memory': {
                    'rss': memory_info.rss,
                    'vms': memory_info.vms,
                    'percent': memory_percent
                },
                'threads': num_threads,
                'open_files': open_files,
                'connections': connections
            }
        except Exception as e:
            logger.warning(f"[STATS] 获取进程统计失败: {e}")
            return {
                'error': str(e),
                'status': 'partial'
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the system
        
        Returns:
            Health status dictionary
        """
        stats = self.get_system_stats()
        
        # Determine health status based on various metrics
        health_status = 'healthy'
        warnings = []
        
        # Check CPU usage
        cpu_percent = stats.get('system_resources', {}).get('cpu', {}).get('percent', 0)
        if cpu_percent > 80:
            warnings.append(f"CPU usage high: {cpu_percent}%")
            health_status = 'warning'
        
        # Check memory usage
        memory_percent = stats.get('system_resources', {}).get('memory', {}).get('percent', 0)
        if memory_percent > 85:
            warnings.append(f"Memory usage high: {memory_percent}%")
            health_status = 'warning'
        
        # Check disk usage
        disk_percent = stats.get('system_resources', {}).get('disk', {}).get('percent', 0)
        if disk_percent > 90:
            warnings.append(f"Disk usage high: {disk_percent}%")
            health_status = 'warning'
        
        return {
            'status': health_status,
            'timestamp': datetime.now().isoformat(),
            'warnings': warnings,
            'metrics': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent
            }
        }