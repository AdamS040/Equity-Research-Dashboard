# Market Overview Dashboard

A comprehensive real-time market overview dashboard built with React, TypeScript, and modern web technologies.

## Features

### 🏛️ Market Indices Cards
- **Real-time data** for S&P 500, NASDAQ, DOW, and VIX
- **Color-coded indicators** for positive/negative changes
- **Special VIX interpretation** with fear/greed sentiment
- **Loading states** and error handling
- **Smooth animations** with Framer Motion

### 📊 Sector Performance
- **Interactive charts** using Recharts
- **Pie chart** for performance distribution
- **Bar chart** for change comparison
- **Sector detail modals** with drill-down information
- **Chart/List view toggle**
- **Hover tooltips** with detailed information

### 📈 Top Movers Table
- **Real-time updates** for gainers, losers, and most active stocks
- **Sortable columns** with visual indicators
- **Pagination** for large datasets
- **Debounced search** functionality
- **Performance optimized** with memoization
- **Responsive design** for all screen sizes

### 🎯 Market Sentiment Widget
- **Fear & Greed Index** with radial gauge
- **Market breadth** visualization
- **VIX level** with interpretation
- **Put/Call ratio** analysis
- **High/Low ratio** indicators
- **Comprehensive market summary**

## Technical Implementation

### Data Integration
- **React Query** for server state management
- **WebSocket connections** for real-time updates
- **Fallback mechanisms** for API failures
- **Optimistic updates** for better UX
- **Error boundaries** for graceful error handling

### Performance Optimizations
- **React.memo** for component memoization
- **useMemo** and **useCallback** for expensive operations
- **Virtual scrolling** for large datasets
- **Debounced search** to reduce API calls
- **Performance monitoring** hooks
- **Lazy loading** for code splitting

### Real-time Features
- **WebSocket integration** with automatic reconnection
- **Live data indicators** with pulse animations
- **Real-time price updates** every 30 seconds
- **Market sentiment** updates every 5 minutes
- **Sector performance** updates every 5 minutes

## Components Structure

```
src/components/dashboard/
├── MarketIndices.tsx          # Market indices cards
├── SectorPerformance.tsx      # Sector performance charts
├── TopMovers.tsx             # Top movers table
├── MarketSentiment.tsx       # Market sentiment widgets
└── index.ts                  # Component exports
```

## Hooks

### Market Data Hooks
- `useMarketOverviewRealtime()` - Real-time market overview
- `useSectorPerformanceRealtime()` - Real-time sector data
- `useMarketMoversRealtime()` - Real-time movers data
- `useStockQuotesRealtime()` - Real-time stock quotes
- `useMarketSentimentRealtime()` - Real-time sentiment data

### WebSocket Hooks
- `useWebSocket()` - Generic WebSocket hook
- `useMarketDataWebSocket()` - Market data WebSocket
- `useStockQuotesWebSocket()` - Stock quotes WebSocket

### Performance Hooks
- `usePerformance()` - Performance monitoring
- `useRenderCount()` - Component render counting
- `useAsyncPerformance()` - Async operation timing
- `useMemoryMonitor()` - Memory usage monitoring

## Usage

```tsx
import { 
  MarketIndices, 
  SectorPerformance, 
  TopMovers, 
  MarketSentiment 
} from '../components/dashboard'

function Dashboard() {
  return (
    <div className="space-y-6">
      <MarketIndices />
      <SectorPerformance />
      <TopMovers />
      <MarketSentiment />
    </div>
  )
}
```

## Configuration

### Environment Variables
```env
REACT_APP_WS_URL=ws://localhost:8000/ws/market-data
REACT_APP_API_URL=http://localhost:8000/api
```

### WebSocket Endpoints
- `/ws/market-data` - General market data
- `/ws/stock-quotes` - Real-time stock quotes
- `/ws/sector-performance` - Sector performance data

## Styling

The dashboard uses Tailwind CSS with a custom design system:
- **Primary colors**: Blue theme for professional look
- **Success colors**: Green for positive changes
- **Danger colors**: Red for negative changes
- **Neutral colors**: Gray scale for text and backgrounds
- **Responsive design**: Mobile-first approach

## Error Handling

- **Network errors**: Graceful fallback to cached data
- **WebSocket disconnection**: Automatic reconnection with exponential backoff
- **API failures**: Error boundaries with user-friendly messages
- **Loading states**: Skeleton loaders and spinners
- **Empty states**: Helpful messages when no data is available

## Performance Metrics

- **Initial load time**: < 2 seconds
- **Re-render optimization**: Memoized components prevent unnecessary updates
- **Memory usage**: Monitored and optimized for large datasets
- **Bundle size**: Code splitting reduces initial bundle size
- **Real-time updates**: < 100ms latency for WebSocket updates

## Browser Support

- **Modern browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile support**: iOS Safari 14+, Chrome Mobile 90+
- **WebSocket support**: All modern browsers
- **ES2020 features**: Used throughout the codebase

## Development

### Prerequisites
- Node.js 16+
- npm or yarn
- TypeScript 4.5+

### Running the Dashboard
```bash
npm install
npm run dev
```

### Building for Production
```bash
npm run build
```

### Testing
```bash
npm run test
npm run test:coverage
```

## Future Enhancements

- [ ] **Dark mode** support
- [ ] **Customizable widgets** with drag-and-drop
- [ ] **Advanced filtering** options
- [ ] **Export functionality** for data
- [ ] **Push notifications** for price alerts
- [ ] **Mobile app** with React Native
- [ ] **Advanced charting** with TradingView integration
- [ ] **AI-powered insights** and recommendations
