from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
import secrets
import logging
from typing import Optional, Dict, Any
from .interfaces import IConfigProvider, IAsyncTaskService
from .di_container import container

mail = Mail()
logger = logging.getLogger(__name__)

class EmailVerificationService:
    def __init__(self, app, config_provider: IConfigProvider = None, async_task_service: IAsyncTaskService = None):
        self.app = app
        self.serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        self.config_provider = config_provider or container.get(IConfigProvider)
        self.async_task_service = async_task_service or container.get(IAsyncTaskService)
    
    def generate_verification_token(self, email):
        """Generate verification token for email."""
        return self.serializer.dumps(email, salt='email-verification')
    
    def verify_token(self, token, max_age=86400):
        """Verify email verification token."""
        try:
            email = self.serializer.loads(
                token,
                salt='email-verification',
                max_age=max_age
            )
            return email
        except Exception:
            return None
    
    def _send_email_sync(self, recipient: str, subject: str, html_body: str, text_body: str) -> bool:
        """同步发送邮件（内部方法）"""
        if not self.config_provider.validate_email_config():
            logger.warning("Email configuration incomplete. Skipping email sending.")
            return False
        
        try:
            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=html_body,
                body=text_body
            )
            
            mail.send(msg)
            logger.info(f"邮件发送成功: {recipient}")
            return True
        except Exception as e:
            logger.error(f"邮件发送失败 {recipient}: {e}")
            return False
    
    def send_verification_email(self, user, verification_url, async_mode: bool = True) -> Dict[str, Any]:
        """
        发送验证邮件（支持异步模式）
        
        参数:
            user: 用户对象
            verification_url: 验证URL
            async_mode: 是否异步发送
        
        返回:
            包含发送状态和任务ID的字典
        """
        if not self.config_provider.validate_email_config():
            return {
                'success': False,
                'message': '邮箱配置不完整',
                'task_id': None
            }
        
        subject = f"Verify Your Email - {self.config_provider.app_name}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #4CAF50; 
                          color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {self.config_provider.app_name}!</h1>
                </div>
                <div class="content">
                    <p>Hello {user.username},</p>
                    <p>Thank you for registering with {self.config_provider.app_name}. Please verify your email address by clicking the button below:</p>
                    <p style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background-color: #eee; padding: 10px; border-radius: 5px;">
                        {verification_url}
                    </p>
                    <p>This verification link will expire in 24 hours.</p>
                    <p>If you did not create an account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} {self.config_provider.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to {self.config_provider.app_name}!
        
        Hello {user.username},
        
        Thank you for registering with {self.config_provider.app_name}. Please verify your email address by visiting the following link:
        
        {verification_url}
        
        This verification link will expire in 24 hours.
        
        If you did not create an account, please ignore this email.
        
        © {datetime.now().year} {self.config_provider.app_name}. All rights reserved.
        """
        
        if async_mode:
            # 异步发送
            try:
                task_id = self.async_task_service.submit_task(
                    self._send_email_sync,
                    user.email,
                    subject,
                    html_body,
                    text_body
                )
                
                logger.info(f"异步邮件任务已提交: {task_id}, 收件人: {user.email}")
                return {
                    'success': True,
                    'message': '邮件发送任务已提交',
                    'task_id': task_id,
                    'async': True
                }
            except Exception as e:
                logger.error(f"提交异步邮件任务失败: {e}")
                # 降级为同步发送
                return self._send_email_fallback(user.email, subject, html_body, text_body)
        else:
            # 同步发送
            success = self._send_email_sync(user.email, subject, html_body, text_body)
            return {
                'success': success,
                'message': '邮件发送完成' if success else '邮件发送失败',
                'task_id': None,
                'async': False
            }
    
    def _send_email_fallback(self, recipient: str, subject: str, html_body: str, text_body: str) -> Dict[str, Any]:
        """邮件发送降级方案"""
        logger.warning(f"使用同步发送降级方案: {recipient}")
        success = self._send_email_sync(recipient, subject, html_body, text_body)
        return {
            'success': success,
            'message': '邮件发送完成（同步模式）' if success else '邮件发送失败',
            'task_id': None,
            'async': False
        }
    
    def send_welcome_email(self, user, async_mode: bool = True) -> Dict[str, Any]:
        """发送欢迎邮件（支持异步模式）"""
        if not self.config_provider.validate_email_config():
            return {
                'success': False,
                'message': '邮箱配置不完整',
                'task_id': None
            }
        
        subject = f"Welcome to {self.config_provider.app_name}!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {self.config_provider.app_name}!</h1>
                </div>
                <div class="content">
                    <p>Hello {user.username},</p>
                    <p>Your email has been successfully verified. Welcome to {self.config_provider.app_name}!</p>
                    <p>You can now log in to your account and start using our services.</p>
                    <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} {self.config_provider.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        if async_mode:
            # 异步发送
            try:
                task_id = self.async_task_service.submit_task(
                    self._send_email_sync,
                    user.email,
                    subject,
                    html_body,
                    ""
                )
                
                logger.info(f"异步欢迎邮件任务已提交: {task_id}, 收件人: {user.email}")
                return {
                    'success': True,
                    'message': '欢迎邮件发送任务已提交',
                    'task_id': task_id,
                    'async': True
                }
            except Exception as e:
                logger.error(f"提交异步欢迎邮件任务失败: {e}")
                # 降级为同步发送
                success = self._send_email_sync(user.email, subject, html_body, "")
                return {
                    'success': success,
                    'message': '欢迎邮件发送完成（同步模式）' if success else '欢迎邮件发送失败',
                    'task_id': None,
                    'async': False
                }
        else:
            # 同步发送
            success = self._send_email_sync(user.email, subject, html_body, "")
            return {
                'success': success,
                'message': '欢迎邮件发送完成' if success else '欢迎邮件发送失败',
                'task_id': None,
                'async': False
            }