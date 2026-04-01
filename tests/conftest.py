"""
测试配置共享文件
为所有测试提供共享的配置和fixture
"""
import os
import sys
import pytest

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


@pytest.fixture
def test_data_dir():
    """返回测试数据目录路径"""
    return os.path.join(os.path.dirname(__file__), "..", "data")


@pytest.fixture
def test_instance_dir():
    """返回测试实例目录路径"""
    return os.path.join(os.path.dirname(__file__), "..", "instance")


@pytest.fixture
def test_logs_dir():
    """返回测试日志目录路径"""
    return os.path.join(os.path.dirname(__file__), "..", "logs")


@pytest.fixture
def api_base_url():
    """返回API基础URL"""
    return "http://localhost:5000"


@pytest.fixture(autouse=True)
def setup_test_environment():
    """为每个测试设置环境"""
    # 保存原始环境变量
    original_env = os.environ.copy()
    
    # 设置测试环境变量
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///test_users.db'
    
    yield
    
    # 恢复原始环境变量
    os.environ.clear()
    os.environ.update(original_env)