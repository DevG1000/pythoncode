"""
API服务组件包
包含Flask应用、配置、模型、邮箱服务和内存管理
"""

from .app import app
from .config import Config
from .models import db, User, EmailVerification
from .email_service import mail, EmailVerificationService
from .memory_manager import MemoryMonitor, init_memory_monitoring, shutdown_memory_monitoring, get_resource_info, optimize_memory

__all__ = [
    'app',
    'Config',
    'db',
    'User',
    'EmailVerification',
    'mail',
    'EmailVerificationService',
    'MemoryMonitor',
    'init_memory_monitoring',
    'shutdown_memory_monitoring',
    'get_resource_info',
    'optimize_memory'
]