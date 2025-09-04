import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { stockApi } from '../services/api'
import { Stock, StockQuote, HistoricalData, FinancialMetrics } from '../types'

// Hook for fetching stock information
export const useStock = (symbol: string) => {
  return useQuery({
    queryKey: ['stock', symbol],
    queryFn: () => stockApi.getStock(symbol),
    enabled: !!symbol,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Hook for fetching stock quote
export const useStockQuote = (symbol: string) => {
  return useQuery({
    queryKey: ['stock-quote', symbol],
    queryFn: () => stockApi.getQuote(symbol),
    enabled: !!symbol,
    refetchInterval: 30000, // 30 seconds
  })
}

// Hook for fetching historical data
export const useHistoricalData = (symbol: string, period: string = '1y') => {
  return useQuery({
    queryKey: ['historical-data', symbol, period],
    queryFn: () => stockApi.getHistoricalData(symbol, period),
    enabled: !!symbol,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Hook for fetching financial metrics
export const useFinancialMetrics = (symbol: string) => {
  return useQuery({
    queryKey: ['financial-metrics', symbol],
    queryFn: () => stockApi.getFinancialMetrics(symbol),
    enabled: !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Hook for searching stocks
export const useStockSearch = (query: string) => {
  return useQuery({
    queryKey: ['stock-search', query],
    queryFn: () => stockApi.searchStocks(query),
    enabled: query.length >= 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
