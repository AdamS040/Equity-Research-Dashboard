/**
 * Portfolio Types
 * 
 * Extended type definitions for portfolio management system
 */

import { Portfolio, PortfolioHolding, PortfolioPerformance, PortfolioOptimization } from './api'

// Extended Portfolio Types
export interface PortfolioMetrics {
  totalValue: number
  totalCost: number
  totalReturn: number
  totalReturnPercent: number
  dayChange: number
  dayChangePercent: number
  sharpeRatio: number
  beta: number
  var95: number
  var99: number
  maxDrawdown: number
  volatility: number
}

export interface AssetAllocation {
  symbol: string
  name: string
  value: number
  weight: number
  sector?: string
  color: string
}

export interface SectorAllocation {
  sector: string
  value: number
  weight: number
  holdings: string[]
  color: string
}

export interface PerformanceData {
  date: string
  portfolioValue: number
  benchmarkValue: number
  returns: number
  cumulativeReturns: number
  drawdown: number
}

export interface RiskMetrics {
  var95: number
  var99: number
  expectedShortfall: number
  maxDrawdown: number
  volatility: number
  sharpeRatio: number
  beta: number
  alpha: number
  trackingError: number
  informationRatio: number
}

export interface CorrelationMatrix {
  symbols: string[]
  matrix: number[][]
}

export interface StressTestScenario {
  name: string
  description: string
  impact: number
  probability: number
  portfolioImpact: number
}

export interface OptimizationResult {
  method: 'max_sharpe' | 'min_volatility' | 'target_return'
  weights: Record<string, number>
  expectedReturn: number
  expectedRisk: number
  sharpeRatio: number
  transactionCosts: number
}

export interface EfficientFrontierPoint {
  return: number
  risk: number
  weights: Record<string, number>
  sharpeRatio: number
}

export interface RebalancingRecommendation {
  symbol: string
  currentWeight: number
  targetWeight: number
  currentShares: number
  targetShares: number
  action: 'buy' | 'sell' | 'hold'
  sharesToTrade: number
  estimatedCost: number
  priority: 'high' | 'medium' | 'low'
}

export interface PositionFormData {
  symbol: string
  shares: number
  purchasePrice: number
  purchaseDate: string
  commission: number
  fees: number
}

export interface StockSearchResult {
  symbol: string
  name: string
  exchange: string
  price: number
  change: number
  changePercent: number
  marketCap: number
  sector: string
}

export interface HoldingsTableFilters {
  search: string
  sector: string
  minWeight: number
  maxWeight: number
  minReturn: number
  maxReturn: number
  sortBy: 'symbol' | 'value' | 'weight' | 'return' | 'returnPercent'
  sortOrder: 'asc' | 'desc'
}

export interface PerformanceChartFilters {
  period: '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | 'all'
  benchmark: string
  showDrawdown: boolean
  showRollingReturns: boolean
}

export interface RiskAnalysisFilters {
  confidenceLevel: 95 | 99
  timeHorizon: number
  stressTestScenarios: string[]
  showCorrelationMatrix: boolean
}

export interface OptimizationFilters {
  method: 'max_sharpe' | 'min_volatility' | 'target_return'
  targetReturn?: number
  maxRisk?: number
  constraints: {
    maxWeight: number
    minWeight: number
    sectorLimits: Record<string, number>
    excludeSymbols: string[]
  }
}

// Re-export API types for convenience
export type {
  Portfolio,
  PortfolioHolding,
  PortfolioPerformance,
  PortfolioOptimization,
} from './api'
