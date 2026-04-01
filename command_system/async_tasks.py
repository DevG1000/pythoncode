"""
异步任务处理模块
用于处理耗时的后台任务，如邮箱发送
"""
import threading
import queue
import time
import logging
from typing import Callable, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import traceback

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AsyncTask:
    """异步任务"""
    id: str
    func: Callable
    args: tuple
    kwargs: dict
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    
    def execute(self):
        """执行任务"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
        
        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.status = TaskStatus.COMPLETED
            logger.info(f"任务 {self.id} 执行成功")
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            logger.error(f"任务 {self.id} 执行失败: {e}")
            logger.debug(traceback.format_exc())
        finally:
            self.completed_at = datetime.now()
    
    def get_execution_time(self) -> Optional[float]:
        """获取执行时间（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        execution_time = self.get_execution_time()
        
        return {
            'id': self.id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'execution_time': execution_time,
            'error': self.error,
            'result': self.result
        }

class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_workers: int = 3, max_queue_size: int = 100):
        """
        初始化任务管理器
        
        参数:
            max_workers: 最大工作线程数
            max_queue_size: 最大队列大小
        """
        self.task_queue = queue.Queue(maxsize=max_queue_size)
        self.workers = []
        self.tasks = {}  # 任务ID -> 任务对象
        self.is_running = False
        self.max_workers = max_workers
        
        # 统计信息
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'pending_tasks': 0,
        }
    
    def start(self):
        """启动任务管理器"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info(f"启动异步任务管理器，工作线程数: {self.max_workers}")
        
        # 创建工作线程
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"AsyncWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """停止任务管理器"""
        self.is_running = False
        logger.info("停止异步任务管理器")
        
        # 清空队列
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
            except queue.Empty:
                break
    
    def _worker_loop(self):
        """工作线程循环"""
        thread_name = threading.current_thread().name
        logger.debug(f"工作线程启动: {thread_name}")
        
        while self.is_running:
            try:
                # 获取任务（阻塞，最多等待1秒）
                task = self.task_queue.get(timeout=1)
                
                # 执行任务
                logger.debug(f"{thread_name} 执行任务: {task.id}")
                task.execute()
                
                # 更新统计
                self._update_stats(task)
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except queue.Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                logger.error(f"工作线程错误: {e}")
    
    def _update_stats(self, task: AsyncTask):
        """更新统计信息"""
        if task.status == TaskStatus.COMPLETED:
            self.stats['completed_tasks'] += 1
        elif task.status == TaskStatus.FAILED:
            self.stats['failed_tasks'] += 1
        
        self.stats['pending_tasks'] = self.task_queue.qsize()
    
    def submit(self, func: Callable, *args, **kwargs) -> str:
        """
        提交异步任务
        
        参数:
            func: 要执行的函数，或者一个AsyncTask实例
            *args, **kwargs: 函数参数（如果func是Callable）
        
        返回:
            任务ID
        """
        import uuid
        
        # 检查func是否已经是AsyncTask实例
        if isinstance(func, AsyncTask):
            # 如果已经是AsyncTask实例，直接使用
            task = func
            task_id = task.id
            
            # 确保任务有ID
            if not task_id:
                task_id = str(uuid.uuid4())[:8]
                task.id = task_id
        else:
            # 传统方式：创建新的AsyncTask
            task_id = str(uuid.uuid4())[:8]
            task = AsyncTask(
                id=task_id,
                func=func,
                args=args,
                kwargs=kwargs,
                created_at=datetime.now()
            )
        
        # 添加到任务字典
        self.tasks[task_id] = task
        
        try:
            # 添加到队列
            self.task_queue.put(task, block=True, timeout=5)
            self.stats['total_tasks'] += 1
            self.stats['pending_tasks'] = self.task_queue.qsize()
            
            logger.debug(f"任务提交成功: {task_id}")
            return task_id
            
        except queue.Full:
            error_msg = "任务队列已满，无法提交新任务"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """
        获取任务状态
        
        参数:
            task_id: 任务ID
        
        返回:
            任务状态字典或None
        """
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        # 使用任务的to_dict方法
        status_dict = task.to_dict()
        
        # 确保包含所有必要字段
        if 'result' not in status_dict:
            status_dict['result'] = task.result
        
        return status_dict
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            'active_workers': len([w for w in self.workers if w.is_alive()]),
            'queue_size': self.task_queue.qsize(),
            'total_tasks_in_memory': len(self.tasks),
        }
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务记录"""
        cutoff_time = datetime.now() - time.timedelta(hours=max_age_hours)
        old_task_ids = []
        
        for task_id, task in self.tasks.items():
            if task.completed_at and task.completed_at < cutoff_time:
                old_task_ids.append(task_id)
        
        for task_id in old_task_ids:
            del self.tasks[task_id]
        
        if old_task_ids:
            logger.info(f"清理了 {len(old_task_ids)} 个旧任务记录")

# 全局任务管理器实例
try:
    from config import Config
    # 使用配置中的参数
    task_manager = AsyncTaskManager(
        max_workers=Config.CMD_MAX_WORKERS,
        max_queue_size=Config.CMD_MAX_QUEUE_SIZE
    )
    logger.info(f"使用配置参数创建任务管理器: max_workers={Config.CMD_MAX_WORKERS}, max_queue_size={Config.CMD_MAX_QUEUE_SIZE}")
except (ImportError, AttributeError):
    # 如果config.py不存在或没有相关配置，使用默认值
    task_manager = AsyncTaskManager(max_workers=7, max_queue_size=100)
    logger.info("使用默认参数创建任务管理器: max_workers=7, max_queue_size=100")

def init_async_tasks():
    """初始化异步任务系统"""
    task_manager.start()
    logger.info("异步任务系统初始化完成")

def shutdown_async_tasks():
    """关闭异步任务系统"""
    task_manager.stop()
    logger.info("异步任务系统已关闭")

def submit_async_task(func: Callable, *args, **kwargs) -> str:
    """
    提交异步任务（便捷函数）
    
    参数:
        func: 要执行的函数
        *args, **kwargs: 函数参数
    
    返回:
        任务ID
    """
    return task_manager.submit(func, *args, **kwargs)

def get_async_task_status(task_id: str) -> Optional[dict]:
    """
    获取异步任务状态（便捷函数）
    
    参数:
        task_id: 任务ID
    
    返回:
        任务状态字典或None
    """
    return task_manager.get_task_status(task_id)

def get_async_stats() -> dict:
    """
    获取异步任务统计信息（便捷函数）
    
    返回:
        统计信息字典
    """
    return task_manager.get_stats()

# 命令任务支持函数
def submit_command_task(command: str, timeout: int = 15, working_dir: str = ".") -> str:
    """
    提交命令执行任务
    
    参数:
        command: 要执行的命令字符串
        timeout: 命令执行超时时间（秒），默认15秒
        working_dir: 工作目录，默认当前目录
        
    返回:
        str: 任务ID
    """
    try:
        # 动态导入以避免循环导入
        from cmd_tasks import create_command_task
        
        # 创建命令任务
        task = create_command_task(command, timeout, working_dir)
        
        # 直接提交任务实例（submit方法现在支持AsyncTask实例）
        return task_manager.submit(task)
        
    except ImportError as e:
        logger.error(f"无法导入cmd_tasks模块: {e}")
        raise RuntimeError("CMD任务模块未安装或配置不正确")
    except Exception as e:
        logger.error(f"提交命令任务失败: {e}")
        raise


def get_command_task_status(task_id: str) -> Optional[dict]:
    """
    获取命令任务状态
    
    参数:
        task_id: 任务ID
        
    返回:
        Optional[dict]: 任务状态字典，包含命令执行详情
    """
    status = get_async_task_status(task_id)
    if not status:
        return None
    
    # 这里可以添加命令任务特定的状态信息
    # 在实际实现中，可能需要从任务存储中获取更多信息
    
    return status


def get_command_stats() -> dict:
    """
    获取命令任务统计信息
    
    返回:
        dict: 命令任务统计信息
    """
    stats = get_async_stats()
    
    # 添加命令任务特定的统计信息
    cmd_stats = {
        'cmd_total_tasks': 0,  # 需要从任务历史中统计
        'cmd_completed_tasks': 0,
        'cmd_failed_tasks': 0,
        'cmd_timed_out_tasks': 0,
    }
    
    return {**stats, **cmd_stats}


class AsyncTaskSystem:
    """Async Task System wrapper for dependency injection"""
    
    def __init__(self):
        self.task_manager = None
    
    def init_async_tasks(self):
        """Initialize async task system"""
        global task_manager
        if task_manager is None or not task_manager.is_running:
            task_manager = AsyncTaskManager()
            task_manager.start()
        self.task_manager = task_manager
    
    def submit_task(self, func: callable, *args, **kwargs) -> str:
        """Submit a task for async execution"""
        return submit_async_task(func, *args, **kwargs)
    
    def get_task_status(self, task_id: str) -> dict:
        """Get status of an async task"""
        return get_async_task_status(task_id)
    
    def get_stats(self) -> dict:
        """Get async task system statistics"""
        return get_async_stats()
    
    def shutdown(self) -> None:
        """Shutdown async task system"""
        shutdown_async_tasks()


# 示例任务函数
def example_task(duration: int, task_name: str):
    """示例任务：模拟耗时操作"""
    logger.info(f"开始执行任务: {task_name}，预计耗时: {duration}秒")
    time.sleep(duration)
    logger.info(f"任务完成: {task_name}")
    return f"任务 {task_name} 完成，耗时 {duration}秒"

if __name__ == "__main__":
    # 测试异步任务系统
    print("测试异步任务系统...")
    
    # 初始化
    init_async_tasks()
    
    try:
        # 提交测试任务
        task_ids = []
        for i in range(5):
            task_id = submit_async_task(example_task, 2, f"测试任务-{i}")
            task_ids.append(task_id)
            print(f"提交任务: {task_id}")
        
        # 等待任务执行
        print("等待任务执行...")
        time.sleep(3)
        
        # 检查任务状态
        print("\n任务状态:")
        for task_id in task_ids:
            status = get_async_task_status(task_id)
            if status:
                print(f"  {task_id}: {status['status']}")
        
        # 获取统计信息
        print("\n统计信息:")
        stats = get_async_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    finally:
        # 关闭
        shutdown_async_tasks()