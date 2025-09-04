// Stock and Market Data Types
export interface Stock {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  marketCap: number
  pe: number
  eps: number
  dividend: number
  dividendYield: number
}

export interface StockQuote {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume: number
  timestamp: string
}

export interface HistoricalData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface FinancialMetrics {
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
}

// Portfolio Types
export interface Portfolio {
  id: string
  name: string
  description: string
  holdings: PortfolioHolding[]
  totalValue: number
  totalReturn: number
  totalReturnPercent: number
  createdAt: string
  updatedAt: string
}

export interface PortfolioHolding {
  symbol: string
  shares: number
  averagePrice: number
  currentPrice: number
  marketValue: number
  unrealizedGain: number
  unrealizedGainPercent: number
  weight: number
}

// Analysis Types
export interface DCFAnalysis {
  symbol: string
  currentPrice: number
  fairValue: number
  upside: number
  upsidePercent: number
  assumptions: DCFAssumptions
  projections: DCFProjections
}

export interface DCFAssumptions {
  growthRate: number
  terminalGrowthRate: number
  discountRate: number
  taxRate: number
}

export interface DCFProjections {
  years: number[]
  revenue: number[]
  ebitda: number[]
  freeCashFlow: number[]
  terminalValue: number
}

export interface ComparableAnalysis {
  symbol: string
  peers: PeerCompany[]
  metrics: ComparableMetrics
  valuation: ComparableValuation
}

export interface PeerCompany {
  symbol: string
  name: string
  marketCap: number
  pe: number
  pb: number
  ps: number
  evEbitda: number
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
}

// Risk Analysis Types
export interface RiskMetrics {
  beta: number
  volatility: number
  sharpeRatio: number
  maxDrawdown: number
  var95: number
  var99: number
}

export interface MonteCarloSimulation {
  symbol: string
  simulations: number
  timeHorizon: number
  results: MonteCarloResults
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
}

// UI State Types
export interface AppState {
  theme: 'light' | 'dark'
  sidebarOpen: boolean
  selectedPortfolio: string | null
  selectedStock: string | null
}

export interface LoadingState {
  isLoading: boolean
  error: string | null
}

// API Response Types
export interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
  timestamp: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  hasNext: boolean
  hasPrev: boolean
}
