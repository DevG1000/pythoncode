#!/usr/bin/env python
"""
Windows CMD命令执行Agent (重构版)
使用单一职责原则重构的模块化设计
"""

import sys
import os
import logging

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CmdAgent:
    """重构后的CMD Agent - 协调各个服务"""
    
    def __init__(self):
        """初始化Agent"""
        from services.command_executor import CommandExecutor
        from services.task_monitor import TaskMonitor
        from services.system_stats import SystemStatsService
        from services.task_cleanup import TaskCleanupService
        
        self.agent_id = f"agent_{int(os.times().elapsed)}"
        self.start_time = os.times().elapsed
        
        # 初始化各个服务
        self.executor = CommandExecutor()
        self.monitor = TaskMonitor()
        self.stats_service = SystemStatsService()
        self.cleanup_service = TaskCleanupService()
        
        logger.info(f"[AGENT] CMD Agent启动 (重构版): {self.agent_id}")
        logger.info(f"[AGENT] 服务初始化完成:")
        logger.info(f"[AGENT]   - CommandExecutor: {self.executor.executor_id}")
        logger.info(f"[AGENT]   - TaskMonitor: {self.monitor.monitor_id}")
        logger.info(f"[AGENT]   - SystemStatsService: {self.stats_service.stats_id}")
        logger.info(f"[AGENT]   - TaskCleanupService: {self.cleanup_service.cleanup_id}")
    
    def execute_single_command(self, command: str, timeout: int = 15, 
                              working_dir: str = ".", wait_for_result: bool = True):
        """
        执行单个命令
        
        参数:
            command: 要执行的命令
            timeout: 超时时间（秒）
            working_dir: 工作目录
            wait_for_result: 是否等待结果
            
        返回:
            执行结果
        """
        logger.info(f"[AGENT] 执行单个命令: {command}")
        
        # 使用CommandExecutor执行命令
        result = self.executor.execute_single(
            command=command,
            timeout=timeout,
            working_dir=working_dir,
            wait_for_result=wait_for_result
        )
        
        # 如果需要等待结果，使用TaskMonitor等待
        if wait_for_result and result.get('status') == 'submitted':
            task_id = result.get('task_id')
            if task_id:
                wait_result = self.monitor.wait_for_task(task_id, timeout + 2)
                return wait_result
        
        return result
    
    def execute_batch_commands(self, commands: list, timeout: int = 15,
                              working_dir: str = ".", max_concurrent: int = 7):
        """
        批量执行命令
        
        参数:
            commands: 命令列表
            timeout: 超时时间（秒）
            working_dir: 工作目录
            max_concurrent: 最大并发数
            
        返回:
            执行结果列表
        """
        logger.info(f"[AGENT] 批量执行 {len(commands)} 个命令")
        
        # 使用CommandExecutor执行批量命令
        return self.executor.execute_batch(
            commands=commands,
            timeout=timeout,
            working_dir=working_dir,
            max_concurrent=max_concurrent
        )
    
    def get_task_status(self, task_id: str):
        """
        获取任务状态
        
        参数:
            task_id: 任务ID
            
        返回:
            任务状态
        """
        logger.info(f"[AGENT] 获取任务状态: {task_id}")
        
        # 使用TaskMonitor获取任务状态
        return self.monitor.get_task_status(task_id)
    
    def get_system_stats(self):
        """
        获取系统统计信息
        
        返回:
            系统统计信息
        """
        logger.info(f"[AGENT] 获取系统统计信息")
        
        # 使用SystemStatsService获取统计信息
        return self.stats_service.get_system_stats()
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """
        清理旧任务
        
        参数:
            max_age_hours: 最大任务年龄（小时）
            
        返回:
            清理结果
        """
        logger.info(f"[AGENT] 清理超过 {max_age_hours} 小时的旧任务")
        
        # 使用TaskCleanupService清理任务
        return self.cleanup_service.cleanup_old_tasks(max_age_hours)
    
    def get_health_status(self):
        """
        获取系统健康状态
        
        返回:
            健康状态
        """
        logger.info(f"[AGENT] 获取系统健康状态")
        
        # 使用SystemStatsService获取健康状态
        return self.stats_service.get_health_status()
    
    def shutdown(self):
        """
        关闭Agent
        
        返回:
            关闭结果
        """
        logger.info(f"[AGENT] 关闭Agent")
        
        # 清理任务
        cleanup_result = self.cleanup_service.shutdown()
        
        result = {
            'agent_id': self.agent_id,
            'shutdown_time': os.times().elapsed,
            'uptime_seconds': os.times().elapsed - self.start_time,
            'cleanup_result': cleanup_result,
            'status': 'shutdown_complete'
        }
        
        logger.info(f"[AGENT] Agent已关闭: {self.agent_id}")
        return result


def main():
    """主函数 - 兼容旧版CLI接口"""
    from cli.cmd_cli import main as cli_main
    return cli_main()


if __name__ == "__main__":
    sys.exit(main())