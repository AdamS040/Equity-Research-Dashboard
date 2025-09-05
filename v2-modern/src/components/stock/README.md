# Stock Analysis Components

This directory contains comprehensive stock analysis components for the equity research dashboard. These components provide detailed financial analysis, technical indicators, news feeds, and interactive charts.

## Components Overview

### Core Components

#### `StockHeader`
Displays the main stock information including:
- Stock symbol and company name
- Current price with change indicators
- Key metrics (P/E, Market Cap, Volume)
- Watchlist toggle functionality
- Share/export options

**Props:**
- `stock: Stock` - Stock information
- `quote: StockQuote` - Real-time price data
- `loading?: boolean` - Loading state
- `onShare?: () => void` - Share callback
- `onExport?: () => void` - Export callback

#### `PriceChart`
Interactive price chart with:
- Candlestick/line chart visualization
- Multiple timeframes (1D, 5D, 1M, 3M, 1Y, 5Y)
- Technical indicators overlay (MA, Bollinger Bands)
- Volume chart below price chart
- Zoom and pan functionality
- Mobile-friendly touch interactions

**Props:**
- `symbol: string` - Stock symbol
- `data: HistoricalData[]` - Historical price data
- `loading?: boolean` - Loading state
- `onTimeframeChange?: (timeframe: string) => void` - Timeframe change callback

#### `TechnicalAnalysis`
Technical analysis panel featuring:
- RSI indicator with overbought/oversold levels
- MACD with signal line
- Moving averages (20, 50, 200 day)
- Support and resistance levels
- Trading signals and recommendations

**Props:**
- `symbol: string` - Stock symbol
- `data: HistoricalData[]` - Historical price data
- `loading?: boolean` - Loading state

#### `FinancialMetrics`
Financial metrics dashboard with:
- Profitability ratios (ROE, ROA, Margins)
- Liquidity ratios (Current, Quick)
- Leverage ratios (Debt/Equity, Interest Coverage)
- Efficiency ratios (Asset Turnover, Inventory)
- Growth metrics (Revenue, Earnings growth)

**Props:**
- `symbol: string` - Stock symbol
- `data: FinancialMetrics[]` - Financial data
- `loading?: boolean` - Loading state

#### `NewsFeed`
Real-time news feed with:
- Latest news articles
- Sentiment analysis indicators
- Source credibility indicators
- Article preview with full text option
- Filtering by date and relevance

**Props:**
- `symbol: string` - Stock symbol
- `news: StockNews[]` - News articles
- `loading?: boolean` - Loading state
- `onNewsClick?: (news: StockNews) => void` - News click callback

#### `AnalysisTabs`
Tabbed interface for different analysis types:
- Smooth transitions between tabs
- Persistent state for user preferences
- URL-based navigation for sharing
- Mobile-responsive design

**Props:**
- `symbol: string` - Stock symbol
- `children: React.ReactNode` - Tab content
- `loading?: boolean` - Loading state

### Error Handling & Loading Components

#### `StockErrorBoundary`
Error boundary component for stock components:
- Catches and displays component errors
- Provides retry functionality
- Shows error details in development mode
- Custom fallback support

#### `StockLoadingState`
Loading state components:
- `StockLoadingState` - General loading state
- `StockHeaderSkeleton` - Header skeleton loader
- `ChartSkeleton` - Chart skeleton loader
- `MetricsSkeleton` - Metrics skeleton loader
- `NewsSkeleton` - News skeleton loader

## Usage Examples

### Basic Stock Analysis Page
```tsx
import { 
  StockHeader, 
  PriceChart, 
  TechnicalAnalysis, 
  FinancialMetrics, 
  NewsFeed,
  AnalysisTabs,
  StockErrorBoundary 
} from '@/components/stock'

function StockAnalysisPage({ symbol }: { symbol: string }) {
  return (
    <StockErrorBoundary>
      <div className="space-y-6">
        <StockHeader 
          stock={stock} 
          quote={quote} 
          onShare={handleShare}
          onExport={handleExport}
        />
        
        <AnalysisTabs symbol={symbol}>
          <PriceChart 
            symbol={symbol}
            data={historicalData}
            onTimeframeChange={handleTimeframeChange}
          />
        </AnalysisTabs>
      </div>
    </StockErrorBoundary>
  )
}
```

### With Error Boundary HOC
```tsx
import { withStockErrorBoundary } from '@/components/stock'

const ProtectedPriceChart = withStockErrorBoundary(PriceChart)

function MyComponent() {
  return (
    <ProtectedPriceChart 
      symbol="AAPL"
      data={data}
    />
  )
}
```

### Loading States
```tsx
import { StockLoadingState, ChartSkeleton } from '@/components/stock'

function MyComponent({ loading }: { loading: boolean }) {
  if (loading) {
    return <ChartSkeleton />
  }
  
  return <PriceChart {...props} />
}
```

## Data Requirements

### Stock Data
- `Stock` - Basic stock information
- `StockQuote` - Real-time price data
- `HistoricalData[]` - Historical price data
- `FinancialMetrics[]` - Financial ratios and metrics
- `StockNews[]` - News articles with sentiment

### API Integration
Components use React Query hooks for data fetching:
- `useStock(symbol)` - Stock information
- `useStockQuote(symbol)` - Real-time quotes
- `useHistoricalData(symbol, period, interval)` - Historical data
- `useFinancialMetrics(symbol, period)` - Financial metrics
- `useStockNews(symbol, params)` - News articles

## Styling

Components use Tailwind CSS classes and follow the design system:
- Consistent spacing and typography
- Responsive design patterns
- Dark/light theme support
- Accessibility features

## Performance Considerations

- Lazy loading of chart libraries
- Memoized calculations for technical indicators
- Efficient re-rendering with React.memo
- Optimized data fetching with React Query
- Skeleton loading states for better UX

## Accessibility

- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus management

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Responsive design for all screen sizes
- Touch-friendly interactions

## Dependencies

- React 18+
- Recharts for charting
- Heroicons for icons
- Tailwind CSS for styling
- React Query for data fetching
- React Router for navigation
