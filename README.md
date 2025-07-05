# RAT Control Panel v2.0

<div align="center">
  <img src="docs/images/logo.png" alt="RAT Control Panel Logo" width="200"/>

  [![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/your-repo/rat-control-panel)
  [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
  [![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
  [![React](https://img.shields.io/badge/react-18.2+-blue.svg)](https://reactjs.org)
  [![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://docker.com)
</div>

## 🚀 Overview

RAT Control Panel v2.0 is a modern, secure Remote Administration Tool designed for authorized system administration and educational purposes. Built with enterprise-grade security features and a user-friendly interface.

### ⚠️ **IMPORTANT DISCLAIMER**

This software is intended **ONLY** for:
- Authorized system administration
- Educational and research purposes
- Penetration testing with explicit permission
- Security research in controlled environments

**Users are solely responsible for ensuring compliance with all applicable laws and regulations.**

## ✨ Features

### 🔒 **Enterprise Security**
- **JWT Authentication** - Secure token-based authentication
- **AES-256-GCM Encryption** - End-to-end encryption for all communications
- **RSA Key Exchange** - Secure session establishment
- **Rate Limiting** - DDoS protection and abuse prevention
- **Input Validation** - Comprehensive data sanitization
- **Audit Logging** - Complete activity tracking

### 🏗️ **Modern Architecture**
- **Microservices Design** - Scalable and maintainable architecture
- **React Frontend** - Modern, responsive web interface
- **FastAPI Backend** - High-performance async API server
- **WebSocket Communication** - Real-time bidirectional communication
- **Docker Support** - Containerized deployment
- **Plugin System** - Extensible module architecture

### 📊 **Advanced Features**
- **Real-time Dashboard** - Live monitoring and control
- **Multi-tenancy** - Support for multiple organizations
- **File Management** - Secure file transfer and management
- **Remote Shell** - Secure command execution
- **System Monitoring** - Comprehensive system information
- **Screenshot Capture** - Remote desktop monitoring
- **Keylogger** - Keystroke monitoring (authorized use only)
- **Webcam/Audio** - Remote media capture
- **Process Management** - Remote process control

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Web     │    │   FastAPI       │    │   Client        │
│   Frontend      │◄──►│   Server        │◄──►│   Application   │
│   (Port 3000)   │    │   (Port 8000)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────►│   PostgreSQL    │◄─────────────┘
                        │   Database      │
                        │   (Port 5432)   │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │     Redis       │
                        │     Cache       │
                        │   (Port 6379)   │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (Recommended)
- **Python 3.9+** (For manual installation)
- **Node.js 18+** (For frontend development)
- **PostgreSQL 13+** (For database)
- **Redis 6+** (For caching)

### 🐳 Docker Installation (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/rat-control-panel-v2.git
   cd rat-control-panel-v2
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Web Interface: http://localhost:3000
   - API Documentation: http://localhost:8000/api/docs
   - Grafana Dashboard: http://localhost:3001

### 🔧 Manual Installation

#### Server Setup

1. **Install server dependencies**
   ```bash
   cd server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure database**
   ```bash
   # Create PostgreSQL database
   createdb rat_control_panel

   # Run migrations
   alembic upgrade head
   ```

3. **Start server**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### Frontend Setup

1. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

#### Client Setup

1. **Install client dependencies**
   ```bash
   cd client
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure client**
   ```bash
   cp config/client.json.example config/client.json
   # Edit configuration as needed
   ```

3. **Start client**
   ```bash
   python main.py
   ```

## 📖 Documentation

### 📚 **User Guides**
- [Installation Guide](docs/user-guide/installation/README.md)
- [Configuration Guide](docs/user-guide/configuration/README.md)
- [User Manual](docs/user-guide/usage/README.md)
- [Troubleshooting](docs/user-guide/troubleshooting/README.md)

### 🔧 **Technical Documentation**
- [API Documentation](docs/api/README.md)
- [Architecture Overview](docs/developer/architecture/README.md)
- [Security Guide](docs/security/README.md)
- [Plugin Development](docs/developer/plugins/README.md)

### 🚀 **Deployment Guides**
- [Docker Deployment](docs/deployment/docker/README.md)
- [Kubernetes Deployment](docs/deployment/kubernetes/README.md)
- [AWS Deployment](docs/deployment/aws/README.md)
- [Azure Deployment](docs/deployment/azure/README.md)

## 🔒 Security

### Security Features
- **End-to-end encryption** using AES-256-GCM
- **RSA key exchange** for secure session establishment
- **JWT authentication** with configurable expiration
- **Rate limiting** to prevent abuse
- **Input validation** and sanitization
- **Secure headers** and CORS configuration
- **Audit logging** for all activities

### Security Best Practices
- Change default passwords immediately
- Use strong encryption keys
- Enable HTTPS in production
- Regularly update dependencies
- Monitor audit logs
- Implement network segmentation
- Use firewall rules

### Compliance
- Follows OWASP security guidelines
- Implements zero-trust architecture
- Supports compliance auditing
- Regular security assessments

## 🛠️ Development

### Development Setup

1. **Clone repository**
   ```bash
   git clone https://github.com/your-repo/rat-control-panel-v2.git
   cd rat-control-panel-v2
   ```

2. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Setup pre-commit hooks**
   ```bash
   pre-commit install
   ```

4. **Run tests**
   ```bash
   make test
   ```

### Available Commands

```bash
make install    # Install all dependencies
make build      # Build all containers
make start      # Start all services
make stop       # Stop all services
make test       # Run all tests
make lint       # Run linting
make format     # Format code
make clean      # Clean up containers and volumes
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📊 Monitoring

### Built-in Monitoring
- **Prometheus** metrics collection
- **Grafana** dashboards
- **Health checks** for all services
- **Performance monitoring**
- **Error tracking**
- **Audit logging**

### Metrics Collected
- Client connection status
- Command execution statistics
- System resource usage
- API response times
- Error rates
- Security events

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `JWT_SECRET` | JWT signing secret | Required |
| `ENCRYPTION_KEY` | AES encryption key | Required |
| `SERVER_HOST` | Server bind address | 0.0.0.0 |
| `SERVER_PORT` | Server port | 8000 |
| `DEBUG` | Enable debug mode | false |
| `LOG_LEVEL` | Logging level | INFO |

### Configuration Files
- `server/config/` - Server configuration
- `client/config/` - Client configuration
- `frontend/.env` - Frontend environment
- `docker-compose.yml` - Docker services

## 🚨 Troubleshooting

### Common Issues

**Connection Issues**
- Check firewall settings
- Verify network connectivity
- Ensure correct ports are open

**Authentication Errors**
- Verify JWT secret configuration
- Check token expiration
- Ensure correct credentials

**Performance Issues**
- Monitor system resources
- Check database performance
- Review log files

### Getting Help
- Check the [troubleshooting guide](docs/user-guide/troubleshooting/README.md)
- Review [FAQ](docs/FAQ.md)
- Open an issue on GitHub
- Contact support team

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Notice

This software is provided for educational and authorized administrative purposes only. Users must:

- Obtain explicit permission before using on any system
- Comply with all applicable laws and regulations
- Use only for legitimate security testing or administration
- Respect privacy and data protection laws
- Not use for malicious purposes

The developers are not responsible for any misuse of this software.

## 🤝 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [React](https://reactjs.org/)
- UI components from [Material-UI](https://mui.com/)
- Database with [PostgreSQL](https://postgresql.org/)
- Caching with [Redis](https://redis.io/)
- Containerization with [Docker](https://docker.com/)

## 📞 Support

For support and questions:
- 📧 Email: support@example.com
- 💬 Discord: [Join our server](https://discord.gg/example)
- 📖 Documentation: [docs.example.com](https://docs.example.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/rat-control-panel/issues)

---

<div align="center">
  <strong>RAT Control Panel v2.0</strong><br>
  Built with ❤️ for security professionals and educators
</div>
