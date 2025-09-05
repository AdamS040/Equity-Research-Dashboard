/**
 * Enhanced React Query Configuration
 * 
 * Advanced caching strategies and query optimization
 * for the equity research dashboard
 */

import { QueryClient, QueryKey, QueryFunction, UseQueryOptions } from '@tanstack/react-query'
import { cacheManager } from '../cache/CacheManager'

// Cache time configurations based on data type
export const CACHE_TIMES = {
  // Real-time data (30 seconds)
  REALTIME: 30 * 1000,
  // Market data (1 minute)
  MARKET: 60 * 1000,
  // Stock quotes (30 seconds)
  QUOTES: 30 * 1000,
  // Historical data (10 minutes)
  HISTORICAL: 10 * 60 * 1000,
  // Financial metrics (1 hour)
  METRICS: 60 * 60 * 1000,
  // Static data (24 hours)
  STATIC: 24 * 60 * 60 * 1000,
  // User data (5 minutes)
  USER: 5 * 60 * 1000,
  // Reports (30 minutes)
  REPORTS: 30 * 60 * 1000
} as const

// Stale time configurations
export const STALE_TIMES = {
  REALTIME: 0, // Always consider stale
  MARKET: 30 * 1000, // 30 seconds
  QUOTES: 15 * 1000, // 15 seconds
  HISTORICAL: 5 * 60 * 1000, // 5 minutes
  METRICS: 30 * 60 * 1000, // 30 minutes
  STATIC: 12 * 60 * 60 * 1000, // 12 hours
  USER: 2 * 60 * 1000, // 2 minutes
  REPORTS: 15 * 60 * 1000 // 15 minutes
} as const

// Retry configurations
export const RETRY_CONFIG = {
  // Don't retry on auth errors
  auth: (failureCount: number, error: any) => {
    if (error?.status === 401 || error?.status === 403) return false
    return failureCount < 2
  },
  // Retry network errors more aggressively
  network: (failureCount: number, error: any) => {
    if (error?.status >= 400 && error?.status < 500) return false
    return failureCount < 3
  },
  // Standard retry for most queries
  standard: (failureCount: number, error: any) => {
    if (error?.status === 401 || error?.status === 403) return false
    return failureCount < 3
  }
} as const

// Enhanced query function with caching
export function createCachedQueryFunction<T>(
  queryFn: QueryFunction<T>,
  cacheLevel: 'memory' | 'localStorage' | 'indexedDB' = 'memory',
  ttl?: number
): QueryFunction<T> {
  return async (context) => {
    const queryKey = context.queryKey.join(':')
    
    // Try to get from cache first
    const cached = await cacheManager.get<T>(queryKey, cacheLevel)
    if (cached) {
      return cached
    }

    // Fetch fresh data
    const data = await queryFn(context)
    
    // Cache the result
    await cacheManager.set(queryKey, data, cacheLevel, ttl)
    
    return data
  }
}

// Query key factories with consistent structure
export const queryKeys = {
  // Stock-related queries
  stocks: {
    all: ['stocks'] as const,
    lists: () => [...queryKeys.stocks.all, 'list'] as const,
    list: (filters: Record<string, any>) => [...queryKeys.stocks.lists(), filters] as const,
    details: () => [...queryKeys.stocks.all, 'detail'] as const,
    detail: (symbol: string) => [...queryKeys.stocks.details(), symbol] as const,
    quotes: () => [...queryKeys.stocks.all, 'quotes'] as const,
    quote: (symbol: string) => [...queryKeys.stocks.quotes(), symbol] as const,
    historical: (symbol: string, period: string, interval: string) => 
      [...queryKeys.stocks.all, 'historical', symbol, period, interval] as const,
    metrics: (symbol: string, period: string) => 
      [...queryKeys.stocks.all, 'metrics', symbol, period] as const,
    news: (symbol: string, params: Record<string, any>) => 
      [...queryKeys.stocks.all, 'news', symbol, params] as const,
    analysis: (symbol: string, type: string) => 
      [...queryKeys.stocks.all, 'analysis', symbol, type] as const,
    search: (query: string) => [...queryKeys.stocks.all, 'search', query] as const,
    watchlist: () => [...queryKeys.stocks.all, 'watchlist'] as const,
    market: () => [...queryKeys.stocks.all, 'market'] as const,
  },
  
  // Portfolio-related queries
  portfolios: {
    all: ['portfolios'] as const,
    lists: () => [...queryKeys.portfolios.all, 'list'] as const,
    list: (userId: string) => [...queryKeys.portfolios.lists(), userId] as const,
    details: () => [...queryKeys.portfolios.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.portfolios.details(), id] as const,
    performance: (id: string, period: string) => 
      [...queryKeys.portfolios.all, 'performance', id, period] as const,
    holdings: (id: string) => [...queryKeys.portfolios.all, 'holdings', id] as const,
    transactions: (id: string, params: Record<string, any>) => 
      [...queryKeys.portfolios.all, 'transactions', id, params] as const,
  },
  
  // Report-related queries
  reports: {
    all: ['reports'] as const,
    lists: () => [...queryKeys.reports.all, 'list'] as const,
    list: (userId: string) => [...queryKeys.reports.lists(), userId] as const,
    details: () => [...queryKeys.reports.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.reports.details(), id] as const,
    templates: () => [...queryKeys.reports.all, 'templates'] as const,
    generated: (id: string) => [...queryKeys.reports.all, 'generated', id] as const,
  },
  
  // User-related queries
  users: {
    all: ['users'] as const,
    current: () => [...queryKeys.users.all, 'current'] as const,
    profile: (id: string) => [...queryKeys.users.all, 'profile', id] as const,
    preferences: (id: string) => [...queryKeys.users.all, 'preferences', id] as const,
  }
} as const

// Enhanced query client with optimized defaults
export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Default retry configuration
        retry: RETRY_CONFIG.standard,
        
        // Default stale time
        staleTime: STALE_TIMES.MARKET,
        
        // Default cache time
        gcTime: CACHE_TIMES.MARKET,
        
        // Don't refetch on window focus for better UX
        refetchOnWindowFocus: false,
        
        // Don't refetch on reconnect by default
        refetchOnReconnect: false,
        
        // Network mode for offline support
        networkMode: 'online',
        
        // Error handling
        throwOnError: false,
        
        // Placeholder data for better UX
        placeholderData: (previousData) => previousData,
      },
      mutations: {
        // Don't retry mutations by default
        retry: false,
        
        // Network mode
        networkMode: 'online',
      },
    },
    
    // Global error handler
    mutationCache: {
      onError: (error, variables, context, mutation) => {
        console.error('Mutation error:', error)
        // Could integrate with error tracking service here
      },
    },
    
    // Query cache configuration
    queryCache: {
      onError: (error, query) => {
        console.error('Query error:', error)
        // Could integrate with error tracking service here
      },
    },
  })
}

// Query options factory for different data types
export function createQueryOptions<T>(
  queryKey: QueryKey,
  queryFn: QueryFunction<T>,
  options: {
    cacheTime?: number
    staleTime?: number
    retry?: boolean | ((failureCount: number, error: any) => boolean)
    refetchInterval?: number | false
    enabled?: boolean
    cacheLevel?: 'memory' | 'localStorage' | 'indexedDB'
    ttl?: number
  } = {}
): UseQueryOptions<T> {
  const {
    cacheTime = CACHE_TIMES.MARKET,
    staleTime = STALE_TIMES.MARKET,
    retry = RETRY_CONFIG.standard,
    refetchInterval = false,
    enabled = true,
    cacheLevel = 'memory',
    ttl
  } = options

  return {
    queryKey,
    queryFn: createCachedQueryFunction(queryFn, cacheLevel, ttl),
    cacheTime,
    staleTime,
    retry,
    refetchInterval,
    enabled,
    // Optimistic updates
    placeholderData: (previousData) => previousData,
    // Error handling
    throwOnError: false,
  }
}

// Prefetch utilities
export function createPrefetchUtils(queryClient: QueryClient) {
  return {
    // Prefetch stock data
    prefetchStock: (symbol: string) => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.stocks.detail(symbol),
        queryFn: () => import('../../services/api/stocks').then(module => 
          module.stockService.getStock(symbol)
        ),
        staleTime: STALE_TIMES.STATIC,
      })
    },
    
    // Prefetch portfolio data
    prefetchPortfolio: (id: string) => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.portfolios.detail(id),
        queryFn: () => import('../../services/api/portfolios').then(module => 
          module.portfolioService.getPortfolio(id)
        ),
        staleTime: STALE_TIMES.USER,
      })
    },
    
    // Prefetch market data
    prefetchMarketData: () => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.stocks.market(),
        queryFn: () => import('../../services/api/stocks').then(module => 
          module.stockService.getMarketOverview()
        ),
        staleTime: STALE_TIMES.MARKET,
      })
    },
  }
}

// Global query client instance
export const queryClient = createQueryClient()
export const prefetchUtils = createPrefetchUtils(queryClient)
