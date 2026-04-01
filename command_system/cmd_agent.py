#!/usr/bin/env python
"""
Windows CMD命令执行Agent
独立命令行工具，深度集成到现有异步任务系统
支持最大并发数7，15秒超时监控，日志通知
"""
import argparse
import sys
import os
import time
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CmdAgent:
    """CMD命令执行Agent"""
    
    def __init__(self):
        """初始化Agent"""
        self.agent_id = f"agent_{int(time.time())}"
        self.start_time = datetime.now()
        self.command_history: List[Dict[str, Any]] = []
        
        logger.info(f"[AGENT] CMD Agent启动: {self.agent_id}")
        logger.info(f"[AGENT] 启动时间: {self.start_time}")
        logger.info(f"[AGENT] 最大并发数: 7")
        logger.info(f"[AGENT] 默认超时时间: 15秒")
    
    def execute_single_command(self, command: str, timeout: int = 15, 
                              working_dir: str = ".", wait_for_result: bool = True) -> Dict[str, Any]:
        """
        执行单个命令
        
        参数:
            command: 要执行的命令
            timeout: 超时时间（秒）
            working_dir: 工作目录
            wait_for_result: 是否等待结果
            
        返回:
            执行结果字典
        """
        logger.info(f"[AGENT] 执行单个命令: {command}")
        logger.info(f"[AGENT] 超时时间: {timeout}秒")
        logger.info(f"[AGENT] 工作目录: {working_dir}")
        
        try:
            from async_tasks import submit_command_task, get_async_task_status, init_async_tasks
            
            # 确保异步任务系统已启动
            init_async_tasks()
            
            # 提交命令任务
            task_id = submit_command_task(command, timeout, working_dir)
            logger.info(f"[AGENT] 命令任务已提交: {task_id}")
            
            # 记录命令历史
            self.command_history.append({
                'task_id': task_id,
                'command': command,
                'timeout': timeout,
                'working_dir': working_dir,
                'submitted_at': datetime.now().isoformat(),
                'status': 'submitted'
            })
            
            if wait_for_result:
                # 等待结果
                return self.wait_for_task(task_id, timeout + 2)  # 额外给2秒缓冲时间
            else:
                return {
                    'task_id': task_id,
                    'status': 'submitted',
                    'message': f'命令已提交，任务ID: {task_id}'
                }
                
        except Exception as e:
            logger.error(f"[AGENT] 执行命令失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'command': command
            }
    
    def execute_batch_commands(self, commands: List[str], timeout: int = 15,
                              working_dir: str = ".", max_concurrent: int = 7) -> List[Dict[str, Any]]:
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
        logger.info(f"[AGENT] 批量执行命令: {len(commands)}个命令")
        logger.info(f"[AGENT] 超时时间: {timeout}秒")
        logger.info(f"[AGENT] 工作目录: {working_dir}")
        logger.info(f"[AGENT] 最大并发数: {max_concurrent}")
        
        try:
            from async_tasks import submit_command_task, get_async_task_status, init_async_tasks
            
            # 确保异步任务系统已启动
            init_async_tasks()
            
            results = []
            task_ids = []
            
            # 提交所有任务
            for i, command in enumerate(commands):
                task_id = submit_command_task(command, timeout, working_dir)
                task_ids.append(task_id)
                
                logger.info(f"[AGENT] 提交命令 {i+1}/{len(commands)}: {command}")
                logger.info(f"[AGENT] 任务ID: {task_id}")
                
                # 记录命令历史
                self.command_history.append({
                    'task_id': task_id,
                    'command': command,
                    'timeout': timeout,
                    'working_dir': working_dir,
                    'submitted_at': datetime.now().isoformat(),
                    'status': 'submitted'
                })
                
                # 控制并发数
                if len(task_ids) >= max_concurrent:
                    # 等待一些任务完成
                    self._wait_for_some_tasks(task_ids, results)
            
            # 等待剩余任务完成
            self._wait_for_remaining_tasks(task_ids, results)
            
            return results
            
        except Exception as e:
            logger.error(f"[AGENT] 批量执行命令失败: {e}")
            return [{
                'status': 'error',
                'error': str(e),
                'command': 'batch_execution'
            }]
    
    def wait_for_task(self, task_id: str, max_wait_time: int = 30) -> Dict[str, Any]:
        """
        等待任务完成
        
        参数:
            task_id: 任务ID
            max_wait_time: 最大等待时间（秒）
            
        返回:
            任务结果字典
        """
        logger.info(f"[AGENT] 等待任务完成: {task_id}")
        logger.info(f"[AGENT] 最大等待时间: {max_wait_time}秒")
        
        from async_tasks import get_async_task_status
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = get_async_task_status(task_id)
            
            if not status:
                logger.warning(f"[AGENT] 未找到任务: {task_id}")
                return {
                    'task_id': task_id,
                    'status': 'not_found',
                    'error': f'未找到任务: {task_id}'
                }
            
            if status['status'] in ['completed', 'failed']:
                # 更新命令历史
                for cmd in self.command_history:
                    if cmd.get('task_id') == task_id:
                        cmd['status'] = status['status']
                        cmd['completed_at'] = datetime.now().isoformat()
                        cmd['result'] = status
                        break
                
                logger.info(f"[AGENT] 任务完成: {task_id}")
                logger.info(f"[AGENT] 最终状态: {status['status']}")
                
                if status['status'] == 'completed':
                    logger.info(f"[AGENT] 任务执行成功")
                else:
                    logger.warning(f"[AGENT] 任务执行失败")
                    if status.get('error'):
                        logger.warning(f"[AGENT] 错误信息: {status['error']}")
                
                return {
                    'task_id': task_id,
                    'status': status['status'],
                    'result': status,
                    'wait_time': time.time() - start_time
                }
            
            # 等待一段时间再检查
            time.sleep(0.5)
        
        # 超时
        logger.warning(f"[AGENT] 等待任务超时: {task_id}")
        
        return {
            'task_id': task_id,
            'status': 'timeout',
            'error': f'等待任务超时，最大等待时间: {max_wait_time}秒',
            'wait_time': time.time() - start_time
        }
    
    def _wait_for_some_tasks(self, task_ids: List[str], results: List[Dict[str, Any]], 
                            min_completed: int = 1):
        """等待一些任务完成"""
        from async_tasks import get_async_task_status
        
        logger.debug(f"[AGENT] 等待至少 {min_completed} 个任务完成")
        
        completed_count = 0
        start_time = time.time()
        
        while completed_count < min_completed and time.time() - start_time < 30:
            for task_id in task_ids[:]:  # 使用副本遍历
                if any(r['task_id'] == task_id for r in results):
                    continue  # 已经处理过
                
                status = get_async_task_status(task_id)
                if status and status['status'] in ['completed', 'failed']:
                    results.append({
                        'task_id': task_id,
                        'status': status['status'],
                        'result': status
                    })
                    completed_count += 1
                    task_ids.remove(task_id)  # 从原列表中移除
            
            if completed_count >= min_completed:
                break
            
            time.sleep(0.5)
    
    def _wait_for_remaining_tasks(self, task_ids: List[str], results: List[Dict[str, Any]]):
        """等待剩余任务完成"""
        logger.info(f"[AGENT] 等待剩余 {len(task_ids)} 个任务完成")
        
        for task_id in task_ids:
            result = self.wait_for_task(task_id, 60)  # 给每个任务最多60秒
            results.append(result)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        参数:
            task_id: 任务ID
            
        返回:
            任务状态字典
        """
        from async_tasks import get_async_task_status
        
        status = get_async_task_status(task_id)
        
        if status:
            logger.info(f"[AGENT] 获取任务状态: {task_id}")
            logger.info(f"[AGENT] 状态: {status['status']}")
            return {
                'task_id': task_id,
                'status': 'found',
                'result': status
            }
        else:
            logger.warning(f"[AGENT] 未找到任务: {task_id}")
            return {
                'task_id': task_id,
                'status': 'not_found',
                'error': f'未找到任务: {task_id}'
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        获取系统统计信息
        
        返回:
            系统统计字典
        """
        try:
            from async_tasks import get_async_stats
            
            stats = get_async_stats()
            
            # 添加Agent统计信息
            agent_stats = {
                'agent_id': self.agent_id,
                'start_time': self.start_time.isoformat(),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                'total_commands_executed': len(self.command_history),
                'successful_commands': len([c for c in self.command_history if c.get('status') == 'completed']),
                'failed_commands': len([c for c in self.command_history if c.get('status') == 'failed']),
                'pending_commands': len([c for c in self.command_history if c.get('status') == 'submitted'])
            }
            
            logger.info(f"[AGENT] 获取系统统计信息")
            logger.info(f"[AGENT] Agent运行时间: {agent_stats['uptime_seconds']:.1f}秒")
            logger.info(f"[AGENT] 执行命令总数: {agent_stats['total_commands_executed']}")
            
            return {**stats, **agent_stats}
            
        except Exception as e:
            logger.error(f"[AGENT] 获取系统统计信息失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        try:
            from async_tasks import task_manager
            
            old_count = len(task_manager.tasks)
            task_manager.cleanup_old_tasks(max_age_hours)
            new_count = len(task_manager.tasks)
            
            logger.info(f"[AGENT] 清理旧任务完成")
            logger.info(f"[AGENT] 清理前任务数: {old_count}")
            logger.info(f"[AGENT] 清理后任务数: {new_count}")
            logger.info(f"[AGENT] 清理任务数: {old_count - new_count}")
            
            return {
                'status': 'success',
                'cleaned_tasks': old_count - new_count,
                'remaining_tasks': new_count
            }
            
        except Exception as e:
            logger.error(f"[AGENT] 清理旧任务失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def shutdown(self):
        """关闭Agent"""
        try:
            from async_tasks import shutdown_async_tasks
            
            shutdown_async_tasks()
            
            uptime = (datetime.now() - self.start_time).total_seconds()
            logger.info(f"[AGENT] CMD Agent关闭: {self.agent_id}")
            logger.info(f"[AGENT] 运行时间: {uptime:.1f}秒")
            logger.info(f"[AGENT] 执行命令总数: {len(self.command_history)}")
            logger.info(f"[AGENT] Agent关闭完成")
            
            return {
                'status': 'shutdown',
                'agent_id': self.agent_id,
                'uptime_seconds': uptime,
                'total_commands': len(self.command_history)
            }
            
        except Exception as e:
            logger.error(f"[AGENT] 关闭Agent失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


class InteractiveShell:
    """交互式Shell"""
    
    def __init__(self, agent: CmdAgent):
        self.agent = agent
        self.running = True
        self.command_buffer: List[str] = []
        
    def run(self):
        """运行交互式Shell"""
        print("\n" + "=" * 60)
        print("CMD Agent 交互式模式")
        print("=" * 60)
        print("输入 'help' 查看帮助")
        print("输入 'exit' 退出")
        print("输入多行命令时，以空行结束")
        print("=" * 60)
        
        while self.running:
            try:
                # 读取命令
                if self.command_buffer:
                    prompt = ">>> "
                else:
                    prompt = "cmd> "
                
                line = input(prompt).strip()
                
                # 处理空行（多行命令结束）
                if not line and self.command_buffer:
                    command = "\n".join(self.command_buffer)
                    self.command_buffer = []
                    self._execute_command(command)
                    continue
                elif not line:
                    continue
                
                # 处理特殊命令
                if line.lower() == 'exit':
                    self.running = False
                    continue
                elif line.lower() == 'help':
                    self._show_help()
                    continue
                elif line.lower() == 'status':
                    self._show_status()
                    continue
                elif line.lower() == 'stats':
                    self._show_stats()
                    continue
                elif line.lower() == 'history':
                    self._show_history()
                    continue
                elif line.lower() == 'clear':
                    self.command_buffer = []
                    print("命令缓冲区已清空")
                    continue
                
                # 检查是否是多行命令
                if line.endswith('\\'):
                    self.command_buffer.append(line.rstrip('\\'))
                    continue
                else:
                    if self.command_buffer:
                        self.command_buffer.append(line)
                        command = "\n".join(self.command_buffer)
                        self.command_buffer = []
                    else:
                        command = line
                    
                    self._execute_command(command)
                    
            except KeyboardInterrupt:
                print("\n输入 'exit' 退出")
                self.command_buffer = []
            except EOFError:
                self.running = False
                print("\n检测到文件结束，退出交互式模式")
        
        print("交互式模式结束")
    
    def _execute_command(self, command: str):
        """执行命令"""
        print(f"执行命令: {command}")
        
        # 询问超时时间
        timeout = 15
        try:
            timeout_input = input(f"超时时间（秒，默认{timeout}）: ").strip()
            if timeout_input:
                timeout = int(timeout_input)
        except ValueError:
            print(f"无效的超时时间，使用默认值: {timeout}秒")
        
        # 执行命令
        result = self.agent.execute_single_command(command, timeout)
        
        # 显示结果
        if result['status'] == 'submitted':
            print(f"命令已提交，任务ID: {result.get('task_id')}")
            print("任务正在后台执行，使用 'status <任务ID>' 查看状态")
        elif result['status'] == 'completed':
            print("命令执行成功")
            if result.get('result', {}).get('result', {}).get('command_result'):
                cmd_result = result['result']['result']['command_result']
                if cmd_result.get('stdout'):
                    print("\n标准输出:")
                    print(cmd_result['stdout'][:1000] + ("..." if len(cmd_result['stdout']) > 1000 else ""))
        elif result['status'] == 'error':
            print(f"命令执行失败: {result.get('error')}")
        else:
            print(f"命令状态: {result['status']}")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
可用命令:
  <命令>              - 执行CMD命令
  help               - 显示此帮助信息
  status [任务ID]    - 查看任务状态（不指定任务ID则显示所有）
  stats              - 查看系统统计信息
  history            - 查看命令历史
  clear              - 清空命令缓冲区
  exit               - 退出交互式模式

多行命令:
  在行尾添加反斜杠（\）可以输入多行命令
  输入空行结束多行命令输入

示例:
  cmd> dir C:\
  cmd> echo Hello World\
  >>> echo This is multi-line\
  >>> echo command
  cmd> 
        """
        print(help_text)
    
    def _show_status(self):
        """显示任务状态"""
        task_id = input("任务ID（留空显示所有）: ").strip()
        
        if task_id:
            result = self.agent.get_task_status(task_id)
            if result['status'] == 'found':
                status = result['result']
                print(f"\n任务状态: {status['status']}")
                print(f"任务ID: {status['id']}")
                print(f"创建时间: {status.get('created_at')}")
                print(f"开始时间: {status.get('started_at')}")
                print(f"完成时间: {status.get('completed_at')}")
                print(f"执行时间: {status.get('execution_time')}秒")
                
                if status.get('error'):
                    print(f"错误信息: {status['error']}")
                
                if status.get('result') and status['result'].get('command_result'):
                    cmd_result = status['result']['command_result']
                    print(f"命令: {cmd_result.get('command')}")
                    print(f"退出码: {cmd_result.get('exit_code')}")
            else:
                print(f"未找到任务: {task_id}")
        else:
            # 显示所有任务状态
            stats = self.agent.get_system_stats()
            if 'queue_size' in stats:
                print(f"\n任务队列大小: {stats['queue_size']}")
                print(f"总任务数: {stats.get('total_tasks', 'N/A')}")
                print(f"已完成任务: {stats.get('completed_tasks', 'N/A')}")
                print(f"失败任务: {stats.get('failed_tasks', 'N/A')}")
                print(f"待处理任务: {stats.get('pending_tasks', 'N/A')}")
    
    def _show_stats(self):
        """显示统计信息"""
        stats = self.agent.get_system_stats()
        
        print("\n系统统计信息:")
        print("=" * 40)
        
        for key, value in stats.items():
            if key not in ['agent_id', 'start_time']:
                print(f"{key}: {value}")
        
        print("=" * 40)
    
    def _show_history(self):
        """显示命令历史"""
        if not self.agent.command_history:
            print("命令历史为空")
            return
        
        print("\n命令历史:")
        print("=" * 60)
        
        for i, cmd in enumerate(self.agent.command_history[-10:], 1):  # 显示最近10条
            print(f"{i}. 任务ID: {cmd.get('task_id', 'N/A')}")
            print(f"   命令: {cmd.get('command', 'N/A')}")
            print(f"   状态: {cmd.get('status', 'N/A')}")
            print(f"   提交时间: {cmd.get('submitted_at', 'N/A')}")
            print()


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Windows CMD命令执行Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s exec "dir C:\\"
  %(prog)s exec "echo Hello World" --timeout 10
  %(prog)s batch commands.txt
  %(prog)s interactive
  %(prog)s status task_123
  %(prog)s stats
  %(prog)s cleanup
  %(prog)s stop

批量命令文件格式（commands.txt）:
  每行一个命令，空行和以#开头的行会被忽略
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令", required=True)
    
    # exec命令：执行单个命令
    exec_parser = subparsers.add_parser("exec", help="执行单个命令")
    exec_parser.add_argument("command_str", help="要执行的命令")
    exec_parser.add_argument("--timeout", type=int, default=15, help="超时时间（秒），默认15")
    exec_parser.add_argument("--working-dir", default=".", help="工作目录，默认当前目录")
    exec_parser.add_argument("--no-wait", action="store_true", help="不等待结果，立即返回")
    
    # batch命令：批量执行
    batch_parser = subparsers.add_parser("batch", help="批量执行命令")
    batch_parser.add_argument("file", help="包含命令的文件（每行一个命令）")
    batch_parser.add_argument("--timeout", type=int, default=15, help="超时时间（秒），默认15")
    batch_parser.add_argument("--working-dir", default=".", help="工作目录，默认当前目录")
    batch_parser.add_argument("--max-concurrent", type=int, default=7, help="最大并发数，默认7")
    
    # interactive命令：交互式模式
    subparsers.add_parser("interactive", help="进入交互式模式")
    
    # status命令：查看任务状态
    status_parser = subparsers.add_parser("status", help="查看任务状态")
    status_parser.add_argument("task_id", nargs="?", help="任务ID（不指定则显示系统状态）")
    
    # stats命令：查看统计信息
    subparsers.add_parser("stats", help="查看系统统计信息")
    
    # cleanup命令：清理旧任务
    cleanup_parser = subparsers.add_parser("cleanup", help="清理旧任务")
    cleanup_parser.add_argument("--max-age-hours", type=int, default=24, help="最大保留时间（小时），默认24")
    
    # stop命令：停止agent
    subparsers.add_parser("stop", help="停止agent")
    
    return parser


def load_commands_from_file(file_path: str) -> List[str]:
    """从文件加载命令"""
    commands = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    commands.append(line)
        
        logger.info(f"[AGENT] 从文件加载命令: {file_path}")
        logger.info(f"[AGENT] 加载命令数: {len(commands)}")
        
        return commands
        
    except Exception as e:
        logger.error(f"[AGENT] 加载命令文件失败: {e}")
        raise


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 创建Agent实例
    agent = CmdAgent()
    
    try:
        if args.command == "exec":
            # 执行单个命令
            result = agent.execute_single_command(
                args.command_str,
                args.timeout,
                args.working_dir,
                not args.no_wait
            )
            
            # 显示结果
            if args.no_wait:
                print(f"命令已提交，任务ID: {result.get('task_id')}")
                print("使用 'python cmd_agent.py status <任务ID>' 查看状态")
            else:
                if result['status'] == 'completed':
                    print("命令执行成功")
                    if result.get('result', {}).get('result', {}).get('command_result'):
                        cmd_result = result['result']['result']['command_result']
                        if cmd_result.get('stdout'):
                            print("\n标准输出:")
                            print(cmd_result['stdout'])
                else:
                    print(f"命令执行失败: {result.get('error', '未知错误')}")
        
        elif args.command == "batch":
            # 批量执行命令
            commands = load_commands_from_file(args.file)
            
            if not commands:
                print("文件中没有有效的命令")
                return
            
            print(f"开始批量执行 {len(commands)} 个命令...")
            print(f"超时时间: {args.timeout}秒")
            print(f"最大并发数: {args.max_concurrent}")
            print()
            
            results = agent.execute_batch_commands(
                commands,
                args.timeout,
                args.working_dir,
                args.max_concurrent
            )
            
            # 显示统计信息
            completed = len([r for r in results if r.get('status') == 'completed'])
            failed = len([r for r in results if r.get('status') in ['failed', 'error', 'timeout']])
            
            print(f"\n批量执行完成:")
            print(f"  成功: {completed}")
            print(f"  失败: {failed}")
            print(f"  总计: {len(results)}")
        
        elif args.command == "interactive":
            # 交互式模式
            shell = InteractiveShell(agent)
            shell.run()
        
        elif args.command == "status":
            # 查看任务状态
            if args.task_id:
                result = agent.get_task_status(args.task_id)
                if result['status'] == 'found':
                    status = result['result']
                    print(f"任务状态: {status['status']}")
                    print(f"任务ID: {status['id']}")
                    print(f"创建时间: {status.get('created_at')}")
                    print(f"开始时间: {status.get('started_at')}")
                    print(f"完成时间: {status.get('completed_at')}")
                    print(f"执行时间: {status.get('execution_time')}秒")
                    
                    if status.get('error'):
                        print(f"错误信息: {status['error']}")
                else:
                    print(f"未找到任务: {args.task_id}")
            else:
                # 显示系统状态
                stats = agent.get_system_stats()
                print("系统状态:")
                print(f"  Agent ID: {stats.get('agent_id')}")
                print(f"  启动时间: {stats.get('start_time')}")
                print(f"  运行时间: {stats.get('uptime_seconds', 0):.1f}秒")
                print(f"  执行命令总数: {stats.get('total_commands_executed', 0)}")
                print(f"  成功命令: {stats.get('successful_commands', 0)}")
                print(f"  失败命令: {stats.get('failed_commands', 0)}")
                print(f"  待处理命令: {stats.get('pending_commands', 0)}")
        
        elif args.command == "stats":
            # 查看统计信息
            stats = agent.get_system_stats()
            
            print("系统统计信息:")
            print("=" * 50)
            
            for key, value in stats.items():
                if isinstance(value, (int, float)) and key.endswith('_seconds'):
                    print(f"  {key}: {value:.1f}")
                else:
                    print(f"  {key}: {value}")
            
            print("=" * 50)
        
        elif args.command == "cleanup":
            # 清理旧任务
            result = agent.cleanup_old_tasks(args.max_age_hours)
            
            if result['status'] == 'success':
                print(f"清理完成:")
                print(f"  清理任务数: {result.get('cleaned_tasks', 0)}")
                print(f"  剩余任务数: {result.get('remaining_tasks', 0)}")
            else:
                print(f"清理失败: {result.get('error')}")
        
        elif args.command == "stop":
            # 停止agent
            result = agent.shutdown()
            
            if result['status'] == 'shutdown':
                print(f"Agent已停止:")
                print(f"  Agent ID: {result.get('agent_id')}")
                print(f"  运行时间: {result.get('uptime_seconds', 0):.1f}秒")
                print(f"  执行命令总数: {result.get('total_commands', 0)}")
            else:
                print(f"停止失败: {result.get('error')}")
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        agent.shutdown()
    except Exception as e:
        logger.error(f"[AGENT] 执行命令失败: {e}")
        print(f"错误: {e}")
        agent.shutdown()


if __name__ == "__main__":
    main()