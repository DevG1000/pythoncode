from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from sqlalchemy import text
from .config import Config
from .models import db, User, EmailVerification
from .email_service import mail, EmailVerificationService
from .di_container import container
from .interfaces import IAsyncTaskService, IMemoryMonitor, IConfigProvider, IUserRepository, IEmailVerificationRepository
from datetime import datetime
import re
import logging

# Try to import Swagger documentation
try:
    from .swagger_docs import setup_swagger
    SWAGGER_AVAILABLE = True
except ImportError:
    SWAGGER_AVAILABLE = False
    print("Note: Swagger documentation not available. Install flask-swagger-ui to enable.")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
mail.init_app(app)
CORS(app)

# Initialize services lazily to avoid circular imports
email_service = None
async_task_service = None
memory_monitor = None
config_provider = None
user_repository = None
email_verification_repository = None

def init_services():
    """Initialize services lazily"""
    global email_service, async_task_service, memory_monitor, config_provider
    global user_repository, email_verification_repository
    
    # First register default services
    from .di_container import register_default_services
    register_default_services()
    
    # Get services from container
    from .di_container import container
    from .interfaces import IAsyncTaskService, IMemoryMonitor, IConfigProvider, IUserRepository, IEmailVerificationRepository
    
    config_provider = container.get(IConfigProvider)
    async_task_service = container.get(IAsyncTaskService)
    memory_monitor = container.get(IMemoryMonitor)
    user_repository = container.get(IUserRepository)
    email_verification_repository = container.get(IEmailVerificationRepository)
    
    # Initialize email service with dependencies
    email_service = EmailVerificationService(
        app, 
        config_provider=config_provider,
        async_task_service=async_task_service
    )
    
    # Start memory monitoring
    memory_monitor.start_monitoring(interval_seconds=300)

with app.app_context():
    """Create database tables."""
    db.create_all()
    logger.info("数据库表创建完成")

# 应用关闭时清理资源
@app.teardown_appcontext
def shutdown_systems(exception=None):
    """关闭所有后台系统"""
    async_task_service.shutdown()
    memory_monitor.stop_monitoring()
    logger.info("所有后台系统已关闭")

@app.route('/')
def index():
    """Home endpoint."""
    return jsonify({
        'message': f'Welcome to {Config.APP_NAME} API',
        'version': '1.0.0',
        'endpoints': {
            'register': '/api/register',
            'verify_email': '/api/verify/<token>',
            'resend_verification': '/api/resend-verification'
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        email = data['email'].strip().lower()
        username = data['username'].strip()
        password = data['password']
        
        # Validate email format
        if not User.validate_email(email):
            return jsonify({
                'error': 'Invalid email format'
            }), 400
        
        # Validate username
        is_valid_username, username_error = User.validate_username(username)
        if not is_valid_username:
            return jsonify({
                'error': username_error
            }), 400
        
        # Validate password length
        if len(password) < 8:
            return jsonify({
                'error': 'Password must be at least 8 characters long'
            }), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({
                'error': 'Email already registered'
            }), 409
        
        if User.query.filter_by(username=username).first():
            return jsonify({
                'error': 'Username already taken'
            }), 409
        
        # Create new user
        user = User(email=email, username=username)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate verification token
        token = email_service.generate_verification_token(email)
        
        # Create verification URL
        verification_url = url_for('verify_email', token=token, _external=True)
        
        # 异步发送验证邮件
        email_result = email_service.send_verification_email(user, verification_url, async_mode=True)
        
        # Create email verification record
        verification = EmailVerification.create_for_user(user)
        db.session.add(verification)
        db.session.commit()
        
        response_data = {
            'message': 'Registration successful. Please check your email for verification.',
            'user': user.to_dict(),
            'email': email_result
        }
        
        if not email_result['success']:
            response_data['warning'] = email_result['message']
        
        return jsonify(response_data), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({
            'error': 'An unexpected error occurred during registration'
        }), 500

@app.route('/api/verify/<token>', methods=['GET'])
def verify_email(token):
    """Email verification endpoint."""
    try:
        # Verify token
        email = email_service.verify_token(token)
        if not email:
            return jsonify({
                'error': 'Invalid or expired verification token'
            }), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'error': 'User not found'
            }), 404
        
        # Check if already verified
        if user.is_verified:
            return jsonify({
                'message': 'Email already verified'
            }), 200
        
        # Find verification record
        verification = EmailVerification.query.filter_by(
            user_id=user.id,
            token=token,
            is_used=False
        ).first()
        
        if not verification:
            return jsonify({
                'error': 'Verification token not found'
            }), 400
        
        if verification.is_expired():
            return jsonify({
                'error': 'Verification token has expired'
            }), 400
        
        # Mark user as verified
        user.is_verified = True
        verification.is_used = True
        
        db.session.commit()
        
        # 异步发送欢迎邮件
        welcome_result = email_service.send_welcome_email(user, async_mode=True)
        
        if welcome_result['success']:
            logger.info(f"欢迎邮件发送任务已提交: {welcome_result.get('task_id')}")
        else:
            logger.warning(f"欢迎邮件发送失败: {welcome_result.get('message')}")
        
        return jsonify({
            'message': 'Email verified successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Verification error: {e}")
        return jsonify({
            'error': 'An unexpected error occurred during verification'
        }), 500

@app.route('/api/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email endpoint."""
    try:
        data = request.get_json()
        
        if 'email' not in data:
            return jsonify({
                'error': 'Email is required'
            }), 400
        
        email = data['email'].strip().lower()
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'error': 'User not found'
            }), 404
        
        if user.is_verified:
            return jsonify({
                'message': 'Email already verified'
            }), 200
        
        # Generate new verification token
        token = email_service.generate_verification_token(email)
        
        # Create verification URL
        verification_url = url_for('verify_email', token=token, _external=True)
        
        # Create new verification record
        verification = EmailVerification.create_for_user(user)
        db.session.add(verification)
        db.session.commit()
        
        # 异步发送验证邮件
        email_result = email_service.send_verification_email(user, verification_url, async_mode=True)
        
        response_data = {
            'message': 'Verification email resent',
            'email': email_result
        }
        
        if not email_result['success']:
            response_data['warning'] = email_result['message']
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Resend verification error: {e}")
        return jsonify({
            'error': 'An unexpected error occurred'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        db.session.execute(text('SELECT 1'))
        
        # 获取异步任务统计
        async_stats = async_task_service.get_stats()
        
        # 获取资源信息
        resource_info = memory_monitor.get_resource_info()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'async_tasks': async_stats,
            'resources': resource_info
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }), 500

@app.route('/api/async/task/<task_id>', methods=['GET'])
def get_async_task(task_id):
    """获取异步任务状态"""
    task_status = async_task_service.get_task_status(task_id)
    if task_status:
        return jsonify(task_status), 200
    else:
        return jsonify({'error': 'Task not found'}), 404

@app.route('/api/async/stats', methods=['GET'])
def get_async_task_stats():
    """获取异步任务统计信息"""
    stats = async_task_service.get_stats()
    return jsonify(stats), 200

@app.route('/api/performance', methods=['GET'])
def performance_info():
    """性能信息端点"""
    return jsonify(get_resource_info()), 200

@app.route('/api/memory/optimize', methods=['POST'])
def optimize_memory_endpoint():
    """内存优化端点"""
    try:
        result = optimize_memory()
        return jsonify({
            'message': '内存优化完成',
            'result': result
        }), 200
    except Exception as e:
        logger.error(f"内存优化失败: {e}")
        return jsonify({
            'error': '内存优化失败',
            'details': str(e)
        }), 500

@app.route('/api/memory/info', methods=['GET'])
def memory_info():
    """内存信息端点"""
    from memory_manager import get_memory_info
    return jsonify(get_memory_info()), 200

# Setup Swagger documentation if available
if SWAGGER_AVAILABLE:
    setup_swagger(app)
    logger.info("Swagger documentation enabled at /api/docs")
else:
    logger.info("Swagger documentation not available. Install flask-swagger-ui to enable.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)