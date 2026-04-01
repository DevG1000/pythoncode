"""
CMD命令任务扩展模块
扩展现有异步任务系统以支持Windows CMD命令执行
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from command_system.async_tasks import AsyncTask, TaskStatus
from command_system.command_executor import CommandExecutor, CommandResult, CommandStatus

logger = logging.getLogger(__name__)


class CommandTask(AsyncTask):
    """CMD命令执行任务"""
    
    def __init__(self, command: str, timeout: int = 15, working_dir: str = ".", **kwargs):
        """
        初始化命令任�?        
        参数:
            command: 要执行的命令字符�?            timeout: 命令执行超时时间（秒），默认15�?            working_dir: 工作目录，默认当前目�?            **kwargs: 传递给父类的其他参�?        """
        # 如果未提供id，生成一�?        if 'id' not in kwargs:
            kwargs['id'] = f"cmd_{str(uuid.uuid4())[:8]}"
        
        # 如果未提供created_at，使用当前时�?        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.now()
        
        # 设置默认的函数和参数
        if 'func' not in kwargs:
            # 使用lambda函数，稍后在execute方法中替�?            kwargs['func'] = lambda: None
        if 'args' not in kwargs:
            kwargs['args'] = ()
        if 'kwargs' not in kwargs:
            kwargs['kwargs'] = {}
        
        super().__init__(**kwargs)
        
        self.command = command
        self.timeout = timeout
        self.working_dir = working_dir
        self.executor = CommandExecutor(timeout=timeout, working_dir=working_dir)
        self.command_result: Optional[CommandResult] = None
        
        # 现在设置正确的函�?        self.func = self._execute_command
    
    def _execute_command(self) -> CommandResult:
        """执行命令的内部函�?""
        return self.executor.execute(self.command, self.working_dir)
    
    def execute(self):
        """执行命令任务（重写父类方法）"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
        
        logger.info(f"[CMD-TASK] 开始执行命令任�? {self.id}")
        logger.info(f"[CMD-TASK] 命令: {self.command}")
        logger.info(f"[CMD-TASK] 超时时间: {self.timeout}�?)
        logger.info(f"[CMD-TASK] 工作目录: {self.working_dir}")
        
        try:
            # 执行命令
            self.command_result = self._execute_command()
            
            # 根据命令执行结果更新任务状�?            if self.command_result.status == CommandStatus.COMPLETED:
                self.status = TaskStatus.COMPLETED
                self.result = self.command_result.to_dict()
                logger.info(f"[CMD-TASK] 命令任务完成: {self.id}")
                logger.info(f"[CMD-TASK] 命令: {self.command}")
                logger.info(f"[CMD-TASK] 退出码: {self.command_result.exit_code}")
                logger.info(f"[CMD-TASK] 执行时间: {self.command_result.execution_time:.2f}�?)
                
            elif self.command_result.status == CommandStatus.TIMEOUT:
                self.status = TaskStatus.FAILED
                self.error = f"命令执行超时，超时时�? {self.timeout}�?
                self.result = self.command_result.to_dict()
                logger.warning(f"[CMD-TASK] 命令任务超时: {self.id}")
                logger.warning(f"[CMD-TASK] 命令: {self.command}")
                logger.warning(f"[CMD-TASK] 超时时间: {self.timeout}�?)
                logger.warning(f"[CMD-TASK] 实际执行时间: {self.command_result.execution_time:.2f}�?)
                
            else:  # FAILED 或其他状�?                self.status = TaskStatus.FAILED
                self.error = self.command_result.stderr or "命令执行失败"
                self.result = self.command_result.to_dict()
                logger.error(f"[CMD-TASK] 命令任务失败: {self.id}")
                logger.error(f"[CMD-TASK] 命令: {self.command}")
                logger.error(f"[CMD-TASK] 退出码: {self.command_result.exit_code}")
                logger.error(f"[CMD-TASK] 错误信息: {self.error[:200]}...")
                logger.error(f"[CMD-TASK] 执行时间: {self.command_result.execution_time:.2f}�?)
                
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            logger.error(f"[CMD-TASK] 命令任务执行异常: {self.id}")
            logger.error(f"[CMD-TASK] 命令: {self.command}")
            logger.error(f"[CMD-TASK] 异常信息: {e}")
            
        finally:
            self.completed_at = datetime.now()
            execution_time = self.get_execution_time() or 0
            logger.info(f"[CMD-TASK] 命令任务结束: {self.id}")
            logger.info(f"[CMD-TASK] 最终状�? {self.status.value}")
            logger.info(f"[CMD-TASK] 总执行时�? {execution_time:.2f}�?)
    
    def get_command_result(self) -> Optional[CommandResult]:
        """获取命令执行结果"""
        return self.command_result
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（扩展父类方法�?""
        base_dict = super().to_dict() if hasattr(super(), 'to_dict') else {}
        
        command_dict = {
            'command': self.command,
            'timeout': self.timeout,
            'working_dir': self.working_dir,
            'command_result': self.command_result.to_dict() if self.command_result else None
        }
        
        # 合并基础信息和命令信�?        result = {**base_dict, **command_dict}
        
        # 确保必要的字段存�?        if 'id' not in result:
            result['id'] = self.id
        if 'status' not in result:
            result['status'] = self.status.value
        if 'created_at' not in result:
            result['created_at'] = self.created_at.isoformat() if self.created_at else None
        if 'started_at' not in result:
            result['started_at'] = self.started_at.isoformat() if self.started_at else None
        if 'completed_at' not in result:
            result['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        if 'error' not in result:
            result['error'] = self.error
        if 'result' not in result:
            result['result'] = self.result
        
        return result


# 便捷函数
def create_command_task(command: str, timeout: int = 15, working_dir: str = ".", 
                       task_id: Optional[str] = None) -> CommandTask:
    """
    创建命令任务
    
    参数:
        command: 要执行的命令
        timeout: 超时时间（秒�?        working_dir: 工作目录
        task_id: 任务ID，如果为None则自动生�?        
    返回:
        CommandTask: 命令任务实例
    """
    kwargs = {}
    if task_id:
        kwargs['id'] = task_id
    
    return CommandTask(
        command=command,
        timeout=timeout,
        working_dir=working_dir,
        **kwargs
    )


def validate_command_safety(command: str) -> bool:
    """
    验证命令安全�?    
    参数:
        command: 要验证的命令
        
    返回:
        bool: 是否允许执行
    """
    executor = CommandExecutor()
    return executor.validate_command(command)


if __name__ == "__main__":
    # 测试命令任务
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("CMD命令任务测试")
    print("=" * 50)
    
    # 创建测试命令任务
    test_commands = [
        ("dir", 5, "."),
        ("echo Hello World", 5, "."),
        ("timeout 3", 2, "."),  # 应该会超�?        ("invalid_command", 5, "."),  # 应该会失�?    ]
    
    for i, (cmd, timeout, wd) in enumerate(test_commands, 1):
        print(f"\n{i}. 测试命令: {cmd}")
        print(f"   超时: {timeout}�? 工作目录: {wd}")
        
        # 创建任务
        task = create_command_task(cmd, timeout, wd, f"test_task_{i}")
        
        # 执行任务
        task.execute()
        
        # 显示结果
        print(f"   任务ID: {task.id}")
        print(f"   状�? {task.status.value}")
        
        if task.command_result:
            print(f"   命令状�? {task.command_result.status.value}")
            print(f"   退出码: {task.command_result.exit_code}")
            print(f"   执行时间: {task.command_result.execution_time:.2f}�?)
            print(f"   是否超时: {task.command_result.timed_out}")
        
        if task.error:
            print(f"   错误: {task.error[:100]}...")
    
    print("\n测试完成")
