"""
Windows CMD命令执行器
封装Windows cmd命令执行的核心逻辑，支持超时控制和输出捕获
"""
import subprocess
import threading
import time
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)


class CommandStatus(Enum):
    """命令执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class CommandResult:
    """命令执行结果"""
    command: str
    status: CommandStatus
    exit_code: int
    stdout: str
    stderr: str
    start_time: datetime
    end_time: datetime
    execution_time: float
    timed_out: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'command': self.command,
            'status': self.status.value,
            'exit_code': self.exit_code,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'execution_time': self.execution_time,
            'timed_out': self.timed_out
        }


class CommandExecutor:
    """命令执行器"""
    
    def __init__(self, timeout: int = 15, working_dir: str = "."):
        """
        初始化命令执行器
        
        参数:
            timeout: 命令执行超时时间（秒），默认15秒
            working_dir: 工作目录，默认当前目录
        """
        self.timeout = timeout
        self.working_dir = working_dir
        
    def execute(self, command: str, working_dir: Optional[str] = None) -> CommandResult:
        """
        执行Windows cmd命令
        
        参数:
            command: 要执行的命令字符串
            working_dir: 工作目录，如果为None则使用初始化时设置的目录
            
        返回:
            CommandResult: 命令执行结果
        """
        actual_working_dir = working_dir if working_dir is not None else self.working_dir
        
        # 确保工作目录存在
        if not os.path.exists(actual_working_dir):
            logger.warning(f"工作目录不存在: {actual_working_dir}，使用当前目录")
            actual_working_dir = "."
        
        start_time = datetime.now()
        
        try:
            # 记录命令开始执行
            logger.info(f"[CMD] 开始执行命令: {command}")
            logger.info(f"[CMD] 工作目录: {actual_working_dir}")
            logger.info(f"[CMD] 超时时间: {self.timeout}秒")
            
            # 执行命令
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=actual_working_dir,
                encoding='utf-8',
                errors='replace'
            )
            
            # 设置超时监控
            timed_out = False
            timer = threading.Timer(self.timeout, self._terminate_process, [process])
            timer.start()
            
            try:
                # 等待进程完成
                stdout, stderr = process.communicate()
            except Exception as e:
                # 如果communicate抛出异常，可能是进程被终止
                logger.error(f"[CMD] 命令执行异常: {e}")
                stdout, stderr = "", str(e)
            finally:
                # 取消定时器
                timer.cancel()
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 检查是否超时
            if process.returncode is None:
                # 进程仍在运行，强制终止
                self._terminate_process(process)
                timed_out = True
                status = CommandStatus.TIMEOUT
                exit_code = -1
                stderr = f"Command timed out after {self.timeout} seconds"
                logger.warning(f"[CMD] 命令执行超时: {command}")
                logger.warning(f"[CMD] 超时时间: {self.timeout}秒")
                logger.warning(f"[CMD] 实际执行时间: {execution_time:.2f}秒")
            else:
                timed_out = False
                exit_code = process.returncode
                
                if exit_code == 0:
                    status = CommandStatus.COMPLETED
                    logger.info(f"[CMD] 命令执行完成: {command}")
                    logger.info(f"[CMD] 退出码: {exit_code}")
                    logger.info(f"[CMD] 执行时间: {execution_time:.2f}秒")
                    
                    # 记录输出长度（避免日志过长）
                    if stdout:
                        logger.debug(f"[CMD] 标准输出长度: {len(stdout)}字符")
                    if stderr:
                        logger.debug(f"[CMD] 标准错误长度: {len(stderr)}字符")
                else:
                    status = CommandStatus.FAILED
                    logger.error(f"[CMD] 命令执行失败: {command}")
                    logger.error(f"[CMD] 退出码: {exit_code}")
                    logger.error(f"[CMD] 执行时间: {execution_time:.2f}秒")
                    if stderr:
                        logger.error(f"[CMD] 错误信息: {stderr[:500]}...")
            
            return CommandResult(
                command=command,
                status=status,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                timed_out=timed_out
            )
            
        except subprocess.TimeoutExpired:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.warning(f"[CMD] 命令执行超时（TimeoutExpired）: {command}")
            logger.warning(f"[CMD] 超时时间: {self.timeout}秒")
            logger.warning(f"[CMD] 实际执行时间: {execution_time:.2f}秒")
            
            return CommandResult(
                command=command,
                status=CommandStatus.TIMEOUT,
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {self.timeout} seconds",
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                timed_out=True
            )
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.error(f"[CMD] 命令执行异常: {command}")
            logger.error(f"[CMD] 异常信息: {e}")
            logger.error(f"[CMD] 执行时间: {execution_time:.2f}秒")
            
            return CommandResult(
                command=command,
                status=CommandStatus.FAILED,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                timed_out=False
            )
    
    def _terminate_process(self, process: subprocess.Popen):
        """终止进程"""
        try:
            process.terminate()
            time.sleep(0.1)  # 等待进程响应终止信号
            if process.poll() is None:
                process.kill()  # 强制终止
        except Exception as e:
            logger.warning(f"[CMD] 终止进程时发生错误: {e}")
    
    def validate_command(self, command: str) -> bool:
        """
        验证命令安全性（基础验证）
        
        参数:
            command: 要验证的命令
            
        返回:
            bool: 是否允许执行
        """
        # 危险命令列表（可根据需要扩展）
        dangerous_patterns = [
            "format ", "del /s", "rm -rf", "chmod 777",
            "chown root", "shutdown", "taskkill /f /im",
            "reg delete", "fsutil", "diskpart"
        ]
        
        # 检查危险命令
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                logger.warning(f"[CMD] 检测到危险命令: {command}")
                return False
        
        return True
    
    def set_timeout(self, timeout: int):
        """设置超时时间"""
        if timeout <= 0:
            raise ValueError("超时时间必须大于0")
        self.timeout = timeout
        logger.info(f"[CMD] 超时时间已设置为: {timeout}秒")
    
    def set_working_dir(self, working_dir: str):
        """设置工作目录"""
        if os.path.exists(working_dir):
            self.working_dir = working_dir
            logger.info(f"[CMD] 工作目录已设置为: {working_dir}")
        else:
            logger.warning(f"[CMD] 工作目录不存在: {working_dir}")


# 全局命令执行器实例
_default_executor = CommandExecutor()


def execute_command(command: str, timeout: int = 15, working_dir: str = ".") -> CommandResult:
    """
    执行命令的便捷函数
    
    参数:
        command: 要执行的命令
        timeout: 超时时间（秒）
        working_dir: 工作目录
        
    返回:
        CommandResult: 命令执行结果
    """
    executor = CommandExecutor(timeout=timeout, working_dir=working_dir)
    return executor.execute(command)


if __name__ == "__main__":
    # 测试命令执行器
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) > 1:
        # 执行命令行参数中的命令
        command = " ".join(sys.argv[1:])
        print(f"执行命令: {command}")
        
        executor = CommandExecutor(timeout=10)
        result = executor.execute(command)
        
        print(f"\n命令执行结果:")
        print(f"  状态: {result.status.value}")
        print(f"  退出码: {result.exit_code}")
        print(f"  执行时间: {result.execution_time:.2f}秒")
        print(f"  是否超时: {result.timed_out}")
        
        if result.stdout:
            print(f"\n标准输出:")
            print(result.stdout[:1000] + ("..." if len(result.stdout) > 1000 else ""))
        
        if result.stderr:
            print(f"\n标准错误:")
            print(result.stderr[:1000] + ("..." if len(result.stderr) > 1000 else ""))
    else:
        # 示例用法
        print("命令执行器测试")
        print("=" * 50)
        
        executor = CommandExecutor(timeout=5)
        
        # 测试正常命令
        print("\n1. 测试正常命令 (dir):")
        result = executor.execute("dir")
        print(f"   状态: {result.status.value}, 退出码: {result.exit_code}")
        
        # 测试超时命令
        print("\n2. 测试超时命令 (timeout 10):")
        result = executor.execute("timeout 10")
        print(f"   状态: {result.status.value}, 是否超时: {result.timed_out}")
        
        # 测试错误命令
        print("\n3. 测试错误命令 (invalid_command):")
        result = executor.execute("invalid_command")
        print(f"   状态: {result.status.value}, 退出码: {result.exit_code}")
        
        print("\n测试完成")