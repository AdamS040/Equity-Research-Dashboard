# Financial Data API Alternatives

Since IEX Cloud retired on August 31, 2024, we've updated the backend to support multiple alternative financial data providers. This document outlines the available options and their features.

## Primary Alternatives

### 1. Financial Modeling Prep (FMP) - **Recommended Primary**

**Why FMP is our top choice:**
- Comprehensive financial data including 30+ years of historical data
- Earnings call transcripts dating back to 2007
- Real-time and historical market data
- Excellent API documentation
- Good pricing for equity research use cases
- Strong focus on fundamental analysis data

**API Features:**
- Real-time stock quotes
- Historical price data
- Financial statements (Income Statement, Balance Sheet, Cash Flow)
- Company profiles and metrics
- Earnings data and transcripts
- Insider trading data
- Institutional holdings
- Analyst estimates and price targets

**Pricing:**
- Free tier: 250 requests/day
- Basic: $14/month (10,000 requests/day)
- Professional: $29/month (50,000 requests/day)
- Enterprise: Custom pricing

**Get API Key:** https://financialmodelingprep.com/developer/docs

### 2. Alpha Vantage - **Good Secondary Option**

**Why Alpha Vantage:**
- Generous free tier (500 requests/day)
- Familiar JSON responses
- Good for basic market data
- Active community support
- Global market coverage

**API Features:**
- Real-time and historical stock data
- Technical indicators
- Foreign exchange rates
- Cryptocurrency data
- Economic indicators
- News sentiment

**Pricing:**
- Free: 500 requests/day
- Premium: $49.99/month (1,200 requests/day)
- Enterprise: Custom pricing

**Get API Key:** https://www.alphavantage.co/support/#api-key

### 3. Tiingo - **High-Quality Data**

**Why Tiingo:**
- Transparent, fixed pricing model
- High-quality data with extensive history
- Simplified query system
- Good for institutional use
- Strong data quality and reliability

**API Features:**
- End-of-day data back to 1962
- Intraday data with 1-minute bars from 2017
- Real-time quotes
- News data
- IEX data (since IEX Cloud shutdown)
- Crypto data

**Pricing:**
- Free: 1,000 requests/day
- Starter: $10/month (10,000 requests/day)
- Professional: $20/month (50,000 requests/day)
- Enterprise: Custom pricing

**Get API Key:** https://www.tiingo.com/

## Additional Options

### 4. EODHD (End of Day Historical Data)

**Features:**
- Extensive fundamental data (US companies back to 1985)
- 20,000+ US mutual funds
- 10,000+ global ETFs
- Real-time data with <50ms latency
- 24/7 customer support

**Pricing:**
- Free: 20 requests/day
- Basic: $9.99/month (1,000 requests/day)
- Professional: $19.99/month (10,000 requests/day)

### 5. Databento

**Features:**
- Real-time data from 60+ trading venues
- Usage-based pricing (per GB)
- No monthly commitments
- Official Python, C++, Rust libraries
- High-frequency trading focus

**Pricing:**
- Pay-per-use model
- $0.10 per GB for historical data
- $0.50 per GB for real-time data

### 6. Finage

**Features:**
- Real-time and historical data
- Stocks, crypto, forex coverage
- User-friendly interface
- Comprehensive documentation
- Easy migration from IEX Cloud

**Pricing:**
- Free: 1,000 requests/day
- Basic: $9.99/month (10,000 requests/day)
- Professional: $19.99/month (50,000 requests/day)

## Implementation Strategy

### Phase 1: Primary Integration (FMP)
1. **Real-time Quotes**: Use FMP for current stock prices
2. **Historical Data**: Leverage FMP's extensive historical database
3. **Financial Statements**: Use FMP for fundamental analysis
4. **Earnings Data**: Utilize FMP's earnings transcripts and data

### Phase 2: Secondary Integration (Alpha Vantage)
1. **Backup Data Source**: Use Alpha Vantage as fallback
2. **Technical Indicators**: Leverage Alpha Vantage's technical analysis
3. **Economic Data**: Use for macroeconomic indicators
4. **News Sentiment**: Integrate news sentiment analysis

### Phase 3: Specialized Integration (Tiingo)
1. **High-Quality Historical Data**: Use Tiingo for long-term analysis
2. **IEX Data**: Access IEX data through Tiingo
3. **News Integration**: Leverage Tiingo's news API
4. **Crypto Data**: Use for cryptocurrency analysis

## API Integration Examples

### Financial Modeling Prep Integration

```python
import httpx
from app.config import settings

class FMPClient:
    def __init__(self):
        self.api_key = settings.financial_modeling_prep_api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"
    
    async def get_quote(self, symbol: str):
        """Get real-time stock quote."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/quote/{symbol}",
                params={"apikey": self.api_key}
            )
            return response.json()
    
    async def get_historical_data(self, symbol: str, period: str = "1y"):
        """Get historical price data."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/historical-price-full/{symbol}",
                params={
                    "apikey": self.api_key,
                    "timeseries": period
                }
            )
            return response.json()
    
    async def get_financial_statements(self, symbol: str, statement_type: str = "income-statement"):
        """Get financial statements."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{statement_type}/{symbol}",
                params={"apikey": self.api_key}
            )
            return response.json()
```

### Alpha Vantage Integration

```python
class AlphaVantageClient:
    def __init__(self):
        self.api_key = settings.alpha_vantage_api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    async def get_quote(self, symbol: str):
        """Get real-time stock quote."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url,
                params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": symbol,
                    "apikey": self.api_key
                }
            )
            return response.json()
    
    async def get_technical_indicator(self, symbol: str, indicator: str = "RSI"):
        """Get technical indicators."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url,
                params={
                    "function": indicator,
                    "symbol": symbol,
                    "interval": "daily",
                    "time_period": 14,
                    "series_type": "close",
                    "apikey": self.api_key
                }
            )
            return response.json()
```

### Tiingo Integration

```python
class TiingoClient:
    def __init__(self):
        self.api_key = settings.tiingo_api_key
        self.base_url = "https://api.tiingo.com"
    
    async def get_quote(self, symbol: str):
        """Get real-time stock quote."""
        headers = {"Authorization": f"Token {self.api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/iex/{symbol}",
                headers=headers
            )
            return response.json()
    
    async def get_historical_data(self, symbol: str, start_date: str, end_date: str):
        """Get historical price data."""
        headers = {"Authorization": f"Token {self.api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tiingo/daily/{symbol}/prices",
                headers=headers,
                params={
                    "startDate": start_date,
                    "endDate": end_date
                }
            )
            return response.json()
```

## Data Source Fallback Strategy

```python
class MarketDataService:
    def __init__(self):
        self.fmp_client = FMPClient()
        self.alpha_vantage_client = AlphaVantageClient()
        self.tiingo_client = TiingoClient()
    
    async def get_stock_quote(self, symbol: str):
        """Get stock quote with fallback strategy."""
        try:
            # Try FMP first (primary)
            return await self.fmp_client.get_quote(symbol)
        except Exception as e:
            logger.warning(f"FMP failed for {symbol}: {e}")
            try:
                # Fallback to Alpha Vantage
                return await self.alpha_vantage_client.get_quote(symbol)
            except Exception as e:
                logger.warning(f"Alpha Vantage failed for {symbol}: {e}")
                try:
                    # Final fallback to Tiingo
                    return await self.tiingo_client.get_quote(symbol)
                except Exception as e:
                    logger.error(f"All data sources failed for {symbol}: {e}")
                    raise
```

## Configuration

### Environment Variables

```bash
# Primary data source
FINANCIAL_MODELING_PREP_API_KEY=your_fmp_api_key

# Secondary data sources
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
TIINGO_API_KEY=your_tiingo_api_key

# Free alternative (no API key required)
YAHOO_FINANCE_ENABLED=true
```

### Rate Limiting Considerations

- **FMP**: 10,000 requests/day (Basic plan)
- **Alpha Vantage**: 500 requests/day (Free), 1,200 requests/day (Premium)
- **Tiingo**: 1,000 requests/day (Free), 10,000 requests/day (Starter)

### Cost Optimization

1. **Cache Results**: Implement Redis caching for frequently requested data
2. **Batch Requests**: Use batch endpoints when available
3. **Smart Fallbacks**: Use free tiers for non-critical data
4. **Data Prioritization**: Use premium sources for real-time critical data

## Migration Timeline

### Week 1-2: FMP Integration
- Set up FMP API client
- Implement real-time quotes
- Add historical data endpoints
- Test and validate data quality

### Week 3-4: Alpha Vantage Integration
- Set up Alpha Vantage client
- Implement technical indicators
- Add economic data endpoints
- Set up fallback mechanisms

### Week 5-6: Tiingo Integration
- Set up Tiingo client
- Implement high-quality historical data
- Add news integration
- Complete fallback strategy

### Week 7-8: Optimization
- Implement caching strategies
- Optimize rate limiting
- Add data quality monitoring
- Performance testing

## Monitoring and Alerts

### Data Quality Monitoring
- Track API response times
- Monitor data accuracy
- Alert on API failures
- Track rate limit usage

### Cost Monitoring
- Track API usage by provider
- Monitor monthly costs
- Set up cost alerts
- Optimize usage patterns

## Conclusion

The migration from IEX Cloud to multiple alternative providers ensures:

1. **Data Continuity**: No interruption in financial data access
2. **Redundancy**: Multiple data sources prevent single points of failure
3. **Cost Optimization**: Flexible pricing options for different use cases
4. **Feature Richness**: Access to specialized data from different providers
5. **Future-Proofing**: Multiple providers reduce dependency risk

Financial Modeling Prep serves as our primary provider due to its comprehensive financial data and excellent API documentation, while Alpha Vantage and Tiingo provide valuable backup and specialized data sources.
