/**
 * API Services Index
 * 
 * Centralized export of all API services and utilities
 */

export { BaseApiClient, apiClient } from './base'
export { AuthService, authService } from './auth'
export { StockService, stockService } from './stocks'
export { PortfolioService, portfolioService } from './portfolios'
export { ReportsService, reportsService } from './reports'

// Re-export types for convenience
export type {
  ApiResponse,
  PaginatedResponse,
  ApiError,
  RequestParams,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  UserPreferences,
  Stock,
  StockQuote,
  HistoricalData,
  FinancialMetrics,
  StockNews,
  StockSearchResult,
  Portfolio,
  PortfolioHolding,
  PortfolioPerformance,
  PortfolioOptimization,
  Report,
  ReportContent,
  ReportMetadata,
} from '../../types/api'
