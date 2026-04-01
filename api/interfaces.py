"""
Dependency Injection Interfaces for API Service
Defines abstract contracts to decouple components and follow DIP.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class IEmailService(ABC):
    """Abstract interface for email services"""
    
    @abstractmethod
    def send_verification_email(self, user, verification_url: str, async_mode: bool = True) -> Dict[str, Any]:
        """Send email verification email"""
        pass
    
    @abstractmethod
    def send_welcome_email(self, user, async_mode: bool = True) -> Dict[str, Any]:
        """Send welcome email after verification"""
        pass
    
    @abstractmethod
    def verify_token(self, token: str, max_age: int = 86400) -> Optional[str]:
        """Verify email verification token"""
        pass


class IAsyncTaskService(ABC):
    """Abstract interface for async task services"""
    
    @abstractmethod
    def submit_task(self, func: callable, *args, **kwargs) -> str:
        """Submit a task for async execution"""
        pass
    
    @abstractmethod
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of an async task"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get async task system statistics"""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown async task system"""
        pass


class IMemoryMonitor(ABC):
    """Abstract interface for memory monitoring"""
    
    @abstractmethod
    def start_monitoring(self, interval_seconds: int = 300) -> None:
        """Start memory monitoring"""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        """Stop memory monitoring"""
        pass
    
    @abstractmethod
    def get_resource_info(self) -> Dict[str, Any]:
        """Get current resource usage information"""
        pass
    
    @abstractmethod
    def optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage"""
        pass


class IConfigProvider(ABC):
    """Abstract interface for configuration providers"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        pass
    
    @abstractmethod
    def validate_email_config(self) -> bool:
        """Validate email configuration"""
        pass
    
    @property
    @abstractmethod
    def app_name(self) -> str:
        """Get application name"""
        pass


class IUserRepository(ABC):
    """Abstract interface for user data access"""
    
    @abstractmethod
    def create_user(self, username: str, email: str, password_hash: str) -> Any:
        """Create a new user"""
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Any]:
        """Get user by email"""
        pass
    
    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[Any]:
        """Get user by username"""
        pass
    
    @abstractmethod
    def update_user_verification(self, user, verified: bool = True) -> None:
        """Update user verification status"""
        pass


class IEmailVerificationRepository(ABC):
    """Abstract interface for email verification data access"""
    
    @abstractmethod
    def create_verification(self, user_id: int, token: str) -> Any:
        """Create email verification record"""
        pass
    
    @abstractmethod
    def get_verification_by_token(self, token: str) -> Optional[Any]:
        """Get verification by token"""
        pass
    
    @abstractmethod
    def delete_verification(self, verification_id: int) -> None:
        """Delete verification record"""
        pass