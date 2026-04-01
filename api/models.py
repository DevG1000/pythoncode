from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, text
import bcrypt
import re
from typing import Optional, Tuple

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False, index=True)  # 添加索引
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)  # 添加索引
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Email verification token
    verification_token = db.Column(db.String(100), unique=True, nullable=True, index=True)  # 添加索引
    verification_sent_at = db.Column(db.DateTime, nullable=True)
    
    # 复合索引优化常用查询
    __table_args__ = (
        Index('idx_email_verified', 'email', 'is_verified'),  # 常用查询组合
        Index('idx_user_created', 'username', 'created_at'),  # 用户查询排序
    )
    
    def set_password(self, password):
        """Hash and set password."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username):
        """Validate username format."""
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        if len(username) > 30:
            return False, "Username must be at most 30 characters long"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        return True, ""
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)  # 添加索引
    is_used = db.Column(db.Boolean, default=False, nullable=False, index=True)  # 添加索引
    
    user = db.relationship('User', backref=db.backref('verifications', lazy='dynamic'))  # 使用dynamic减少内存
    
    # 复合索引优化查询
    __table_args__ = (
        Index('idx_token_used_expired', 'token', 'is_used', 'expires_at'),  # 验证查询优化
        Index('idx_user_token', 'user_id', 'token'),  # 用户令牌查询
        Index('idx_cleanup', 'expires_at', 'is_used'),  # 清理过期令牌
    )
    
    def is_expired(self):
        """Check if verification token is expired."""
        return datetime.utcnow() > self.expires_at
    
    @classmethod
    def create_for_user(cls, user, expiry_hours=24):
        """Create verification token for user."""
        import secrets
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        
        verification = cls(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        return verification