/**
 * Legacy Stock Hooks
 * 
 * This file is kept for backward compatibility.
 * New code should use the hooks in the api/ directory.
 */

// Re-export from the new API hooks
export {
  useStock,
  useStockQuote,
  useHistoricalData,
  useFinancialMetrics,
  useStockSearch,
} from './api/useStocks'
