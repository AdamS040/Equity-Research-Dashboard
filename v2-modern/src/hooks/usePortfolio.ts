/**
 * Legacy Portfolio Hooks
 * 
 * This file is kept for backward compatibility.
 * New code should use the hooks in the api/ directory.
 */

// Re-export from the new API hooks
export {
  usePortfolios,
  usePortfolio,
  useCreatePortfolio,
  useUpdatePortfolio,
  useDeletePortfolio,
} from './api/usePortfolios'
