"""
Task Monitor Service
Responsibility: Monitor task status and wait for completion
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..async_tasks import get_async_task_status

logger = logging.getLogger(__name__)


class TaskMonitor:
    """Monitors task status and waits for completion"""
    
    def __init__(self):
        """Initialize task monitor"""
        self.monitor_id = f"monitor_{int(datetime.now().timestamp())}"
        logger.info(f"[MONITOR] Task Monitor启动: {self.monitor_id}")
    
    def wait_for_task(self, task_id: str, max_wait_time: int = 30) -> Dict[str, Any]:
        """
        Wait for task completion
        
        Args:
            task_id: Task ID to wait for
            max_wait_time: Maximum wait time in seconds
            
        Returns:
            Task result dictionary
        """
        logger.info(f"[MONITOR] 等待任务完成: {task_id}")
        logger.info(f"[MONITOR] 最大等待时间: {max_wait_time}秒")
        
        start_time = time.time()
        check_interval = 0.5  # Check every 0.5 seconds
        
        while time.time() - start_time < max_wait_time:
            task_status = get_async_task_status(task_id)
            
            if not task_status:
                logger.warning(f"[MONITOR] 任务不存在: {task_id}")
                return {
                    'task_id': task_id,
                    'status': 'error',
                    'error': 'Task not found'
                }
            
            status = task_status.get('status')
            
            if status == 'completed':
                logger.info(f"[MONITOR] 任务完成: {task_id}")
                return {
                    'task_id': task_id,
                    'status': 'completed',
                    'result': task_status.get('result'),
                    'execution_time': task_status.get('execution_time'),
                    'completed_at': task_status.get('completed_at')
                }
            
            elif status == 'failed':
                logger.error(f"[MONITOR] 任务失败: {task_id}")
                return {
                    'task_id': task_id,
                    'status': 'failed',
                    'error': task_status.get('error'),
                    'failed_at': task_status.get('completed_at')
                }
            
            elif status == 'running':
                # Task is still running, continue waiting
                elapsed = time.time() - start_time
                if elapsed % 5 < check_interval:  # Log every 5 seconds
                    logger.info(f"[MONITOR] 任务运行中: {task_id} (已等待 {elapsed:.1f}秒)")
            
            time.sleep(check_interval)
        
        # Timeout reached
        logger.warning(f"[MONITOR] 任务等待超时: {task_id}")
        return {
            'task_id': task_id,
            'status': 'timeout',
            'error': f'Task timeout after {max_wait_time} seconds',
            'waited_for': max_wait_time
        }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get task status
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status dictionary
        """
        try:
            task_status = get_async_task_status(task_id)
            if task_status:
                logger.info(f"[MONITOR] 获取任务状态: {task_id} - {task_status.get('status')}")
                return task_status
            else:
                logger.warning(f"[MONITOR] 任务不存在: {task_id}")
                return {
                    'task_id': task_id,
                    'status': 'not_found',
                    'error': 'Task not found'
                }
        except Exception as e:
            logger.error(f"[MONITOR] 获取任务状态失败: {e}")
            return {
                'task_id': task_id,
                'status': 'error',
                'error': str(e)
            }
    
    def wait_for_multiple_tasks(self, task_ids: List[str], 
                               max_wait_time: int = 30) -> List[Dict[str, Any]]:
        """
        Wait for multiple tasks to complete
        
        Args:
            task_ids: List of task IDs
            max_wait_time: Maximum wait time in seconds
            
        Returns:
            List of task results
        """
        logger.info(f"[MONITOR] 等待多个任务完成: {len(task_ids)} 个任务")
        
        results = []
        remaining_tasks = task_ids.copy()
        start_time = time.time()
        
        while remaining_tasks and (time.time() - start_time < max_wait_time):
            completed_tasks = []
            
            for task_id in remaining_tasks:
                task_status = get_async_task_status(task_id)
                
                if not task_status:
                    results.append({
                        'task_id': task_id,
                        'status': 'not_found',
                        'error': 'Task not found'
                    })
                    completed_tasks.append(task_id)
                    continue
                
                status = task_status.get('status')
                
                if status in ['completed', 'failed']:
                    results.append({
                        'task_id': task_id,
                        'status': status,
                        'result': task_status.get('result') if status == 'completed' else None,
                        'error': task_status.get('error') if status == 'failed' else None,
                        'execution_time': task_status.get('execution_time')
                    })
                    completed_tasks.append(task_id)
            
            # Remove completed tasks
            for task_id in completed_tasks:
                remaining_tasks.remove(task_id)
            
            if remaining_tasks:
                time.sleep(0.5)  # Wait before checking again
        
        # Handle timeout for remaining tasks
        for task_id in remaining_tasks:
            results.append({
                'task_id': task_id,
                'status': 'timeout',
                'error': f'Task timeout after {max_wait_time} seconds'
            })
        
        logger.info(f"[MONITOR] 多个任务等待完成: {len(results)} 个结果")
        return results