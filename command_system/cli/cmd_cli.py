"""
Command Line Interface for CMD Agent
Responsibility: Provide user interface for command execution
"""

import argparse
import sys
import os
import logging
from typing import List, Optional
from ..services.command_executor import CommandExecutor
from ..services.task_monitor import TaskMonitor
from ..services.system_stats import SystemStatsService
from ..services.task_cleanup import TaskCleanupService

logger = logging.getLogger(__name__)


class CmdCLI:
    """Command Line Interface for CMD operations"""
    
    def __init__(self):
        """Initialize CLI"""
        self.executor = CommandExecutor()
        self.monitor = TaskMonitor()
        self.stats_service = SystemStatsService()
        self.cleanup_service = TaskCleanupService()
        
        logger.info("[CLI] CMD CLI启动")
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI with given arguments
        
        Args:
            args: Command line arguments (defaults to sys.argv[1:])
            
        Returns:
            Exit code
        """
        parser = self._create_parser()
        
        if args is None:
            args = sys.argv[1:]
        
        if not args:
            parser.print_help()
            return 0
        
        try:
            parsed_args = parser.parse_args(args)
            
            # Execute command based on parsed arguments
            if parsed_args.command == 'execute':
                return self._execute_command(parsed_args)
            elif parsed_args.command == 'status':
                return self._show_status(parsed_args)
            elif parsed_args.command == 'stats':
                return self._show_stats(parsed_args)
            elif parsed_args.command == 'history':
                return self._show_history(parsed_args)
            elif parsed_args.command == 'cleanup':
                return self._cleanup_tasks(parsed_args)
            elif parsed_args.command == 'health':
                return self._show_health(parsed_args)
            elif parsed_args.command == 'help':
                parser.print_help()
                return 0
            else:
                print(f"未知命令: {parsed_args.command}")
                parser.print_help()
                return 1
                
        except SystemExit:
            # argparse already printed help/error
            return 1
        except Exception as e:
            print(f"错误: {e}")
            logger.error(f"[CLI] 执行失败: {e}")
            return 1
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            description='Windows CMD命令执行工具',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  %(prog)s execute "dir /w" --timeout 10
  %(prog)s execute --file commands.txt --max-concurrent 5
  %(prog)s status <task_id>
  %(prog)s stats
  %(prog)s history
  %(prog)s cleanup --max-age 48
  %(prog)s health
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='可用命令')
        
        # Execute command
        execute_parser = subparsers.add_parser('execute', help='执行命令')
        execute_group = execute_parser.add_mutually_exclusive_group(required=True)
        execute_group.add_argument('command_text', nargs='?', help='要执行的命令')
        execute_group.add_argument('--file', '-f', help='从文件读取命令')
        execute_parser.add_argument('--timeout', '-t', type=int, default=15, 
                                   help='超时时间（秒）')
        execute_parser.add_argument('--working-dir', '-d', default='.', 
                                   help='工作目录')
        execute_parser.add_argument('--max-concurrent', '-m', type=int, default=7,
                                   help='最大并发数（仅批量执行时有效）')
        execute_parser.add_argument('--no-wait', action='store_true',
                                   help='不等待结果，立即返回任务ID')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='查看任务状态')
        status_parser.add_argument('task_id', help='任务ID')
        
        # Stats command
        subparsers.add_parser('stats', help='查看系统统计')
        
        # History command
        subparsers.add_parser('history', help='查看命令历史')
        
        # Cleanup command
        cleanup_parser = subparsers.add_parser('cleanup', help='清理旧任务')
        cleanup_parser.add_argument('--max-age', type=int, default=24,
                                   help='最大任务年龄（小时）')
        
        # Health command
        subparsers.add_parser('health', help='查看系统健康状态')
        
        # Help command
        subparsers.add_parser('help', help='显示帮助信息')
        
        return parser
    
    def _execute_command(self, args) -> int:
        """Execute command based on arguments"""
        if args.file:
            # Execute commands from file
            commands = self._load_commands_from_file(args.file)
            if not commands:
                print(f"错误: 文件 {args.file} 中没有找到命令或文件不存在")
                return 1
            
            print(f"从文件 {args.file} 读取 {len(commands)} 个命令")
            results = self.executor.execute_batch(
                commands=commands,
                timeout=args.timeout,
                working_dir=args.working_dir,
                max_concurrent=args.max_concurrent
            )
            
            # Print results
            self._print_batch_results(results)
            
        else:
            # Execute single command
            result = self.executor.execute_single(
                command=args.command_text,
                timeout=args.timeout,
                working_dir=args.working_dir,
                wait_for_result=not args.no_wait
            )
            
            # Print result
            self._print_single_result(result)
            
            # If not waiting, show task ID
            if args.no_wait and result.get('status') == 'submitted':
                print(f"任务已提交，ID: {result.get('task_id')}")
                print(f"使用 'status {result.get('task_id')}' 查看状态")
        
        return 0
    
    def _show_status(self, args) -> int:
        """Show task status"""
        status = self.monitor.get_task_status(args.task_id)
        
        print(f"任务状态: {args.task_id}")
        print("-" * 50)
        
        for key, value in status.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for subkey, subvalue in value.items():
                    print(f"  {subkey}: {subvalue}")
            else:
                print(f"{key}: {value}")
        
        return 0
    
    def _show_stats(self, args) -> int:
        """Show system statistics"""
        stats = self.stats_service.get_system_stats()
        
        print("系统统计信息")
        print("=" * 50)
        
        # Print basic info
        print(f"服务ID: {stats.get('service_id')}")
        print(f"状态: {stats.get('status')}")
        print(f"当前时间: {stats.get('current_time')}")
        print(f"运行时间: {stats.get('uptime_seconds', 0):.0f} 秒")
        
        # Print async task stats
        print("\n异步任务统计:")
        print("-" * 30)
        async_stats = stats.get('async_tasks', {})
        for key, value in async_stats.items():
            print(f"  {key}: {value}")
        
        # Print system resources
        print("\n系统资源:")
        print("-" * 30)
        resources = stats.get('system_resources', {})
        if 'cpu' in resources:
            cpu = resources['cpu']
            print(f"  CPU使用率: {cpu.get('percent', 0)}%")
            print(f"  CPU核心数: {cpu.get('count', 0)}")
        
        if 'memory' in resources:
            memory = resources['memory']
            print(f"  内存使用率: {memory.get('percent', 0)}%")
            print(f"  内存总量: {self._format_bytes(memory.get('total', 0))}")
        
        if 'disk' in resources:
            disk = resources['disk']
            print(f"  磁盘使用率: {disk.get('percent', 0)}%")
            print(f"  磁盘总量: {self._format_bytes(disk.get('total', 0))}")
        
        return 0
    
    def _show_history(self, args) -> int:
        """Show command history"""
        history = self.executor.get_history()
        
        print("命令执行历史")
        print("=" * 50)
        
        if not history:
            print("暂无历史记录")
            return 0
        
        for i, entry in enumerate(history, 1):
            print(f"{i}. 任务ID: {entry.get('task_id')}")
            print(f"   命令: {entry.get('command')}")
            print(f"   状态: {entry.get('status')}")
            print(f"   提交时间: {entry.get('submitted_at')}")
            print(f"   超时: {entry.get('timeout')}秒")
            print(f"   工作目录: {entry.get('working_dir')}")
            print()
        
        return 0
    
    def _cleanup_tasks(self, args) -> int:
        """Cleanup old tasks"""
        print(f"清理超过 {args.max_age} 小时的旧任务...")
        
        result = self.cleanup_service.cleanup_old_tasks(max_age_hours=args.max_age)
        
        if result.get('status') == 'success':
            cleaned = result.get('tasks_cleaned', {})
            print(f"清理完成: 清理了 {cleaned.get('total', 0)} 个任务")
            print(f"  - 已完成任务: {cleaned.get('completed', 0)}")
            print(f"  - 失败任务: {cleaned.get('failed', 0)}")
        else:
            print(f"清理失败: {result.get('error')}")
            return 1
        
        return 0
    
    def _show_health(self, args) -> int:
        """Show system health status"""
        health = self.stats_service.get_health_status()
        
        print("系统健康状态")
        print("=" * 50)
        
        status = health.get('status', 'unknown')
        status_symbol = "✅" if status == 'healthy' else "⚠️" if status == 'warning' else "❌"
        
        print(f"状态: {status_symbol} {status.upper()}")
        print(f"检查时间: {health.get('timestamp')}")
        
        # Print metrics
        metrics = health.get('metrics', {})
        print("\n关键指标:")
        print("-" * 30)
        print(f"  CPU使用率: {metrics.get('cpu_percent', 0)}%")
        print(f"  内存使用率: {metrics.get('memory_percent', 0)}%")
        print(f"  磁盘使用率: {metrics.get('disk_percent', 0)}%")
        
        # Print warnings
        warnings = health.get('warnings', [])
        if warnings:
            print("\n警告:")
            print("-" * 30)
            for warning in warnings:
                print(f"  ⚠️ {warning}")
        
        return 0
    
    def _load_commands_from_file(self, file_path: str) -> List[str]:
        """Load commands from file"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"[CLI] 文件不存在: {file_path}")
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                commands = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        commands.append(line)
                
            logger.info(f"[CLI] 从文件加载 {len(commands)} 个命令: {file_path}")
            return commands
            
        except Exception as e:
            logger.error(f"[CLI] 加载命令文件失败: {e}")
            return []
    
    def _print_single_result(self, result: dict) -> None:
        """Print single command result"""
        status = result.get('status', 'unknown')
        
        if status == 'submitted':
            print(f"✅ 命令已提交")
            print(f"   任务ID: {result.get('task_id')}")
            print(f"   消息: {result.get('message')}")
        elif status == 'completed':
            print(f"✅ 命令执行成功")
            print(f"   任务ID: {result.get('task_id')}")
            print(f"   结果: {result.get('result')}")
            print(f"   执行时间: {result.get('execution_time')}秒")
        elif status == 'failed':
            print(f"❌ 命令执行失败")
            print(f"   任务ID: {result.get('task_id')}")
            print(f"   错误: {result.get('error')}")
        elif status == 'timeout':
            print(f"⏰ 命令执行超时")
            print(f"   任务ID: {result.get('task_id')}")
            print(f"   错误: {result.get('error')}")
        else:
            print(f"❓ 未知状态: {status}")
            for key, value in result.items():
                print(f"   {key}: {value}")
    
    def _print_batch_results(self, results: List[dict]) -> None:
        """Print batch command results"""
        if not results:
            print("没有执行结果")
            return
        
        # Count results by status
        status_counts = {}
        for result in results:
            status = result.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n批量执行完成:")
        print(f"  总计: {len(results)} 个命令")
        for status, count in status_counts.items():
            status_display = {
                'completed': '成功',
                'failed': '失败',
                'timeout': '超时',
                'submitted': '已提交',
                'error': '错误'
            }.get(status, status)
            
            print(f"  {status_display}: {count}")
        
        # Show detailed results for failures
        failures = [r for r in results if r.get('status') in ['failed', 'timeout', 'error']]
        if failures:
            print(f"\n失败详情:")
            for i, failure in enumerate(failures, 1):
                print(f"  {i}. 任务ID: {failure.get('task_id')}")
                print(f"     状态: {failure.get('status')}")
                print(f"     错误: {failure.get('error')}")
                if 'command' in failure:
                    print(f"     命令: {failure.get('command')}")
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"


def main():
    """Main entry point for CLI"""
    cli = CmdCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())