/**
 * Legacy Analysis Hooks
 * 
 * This file is kept for backward compatibility.
 * New code should use the hooks in the api/ directory.
 */

// Re-export from the new API hooks
export {
  useDCFAnalysis,
  useComparableAnalysis,
  useRiskAnalysis as useRiskMetrics,
  useMonteCarloSimulation,
} from './api/useStocks'
