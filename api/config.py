"""
Configuration for Flask Application
Uses centralized configuration system.
"""

from config import get_config

# Get centralized configuration
config_manager = get_config()


class Config:
    """Flask configuration class"""
    
    # Application settings
    SECRET_KEY = config_manager.get('app.secret_key', 'dev-secret-key-change-in-production')
    APP_NAME = config_manager.get('app.name', 'PythonCode')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = config_manager.get('database.url', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database connection pool optimization
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': config_manager.get('database.pool_size', 10),
        'max_overflow': config_manager.get('database.max_overflow', 20),
        'pool_recycle': config_manager.get('database.pool_recycle', 3600),
        'pool_pre_ping': True,
        'pool_timeout': 30,
    }
    
    # SQLite specific optimization
    if 'sqlite' in (config_manager.get('database.url') or 'sqlite:///app.db'):
        SQLALCHEMY_ENGINE_OPTIONS.update({
            'connect_args': {
                'check_same_thread': False,
                'timeout': 30,
                'isolation_level': None,
            }
        })
    
    # Email configuration
    MAIL_SERVER = config_manager.get('email.server', 'smtp.gmail.com')
    MAIL_PORT = config_manager.get('email.port', 587)
    MAIL_USE_TLS = config_manager.get('email.use_tls', True)
    MAIL_USERNAME = config_manager.get('email.username')
    MAIL_PASSWORD = config_manager.get('email.password')
    MAIL_DEFAULT_SENDER = config_manager.get('email.default_sender')
    
    # Application settings from config
    VERIFICATION_TOKEN_EXPIRY = config_manager.get('email.verification_token_expiry', 86400)
    
    # API settings
    API_HOST = config_manager.get('api.host', '0.0.0.0')
    API_PORT = config_manager.get('api.port', 5000)
    
    @classmethod
    def validate_email_config(cls):
        """Validate email configuration"""
        required = ['MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER']
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            print(f"Warning: Email configuration missing: {missing}")
            print("Email verification will not work without proper email configuration.")
            return False
        return True
    
    @classmethod
    def get_config_summary(cls):
        """Get configuration summary"""
        return {
            'app': {
                'name': cls.APP_NAME,
                'environment': config_manager.get('app.environment', 'development'),
                'debug': config_manager.get('app.debug', False)
            },
            'database': {
                'url': cls.SQLALCHEMY_DATABASE_URI[:50] + '...' if len(cls.SQLALCHEMY_DATABASE_URI) > 50 else cls.SQLALCHEMY_DATABASE_URI,
                'pool_size': cls.SQLALCHEMY_ENGINE_OPTIONS['pool_size']
            },
            'email': {
                'server': cls.MAIL_SERVER,
                'port': cls.MAIL_PORT,
                'username_set': bool(cls.MAIL_USERNAME),
                'password_set': bool(cls.MAIL_PASSWORD),
                'sender_set': bool(cls.MAIL_DEFAULT_SENDER)
            },
            'api': {
                'host': cls.API_HOST,
                'port': cls.API_PORT
            }
        }
    
    @classmethod
    def validate_all(cls):
        """Validate all configurations"""
        validation = config_manager.validate()
        
        # Additional Flask-specific validation
        if not cls.validate_email_config():
            validation['valid'] = False
            validation['errors'].append('Email configuration incomplete')
        
        return validation