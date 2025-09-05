// Advanced Analytics Types for Financial Modeling

// DCF Analysis Types
export interface DCFInputs {
  symbol: string
  currentPrice: number
  revenue: number
  revenueGrowthRate: number
  ebitdaMargin: number
  taxRate: number
  capex: number
  workingCapital: number
  terminalGrowthRate: number
  wacc: number
  beta: number
  riskFreeRate: number
  marketRiskPremium: number
  debtToEquity: number
  costOfDebt: number
  projectionYears: number
}

export interface DCFProjection {
  year: number
  revenue: number
  ebitda: number
  ebit: number
  tax: number
  nopat: number
  depreciation: number
  capex: number
  workingCapitalChange: number
  freeCashFlow: number
  presentValue: number
}

export interface DCFResults {
  fairValue: number
  upside: number
  upsidePercent: number
  terminalValue: number
  projections: DCFProjection[]
  sensitivityAnalysis: DCFSensitivityAnalysis
  monteCarloResults: MonteCarloResults
}

export interface DCFSensitivityAnalysis {
  waccRange: { min: number; max: number; step: number }
  growthRange: { min: number; max: number; step: number }
  results: Array<{
    wacc: number
    growth: number
    fairValue: number
  }>
}

export interface DCFScenario {
  name: string
  probability: number
  revenueGrowth: number
  ebitdaMargin: number
  terminalGrowth: number
  wacc: number
  fairValue: number
}

// Comparable Analysis Types
export interface ComparableCompany {
  symbol: string
  name: string
  marketCap: number
  enterpriseValue: number
  revenue: number
  ebitda: number
  netIncome: number
  sharesOutstanding: number
  price: number
  pe: number
  pb: number
  ps: number
  evRevenue: number
  evEbitda: number
  peg: number
  roe: number
  roa: number
  debtToEquity: number
  currentRatio: number
  industry: string
  sector: string
}

export interface ComparableMetrics {
  pe: ValuationMetric
  pb: ValuationMetric
  ps: ValuationMetric
  evRevenue: ValuationMetric
  evEbitda: ValuationMetric
  peg: ValuationMetric
}

export interface ValuationMetric {
  min: number
  max: number
  median: number
  mean: number
  percentile25: number
  percentile75: number
  standardDeviation: number
}

export interface ComparableValuation {
  peBased: number
  pbBased: number
  psBased: number
  evRevenueBased: number
  evEbitdaBased: number
  average: number
  median: number
  weightedAverage: number
}

export interface PeerRanking {
  symbol: string
  name: string
  overallScore: number
  valuationScore: number
  profitabilityScore: number
  growthScore: number
  financialHealthScore: number
  rank: number
}

// Risk Analysis Types
export interface RiskMetrics {
  beta: number
  volatility: number
  sharpeRatio: number
  sortinoRatio: number
  maxDrawdown: number
  var95: number
  var99: number
  cvar95: number
  cvar99: number
  trackingError: number
  informationRatio: number
  calmarRatio: number
}

export interface MonteCarloSimulation {
  symbol: string
  simulations: number
  timeHorizon: number
  initialValue: number
  expectedReturn: number
  volatility: number
  results: MonteCarloResults
  confidenceIntervals: ConfidenceInterval[]
}

export interface MonteCarloResults {
  mean: number
  median: number
  percentile5: number
  percentile10: number
  percentile25: number
  percentile75: number
  percentile90: number
  percentile95: number
  probabilityOfLoss: number
  expectedReturn: number
  finalValues: number[]
}

export interface ConfidenceInterval {
  level: number
  lower: number
  upper: number
}

export interface StressTestScenario {
  name: string
  description: string
  marketShock: number
  correlationShock: number
  volatilityShock: number
  expectedLoss: number
  var95: number
  var99: number
}

export interface CorrelationMatrix {
  symbols: string[]
  matrix: number[][]
  averageCorrelation: number
  maxCorrelation: number
  minCorrelation: number
}

// Backtesting Types
export interface BacktestStrategy {
  name: string
  description: string
  parameters: Record<string, any>
  entryRules: string[]
  exitRules: string[]
  positionSizing: string
}

export interface BacktestResults {
  strategy: BacktestStrategy
  startDate: string
  endDate: string
  initialCapital: number
  finalValue: number
  totalReturn: number
  annualizedReturn: number
  volatility: number
  sharpeRatio: number
  maxDrawdown: number
  maxDrawdownDuration: number
  winRate: number
  profitFactor: number
  trades: BacktestTrade[]
  monthlyReturns: MonthlyReturn[]
  benchmarkComparison: BenchmarkComparison
}

export interface BacktestTrade {
  entryDate: string
  exitDate: string
  symbol: string
  entryPrice: number
  exitPrice: number
  quantity: number
  pnl: number
  pnlPercent: number
  duration: number
  reason: string
}

export interface MonthlyReturn {
  month: string
  return: number
  cumulativeReturn: number
}

export interface BenchmarkComparison {
  benchmark: string
  benchmarkReturn: number
  alpha: number
  beta: number
  informationRatio: number
  trackingError: number
}

// Options Analysis Types
export interface OptionsChain {
  symbol: string
  expirationDate: string
  calls: OptionContract[]
  puts: OptionContract[]
  underlyingPrice: number
  impliedVolatility: number
  timeToExpiration: number
}

export interface OptionContract {
  strike: number
  bid: number
  ask: number
  last: number
  volume: number
  openInterest: number
  impliedVolatility: number
  delta: number
  gamma: number
  theta: number
  vega: number
  rho: number
  intrinsicValue: number
  timeValue: number
}

export interface OptionsStrategy {
  name: string
  description: string
  legs: OptionsLeg[]
  maxProfit: number
  maxLoss: number
  breakevenPoints: number[]
  profitLossDiagram: ProfitLossPoint[]
}

export interface OptionsLeg {
  type: 'call' | 'put'
  action: 'buy' | 'sell'
  strike: number
  premium: number
  quantity: number
  expiration: string
}

export interface ProfitLossPoint {
  underlyingPrice: number
  profitLoss: number
}

export interface GreeksAnalysis {
  symbol: string
  delta: number
  gamma: number
  theta: number
  vega: number
  rho: number
  impliedVolatility: number
  historicalVolatility: number
  volatilitySkew: VolatilitySkew[]
}

export interface VolatilitySkew {
  strike: number
  impliedVolatility: number
  moneyness: number
}

// Economic Indicators Types
export interface EconomicIndicator {
  name: string
  symbol: string
  value: number
  previousValue: number
  change: number
  changePercent: number
  unit: string
  frequency: string
  lastUpdated: string
  source: string
  description: string
}

export interface EconomicCalendar {
  date: string
  events: EconomicEvent[]
}

export interface EconomicEvent {
  time: string
  country: string
  event: string
  importance: 'Low' | 'Medium' | 'High'
  actual: number | null
  forecast: number | null
  previous: number | null
  unit: string
}

export interface InterestRateData {
  rate: number
  previousRate: number
  change: number
  effectiveDate: string
  nextMeeting: string
  targetRange: {
    lower: number
    upper: number
  }
}

export interface InflationData {
  cpi: number
  cpiChange: number
  coreCpi: number
  coreCpiChange: number
  pce: number
  pceChange: number
  corePce: number
  corePceChange: number
  lastUpdated: string
}

export interface GDPData {
  gdp: number
  gdpGrowth: number
  gdpPerCapita: number
  gdpPerCapitaGrowth: number
  lastUpdated: string
  quarter: string
}

export interface EmploymentData {
  unemploymentRate: number
  unemploymentRateChange: number
  nonFarmPayrolls: number
  nonFarmPayrollsChange: number
  laborForceParticipation: number
  laborForceParticipationChange: number
  lastUpdated: string
}

// Market Sentiment Types
export interface MarketSentiment {
  vix: number
  vixChange: number
  fearGreedIndex: number
  putCallRatio: number
  insiderTrading: number
  institutionalFlow: number
  retailFlow: number
  lastUpdated: string
}

// Utility Types
export interface TimeSeriesData {
  date: string
  value: number
}

export interface StatisticalSummary {
  count: number
  mean: number
  median: number
  mode: number
  standardDeviation: number
  variance: number
  skewness: number
  kurtosis: number
  min: number
  max: number
  range: number
  percentile25: number
  percentile75: number
  percentile90: number
  percentile95: number
  percentile99: number
}
