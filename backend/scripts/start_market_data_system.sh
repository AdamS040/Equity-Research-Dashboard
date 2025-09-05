#!/bin/bash

# Market Data System Startup Script
# This script starts all components of the market data system

set -e

echo "🚀 Starting Market Data System..."

# Check if required services are running
echo "📋 Checking prerequisites..."

# Check Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Please start Redis first."
    echo "   docker run -d -p 6379:6379 redis:7-alpine"
    exit 1
fi
echo "✅ Redis is running"

# Check PostgreSQL
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    echo "   docker run -d -p 5432:5432 -e POSTGRES_DB=equity_research -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password postgres:15-alpine"
    exit 1
fi
echo "✅ PostgreSQL is running"

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export REDIS_URL="redis://localhost:6379/0"
export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/equity_research"

# Create logs directory
mkdir -p logs

echo "🔧 Starting Celery Beat Scheduler..."
# Start Celery Beat in background
python scripts/start_celery_beat.py > logs/celery_beat.log 2>&1 &
CELERY_BEAT_PID=$!
echo "✅ Celery Beat started (PID: $CELERY_BEAT_PID)"

echo "👷 Starting Celery Worker..."
# Start Celery Worker in background
python scripts/start_celery_worker.py > logs/celery_worker.log 2>&1 &
CELERY_WORKER_PID=$!
echo "✅ Celery Worker started (PID: $CELERY_WORKER_PID)"

# Wait a moment for Celery to initialize
sleep 3

echo "🌐 Starting FastAPI Application..."
# Start FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/fastapi.log 2>&1 &
FASTAPI_PID=$!
echo "✅ FastAPI started (PID: $FASTAPI_PID)"

# Wait for FastAPI to start
sleep 5

echo "📊 Market Data System is running!"
echo ""
echo "🔗 Services:"
echo "   • FastAPI API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/api/v1/docs"
echo "   • WebSocket Market Data: ws://localhost:8000/api/v1/market/ws/market-data"
echo "   • WebSocket Stock Quotes: ws://localhost:8000/api/v1/market/ws/stock-quotes"
echo ""
echo "📝 Logs:"
echo "   • FastAPI: logs/fastapi.log"
echo "   • Celery Beat: logs/celery_beat.log"
echo "   • Celery Worker: logs/celery_worker.log"
echo ""
echo "🛑 To stop the system:"
echo "   kill $FASTAPI_PID $CELERY_BEAT_PID $CELERY_WORKER_PID"
echo ""

# Create a simple health check
echo "🏥 Performing health check..."
sleep 10

# Check if FastAPI is responding
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ FastAPI health check passed"
else
    echo "❌ FastAPI health check failed"
fi

# Check if Celery is responding
if celery -A app.services.background_jobs inspect active > /dev/null 2>&1; then
    echo "✅ Celery health check passed"
else
    echo "❌ Celery health check failed"
fi

echo ""
echo "🎉 Market Data System is ready!"
echo ""
echo "📖 Quick Start:"
echo "   1. Get an auth token: POST /api/v1/auth/login"
echo "   2. Get market overview: GET /api/v1/market/overview"
echo "   3. Get stock quote: GET /api/v1/market/quote/AAPL"
echo "   4. Connect to WebSocket: ws://localhost:8000/api/v1/market/ws/market-data"
echo ""
echo "📚 Documentation: http://localhost:8000/api/v1/docs"
echo ""

# Keep the script running and show logs
echo "📋 Following logs (Ctrl+C to stop)..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Market Data System..."
    kill $FASTAPI_PID $CELERY_BEAT_PID $CELERY_WORKER_PID 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Follow logs
tail -f logs/fastapi.log logs/celery_beat.log logs/celery_worker.log
