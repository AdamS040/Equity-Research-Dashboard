# API Documentation

## 🚀 API Overview

The Equity Research Dashboard provides a comprehensive RESTful API for financial data, portfolio management, and analysis tools. The API is designed with modern best practices including type safety, comprehensive error handling, and real-time capabilities.

## 🔗 Base URL

```
Development: http://localhost:5000/api
Production: https://api.equity-dashboard.com/api
```

## 🔐 Authentication

### **JWT Token Authentication**

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### **Token Management**

#### **Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user-id",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe"
    },
    "token": "jwt-access-token",
    "refreshToken": "jwt-refresh-token",
    "expiresIn": 3600
  }
}
```

#### **Refresh Token**
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refreshToken": "jwt-refresh-token"
}
```

#### **Logout**
```http
POST /api/auth/logout
Authorization: Bearer <your-jwt-token>
```

## 📊 Stock Data API

### **Stock Search**

```http
GET /api/stocks/search?query=AAPL&limit=10
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "exchange": "NASDAQ",
      "type": "stock",
      "marketCap": 3000000000000
    }
  ]
}
```

### **Stock Quote**

```http
GET /api/stocks/AAPL/quote
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "price": 150.25,
    "change": 2.15,
    "changePercent": 1.45,
    "volume": 45000000,
    "avgVolume": 50000000,
    "high": 152.00,
    "low": 148.50,
    "open": 149.00,
    "previousClose": 148.10,
    "marketCap": 3000000000000,
    "pe": 25.5,
    "eps": 5.89,
    "dividend": 0.96,
    "dividendYield": 0.64,
    "timestamp": "2024-01-15T16:00:00Z"
  }
}
```

### **Historical Data**

```http
GET /api/stocks/AAPL/historical?period=1y&interval=1d
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-01-15",
      "open": 149.00,
      "high": 152.00,
      "low": 148.50,
      "close": 150.25,
      "volume": 45000000,
      "adjustedClose": 150.25
    }
  ]
}
```

### **Financial Metrics**

```http
GET /api/stocks/AAPL/metrics?period=annual
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "period": "annual",
    "year": 2023,
    "revenue": 383285000000,
    "netIncome": 96995000000,
    "totalAssets": 352755000000,
    "totalLiabilities": 258549000000,
    "equity": 94206000000,
    "operatingCashFlow": 110543000000,
    "freeCashFlow": 99584000000,
    "roe": 10.3,
    "roa": 2.7,
    "debtToEquity": 0.17,
    "currentRatio": 1.04,
    "grossMargin": 0.44,
    "operatingMargin": 0.30,
    "netMargin": 0.25,
    "eps": 6.13,
    "pe": 24.5,
    "pb": 3.2,
    "ps": 7.8,
    "evEbitda": 18.5
  }
}
```

### **Stock News**

```http
GET /api/stocks/AAPL/news?limit=20&offset=0
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "news-id",
        "symbol": "AAPL",
        "title": "Apple Reports Strong Q4 Earnings",
        "summary": "Apple Inc. reported better-than-expected earnings...",
        "content": "Full article content...",
        "source": "Reuters",
        "url": "https://example.com/news",
        "publishedAt": "2024-01-15T10:30:00Z",
        "sentiment": "positive",
        "relevance": 0.95
      }
    ],
    "total": 150,
    "page": 1,
    "limit": 20,
    "hasNext": true,
    "hasPrev": false
  }
}
```

## 📈 Portfolio Management API

### **Get Portfolios**

```http
GET /api/portfolios
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "portfolio-id",
      "name": "My Portfolio",
      "description": "Main investment portfolio",
      "totalValue": 100000,
      "totalCost": 95000,
      "totalReturn": 5000,
      "totalReturnPercent": 5.26,
      "dayChange": 250,
      "dayChangePercent": 0.25,
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-15T16:00:00Z"
    }
  ]
}
```

### **Create Portfolio**

```http
POST /api/portfolios
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "name": "New Portfolio",
  "description": "Portfolio description"
}
```

### **Get Portfolio Holdings**

```http
GET /api/portfolios/{portfolioId}/holdings
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "holding-id",
      "symbol": "AAPL",
      "shares": 100,
      "averagePrice": 145.50,
      "currentPrice": 150.25,
      "marketValue": 15025,
      "costBasis": 14550,
      "unrealizedGain": 475,
      "unrealizedGainPercent": 3.26,
      "weight": 0.15,
      "addedAt": "2024-01-01T00:00:00Z",
      "lastUpdated": "2024-01-15T16:00:00Z"
    }
  ]
}
```

### **Add Holding**

```http
POST /api/portfolios/{portfolioId}/holdings
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "symbol": "AAPL",
  "shares": 100,
  "averagePrice": 145.50
}
```

### **Portfolio Performance**

```http
GET /api/portfolios/{portfolioId}/performance?period=1y
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "portfolioId": "portfolio-id",
    "period": "1y",
    "returns": 0.15,
    "volatility": 0.18,
    "sharpeRatio": 0.83,
    "maxDrawdown": -0.08,
    "beta": 1.05,
    "alpha": 0.02,
    "benchmarkComparison": {
      "benchmark": "SPY",
      "benchmarkReturn": 0.13,
      "excessReturn": 0.02,
      "trackingError": 0.05,
      "informationRatio": 0.40
    }
  }
}
```

## 🔬 Analysis API

### **DCF Analysis**

```http
POST /api/analysis/dcf
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "symbol": "AAPL",
  "assumptions": {
    "growthRate": 0.05,
    "terminalGrowthRate": 0.03,
    "discountRate": 0.10,
    "taxRate": 0.25
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "currentPrice": 150.25,
    "fairValue": 165.50,
    "upside": 15.25,
    "upsidePercent": 10.15,
    "assumptions": {
      "growthRate": 0.05,
      "terminalGrowthRate": 0.03,
      "discountRate": 0.10,
      "taxRate": 0.25
    },
    "projections": {
      "years": [2024, 2025, 2026, 2027, 2028],
      "revenue": [400000000000, 420000000000, 441000000000, 463050000000, 486202500000],
      "ebitda": [120000000000, 126000000000, 132300000000, 138915000000, 145860750000],
      "freeCashFlow": [100000000000, 105000000000, 110250000000, 115762500000, 121550625000],
      "terminalValue": 2431012500000,
      "presentValue": 2000000000000
    }
  }
}
```

### **Comparable Analysis**

```http
POST /api/analysis/comparable
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "symbol": "AAPL",
  "peerSymbols": ["MSFT", "GOOGL", "AMZN", "META"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "peers": [
      {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "marketCap": 2800000000000,
        "pe": 28.5,
        "pb": 12.3,
        "ps": 8.9,
        "evEbitda": 20.1,
        "roe": 0.45,
        "debtToEquity": 0.25
      }
    ],
    "metrics": {
      "pe": {
        "min": 15.2,
        "max": 35.8,
        "median": 25.5,
        "mean": 26.1
      },
      "pb": {
        "min": 3.1,
        "max": 15.2,
        "median": 8.5,
        "mean": 9.2
      }
    },
    "valuation": {
      "peBased": 165.50,
      "pbBased": 158.75,
      "psBased": 162.25,
      "evEbitdaBased": 160.00,
      "average": 161.63,
      "confidence": 0.85
    }
  }
}
```

### **Risk Analysis**

```http
POST /api/analysis/risk
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "symbol": "AAPL",
  "timeHorizon": 252,
  "confidenceLevel": 0.95
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "metrics": {
      "beta": 1.05,
      "volatility": 0.25,
      "sharpeRatio": 0.60,
      "maxDrawdown": -0.15,
      "var95": -0.04,
      "var99": -0.06,
      "expectedShortfall": -0.05,
      "downsideDeviation": 0.18
    },
    "stressTests": [
      {
        "scenario": "Market Crash",
        "impact": -0.20,
        "probability": 0.05,
        "description": "20% market decline scenario"
      }
    ],
    "varAnalysis": {
      "confidenceLevels": [
        {
          "confidence": 0.95,
          "value": -0.04
        },
        {
          "confidence": 0.99,
          "value": -0.06
        }
      ],
      "historical": -0.04,
      "parametric": -0.04,
      "monteCarlo": -0.04
    }
  }
}
```

## 📊 Market Data API

### **Market Overview**

```http
GET /api/market/overview
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "indices": [
      {
        "symbol": "SPY",
        "name": "S&P 500",
        "value": 4500.25,
        "change": 25.50,
        "changePercent": 0.57
      }
    ],
    "sectors": [
      {
        "sector": "Technology",
        "change": 0.75,
        "changePercent": 0.85,
        "topGainers": ["AAPL", "MSFT", "GOOGL"],
        "topLosers": ["META", "NFLX"]
      }
    ],
    "movers": {
      "gainers": [
        {
          "symbol": "AAPL",
          "price": 150.25,
          "change": 2.15,
          "changePercent": 1.45,
          "volume": 45000000
        }
      ],
      "losers": [],
      "mostActive": []
    },
    "timestamp": "2024-01-15T16:00:00Z"
  }
}
```

### **Sector Performance**

```http
GET /api/market/sectors
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "sector": "Technology",
      "change": 0.75,
      "changePercent": 0.85,
      "topGainers": ["AAPL", "MSFT", "GOOGL"],
      "topLosers": ["META", "NFLX"],
      "marketCap": 15000000000000,
      "weight": 0.28
    }
  ]
}
```

## 📋 Reports API

### **Get Reports**

```http
GET /api/reports
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "report-id",
        "title": "AAPL Analysis Report",
        "type": "stock",
        "symbol": "AAPL",
        "status": "published",
        "createdAt": "2024-01-15T10:00:00Z",
        "updatedAt": "2024-01-15T10:00:00Z",
        "publishedAt": "2024-01-15T10:00:00Z"
      }
    ],
    "total": 25,
    "page": 1,
    "limit": 20,
    "hasNext": true,
    "hasPrev": false
  }
}
```

### **Generate Report**

```http
POST /api/reports
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "title": "AAPL Analysis Report",
  "type": "stock",
  "symbol": "AAPL",
  "template": "stock-analysis-template",
  "parameters": {
    "includeDCF": true,
    "includeComparable": true,
    "includeRisk": true
  }
}
```

### **Export Report**

```http
GET /api/reports/{reportId}/export?format=pdf
Authorization: Bearer <your-jwt-token>
```

**Response:** Binary file (PDF, Excel, Word, etc.)

## 🔄 WebSocket API

### **Connection**

```javascript
const ws = new WebSocket('ws://localhost:5000/ws/market-data');

ws.onopen = function() {
  console.log('WebSocket connected');
};

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### **Market Data Stream**

```javascript
// Subscribe to market data
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'market-data',
  symbols: ['AAPL', 'MSFT', 'GOOGL']
}));

// Receive real-time updates
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'market-data') {
    // Update UI with real-time data
    updateStockPrice(data.symbol, data.price);
  }
};
```

### **Portfolio Updates**

```javascript
// Subscribe to portfolio updates
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'portfolio',
  portfolioId: 'portfolio-id'
}));

// Receive portfolio updates
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'portfolio-update') {
    // Update portfolio UI
    updatePortfolioValue(data.totalValue);
  }
};
```

## ❌ Error Handling

### **Error Response Format**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "symbol",
      "reason": "Symbol is required"
    }
  },
  "timestamp": "2024-01-15T16:00:00Z"
}
```

### **HTTP Status Codes**

- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **422**: Validation Error
- **429**: Rate Limited
- **500**: Internal Server Error

### **Error Codes**

- **VALIDATION_ERROR**: Input validation failed
- **AUTHENTICATION_ERROR**: Authentication failed
- **AUTHORIZATION_ERROR**: Insufficient permissions
- **NOT_FOUND**: Resource not found
- **RATE_LIMITED**: Too many requests
- **EXTERNAL_API_ERROR**: External API error
- **INTERNAL_ERROR**: Internal server error

## 📊 Rate Limiting

### **Rate Limits**

- **Authentication**: 5 requests per minute
- **Stock Data**: 100 requests per minute
- **Portfolio Data**: 50 requests per minute
- **Analysis**: 20 requests per minute
- **Reports**: 10 requests per minute

### **Rate Limit Headers**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642252800
```

## 🔧 SDK and Libraries

### **TypeScript SDK**

```typescript
import { EquityDashboardAPI } from '@equity-dashboard/sdk';

const api = new EquityDashboardAPI({
  baseURL: 'https://api.equity-dashboard.com/api',
  token: 'your-jwt-token'
});

// Get stock quote
const quote = await api.stocks.getQuote('AAPL');

// Get portfolio
const portfolio = await api.portfolios.get('portfolio-id');

// Generate DCF analysis
const dcf = await api.analysis.dcf({
  symbol: 'AAPL',
  assumptions: {
    growthRate: 0.05,
    terminalGrowthRate: 0.03,
    discountRate: 0.10
  }
});
```

### **React Hooks**

```typescript
import { useStock, usePortfolio, useDCFAnalysis } from '@equity-dashboard/hooks';

function StockComponent() {
  const { data: stock, isLoading, error } = useStock('AAPL');
  const { data: portfolio } = usePortfolio('portfolio-id');
  const { data: dcf } = useDCFAnalysis('AAPL', {
    growthRate: 0.05,
    terminalGrowthRate: 0.03,
    discountRate: 0.10
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>{stock.name}</h1>
      <p>Price: ${stock.price}</p>
      <p>DCF Fair Value: ${dcf.fairValue}</p>
    </div>
  );
}
```

## 📚 Additional Resources

- **[API Changelog](CHANGELOG.md)** - API version history and changes
- **[SDK Documentation](SDK.md)** - SDK usage and examples
- **[WebSocket Guide](WEBSOCKET.md)** - Real-time data integration
- **[Error Handling Guide](ERRORS.md)** - Comprehensive error handling
- **[Rate Limiting Guide](RATE_LIMITING.md)** - Rate limiting best practices

---

For more information, please refer to the [Architecture Guide](ARCHITECTURE.md) or contact our support team.
