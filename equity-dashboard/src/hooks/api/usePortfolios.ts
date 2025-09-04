/**
 * Portfolio Hooks
 * 
 * React Query hooks for portfolio management operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { portfolioService } from '../../services/api/portfolios'
import { Portfolio, PortfolioHolding, PortfolioPerformance, PortfolioOptimization } from '../../types/api'

// Query Keys
export const portfolioKeys = {
  all: ['portfolios'] as const,
  lists: () => [...portfolioKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...portfolioKeys.lists(), filters] as const,
  details: () => [...portfolioKeys.all, 'detail'] as const,
  detail: (id: string) => [...portfolioKeys.details(), id] as const,
  holdings: (id: string) => [...portfolioKeys.detail(id), 'holdings'] as const,
  performance: (id: string, period: string) => [...portfolioKeys.detail(id), 'performance', period] as const,
  risk: (id: string) => [...portfolioKeys.detail(id), 'risk'] as const,
  allocation: (id: string) => [...portfolioKeys.detail(id), 'allocation'] as const,
  transactions: (id: string, params: Record<string, any>) => 
    [...portfolioKeys.detail(id), 'transactions', params] as const,
  alerts: (id: string) => [...portfolioKeys.detail(id), 'alerts'] as const,
  templates: () => [...portfolioKeys.all, 'templates'] as const,
}

// Get all portfolios
export const usePortfolios = (params: Record<string, any> = {}) => {
  return useQuery({
    queryKey: portfolioKeys.list(params),
    queryFn: () => portfolioService.getPortfolios(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get portfolio
export const usePortfolio = (portfolioId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: portfolioKeys.detail(portfolioId),
    queryFn: () => portfolioService.getPortfolio(portfolioId),
    enabled: enabled && !!portfolioId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get portfolio holdings
export const usePortfolioHoldings = (portfolioId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: portfolioKeys.holdings(portfolioId),
    queryFn: () => portfolioService.getHoldings(portfolioId),
    enabled: enabled && !!portfolioId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Get portfolio performance
export const usePortfolioPerformance = (
  portfolioId: string,
  period: string = '1y',
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: portfolioKeys.performance(portfolioId, period),
    queryFn: () => portfolioService.getPerformance(portfolioId, period),
    enabled: enabled && !!portfolioId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get portfolio risk metrics
export const usePortfolioRiskMetrics = (portfolioId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: portfolioKeys.risk(portfolioId),
    queryFn: () => portfolioService.getRiskMetrics(portfolioId),
    enabled: enabled && !!portfolioId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Get portfolio allocation
export const usePortfolioAllocation = (portfolioId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: portfolioKeys.allocation(portfolioId),
    queryFn: () => portfolioService.getAllocation(portfolioId),
    enabled: enabled && !!portfolioId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get sector allocation
export const useSectorAllocation = (portfolioId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...portfolioKeys.allocation(portfolioId), 'sectors'],
    queryFn: () => portfolioService.getSectorAllocation(portfolioId),
    enabled: enabled && !!portfolioId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get geographic allocation
export const useGeographicAllocation = (portfolioId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...portfolioKeys.allocation(portfolioId), 'geographic'],
    queryFn: () => portfolioService.getGeographicAllocation(portfolioId),
    enabled: enabled && !!portfolioId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get portfolio transactions
export const usePortfolioTransactions = (
  portfolioId: string,
  params: Record<string, any> = {},
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: portfolioKeys.transactions(portfolioId, params),
    queryFn: () => portfolioService.getTransactions(portfolioId, params),
    enabled: enabled && !!portfolioId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Get portfolio alerts
export const usePortfolioAlerts = (portfolioId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: portfolioKeys.alerts(portfolioId),
    queryFn: () => portfolioService.getAlerts(portfolioId),
    enabled: enabled && !!portfolioId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get portfolio templates
export const usePortfolioTemplates = () => {
  return useQuery({
    queryKey: portfolioKeys.templates(),
    queryFn: portfolioService.getTemplates,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Get portfolio benchmarks
export const usePortfolioBenchmarks = (portfolioId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...portfolioKeys.detail(portfolioId), 'benchmarks'],
    queryFn: () => portfolioService.getBenchmarks(portfolioId),
    enabled: enabled && !!portfolioId,
    staleTime: 60 * 60 * 1000, // 1 hour
  })
}

// Create portfolio mutation
export const useCreatePortfolio = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: portfolioService.createPortfolio,
    onSuccess: () => {
      // Invalidate portfolios list
      queryClient.invalidateQueries({ queryKey: portfolioKeys.lists() })
    },
    onError: (error) => {
      console.error('Failed to create portfolio:', error)
    },
  })
}

// Update portfolio mutation
export const useUpdatePortfolio = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, data }: { portfolioId: string; data: any }) =>
      portfolioService.updatePortfolio(portfolioId, data),
    onSuccess: (data, { portfolioId }) => {
      // Update portfolio in cache
      queryClient.setQueryData(portfolioKeys.detail(portfolioId), data)
      // Invalidate portfolios list
      queryClient.invalidateQueries({ queryKey: portfolioKeys.lists() })
    },
    onError: (error) => {
      console.error('Failed to update portfolio:', error)
    },
  })
}

// Delete portfolio mutation
export const useDeletePortfolio = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: portfolioService.deletePortfolio,
    onSuccess: (_, portfolioId) => {
      // Remove portfolio from cache
      queryClient.removeQueries({ queryKey: portfolioKeys.detail(portfolioId) })
      // Invalidate portfolios list
      queryClient.invalidateQueries({ queryKey: portfolioKeys.lists() })
    },
    onError: (error) => {
      console.error('Failed to delete portfolio:', error)
    },
  })
}

// Duplicate portfolio mutation
export const useDuplicatePortfolio = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, name }: { portfolioId: string; name: string }) =>
      portfolioService.duplicatePortfolio(portfolioId, name),
    onSuccess: () => {
      // Invalidate portfolios list
      queryClient.invalidateQueries({ queryKey: portfolioKeys.lists() })
    },
    onError: (error) => {
      console.error('Failed to duplicate portfolio:', error)
    },
  })
}

// Add holding mutation
export const useAddHolding = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, data }: { portfolioId: string; data: any }) =>
      portfolioService.addHolding(portfolioId, data),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate portfolio and holdings
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(portfolioId) })
      queryClient.invalidateQueries({ queryKey: portfolioKeys.holdings(portfolioId) })
    },
    onError: (error) => {
      console.error('Failed to add holding:', error)
    },
  })
}

// Update holding mutation
export const useUpdateHolding = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, holdingId, data }: { portfolioId: string; holdingId: string; data: any }) =>
      portfolioService.updateHolding(portfolioId, holdingId, data),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate portfolio and holdings
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(portfolioId) })
      queryClient.invalidateQueries({ queryKey: portfolioKeys.holdings(portfolioId) })
    },
    onError: (error) => {
      console.error('Failed to update holding:', error)
    },
  })
}

// Remove holding mutation
export const useRemoveHolding = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, holdingId }: { portfolioId: string; holdingId: string }) =>
      portfolioService.removeHolding(portfolioId, holdingId),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate portfolio and holdings
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(portfolioId) })
      queryClient.invalidateQueries({ queryKey: portfolioKeys.holdings(portfolioId) })
    },
    onError: (error) => {
      console.error('Failed to remove holding:', error)
    },
  })
}

// Bulk update holdings mutation
export const useBulkUpdateHoldings = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, holdings }: { portfolioId: string; holdings: any[] }) =>
      portfolioService.bulkUpdateHoldings(portfolioId, holdings),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate portfolio and holdings
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(portfolioId) })
      queryClient.invalidateQueries({ queryKey: portfolioKeys.holdings(portfolioId) })
    },
    onError: (error) => {
      console.error('Failed to bulk update holdings:', error)
    },
  })
}

// Rebalance portfolio mutation
export const useRebalancePortfolio = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, targetAllocation }: { portfolioId: string; targetAllocation: Record<string, number> }) =>
      portfolioService.rebalancePortfolio(portfolioId, targetAllocation),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate portfolio and holdings
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(portfolioId) })
      queryClient.invalidateQueries({ queryKey: portfolioKeys.holdings(portfolioId) })
    },
    onError: (error) => {
      console.error('Failed to rebalance portfolio:', error)
    },
  })
}

// Get portfolio optimization
export const usePortfolioOptimization = (
  portfolioId: string,
  constraints: any,
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: [...portfolioKeys.detail(portfolioId), 'optimization', constraints],
    queryFn: () => portfolioService.getOptimization(portfolioId, constraints),
    enabled: enabled && !!portfolioId && !!constraints,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Get efficient frontier
export const useEfficientFrontier = (portfolioId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...portfolioKeys.detail(portfolioId), 'efficient-frontier'],
    queryFn: () => portfolioService.getEfficientFrontier(portfolioId),
    enabled: enabled && !!portfolioId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Get correlation matrix
export const useCorrelationMatrix = (portfolioId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...portfolioKeys.detail(portfolioId), 'correlation'],
    queryFn: () => portfolioService.getCorrelationMatrix(portfolioId),
    enabled: enabled && !!portfolioId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Get attribution analysis
export const useAttributionAnalysis = (
  portfolioId: string,
  period: string = '1y',
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: [...portfolioKeys.detail(portfolioId), 'attribution', period],
    queryFn: () => portfolioService.getAttributionAnalysis(portfolioId, period),
    enabled: enabled && !!portfolioId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Add transaction mutation
export const useAddTransaction = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, transaction }: { portfolioId: string; transaction: any }) =>
      portfolioService.addTransaction(portfolioId, transaction),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate portfolio and transactions
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(portfolioId) })
      queryClient.invalidateQueries({ queryKey: portfolioKeys.transactions(portfolioId, {}) })
    },
    onError: (error) => {
      console.error('Failed to add transaction:', error)
    },
  })
}

// Update transaction mutation
export const useUpdateTransaction = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, transactionId, data }: { portfolioId: string; transactionId: string; data: any }) =>
      portfolioService.updateTransaction(portfolioId, transactionId, data),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate portfolio and transactions
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(portfolioId) })
      queryClient.invalidateQueries({ queryKey: portfolioKeys.transactions(portfolioId, {}) })
    },
    onError: (error) => {
      console.error('Failed to update transaction:', error)
    },
  })
}

// Delete transaction mutation
export const useDeleteTransaction = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, transactionId }: { portfolioId: string; transactionId: string }) =>
      portfolioService.deleteTransaction(portfolioId, transactionId),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate portfolio and transactions
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(portfolioId) })
      queryClient.invalidateQueries({ queryKey: portfolioKeys.transactions(portfolioId, {}) })
    },
    onError: (error) => {
      console.error('Failed to delete transaction:', error)
    },
  })
}

// Create alert mutation
export const useCreatePortfolioAlert = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, alert }: { portfolioId: string; alert: any }) =>
      portfolioService.createAlert(portfolioId, alert),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate alerts
      queryClient.invalidateQueries({ queryKey: portfolioKeys.alerts(portfolioId) })
    },
    onError: (error) => {
      console.error('Failed to create alert:', error)
    },
  })
}

// Update alert mutation
export const useUpdatePortfolioAlert = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, alertId, data }: { portfolioId: string; alertId: string; data: any }) =>
      portfolioService.updateAlert(portfolioId, alertId, data),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate alerts
      queryClient.invalidateQueries({ queryKey: portfolioKeys.alerts(portfolioId) })
    },
    onError: (error) => {
      console.error('Failed to update alert:', error)
    },
  })
}

// Delete alert mutation
export const useDeletePortfolioAlert = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, alertId }: { portfolioId: string; alertId: string }) =>
      portfolioService.deleteAlert(portfolioId, alertId),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate alerts
      queryClient.invalidateQueries({ queryKey: portfolioKeys.alerts(portfolioId) })
    },
    onError: (error) => {
      console.error('Failed to delete alert:', error)
    },
  })
}

// Set benchmark mutation
export const useSetBenchmark = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ portfolioId, benchmarkSymbol }: { portfolioId: string; benchmarkSymbol: string }) =>
      portfolioService.setBenchmark(portfolioId, benchmarkSymbol),
    onSuccess: (_, { portfolioId }) => {
      // Invalidate benchmarks and performance
      queryClient.invalidateQueries({ queryKey: [...portfolioKeys.detail(portfolioId), 'benchmarks'] })
      queryClient.invalidateQueries({ queryKey: portfolioKeys.performance(portfolioId, '1y') })
    },
    onError: (error) => {
      console.error('Failed to set benchmark:', error)
    },
  })
}

// Compare portfolios
export const useComparePortfolios = (portfolioIds: string[], enabled: boolean = true) => {
  return useQuery({
    queryKey: [...portfolioKeys.all, 'compare', portfolioIds.sort()],
    queryFn: () => portfolioService.comparePortfolios(portfolioIds),
    enabled: enabled && portfolioIds.length > 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
