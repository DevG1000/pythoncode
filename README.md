# PythonCode - Multi-Service Python Application

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Quality](https://img.shields.io/badge/code%20quality-78%2F100-B%2B-green)](CODE_QUALITY_REPORT.md)
[![Documentation](https://img.shields.io/badge/documentation-82%2F100-B%2B-green)](DOCUMENTATION_QUALITY_REPORT.md)
[![Architecture](https://img.shields.io/badge/architecture-76%2F100-B-green)](ARCHITECTURE_QUALITY_REPORT.md)

A comprehensive multi-service Python application featuring API services, command execution systems, and business card generation capabilities.

## 🚀 Features

### API Service
- **User Registration API** with email verification
- **JWT-based Authentication** for secure access
- **Email Service Integration** using SMTP
- **RESTful endpoints** with proper HTTP status codes
- **Input validation** and error handling

### Command System
- **Windows Command Execution** with real-time output
- **Async Task Management** for long-running operations
- **Command History** and result tracking
- **Process Management** with timeout controls
- **Secure command execution** with input sanitization

### Business Card Generator
- **Excel to Image Conversion** for business cards
- **Template-based Design** system
- **Batch Processing** capabilities
- **Image Optimization** and formatting
- **Customizable layouts** and styling

## 📁 Project Structure

```
pythoncode/
├── api/                    # Flask-based API service
│   ├── app.py             # Main Flask application
│   ├── routes/            # API route definitions
│   ├── models/            # Data models and schemas
│   ├── services/          # Business logic services
│   └── utils/             # Utility functions
├── command_system/        # Command execution system
│   ├── cmd_agent.py       # Main command agent
│   ├── async_tasks.py     # Async task management
│   └── utils/             # Command utilities
├── card_generator/        # Business card generator
│   ├── Line2Card.py       # Main card generator
│   ├── templates/         # Card templates
│   └── utils/             # Image processing utilities
├── tests/                 # Test suite
│   ├── api/               # API tests
│   ├── command_system/    # Command system tests
│   └── card_generator/    # Card generator tests
├── docs/                  # Documentation
│   ├── api/               # API documentation
│   ├── architecture/      # Architecture diagrams
│   └── deployment/        # Deployment guides
├── scripts/               # Utility scripts
├── .github/               # GitHub workflows and configs
└── docker/                # Docker configuration
```

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pythoncode.git
   cd pythoncode
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python scripts/init_db.py
   ```

## 🚀 Quick Start

### Running the API Service
```bash
cd api
python app.py
```
The API will be available at `http://localhost:5000`

### Using the Command System
```bash
cd command_system
python -m cmd_agent --help
```

### Generating Business Cards
```bash
cd card_generator
python Line2Card.py --input data/cards.xlsx --output cards/
```

## 📚 Documentation

- [API Documentation](docs/api/README.md) - Complete API reference
- [Architecture Overview](docs/architecture/README.md) - System design and components
- [Deployment Guide](docs/deployment/README.md) - Production deployment instructions
- [Development Guide](docs/development/README.md) - Contribution guidelines

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/api/
pytest tests/command_system/
pytest tests/card_generator/

# Run with coverage report
pytest --cov=api --cov=command_system --cov=card_generator
```

## 🐳 Docker Deployment

### Build and run with Docker Compose
```bash
docker-compose up --build
```

### Individual services
```bash
# API Service
docker build -t pythoncode-api -f docker/api.Dockerfile .

# Command System
docker build -t pythoncode-cmd -f docker/cmd.Dockerfile .

# Card Generator
docker build -t pythoncode-card -f docker/card.Dockerfile .
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///app.db` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `SMTP_SERVER` | SMTP server for emails | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `EMAIL_USER` | Email username | - |
| `EMAIL_PASSWORD` | Email password | - |
| `LOG_LEVEL` | Logging level | `INFO` |

### Configuration Files
- `config/settings.py` - Application settings
- `config/logging.conf` - Logging configuration
- `.pre-commit-config.yaml` - Pre-commit hooks
- `pyproject.toml` - Project metadata and tooling

## 👥 Team Structure

This project follows a structured team organization:

- **Project Manager**: Oversees project planning and delivery
- **Solution Architect**: Designs system architecture and technical standards
- **Business Analyst**: Manages requirements and user stories
- **Backend Developers**: Implement API and business logic
- **Frontend Developer**: Creates user interfaces (if applicable)
- **QA Engineer**: Ensures quality through testing
- **DevOps Engineer**: Manages deployment and infrastructure

See [TEAM_STRUCTURE.md](TEAM_STRUCTURE.md) for detailed role descriptions and workflows.

## 📊 Quality Metrics

| Metric | Score | Grade | Status |
|--------|-------|-------|--------|
| Code Quality | 78/100 | B+ | ✅ Good |
| Documentation | 82/100 | B+ | ✅ Good |
| Architecture | 76/100 | B | ⚠️ Needs Improvement |
| Test Coverage | 85% | A | ✅ Excellent |

Detailed reports:
- [Code Quality Report](CODE_QUALITY_REPORT.md)
- [Documentation Quality Report](DOCUMENTATION_QUALITY_REPORT.md)
- [Architecture Quality Report](ARCHITECTURE_QUALITY_REPORT.md)

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

- **Automated Testing**: Runs on every push and pull request
- **Code Quality Checks**: Pylint, flake8, and black formatting
- **Security Scanning**: Dependency vulnerability checks
- **Docker Builds**: Automated container builds
- **Deployment**: Staging and production deployments

See [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml) for pipeline configuration.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](.github/CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Write comprehensive tests for new features
- Update documentation for API changes
- Use type hints for better code clarity

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/pythoncode/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pythoncode/discussions)
- **Email**: support@pythoncode.example.com

## 🙏 Acknowledgments

- Flask team for the excellent web framework
- Python community for amazing libraries and tools
- Contributors who help improve this project

---

**Made with ❤️ by the PythonCode Team**