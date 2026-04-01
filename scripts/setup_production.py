#!/usr/bin/env python3
"""
生产环境设置脚本
用于自动化设置生产环境配置
"""

import os
import sys
import secrets
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionSetup:
    """生产环境设置器"""
    
    def __init__(self, env_file: str = '.env.production'):
        """初始化设置器"""
        self.env_file = env_file
        self.secrets: Dict[str, str] = {}
        
    def generate_secrets(self):
        """生成安全密钥"""
        logger.info("生成安全密钥...")
        
        self.secrets = {
            'SECRET_KEY': secrets.token_urlsafe(64),
            'REDIS_PASSWORD': secrets.token_urlsafe(32),
            'POSTGRES_PASSWORD': secrets.token_urlsafe(32),
            'GRAFANA_PASSWORD': secrets.token_urlsafe(16),
        }
        
        logger.info(f"已生成 {len(self.secrets)} 个安全密钥")
        
    def create_env_file(self, template_file: str = '.env.production.example'):
        """创建环境变量文件"""
        logger.info(f"创建环境变量文件: {self.env_file}")
        
        if not os.path.exists(template_file):
            logger.error(f"模板文件不存在: {template_file}")
            return False
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换占位符
            for key, value in self.secrets.items():
                placeholder = f"${{{key}}}"
                content = content.replace(placeholder, value)
            
            # 写入新文件
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 设置文件权限
            os.chmod(self.env_file, 0o600)
            
            logger.info(f"环境变量文件已创建: {self.env_file}")
            return True
            
        except Exception as e:
            logger.error(f"创建环境变量文件失败: {e}")
            return False
    
    def setup_directories(self):
        """设置目录结构"""
        logger.info("设置目录结构...")
        
        directories = [
            'logs',
            'logs/nginx',
            'uploads',
            'config/nginx/ssl',
            'config/grafana/provisioning',
            'config/logstash/config',
            'config/logstash/pipeline',
            'config/postgres-init'
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.debug(f"创建目录: {directory}")
            except Exception as e:
                logger.error(f"创建目录失败 {directory}: {e}")
        
        logger.info("目录结构设置完成")
    
    def generate_ssl_certificates(self):
        """生成SSL证书（自签名）"""
        logger.info("生成SSL证书...")
        
        ssl_dir = 'config/nginx/ssl'
        cert_file = os.path.join(ssl_dir, 'cert.pem')
        key_file = os.path.join(ssl_dir, 'key.pem')
        
        if os.path.exists(cert_file) and os.path.exists(key_file):
            logger.info("SSL证书已存在，跳过生成")
            return True
        
        try:
            # 生成自签名证书
            subprocess.run([
                'openssl', 'req', '-x509', '-nodes', '-days', '365',
                '-newkey', 'rsa:2048',
                '-keyout', key_file,
                '-out', cert_file,
                '-subj', '/C=US/ST=State/L=City/O=Organization/CN=localhost'
            ], check=True, capture_output=True)
            
            # 设置文件权限
            os.chmod(key_file, 0o600)
            os.chmod(cert_file, 0o644)
            
            logger.info("SSL证书生成完成")
            return True
            
        except Exception as e:
            logger.warning(f"生成SSL证书失败: {e}")
            logger.warning("请手动生成SSL证书或使用Let's Encrypt")
            return False
    
    def create_postgres_init_script(self):
        """创建PostgreSQL初始化脚本"""
        logger.info("创建PostgreSQL初始化脚本...")
        
        init_dir = 'config/postgres-init'
        init_file = os.path.join(init_dir, '01-init.sql')
        
        init_script = """
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 创建审计表
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

-- 创建函数：记录审计日志
CREATE OR REPLACE FUNCTION log_audit_event(
    p_user_id INTEGER,
    p_action VARCHAR(100),
    p_resource_type VARCHAR(50),
    p_resource_id INTEGER,
    p_details JSONB,
    p_ip_address INET,
    p_user_agent TEXT
) RETURNS VOID AS $$
BEGIN
    INSERT INTO audit_logs (
        user_id, action, resource_type, resource_id,
        details, ip_address, user_agent
    ) VALUES (
        p_user_id, p_action, p_resource_type, p_resource_id,
        p_details, p_ip_address, p_user_agent
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建视图：安全事件视图
CREATE OR REPLACE VIEW security_events AS
SELECT 
    id,
    user_id,
    action,
    resource_type,
    resource_id,
    details,
    ip_address,
    user_agent,
    created_at
FROM audit_logs
WHERE action IN ('LOGIN_FAILED', 'UNAUTHORIZED_ACCESS', 'PASSWORD_CHANGE', 'ROLE_CHANGE')
ORDER BY created_at DESC;

-- 注释
COMMENT ON TABLE audit_logs IS '系统审计日志表';
COMMENT ON VIEW security_events IS '安全事件视图';
COMMENT ON FUNCTION log_audit_event IS '记录审计日志的函数';
"""
        
        try:
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(init_script)
            
            logger.info(f"PostgreSQL初始化脚本已创建: {init_file}")
            return True
            
        except Exception as e:
            logger.error(f"创建PostgreSQL初始化脚本失败: {e}")
            return False
    
    def create_grafana_provisioning(self):
        """创建Grafana配置"""
        logger.info("创建Grafana配置...")
        
        provisioning_dir = 'config/grafana/provisioning'
        
        # 数据源配置
        datasources_file = os.path.join(provisioning_dir, 'datasources', 'datasources.yaml')
        Path(os.path.dirname(datasources_file)).mkdir(parents=True, exist_ok=True)
        
        datasources_config = """
apiVersion: 1

datasources:
  - name: PostgreSQL
    type: postgres
    access: proxy
    url: postgres:5432
    database: ${POSTGRES_DB}
    user: ${POSTGRES_USER}
    secureJsonData:
      password: ${POSTGRES_PASSWORD}
    jsonData:
      sslmode: disable
      postgresVersion: 1500
      timescaledb: false

  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
"""
        
        # 仪表板配置
        dashboards_file = os.path.join(provisioning_dir, 'dashboards', 'dashboards.yaml')
        Path(os.path.dirname(dashboards_file)).mkdir(parents=True, exist_ok=True)
        
        dashboards_config = """
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
"""
        
        try:
            with open(datasources_file, 'w', encoding='utf-8') as f:
                f.write(datasources_config)
            
            with open(dashboards_file, 'w', encoding='utf-8') as f:
                f.write(dashboards_config)
            
            logger.info("Grafana配置已创建")
            return True
            
        except Exception as e:
            logger.error(f"创建Grafana配置失败: {e}")
            return False
    
    def run_security_audit(self):
        """运行安全审计"""
        logger.info("运行安全审计...")
        
        try:
            result = subprocess.run(
                ['python', 'scripts/security_audit_simple.py', '--format', 'text'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("安全审计通过")
                return True
            else:
                logger.warning("安全审计发现问题:")
                print(result.stdout)
                return False
                
        except Exception as e:
            logger.error(f"运行安全审计失败: {e}")
            return False
    
    def display_summary(self):
        """显示设置摘要"""
        logger.info("\n" + "="*60)
        logger.info("生产环境设置完成")
        logger.info("="*60)
        
        print("\n设置摘要:")
        print(f"1. 环境变量文件: {self.env_file}")
        print("2. 生成的密钥:")
        for key in ['SECRET_KEY', 'REDIS_PASSWORD', 'POSTGRES_PASSWORD']:
            if key in self.secrets:
                print(f"   - {key}: 已生成")
        
        print("\n3. 创建的目录:")
        directories = [
            'logs/', 'logs/nginx/', 'uploads/',
            'config/nginx/ssl/', 'config/grafana/provisioning/'
        ]
        for directory in directories:
            if os.path.exists(directory):
                print(f"   - {directory}")
        
        print("\n4. 生成的配置文件:")
        configs = [
            'config/nginx/nginx.conf',
            'config/docker-compose.production.yml',
            'config/Dockerfile.production',
            'config/postgres-init/01-init.sql'
        ]
        for config in configs:
            if os.path.exists(config):
                print(f"   - {config}")
        
        print("\n5. 后续步骤:")
        print("   a. 检查并修改 .env.production 文件中的配置")
        print("   b. 获取有效的SSL证书（替换 config/nginx/ssl/ 中的文件）")
        print("   c. 运行: docker-compose -f config/docker-compose.production.yml up -d")
        print("   d. 访问 https://localhost 验证部署")
        print("   e. 访问 http://localhost:3000 配置监控（用户名: admin, 密码见.env文件）")
        
        print("\n6. 安全注意事项:")
        print("   - 确保 .env.production 文件权限为 600")
        print("   - 定期更新生成的密钥")
        print("   - 启用防火墙规则")
        print("   - 配置定期备份")
        print("   - 监控安全日志")
        
        logger.info("\n设置完成!")
    
    def run_all(self):
        """运行所有设置步骤"""
        logger.info("开始生产环境设置...")
        
        steps = [
            ("生成安全密钥", self.generate_secrets),
            ("创建环境变量文件", lambda: self.create_env_file()),
            ("设置目录结构", self.setup_directories),
            ("生成SSL证书", self.generate_ssl_certificates),
            ("创建PostgreSQL初始化脚本", self.create_postgres_init_script),
            ("创建Grafana配置", self.create_grafana_provisioning),
            ("运行安全审计", self.run_security_audit)
        ]
        
        success = True
        for step_name, step_func in steps:
            logger.info(f"\n步骤: {step_name}")
            try:
                if not step_func():
                    logger.warning(f"步骤失败: {step_name}")
                    success = False
            except Exception as e:
                logger.error(f"步骤执行异常 {step_name}: {e}")
                success = False
        
        if success:
            self.display_summary()
            return True
        else:
            logger.error("生产环境设置失败，请检查错误信息")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='生产环境设置脚本')
    parser.add_argument('--env-file', default='.env.production',
                       help='环境变量文件路径')
    parser.add_argument('--skip-audit', action='store_true',
                       help='跳过安全审计')
    
    args = parser.parse_args()
    
    # 创建设置器
    setup = ProductionSetup(args.env_file)
    
    # 运行设置
    if setup.run_all():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()