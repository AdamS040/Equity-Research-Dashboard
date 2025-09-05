# Market Data Integration & Real-time Services

This document describes the comprehensive market data integration and real-time services implementation for the Equity Research Dashboard.

## Overview

The market data system provides:
- **Multiple Data Providers**: Yahoo Finance, Financial Modeling Prep, Alpha Vantage, Tiingo
- **Real-time WebSocket Streaming**: Live market data updates
- **Intelligent Caching**: Redis-based caching with TTL strategies
- **Background Processing**: Celery-based job processing
- **Rate Limiting**: API quota management and fallback strategies
- **Comprehensive Error Handling**: Graceful degradation and retry logic

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   WebSocket     │    │   Background    │
│   (React)       │◄──►│   Service       │◄──►│   Jobs (Celery) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Endpoints │    │   Cache Service │    │   Data Providers│
│   (FastAPI)     │◄──►│   (Redis)       │◄──►│   (Multi-source)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (PostgreSQL)  │
                       └─────────────────┘
```

## Components

### 1. Data Providers

#### Yahoo Finance Client
- **Primary Provider**: Free, reliable, no API key required
- **Rate Limits**: 2000 requests/minute, 100,000 requests/day
- **Features**: Real-time quotes, historical data, company profiles
- **Implementation**: Uses `yfinance` library with async wrapper

#### Financial Modeling Prep Client
- **Secondary Provider**: Professional-grade financial data
- **Rate Limits**: 250 requests/minute, 10,000 requests/day
- **Features**: Comprehensive financial statements, advanced metrics
- **Implementation**: REST API with async HTTP client

#### Alpha Vantage Client
- **Tertiary Provider**: Technical indicators and advanced analytics
- **Rate Limits**: 5 requests/minute, 500 requests/day
- **Features**: Technical indicators, sector performance
- **Implementation**: REST API with rate limiting

#### Tiingo Client
- **Final Fallback**: Alternative data source
- **Rate Limits**: 1000 requests/minute, 50,000 requests/day
- **Features**: Historical data, news sentiment
- **Implementation**: REST API with token authentication

### 2. WebSocket Service

#### Connection Management
- **User-based Connections**: Each user can have multiple WebSocket connections
- **Subscription System**: Subscribe to specific symbols or market channels
- **Connection Pooling**: Efficient management of active connections
- **Graceful Disconnection**: Cleanup of subscriptions and resources

#### Real-time Data Streaming
- **Market Updates**: Indices, sectors, market sentiment
- **Quote Updates**: Individual stock price changes
- **Sector Updates**: Sector performance changes
- **Sentiment Updates**: Market sentiment indicators

#### Message Types
```json
{
  "type": "quote_update",
  "data": {
    "symbol": "AAPL",
    "quote": {
      "price": 150.25,
      "change": 2.15,
      "changePercent": 1.45,
      "volume": 45000000
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### 3. Caching System

#### Cache Strategy
- **Quote Cache**: 1-minute TTL for real-time data
- **Historical Cache**: 1-hour TTL for historical data
- **Profile Cache**: 30-minute TTL for company profiles
- **News Cache**: 15-minute TTL for news data
- **Indices Cache**: 2-minute TTL for market indices
- **Sentiment Cache**: 5-minute TTL for sentiment data

#### Cache Keys
```
quote:AAPL                    # Stock quote
historical:AAPL:1y:1d        # Historical data
profile:AAPL                 # Company profile
news:AAPL:10                 # Stock news
market:indices               # Market indices
market:sentiment             # Market sentiment
market:sectors               # Sector performance
market:movers:gainers        # Market movers
search:apple:10              # Search results
```

#### Cache Warming
- **Scheduled Warming**: Every 6 hours for popular stocks
- **On-demand Warming**: When cache misses occur
- **Background Warming**: During low-traffic periods

### 4. Background Jobs

#### Celery Tasks
- **Market Data Updates**: Every 5 minutes
- **Stock Quote Updates**: Every minute
- **Market Indices Updates**: Every 2 minutes
- **Market Sentiment Updates**: Every 5 minutes
- **Cache Warming**: Every 6 hours
- **Data Cleanup**: Daily at 2 AM

#### Task Management
- **Retry Logic**: Exponential backoff with max retries
- **Error Handling**: Comprehensive error logging and recovery
- **Task Monitoring**: Status tracking and health checks
- **Queue Management**: Priority-based task processing

### 5. API Endpoints

#### Market Data Endpoints
```
GET /api/v1/market/overview          # Market overview
GET /api/v1/market/indices           # Market indices
GET /api/v1/market/sectors           # Sector performance
GET /api/v1/market/movers            # Market movers
GET /api/v1/market/sentiment         # Market sentiment
GET /api/v1/market/quote/{symbol}    # Stock quote
GET /api/v1/market/historical/{symbol} # Historical data
GET /api/v1/market/profile/{symbol}  # Company profile
POST /api/v1/market/search           # Stock search
GET /api/v1/market/providers         # Available providers
```

#### WebSocket Endpoints
```
WS /api/v1/market/ws/market-data     # Market data stream
WS /api/v1/market/ws/stock-quotes    # Stock quotes stream
```

#### Management Endpoints
```
GET /api/v1/market/cache/stats       # Cache statistics
GET /api/v1/market/jobs/status       # Job status
GET /api/v1/market/jobs/{task_id}    # Task status
```

## Configuration

### Environment Variables
```bash
# Data Provider API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINANCIAL_MODELING_PREP_API_KEY=your_fmp_key
TIINGO_API_KEY=your_tiingo_key

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Rate Limiting Configuration
```python
# Provider-specific rate limits
YAHOO_FINANCE_LIMITS = {
    "requests_per_minute": 2000,
    "requests_per_day": 100000
}

FMP_LIMITS = {
    "requests_per_minute": 250,
    "requests_per_day": 10000
}

ALPHA_VANTAGE_LIMITS = {
    "requests_per_minute": 5,
    "requests_per_day": 500
}

TIINGO_LIMITS = {
    "requests_per_minute": 1000,
    "requests_per_day": 50000
}
```

## Usage Examples

### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/market/ws/market-data');

// Subscribe to market data
ws.send(JSON.stringify({
  type: 'subscribe',
  data: {
    type: 'market_data',
    channels: ['indices', 'sentiment']
  }
}));

// Subscribe to stock quotes
ws.send(JSON.stringify({
  type: 'subscribe',
  data: {
    type: 'stock_quotes',
    symbols: ['AAPL', 'MSFT', 'GOOGL']
  }
}));

// Handle incoming messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

### API Usage
```python
import httpx

# Get market overview
async with httpx.AsyncClient() as client:
    response = await client.get(
        'http://localhost:8000/api/v1/market/overview',
        headers={'Authorization': 'Bearer your_token'}
    )
    market_data = response.json()

# Get stock quote
response = await client.get(
    'http://localhost:8000/api/v1/market/quote/AAPL',
    headers={'Authorization': 'Bearer your_token'}
)
quote = response.json()

# Search stocks
search_data = {
    'query': 'apple',
    'limit': 10
}
response = await client.post(
    'http://localhost:8000/api/v1/market/search',
    json=search_data,
    headers={'Authorization': 'Bearer your_token'}
)
results = response.json()
```

## Performance Metrics

### Target Performance
- **API Response Time**: < 200ms
- **WebSocket Latency**: < 50ms
- **Cache Hit Rate**: > 90%
- **Background Job Processing**: < 5 minutes
- **Data Freshness**: < 1 minute for quotes, < 5 minutes for market data

### Monitoring
- **Prometheus Metrics**: Request counts, response times, error rates
- **Cache Statistics**: Hit rates, miss rates, TTL effectiveness
- **Job Monitoring**: Task success rates, processing times
- **WebSocket Metrics**: Connection counts, message throughput

## Error Handling

### Fallback Strategy
1. **Primary Provider**: Yahoo Finance (always available)
2. **Secondary Provider**: Financial Modeling Prep
3. **Tertiary Provider**: Alpha Vantage
4. **Final Fallback**: Tiingo
5. **Cache Fallback**: Return cached data if available
6. **Error Response**: Graceful error messages

### Error Types
- **Rate Limit Exceeded**: Automatic retry with backoff
- **Provider Unavailable**: Switch to next provider
- **Invalid Symbol**: Return 404 with helpful message
- **Network Timeout**: Retry with exponential backoff
- **Data Parsing Error**: Log error and try next provider

## Security

### Authentication
- **JWT Tokens**: Required for all API endpoints
- **WebSocket Auth**: Token-based authentication
- **Rate Limiting**: Per-user rate limiting
- **API Key Security**: Secure storage of provider API keys

### Data Validation
- **Input Validation**: Pydantic schemas for all inputs
- **Output Sanitization**: Clean data before sending to clients
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Proper data encoding

## Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/equity_research
    depends_on:
      - redis
      - postgres

  celery-worker:
    build: .
    command: python scripts/start_celery_worker.py
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  celery-beat:
    build: .
    command: python scripts/start_celery_beat.py
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=equity_research
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
```

### Production Considerations
- **Load Balancing**: Multiple API instances
- **Redis Clustering**: High availability caching
- **Database Replication**: Read replicas for performance
- **Monitoring**: Comprehensive logging and metrics
- **Backup Strategy**: Regular data backups
- **Scaling**: Horizontal scaling for high traffic

## Testing

### Unit Tests
```bash
# Run market data service tests
pytest app/services/test_market_data_service.py

# Run cache service tests
pytest app/services/test_cache_service.py

# Run WebSocket service tests
pytest app/services/test_websocket_service.py
```

### Integration Tests
```bash
# Run API endpoint tests
pytest app/api/v1/endpoints/test_market_data.py

# Run WebSocket integration tests
pytest tests/integration/test_websocket_integration.py
```

### Load Testing
```bash
# Test API performance
locust -f tests/load/test_api_load.py --host=http://localhost:8000

# Test WebSocket performance
locust -f tests/load/test_websocket_load.py --host=ws://localhost:8000
```

## Troubleshooting

### Common Issues

#### High API Response Times
- Check cache hit rates
- Verify provider rate limits
- Monitor database performance
- Check Redis connection health

#### WebSocket Connection Drops
- Check authentication tokens
- Verify network connectivity
- Monitor server resources
- Check for rate limiting

#### Background Job Failures
- Check Celery worker logs
- Verify Redis connectivity
- Monitor provider API status
- Check database connections

#### Cache Misses
- Verify cache TTL settings
- Check Redis memory usage
- Monitor cache warming jobs
- Verify cache key patterns

### Debug Commands
```bash
# Check cache statistics
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/market/cache/stats

# Check job status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/market/jobs/status

# Check WebSocket connections
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/market/ws/stats
```

## Future Enhancements

### Planned Features
- **Real-time News**: News sentiment analysis
- **Options Data**: Options chain and volatility data
- **Crypto Support**: Cryptocurrency market data
- **International Markets**: Global market data
- **Advanced Analytics**: Technical indicators and patterns
- **Machine Learning**: Predictive analytics and insights

### Performance Improvements
- **Data Compression**: Reduce WebSocket payload size
- **Batch Processing**: Optimize bulk data operations
- **Edge Caching**: CDN integration for static data
- **Database Optimization**: Query optimization and indexing
- **Async Processing**: More async operations for better concurrency

This comprehensive market data integration provides a robust, scalable, and performant solution for real-time financial data delivery with multiple fallback strategies and intelligent caching.
