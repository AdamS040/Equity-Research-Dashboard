/**
 * Web Worker for Heavy Calculations
 * 
 * Handles computationally expensive operations like:
 * - Portfolio optimization
 * - Risk analysis
 * - Monte Carlo simulations
 * - Technical indicators
 */

// Message types for worker communication
interface WorkerMessage {
  id: string
  type: 'CALCULATE_PORTFOLIO_OPTIMIZATION' | 'CALCULATE_RISK_METRICS' | 'CALCULATE_MONTE_CARLO' | 'CALCULATE_TECHNICAL_INDICATORS'
  data: any
}

interface WorkerResponse {
  id: string
  type: 'SUCCESS' | 'ERROR'
  data?: any
  error?: string
}

// Portfolio optimization using Modern Portfolio Theory
function calculatePortfolioOptimization(data: {
  assets: Array<{
    symbol: string
    returns: number[]
    expectedReturn: number
    volatility: number
  }>
  riskFreeRate: number
  targetReturn?: number
  maxWeight?: number
}) {
  const { assets, riskFreeRate, targetReturn, maxWeight = 0.4 } = data
  
  // Calculate correlation matrix
  const correlationMatrix = calculateCorrelationMatrix(assets)
  
  // Calculate covariance matrix
  const covarianceMatrix = calculateCovarianceMatrix(assets, correlationMatrix)
  
  // Generate efficient frontier
  const efficientFrontier = generateEfficientFrontier(assets, covarianceMatrix, riskFreeRate)
  
  // Find optimal portfolio
  const optimalPortfolio = findOptimalPortfolio(efficientFrontier, targetReturn)
  
  // Calculate portfolio metrics
  const portfolioMetrics = calculatePortfolioMetrics(optimalPortfolio, assets, covarianceMatrix)
  
  return {
    optimalWeights: optimalPortfolio.weights,
    expectedReturn: optimalPortfolio.expectedReturn,
    volatility: optimalPortfolio.volatility,
    sharpeRatio: optimalPortfolio.sharpeRatio,
    efficientFrontier,
    portfolioMetrics
  }
}

// Risk metrics calculation
function calculateRiskMetrics(data: {
  returns: number[]
  confidenceLevel?: number
  timeHorizon?: number
}) {
  const { returns, confidenceLevel = 0.05, timeHorizon = 1 } = data
  
  // Calculate basic statistics
  const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / (returns.length - 1)
  const volatility = Math.sqrt(variance)
  
  // Value at Risk (VaR)
  const sortedReturns = [...returns].sort((a, b) => a - b)
  const varIndex = Math.floor(confidenceLevel * sortedReturns.length)
  const valueAtRisk = sortedReturns[varIndex]
  
  // Conditional Value at Risk (CVaR)
  const tailReturns = sortedReturns.slice(0, varIndex)
  const cvar = tailReturns.reduce((sum, r) => sum + r, 0) / tailReturns.length
  
  // Maximum Drawdown
  const maxDrawdown = calculateMaxDrawdown(returns)
  
  // Beta calculation (if benchmark returns provided)
  const beta = data.benchmarkReturns ? calculateBeta(returns, data.benchmarkReturns) : null
  
  return {
    mean,
    volatility,
    var: Math.abs(valueAtRisk),
    cvar: Math.abs(cvar),
    maxDrawdown,
    beta,
    skewness: calculateSkewness(returns),
    kurtosis: calculateKurtosis(returns)
  }
}

// Monte Carlo simulation
function calculateMonteCarloSimulation(data: {
  initialValue: number
  expectedReturn: number
  volatility: number
  timeHorizon: number
  simulations: number
}) {
  const { initialValue, expectedReturn, volatility, timeHorizon, simulations } = data
  
  const results = []
  
  for (let i = 0; i < simulations; i++) {
    let value = initialValue
    const path = [value]
    
    for (let t = 1; t <= timeHorizon; t++) {
      // Generate random return using Box-Muller transform
      const randomReturn = generateNormalRandom() * volatility + expectedReturn
      value *= (1 + randomReturn)
      path.push(value)
    }
    
    results.push({
      finalValue: value,
      path,
      totalReturn: (value - initialValue) / initialValue
    })
  }
  
  // Calculate statistics
  const finalValues = results.map(r => r.finalValue)
  const totalReturns = results.map(r => r.totalReturn)
  
  const meanFinalValue = finalValues.reduce((sum, v) => sum + v, 0) / finalValues.length
  const meanReturn = totalReturns.reduce((sum, r) => sum + r, 0) / totalReturns.length
  
  // Calculate percentiles
  const sortedFinalValues = finalValues.sort((a, b) => a - b)
  const percentiles = {
    p5: sortedFinalValues[Math.floor(0.05 * sortedFinalValues.length)],
    p25: sortedFinalValues[Math.floor(0.25 * sortedFinalValues.length)],
    p50: sortedFinalValues[Math.floor(0.50 * sortedFinalValues.length)],
    p75: sortedFinalValues[Math.floor(0.75 * sortedFinalValues.length)],
    p95: sortedFinalValues[Math.floor(0.95 * sortedFinalValues.length)]
  }
  
  return {
    meanFinalValue,
    meanReturn,
    percentiles,
    results: results.slice(0, 1000) // Limit results for performance
  }
}

// Technical indicators calculation
function calculateTechnicalIndicators(data: {
  prices: number[]
  volumes?: number[]
  period?: number
}) {
  const { prices, volumes, period = 14 } = data
  
  const indicators = {
    // Moving averages
    sma20: calculateSMA(prices, 20),
    sma50: calculateSMA(prices, 50),
    sma200: calculateSMA(prices, 200),
    ema12: calculateEMA(prices, 12),
    ema26: calculateEMA(prices, 26),
    
    // Momentum indicators
    rsi: calculateRSI(prices, period),
    macd: calculateMACD(prices),
    stochastic: calculateStochastic(prices, period),
    
    // Volatility indicators
    bollingerBands: calculateBollingerBands(prices, 20, 2),
    atr: calculateATR(prices, period),
    
    // Volume indicators
    obv: volumes ? calculateOBV(prices, volumes) : null,
    vwap: volumes ? calculateVWAP(prices, volumes) : null
  }
  
  return indicators
}

// Helper functions
function calculateCorrelationMatrix(assets: any[]) {
  const n = assets.length
  const matrix = Array(n).fill(null).map(() => Array(n).fill(0))
  
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (i === j) {
        matrix[i][j] = 1
      } else {
        matrix[i][j] = calculateCorrelation(assets[i].returns, assets[j].returns)
      }
    }
  }
  
  return matrix
}

function calculateCorrelation(returns1: number[], returns2: number[]) {
  const n = returns1.length
  const mean1 = returns1.reduce((sum, r) => sum + r, 0) / n
  const mean2 = returns2.reduce((sum, r) => sum + r, 0) / n
  
  let numerator = 0
  let sumSq1 = 0
  let sumSq2 = 0
  
  for (let i = 0; i < n; i++) {
    const diff1 = returns1[i] - mean1
    const diff2 = returns2[i] - mean2
    numerator += diff1 * diff2
    sumSq1 += diff1 * diff1
    sumSq2 += diff2 * diff2
  }
  
  return numerator / Math.sqrt(sumSq1 * sumSq2)
}

function calculateCovarianceMatrix(assets: any[], correlationMatrix: number[][]) {
  const n = assets.length
  const matrix = Array(n).fill(null).map(() => Array(n).fill(0))
  
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      matrix[i][j] = correlationMatrix[i][j] * assets[i].volatility * assets[j].volatility
    }
  }
  
  return matrix
}

function generateEfficientFrontier(assets: any[], covarianceMatrix: number[][], riskFreeRate: number) {
  // Simplified efficient frontier generation
  const points = []
  const numPoints = 50
  
  for (let i = 0; i <= numPoints; i++) {
    const targetReturn = 0.05 + (i / numPoints) * 0.15 // 5% to 20% range
    const weights = generateOptimalWeights(assets, covarianceMatrix, targetReturn)
    const expectedReturn = calculateExpectedReturn(weights, assets)
    const volatility = calculatePortfolioVolatility(weights, covarianceMatrix)
    const sharpeRatio = (expectedReturn - riskFreeRate) / volatility
    
    points.push({
      expectedReturn,
      volatility,
      sharpeRatio,
      weights
    })
  }
  
  return points
}

function findOptimalPortfolio(efficientFrontier: any[], targetReturn?: number) {
  if (targetReturn) {
    // Find portfolio closest to target return
    return efficientFrontier.reduce((best, current) => 
      Math.abs(current.expectedReturn - targetReturn) < Math.abs(best.expectedReturn - targetReturn) 
        ? current : best
    )
  } else {
    // Find portfolio with highest Sharpe ratio
    return efficientFrontier.reduce((best, current) => 
      current.sharpeRatio > best.sharpeRatio ? current : best
    )
  }
}

function calculatePortfolioMetrics(portfolio: any, assets: any[], covarianceMatrix: number[][]) {
  return {
    expectedReturn: portfolio.expectedReturn,
    volatility: portfolio.volatility,
    sharpeRatio: portfolio.sharpeRatio,
    weights: portfolio.weights,
    diversificationRatio: calculateDiversificationRatio(portfolio.weights, assets),
    maxDrawdown: calculateMaxDrawdown(portfolio.returns || [])
  }
}

// Additional helper functions (simplified implementations)
function calculateMaxDrawdown(returns: number[]): number {
  let maxDrawdown = 0
  let peak = 0
  
  for (const ret of returns) {
    peak = Math.max(peak, ret)
    const drawdown = (peak - ret) / peak
    maxDrawdown = Math.max(maxDrawdown, drawdown)
  }
  
  return maxDrawdown
}

function calculateBeta(assetReturns: number[], benchmarkReturns: number[]): number {
  const correlation = calculateCorrelation(assetReturns, benchmarkReturns)
  const assetVolatility = Math.sqrt(assetReturns.reduce((sum, r) => sum + r * r, 0) / assetReturns.length)
  const benchmarkVolatility = Math.sqrt(benchmarkReturns.reduce((sum, r) => sum + r * r, 0) / benchmarkReturns.length)
  
  return correlation * (assetVolatility / benchmarkVolatility)
}

function calculateSkewness(returns: number[]): number {
  const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length
  const stdDev = Math.sqrt(variance)
  
  const skewness = returns.reduce((sum, r) => sum + Math.pow((r - mean) / stdDev, 3), 0) / returns.length
  return skewness
}

function calculateKurtosis(returns: number[]): number {
  const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length
  const stdDev = Math.sqrt(variance)
  
  const kurtosis = returns.reduce((sum, r) => sum + Math.pow((r - mean) / stdDev, 4), 0) / returns.length
  return kurtosis - 3 // Excess kurtosis
}

function generateNormalRandom(): number {
  // Box-Muller transform for normal distribution
  const u1 = Math.random()
  const u2 = Math.random()
  return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2)
}

// Technical indicator helper functions (simplified)
function calculateSMA(prices: number[], period: number): number[] {
  const sma = []
  for (let i = period - 1; i < prices.length; i++) {
    const sum = prices.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0)
    sma.push(sum / period)
  }
  return sma
}

function calculateEMA(prices: number[], period: number): number[] {
  const ema = []
  const multiplier = 2 / (period + 1)
  
  ema[0] = prices[0]
  for (let i = 1; i < prices.length; i++) {
    ema[i] = (prices[i] * multiplier) + (ema[i - 1] * (1 - multiplier))
  }
  
  return ema
}

function calculateRSI(prices: number[], period: number): number[] {
  const rsi = []
  const gains = []
  const losses = []
  
  for (let i = 1; i < prices.length; i++) {
    const change = prices[i] - prices[i - 1]
    gains.push(change > 0 ? change : 0)
    losses.push(change < 0 ? -change : 0)
  }
  
  for (let i = period - 1; i < gains.length; i++) {
    const avgGain = gains.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) / period
    const avgLoss = losses.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) / period
    
    if (avgLoss === 0) {
      rsi.push(100)
    } else {
      const rs = avgGain / avgLoss
      rsi.push(100 - (100 / (1 + rs)))
    }
  }
  
  return rsi
}

function calculateMACD(prices: number[]): { macd: number[], signal: number[], histogram: number[] } {
  const ema12 = calculateEMA(prices, 12)
  const ema26 = calculateEMA(prices, 26)
  
  const macd = []
  for (let i = 0; i < ema12.length; i++) {
    macd.push(ema12[i] - ema26[i])
  }
  
  const signal = calculateEMA(macd, 9)
  const histogram = []
  
  for (let i = 0; i < macd.length; i++) {
    histogram.push(macd[i] - (signal[i] || 0))
  }
  
  return { macd, signal, histogram }
}

function calculateStochastic(prices: number[], period: number): { k: number[], d: number[] } {
  const k = []
  const d = []
  
  for (let i = period - 1; i < prices.length; i++) {
    const periodPrices = prices.slice(i - period + 1, i + 1)
    const highest = Math.max(...periodPrices)
    const lowest = Math.min(...periodPrices)
    const current = prices[i]
    
    k.push(((current - lowest) / (highest - lowest)) * 100)
  }
  
  // Calculate %D (3-period SMA of %K)
  for (let i = 2; i < k.length; i++) {
    d.push((k[i] + k[i - 1] + k[i - 2]) / 3)
  }
  
  return { k, d }
}

function calculateBollingerBands(prices: number[], period: number, stdDev: number): { upper: number[], middle: number[], lower: number[] } {
  const sma = calculateSMA(prices, period)
  const upper = []
  const lower = []
  
  for (let i = period - 1; i < prices.length; i++) {
    const periodPrices = prices.slice(i - period + 1, i + 1)
    const mean = sma[i - period + 1]
    const variance = periodPrices.reduce((sum, price) => sum + Math.pow(price - mean, 2), 0) / period
    const standardDeviation = Math.sqrt(variance)
    
    upper.push(mean + (stdDev * standardDeviation))
    lower.push(mean - (stdDev * standardDeviation))
  }
  
  return { upper, middle: sma, lower }
}

function calculateATR(prices: number[], period: number): number[] {
  const tr = []
  for (let i = 1; i < prices.length; i++) {
    const high = prices[i]
    const low = prices[i - 1]
    const close = prices[i - 1]
    tr.push(Math.max(high - low, Math.abs(high - close), Math.abs(low - close)))
  }
  
  return calculateSMA(tr, period)
}

function calculateOBV(prices: number[], volumes: number[]): number[] {
  const obv = [volumes[0]]
  
  for (let i = 1; i < prices.length; i++) {
    if (prices[i] > prices[i - 1]) {
      obv.push(obv[i - 1] + volumes[i])
    } else if (prices[i] < prices[i - 1]) {
      obv.push(obv[i - 1] - volumes[i])
    } else {
      obv.push(obv[i - 1])
    }
  }
  
  return obv
}

function calculateVWAP(prices: number[], volumes: number[]): number[] {
  const vwap = []
  let cumulativeVolume = 0
  let cumulativePriceVolume = 0
  
  for (let i = 0; i < prices.length; i++) {
    cumulativePriceVolume += prices[i] * volumes[i]
    cumulativeVolume += volumes[i]
    vwap.push(cumulativePriceVolume / cumulativeVolume)
  }
  
  return vwap
}

function calculateDiversificationRatio(weights: number[], assets: any[]): number {
  // Simplified diversification ratio calculation
  const weightedVolatility = weights.reduce((sum, weight, i) => sum + weight * assets[i].volatility, 0)
  const portfolioVolatility = Math.sqrt(weights.reduce((sum, weight, i) => {
    return sum + weight * weight * assets[i].volatility * assets[i].volatility
  }, 0))
  
  return weightedVolatility / portfolioVolatility
}

function generateOptimalWeights(assets: any[], covarianceMatrix: number[][], targetReturn: number): number[] {
  // Simplified weight generation (in practice, this would use quadratic programming)
  const n = assets.length
  const weights = Array(n).fill(1 / n) // Equal weights as starting point
  
  // Simple optimization to get closer to target return
  const currentReturn = calculateExpectedReturn(weights, assets)
  const adjustment = (targetReturn - currentReturn) / 0.1 // Rough adjustment
  
  for (let i = 0; i < n; i++) {
    weights[i] = Math.max(0, Math.min(0.4, weights[i] + adjustment * 0.1))
  }
  
  // Normalize weights
  const sum = weights.reduce((a, b) => a + b, 0)
  return weights.map(w => w / sum)
}

function calculateExpectedReturn(weights: number[], assets: any[]): number {
  return weights.reduce((sum, weight, i) => sum + weight * assets[i].expectedReturn, 0)
}

function calculatePortfolioVolatility(weights: number[], covarianceMatrix: number[][]): number {
  let variance = 0
  for (let i = 0; i < weights.length; i++) {
    for (let j = 0; j < weights.length; j++) {
      variance += weights[i] * weights[j] * covarianceMatrix[i][j]
    }
  }
  return Math.sqrt(variance)
}

// Worker message handler
self.onmessage = function(e: MessageEvent<WorkerMessage>) {
  const { id, type, data } = e.data
  
  try {
    let result
    
    switch (type) {
      case 'CALCULATE_PORTFOLIO_OPTIMIZATION':
        result = calculatePortfolioOptimization(data)
        break
      case 'CALCULATE_RISK_METRICS':
        result = calculateRiskMetrics(data)
        break
      case 'CALCULATE_MONTE_CARLO':
        result = calculateMonteCarloSimulation(data)
        break
      case 'CALCULATE_TECHNICAL_INDICATORS':
        result = calculateTechnicalIndicators(data)
        break
      default:
        throw new Error(`Unknown calculation type: ${type}`)
    }
    
    const response: WorkerResponse = {
      id,
      type: 'SUCCESS',
      data: result
    }
    
    self.postMessage(response)
  } catch (error) {
    const response: WorkerResponse = {
      id,
      type: 'ERROR',
      error: error instanceof Error ? error.message : 'Unknown error'
    }
    
    self.postMessage(response)
  }
}
