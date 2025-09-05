# API Services Documentation

This directory contains the complete RESTful API integration for the Equity Research Dashboard, built with TypeScript and React Query.

## 🏗️ Architecture

### Base API Client (`base.ts`)
- **Request/Response Interceptors**: Automatic token management and error handling
- **Retry Logic**: Exponential backoff for failed requests
- **Timeout Management**: Configurable request timeouts
- **Error Handling**: Comprehensive error types and handling

### Service Layer
- **Authentication Service** (`auth.ts`): User authentication and session management
- **Stock Service** (`stocks.ts`): Market data, quotes, and analysis
- **Portfolio Service** (`portfolios.ts`): Portfolio management and optimization
- **Reports Service** (`reports.ts`): Report generation and management

### React Query Integration
- **Custom Hooks**: Type-safe hooks for all API endpoints
- **Caching Strategies**: Optimized caching with proper stale times
- **Background Refetching**: Automatic data synchronization
- **Optimistic Updates**: Immediate UI updates for better UX

## 🚀 Quick Start

### 1. Import Services
```typescript
import { authService, stockService, portfolioService } from '@/services/api'
```

### 2. Use React Query Hooks
```typescript
import { useStock, usePortfolios, useCurrentUser } from '@/hooks/api'

function StockComponent() {
  const { data: stock, isLoading, error } = useStock('AAPL')
  const { data: user } = useCurrentUser()
  
  if (isLoading) return <Spinner />
  if (error) return <ErrorDisplay error={error} />
  
  return <div>{stock?.name}</div>
}
```

### 3. Handle Mutations
```typescript
import { useCreatePortfolio, useAddToWatchlist } from '@/hooks/api'

function PortfolioForm() {
  const createPortfolio = useCreatePortfolio()
  
  const handleSubmit = async (data) => {
    try {
      await createPortfolio.mutateAsync(data)
      // Success handled automatically
    } catch (error) {
      // Error handled by the hook
    }
  }
}
```

## 📡 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Refresh token
- `GET /auth/me` - Get current user
- `PATCH /auth/me` - Update profile
- `DELETE /auth/me` - Delete account

### Stocks
- `GET /stocks/search` - Search stocks
- `GET /stocks/{symbol}` - Get stock info
- `GET /stocks/{symbol}/quote` - Get real-time quote
- `GET /stocks/{symbol}/historical` - Get historical data
- `GET /stocks/{symbol}/metrics` - Get financial metrics
- `GET /stocks/{symbol}/news` - Get stock news
- `GET /stocks/{symbol}/analysis/dcf` - DCF analysis
- `GET /stocks/{symbol}/analysis/comparable` - Comparable analysis
- `GET /stocks/{symbol}/analysis/risk` - Risk analysis

### Portfolios
- `GET /portfolios` - Get all portfolios
- `POST /portfolios` - Create portfolio
- `GET /portfolios/{id}` - Get portfolio
- `PATCH /portfolios/{id}` - Update portfolio
- `DELETE /portfolios/{id}` - Delete portfolio
- `GET /portfolios/{id}/holdings` - Get holdings
- `POST /portfolios/{id}/holdings` - Add holding
- `GET /portfolios/{id}/performance` - Get performance
- `POST /portfolios/{id}/optimize` - Portfolio optimization

### Reports
- `GET /reports` - Get all reports
- `POST /reports` - Create report
- `GET /reports/{id}` - Get report
- `PATCH /reports/{id}` - Update report
- `DELETE /reports/{id}` - Delete report
- `POST /reports/{id}/generate` - Generate report
- `GET /reports/{id}/export` - Export report

## 🔧 Configuration

### Environment Variables
```env
VITE_API_BASE_URL=http://localhost:5000/api
```

### Query Client Configuration
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        if (error?.status === 401 || error?.status === 403) return false
        return failureCount < 3
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
})
```

## 🎯 Caching Strategies

### Real-time Data (30s refresh)
- Stock quotes
- Market overview
- Portfolio values

### Historical Data (10min stale)
- Historical price data
- Financial metrics
- Analysis results

### Static Data (1hr stale)
- Stock information
- User profiles
- Report templates

## 🛡️ Error Handling

### Global Error Boundary
```typescript
import { ErrorBoundary } from '@/components/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <YourApp />
    </ErrorBoundary>
  )
}
```

### API Error Display
```typescript
import { ErrorDisplay } from '@/components/ErrorDisplay'

function Component() {
  const { data, error } = useStock('AAPL')
  
  if (error) {
    return <ErrorDisplay error={error} onRetry={() => refetch()} />
  }
}
```

### Error Types
- **ApiError**: HTTP errors with status codes
- **NetworkError**: Connection issues
- **ValidationError**: Input validation failures
- **AuthenticationError**: Auth-related errors

## 🔐 Authentication Flow

### 1. Login
```typescript
const login = useLogin()
await login.mutateAsync({ email, password })
```

### 2. Protected Routes
```typescript
import { ProtectedRoute } from '@/components/ProtectedRoute'

<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

### 3. Token Management
- Automatic token refresh
- Secure token storage
- Session persistence

## 📊 TypeScript Integration

### Comprehensive Types
```typescript
import { Stock, Portfolio, Report, ApiResponse } from '@/types/api'

// All API responses are fully typed
const { data }: { data: ApiResponse<Stock> } = useStock('AAPL')
```

### Type Safety
- Request/response types
- Error types
- Hook return types
- Service method signatures

## 🧪 Testing

### Mock Services
```typescript
import { vi } from 'vitest'

vi.mock('@/services/api', () => ({
  stockService: {
    getStock: vi.fn(),
    getQuote: vi.fn(),
  },
}))
```

### Test Hooks
```typescript
import { renderHook } from '@testing-library/react'
import { useStock } from '@/hooks/api/useStocks'

test('should fetch stock data', async () => {
  const { result } = renderHook(() => useStock('AAPL'))
  // Test implementation
})
```

## 🚀 Performance Optimizations

### Request Deduplication
- Automatic request deduplication
- Shared cache across components
- Background refetching

### Optimistic Updates
```typescript
const updatePortfolio = useUpdatePortfolio()

updatePortfolio.mutate(data, {
  onMutate: async (newData) => {
    // Optimistically update UI
    await queryClient.cancelQueries(['portfolio', id])
    const previousData = queryClient.getQueryData(['portfolio', id])
    queryClient.setQueryData(['portfolio', id], newData)
    return { previousData }
  },
  onError: (err, newData, context) => {
    // Rollback on error
    queryClient.setQueryData(['portfolio', id], context.previousData)
  },
})
```

### Pagination
```typescript
const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: ['reports'],
  queryFn: ({ pageParam = 1 }) => reportsService.getReports({ page: pageParam }),
  getNextPageParam: (lastPage) => lastPage.hasNext ? lastPage.page + 1 : undefined,
})
```

## 🔄 Migration Guide

### From Legacy API
1. Update imports:
   ```typescript
   // Old
   import { stockApi } from '@/services/api'
   
   // New
   import { useStock } from '@/hooks/api/useStocks'
   ```

2. Replace direct API calls with hooks:
   ```typescript
   // Old
   const stock = await stockApi.getStock('AAPL')
   
   // New
   const { data: stock } = useStock('AAPL')
   ```

3. Handle loading and error states:
   ```typescript
   const { data, isLoading, error } = useStock('AAPL')
   
   if (isLoading) return <Spinner />
   if (error) return <ErrorDisplay error={error} />
   ```

## 📚 Additional Resources

- [React Query Documentation](https://tanstack.com/query/latest)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [REST API Best Practices](https://restfulapi.net/)
- [Error Handling Patterns](https://kentcdodds.com/blog/use-react-error-boundary-to-handle-errors-in-react)
