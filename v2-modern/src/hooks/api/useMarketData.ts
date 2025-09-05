import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useMarketDataWebSocket, useStockQuotesWebSocket } from '../useWebSocket'
import { stockService } from '../../services/api/stocks'
import { stockKeys } from './useStocks'

// Enhanced market overview hook with WebSocket integration
export const useMarketOverviewRealtime = () => {
  const queryClient = useQueryClient()
  const { marketData, isConnected, error: wsError } = useMarketDataWebSocket()

  const query = useQuery({
    queryKey: [...stockKeys.market(), 'overview'],
    queryFn: stockService.getMarketOverview,
    refetchInterval: 60000, // 1 minute fallback
    staleTime: 0,
  })

  // Update cache when WebSocket data arrives
  useEffect(() => {
    if (marketData && isConnected) {
      queryClient.setQueryData([...stockKeys.market(), 'overview'], marketData)
    }
  }, [marketData, isConnected, queryClient])

  return {
    ...query,
    isRealtime: isConnected,
    wsError
  }
}

// Enhanced sector performance hook with WebSocket integration
export const useSectorPerformanceRealtime = () => {
  const queryClient = useQueryClient()
  const { marketData, isConnected, error: wsError } = useMarketDataWebSocket()

  const query = useQuery({
    queryKey: [...stockKeys.market(), 'sectors'],
    queryFn: stockService.getSectorPerformance,
    refetchInterval: 5 * 60 * 1000, // 5 minutes fallback
    staleTime: 0,
  })

  // Update cache when WebSocket data arrives
  useEffect(() => {
    if (marketData?.sectors && isConnected) {
      queryClient.setQueryData([...stockKeys.market(), 'sectors'], marketData.sectors)
    }
  }, [marketData, isConnected, queryClient])

  return {
    ...query,
    isRealtime: isConnected,
    wsError
  }
}

// Enhanced market movers hook with WebSocket integration
export const useMarketMoversRealtime = () => {
  const queryClient = useQueryClient()
  const { marketData, isConnected, error: wsError } = useMarketDataWebSocket()

  const query = useQuery({
    queryKey: [...stockKeys.market(), 'movers'],
    queryFn: stockService.getMarketMovers,
    refetchInterval: 2 * 60 * 1000, // 2 minutes fallback
    staleTime: 0,
  })

  // Update cache when WebSocket data arrives
  useEffect(() => {
    if (marketData?.movers && isConnected) {
      queryClient.setQueryData([...stockKeys.market(), 'movers'], marketData.movers)
    }
  }, [marketData, isConnected, queryClient])

  return {
    ...query,
    isRealtime: isConnected,
    wsError
  }
}

// Enhanced stock quotes hook with WebSocket integration
export const useStockQuotesRealtime = (symbols: string[]) => {
  const queryClient = useQueryClient()
  const { quotes, isConnected, error: wsError } = useStockQuotesWebSocket(symbols)

  const query = useQuery({
    queryKey: [...stockKeys.quotes(), symbols.sort()],
    queryFn: () => stockService.getQuotes(symbols),
    enabled: symbols.length > 0,
    refetchInterval: 30000, // 30 seconds fallback
    staleTime: 0,
  })

  // Update cache when WebSocket data arrives
  useEffect(() => {
    if (quotes && isConnected && Object.keys(quotes).length > 0) {
      const updatedQuotes = Object.values(quotes)
      queryClient.setQueryData([...stockKeys.quotes(), symbols.sort()], updatedQuotes)
    }
  }, [quotes, isConnected, symbols, queryClient])

  return {
    ...query,
    isRealtime: isConnected,
    wsError,
    realtimeQuotes: quotes
  }
}

// Hook for market sentiment with real-time updates
export const useMarketSentimentRealtime = () => {
  const queryClient = useQueryClient()
  const { marketData, isConnected, error: wsError } = useMarketDataWebSocket()

  const query = useQuery({
    queryKey: [...stockKeys.market(), 'sentiment'],
    queryFn: async () => {
      // This would be a new API endpoint for sentiment data
      // For now, we'll use mock data
      return {
        fearGreedIndex: 45,
        vixLevel: 18.5,
        marketBreadth: {
          advancing: 1250,
          declining: 1850,
          unchanged: 400
        },
        putCallRatio: 0.85,
        highLowRatio: 0.65,
        timestamp: new Date().toISOString()
      }
    },
    refetchInterval: 5 * 60 * 1000, // 5 minutes fallback
    staleTime: 0,
  })

  // Update cache when WebSocket data arrives
  useEffect(() => {
    if (marketData?.sentiment && isConnected) {
      queryClient.setQueryData([...stockKeys.market(), 'sentiment'], marketData.sentiment)
    }
  }, [marketData, isConnected, queryClient])

  return {
    ...query,
    isRealtime: isConnected,
    wsError
  }
}

// Hook for real-time price alerts
export const usePriceAlerts = () => {
  const { marketData, isConnected, error: wsError } = useMarketDataWebSocket()

  const alerts = marketData?.alerts || []

  return {
    alerts,
    isConnected,
    wsError
  }
}

// Hook for market news with real-time updates
export const useMarketNewsRealtime = () => {
  const queryClient = useQueryClient()
  const { marketData, isConnected, error: wsError } = useMarketDataWebSocket()

  const query = useQuery({
    queryKey: [...stockKeys.market(), 'news'],
    queryFn: async () => {
      // This would be a new API endpoint for market news
      return []
    },
    refetchInterval: 10 * 60 * 1000, // 10 minutes fallback
    staleTime: 0,
  })

  // Update cache when WebSocket data arrives
  useEffect(() => {
    if (marketData?.news && isConnected) {
      queryClient.setQueryData([...stockKeys.market(), 'news'], marketData.news)
    }
  }, [marketData, isConnected, queryClient])

  return {
    ...query,
    isRealtime: isConnected,
    wsError
  }
}
