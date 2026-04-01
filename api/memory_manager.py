"""
内存管理模块
用于监控和优化内存使用
"""
import gc
import psutil
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)

class MemoryMonitor:
    """内存监控器"""
    
    def __init__(self, warning_threshold_mb: int = 500, critical_threshold_mb: int = 800):
        """
        初始化内存监控器
        
        参数:
            warning_threshold_mb: 警告阈值（MB）
            critical_threshold_mb: 严重阈值（MB）
        """
        self.warning_threshold = warning_threshold_mb
        self.critical_threshold = critical_threshold_mb
        self.process = psutil.Process(os.getpid())
        self.monitoring = False
        self.monitor_thread = None
        
        # 统计信息
        self.stats = {
            'peak_memory_mb': 0,
            'gc_collections': 0,
            'memory_warnings': 0,
            'last_check': None,
        }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """获取当前内存信息"""
        memory_info = self.process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # 常驻内存
            'vms_mb': memory_info.vms / 1024 / 1024,  # 虚拟内存
            'percent': self.process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024,
            'total_mb': psutil.virtual_memory().total / 1024 / 1024,
            'timestamp': datetime.now().isoformat(),
        }
    
    def check_memory_usage(self) -> Dict[str, Any]:
        """检查内存使用情况"""
        memory_info = self.get_memory_info()
        rss_mb = memory_info['rss_mb']
        
        # 更新峰值内存
        if rss_mb > self.stats['peak_memory_mb']:
            self.stats['peak_memory_mb'] = rss_mb
        
        # 检查阈值
        status = 'normal'
        if rss_mb >= self.critical_threshold:
            status = 'critical'
            self.stats['memory_warnings'] += 1
            logger.warning(f"内存使用严重: {rss_mb:.1f}MB (阈值: {self.critical_threshold}MB)")
        elif rss_mb >= self.warning_threshold:
            status = 'warning'
            self.stats['memory_warnings'] += 1
            logger.warning(f"内存使用警告: {rss_mb:.1f}MB (阈值: {self.warning_threshold}MB)")
        
        memory_info['status'] = status
        self.stats['last_check'] = datetime.now().isoformat()
        
        return memory_info
    
    def force_garbage_collection(self) -> Dict[str, Any]:
        """强制垃圾回收"""
        logger.info("执行强制垃圾回收")
        
        # 获取回收前的内存
        memory_before = self.get_memory_info()
        
        # 执行垃圾回收
        collected = gc.collect()
        
        # 获取回收后的内存
        memory_after = self.get_memory_info()
        
        # 更新统计
        self.stats['gc_collections'] += 1
        
        result = {
            'collected_objects': collected,
            'memory_before_mb': memory_before['rss_mb'],
            'memory_after_mb': memory_after['rss_mb'],
            'memory_freed_mb': memory_before['rss_mb'] - memory_after['rss_mb'],
            'timestamp': datetime.now().isoformat(),
        }
        
        logger.info(f"垃圾回收完成: 回收了 {collected} 个对象，释放了 {result['memory_freed_mb']:.1f}MB 内存")
        
        return result
    
    def start_monitoring(self, interval_seconds: int = 30):
        """启动内存监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            name="MemoryMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info(f"内存监控已启动，检查间隔: {interval_seconds}秒")
    
    def stop_monitoring(self):
        """停止内存监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("内存监控已停止")
    
    def _monitor_loop(self, interval_seconds: int):
        """监控循环"""
        logger.debug("内存监控循环开始")
        
        while self.monitoring:
            try:
                memory_info = self.check_memory_usage()
                
                # 如果内存使用严重，尝试垃圾回收
                if memory_info['status'] == 'critical':
                    self.force_garbage_collection()
                
                # 等待下一次检查
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"内存监控错误: {e}")
                time.sleep(interval_seconds)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            'monitoring': self.monitoring,
            'current_memory': self.get_memory_info(),
        }
    
    def optimize_memory(self) -> Dict[str, Any]:
        """执行内存优化"""
        logger.info("执行内存优化")
        
        results = []
        
        # 1. 强制垃圾回收
        gc_result = self.force_garbage_collection()
        results.append({'action': 'garbage_collection', 'result': gc_result})
        
        # 2. 清理导入模块缓存（谨慎使用）
        try:
            import sys
            modules_before = len(sys.modules)
            
            # 只清理非系统、非项目的重要模块
            safe_modules = {'builtins', 'sys', 'os', '__main__'}
            modules_to_keep = set()
            
            for module_name in list(sys.modules.keys()):
                if (module_name.startswith('_') or 
                    module_name in safe_modules or
                    'flask' in module_name.lower() or
                    'sqlalchemy' in module_name.lower() or
                    module_name.startswith('email_service') or
                    module_name.startswith('models') or
                    module_name.startswith('config')):
                    modules_to_keep.add(module_name)
            
            # 实际不删除，只是记录
            logger.info(f"模块缓存: {modules_before} 个模块，{len(modules_to_keep)} 个重要模块")
            
            results.append({
                'action': 'module_cache_check',
                'modules_total': modules_before,
                'modules_important': len(modules_to_keep),
            })
        except Exception as e:
            logger.error(f"清理模块缓存失败: {e}")
            results.append({'action': 'module_cache_check', 'error': str(e)})
        
        # 3. 获取优化后的内存信息
        memory_after = self.get_memory_info()
        
        return {
            'actions': results,
            'memory_after_mb': memory_after['rss_mb'],
            'timestamp': datetime.now().isoformat(),
        }

class ResourceManager:
    """资源管理器"""
    
    def __init__(self):
        self.memory_monitor = MemoryMonitor()
        self.open_files = {}
        self.open_connections = {}
    
    def track_file(self, file_path: str, file_obj):
        """跟踪打开的文件"""
        self.open_files[file_path] = {
            'object': file_obj,
            'opened_at': datetime.now().isoformat(),
            'access_count': 0,
        }
    
    def untrack_file(self, file_path: str):
        """取消跟踪文件"""
        if file_path in self.open_files:
            del self.open_files[file_path]
    
    def track_connection(self, connection_id: str, connection_obj):
        """跟踪数据库连接"""
        self.open_connections[connection_id] = {
            'object': connection_obj,
            'opened_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
        }
    
    def update_connection_usage(self, connection_id: str):
        """更新连接使用时间"""
        if connection_id in self.open_connections:
            self.open_connections[connection_id]['last_used'] = datetime.now().isoformat()
    
    def close_idle_connections(self, max_idle_minutes: int = 30):
        """关闭空闲连接（示例，实际需要具体实现）"""
        logger.info("检查空闲连接...")
        # 这里需要根据具体的连接对象实现关闭逻辑
    
    def get_resource_info(self) -> Dict[str, Any]:
        """获取资源信息"""
        return {
            'memory': self.memory_monitor.get_stats(),
            'open_files': len(self.open_files),
            'open_connections': len(self.open_connections),
            'timestamp': datetime.now().isoformat(),
        }

# 全局资源管理器实例
resource_manager = ResourceManager()

def init_memory_monitoring(interval_seconds: int = 60):
    """初始化内存监控"""
    resource_manager.memory_monitor.start_monitoring(interval_seconds)
    logger.info(f"内存监控初始化完成，检查间隔: {interval_seconds}秒")

def shutdown_memory_monitoring():
    """关闭内存监控"""
    resource_manager.memory_monitor.stop_monitoring()
    logger.info("内存监控已关闭")

def get_memory_info() -> Dict[str, Any]:
    """获取内存信息（便捷函数）"""
    return resource_manager.memory_monitor.get_memory_info()

def check_memory_usage() -> Dict[str, Any]:
    """检查内存使用（便捷函数）"""
    return resource_manager.memory_monitor.check_memory_usage()

def force_garbage_collection() -> Dict[str, Any]:
    """强制垃圾回收（便捷函数）"""
    return resource_manager.memory_monitor.force_garbage_collection()

def optimize_memory() -> Dict[str, Any]:
    """执行内存优化（便捷函数）"""
    return resource_manager.memory_monitor.optimize_memory()

def get_resource_info() -> Dict[str, Any]:
    """获取资源信息（便捷函数）"""
    return resource_manager.get_resource_info()

if __name__ == "__main__":
    # 测试内存管理
    print("测试内存管理模块...")
    
    # 初始化监控
    init_memory_monitoring(interval_seconds=10)
    
    try:
        # 获取初始内存信息
        print("\n初始内存信息:")
        mem_info = get_memory_info()
        for key, value in mem_info.items():
            if key != 'timestamp':
                print(f"  {key}: {value}")
        
        # 模拟内存使用
        print("\n模拟内存使用...")
        data = []
        for i in range(100000):
            data.append([f"test_{i}" * 10] * 100)
        
        # 检查内存使用
        print("\n使用后内存信息:")
        mem_info = check_memory_usage()
        for key, value in mem_info.items():
            if key != 'timestamp':
                print(f"  {key}: {value}")
        
        # 强制垃圾回收
        print("\n执行垃圾回收...")
        gc_result = force_garbage_collection()
        print(f"  回收对象: {gc_result['collected_objects']}")
        print(f"  释放内存: {gc_result['memory_freed_mb']:.1f}MB")
        
        # 等待监控检查
        print("\n等待监控检查...")
        time.sleep(15)
        
        # 获取统计信息
        print("\n内存统计信息:")
        stats = resource_manager.memory_monitor.get_stats()
        for key, value in stats.items():
            if key != 'current_memory':
                print(f"  {key}: {value}")
        
    finally:
        # 关闭监控
        shutdown_memory_monitoring()
        print("\n测试完成")