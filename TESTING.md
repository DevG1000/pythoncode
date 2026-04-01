# 项目测试大纲

## 概述

本文档定义了 PythonCode 项目的测试策略、测试类型、测试范围和测试执行流程。项目采用组件化架构，包含 API 服务、命令执行系统、业务卡生成器和工具模块。

## 测试策略

### 测试金字塔
```
        E2E 测试 (5%)
        ┌─────────────┐
        │ 集成测试 (15%) │
        └─────────────┘
        ┌─────────────┐
        │ 单元测试 (80%) │
        └─────────────┘
```

### 测试类型
1. **单元测试**：测试单个函数、类或模块
2. **集成测试**：测试组件间的交互
3. **端到端测试**：测试完整业务流程
4. **性能测试**：测试系统性能和资源使用

## 测试目录结构

```
tests/
├── conftest.py              # 共享测试配置
├── api/                     # API 组件测试
│   ├── __init__.py
│   ├── test_app.py         # Flask API 端点测试
│   └── test_models.py      # 数据库模型测试（待添加）
├── command_system/         # 命令执行系统测试
│   ├── __init__.py
│   ├── test_cmd_agent.py   # CMD 代理测试
│   ├── test_command_executor.py  # 命令执行器测试（待添加）
│   ├── test_cmd_tasks.py   # 命令任务测试（待添加）
│   └── test_async_tasks.py # 异步任务系统测试（待添加）
├── card_generator/         # 业务卡生成器测试
│   ├── __init__.py
│   └── test_line2card.py   # 业务卡生成器测试
└── utils/                  # 工具模块测试
    ├── __init__.py
    └── test_string_utils.py # 字符串工具测试
```

## 测试范围

### 1. API 组件测试
#### 1.1 健康检查端点
- [x] GET /api/health - 服务健康状态
- [ ] GET /api/stats - 系统统计信息（待添加）

#### 1.2 用户管理端点
- [x] POST /api/register - 用户注册
- [x] 无效注册数据验证
- [x] 重复注册验证
- [x] POST /api/resend-verification - 重新发送验证邮件
- [ ] POST /api/verify-email - 邮箱验证（待添加）
- [ ] POST /api/login - 用户登录（待添加）
- [ ] GET /api/profile - 用户资料（待添加）

#### 1.3 数据库模型测试
- [ ] User 模型测试（待添加）
- [ ] EmailVerification 模型测试（待添加）
- [ ] 密码加密验证（待添加）
- [ ] 数据关系测试（待添加）

### 2. 命令执行系统测试
#### 2.1 CommandExecutor 测试
- [x] 成功命令执行
- [x] 失败命令执行
- [x] 命令超时处理
- [x] 工作目录设置
- [ ] 环境变量设置（待添加）
- [ ] 命令输出编码处理（待添加）

#### 2.2 CommandTask 测试
- [x] 命令任务创建
- [x] 命令任务执行
- [x] 命令任务序列化
- [ ] 任务状态转换（待添加）
- [ ] 任务取消机制（待添加）

#### 2.3 AsyncTaskManager 测试
- [x] 提交命令任务
- [x] 多命令任务执行
- [x] 任务统计收集
- [ ] 任务队列管理（待添加）
- [ ] 工作线程管理（待添加）
- [ ] 系统关闭清理（待添加）

#### 2.4 CmdAgent 测试
- [x] Agent 初始化
- [x] 单命令执行
- [x] 命令历史记录
- [x] 端到端执行
- [x] 并发执行
- [x] 错误处理
- [ ] 交互模式测试（待添加）
- [ ] 批量命令执行（待添加）

#### 2.5 配置集成测试
- [x] 配置加载测试

### 3. 业务卡生成器测试
#### 3.1 Line2Card 功能测试
- [x] 性能优化测试
- [x] API 优化测试
- [x] 并发注册测试
- [x] 内存优化测试
- [ ] Excel 数据读取（待添加）
- [ ] 图像生成验证（待添加）
- [ ] 字体支持测试（待添加）
- [ ] 错误数据处理（待添加）

### 4. 工具模块测试
#### 4.1 字符串工具测试
- [x] 单词反转功能
  - [x] 单个单词
  - [x] 两个单词
  - [x] 多个单词
  - [x] 带标点符号
  - [x] 大小写保持
- [x] 边界条件测试
  - [x] 空字符串
  - [x] 单个字符
  - [x] 只有空格
  - [x] 前后空格
  - [x] 多个连续空格
- [x] Unicode 和特殊字符测试
  - [x] 中文文本
  - [x] Emoji 表情
  - [x] 混合语言
  - [x] 特殊符号
- [x] 性能测试
  - [x] 长字符串处理
  - [x] 重复单词处理
- [x] 错误处理测试
  - [x] None 输入
  - [x] 整数输入
  - [x] 列表输入
  - [x] 字典输入
- [x] 参数化测试
  - [x] 多种输入组合

#### 4.2 Redis 管理器测试（待实现）
- [ ] Redis 连接测试
- [ ] 数据存储/读取测试
- [ ] 过期时间测试
- [ ] 连接池测试

#### 4.3 其他工具测试（待添加）
- [ ] 日期时间工具
- [ ] 文件处理工具
- [ ] 加密工具

## 测试数据管理

### 测试数据库
- 使用 SQLite 内存数据库进行测试
- 每个测试用例独立数据库会话
- 测试后自动清理数据

### 测试文件
- 测试数据文件位于 `tests/data/` 目录
- 测试图像文件位于 `tests/images/` 目录
- 测试 Excel 文件位于 `tests/excel/` 目录

### 环境变量
```python
# tests/conftest.py 中设置
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///test_users.db'
os.environ['TESTING'] = 'true'
```

## 测试执行流程

### 1. 本地开发测试
```bash
# 运行所有测试
pytest tests/

# 运行特定组件测试
pytest tests/api/
pytest tests/command_system/
pytest tests/card_generator/
pytest tests/utils/

# 运行单个测试文件
pytest tests/api/test_app.py

# 运行特定测试用例
pytest tests/api/test_app.py::test_health_check

# 带详细输出
pytest tests/ -v

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

### 2. 持续集成测试
```yaml
# GitHub Actions 配置示例
name: Python Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### 3. Docker 测试
```bash
# 构建测试镜像
docker build -t pythoncode-test -f config/Dockerfile .

# 运行容器测试
docker run --rm pythoncode-test pytest tests/

# 使用 docker-compose 测试
docker-compose -f config/docker-compose.yml run api pytest tests/
```

## 测试质量标准

### 1. 覆盖率目标
- 单元测试覆盖率：≥ 80%
- 集成测试覆盖率：≥ 70%
- 整体测试覆盖率：≥ 75%

### 2. 测试通过标准
- 所有测试用例必须通过
- 无严重或阻塞性缺陷
- 代码审查通过
- 性能指标达标

### 3. 测试文档要求
- 每个测试文件有清晰的文档字符串
- 测试用例名称描述测试意图
- 复杂的测试逻辑有注释说明
- 测试数据来源清晰

## 测试工具和框架

### 主要工具
- **pytest**: 主要测试框架
- **pytest-cov**: 测试覆盖率
- **requests**: HTTP 客户端测试
- **unittest.mock**: 模拟和打桩

### 辅助工具
- **curl**: API 端点手动测试
- **Postman/Insomnia**: API 测试工具
- **Docker**: 容器化测试环境
- **GitHub Actions**: 持续集成

## 测试最佳实践

### 1. 测试命名规范
```python
# 测试函数命名
def test_<function_name>_<scenario>():
    """测试 <功能> 的 <场景>"""
    
# 测试类命名
class Test<ComponentName>:
    """测试 <组件名>"""
    
# 测试文件命名
test_<module_name>.py
```

### 2. 测试结构
```python
def test_example():
    # Arrange - 准备测试数据
    input_data = "test input"
    expected_output = "expected result"
    
    # Act - 执行测试操作
    actual_output = function_under_test(input_data)
    
    # Assert - 验证结果
    assert actual_output == expected_output
```

### 3. 测试隔离
- 每个测试用例独立运行
- 测试数据不互相影响
- 测试后清理资源
- 使用 pytest fixture 管理测试资源

### 4. 错误处理测试
- 测试正常流程
- 测试边界条件
- 测试异常情况
- 测试错误恢复

## 待完成的测试任务

### 高优先级
1. [ ] 添加数据库模型测试
2. [ ] 完善命令执行系统单元测试
3. [ ] 添加业务卡生成器单元测试
4. [ ] 实现 Redis 管理器测试

### 中优先级
1. [ ] 添加 API 端点认证测试
2. [ ] 添加性能基准测试
3. [ ] 添加安全测试
4. [ ] 添加负载测试

### 低优先级
1. [ ] 添加可视化测试报告
2. [ ] 添加测试数据生成工具
3. [ ] 添加测试监控仪表板
4. [ ] 添加自动化测试脚本

## 附录

### A. 测试命令速查表
```bash
# 基本测试
pytest tests/                    # 运行所有测试
pytest -v                       # 详细输出
pytest -x                       # 遇到失败立即停止
pytest --lf                     # 只运行上次失败的测试

# 覆盖率测试
pytest --cov=.                  # 测量覆盖率
pytest --cov=. --cov-report=html # 生成 HTML 报告
pytest --cov=. --cov-report=xml  # 生成 XML 报告

# 特定测试
pytest -k "health"              # 运行名称包含 "health" 的测试
pytest -m "slow"                # 运行标记为 "slow" 的测试
pytest --tb=short               # 简化的错误回溯
```

### B. 测试标记
```python
@pytest.mark.slow               # 慢速测试
@pytest.mark.integration        # 集成测试
@pytest.mark.e2e                # 端到端测试
@pytest.mark.performance        # 性能测试
@pytest.mark.security           # 安全测试
@pytest.mark.skip(reason="...") # 跳过测试
@pytest.mark.xfail              # 预期失败的测试
```

### C. 测试环境变量
```bash
# .env.test 文件示例
FLASK_ENV=testing
DATABASE_URL=sqlite:///test_users.db
SECRET_KEY=test-secret-key
MAIL_SERVER=smtp.test.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=test@example.com
MAIL_PASSWORD=testpassword
TESTING=true
```

---

*最后更新: 2026-03-13*
*版本: 1.0.0*