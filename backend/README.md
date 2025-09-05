# Equity Research Dashboard Backend

A sophisticated, production-ready backend API for the Equity Research Dashboard built with FastAPI, PostgreSQL, and Redis.

## Features

- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- **PostgreSQL Database**: Robust relational database with SQLAlchemy ORM
- **Redis Caching**: High-performance caching and session management
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Docker Support**: Complete containerization with Docker Compose
- **Database Migrations**: Alembic for schema versioning and migrations
- **Structured Logging**: JSON logging with configurable levels
- **Health Checks**: Comprehensive health monitoring endpoints
- **Security**: Password hashing, CORS, rate limiting, and security headers
- **Monitoring**: Prometheus metrics and Grafana dashboards

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (for local development)
- Redis 7+ (for local development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd equity-research-dashboard/backend
   ```

2. **Copy environment configuration**
   ```bash
   cp env.example .env
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/api/v1/docs
   - Health Check: http://localhost:8000/health
   - API Base URL: http://localhost:8000/api/v1

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start PostgreSQL and Redis**
   ```bash
   docker-compose up -d postgres redis
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password
- `POST /api/v1/auth/verify-email` - Verify email address
- `GET /api/v1/auth/me` - Get current user info

### User Management Endpoints

- `GET /api/v1/users/me` - Get user profile
- `PUT /api/v1/users/me` - Update user profile
- `POST /api/v1/users/me/change-password` - Change password
- `GET /api/v1/users/me/sessions` - Get user sessions
- `DELETE /api/v1/users/me/sessions/{session_id}` - Revoke session
- `DELETE /api/v1/users/me` - Delete account

### Portfolio Endpoints

- `GET /api/v1/portfolios/` - Get user portfolios
- `POST /api/v1/portfolios/` - Create portfolio
- `GET /api/v1/portfolios/{portfolio_id}` - Get portfolio
- `PUT /api/v1/portfolios/{portfolio_id}` - Update portfolio
- `DELETE /api/v1/portfolios/{portfolio_id}` - Delete portfolio

### Health Check Endpoints

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health check
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check
- `GET /metrics` - Prometheus metrics

## Database Schema

### Core Tables

- **users**: User accounts and authentication
- **user_sessions**: Active user sessions
- **user_preferences**: User-specific settings
- **user_activities**: User activity logs
- **portfolios**: Investment portfolios
- **portfolio_holdings**: Individual stock positions
- **portfolio_transactions**: Buy/sell transactions
- **portfolio_performance**: Historical performance data
- **portfolio_alerts**: Price and performance alerts

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Application environment | `development` |
| `DEBUG` | Enable debug mode | `false` |
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `REDIS_URL` | Redis connection URL | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | Optional |
| `FINANCIAL_MODELING_PREP_API_KEY` | Financial Modeling Prep API key | Optional |
| `TIINGO_API_KEY` | Tiingo API key | Optional |

### Database Configuration

- **Connection Pooling**: Configurable pool size and overflow
- **Connection Timeout**: 30 seconds default
- **Connection Recycle**: 1 hour default
- **Health Checks**: Automatic connection validation

### Redis Configuration

- **Connection Pooling**: Up to 20 concurrent connections
- **Socket Timeouts**: 5 seconds for operations
- **Retry Logic**: Automatic retry on timeout
- **Health Checks**: Connection validation

## Security Features

### Authentication & Authorization

- **JWT Tokens**: Access tokens (15 min) and refresh tokens (7 days)
- **Password Hashing**: bcrypt with configurable rounds
- **Session Management**: Secure session tracking and revocation
- **Role-Based Access**: User roles and permissions

### Security Headers

- **CORS**: Configurable cross-origin resource sharing
- **Rate Limiting**: 1000 requests per hour per user
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM protection

## Monitoring & Observability

### Health Checks

- **Database Health**: Connection and query validation
- **Redis Health**: Connection and operation validation
- **Service Status**: Overall application health

### Metrics

- **Prometheus Integration**: HTTP request metrics
- **Custom Metrics**: Business logic metrics
- **Performance Monitoring**: Response time tracking

### Logging

- **Structured Logging**: JSON format for production
- **Log Levels**: Configurable logging levels
- **Request Logging**: HTTP request/response logging
- **Error Tracking**: Comprehensive error logging

## Development

### Code Quality

- **Type Hints**: Full type annotation coverage
- **Linting**: Black, isort, flake8, mypy
- **Testing**: pytest with async support
- **Documentation**: Comprehensive docstrings

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## Deployment

### Docker Production

```bash
# Build production image
docker build -t equity-research-backend .

# Run with production settings
docker run -d \
  --name equity-research-backend \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  equity-research-backend
```

### Docker Compose Production

```bash
# Start with production profile
docker-compose --profile production up -d

# Start with monitoring
docker-compose --profile monitoring up -d
```

### Environment-Specific Configuration

- **Development**: Debug enabled, local database
- **Staging**: Production-like with test data
- **Production**: Optimized for performance and security

## API Usage Examples

### User Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123",
    "confirm_password": "SecurePassword123",
    "first_name": "John",
    "last_name": "Doe",
    "agree_to_terms": true
  }'
```

### User Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'
```

### Authenticated Request

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check PostgreSQL is running
   - Verify DATABASE_URL format
   - Check network connectivity

2. **Redis Connection Failed**
   - Check Redis is running
   - Verify REDIS_URL format
   - Check authentication credentials

3. **Migration Errors**
   - Ensure database is accessible
   - Check migration file syntax
   - Verify model imports

### Logs

```bash
# View application logs
docker-compose logs -f backend

# View database logs
docker-compose logs -f postgres

# View Redis logs
docker-compose logs -f redis
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API documentation at `/api/v1/docs`
