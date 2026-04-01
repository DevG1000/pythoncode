"""
Command Executor Service
Responsibility: Execute single and batch commands
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from ..async_tasks import submit_command_task, init_async_tasks

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Executes single and batch commands"""
    
    def __init__(self):
        """Initialize command executor"""
        self.command_history: List[Dict[str, Any]] = []
        self.executor_id = f"executor_{int(datetime.now().timestamp())}"
        logger.info(f"[EXECUTOR] Command Executor启动: {self.executor_id}")
    
    def execute_single(self, command: str, timeout: int = 15, 
                      working_dir: str = ".", wait_for_result: bool = True) -> Dict[str, Any]:
        """
        Execute single command
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
            working_dir: Working directory
            wait_for_result: Whether to wait for result
            
        Returns:
            Execution result dictionary
        """
        logger.info(f"[EXECUTOR] 执行单个命令: {command}")
        logger.info(f"[EXECUTOR] 超时时间: {timeout}秒")
        logger.info(f"[EXECUTOR] 工作目录: {working_dir}")
        
        try:
            # Ensure async task system is running
            init_async_tasks()
            
            # Submit command task
            task_id = submit_command_task(command, timeout, working_dir)
            logger.info(f"[EXECUTOR] 命令任务已提交: {task_id}")
            
            # Record command history
            self._record_command(task_id, command, timeout, working_dir, 'submitted')
            
            if wait_for_result:
                return {
                    'task_id': task_id,
                    'status': 'submitted',
                    'message': f'命令已提交，任务ID: {task_id}'
                }
            else:
                return {
                    'task_id': task_id,
                    'status': 'submitted',
                    'message': f'命令已提交，任务ID: {task_id}'
                }
                
        except Exception as e:
            logger.error(f"[EXECUTOR] 执行命令失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'command': command
            }
    
    def execute_batch(self, commands: List[str], timeout: int = 15,
                     working_dir: str = ".", max_concurrent: int = 7) -> List[Dict[str, Any]]:
        """
        Execute batch commands
        
        Args:
            commands: List of commands to execute
            timeout: Timeout in seconds for each command
            working_dir: Working directory
            max_concurrent: Maximum concurrent commands
            
        Returns:
            List of execution results
        """
        logger.info(f"[EXECUTOR] 批量执行 {len(commands)} 个命令")
        logger.info(f"[EXECUTOR] 最大并发数: {max_concurrent}")
        logger.info(f"[EXECUTOR] 超时时间: {timeout}秒")
        
        results = []
        task_ids = []
        
        try:
            # Ensure async task system is running
            init_async_tasks()
            
            # Submit commands in batches
            for i, command in enumerate(commands):
                if len(task_ids) >= max_concurrent:
                    # Wait for some tasks to complete
                    self._wait_for_some_tasks(task_ids, results)
                
                # Submit command
                task_id = submit_command_task(command, timeout, working_dir)
                task_ids.append(task_id)
                
                # Record command history
                self._record_command(task_id, command, timeout, working_dir, 'submitted')
                
                logger.info(f"[EXECUTOR] 命令 {i+1}/{len(commands)} 已提交: {task_id}")
            
            # Wait for remaining tasks
            self._wait_for_remaining_tasks(task_ids, results)
            
            logger.info(f"[EXECUTOR] 批量执行完成，成功: {len([r for r in results if r.get('status') == 'completed'])}")
            
        except Exception as e:
            logger.error(f"[EXECUTOR] 批量执行失败: {e}")
            results.append({
                'status': 'error',
                'error': str(e),
                'message': '批量执行过程中发生错误'
            })
        
        return results
    
    def _record_command(self, task_id: str, command: str, timeout: int, 
                       working_dir: str, status: str) -> None:
        """Record command in history"""
        self.command_history.append({
            'task_id': task_id,
            'command': command,
            'timeout': timeout,
            'working_dir': working_dir,
            'submitted_at': datetime.now().isoformat(),
            'status': status
        })
    
    def _wait_for_some_tasks(self, task_ids: List[str], results: List[Dict[str, Any]]) -> None:
        """Wait for some tasks to complete (internal helper)"""
        # This would be implemented with actual task waiting logic
        # For now, it's a placeholder
        pass
    
    def _wait_for_remaining_tasks(self, task_ids: List[str], results: List[Dict[str, Any]]) -> None:
        """Wait for remaining tasks to complete (internal helper)"""
        # This would be implemented with actual task waiting logic
        # For now, it's a placeholder
        pass
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get command execution history"""
        return self.command_history.copy()