// Advanced Financial Calculations and Mathematical Functions

import { 
  DCFInputs, 
  DCFProjection, 
  DCFResults, 
  MonteCarloResults,
  RiskMetrics,
  StatisticalSummary,
  ConfidenceInterval
} from '../types/analytics'

// DCF Calculation Functions
export const calculateDCF = (inputs: DCFInputs): DCFResults => {
  const projections: DCFProjection[] = []
  let cumulativePresentValue = 0
  
  // Calculate projections for each year
  for (let year = 1; year <= inputs.projectionYears; year++) {
    const prevYear = year === 1 ? 0 : projections[year - 2]
    
    // Revenue calculation
    const revenue = year === 1 
      ? inputs.revenue * (1 + inputs.revenueGrowthRate)
      : prevYear.revenue * (1 + inputs.revenueGrowthRate)
    
    // EBITDA calculation
    const ebitda = revenue * inputs.ebitdaMargin
    
    // EBIT calculation (assuming depreciation is 10% of revenue)
    const depreciation = revenue * 0.1
    const ebit = ebitda - depreciation
    
    // Tax calculation
    const tax = ebit * inputs.taxRate
    
    // NOPAT calculation
    const nopat = ebit - tax
    
    // Free Cash Flow calculation
    const capex = revenue * 0.05 // Assuming 5% of revenue
    const workingCapitalChange = revenue * 0.02 // Assuming 2% of revenue
    const freeCashFlow = nopat + depreciation - capex - workingCapitalChange
    
    // Present Value calculation
    const presentValue = freeCashFlow / Math.pow(1 + inputs.wacc, year)
    cumulativePresentValue += presentValue
    
    projections.push({
      year,
      revenue,
      ebitda,
      ebit,
      tax,
      nopat,
      depreciation,
      capex,
      workingCapitalChange,
      freeCashFlow,
      presentValue
    })
  }
  
  // Terminal Value calculation
  const lastYearFCF = projections[projections.length - 1].freeCashFlow
  const terminalValue = (lastYearFCF * (1 + inputs.terminalGrowthRate)) / 
    (inputs.wacc - inputs.terminalGrowthRate)
  
  const terminalValuePV = terminalValue / Math.pow(1 + inputs.wacc, inputs.projectionYears)
  
  // Fair Value calculation
  const fairValue = cumulativePresentValue + terminalValuePV
  const upside = fairValue - inputs.currentPrice
  const upsidePercent = (upside / inputs.currentPrice) * 100
  
  return {
    fairValue,
    upside,
    upsidePercent,
    terminalValue,
    projections,
    sensitivityAnalysis: calculateSensitivityAnalysis(inputs),
    monteCarloResults: runMonteCarloSimulation(inputs, 10000)
  }
}

export const calculateSensitivityAnalysis = (inputs: DCFInputs) => {
  const waccRange = { min: inputs.wacc - 0.02, max: inputs.wacc + 0.02, step: 0.005 }
  const growthRange = { min: inputs.revenueGrowthRate - 0.05, max: inputs.revenueGrowthRate + 0.05, step: 0.01 }
  
  const results: Array<{ wacc: number; growth: number; fairValue: number }> = []
  
  for (let wacc = waccRange.min; wacc <= waccRange.max; wacc += waccRange.step) {
    for (let growth = growthRange.min; growth <= growthRange.max; growth += growthRange.step) {
      const modifiedInputs = { ...inputs, wacc, revenueGrowthRate: growth }
      const dcfResult = calculateDCF(modifiedInputs)
      results.push({ wacc, growth, fairValue: dcfResult.fairValue })
    }
  }
  
  return { waccRange, growthRange, results }
}

export const runMonteCarloSimulation = (inputs: DCFInputs, simulations: number): MonteCarloResults => {
  const results: number[] = []
  
  for (let i = 0; i < simulations; i++) {
    // Add random variation to key inputs
    const randomWacc = inputs.wacc + (Math.random() - 0.5) * 0.04 // ±2% variation
    const randomGrowth = inputs.revenueGrowthRate + (Math.random() - 0.5) * 0.1 // ±5% variation
    const randomMargin = inputs.ebitdaMargin + (Math.random() - 0.5) * 0.04 // ±2% variation
    
    const modifiedInputs = {
      ...inputs,
      wacc: Math.max(0.01, randomWacc), // Ensure positive WACC
      revenueGrowthRate: Math.max(-0.2, randomGrowth), // Cap at -20%
      ebitdaMargin: Math.max(0.01, Math.min(0.5, randomMargin)) // Keep between 1% and 50%
    }
    
    const dcfResult = calculateDCF(modifiedInputs)
    results.push(dcfResult.fairValue)
  }
  
  return calculateMonteCarloStatistics(results)
}

// Monte Carlo Statistics
export const calculateMonteCarloStatistics = (values: number[]): MonteCarloResults => {
  const sorted = [...values].sort((a, b) => a - b)
  const n = values.length
  
  const mean = values.reduce((sum, val) => sum + val, 0) / n
  const median = n % 2 === 0 
    ? (sorted[n / 2 - 1] + sorted[n / 2]) / 2 
    : sorted[Math.floor(n / 2)]
  
  const percentile5 = sorted[Math.floor(n * 0.05)]
  const percentile10 = sorted[Math.floor(n * 0.10)]
  const percentile25 = sorted[Math.floor(n * 0.25)]
  const percentile75 = sorted[Math.floor(n * 0.75)]
  const percentile90 = sorted[Math.floor(n * 0.90)]
  const percentile95 = sorted[Math.floor(n * 0.95)]
  
  const probabilityOfLoss = values.filter(val => val < 0).length / n
  
  return {
    mean,
    median,
    percentile5,
    percentile10,
    percentile25,
    percentile75,
    percentile90,
    percentile95,
    probabilityOfLoss,
    expectedReturn: mean,
    finalValues: values
  }
}

// Risk Metrics Calculations
export const calculateRiskMetrics = (
  returns: number[],
  benchmarkReturns: number[] = [],
  riskFreeRate: number = 0.02
): RiskMetrics => {
  const n = returns.length
  
  // Basic statistics
  const meanReturn = returns.reduce((sum, ret) => sum + ret, 0) / n
  const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - meanReturn, 2), 0) / (n - 1)
  const volatility = Math.sqrt(variance)
  
  // Beta calculation (if benchmark provided)
  const beta = benchmarkReturns.length > 0 ? calculateBeta(returns, benchmarkReturns) : 1
  
  // Sharpe Ratio
  const sharpeRatio = (meanReturn - riskFreeRate) / volatility
  
  // Sortino Ratio (downside deviation)
  const downsideReturns = returns.filter(ret => ret < 0)
  const downsideVariance = downsideReturns.reduce((sum, ret) => sum + Math.pow(ret, 2), 0) / n
  const downsideDeviation = Math.sqrt(downsideVariance)
  const sortinoRatio = (meanReturn - riskFreeRate) / downsideDeviation
  
  // Maximum Drawdown
  const maxDrawdown = calculateMaxDrawdown(returns)
  
  // Value at Risk (VaR)
  const sortedReturns = [...returns].sort((a, b) => a - b)
  const var95 = sortedReturns[Math.floor(n * 0.05)]
  const var99 = sortedReturns[Math.floor(n * 0.01)]
  
  // Conditional Value at Risk (CVaR)
  const cvar95 = sortedReturns.slice(0, Math.floor(n * 0.05)).reduce((sum, ret) => sum + ret, 0) / Math.floor(n * 0.05)
  const cvar99 = sortedReturns.slice(0, Math.floor(n * 0.01)).reduce((sum, ret) => sum + ret, 0) / Math.floor(n * 0.01)
  
  // Tracking Error and Information Ratio (if benchmark provided)
  const trackingError = benchmarkReturns.length > 0 ? calculateTrackingError(returns, benchmarkReturns) : 0
  const informationRatio = benchmarkReturns.length > 0 ? (meanReturn - calculateMean(benchmarkReturns)) / trackingError : 0
  
  // Calmar Ratio
  const annualizedReturn = Math.pow(1 + meanReturn, 252) - 1 // Assuming daily returns
  const calmarRatio = annualizedReturn / Math.abs(maxDrawdown)
  
  return {
    beta,
    volatility,
    sharpeRatio,
    sortinoRatio,
    maxDrawdown,
    var95,
    var99,
    cvar95,
    cvar99,
    trackingError,
    informationRatio,
    calmarRatio
  }
}

// Helper functions for risk calculations
export const calculateBeta = (assetReturns: number[], marketReturns: number[]): number => {
  const n = Math.min(assetReturns.length, marketReturns.length)
  const assetMean = calculateMean(assetReturns.slice(0, n))
  const marketMean = calculateMean(marketReturns.slice(0, n))
  
  let covariance = 0
  let marketVariance = 0
  
  for (let i = 0; i < n; i++) {
    const assetDiff = assetReturns[i] - assetMean
    const marketDiff = marketReturns[i] - marketMean
    covariance += assetDiff * marketDiff
    marketVariance += marketDiff * marketDiff
  }
  
  return covariance / marketVariance
}

export const calculateMaxDrawdown = (returns: number[]): number => {
  let peak = 0
  let maxDrawdown = 0
  let cumulative = 0
  
  for (const ret of returns) {
    cumulative += ret
    if (cumulative > peak) {
      peak = cumulative
    }
    const drawdown = peak - cumulative
    if (drawdown > maxDrawdown) {
      maxDrawdown = drawdown
    }
  }
  
  return maxDrawdown
}

export const calculateTrackingError = (assetReturns: number[], benchmarkReturns: number[]): number => {
  const n = Math.min(assetReturns.length, benchmarkReturns.length)
  const excessReturns = assetReturns.slice(0, n).map((ret, i) => ret - benchmarkReturns[i])
  const meanExcessReturn = calculateMean(excessReturns)
  
  const variance = excessReturns.reduce((sum, ret) => sum + Math.pow(ret - meanExcessReturn, 2), 0) / (n - 1)
  return Math.sqrt(variance)
}

export const calculateMean = (values: number[]): number => {
  return values.reduce((sum, val) => sum + val, 0) / values.length
}

// Statistical Functions
export const calculateStatisticalSummary = (values: number[]): StatisticalSummary => {
  const sorted = [...values].sort((a, b) => a - b)
  const n = values.length
  
  const mean = calculateMean(values)
  const median = n % 2 === 0 
    ? (sorted[n / 2 - 1] + sorted[n / 2]) / 2 
    : sorted[Math.floor(n / 2)]
  
  const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / (n - 1)
  const standardDeviation = Math.sqrt(variance)
  
  // Skewness
  const skewness = values.reduce((sum, val) => sum + Math.pow((val - mean) / standardDeviation, 3), 0) / n
  
  // Kurtosis
  const kurtosis = values.reduce((sum, val) => sum + Math.pow((val - mean) / standardDeviation, 4), 0) / n - 3
  
  // Mode (most frequent value)
  const frequency: Record<number, number> = {}
  values.forEach(val => {
    frequency[val] = (frequency[val] || 0) + 1
  })
  const mode = Object.keys(frequency).reduce((a, b) => frequency[Number(a)] > frequency[Number(b)] ? a : b, '0')
  
  return {
    count: n,
    mean,
    median,
    mode: Number(mode),
    standardDeviation,
    variance,
    skewness,
    kurtosis,
    min: sorted[0],
    max: sorted[n - 1],
    range: sorted[n - 1] - sorted[0],
    percentile25: sorted[Math.floor(n * 0.25)],
    percentile75: sorted[Math.floor(n * 0.75)],
    percentile90: sorted[Math.floor(n * 0.90)],
    percentile95: sorted[Math.floor(n * 0.95)],
    percentile99: sorted[Math.floor(n * 0.99)]
  }
}

// Options Pricing Functions (Black-Scholes)
export const calculateBlackScholes = (
  spotPrice: number,
  strikePrice: number,
  timeToExpiration: number,
  riskFreeRate: number,
  volatility: number,
  optionType: 'call' | 'put'
): { price: number; delta: number; gamma: number; theta: number; vega: number; rho: number } => {
  const d1 = (Math.log(spotPrice / strikePrice) + (riskFreeRate + 0.5 * volatility * volatility) * timeToExpiration) / 
    (volatility * Math.sqrt(timeToExpiration))
  const d2 = d1 - volatility * Math.sqrt(timeToExpiration)
  
  // Cumulative normal distribution approximation
  const N = (x: number) => 0.5 * (1 + erf(x / Math.sqrt(2)))
  const n = (x: number) => Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI)
  
  const price = optionType === 'call' 
    ? spotPrice * N(d1) - strikePrice * Math.exp(-riskFreeRate * timeToExpiration) * N(d2)
    : strikePrice * Math.exp(-riskFreeRate * timeToExpiration) * N(-d2) - spotPrice * N(-d1)
  
  const delta = optionType === 'call' ? N(d1) : N(d1) - 1
  const gamma = n(d1) / (spotPrice * volatility * Math.sqrt(timeToExpiration))
  const theta = optionType === 'call'
    ? -spotPrice * n(d1) * volatility / (2 * Math.sqrt(timeToExpiration)) - 
      riskFreeRate * strikePrice * Math.exp(-riskFreeRate * timeToExpiration) * N(d2)
    : -spotPrice * n(d1) * volatility / (2 * Math.sqrt(timeToExpiration)) + 
      riskFreeRate * strikePrice * Math.exp(-riskFreeRate * timeToExpiration) * N(-d2)
  const vega = spotPrice * n(d1) * Math.sqrt(timeToExpiration)
  const rho = optionType === 'call'
    ? strikePrice * timeToExpiration * Math.exp(-riskFreeRate * timeToExpiration) * N(d2)
    : -strikePrice * timeToExpiration * Math.exp(-riskFreeRate * timeToExpiration) * N(-d2)
  
  return { price, delta, gamma, theta, vega, rho }
}

// Error function approximation
const erf = (x: number): number => {
  // Abramowitz and Stegun approximation
  const a1 = 0.254829592
  const a2 = -0.284496736
  const a3 = 1.421413741
  const a4 = -1.453152027
  const a5 = 1.061405429
  const p = 0.3275911
  
  const sign = x >= 0 ? 1 : -1
  x = Math.abs(x)
  
  const t = 1.0 / (1.0 + p * x)
  const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x)
  
  return sign * y
}

// Portfolio Optimization Functions
export const calculatePortfolioMetrics = (
  weights: number[],
  returns: number[][],
  covarianceMatrix: number[][]
): { expectedReturn: number; volatility: number; sharpeRatio: number } => {
  const expectedReturns = returns.map(assetReturns => calculateMean(assetReturns))
  
  // Portfolio expected return
  const expectedReturn = weights.reduce((sum, weight, i) => sum + weight * expectedReturns[i], 0)
  
  // Portfolio variance
  let variance = 0
  for (let i = 0; i < weights.length; i++) {
    for (let j = 0; j < weights.length; j++) {
      variance += weights[i] * weights[j] * covarianceMatrix[i][j]
    }
  }
  
  const volatility = Math.sqrt(variance)
  const sharpeRatio = expectedReturn / volatility // Assuming risk-free rate is 0
  
  return { expectedReturn, volatility, sharpeRatio }
}

// Correlation Matrix Calculation
export const calculateCorrelationMatrix = (returns: number[][]): number[][] => {
  const n = returns.length
  const correlationMatrix: number[][] = Array(n).fill(null).map(() => Array(n).fill(0))
  
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (i === j) {
        correlationMatrix[i][j] = 1
      } else {
        correlationMatrix[i][j] = calculateCorrelation(returns[i], returns[j])
      }
    }
  }
  
  return correlationMatrix
}

export const calculateCorrelation = (x: number[], y: number[]): number => {
  const n = Math.min(x.length, y.length)
  const xMean = calculateMean(x.slice(0, n))
  const yMean = calculateMean(y.slice(0, n))
  
  let numerator = 0
  let xSumSquared = 0
  let ySumSquared = 0
  
  for (let i = 0; i < n; i++) {
    const xDiff = x[i] - xMean
    const yDiff = y[i] - yMean
    numerator += xDiff * yDiff
    xSumSquared += xDiff * xDiff
    ySumSquared += yDiff * yDiff
  }
  
  return numerator / Math.sqrt(xSumSquared * ySumSquared)
}

// Utility Functions
export const calculateConfidenceInterval = (
  values: number[],
  confidenceLevel: number = 0.95
): ConfidenceInterval => {
  const sorted = [...values].sort((a, b) => a - b)
  const n = values.length
  const alpha = 1 - confidenceLevel
  
  const lowerIndex = Math.floor(n * (alpha / 2))
  const upperIndex = Math.floor(n * (1 - alpha / 2))
  
  return {
    level: confidenceLevel,
    lower: sorted[lowerIndex],
    upper: sorted[upperIndex]
  }
}

export const calculateWACC = (
  equityValue: number,
  debtValue: number,
  costOfEquity: number,
  costOfDebt: number,
  taxRate: number
): number => {
  const totalValue = equityValue + debtValue
  const equityWeight = equityValue / totalValue
  const debtWeight = debtValue / totalValue
  
  return equityWeight * costOfEquity + debtWeight * costOfDebt * (1 - taxRate)
}

export const calculateCostOfEquity = (
  riskFreeRate: number,
  beta: number,
  marketRiskPremium: number
): number => {
  return riskFreeRate + beta * marketRiskPremium
}
