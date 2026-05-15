# AGENTS.md - Python Codebase Guidelines

This document provides guidelines for agentic coding agents working in this Python codebase.

## Project Overview

This is a multi-service Python project containing:
- **API Service** (`app.py`): User registration API with email verification, password encryption, and async task management
- **CMD Agent** (`cmd_agent.py`): Windows command execution agent with async task system (max 7 concurrent workers)
- **Architecture Quality Agent** (`architecture_agent.py`): Architecture quality assessment agent for SOLID principles and dependency analysis
- **Business Card Generator** (`Line2Card.py`): Excel data to image-based business cards
- **Utility Modules**: String utilities, memory management, email service, Redis manager
- **Testing**: Comprehensive pytest test suites for all major components
- **Docker**: Full containerized deployment with Docker Compose

## Build, Lint, and Test Commands

### Environment Setup
```bash
# Install all dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Verify installation
python -c "import flask; import pytest; import redis; print('All packages installed successfully')"
```

### Running Services
```bash
# Run API service (Flask)
python app.py

# Run CMD Agent (interactive mode)
python cmd_agent.py interactive

# Run CMD Agent (single command)
python cmd_agent.py execute "echo Hello"

# Run business card generator
python Line2Card.py

# Run architecture quality assessment agent
python architecture_agent.py assess

# Run DeepSeek API test
python deepseekeytest.py
```

### Testing Commands
```bash
# Run all tests with pytest
pytest

# Run specific test file
pytest test_string_utils.py
pytest test_cmd_agent.py
pytest test_api.py

# Run single test class
pytest test_string_utils.py::TestReverseWords
pytest test_cmd_agent.py::TestCommandExecutor

# Run single test method
pytest test_string_utils.py::TestReverseWords::test_single_word
pytest test_cmd_agent.py::TestCommandExecutor::test_execute_success

# Run tests with coverage report
pytest --cov=. --cov-report=html

# Run tests verbosely
pytest -v

# Run tests and stop on first failure
pytest -x

# Run specific test by name pattern
pytest -k "test_execute"

# Run tests without capturing output (see print statements)
pytest -s
```

### Docker Commands
```bash
# Build and start all services
docker-compose up -d

# Build specific service
docker-compose build api

# Start specific service
docker-compose up api -d

# View logs
docker-compose logs -f api
docker-compose logs -f cmd-agent

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Run tests in Docker
docker-compose run api pytest
```

### Code Quality
```bash
# Check Python syntax
python -m py_compile *.py

# Type checking with mypy
python -m mypy *.py --ignore-missing-imports

# Linting with flake8
python -m flake8 *.py --max-line-length=120

# Formatting with black
python -m black *.py

# Sort imports with isort
python -m isort *.py
```

## Code Style Guidelines

### Imports Structure
```python
# Standard library imports first
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Third-party imports next
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis
import pytest

# Local/application imports last
from config import Config
from models import db, User
from email_service import EmailVerificationService
```

### Formatting Rules
- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 120 characters (project uses 120, not PEP 8's 79)
- **Quotes**: Single quotes for strings, double quotes for docstrings
- **Blank lines**: Two blank lines between top-level functions/classes, one blank line between methods
- **Trailing commas**: Include in multi-line collections
- **Line breaks**: Break before binary operators

### Naming Conventions
- **Functions and variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Classes**: `PascalCase`
- **Private members**: `_leading_underscore`
- **Protected members**: `_single_leading_underscore`
- **Module-level dunder**: `__all__` for public API

### Function Definitions
```python
def function_name(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    Brief description of function.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter (default: None)
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When invalid parameter is provided
        RuntimeError: When operation fails
    
    Examples:
        >>> function_name("test", 123)
        {'result': 'test_123'}
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    result = process_data(param1, param2)
    return {"result": result}
```

### Error Handling
```python
# Use specific exceptions
try:
    result = risky_operation()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    return {"error": "File not found", "code": 404}
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    return {"error": "Connection failed", "code": 503}
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

### Type Hints (Required)
```python
from typing import Dict, List, Optional, Union, Any

def process_data(
    data: Dict[str, Any],
    max_items: Optional[int] = None
) -> List[Dict[str, Union[str, int]]]:
    """Process data with full type hints."""
    if not data:
        return []
    
    items = data.get("items", [])
    if max_items:
        items = items[:max_items]
    
    return [{"id": i, "value": v} for i, v in enumerate(items)]
```

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debug information")
logger.info("Normal operational messages")
logger.warning("Warning messages")
logger.error("Error conditions")
logger.critical("Critical conditions")
```

## Project-Specific Patterns

### Async Task System
- Use `AsyncTaskManager` for background task execution
- Maximum 7 concurrent workers (configurable via `CMD_MAX_WORKERS`)
- 15-second default timeout (configurable via `CMD_TIMEOUT`)
- Tasks implement `AsyncTask` interface with `run()` method
- Use `submit_command_task()` for command execution tasks

### API Development
- Use Flask with Flask-SQLAlchemy for database operations
- Implement proper error handling with JSON responses
- Use environment variables for configuration (`.env` file)
- Implement email verification with tokens
- Use bcrypt for password hashing (never store plaintext)

### Command Execution (CMD Agent)
- Validate commands for safety before execution
- Use `CommandExecutor` class for command execution
- Implement timeout handling
- Log all command executions with results
- Support both synchronous and asynchronous execution

### Database Operations
- Use SQLAlchemy ORM with connection pooling
- SQLite for development, PostgreSQL for production
- Implement proper migrations (Alembic recommended)
- Use transaction blocks for atomic operations
- Implement connection retry logic

### Testing Patterns
- Use pytest for all testing
- Organize tests by component (unit, integration, e2e)
- Use fixtures for test setup/teardown
- Mock external dependencies (APIs, databases)
- Test error conditions and edge cases
- Use parameterized tests for multiple scenarios

## File Structure
```
project/
├── AGENTS.md              # This file
├── app.py                # Main Flask API
├── cmd_agent.py          # CMD Agent system
├── architecture_agent.py # Architecture quality assessment agent
├── Line2Card.py          # Business card generator
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Docker build configuration
├── .env.example         # Environment variables template
├── config.py            # Application configuration
├── models.py            # Database models
├── email_service.py     # Email service
├── memory_manager.py    # Memory monitoring
├── redis_manager.py     # Redis client
├── async_tasks.py       # Async task system
├── command_executor.py  # Command execution
├── cmd_tasks.py         # CMD task definitions
├── string_utils.py      # String utilities
├── test_*.py           # Test files
├── instance/           # SQLite database files
├── logs/              # Application logs
└── data/              # Data files
```

## Security Best Practices

1. **Never commit secrets**: Use `.env` file for environment variables
2. **Validate all inputs**: Sanitize user inputs, especially for command execution
3. **Use prepared statements**: Prevent SQL injection with ORM/parameterized queries
4. **Implement rate limiting**: Protect APIs from abuse
5. **Use HTTPS**: Always in production, enforce in development
6. **Hash passwords**: Use bcrypt with appropriate work factor
7. **Secure file uploads**: Validate file types, scan for malware
8. **Implement CORS**: Restrict cross-origin requests appropriately

## Performance Considerations

1. **Database optimization**: Use indexes, connection pooling, query optimization
2. **Memory management**: Monitor memory usage, implement cleanup routines
3. **Async operations**: Use async tasks for long-running operations
4. **Caching**: Implement Redis caching for frequently accessed data
5. **File handling**: Use context managers, stream large files
6. **Logging optimization**: Use appropriate log levels, rotate logs

## Troubleshooting

### Common Issues
1. **Database connection errors**: Check `.env` file, database service status
2. **Email sending failures**: Verify SMTP configuration in `.env`
3. **Command execution failures**: Check command syntax, permissions
4. **Import errors**: Verify Python path, virtual environment
5. **Docker issues**: Check Docker service, port conflicts

### Debugging Commands
```bash
# Check service status
docker-compose ps

# View application logs
docker-compose logs api

# Check database
sqlite3 instance/users.db ".tables"

# Test API endpoints
curl http://localhost:5000/api/health

# Test Redis connection
redis-cli ping

# Run performance analysis
python performance_analysis.py
```

## Notes for Agents

- This is a Windows-based project but supports cross-platform via Docker
- Use Windows-style paths (backslashes) for file operations
- Font paths in `Line2Card.py` are Windows-specific
- Command execution defaults to Windows CMD syntax
- Always test changes before considering work complete
- Follow existing patterns in the codebase for consistency
- Update tests when modifying functionality
- Run `pytest` after making changes to ensure no regressions