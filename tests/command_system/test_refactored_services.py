#!/usr/bin/env python3
"""
Comprehensive tests for refactored command system service classes
"""

import unittest
import tempfile
import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from command_system.services.command_executor import CommandExecutor
from command_system.services.task_monitor import TaskMonitor
from command_system.services.system_stats import SystemStatsService
from command_system.services.task_cleanup import TaskCleanupService
from command_system.cli.cmd_cli import CmdCLI
from command_system.cmd_agent_refactored import CmdAgent


class TestCommandExecutor(unittest.TestCase):
    """Test CommandExecutor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = CommandExecutor()
        self.test_command = "echo Hello World"
        
    def test_execute_simple_command(self):
        """Test executing a simple command"""
        result = self.executor.execute(self.test_command)
        
        self.assertIsNotNone(result)
        self.assertIn('command', result)
        self.assertIn('output', result)
        self.assertIn('return_code', result)
        self.assertIn('timestamp', result)
        self.assertEqual(result['command'], self.test_command)
        self.assertEqual(result['return_code'], 0)
        self.assertIn('Hello World', result['output'])
    
    def test_execute_invalid_command(self):
        """Test executing an invalid command"""
        result = self.executor.execute("invalid_command_that_does_not_exist")
        
        self.assertIsNotNone(result)
        self.assertIn('error', result)
        self.assertNotEqual(result['return_code'], 0)
    
    def test_execute_with_timeout(self):
        """Test command execution with timeout"""
        # Test with a command that would run indefinitely
        result = self.executor.execute("ping 127.0.0.1 -n 10", timeout=1)
        
        self.assertIsNotNone(result)
        self.assertIn('timeout', str(result).lower() or 'error' in str(result).lower())
    
    def test_execute_with_working_dir(self):
        """Test command execution with working directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.executor.execute("dir", workdir=temp_dir)
            
            self.assertIsNotNone(result)
            self.assertEqual(result['return_code'], 0)
    
    def test_batch_execute(self):
        """Test batch execution of multiple commands"""
        commands = [
            "echo Command 1",
            "echo Command 2",
            "echo Command 3"
        ]
        
        results = self.executor.batch_execute(commands)
        
        self.assertEqual(len(results), len(commands))
        for i, result in enumerate(results):
            self.assertEqual(result['return_code'], 0)
            self.assertIn(f'Command {i+1}', result['output'])
    
    def test_get_execution_history(self):
        """Test getting execution history"""
        # Execute some commands
        self.executor.execute("echo Test 1")
        self.executor.execute("echo Test 2")
        
        history = self.executor.get_execution_history()
        
        self.assertGreaterEqual(len(history), 2)
        self.assertEqual(history[0]['command'], "echo Test 1")
        self.assertEqual(history[1]['command'], "echo Test 2")


class TestTaskMonitor(unittest.TestCase):
    """Test TaskMonitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = TaskMonitor()
        
        # Create some test tasks
        self.test_tasks = [
            {
                'id': 'task_1',
                'command': 'echo Task 1',
                'status': 'running',
                'start_time': datetime.now() - timedelta(minutes=5),
                'pid': 1234
            },
            {
                'id': 'task_2',
                'command': 'echo Task 2',
                'status': 'completed',
                'start_time': datetime.now() - timedelta(minutes=10),
                'end_time': datetime.now() - timedelta(minutes=9),
                'pid': 1235
            },
            {
                'id': 'task_3',
                'command': 'echo Task 3',
                'status': 'failed',
                'start_time': datetime.now() - timedelta(minutes=15),
                'end_time': datetime.now() - timedelta(minutes=14),
                'pid': 1236,
                'error': 'Command failed'
            }
        ]
        
        # Add tasks to monitor
        for task in self.test_tasks:
            self.monitor.add_task(task)
    
    def test_add_and_get_task(self):
        """Test adding and getting a task"""
        task_id = 'test_task'
        task_data = {
            'id': task_id,
            'command': 'echo Test',
            'status': 'pending',
            'start_time': datetime.now()
        }
        
        self.monitor.add_task(task_data)
        retrieved_task = self.monitor.get_task(task_id)
        
        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task['id'], task_id)
        self.assertEqual(retrieved_task['command'], 'echo Test')
    
    def test_update_task_status(self):
        """Test updating task status"""
        task_id = 'task_1'
        new_status = 'completed'
        
        success = self.monitor.update_task_status(task_id, new_status)
        self.assertTrue(success)
        
        task = self.monitor.get_task(task_id)
        self.assertEqual(task['status'], new_status)
    
    def test_get_all_tasks(self):
        """Test getting all tasks"""
        all_tasks = self.monitor.get_all_tasks()
        
        self.assertEqual(len(all_tasks), len(self.test_tasks))
        for task in self.test_tasks:
            self.assertIn(task['id'], all_tasks)
    
    def test_get_tasks_by_status(self):
        """Test getting tasks by status"""
        running_tasks = self.monitor.get_tasks_by_status('running')
        completed_tasks = self.monitor.get_tasks_by_status('completed')
        failed_tasks = self.monitor.get_tasks_by_status('failed')
        
        self.assertEqual(len(running_tasks), 1)
        self.assertEqual(len(completed_tasks), 1)
        self.assertEqual(len(failed_tasks), 1)
        
        self.assertEqual(running_tasks[0]['id'], 'task_1')
        self.assertEqual(completed_tasks[0]['id'], 'task_2')
        self.assertEqual(failed_tasks[0]['id'], 'task_3')
    
    def test_get_task_statistics(self):
        """Test getting task statistics"""
        stats = self.monitor.get_task_statistics()
        
        self.assertIn('total_tasks', stats)
        self.assertIn('running_tasks', stats)
        self.assertIn('completed_tasks', stats)
        self.assertIn('failed_tasks', stats)
        self.assertIn('pending_tasks', stats)
        
        self.assertEqual(stats['total_tasks'], 3)
        self.assertEqual(stats['running_tasks'], 1)
        self.assertEqual(stats['completed_tasks'], 1)
        self.assertEqual(stats['failed_tasks'], 1)
    
    def test_cleanup_old_tasks(self):
        """Test cleaning up old tasks"""
        # Add an old task
        old_task = {
            'id': 'old_task',
            'command': 'echo Old',
            'status': 'completed',
            'start_time': datetime.now() - timedelta(days=2),
            'end_time': datetime.now() - timedelta(days=2)
        }
        self.monitor.add_task(old_task)
        
        # Clean up tasks older than 1 day
        removed_count = self.monitor.cleanup_old_tasks(max_age_days=1)
        
        self.assertGreaterEqual(removed_count, 1)
        
        # Verify old task was removed
        task = self.monitor.get_task('old_task')
        self.assertIsNone(task)


class TestSystemStatsService(unittest.TestCase):
    """Test SystemStatsService class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.stats_service = SystemStatsService()
    
    @patch('psutil.cpu_percent')
    def test_get_cpu_usage(self, mock_cpu_percent):
        """Test getting CPU usage"""
        mock_cpu_percent.return_value = 45.5
        
        cpu_usage = self.stats_service.get_cpu_usage()
        
        self.assertIsInstance(cpu_usage, float)
        self.assertEqual(cpu_usage, 45.5)
        mock_cpu_percent.assert_called_once_with(interval=0.1)
    
    @patch('psutil.virtual_memory')
    def test_get_memory_usage(self, mock_virtual_memory):
        """Test getting memory usage"""
        mock_memory = Mock()
        mock_memory.percent = 65.2
        mock_memory.used = 1024 * 1024 * 1024  # 1GB
        mock_memory.total = 2 * 1024 * 1024 * 1024  # 2GB
        mock_virtual_memory.return_value = mock_memory
        
        memory_usage = self.stats_service.get_memory_usage()
        
        self.assertIsInstance(memory_usage, dict)
        self.assertIn('percent', memory_usage)
        self.assertIn('used_gb', memory_usage)
        self.assertIn('total_gb', memory_usage)
        
        self.assertEqual(memory_usage['percent'], 65.2)
        self.assertEqual(memory_usage['used_gb'], 1.0)
        self.assertEqual(memory_usage['total_gb'], 2.0)
    
    @patch('psutil.disk_usage')
    def test_get_disk_usage(self, mock_disk_usage):
        """Test getting disk usage"""
        mock_disk = Mock()
        mock_disk.percent = 75.5
        mock_disk.used = 500 * 1024 * 1024 * 1024  # 500GB
        mock_disk.total = 1000 * 1024 * 1024 * 1024  # 1TB
        mock_disk_usage.return_value = mock_disk
        
        disk_usage = self.stats_service.get_disk_usage()
        
        self.assertIsInstance(disk_usage, dict)
        self.assertIn('percent', disk_usage)
        self.assertIn('used_gb', disk_usage)
        self.assertIn('total_gb', disk_usage)
        
        self.assertEqual(disk_usage['percent'], 75.5)
        self.assertEqual(disk_usage['used_gb'], 500.0)
        self.assertEqual(disk_usage['total_gb'], 1000.0)
    
    @patch('psutil.net_io_counters')
    def test_get_network_stats(self, mock_net_io):
        """Test getting network statistics"""
        mock_counters = Mock()
        mock_counters.bytes_sent = 100 * 1024 * 1024  # 100MB
        mock_counters.bytes_recv = 200 * 1024 * 1024  # 200MB
        mock_counters.packets_sent = 5000
        mock_counters.packets_recv = 10000
        mock_net_io.return_value = mock_counters
        
        network_stats = self.stats_service.get_network_stats()
        
        self.assertIsInstance(network_stats, dict)
        self.assertIn('sent_mb', network_stats)
        self.assertIn('received_mb', network_stats)
        self.assertIn('packets_sent', network_stats)
        self.assertIn('packets_received', network_stats)
        
        self.assertEqual(network_stats['sent_mb'], 100.0)
        self.assertEqual(network_stats['received_mb'], 200.0)
        self.assertEqual(network_stats['packets_sent'], 5000)
        self.assertEqual(network_stats['packets_received'], 10000)
    
    @patch('psutil.process_iter')
    def test_get_process_info(self, mock_process_iter):
        """Test getting process information"""
        # Create mock processes
        mock_proc1 = Mock()
        mock_proc1.info = {'pid': 1234, 'name': 'python.exe', 'status': 'running'}
        
        mock_proc2 = Mock()
        mock_proc2.info = {'pid': 5678, 'name': 'chrome.exe', 'status': 'running'}
        
        mock_process_iter.return_value = [mock_proc1, mock_proc2]
        
        process_info = self.stats_service.get_process_info(limit=5)
        
        self.assertIsInstance(process_info, list)
        self.assertEqual(len(process_info), 2)
        self.assertEqual(process_info[0]['pid'], 1234)
        self.assertEqual(process_info[0]['name'], 'python.exe')
        self.assertEqual(process_info[1]['pid'], 5678)
        self.assertEqual(process_info[1]['name'], 'chrome.exe')
    
    def test_get_system_summary(self):
        """Test getting system summary"""
        with patch.object(self.stats_service, 'get_cpu_usage', return_value=45.5):
            with patch.object(self.stats_service, 'get_memory_usage', 
                            return_value={'percent': 65.2, 'used_gb': 1.0, 'total_gb': 2.0}):
                with patch.object(self.stats_service, 'get_disk_usage',
                                return_value={'percent': 75.5, 'used_gb': 500.0, 'total_gb': 1000.0}):
                    
                    summary = self.stats_service.get_system_summary()
                    
                    self.assertIsInstance(summary, dict)
                    self.assertIn('cpu_percent', summary)
                    self.assertIn('memory_percent', summary)
                    self.assertIn('disk_percent', summary)
                    self.assertIn('timestamp', summary)
                    
                    self.assertEqual(summary['cpu_percent'], 45.5)
                    self.assertEqual(summary['memory_percent'], 65.2)
                    self.assertEqual(summary['disk_percent'], 75.5)


class TestTaskCleanupService(unittest.TestCase):
    """Test TaskCleanupService class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cleanup_service = TaskCleanupService()
        
        # Create a mock task monitor
        self.mock_monitor = Mock()
        
        # Create test tasks
        self.test_tasks = {
            'task_1': {
                'id': 'task_1',
                'status': 'completed',
                'end_time': datetime.now() - timedelta(days=2)  # 2 days old
            },
            'task_2': {
                'id': 'task_2',
                'status': 'completed',
                'end_time': datetime.now() - timedelta(hours=12)  # 12 hours old
            },
            'task_3': {
                'id': 'task_3',
                'status': 'running',  # Still running
                'start_time': datetime.now() - timedelta(hours=1)
            },
            'task_4': {
                'id': 'task_4',
                'status': 'failed',
                'end_time': datetime.now() - timedelta(days=3)  # 3 days old
            }
        }
        
        # Configure mock
        self.mock_monitor.get_all_tasks.return_value = self.test_tasks
        self.mock_monitor.remove_task.side_effect = lambda task_id: self.test_tasks.pop(task_id, None)
    
    def test_cleanup_old_completed_tasks(self):
        """Test cleaning up old completed tasks"""
        # Set up mock
        self.cleanup_service.task_monitor = self.mock_monitor
        
        # Clean up tasks older than 1 day
        removed_tasks = self.cleanup_service.cleanup_old_completed_tasks(max_age_days=1)
        
        # Verify correct tasks were removed
        self.assertEqual(len(removed_tasks), 2)  # task_1 and task_4
        self.assertIn('task_1', removed_tasks)
        self.assertIn('task_4', removed_tasks)
        
        # Verify task_2 and task_3 were not removed
        self.assertIn('task_2', self.test_tasks)
        self.assertIn('task_3', self.test_tasks)
        
        # Verify remove_task was called for old tasks
        self.mock_monitor.remove_task.assert_any_call('task_1')
        self.mock_monitor.remove_task.assert_any_call('task_4')
    
    def test_cleanup_failed_tasks(self):
        """Test cleaning up failed tasks"""
        # Set up mock
        self.cleanup_service.task_monitor = self.mock_monitor
        
        # Clean up failed tasks older than 2 days
        removed_tasks = self.cleanup_service.cleanup_failed_tasks(max_age_days=2)
        
        # Verify only task_4 was removed (3 days old)
        self.assertEqual(len(removed_tasks), 1)
        self.assertIn('task_4', removed_tasks)
        
        # Verify remove_task was called for old failed task
        self.mock_monitor.remove_task.assert_called_once_with('task_4')
    
    def test_cleanup_stalled_tasks(self):
        """Test cleaning up stalled tasks"""
        # Create a task that appears stalled (running for too long)
        stalled_task = {
            'id': 'stalled_task',
            'status': 'running',
            'start_time': datetime.now() - timedelta(hours=3)  # Running for 3 hours
        }
        self.test_tasks['stalled_task'] = stalled_task
        
        # Set up mock
        self.cleanup_service.task_monitor = self.mock_monitor
        
        # Clean up tasks running for more than 2 hours
        removed_tasks = self.cleanup_service.cleanup_stalled_tasks(max_runtime_hours=2)
        
        # Verify stalled task was removed
        self.assertEqual(len(removed_tasks), 1)
        self.assertIn('stalled_task', removed_tasks)
        
        # Verify remove_task was called
        self.mock_monitor.remove_task.assert_called_once_with('stalled_task')
    
    def test_perform_comprehensive_cleanup(self):
        """Test performing comprehensive cleanup"""
        # Set up mock
        self.cleanup_service.task_monitor = self.mock_monitor
        
        # Mock the individual cleanup methods
        self.cleanup_service.cleanup_old_completed_tasks = Mock(return_value=['task_1'])
        self.cleanup_service.cleanup_failed_tasks = Mock(return_value=['task_4'])
        self.cleanup_service.cleanup_stalled_tasks = Mock(return_value=[])
        
        # Perform comprehensive cleanup
        result = self.cleanup_service.perform_comprehensive_cleanup(
            completed_max_age_days=1,
            failed_max_age_days=2,
            stalled_max_hours=24
        )
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('total_removed', result)
        self.assertIn('removed_completed', result)
        self.assertIn('removed_failed', result)
        self.assertIn('removed_stalled', result)
        
        self.assertEqual(result['total_removed'], 2)
        self.assertEqual(result['removed_completed'], ['task_1'])
        self.assertEqual(result['removed_failed'], ['task_4'])
        self.assertEqual(result['removed_stalled'], [])
        
        # Verify individual methods were called with correct parameters
        self.cleanup_service.cleanup_old_completed_tasks.assert_called_once_with(1)
        self.cleanup_service.cleanup_failed_tasks.assert_called_once_with(2)
        self.cleanup_service.cleanup_stalled_tasks.assert_called_once_with(24)


class TestCmdCLI(unittest.TestCase):
    """Test CmdCLI class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock services
        self.mock_executor = Mock()
        self.mock_monitor = Mock()
        self.mock_stats = Mock()
        self.mock_cleanup = Mock()
        
        # Create CLI instance with mock services
        self.cli = CmdCLI(
            command_executor=self.mock_executor,
            task_monitor=self.mock_monitor,
            system_stats=self.mock_stats,
            task_cleanup=self.mock_cleanup
        )
    
    def test_execute_command(self):
        """Test executing command via CLI"""
        # Mock executor response
        mock_result = {
            'command': 'echo Test',
            'output': 'Test\n',
            'return_code': 0,
            'timestamp': datetime.now().isoformat()
        }
        self.mock_executor.execute.return_value = mock_result
        
        # Execute command
        result = self.cli.execute_command('echo Test')
        
        # Verify result
        self.assertEqual(result, mock_result)
        self.mock_executor.execute.assert_called_once_with('echo Test', None, None)
    
    def test_list_tasks(self):
        """Test listing tasks via CLI"""
        # Mock monitor response
        mock_tasks = [
            {'id': 'task_1', 'command': 'echo 1', 'status': 'completed'},
            {'id': 'task_2', 'command': 'echo 2', 'status': 'running'}
        ]
        self.mock_monitor.get_all_tasks.return_value = mock_tasks
        
        # List tasks
        tasks = self.cli.list_tasks()
        
        # Verify result
        self.assertEqual(tasks, mock_tasks)
        self.mock_monitor.get_all_tasks.assert_called_once()
    
    def test_get_system_stats(self):
        """Test getting system stats via CLI"""
        # Mock stats response
        mock_stats = {
            'cpu_percent': 45.5,
            'memory_percent': 65.2,
            'disk_percent': 75.5,
            'timestamp': datetime.now().isoformat()
        }
        self.mock_stats.get_system_summary.return_value = mock_stats
        
        # Get stats
        stats = self.cli.get_system_stats()
        
        # Verify result
        self.assertEqual(stats, mock_stats)
        self.mock_stats.get_system_summary.assert_called_once()
    
    def test_cleanup_tasks(self):
        """Test cleaning up tasks via CLI"""
        # Mock cleanup response
        mock_result = {
            'total_removed': 3,
            'removed_completed': ['task_1', 'task_2'],
            'removed_failed': ['task_3'],
            'removed_stalled': []
        }
        self.mock_cleanup.perform_comprehensive_cleanup.return_value = mock_result
        
        # Cleanup tasks
        result = self.cli.cleanup_tasks()
        
        # Verify result
        self.assertEqual(result, mock_result)
        self.mock_cleanup.perform_comprehensive_cleanup.assert_called_once()


class TestCmdAgentRefactoredIntegration(unittest.TestCase):
    """Integration tests for CmdAgentRefactored"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = CmdAgent()
    
    def test_agent_initialization(self):
        """Test that agent initializes with all services"""
        self.assertIsNotNone(self.agent.command_executor)
        self.assertIsNotNone(self.agent.task_monitor)
        self.assertIsNotNone(self.agent.system_stats)
        self.assertIsNotNone(self.agent.task_cleanup)
        self.assertIsNotNone(self.agent.cli)
    
    def test_execute_command_through_agent(self):
        """Test executing command through agent"""
        # Mock the CLI's execute_command method
        mock_result = {
            'command': 'echo Integration Test',
            'output': 'Integration Test\n',
            'return_code': 0,
            'timestamp': datetime.now().isoformat()
        }
        self.agent.cli.execute_command = Mock(return_value=mock_result)
        
        # Execute command through agent
        result = self.agent.execute_command('echo Integration Test')
        
        # Verify result
        self.assertEqual(result, mock_result)
        self.agent.cli.execute_command.assert_called_once_with('echo Integration Test')
    
    def test_get_system_stats_through_agent(self):
        """Test getting system stats through agent"""
        # Mock the CLI's get_system_stats method
        mock_stats = {
            'cpu_percent': 30.5,
            'memory_percent': 50.2,
            'disk_percent': 60.5,
            'timestamp': datetime.now().isoformat()
        }
        self.agent.cli.get_system_stats = Mock(return_value=mock_stats)
        
        # Get stats through agent
        stats = self.agent.get_system_stats()
        
        # Verify result
        self.assertEqual(stats, mock_stats)
        self.agent.cli.get_system_stats.assert_called_once()


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)