"""
Dependency Injection Container
Manages service dependencies and provides dependency injection.
"""

from typing import Dict, Any, Type, Optional
from .interfaces import (
    IEmailService, IAsyncTaskService, IMemoryMonitor, 
    IConfigProvider, IUserRepository, IEmailVerificationRepository
)


class DIContainer:
    """Dependency Injection Container"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._instances: Dict[Type, Any] = {}
    
    def register(self, interface: Type, implementation: Any, singleton: bool = True):
        """Register a service implementation"""
        self._services[interface] = {
            'implementation': implementation,
            'singleton': singleton
        }
    
    def get(self, interface: Type) -> Any:
        """Get service instance"""
        if interface not in self._services:
            raise ValueError(f"Service not registered: {interface}")
        
        service_info = self._services[interface]
        
        if service_info['singleton']:
            if interface not in self._instances:
                self._instances[interface] = service_info['implementation']()
            return self._instances[interface]
        else:
            return service_info['implementation']()
    
    def inject(self, cls):
        """Class decorator for dependency injection"""
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            # Get dependencies from type hints
            import inspect
            sig = inspect.signature(original_init)
            params = sig.parameters
            
            for param_name, param in params.items():
                if param_name == 'self':
                    continue
                
                param_type = param.annotation
                if param_type != inspect.Parameter.empty and param_name not in kwargs:
                    try:
                        kwargs[param_name] = self.get(param_type)
                    except ValueError:
                        # Service not registered, keep default
                        pass
            
            original_init(self, *args, **kwargs)
        
        cls.__init__ = new_init
        return cls


# Global DI container instance
container = DIContainer()


def register_default_services():
    """Register default service implementations"""
    # Import inside function to avoid circular imports
    from .config import Config
    
    # Register configuration provider
    class ConfigProvider(IConfigProvider):
        def get(self, key: str, default: Any = None) -> Any:
            return getattr(Config, key, default)
        
        def validate_email_config(self) -> bool:
            return Config.validate_email_config()
        
        @property
        def app_name(self) -> str:
            return Config.APP_NAME
    
    container.register(IConfigProvider, ConfigProvider)
    
    # Register async task service (lazy import)
    class AsyncTaskServiceImpl(IAsyncTaskService):
        def __init__(self):
            from command_system.async_tasks import AsyncTaskSystem
            self._system = AsyncTaskSystem()
            self._system.init_async_tasks()
        
        def submit_task(self, func: callable, *args, **kwargs) -> str:
            from command_system.async_tasks import submit_async_task
            return submit_async_task(func, *args, **kwargs)
        
        def get_task_status(self, task_id: str) -> Dict[str, Any]:
            from command_system.async_tasks import get_async_task_status
            return get_async_task_status(task_id)
        
        def get_stats(self) -> Dict[str, Any]:
            from command_system.async_tasks import get_async_stats
            return get_async_stats()
        
        def shutdown(self) -> None:
            from command_system.async_tasks import shutdown_async_tasks
            shutdown_async_tasks()
    
    container.register(IAsyncTaskService, AsyncTaskServiceImpl)
    
    # Register memory monitor (lazy import)
    class MemoryMonitorImpl(IMemoryMonitor):
        def __init__(self):
            from .memory_manager import MemoryMonitor
            self._monitor = MemoryMonitor()
        
        def start_monitoring(self, interval_seconds: int = 300) -> None:
            self._monitor.start_monitoring(interval_seconds)
        
        def stop_monitoring(self) -> None:
            self._monitor.stop_monitoring()
        
        def get_resource_info(self) -> Dict[str, Any]:
            return self._monitor.get_memory_info()
        
        def optimize_memory(self) -> Dict[str, Any]:
            return self._monitor.force_garbage_collection()
    
    container.register(IMemoryMonitor, MemoryMonitorImpl)
    
    # Register repositories (lazy import)
    class UserRepositoryImpl(IUserRepository):
        def __init__(self):
            from .models import db, User
            self.db = db
            self.User = User
        
        def create_user(self, username: str, email: str, password_hash: str):
            from datetime import datetime
            user = self.User(username=username, email=email, password_hash=password_hash)
            self.db.session.add(user)
            self.db.session.commit()
            return user
        
        def get_user_by_email(self, email: str):
            return self.User.query.filter_by(email=email).first()
        
        def get_user_by_username(self, username: str):
            return self.User.query.filter_by(username=username).first()
        
        def update_user_verification(self, user, verified: bool = True):
            from datetime import datetime
            user.email_verified = verified
            user.verified_at = datetime.now() if verified else None
            self.db.session.commit()
    
    container.register(IUserRepository, UserRepositoryImpl)
    
    class EmailVerificationRepositoryImpl(IEmailVerificationRepository):
        def __init__(self):
            from .models import db, EmailVerification
            self.db = db
            self.EmailVerification = EmailVerification
        
        def create_verification(self, user_id: int, token: str):
            verification = self.EmailVerification(user_id=user_id, token=token)
            self.db.session.add(verification)
            self.db.session.commit()
            return verification
        
        def get_verification_by_token(self, token: str):
            return self.EmailVerification.query.filter_by(token=token).first()
        
        def delete_verification(self, verification_id: int):
            verification = self.EmailVerification.query.get(verification_id)
            if verification:
                self.db.session.delete(verification)
                self.db.session.commit()
    
    container.register(IEmailVerificationRepository, EmailVerificationRepositoryImpl)


# Don't initialize services automatically - let the app initialize them
# This avoids circular imports at module load time