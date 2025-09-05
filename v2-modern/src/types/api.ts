/**
 * API Types
 * 
 * Comprehensive type definitions for API requests, responses, and error handling
 */

// Base API Response
export interface ApiResponse<T = any> {
  data: T
  success: boolean
  message?: string
  timestamp: string
}

// Paginated API Response
export interface PaginatedResponse<T = any> {
  data: T[]
  total: number
  page: number
  limit: number
  hasNext: boolean
  hasPrev: boolean
}

// API Error
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string,
    public details?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// Request/Response Types
export interface RequestParams {
  page?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
  search?: string
  [key: string]: any
}

// Authentication Types
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  firstName: string
  lastName: string
}

export interface AuthResponse {
  user: User
  token: string
  refreshToken: string
  expiresIn: number
}

export interface RefreshTokenRequest {
  refreshToken: string
}

export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  role: 'user' | 'admin' | 'analyst'
  isActive: boolean
  createdAt: string
  updatedAt: string
  preferences?: UserPreferences
}

export interface UserPreferences {
  theme: 'light' | 'dark'
  currency: string
  timezone: string
  notifications: NotificationSettings
  dashboard: DashboardSettings
}

export interface NotificationSettings {
  email: boolean
  push: boolean
  priceAlerts: boolean
  newsAlerts: boolean
  reportAlerts: boolean
}

export interface DashboardSettings {
  defaultView: 'overview' | 'portfolio' | 'research'
  widgets: string[]
  layout: 'grid' | 'list'
}

// Stock Data Types
export interface Stock {
  symbol: string
  name: string
  exchange: string
  sector: string
  industry: string
  marketCap: number
  description: string
  website: string
  logo: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface StockQuote {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume: number
  avgVolume: number
  high: number
  low: number
  open: number
  previousClose: number
  marketCap: number
  pe: number
  eps: number
  dividend: number
  dividendYield: number
  timestamp: string
}

export interface HistoricalData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  adjustedClose: number
}

export interface FinancialMetrics {
  symbol: string
  period: 'annual' | 'quarterly'
  year: number
  quarter?: number
  revenue: number
  netIncome: number
  totalAssets: number
  totalLiabilities: number
  equity: number
  operatingCashFlow: number
  freeCashFlow: number
  roe: number
  roa: number
  debtToEquity: number
  currentRatio: number
  grossMargin: number
  operatingMargin: number
  netMargin: number
  eps: number
  pe: number
  pb: number
  ps: number
  evEbitda: number
}

export interface StockNews {
  id: string
  symbol: string
  title: string
  summary: string
  content: string
  source: string
  url: string
  publishedAt: string
  sentiment: 'positive' | 'negative' | 'neutral'
  relevance: number
}

export interface StockSearchResult {
  symbol: string
  name: string
  exchange: string
  type: 'stock' | 'etf' | 'index' | 'crypto'
  marketCap?: number
}

// Portfolio Types
export interface Portfolio {
  id: string
  name: string
  description: string
  userId: string
  holdings: PortfolioHolding[]
  totalValue: number
  totalCost: number
  totalReturn: number
  totalReturnPercent: number
  dayChange: number
  dayChangePercent: number
  createdAt: string
  updatedAt: string
  settings: PortfolioSettings
}

export interface PortfolioHolding {
  id: string
  symbol: string
  shares: number
  averagePrice: number
  currentPrice: number
  marketValue: number
  costBasis: number
  unrealizedGain: number
  unrealizedGainPercent: number
  weight: number
  addedAt: string
  lastUpdated: string
}

export interface PortfolioSettings {
  rebalanceThreshold: number
  autoRebalance: boolean
  riskTolerance: 'conservative' | 'moderate' | 'aggressive'
  targetAllocation: Record<string, number>
}

export interface PortfolioPerformance {
  portfolioId: string
  period: '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | 'all'
  returns: number
  volatility: number
  sharpeRatio: number
  maxDrawdown: number
  beta: number
  alpha: number
  benchmarkComparison: BenchmarkComparison
}

export interface BenchmarkComparison {
  benchmark: string
  benchmarkReturn: number
  excessReturn: number
  trackingError: number
  informationRatio: number
}

export interface PortfolioOptimization {
  portfolioId: string
  targetReturn?: number
  maxRisk?: number
  constraints: OptimizationConstraints
  results: OptimizationResults
}

export interface OptimizationConstraints {
  maxWeight: number
  minWeight: number
  sectorLimits: Record<string, number>
  excludeSymbols: string[]
}

export interface OptimizationResults {
  weights: Record<string, number>
  expectedReturn: number
  expectedRisk: number
  sharpeRatio: number
  efficientFrontier: EfficientFrontierPoint[]
}

export interface EfficientFrontierPoint {
  return: number
  risk: number
  weights: Record<string, number>
}

// Analysis Types
export interface DCFAnalysis {
  id: string
  symbol: string
  currentPrice: number
  fairValue: number
  upside: number
  upsidePercent: number
  assumptions: DCFAssumptions
  projections: DCFProjections
  sensitivity: DCFSensitivity
  createdAt: string
  updatedAt: string
}

export interface DCFAssumptions {
  growthRate: number
  terminalGrowthRate: number
  discountRate: number
  taxRate: number
  capexRate: number
  workingCapitalRate: number
}

export interface DCFProjections {
  years: number[]
  revenue: number[]
  ebitda: number[]
  freeCashFlow: number[]
  terminalValue: number
  presentValue: number
}

export interface DCFSensitivity {
  scenarios: DCFScenario[]
}

export interface DCFScenario {
  name: string
  growthRate: number
  discountRate: number
  fairValue: number
  upsidePercent: number
}

export interface ComparableAnalysis {
  id: string
  symbol: string
  peers: PeerCompany[]
  metrics: ComparableMetrics
  valuation: ComparableValuation
  createdAt: string
  updatedAt: string
}

export interface PeerCompany {
  symbol: string
  name: string
  marketCap: number
  pe: number
  pb: number
  ps: number
  evEbitda: number
  roe: number
  debtToEquity: number
}

export interface ComparableMetrics {
  pe: { min: number; max: number; median: number; mean: number }
  pb: { min: number; max: number; median: number; mean: number }
  ps: { min: number; max: number; median: number; mean: number }
  evEbitda: { min: number; max: number; median: number; mean: number }
}

export interface ComparableValuation {
  peBased: number
  pbBased: number
  psBased: number
  evEbitdaBased: number
  average: number
  confidence: number
}

export interface RiskAnalysis {
  id: string
  symbol: string
  metrics: RiskMetrics
  stressTests: StressTest[]
  varAnalysis: VaRAnalysis
  createdAt: string
  updatedAt: string
}

export interface RiskMetrics {
  beta: number
  volatility: number
  sharpeRatio: number
  maxDrawdown: number
  var95: number
  var99: number
  expectedShortfall: number
  downsideDeviation: number
}

export interface StressTest {
  scenario: string
  impact: number
  probability: number
  description: string
}

export interface VaRAnalysis {
  confidenceLevels: VaRPoint[]
  historical: number
  parametric: number
  monteCarlo: number
}

export interface VaRPoint {
  confidence: number
  value: number
}

export interface MonteCarloSimulation {
  id: string
  symbol: string
  simulations: number
  timeHorizon: number
  results: MonteCarloResults
  parameters: MonteCarloParameters
  createdAt: string
  updatedAt: string
}

export interface MonteCarloParameters {
  initialPrice: number
  expectedReturn: number
  volatility: number
  drift: number
  randomSeed?: number
}

export interface MonteCarloResults {
  mean: number
  median: number
  percentile5: number
  percentile25: number
  percentile75: number
  percentile95: number
  probabilityOfLoss: number
  expectedReturn: number
  confidenceInterval: ConfidenceInterval
}

export interface ConfidenceInterval {
  lower: number
  upper: number
  confidence: number
}

// Reports Types
export interface Report {
  id: string
  title: string
  type: 'stock' | 'portfolio' | 'market' | 'custom'
  symbol?: string
  portfolioId?: string
  content: ReportContent
  metadata: ReportMetadata
  status: 'draft' | 'published' | 'archived'
  createdAt: string
  updatedAt: string
  publishedAt?: string
}

export interface ReportContent {
  sections: ReportSection[]
  charts: ReportChart[]
  tables: ReportTable[]
  summary: string
  recommendations: string[]
}

export interface ReportSection {
  id: string
  title: string
  content: string
  order: number
  type: 'text' | 'analysis' | 'chart' | 'table'
}

export interface ReportChart {
  id: string
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'candlestick'
  title: string
  data: any
  options: any
  order: number
}

export interface ReportTable {
  id: string
  title: string
  headers: string[]
  rows: any[][]
  order: number
}

export interface ReportMetadata {
  author: string
  version: string
  tags: string[]
  language: string
  format: 'pdf' | 'html' | 'markdown'
}

// Watchlist Types
export interface Watchlist {
  id: string
  name: string
  description: string
  userId: string
  symbols: string[]
  createdAt: string
  updatedAt: string
}

// Alert Types
export interface Alert {
  id: string
  userId: string
  symbol: string
  type: 'price' | 'volume' | 'news' | 'technical'
  condition: AlertCondition
  value: number
  isActive: boolean
  triggeredAt?: string
  createdAt: string
  updatedAt: string
}

export interface AlertCondition {
  operator: 'above' | 'below' | 'equals' | 'crosses_above' | 'crosses_below'
  field: string
}

// Market Data Types
export interface MarketOverview {
  indices: MarketIndex[]
  sectors: SectorPerformance[]
  movers: MarketMovers
  news: MarketNews[]
  timestamp: string
}

export interface MarketIndex {
  symbol: string
  name: string
  value: number
  change: number
  changePercent: number
}

export interface SectorPerformance {
  sector: string
  change: number
  changePercent: number
  topGainers: string[]
  topLosers: string[]
}

export interface MarketMovers {
  gainers: StockQuote[]
  losers: StockQuote[]
  mostActive: StockQuote[]
}

export interface MarketNews {
  id: string
  title: string
  summary: string
  source: string
  url: string
  publishedAt: string
  impact: 'high' | 'medium' | 'low'
}
