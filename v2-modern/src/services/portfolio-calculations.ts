/**
 * Portfolio Calculation Services
 * 
 * Mathematical calculations for portfolio analysis, risk metrics, and optimization
 */

import {
  Portfolio,
  PortfolioHolding,
  PortfolioMetrics,
  AssetAllocation,
  SectorAllocation,
  PerformanceData,
  RiskMetrics,
  CorrelationMatrix,
  StressTestScenario,
  OptimizationResult,
  EfficientFrontierPoint,
  RebalancingRecommendation
} from '../types/portfolio'

/**
 * Calculate portfolio metrics including returns, risk, and performance ratios
 */
export const calculatePortfolioMetrics = (
  portfolio: Portfolio,
  historicalData: PerformanceData[]
): PortfolioMetrics => {
  const totalValue = portfolio.totalValue
  const totalCost = portfolio.totalCost
  const totalReturn = portfolio.totalReturn
  const totalReturnPercent = portfolio.totalReturnPercent
  const dayChange = portfolio.dayChange
  const dayChangePercent = portfolio.dayChangePercent

  // Calculate volatility (annualized standard deviation of returns)
  const returns = historicalData.map(d => d.returns / 100)
  const meanReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - meanReturn, 2), 0) / returns.length
  const volatility = Math.sqrt(variance) * Math.sqrt(252) // Annualized

  // Calculate Sharpe ratio (assuming 2% risk-free rate)
  const riskFreeRate = 0.02
  const sharpeRatio = (totalReturnPercent / 100 - riskFreeRate) / volatility

  // Calculate beta (correlation with market * portfolio volatility / market volatility)
  const benchmarkReturns = historicalData.map(d => (d.benchmarkValue - historicalData[0].benchmarkValue) / historicalData[0].benchmarkValue)
  const portfolioReturns = historicalData.map(d => (d.portfolioValue - historicalData[0].portfolioValue) / historicalData[0].portfolioValue)
  
  const covariance = calculateCovariance(portfolioReturns, benchmarkReturns)
  const benchmarkVariance = calculateVariance(benchmarkReturns)
  const beta = covariance / benchmarkVariance

  // Calculate VaR (Value at Risk)
  const sortedReturns = returns.sort((a, b) => a - b)
  const var95Index = Math.floor(sortedReturns.length * 0.05)
  const var99Index = Math.floor(sortedReturns.length * 0.01)
  const var95 = sortedReturns[var95Index] || 0
  const var99 = sortedReturns[var99Index] || 0

  // Calculate maximum drawdown
  const maxDrawdown = Math.min(...historicalData.map(d => d.drawdown / 100))

  return {
    totalValue,
    totalCost,
    totalReturn,
    totalReturnPercent,
    dayChange,
    dayChangePercent,
    sharpeRatio,
    beta,
    var95,
    var99,
    maxDrawdown,
    volatility
  }
}

/**
 * Calculate asset allocation from portfolio holdings
 */
export const calculateAssetAllocation = (portfolio: Portfolio): AssetAllocation[] => {
  const colors = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', 
    '#8b5cf6', '#06b6d4', '#f97316', '#84cc16',
    '#ec4899', '#6366f1', '#14b8a6', '#f43f5e'
  ]

  return portfolio.holdings.map((holding, index) => ({
    symbol: holding.symbol,
    name: holding.symbol, // In real app, this would be company name
    value: holding.marketValue,
    weight: holding.weight,
    color: colors[index % colors.length]
  }))
}

/**
 * Calculate sector allocation from portfolio holdings
 */
export const calculateSectorAllocation = (portfolio: Portfolio): SectorAllocation[] => {
  // Mock sector data - in real app, this would come from stock data
  const sectorMap: Record<string, string> = {
    'AAPL': 'Technology',
    'GOOGL': 'Technology',
    'MSFT': 'Technology',
    'TSLA': 'Automotive',
    'AMZN': 'Consumer Discretionary',
    'META': 'Technology',
    'NVDA': 'Technology',
    'JNJ': 'Healthcare',
    'PG': 'Consumer Staples',
    'KO': 'Consumer Staples'
  }

  const sectorTotals: Record<string, { value: number; holdings: string[] }> = {}
  
  portfolio.holdings.forEach(holding => {
    const sector = sectorMap[holding.symbol] || 'Other'
    if (!sectorTotals[sector]) {
      sectorTotals[sector] = { value: 0, holdings: [] }
    }
    sectorTotals[sector].value += holding.marketValue
    sectorTotals[sector].holdings.push(holding.symbol)
  })

  const colors = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', 
    '#8b5cf6', '#06b6d4', '#f97316', '#84cc16'
  ]

  return Object.entries(sectorTotals).map(([sector, data], index) => ({
    sector,
    value: data.value,
    weight: (data.value / portfolio.totalValue) * 100,
    holdings: data.holdings,
    color: colors[index % colors.length]
  }))
}

/**
 * Calculate correlation matrix for portfolio holdings
 */
export const calculateCorrelationMatrix = (
  holdings: PortfolioHolding[],
  historicalData: Record<string, number[]>
): CorrelationMatrix => {
  const symbols = holdings.map(h => h.symbol)
  const matrix: number[][] = []

  for (let i = 0; i < symbols.length; i++) {
    matrix[i] = []
    for (let j = 0; j < symbols.length; j++) {
      if (i === j) {
        matrix[i][j] = 1.0
      } else {
        const correlation = calculateCorrelation(
          historicalData[symbols[i]] || [],
          historicalData[symbols[j]] || []
        )
        matrix[i][j] = correlation
      }
    }
  }

  return { symbols, matrix }
}

/**
 * Calculate risk metrics for portfolio
 */
export const calculateRiskMetrics = (
  portfolio: Portfolio,
  historicalData: PerformanceData[]
): RiskMetrics => {
  const returns = historicalData.map(d => d.returns / 100)
  const benchmarkReturns = historicalData.map(d => 
    (d.benchmarkValue - historicalData[0].benchmarkValue) / historicalData[0].benchmarkValue
  )

  // VaR calculations
  const sortedReturns = returns.sort((a, b) => a - b)
  const var95Index = Math.floor(sortedReturns.length * 0.05)
  const var99Index = Math.floor(sortedReturns.length * 0.01)
  const var95 = sortedReturns[var95Index] || 0
  const var99 = sortedReturns[var99Index] || 0

  // Expected Shortfall (Conditional VaR)
  const tailReturns = sortedReturns.slice(0, var95Index + 1)
  const expectedShortfall = tailReturns.reduce((sum, r) => sum + r, 0) / tailReturns.length

  // Maximum drawdown
  const maxDrawdown = Math.min(...historicalData.map(d => d.drawdown / 100))

  // Volatility
  const volatility = Math.sqrt(calculateVariance(returns)) * Math.sqrt(252)

  // Sharpe ratio
  const meanReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length
  const riskFreeRate = 0.02
  const sharpeRatio = (meanReturn * 252 - riskFreeRate) / volatility

  // Beta
  const covariance = calculateCovariance(returns, benchmarkReturns)
  const benchmarkVariance = calculateVariance(benchmarkReturns)
  const beta = covariance / benchmarkVariance

  // Alpha
  const alpha = meanReturn * 252 - (riskFreeRate + beta * (benchmarkReturns.reduce((sum, r) => sum + r, 0) / benchmarkReturns.length * 252 - riskFreeRate))

  // Tracking error
  const excessReturns = returns.map((r, i) => r - benchmarkReturns[i])
  const trackingError = Math.sqrt(calculateVariance(excessReturns)) * Math.sqrt(252)

  // Information ratio
  const informationRatio = (meanReturn * 252 - benchmarkReturns.reduce((sum, r) => sum + r, 0) / benchmarkReturns.length * 252) / trackingError

  // Downside deviation
  const downsideReturns = returns.filter(r => r < 0)
  const downsideDeviation = Math.sqrt(calculateVariance(downsideReturns)) * Math.sqrt(252)

  return {
    var95,
    var99,
    expectedShortfall,
    maxDrawdown,
    volatility,
    sharpeRatio,
    beta,
    alpha,
    trackingError,
    informationRatio,
    downsideDeviation
  }
}

/**
 * Generate stress test scenarios
 */
export const generateStressTestScenarios = (
  portfolio: Portfolio,
  marketData: Record<string, any>
): StressTestScenario[] => {
  const scenarios = [
    {
      name: 'Market Crash',
      description: 'S&P 500 drops 20% in one month',
      impact: -0.15,
      probability: 0.05
    },
    {
      name: 'Economic Recession',
      description: 'GDP contracts 2% for two consecutive quarters',
      impact: -0.25,
      probability: 0.10
    },
    {
      name: 'Interest Rate Hike',
      description: 'Fed raises rates by 2%',
      impact: -0.08,
      probability: 0.20
    },
    {
      name: 'Inflation Spike',
      description: 'CPI increases to 8% annually',
      impact: -0.12,
      probability: 0.15
    },
    {
      name: 'Tech Bubble Burst',
      description: 'Technology sector drops 30%',
      impact: -0.20,
      probability: 0.08
    }
  ]

  return scenarios.map(scenario => {
    // Calculate portfolio-specific impact based on holdings
    const portfolioImpact = calculatePortfolioStressImpact(portfolio, scenario.impact, marketData)
    
    return {
      ...scenario,
      portfolioImpact
    }
  })
}

/**
 * Calculate efficient frontier using Modern Portfolio Theory
 */
export const calculateEfficientFrontier = (
  assets: Array<{ symbol: string; expectedReturn: number; volatility: number }>,
  correlations: Record<string, Record<string, number>>
): EfficientFrontierPoint[] => {
  const points: EfficientFrontierPoint[] = []
  const numPoints = 50

  for (let i = 0; i <= numPoints; i++) {
    const targetReturn = 0.05 + (i / numPoints) * 0.15 // 5% to 20% returns
    
    // Use quadratic programming to find optimal weights
    const weights = optimizePortfolioWeights(assets, correlations, targetReturn)
    const portfolioReturn = calculatePortfolioReturn(assets, weights)
    const portfolioRisk = calculatePortfolioRisk(assets, weights, correlations)
    const sharpeRatio = (portfolioReturn - 0.02) / portfolioRisk // Assuming 2% risk-free rate

    points.push({
      return: portfolioReturn,
      risk: portfolioRisk,
      weights,
      sharpeRatio
    })
  }

  return points.sort((a, b) => a.risk - b.risk)
}

/**
 * Generate rebalancing recommendations
 */
export const generateRebalancingRecommendations = (
  currentPortfolio: Portfolio,
  targetWeights: Record<string, number>
): RebalancingRecommendation[] => {
  const recommendations: RebalancingRecommendation[] = []

  // Calculate current weights
  const currentWeights: Record<string, number> = {}
  currentPortfolio.holdings.forEach(holding => {
    currentWeights[holding.symbol] = holding.weight / 100
  })

  // Generate recommendations for each holding
  currentPortfolio.holdings.forEach(holding => {
    const currentWeight = currentWeights[holding.symbol] || 0
    const targetWeight = targetWeights[holding.symbol] || 0
    const weightDiff = targetWeight - currentWeight

    if (Math.abs(weightDiff) > 0.01) { // Only rebalance if difference > 1%
      const currentShares = holding.shares
      const targetShares = Math.round((targetWeight * currentPortfolio.totalValue) / holding.currentPrice)
      const sharesToTrade = targetShares - currentShares

      const action = sharesToTrade > 0 ? 'buy' : sharesToTrade < 0 ? 'sell' : 'hold'
      const estimatedCost = Math.abs(sharesToTrade) * holding.currentPrice

      const priority = Math.abs(weightDiff) > 0.05 ? 'high' : 
                      Math.abs(weightDiff) > 0.02 ? 'medium' : 'low'

      recommendations.push({
        symbol: holding.symbol,
        currentWeight,
        targetWeight,
        currentShares,
        targetShares,
        action,
        sharesToTrade,
        estimatedCost,
        priority
      })
    }
  })

  return recommendations
}

// Helper functions

const calculateVariance = (values: number[]): number => {
  const mean = values.reduce((sum, val) => sum + val, 0) / values.length
  return values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length
}

const calculateCovariance = (x: number[], y: number[]): number => {
  if (x.length !== y.length) return 0
  
  const meanX = x.reduce((sum, val) => sum + val, 0) / x.length
  const meanY = y.reduce((sum, val) => sum + val, 0) / y.length
  
  return x.reduce((sum, val, i) => sum + (val - meanX) * (y[i] - meanY), 0) / x.length
}

const calculateCorrelation = (x: number[], y: number[]): number => {
  if (x.length !== y.length || x.length === 0) return 0
  
  const covariance = calculateCovariance(x, y)
  const varianceX = calculateVariance(x)
  const varianceY = calculateVariance(y)
  
  if (varianceX === 0 || varianceY === 0) return 0
  
  return covariance / Math.sqrt(varianceX * varianceY)
}

const calculatePortfolioStressImpact = (
  portfolio: Portfolio,
  marketImpact: number,
  marketData: Record<string, any>
): number => {
  // Simplified calculation - in real app, this would consider sector exposure, beta, etc.
  let weightedImpact = 0
  
  portfolio.holdings.forEach(holding => {
    const weight = holding.weight / 100
    const stockBeta = 0.8 + Math.random() * 0.4 // Mock beta between 0.8-1.2
    weightedImpact += weight * marketImpact * stockBeta
  })
  
  return weightedImpact
}

const optimizePortfolioWeights = (
  assets: Array<{ symbol: string; expectedReturn: number; volatility: number }>,
  correlations: Record<string, Record<string, number>>,
  targetReturn: number
): Record<string, number> => {
  // Simplified optimization - in real app, this would use proper quadratic programming
  const weights: Record<string, number> = {}
  const numAssets = assets.length
  
  // Equal weight as starting point
  const equalWeight = 1 / numAssets
  assets.forEach(asset => {
    weights[asset.symbol] = equalWeight
  })
  
  // Add some randomness to simulate optimization
  Object.keys(weights).forEach(symbol => {
    weights[symbol] += (Math.random() - 0.5) * 0.1
  })
  
  // Normalize weights
  const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0)
  Object.keys(weights).forEach(symbol => {
    weights[symbol] = weights[symbol] / totalWeight
  })
  
  return weights
}

const calculatePortfolioReturn = (
  assets: Array<{ symbol: string; expectedReturn: number; volatility: number }>,
  weights: Record<string, number>
): number => {
  return assets.reduce((sum, asset) => sum + asset.expectedReturn * weights[asset.symbol], 0)
}

const calculatePortfolioRisk = (
  assets: Array<{ symbol: string; expectedReturn: number; volatility: number }>,
  weights: Record<string, number>,
  correlations: Record<string, Record<string, number>>
): number => {
  let variance = 0
  
  // Add individual asset variances
  assets.forEach(asset => {
    variance += Math.pow(weights[asset.symbol] * asset.volatility, 2)
  })
  
  // Add covariance terms
  for (let i = 0; i < assets.length; i++) {
    for (let j = i + 1; j < assets.length; j++) {
      const correlation = correlations[assets[i].symbol]?.[assets[j].symbol] || 0
      variance += 2 * weights[assets[i].symbol] * weights[assets[j].symbol] * 
                  assets[i].volatility * assets[j].volatility * correlation
    }
  }
  
  return Math.sqrt(variance)
}
