# 🚆 Railway Traffic Decision-Support System

An AI-powered decision support system for railway traffic management, designed to optimize train precedence, crossings, and scheduling in real-time.

## 📌 Overview

Indian Railways currently relies on manual decision-making by traffic controllers to manage train precedence, crossings, and scheduling. As traffic grows, manual operations face limitations: increasing congestion, delays, and inefficient use of track capacity.

This system provides **AI + Optimization powered Decision-Support** to assist section controllers with real-time recommendations for train scheduling, rerouting, and platform allocation—improving throughput, punctuality, and safety.

## 🎯 Key Features

- **Real-time Optimization**: AI-powered decision engine using constraint programming
- **Interactive Dashboard**: Web-based visualization with live train tracking
- **Performance Metrics**: Throughput improvement and delay reduction tracking
- **Emergency Controls**: Panic mode for manual override
- **RESTful API**: Integration-ready endpoints for railway systems
- **Scalable Architecture**: Microservices design with clean separation of concerns

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend API | FastAPI (Python) | RESTful API with async support |
| Database | PostgreSQL + TimescaleDB | Time-series data and relational storage |
| Optimization | OR-Tools | Constraint programming and linear optimization |
| AI/ML | XGBoost, PyTorch | Delay prediction and disruption modeling |
| Caching | Redis | Real-time status updates |
| Visualization | Plotly, D3.js | Interactive charts and maps |
| Frontend | HTML/JS + Bootstrap | Lightweight web dashboard |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+ (or use Docker)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/railway-ai/tracksAI.git
   cd tracksAI
   ```

2. **Set up environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose (Recommended)**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Or install locally**
   ```bash
   pip install -r requirements.txt
   uvicorn api.main:app --reload
   ```

5. **Access the system**
   - API Documentation: http://localhost:8000/docs
   - Dashboard: http://localhost:8000/dashboard
   - Health Check: http://localhost:8000/health

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP API /     │    │   Data          │    │   PostgreSQL    │
│   Schedules     │───▶│   Collector     │───▶│   + TimescaleDB │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web           │◀───│   FastAPI       │◀───│   Decision      │
│   Dashboard     │    │   Backend       │    │   Engine        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis Cache   │    │   OR-Tools      │
                       │   + Kafka       │    │   Optimizer     │
                       └─────────────────┘    └─────────────────┘
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=api

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m optimization
```

## 📈 Performance Metrics

The system tracks key performance indicators:

- **Throughput**: Trains handled per hour
- **Average Delay**: Mean delay reduction in minutes
- **On-time Percentage**: Punctuality improvement
- **Optimization Confidence**: AI decision confidence scores

## 🔧 Development

### Code Quality

The project follows strict coding standards:

```bash
# Format code
black .
isort .

# Lint code
ruff .

# Type checking
mypy core api

# Run tests
pytest
```

### Architecture Guidelines

- **Core Domain Logic**: Pure Python in `/core` module
- **I/O Operations**: Isolated in `/api`, `/ingest`, `/workers`
- **Database Access**: Through repository interfaces only
- **Error Handling**: Structured logging with correlation IDs
- **Testing**: 80% minimum coverage for critical modules

## 🚨 Emergency Procedures

### Panic Mode

In case of system issues, enable panic mode:

```bash
curl -X POST http://localhost:8000/api/v1/optimization/panic-mode
```

This disables auto-recommendations and reverts to manual control.

### Rollback

Quick rollback procedures are available for:
- Database schema changes
- Feature toggles
- Model updates

## 📚 API Documentation

### Core Endpoints

- `GET /api/v1/trains` - List all trains
- `GET /api/v1/sections` - List railway sections
- `POST /api/v1/optimization/optimize` - Run optimization
- `GET /dashboard` - Web dashboard
- `GET /metrics` - Prometheus metrics

### Authentication

The system supports JWT-based authentication for production deployments.

## 🔐 Security

- Input validation and sanitization
- SQL injection prevention
- HTTPS enforcement in production
- Secret management via environment variables
- OWASP security guidelines compliance

## 📋 Roadmap

- [ ] Multi-section optimization
- [ ] Reinforcement learning integration
- [ ] Mobile/tablet interface
- [ ] Real signalling system integration
- [ ] Weather and disruption modeling
- [ ] Predictive maintenance integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the coding standards
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **AI/ML Developer** → Disruption modeling, delay prediction
- **Optimization Engineer** → OR algorithms, solvers
- **Backend Engineer** → APIs, database, data adapters
- **UI Developer** → Dashboard visuals
- **Systems Integrator** → MCP API, railway systems compatibility

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

---

**Built with ❤️ for Indian Railways**
