#!/usr/bin/env python
"""
Configuration Loader Script
Loads and validates configuration for different environments.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(environment: str = None) -> Dict[str, Any]:
    """
    Load configuration for specified environment
    
    Args:
        environment: Environment name (development, staging, production)
                    If None, uses ENVIRONMENT environment variable
    
    Returns:
        Configuration dictionary
    """
    if environment is None:
        environment = os.environ.get('ENVIRONMENT', 'development')
    
    # Base configuration directory
    config_dir = Path(__file__).parent.parent / 'config'
    
    # Load base configuration
    config = {}
    
    # Load base config.yaml
    base_config_file = config_dir / 'config.yaml'
    if base_config_file.exists():
        with open(base_config_file, 'r', encoding='utf-8') as f:
            config.update(yaml.safe_load(f) or {})
    
    # Load environment-specific config
    env_config_file = config_dir / f'config.{environment}.yaml'
    if env_config_file.exists():
        with open(env_config_file, 'r', encoding='utf-8') as f:
            env_config = yaml.safe_load(f) or {}
            _deep_merge(config, env_config)
    
    # Load local overrides (not committed to git)
    local_config_file = config_dir / 'config.local.yaml'
    if local_config_file.exists():
        with open(local_config_file, 'r', encoding='utf-8') as f:
            local_config = yaml.safe_load(f) or {}
            _deep_merge(config, local_config)
    
    # Override with environment variables
    config = _apply_env_overrides(config)
    
    return config


def _deep_merge(target: Dict, source: Dict):
    """Deep merge source into target"""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value


def _apply_env_overrides(config: Dict) -> Dict:
    """Apply environment variable overrides to configuration"""
    
    # Map environment variables to config paths
    env_mappings = {
        'ENVIRONMENT': ('app', 'environment'),
        'DEBUG': ('app', 'debug'),
        'SECRET_KEY': ('app', 'secret_key'),
        'DATABASE_URL': ('database', 'url'),
        'DB_POOL_SIZE': ('database', 'pool_size'),
        'DB_MAX_OVERFLOW': ('database', 'max_overflow'),
        'DB_POOL_RECYCLE': ('database', 'pool_recycle'),
        'DB_ECHO': ('database', 'echo'),
        'MAIL_SERVER': ('email', 'server'),
        'MAIL_PORT': ('email', 'port'),
        'MAIL_USE_TLS': ('email', 'use_tls'),
        'MAIL_USERNAME': ('email', 'username'),
        'MAIL_PASSWORD': ('email', 'password'),
        'MAIL_DEFAULT_SENDER': ('email', 'default_sender'),
        'VERIFICATION_TOKEN_EXPIRY': ('email', 'verification_token_expiry'),
        'CMD_TIMEOUT': ('command_system', 'timeout'),
        'CMD_MAX_WORKERS': ('command_system', 'max_workers'),
        'CMD_WORKING_DIR': ('command_system', 'working_dir'),
        'CMD_MAX_QUEUE_SIZE': ('command_system', 'max_queue_size'),
        'CMD_ENABLE_VALIDATION': ('command_system', 'enable_validation'),
        'CMD_ALLOWED_COMMANDS': ('command_system', 'allowed_commands'),
        'CMD_DENIED_COMMANDS': ('command_system', 'denied_commands'),
        'CMD_LOG_LEVEL': ('command_system', 'log_level'),
        'CMD_LOG_FILE': ('command_system', 'log_file'),
        'CMD_ENABLE_MONITORING': ('command_system', 'enable_monitoring'),
        'CMD_MONITOR_INTERVAL': ('command_system', 'monitor_interval'),
        'LOG_LEVEL': ('logging', 'level'),
        'LOG_FORMAT': ('logging', 'format'),
        'LOG_FILE': ('logging', 'file'),
        'LOG_MAX_SIZE_MB': ('logging', 'max_size_mb'),
        'LOG_BACKUP_COUNT': ('logging', 'backup_count'),
        'API_HOST': ('api', 'host'),
        'API_PORT': ('api', 'port'),
        'API_WORKERS': ('api', 'workers'),
        'CORS_ORIGINS': ('api', 'cors_origins'),
        'RATE_LIMIT': ('api', 'rate_limit'),
        'ENABLE_SWAGGER': ('api', 'enable_swagger'),
        'CACHE_TYPE': ('cache', 'type'),
        'REDIS_URL': ('cache', 'redis_url'),
        'CACHE_DEFAULT_TIMEOUT': ('cache', 'default_timeout'),
    }
    
    for env_var, config_path in env_mappings.items():
        if env_var in os.environ:
            value = os.environ[env_var]
            
            # Convert to appropriate type
            if env_var.endswith('_PORT') or env_var.endswith('_SIZE') or env_var.endswith('_COUNT') or env_var.endswith('_TIMEOUT') or env_var.endswith('_EXPIRY') or env_var.endswith('_INTERVAL') or env_var.endswith('_MB'):
                try:
                    value = int(value)
                except ValueError:
                    pass
            elif env_var.endswith('_DEBUG') or env_var.endswith('_TLS') or env_var.endswith('_VALIDATION') or env_var.endswith('_MONITORING') or env_var.endswith('_ECHO') or env_var.endswith('_SWAGGER'):
                value = value.lower() == 'true'
            elif env_var.endswith('_COMMANDS') or env_var.endswith('_ORIGINS'):
                value = [v.strip() for v in value.split(',') if v.strip()]
            
            # Set value in config
            current = config
            for key in config_path[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[config_path[-1]] = value
    
    return config


def validate_config(config: Dict) -> Dict[str, Any]:
    """
    Validate configuration
    
    Returns:
        Validation results dictionary
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'environment': config.get('app', {}).get('environment', 'unknown')
    }
    
    # Validate app section
    app_config = config.get('app', {})
    if app_config.get('environment') == 'production':
        if app_config.get('debug', False):
            results['warnings'].append('Debug mode should be disabled in production')
        
        secret_key = app_config.get('secret_key', '')
        if secret_key.startswith('dev-'):
            results['errors'].append('SECRET_KEY must be changed in production')
    
    # Validate database
    db_config = config.get('database', {})
    db_url = db_config.get('url', '')
    if not db_url:
        results['errors'].append('Database URL is required')
    elif 'sqlite' in db_url and app_config.get('environment') == 'production':
        results['warnings'].append('SQLite is not recommended for production')
    
    # Validate email configuration (warning only)
    email_config = config.get('email', {})
    required_email = ['username', 'password', 'default_sender']
    missing_email = [field for field in required_email if not email_config.get(field)]
    if missing_email:
        results['warnings'].append(f'Email configuration incomplete. Missing: {", ".join(missing_email)}')
    
    # Validate command system
    cmd_config = config.get('command_system', {})
    if cmd_config.get('timeout', 0) <= 0:
        results['errors'].append('CMD_TIMEOUT must be positive')
    if cmd_config.get('max_workers', 0) <= 0:
        results['errors'].append('CMD_MAX_WORKERS must be positive')
    if cmd_config.get('max_queue_size', 0) <= 0:
        results['errors'].append('CMD_MAX_QUEUE_SIZE must be positive')
    
    # Update valid status
    if results['errors']:
        results['valid'] = False
    
    return results


def print_config_summary(config: Dict, validation: Dict = None):
    """Print configuration summary"""
    if validation is None:
        validation = validate_config(config)
    
    print("\n" + "=" * 60)
    print("CONFIGURATION SUMMARY")
    print("=" * 60)
    
    env = config.get('app', {}).get('environment', 'unknown')
    print(f"\nEnvironment: {env}")
    print(f"Valid: {'✅' if validation['valid'] else '❌'}")
    
    if validation['errors']:
        print("\nErrors:")
        for error in validation['errors']:
            print(f"  ❌ {error}")
    
    if validation['warnings']:
        print("\nWarnings:")
        for warning in validation['warnings']:
            print(f"  ⚠️ {warning}")
    
    # Print key configuration values
    print("\nKey Configuration Values:")
    print("-" * 40)
    
    # App
    app = config.get('app', {})
    print(f"\nApplication:")
    print(f"  Name: {app.get('name', 'N/A')}")
    print(f"  Version: {app.get('version', 'N/A')}")
    print(f"  Debug: {app.get('debug', False)}")
    
    # Database
    db = config.get('database', {})
    print(f"\nDatabase:")
    print(f"  URL: {db.get('url', 'N/A')[:50]}...")
    print(f"  Pool Size: {db.get('pool_size', 'N/A')}")
    
    # Email
    email = config.get('email', {})
    print(f"\nEmail:")
    print(f"  Server: {email.get('server', 'N/A')}")
    print(f"  Port: {email.get('port', 'N/A')}")
    print(f"  Username: {'Set' if email.get('username') else 'Not set'}")
    print(f"  Password: {'Set' if email.get('password') else 'Not set'}")
    
    # Command System
    cmd = config.get('command_system', {})
    print(f"\nCommand System:")
    print(f"  Timeout: {cmd.get('timeout', 'N/A')}s")
    print(f"  Max Workers: {cmd.get('max_workers', 'N/A')}")
    print(f"  Enable Validation: {cmd.get('enable_validation', False)}")
    
    # API
    api = config.get('api', {})
    print(f"\nAPI:")
    print(f"  Host: {api.get('host', 'N/A')}")
    print(f"  Port: {api.get('port', 'N/A')}")
    print(f"  Workers: {api.get('workers', 'N/A')}")
    
    print("\n" + "=" * 60)


def save_config(config: Dict, format: str = 'json', output_file: str = None):
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary
        format: Output format ('json' or 'yaml')
        output_file: Output file path
    """
    if output_file is None:
        env = config.get('app', {}).get('environment', 'unknown')
        output_file = f'config-{env}.{format}'
    
    if format.lower() == 'json':
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, default=str)
    elif format.lower() == 'yaml':
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    print(f"Configuration saved to: {output_file}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load and validate configuration')
    parser.add_argument('--environment', '-e', default=None,
                       help='Environment name (development, staging, production)')
    parser.add_argument('--validate', '-v', action='store_true',
                       help='Validate configuration')
    parser.add_argument('--save', '-s', action='store_true',
                       help='Save configuration to file')
    parser.add_argument('--format', '-f', default='json',
                       choices=['json', 'yaml'],
                       help='Output format for save')
    parser.add_argument('--output', '-o', default=None,
                       help='Output file path')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.environment)
    
    # Validate if requested
    validation = None
    if args.validate:
        validation = validate_config(config)
    
    # Print summary
    print_config_summary(config, validation)
    
    # Save if requested
    if args.save:
        save_config(config, args.format, args.output)
    
    # Exit with appropriate code
    if validation and not validation['valid']:
        print("\n❌ Configuration validation failed")
        return 1
    else:
        print("\n✅ Configuration loaded successfully")
        return 0


if __name__ == "__main__":
    sys.exit(main())