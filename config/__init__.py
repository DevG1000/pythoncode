"""
Centralized Configuration Management System
Provides unified configuration access for all modules.
"""

import os
import json
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ConfigManager:
    """Centralized configuration manager"""
    
    _instance = None
    _config_cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize configuration manager"""
        self.config_base = Path(__file__).parent
        self._load_configurations()
    
    def _load_configurations(self):
        """Load all configuration files"""
        # Load environment-based config
        self._load_env_config()
        
        # Load YAML config files if they exist
        self._load_yaml_configs()
        
        # Load JSON config files if they exist
        self._load_json_configs()
    
    def _load_env_config(self):
        """Load configuration from environment variables"""
        env_config = {}
        
        # Application settings
        env_config['app'] = {
            'name': os.environ.get('APP_NAME', 'PythonCode'),
            'version': os.environ.get('APP_VERSION', '1.0.0'),
            'environment': os.environ.get('ENVIRONMENT', 'development'),
            'debug': os.environ.get('DEBUG', 'false').lower() == 'true',
            'secret_key': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        }
        
        # Database settings
        env_config['database'] = {
            'url': os.environ.get('DATABASE_URL', 'sqlite:///app.db'),
            'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
            'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),
            'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600')),
            'echo': os.environ.get('DB_ECHO', 'false').lower() == 'true'
        }
        
        # Email settings
        env_config['email'] = {
            'server': os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
            'port': int(os.environ.get('MAIL_PORT', '587')),
            'use_tls': os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true',
            'username': os.environ.get('MAIL_USERNAME'),
            'password': os.environ.get('MAIL_PASSWORD'),
            'default_sender': os.environ.get('MAIL_DEFAULT_SENDER'),
            'verification_token_expiry': int(os.environ.get('VERIFICATION_TOKEN_EXPIRY', '86400'))
        }
        
        # Command system settings
        env_config['command_system'] = {
            'timeout': int(os.environ.get('CMD_TIMEOUT', '15')),
            'max_workers': int(os.environ.get('CMD_MAX_WORKERS', '7')),
            'working_dir': os.environ.get('CMD_WORKING_DIR', '.'),
            'max_queue_size': int(os.environ.get('CMD_MAX_QUEUE_SIZE', '100')),
            'enable_validation': os.environ.get('CMD_ENABLE_VALIDATION', 'true').lower() == 'true',
            'allowed_commands': [c.strip() for c in os.environ.get('CMD_ALLOWED_COMMANDS', '').split(',') if c.strip()],
            'denied_commands': [c.strip() for c in os.environ.get('CMD_DENIED_COMMANDS', '').split(',') if c.strip()],
            'log_level': os.environ.get('CMD_LOG_LEVEL', 'INFO'),
            'log_file': os.environ.get('CMD_LOG_FILE'),
            'enable_monitoring': os.environ.get('CMD_ENABLE_MONITORING', 'true').lower() == 'true',
            'monitor_interval': int(os.environ.get('CMD_MONITOR_INTERVAL', '60'))
        }
        
        # Card generator settings
        env_config['card_generator'] = {
            'default_template': os.environ.get('CARD_DEFAULT_TEMPLATE', 'default'),
            'output_format': os.environ.get('CARD_OUTPUT_FORMAT', 'png'),
            'output_quality': int(os.environ.get('CARD_OUTPUT_QUALITY', '95')),
            'max_image_width': int(os.environ.get('CARD_MAX_IMAGE_WIDTH', '1200')),
            'max_image_height': int(os.environ.get('CARD_MAX_IMAGE_HEIGHT', '800'))
        }
        
        # Logging settings
        env_config['logging'] = {
            'level': os.environ.get('LOG_LEVEL', 'INFO'),
            'format': os.environ.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'file': os.environ.get('LOG_FILE'),
            'max_size_mb': int(os.environ.get('LOG_MAX_SIZE_MB', '10')),
            'backup_count': int(os.environ.get('LOG_BACKUP_COUNT', '5'))
        }
        
        # API settings
        env_config['api'] = {
            'host': os.environ.get('API_HOST', '0.0.0.0'),
            'port': int(os.environ.get('API_PORT', '5000')),
            'workers': int(os.environ.get('API_WORKERS', '4')),
            'cors_origins': [o.strip() for o in os.environ.get('CORS_ORIGINS', '*').split(',')],
            'rate_limit': os.environ.get('RATE_LIMIT', '100 per minute'),
            'enable_swagger': os.environ.get('ENABLE_SWAGGER', 'true').lower() == 'true'
        }
        
        # Cache settings
        env_config['cache'] = {
            'type': os.environ.get('CACHE_TYPE', 'memory'),
            'redis_url': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            'default_timeout': int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
        }
        
        self._config_cache.update(env_config)
    
    def _load_yaml_configs(self):
        """Load configuration from YAML files"""
        yaml_files = [
            self.config_base / 'config.yaml',
            self.config_base / 'config.local.yaml',
            self.config_base / 'secrets.yaml'
        ]
        
        for yaml_file in yaml_files:
            if yaml_file.exists():
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        yaml_config = yaml.safe_load(f)
                        if yaml_config:
                            self._merge_config(self._config_cache, yaml_config)
                except Exception as e:
                    print(f"Warning: Failed to load YAML config {yaml_file}: {e}")
    
    def _load_json_configs(self):
        """Load configuration from JSON files"""
        json_files = [
            self.config_base / 'config.json',
            self.config_base / 'config.local.json'
        ]
        
        for json_file in json_files:
            if json_file.exists():
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json_config = json.load(f)
                        if json_config:
                            self._merge_config(self._config_cache, json_config)
                except Exception as e:
                    print(f"Warning: Failed to load JSON config {json_file}: {e}")
    
    def _merge_config(self, target: Dict, source: Dict):
        """Merge source configuration into target"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot notation key
        
        Args:
            key: Dot notation key (e.g., 'app.name', 'database.url')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config_cache
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        Set configuration value by dot notation key
        
        Args:
            key: Dot notation key
            value: Value to set
        """
        keys = key.split('.')
        config = self._config_cache
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict:
        """
        Get entire configuration section
        
        Args:
            section: Section name
            
        Returns:
            Configuration section dictionary
        """
        return self._config_cache.get(section, {})
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate all configurations
        
        Returns:
            Validation results dictionary
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sections': {}
        }
        
        # Validate app section
        app_results = self._validate_app()
        results['sections']['app'] = app_results
        if not app_results['valid']:
            results['valid'] = False
            results['errors'].extend(app_results['errors'])
        
        # Validate database section
        db_results = self._validate_database()
        results['sections']['database'] = db_results
        if not db_results['valid']:
            results['valid'] = False
            results['errors'].extend(db_results['errors'])
        
        # Validate email section
        email_results = self._validate_email()
        results['sections']['email'] = email_results
        if not email_results['valid']:
            results['warnings'].extend(email_results['errors'])  # Email errors are warnings
        
        # Validate command system section
        cmd_results = self._validate_command_system()
        results['sections']['command_system'] = cmd_results
        if not cmd_results['valid']:
            results['valid'] = False
            results['errors'].extend(cmd_results['errors'])
        
        return results
    
    def _validate_app(self) -> Dict[str, Any]:
        """Validate app configuration"""
        errors = []
        warnings = []
        
        app_config = self.get_section('app')
        
        # Check secret key in production
        if app_config.get('environment') == 'production':
            if app_config.get('secret_key', '').startswith('dev-'):
                errors.append("SECRET_KEY must be changed in production environment")
        
        # Check debug mode in production
        if app_config.get('environment') == 'production' and app_config.get('debug'):
            warnings.append("Debug mode should be disabled in production")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_database(self) -> Dict[str, Any]:
        """Validate database configuration"""
        errors = []
        warnings = []
        
        db_config = self.get_section('database')
        
        # Check database URL
        db_url = db_config.get('url', '')
        if not db_url:
            errors.append("DATABASE_URL is required")
        elif 'sqlite' in db_url:
            warnings.append("SQLite is not recommended for production")
        
        # Check connection pool settings
        pool_size = db_config.get('pool_size', 10)
        if pool_size <= 0:
            errors.append("DB_POOL_SIZE must be positive")
        
        max_overflow = db_config.get('max_overflow', 20)
        if max_overflow < 0:
            errors.append("DB_MAX_OVERFLOW must be non-negative")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_email(self) -> Dict[str, Any]:
        """Validate email configuration"""
        errors = []
        
        email_config = self.get_section('email')
        
        # Check required email settings
        required_fields = ['username', 'password', 'default_sender']
        missing_fields = []
        
        for field in required_fields:
            if not email_config.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            errors.append(f"Email configuration incomplete. Missing: {', '.join(missing_fields)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
    
    def _validate_command_system(self) -> Dict[str, Any]:
        """Validate command system configuration"""
        errors = []
        warnings = []
        
        cmd_config = self.get_section('command_system')
        
        # Check timeout
        timeout = cmd_config.get('timeout', 15)
        if timeout <= 0:
            errors.append("CMD_TIMEOUT must be positive")
        
        # Check max workers
        max_workers = cmd_config.get('max_workers', 7)
        if max_workers <= 0:
            errors.append("CMD_MAX_WORKERS must be positive")
        
        # Check queue size
        max_queue_size = cmd_config.get('max_queue_size', 100)
        if max_queue_size <= 0:
            errors.append("CMD_MAX_QUEUE_SIZE must be positive")
        
        # Check working directory
        working_dir = cmd_config.get('working_dir', '.')
        if not os.path.exists(working_dir):
            warnings.append(f"CMD_WORKING_DIR does not exist: {working_dir}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def to_dict(self) -> Dict:
        """Get all configuration as dictionary"""
        return self._config_cache.copy()
    
    def save_to_file(self, filepath: str, format: str = 'json'):
        """
        Save configuration to file
        
        Args:
            filepath: Path to save file
            format: File format ('json' or 'yaml')
        """
        config_dict = self.to_dict()
        
        if format.lower() == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, default=str)
        elif format.lower() == 'yaml':
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def reload(self):
        """Reload all configurations"""
        self._config_cache.clear()
        self._load_configurations()


# Global configuration instance
config = ConfigManager()


def get_config():
    """Get global configuration instance"""
    return config