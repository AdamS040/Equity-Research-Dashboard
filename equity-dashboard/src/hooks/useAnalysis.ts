import { useQuery } from '@tanstack/react-query'
import { analysisApi } from '../services/api'
import { DCFAnalysis, ComparableAnalysis, RiskMetrics, MonteCarloSimulation } from '../types'

// Hook for DCF Analysis
export const useDCFAnalysis = (symbol: string) => {
  return useQuery({
    queryKey: ['dcf-analysis', symbol],
    queryFn: () => analysisApi.getDCFAnalysis(symbol),
    enabled: !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Hook for Comparable Analysis
export const useComparableAnalysis = (symbol: string) => {
  return useQuery({
    queryKey: ['comparable-analysis', symbol],
    queryFn: () => analysisApi.getComparableAnalysis(symbol),
    enabled: !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Hook for Risk Metrics
export const useRiskMetrics = (symbol: string) => {
  return useQuery({
    queryKey: ['risk-metrics', symbol],
    queryFn: () => analysisApi.getRiskMetrics(symbol),
    enabled: !!symbol,
    staleTime: 30 * 60 * 1000, // 30 minutes
  })
}

// Hook for Monte Carlo Simulation
export const useMonteCarloSimulation = (symbol: string, simulations: number = 10000) => {
  return useQuery({
    queryKey: ['monte-carlo', symbol, simulations],
    queryFn: () => analysisApi.getMonteCarloSimulation(symbol, simulations),
    enabled: !!symbol,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}
