# 贡献指南

感谢您对项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题
- 使用 [GitHub Issues](https://github.com/your-username/pythoncode/issues) 报告bug或提出功能请求
- 在创建issue前，请先搜索是否已有类似问题
- 按照issue模板提供详细信息

### 提交代码
1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 开发流程
1. **设置开发环境**
   ```bash
   # 克隆仓库
   git clone https://github.com/your-username/pythoncode.git
   cd pythoncode
   
   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   
   # 安装依赖
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 开发依赖
   ```

2. **运行测试**
   ```bash
   # 运行所有测试
   pytest tests/
   
   # 运行特定组件测试
   pytest tests/api/
   pytest tests/command_system/
   
   # 带覆盖率报告
   pytest tests/ --cov=api --cov=command_system --cov-report=html
   ```

3. **代码规范**
   ```bash
   # 代码格式化
   black .
   isort .
   
   # 代码检查
   flake8 .
   mypy .
   ```

### 代码风格
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用 [Black](https://github.com/psf/black) 进行代码格式化
- 使用 [isort](https://github.com/PyCQA/isort) 进行导入排序
- 添加适当的类型提示
- 编写清晰的文档字符串

### 提交信息规范
使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

类型包括：
- `feat`: 新功能
- `fix`: bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### Pull Request流程
1. 确保所有测试通过
2. 更新相关文档
3. 遵循项目代码风格
4. 添加适当的测试
5. 描述清楚变更内容

## 项目结构
```
pythoncode/
├── api/                    # API服务组件
├── command_system/         # 命令执行系统
├── card_generator/         # 业务卡生成器
├── utils/                  # 工具模块
├── tests/                  # 测试套件
├── config/                 # 配置和部署
└── docs/                  # 文档
```

## 测试要求
- 新功能必须包含相应的测试
- 修复bug时添加回归测试
- 保持测试覆盖率在80%以上
- 测试应该独立、快速、可靠

## 文档要求
- 公共API必须有文档字符串
- 复杂逻辑需要注释说明
- 更新README和相关文档

## CI/CD流程
项目使用GitHub Actions进行持续集成：
- 代码推送时自动运行测试
- PR合并前必须通过所有检查
- 主分支自动部署到生产环境

## 沟通渠道
- GitHub Issues: 问题讨论和功能请求
- Pull Requests: 代码审查和合并
- [项目Wiki](https://github.com/your-username/pythoncode/wiki): 详细文档

## 行为准则
请遵守我们的[行为准则](CODE_OF_CONDUCT.md)，保持友好和尊重的交流环境。

## 许可证
通过贡献代码，您同意您的贡献将使用项目的许可证（MIT License）。

## 感谢
感谢所有贡献者的支持！