@echo off
REM Market Data System Startup Script for Windows
REM This script starts all components of the market data system

echo 🚀 Starting Market Data System...

REM Check if required services are running
echo 📋 Checking prerequisites...

REM Check Redis (assuming Redis is running on default port)
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo ❌ Redis is not running. Please start Redis first.
    echo    docker run -d -p 6379:6379 redis:7-alpine
    pause
    exit /b 1
)
echo ✅ Redis is running

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%CD%
set REDIS_URL=redis://localhost:6379/0
set DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/equity_research

REM Create logs directory
if not exist logs mkdir logs

echo 🔧 Starting Celery Beat Scheduler...
REM Start Celery Beat in background
start /B python scripts/start_celery_beat.py > logs/celery_beat.log 2>&1
echo ✅ Celery Beat started

echo 👷 Starting Celery Worker...
REM Start Celery Worker in background
start /B python scripts/start_celery_worker.py > logs/celery_worker.log 2>&1
echo ✅ Celery Worker started

REM Wait a moment for Celery to initialize
timeout /t 3 /nobreak >nul

echo 🌐 Starting FastAPI Application...
REM Start FastAPI application
start /B uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/fastapi.log 2>&1
echo ✅ FastAPI started

REM Wait for FastAPI to start
timeout /t 5 /nobreak >nul

echo 📊 Market Data System is running!
echo.
echo 🔗 Services:
echo    • FastAPI API: http://localhost:8000
echo    • API Documentation: http://localhost:8000/api/v1/docs
echo    • WebSocket Market Data: ws://localhost:8000/api/v1/market/ws/market-data
echo    • WebSocket Stock Quotes: ws://localhost:8000/api/v1/market/ws/stock-quotes
echo.
echo 📝 Logs:
echo    • FastAPI: logs/fastapi.log
echo    • Celery Beat: logs/celery_beat.log
echo    • Celery Worker: logs/celery_worker.log
echo.
echo 🛑 To stop the system, close this window or press Ctrl+C
echo.

REM Create a simple health check
echo 🏥 Performing health check...
timeout /t 10 /nobreak >nul

REM Check if FastAPI is responding
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ❌ FastAPI health check failed
) else (
    echo ✅ FastAPI health check passed
)

echo.
echo 🎉 Market Data System is ready!
echo.
echo 📖 Quick Start:
echo    1. Get an auth token: POST /api/v1/auth/login
echo    2. Get market overview: GET /api/v1/market/overview
echo    3. Get stock quote: GET /api/v1/market/quote/AAPL
echo    4. Connect to WebSocket: ws://localhost:8000/api/v1/market/ws/market-data
echo.
echo 📚 Documentation: http://localhost:8000/api/v1/docs
echo.

echo 📋 Press any key to view logs or Ctrl+C to stop...
pause >nul

REM Show logs
echo 📋 Following logs (Ctrl+C to stop)...
echo.
type logs/fastapi.log
