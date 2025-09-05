/**
 * Stock Data Hooks
 * 
 * React Query hooks for stock market data operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { stockService } from '../../services/api/stocks'
import { Stock, StockQuote, HistoricalData, FinancialMetrics, StockNews, DCFAnalysis, ComparableAnalysis, RiskAnalysis, MonteCarloSimulation } from '../../types/api'

// Query Keys
export const stockKeys = {
  all: ['stocks'] as const,
  lists: () => [...stockKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...stockKeys.lists(), filters] as const,
  details: () => [...stockKeys.all, 'detail'] as const,
  detail: (symbol: string) => [...stockKeys.details(), symbol] as const,
  quotes: () => [...stockKeys.all, 'quotes'] as const,
  quote: (symbol: string) => [...stockKeys.quotes(), symbol] as const,
  historical: (symbol: string, period: string, interval: string) => 
    [...stockKeys.all, 'historical', symbol, period, interval] as const,
  metrics: (symbol: string, period: string) => 
    [...stockKeys.all, 'metrics', symbol, period] as const,
  news: (symbol: string, params: Record<string, any>) => 
    [...stockKeys.all, 'news', symbol, params] as const,
  analysis: (symbol: string, type: string) => 
    [...stockKeys.all, 'analysis', symbol, type] as const,
  search: (query: string) => [...stockKeys.all, 'search', query] as const,
  watchlist: () => [...stockKeys.all, 'watchlist'] as const,
  market: () => [...stockKeys.all, 'market'] as const,
}

// Search stocks
export const useStockSearch = (query: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: stockKeys.search(query),
    queryFn: () => stockService.searchStocks(query),
    enabled: enabled && query.length >= 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get stock information
export const useStock = (symbol: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: stockKeys.detail(symbol),
    queryFn: () => stockService.getStock(symbol),
    enabled: enabled && !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get stock quote (real-time)
export const useStockQuote = (symbol: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: stockKeys.quote(symbol),
    queryFn: () => stockService.getQuote(symbol),
    enabled: enabled && !!symbol,
    refetchInterval: 30000, // 30 seconds
    staleTime: 0, // Always consider stale for real-time data
  })
}

// Get multiple stock quotes
export const useStockQuotes = (symbols: string[], enabled: boolean = true) => {
  return useQuery({
    queryKey: [...stockKeys.quotes(), symbols.sort()],
    queryFn: () => stockService.getQuotes(symbols),
    enabled: enabled && symbols.length > 0,
    refetchInterval: 30000, // 30 seconds
    staleTime: 0, // Always consider stale for real-time data
  })
}

// Get historical data
export const useHistoricalData = (
  symbol: string,
  period: string = '1y',
  interval: string = '1d',
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: stockKeys.historical(symbol, period, interval),
    queryFn: () => stockService.getHistoricalData(symbol, period, interval),
    enabled: enabled && !!symbol,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Get financial metrics
export const useFinancialMetrics = (
  symbol: string,
  period: 'annual' | 'quarterly' = 'annual',
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: stockKeys.metrics(symbol, period),
    queryFn: () => stockService.getFinancialMetrics(symbol, period),
    enabled: enabled && !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get stock news
export const useStockNews = (
  symbol: string,
  params: Record<string, any> = {},
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: stockKeys.news(symbol, params),
    queryFn: () => stockService.getNews(symbol, params),
    enabled: enabled && !!symbol,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get market overview
export const useMarketOverview = () => {
  return useQuery({
    queryKey: [...stockKeys.market(), 'overview'],
    queryFn: stockService.getMarketOverview,
    refetchInterval: 60000, // 1 minute
    staleTime: 0, // Always consider stale for real-time data
  })
}

// Get sector performance
export const useSectorPerformance = () => {
  return useQuery({
    queryKey: [...stockKeys.market(), 'sectors'],
    queryFn: stockService.getSectorPerformance,
    refetchInterval: 5 * 60 * 1000, // 5 minutes
    staleTime: 0, // Always consider stale for real-time data
  })
}

// Get market movers
export const useMarketMovers = () => {
  return useQuery({
    queryKey: [...stockKeys.market(), 'movers'],
    queryFn: stockService.getMarketMovers,
    refetchInterval: 2 * 60 * 1000, // 2 minutes
    staleTime: 0, // Always consider stale for real-time data
  })
}

// Get trending stocks
export const useTrendingStocks = () => {
  return useQuery({
    queryKey: [...stockKeys.market(), 'trending'],
    queryFn: stockService.getTrendingStocks,
    refetchInterval: 5 * 60 * 1000, // 5 minutes
    staleTime: 0, // Always consider stale for real-time data
  })
}

// Get similar stocks
export const useSimilarStocks = (symbol: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...stockKeys.detail(symbol), 'similar'],
    queryFn: () => stockService.getSimilarStocks(symbol),
    enabled: enabled && !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get stock recommendations
export const useStockRecommendations = (symbol: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...stockKeys.detail(symbol), 'recommendations'],
    queryFn: () => stockService.getRecommendations(symbol),
    enabled: enabled && !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get earnings calendar
export const useEarningsCalendar = (startDate: string, endDate: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...stockKeys.market(), 'earnings', startDate, endDate],
    queryFn: () => stockService.getEarningsCalendar(startDate, endDate),
    enabled: enabled && !!startDate && !!endDate,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get DCF analysis
export const useDCFAnalysis = (symbol: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: stockKeys.analysis(symbol, 'dcf'),
    queryFn: () => stockService.getDCFAnalysis(symbol),
    enabled: enabled && !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get comparable analysis
export const useComparableAnalysis = (symbol: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: stockKeys.analysis(symbol, 'comparable'),
    queryFn: () => stockService.getComparableAnalysis(symbol),
    enabled: enabled && !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get risk analysis
export const useRiskAnalysis = (symbol: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: stockKeys.analysis(symbol, 'risk'),
    queryFn: () => stockService.getRiskAnalysis(symbol),
    enabled: enabled && !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get all analysis
export const useAllAnalysis = (symbol: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: stockKeys.analysis(symbol, 'all'),
    queryFn: () => stockService.getAllAnalysis(symbol),
    enabled: enabled && !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get watchlist
export const useWatchlist = () => {
  return useQuery({
    queryKey: stockKeys.watchlist(),
    queryFn: stockService.getWatchlist,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Add to watchlist mutation
export const useAddToWatchlist = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (symbol: string) => stockService.addToWatchlist(symbol),
    onSuccess: () => {
      // Invalidate watchlist
      queryClient.invalidateQueries({ queryKey: stockKeys.watchlist() })
    },
    onError: (error) => {
      console.error('Failed to add to watchlist:', error)
    },
  })
}

// Remove from watchlist mutation
export const useRemoveFromWatchlist = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (symbol: string) => stockService.removeFromWatchlist(symbol),
    onSuccess: () => {
      // Invalidate watchlist
      queryClient.invalidateQueries({ queryKey: stockKeys.watchlist() })
    },
    onError: (error) => {
      console.error('Failed to remove from watchlist:', error)
    },
  })
}

// Create DCF analysis mutation
export const useCreateDCFAnalysis = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ symbol, assumptions }: { symbol: string; assumptions: any }) =>
      stockService.createDCFAnalysis(symbol, assumptions),
    onSuccess: (data, { symbol }) => {
      // Update DCF analysis cache
      queryClient.setQueryData(stockKeys.analysis(symbol, 'dcf'), data)
    },
    onError: (error) => {
      console.error('Failed to create DCF analysis:', error)
    },
  })
}

// Create comparable analysis mutation
export const useCreateComparableAnalysis = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ symbol, peerSymbols }: { symbol: string; peerSymbols: string[] }) =>
      stockService.createComparableAnalysis(symbol, peerSymbols),
    onSuccess: (data, { symbol }) => {
      // Update comparable analysis cache
      queryClient.setQueryData(stockKeys.analysis(symbol, 'comparable'), data)
    },
    onError: (error) => {
      console.error('Failed to create comparable analysis:', error)
    },
  })
}

// Get Monte Carlo simulation
export const useMonteCarloSimulation = (
  symbol: string,
  parameters: any,
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: [...stockKeys.analysis(symbol, 'monte-carlo'), parameters],
    queryFn: () => stockService.getMonteCarloSimulation(symbol, parameters),
    enabled: enabled && !!symbol && !!parameters,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get technical indicators
export const useTechnicalIndicators = (
  symbol: string,
  indicators: string[] = ['sma', 'ema', 'rsi', 'macd'],
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: [...stockKeys.detail(symbol), 'technical', indicators.sort()],
    queryFn: () => stockService.getTechnicalIndicators(symbol, indicators),
    enabled: enabled && !!symbol,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Get options data
export const useOptionsData = (
  symbol: string,
  expirationDate?: string,
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: [...stockKeys.detail(symbol), 'options', expirationDate],
    queryFn: () => stockService.getOptionsData(symbol, expirationDate),
    enabled: enabled && !!symbol,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get dividend history
export const useDividendHistory = (symbol: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...stockKeys.detail(symbol), 'dividends'],
    queryFn: () => stockService.getDividendHistory(symbol),
    enabled: enabled && !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get analyst estimates
export const useAnalystEstimates = (symbol: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...stockKeys.detail(symbol), 'estimates'],
    queryFn: () => stockService.getAnalystEstimates(symbol),
    enabled: enabled && !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get price targets
export const usePriceTargets = (symbol: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...stockKeys.detail(symbol), 'price-targets'],
    queryFn: () => stockService.getPriceTargets(symbol),
    enabled: enabled && !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}
