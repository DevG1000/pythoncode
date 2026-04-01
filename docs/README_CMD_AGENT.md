# CMD Agent - Windows Command Execution Tool

## Overview

CMD Agent is a standalone Windows command-line tool that provides asynchronous execution of Windows CMD commands with built-in timeout monitoring, concurrent execution (up to 7 commands), and deep integration with an existing asynchronous task system.

## Features

- **Asynchronous Command Execution**: Execute Windows CMD commands without blocking
- **Concurrent Processing**: Supports up to 7 concurrent command executions
- **Timeout Monitoring**: Automatic 15-second timeout with detailed logging
- **Task Management**: Full integration with existing async task system
- **Multiple Operation Modes**: Single command, batch execution, interactive shell
- **Comprehensive Logging**: Structured logging for monitoring and debugging
- **Safety Features**: Basic dangerous command detection
- **Statistics & Monitoring**: Real-time task statistics and status tracking

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   cmd_agent.py  │───▶│  cmd_tasks.py   │───▶│ async_tasks.py  │
│   (CLI Tool)    │    │ (Command Tasks) │    │ (Task Manager)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ config.py       │    │ command_executor│    │   Thread Pool   │
│ (Configuration) │    │ (Cmd Execution) │    │   (max=7)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Installation

### Prerequisites
- Python 3.7+
- Windows operating system
- Required Python packages (install via pip):

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install dependencies manually:

```bash
pip install pytest  # For testing only
```

### Project Structure
```
D:\pythoncode\
├── cmd_agent.py              # Main CLI tool
├── command_executor.py       # Core command execution
├── cmd_tasks.py             # Command task definitions
├── async_tasks.py           # Async task system (modified)
├── config.py                # Configuration (modified)
├── test_cmd_agent.py        # Test suite
├── README_CMD_AGENT.md      # This documentation
└── (other project files)
```

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# CMD Agent Configuration
CMD_TIMEOUT=15
CMD_MAX_WORKERS=7
CMD_WORKING_DIR=.
CMD_MAX_QUEUE_SIZE=100

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Security
ALLOW_DANGEROUS_COMMANDS=false
```

### Configuration File (config.py)
The agent uses `config.py` for centralized configuration. Key settings:

```python
# Command execution settings
CMD_TIMEOUT = 15  # seconds
CMD_MAX_WORKERS = 7  # maximum concurrent commands
CMD_WORKING_DIR = os.getcwd()  # default working directory
CMD_MAX_QUEUE_SIZE = 100  # maximum queued tasks

# Logging settings
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Security settings
ALLOW_DANGEROUS_COMMANDS = False
DANGEROUS_COMMAND_PATTERNS = [
    r'format\s+[A-Z]:',
    r'rm\s+-rf\s+/',
    r'del\s+/[FQ]\s+',
    # ... more patterns
]
```

## Usage

### Command Line Interface

#### 1. Single Command Execution
```bash
# Basic command execution
python cmd_agent.py exec "echo Hello World"

# With custom timeout
python cmd_agent.py exec "ping 127.0.0.1 -n 10" --timeout 5

# With custom working directory
python cmd_agent.py exec "dir" --working-dir "C:\Users"

# Verbose output
python cmd_agent.py exec "echo Test" --verbose
```

#### 2. Batch Execution
```bash
# Execute multiple commands from file
python cmd_agent.py batch commands.txt

# Execute list of commands
python cmd_agent.py batch "echo C1" "echo C2" "echo C3"

# With parallel execution limit
python cmd_agent.py batch commands.txt --max-parallel 3
```

#### 3. Interactive Shell
```bash
# Start interactive shell
python cmd_agent.py interactive

# Shell commands:
#   help                    - Show help
#   status                  - Show agent status
#   stats                   - Show statistics
#   exec <command>         - Execute command
#   history                - Show command history
#   clear                  - Clear screen
#   exit                   - Exit shell
```

#### 4. Status and Monitoring
```bash
# Show agent status
python cmd_agent.py status

# Show detailed statistics
python cmd_agent.py stats

# Show task history
python cmd_agent.py history

# Clean up completed tasks
python cmd_agent.py cleanup

# Stop the agent
python cmd_agent.py stop
```

#### 5. Help
```bash
# Show help
python cmd_agent.py --help

# Show command-specific help
python cmd_agent.py exec --help
python cmd_agent.py batch --help
```

### Programmatic Usage

#### Basic Command Execution
```python
from cmd_agent import CmdAgent

# Create agent
agent = CmdAgent()

# Execute single command
result = agent.execute_command("echo Hello World")
print(f"Success: {result.success}")
print(f"Output: {result.stdout}")
print(f"Exit Code: {result.exit_code}")

# Execute batch commands
commands = ["echo Command1", "echo Command2", "echo Command3"]
results = agent.execute_batch(commands)

# Get agent status
status = agent.get_status()
print(f"Running: {status['running']}")
print(f"Active Tasks: {status['statistics']['active_tasks']}")

# Stop agent
agent.stop()
```

#### Using Command Tasks
```python
from cmd_tasks import create_command_task
from async_tasks import submit_command_task

# Create command task
task = create_command_task(
    command="dir /w",
    task_id="dir-task-001",
    description="List directory in wide format"
)

# Submit task for execution
submit_command_task("echo Task submitted")

# Or submit the created task
from async_tasks import task_manager
task_manager.submit(task)

# Wait for completion
import time
while task.status != "completed":
    time.sleep(0.1)

# Get result
if task.result.success:
    print(f"Output: {task.result.stdout}")
```

## Logging

The agent uses structured logging with prefixes for easy filtering:

- `[CMD]` - Command execution logs
- `[CMD-TASK]` - Command task logs
- `[AGENT]` - Agent management logs
- `[ASYNC-TASKS]` - Async task system logs

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General operational information
- `WARNING`: Warning messages
- `ERROR`: Error conditions
- `CRITICAL`: Critical errors

### Example Log Output
```
2024-01-15 10:30:45 - CMD - INFO - [CMD] Executing command: echo Hello World
2024-01-15 10:30:45 - CMD-TASK - INFO - [CMD-TASK] Task cmd-123 started
2024-01-15 10:30:45 - CMD - INFO - [CMD] Command completed in 0.12s: exit_code=0
2024-01-15 10:30:45 - CMD-TASK - INFO - [CMD-TASK] Task cmd-123 completed successfully
2024-01-15 10:30:46 - AGENT - INFO - [AGENT] Statistics: total=5, completed=5, failed=0
```

## Error Handling

### Timeout Handling
Commands that exceed the 15-second timeout are automatically terminated:
```bash
# This command will timeout after 15 seconds
python cmd_agent.py exec "ping 127.0.0.1 -n 20 > nul"

# Output:
# [CMD] Command timed out after 15.00s
# [CMD-TASK] Task failed due to timeout
```

### Error Recovery
- Failed commands are logged with detailed error information
- The agent continues processing other commands
- Task statistics track success/failure rates

### Security Features
- Basic dangerous command detection
- Configurable security settings
- Command validation before execution

## Testing

### Running Tests
```bash
# Run all tests
python test_cmd_agent.py

# Run specific test class
python -m pytest test_cmd_agent.py::TestCommandExecutor -v

# Run with coverage
python -m pytest test_cmd_agent.py --cov=.
```

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **End-to-End Tests**: Full workflow testing
4. **Performance Tests**: Concurrent execution testing

### Test Examples
```python
# Test command execution
def test_execute_success():
    executor = CommandExecutor()
    result = executor.execute("echo Test")
    assert result.success is True
    assert "Test" in result.stdout

# Test timeout handling
def test_execute_timeout():
    executor = CommandExecutor(timeout=2)
    result = executor.execute("ping 127.0.0.1 -n 5 > nul")
    assert result.timed_out is True
    assert result.exit_code == -1

# Test concurrent execution
def test_concurrent_execution():
    agent = CmdAgent()
    commands = [f"echo Task{i}" for i in range(5)]
    results = agent.execute_batch(commands)
    assert len(results) == 5
    assert all(r.success for r in results)
```

## Performance

### Concurrency Limits
- Maximum 7 concurrent command executions
- Configurable via `CMD_MAX_WORKERS`
- Queue size limit: 100 tasks

### Resource Usage
- Lightweight thread-based architecture
- Memory-efficient task management
- Automatic resource cleanup

### Optimization Tips
1. Use batch execution for multiple commands
2. Adjust timeout based on command complexity
3. Monitor queue size to prevent overload
4. Use appropriate working directories

## Integration with Existing System

### Async Task System Integration
The CMD Agent deeply integrates with the existing async task system:

```python
# Reuses existing AsyncTaskManager
from async_tasks import task_manager

# Uses existing task statuses
from async_tasks import TaskStatus

# Integrates with existing configuration
from config import CMD_MAX_WORKERS, CMD_TIMEOUT
```

### Modifications Made
1. **async_tasks.py**: Updated to support 7 concurrent workers
2. **config.py**: Added CMD Agent configuration
3. **New modules**: command_executor.py, cmd_tasks.py, cmd_agent.py

## Troubleshooting

### Common Issues

#### 1. Command Not Found
```
Error: 'invalid_command' is not recognized as an internal or external command
```
**Solution**: Verify command syntax and availability on Windows.

#### 2. Timeout Too Short
```
[CMD] Command timed out after 15.00s
```
**Solution**: Increase timeout with `--timeout` parameter.

#### 3. Permission Denied
```
Access is denied.
```
**Solution**: Run as administrator or adjust command permissions.

#### 4. Queue Full
```
Task queue is full (max: 100)
```
**Solution**: Process pending tasks or increase `CMD_MAX_QUEUE_SIZE`.

### Debugging
```bash
# Enable debug logging
python cmd_agent.py exec "echo Test" --verbose

# Check agent status
python cmd_agent.py status

# View detailed statistics
python cmd_agent.py stats --detailed
```

## Security Considerations

### Command Validation
- Basic dangerous command pattern matching
- Configurable via `DANGEROUS_COMMAND_PATTERNS`
- Can be disabled with `ALLOW_DANGEROUS_COMMANDS=true`

### Safe Practices
1. **Validate Input**: Sanitize command parameters
2. **Use Timeouts**: Prevent hanging commands
3. **Limit Permissions**: Run with minimal required privileges
4. **Monitor Logs**: Regularly review command execution logs

### Security Configuration
```python
# Enable/disable dangerous commands
ALLOW_DANGEROUS_COMMANDS = False

# Custom dangerous patterns
DANGEROUS_COMMAND_PATTERNS = [
    r'format\s+[A-Z]:',
    r'rm\s+-rf\s+/',
    r'del\s+/[FQ]\s+',
    r'chkdsk\s+/[FR]',
    r'diskpart',
    r'reg\s+(add|delete)',
]
```

## API Reference

### CommandExecutor Class
```python
class CommandExecutor:
    def execute(command: str, timeout: int = None) -> CommandResult
    # Executes a Windows CMD command with timeout
```

### CommandTask Class
```python
class CommandTask(AsyncTask):
    command: str  # Command to execute
    timeout: int  # Execution timeout
    result: CommandResult  # Execution result
```

### CmdAgent Class
```python
class CmdAgent:
    def execute_command(command: str, **kwargs) -> CommandResult
    def execute_batch(commands: List[str], **kwargs) -> List[CommandResult]
    def get_status() -> Dict
    def get_statistics() -> Dict
    def stop() -> None
```

### CommandResult Dataclass
```python
@dataclass
class CommandResult:
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    timed_out: bool
```

## Examples

### Example 1: System Information Collection
```bash
# Collect system information
python cmd_agent.py batch \
  "systeminfo" \
  "wmic cpu get name" \
  "wmic memorychip get capacity" \
  "ipconfig /all"
```

### Example 2: File Operations
```bash
# Batch file operations
python cmd_agent.py batch \
  "dir C:\Users /s /b *.txt > files.txt" \
  "type files.txt | find /c /v \"\" > count.txt" \
  "del files.txt count.txt"
```

### Example 3: Network Diagnostics
```bash
# Network diagnostics with timeout
python cmd_agent.py batch \
  "ping google.com -n 4" \
  "tracert google.com" \
  "netstat -an" \
  --timeout 30
```

### Example 4: Integration Script
```python
#!/usr/bin/env python3
"""
Example integration script using CMD Agent.
"""

from cmd_agent import CmdAgent
import json

def collect_system_info():
    """Collect comprehensive system information."""
    agent = CmdAgent()
    
    commands = [
        "echo System Information Collection",
        "systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\"",
        "wmic cpu get name, numberofcores, maxclockspeed",
        "wmic memorychip get capacity, speed",
        "ipconfig | findstr IPv4",
        "dir C:\\ /a | find \"File(s)\""
    ]
    
    print("Starting system information collection...")
    results = agent.execute_batch(commands)
    
    info = {}
    for i, result in enumerate(results):
        if result.success:
            info[f"command_{i}"] = {
                "output": result.stdout.strip(),
                "execution_time": result.execution_time
            }
    
    agent.stop()
    
    # Save to JSON
    with open("system_info.json", "w") as f:
        json.dump(info, f, indent=2)
    
    print(f"Information saved to system_info.json")
    return info

if __name__ == "__main__":
    collect_system_info()
```

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python test_cmd_agent.py`
4. Make changes following existing code patterns

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to public functions
- Write comprehensive tests

### Testing Guidelines
1. Test all new functionality
2. Maintain existing test coverage
3. Test edge cases and error conditions
4. Verify integration with existing system

## License

This project is part of the existing Python codebase. See the main project license for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the documentation
3. Examine the logs for error details
4. Contact the development team

## Changelog

### Version 1.0.0 (Initial Release)
- Standalone Windows CMD command execution tool
- Support for 7 concurrent command executions
- 15-second timeout with detailed logging
- Integration with existing async task system
- Multiple operation modes (exec, batch, interactive)
- Comprehensive testing suite
- Detailed documentation