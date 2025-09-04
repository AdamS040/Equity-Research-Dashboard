import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { portfolioApi } from '../services/api'
import { Portfolio } from '../types'

// Hook for fetching all portfolios
export const usePortfolios = () => {
  return useQuery({
    queryKey: ['portfolios'],
    queryFn: portfolioApi.getPortfolios,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Hook for fetching a single portfolio
export const usePortfolio = (id: string) => {
  return useQuery({
    queryKey: ['portfolio', id],
    queryFn: () => portfolioApi.getPortfolio(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Hook for creating a portfolio
export const useCreatePortfolio = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: portfolioApi.createPortfolio,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolios'] })
    },
  })
}

// Hook for updating a portfolio
export const useUpdatePortfolio = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      portfolioApi.updatePortfolio(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['portfolios'] })
      queryClient.invalidateQueries({ queryKey: ['portfolio', id] })
    },
  })
}

// Hook for deleting a portfolio
export const useDeletePortfolio = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: portfolioApi.deletePortfolio,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolios'] })
    },
  })
}
