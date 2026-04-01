# 用户注册API接口

为BusinessCardGenerator项目添加的用户注册接口，包含邮箱验证和密码加密功能。

## 功能特性

- ✅ 用户注册（邮箱、用户名、密码）
- ✅ 密码加密存储（使用bcrypt）
- ✅ 邮箱验证（发送验证邮件）
- ✅ 验证链接有效期（24小时）
- ✅ 重复注册检查
- ✅ 输入验证（邮箱格式、密码强度、用户名规则）
- ✅ 重新发送验证邮件
- ✅ 健康检查端点

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
复制 `.env.example` 为 `.env` 并修改配置：
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置以下配置：
```env
# Flask配置
SECRET_KEY=your-secret-key-here-change-in-production

# 邮箱配置（用于发送验证邮件）
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # 使用应用专用密码
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### 3. 启动服务器
```bash
python app.py
```

服务器将在 `http://localhost:5000` 启动。

### 4. 运行测试
```bash
python test_api.py
```

## API端点

### 主页
```
GET /
```
返回API基本信息。

### 健康检查
```
GET /api/health
```
检查服务状态和数据库连接。

### 用户注册
```
POST /api/register
```
注册新用户。

**请求体：**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePass123!"
}
```

**响应：**
- 201: 注册成功，验证邮件已发送
- 400: 输入验证失败
- 409: 邮箱或用户名已存在
- 500: 服务器错误

### 邮箱验证
```
GET /api/verify/<token>
```
验证邮箱地址。

**参数：**
- `token`: 验证令牌（从注册邮件中获取）

**响应：**
- 200: 验证成功
- 400: 令牌无效或过期
- 404: 用户不存在

### 重新发送验证邮件
```
POST /api/resend-verification
```
重新发送验证邮件。

**请求体：**
```json
{
  "email": "user@example.com"
}
```

**响应：**
- 200: 邮件已重新发送
- 400: 邮箱格式错误
- 404: 用户不存在

## 数据验证规则

### 邮箱
- 必须符合标准邮箱格式
- 自动转换为小写
- 必须唯一

### 用户名
- 3-30个字符
- 只能包含字母、数字、下划线
- 必须唯一

### 密码
- 至少8个字符
- 使用bcrypt加密存储

## 数据库模型

### User（用户表）
- `id`: 主键
- `email`: 邮箱（唯一）
- `username`: 用户名（唯一）
- `password_hash`: 加密后的密码
- `is_verified`: 是否已验证邮箱
- `created_at`: 创建时间
- `updated_at`: 更新时间

### EmailVerification（邮箱验证表）
- `id`: 主键
- `user_id`: 用户ID
- `token`: 验证令牌（唯一）
- `created_at`: 创建时间
- `expires_at`: 过期时间
- `is_used`: 是否已使用

## 安全特性

### 密码安全
- 使用bcrypt进行密码哈希
- 自动生成盐值
- 防止彩虹表攻击

### 令牌安全
- 使用itsdangerous生成安全令牌
- 令牌有时效性（默认24小时）
- 一次性使用

### 输入安全
- SQL注入防护（使用SQLAlchemy）
- 邮箱格式验证
- 密码强度检查

## 邮箱配置

### Gmail配置示例
1. 启用Gmail账户的"两步验证"
2. 生成"应用专用密码"
3. 在 `.env` 文件中配置：
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

### 其他邮箱服务商
根据服务商调整以下配置：
- `MAIL_SERVER`: SMTP服务器地址
- `MAIL_PORT`: 端口号（通常587或465）
- `MAIL_USE_TLS`: 是否使用TLS

## 故障排除

### 常见问题

1. **邮箱发送失败**
   - 检查邮箱配置是否正确
   - 确认应用专用密码有效
   - 检查防火墙设置

2. **数据库连接失败**
   - 检查SQLite文件权限
   - 确认数据库路径可写

3. **验证链接无效**
   - 确认链接在24小时内使用
   - 检查令牌是否正确复制

### 调试模式
启动时设置环境变量：
```bash
set FLASK_ENV=development
python app.py
```

## 扩展功能建议

### 未来可添加的功能
1. 用户登录/登出
2. 密码重置
3. 用户资料管理
4. API密钥管理
5. 角色和权限管理

### 生产环境部署建议
1. 使用PostgreSQL或MySQL替代SQLite
2. 配置HTTPS
3. 设置CORS策略
4. 添加API速率限制
5. 实现日志记录和监控

## 项目结构
```
project/
├── app.py              # 主应用
├── config.py           # 配置
├── models.py           # 数据模型
├── email_service.py    # 邮箱服务
├── test_api.py         # API测试
├── requirements.txt    # 依赖包
├── .env.example        # 环境变量示例
└── README_API.md       # 本文档
```