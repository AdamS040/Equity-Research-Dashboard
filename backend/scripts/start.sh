#!/bin/bash

# Equity Research Dashboard Backend Startup Script

set -e

echo "🚀 Starting Equity Research Dashboard Backend..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   You can start the services with: docker-compose up -d"
    exit 1
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "🔍 Checking service health..."

# Check PostgreSQL
if ! docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not ready"
    exit 1
fi
echo "✅ PostgreSQL is ready"

# Check Redis
if ! docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not ready"
    exit 1
fi
echo "✅ Redis is ready"

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec backend alembic upgrade head

# Check if backend is healthy
echo "🔍 Checking backend health..."
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend is not healthy"
    exit 1
fi
echo "✅ Backend is ready"

echo ""
echo "🎉 Equity Research Dashboard Backend is ready!"
echo ""
echo "📚 API Documentation: http://localhost:8000/api/v1/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo "📊 Metrics: http://localhost:8000/metrics"
echo ""
echo "To view logs: docker-compose logs -f backend"
echo "To stop services: docker-compose down"
echo ""
