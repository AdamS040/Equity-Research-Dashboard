import React, { useState, useEffect, useMemo } from 'react'
import { Card, Button, Input, Typography, Grid, Flex } from '../ui'
import { formatCurrency, formatPercent, formatNumber } from '../../utils'
import { 
  RiskMetrics,
  MonteCarloSimulation,
  StressTestScenario,
  CorrelationMatrix,
  ConfidenceInterval
} from '../../types/analytics'
import { 
  calculateRiskMetrics,
  calculateMonteCarloStatistics,
  calculateCorrelationMatrix,
  calculateConfidenceInterval
} from '../../utils/financial-calculations'

interface RiskAnalysisProps {
  symbols?: string[]
  returns?: Record<string, number[]>
  onResults?: (results: RiskMetrics) => void
}

export const RiskAnalysis: React.FC<RiskAnalysisProps> = ({
  symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
  returns = {},
  onResults
}) => {
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>(symbols)
  const [activeTab, setActiveTab] = useState<'overview' | 'monte-carlo' | 'stress-test' | 'correlation' | 'var'>('overview')
  const [timeHorizon, setTimeHorizon] = useState<number>(252) // 1 year in trading days
  const [simulations, setSimulations] = useState<number>(10000)
  const [confidenceLevel, setConfidenceLevel] = useState<number>(0.95)

  // Generate sample returns data if not provided
  const sampleReturns = useMemo(() => {
    if (Object.keys(returns).length > 0) return returns
    
    const generated: Record<string, number[]> = {}
    selectedSymbols.forEach(symbol => {
      const dailyReturns: number[] = []
      for (let i = 0; i < 1000; i++) {
        // Generate realistic daily returns with some correlation
        const baseReturn = (Math.random() - 0.5) * 0.04 // ±2% base volatility
        const marketFactor = (Math.random() - 0.5) * 0.02 // Market correlation
        dailyReturns.push(baseReturn + marketFactor)
      }
      generated[symbol] = dailyReturns
    })
    return generated
  }, [returns, selectedSymbols])

  // Calculate risk metrics for each symbol
  const riskMetrics = useMemo(() => {
    const metrics: Record<string, RiskMetrics> = {}
    
    selectedSymbols.forEach(symbol => {
      if (sampleReturns[symbol]) {
        metrics[symbol] = calculateRiskMetrics(sampleReturns[symbol])
      }
    })
    
    return metrics
  }, [selectedSymbols, sampleReturns])

  // Calculate portfolio risk metrics
  const portfolioRiskMetrics = useMemo(() => {
    if (selectedSymbols.length === 0) return null
    
    // Equal weight portfolio
    const weights = selectedSymbols.map(() => 1 / selectedSymbols.length)
    const portfolioReturns: number[] = []
    
    // Calculate portfolio returns
    const minLength = Math.min(...selectedSymbols.map(s => sampleReturns[s]?.length || 0))
    for (let i = 0; i < minLength; i++) {
      let portfolioReturn = 0
      selectedSymbols.forEach((symbol, index) => {
        portfolioReturn += weights[index] * (sampleReturns[symbol]?.[i] || 0)
      })
      portfolioReturns.push(portfolioReturn)
    }
    
    return calculateRiskMetrics(portfolioReturns)
  }, [selectedSymbols, sampleReturns])

  // Monte Carlo simulation
  const monteCarloSimulation = useMemo((): MonteCarloSimulation => {
    if (!portfolioRiskMetrics) {
      return {
        symbol: 'Portfolio',
        simulations,
        timeHorizon,
        initialValue: 100000,
        expectedReturn: 0,
        volatility: 0,
        results: {
          mean: 0,
          median: 0,
          percentile5: 0,
          percentile10: 0,
          percentile25: 0,
          percentile75: 0,
          percentile90: 0,
          percentile95: 0,
          probabilityOfLoss: 0,
          expectedReturn: 0,
          finalValues: []
        },
        confidenceIntervals: []
      }
    }

    const initialValue = 100000
    const expectedReturn = portfolioRiskMetrics.expectedReturn || 0.08 // 8% annual
    const volatility = portfolioRiskMetrics.volatility || 0.15 // 15% annual
    
    const finalValues: number[] = []
    
    for (let i = 0; i < simulations; i++) {
      let value = initialValue
      for (let day = 0; day < timeHorizon; day++) {
        const randomReturn = (Math.random() - 0.5) * 2 * volatility / Math.sqrt(252) + expectedReturn / 252
        value *= (1 + randomReturn)
      }
      finalValues.push(value)
    }
    
    const results = calculateMonteCarloStatistics(finalValues)
    const confidenceIntervals: ConfidenceInterval[] = [
      calculateConfidenceInterval(finalValues, 0.90),
      calculateConfidenceInterval(finalValues, 0.95),
      calculateConfidenceInterval(finalValues, 0.99)
    ]
    
    return {
      symbol: 'Portfolio',
      simulations,
      timeHorizon,
      initialValue,
      expectedReturn,
      volatility,
      results,
      confidenceIntervals
    }
  }, [portfolioRiskMetrics, simulations, timeHorizon])

  // Stress test scenarios
  const stressTestScenarios = useMemo((): StressTestScenario[] => {
    if (!portfolioRiskMetrics) return []
    
    const baseVolatility = portfolioRiskMetrics.volatility || 0.15
    const baseReturn = portfolioRiskMetrics.expectedReturn || 0.08
    
    return [
      {
        name: 'Market Crash 2008',
        description: 'Global financial crisis scenario',
        marketShock: -0.40,
        correlationShock: 0.8,
        volatilityShock: 2.0,
        expectedLoss: baseReturn * 0.5 - baseVolatility * 2,
        var95: -baseVolatility * 1.65 * 2,
        var99: -baseVolatility * 2.33 * 2
      },
      {
        name: 'COVID-19 Pandemic',
        description: 'Market volatility during pandemic',
        marketShock: -0.30,
        correlationShock: 0.6,
        volatilityShock: 1.5,
        expectedLoss: baseReturn * 0.3 - baseVolatility * 1.5,
        var95: -baseVolatility * 1.65 * 1.5,
        var99: -baseVolatility * 2.33 * 1.5
      },
      {
        name: 'Interest Rate Shock',
        description: 'Rapid interest rate increase',
        marketShock: -0.20,
        correlationShock: 0.4,
        volatilityShock: 1.2,
        expectedLoss: baseReturn * 0.2 - baseVolatility * 1.2,
        var95: -baseVolatility * 1.65 * 1.2,
        var99: -baseVolatility * 2.33 * 1.2
      },
      {
        name: 'Tech Bubble Burst',
        description: 'Technology sector correction',
        marketShock: -0.25,
        correlationShock: 0.7,
        volatilityShock: 1.8,
        expectedLoss: baseReturn * 0.4 - baseVolatility * 1.8,
        var95: -baseVolatility * 1.65 * 1.8,
        var99: -baseVolatility * 2.33 * 1.8
      }
    ]
  }, [portfolioRiskMetrics])

  // Correlation matrix
  const correlationMatrix = useMemo((): CorrelationMatrix => {
    const returnArrays = selectedSymbols.map(symbol => sampleReturns[symbol] || [])
    const matrix = calculateCorrelationMatrix(returnArrays)
    
    const allCorrelations = matrix.flat().filter((corr, index) => {
      const row = Math.floor(index / matrix.length)
      const col = index % matrix.length
      return row !== col // Exclude diagonal
    })
    
    return {
      symbols: selectedSymbols,
      matrix,
      averageCorrelation: allCorrelations.reduce((sum, corr) => sum + corr, 0) / allCorrelations.length,
      maxCorrelation: Math.max(...allCorrelations),
      minCorrelation: Math.min(...allCorrelations)
    }
  }, [selectedSymbols, sampleReturns])

  const handleSymbolToggle = (symbol: string) => {
    setSelectedSymbols(prev => 
      prev.includes(symbol) 
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    )
  }

  useEffect(() => {
    if (onResults && portfolioRiskMetrics) {
      onResults(portfolioRiskMetrics)
    }
  }, [portfolioRiskMetrics, onResults])

  return (
    <div className="space-y-6">
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <Typography variant="h2" className="text-2xl font-bold">
              Risk Analysis
            </Typography>
            <div className="flex gap-2">
              <Button variant="outline">
                Export Report
              </Button>
              <Button>
                Run Analysis
              </Button>
            </div>
          </div>

          {/* Symbol Selection */}
          <div className="mb-6">
            <Typography variant="h3" className="text-lg font-semibold mb-3">
              Select Assets for Analysis
            </Typography>
            <div className="flex flex-wrap gap-2">
              {symbols.map(symbol => (
                <button
                  key={symbol}
                  onClick={() => handleSymbolToggle(symbol)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    selectedSymbols.includes(symbol)
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {symbol}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200 mb-6">
            {[
              { key: 'overview', label: 'Risk Overview' },
              { key: 'monte-carlo', label: 'Monte Carlo' },
              { key: 'stress-test', label: 'Stress Testing' },
              { key: 'correlation', label: 'Correlation' },
              { key: 'var', label: 'Value at Risk' }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Risk Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Portfolio Risk Metrics */}
              {portfolioRiskMetrics && (
                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      Portfolio Risk Metrics
                    </Typography>
                    <Grid cols={4} gap={4}>
                      <div className="text-center">
                        <Typography variant="h4" className="text-xl font-bold text-blue-600">
                          {formatPercent(portfolioRiskMetrics.volatility * 100)}
                        </Typography>
                        <Typography variant="body2" className="text-gray-600">
                          Volatility
                        </Typography>
                      </div>
                      <div className="text-center">
                        <Typography variant="h4" className="text-xl font-bold text-green-600">
                          {formatNumber(portfolioRiskMetrics.sharpeRatio, 2)}
                        </Typography>
                        <Typography variant="body2" className="text-gray-600">
                          Sharpe Ratio
                        </Typography>
                      </div>
                      <div className="text-center">
                        <Typography variant="h4" className="text-xl font-bold text-red-600">
                          {formatPercent(portfolioRiskMetrics.maxDrawdown * 100)}
                        </Typography>
                        <Typography variant="body2" className="text-gray-600">
                          Max Drawdown
                        </Typography>
                      </div>
                      <div className="text-center">
                        <Typography variant="h4" className="text-xl font-bold text-purple-600">
                          {formatNumber(portfolioRiskMetrics.beta, 2)}
                        </Typography>
                        <Typography variant="body2" className="text-gray-600">
                          Beta
                        </Typography>
                      </div>
                    </Grid>
                  </div>
                </Card>
              )}

              {/* Individual Asset Risk Metrics */}
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Individual Asset Risk Metrics
                  </Typography>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Symbol</th>
                          <th className="text-right py-2">Volatility</th>
                          <th className="text-right py-2">Sharpe Ratio</th>
                          <th className="text-right py-2">Max Drawdown</th>
                          <th className="text-right py-2">Beta</th>
                          <th className="text-right py-2">VaR (95%)</th>
                          <th className="text-right py-2">VaR (99%)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedSymbols.map(symbol => {
                          const metrics = riskMetrics[symbol]
                          if (!metrics) return null
                          
                          return (
                            <tr key={symbol} className="border-b">
                              <td className="py-2 font-medium">{symbol}</td>
                              <td className="text-right py-2">{formatPercent(metrics.volatility * 100)}</td>
                              <td className="text-right py-2">{formatNumber(metrics.sharpeRatio, 2)}</td>
                              <td className="text-right py-2">{formatPercent(metrics.maxDrawdown * 100)}</td>
                              <td className="text-right py-2">{formatNumber(metrics.beta, 2)}</td>
                              <td className="text-right py-2">{formatPercent(metrics.var95 * 100)}</td>
                              <td className="text-right py-2">{formatPercent(metrics.var99 * 100)}</td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Monte Carlo Tab */}
          {activeTab === 'monte-carlo' && (
            <div className="space-y-6">
              {/* Simulation Parameters */}
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Simulation Parameters
                  </Typography>
                  <Grid cols={3} gap={4}>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Number of Simulations
                      </label>
                      <Input
                        type="number"
                        value={simulations}
                        onChange={(e) => setSimulations(Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Time Horizon (Days)
                      </label>
                      <Input
                        type="number"
                        value={timeHorizon}
                        onChange={(e) => setTimeHorizon(Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Initial Value
                      </label>
                      <Input
                        type="number"
                        value={monteCarloSimulation.initialValue}
                        className="w-full"
                        disabled
                      />
                    </div>
                  </Grid>
                </div>
              </Card>

              {/* Monte Carlo Results */}
              <Grid cols={3} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-blue-600">
                      {formatCurrency(monteCarloSimulation.results.mean)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Mean Final Value
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-green-600">
                      {formatPercent(monteCarloSimulation.results.probabilityOfLoss * 100)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Probability of Loss
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-purple-600">
                      {formatCurrency(monteCarloSimulation.results.percentile95)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      95th Percentile
                    </Typography>
                  </div>
                </Card>
              </Grid>

              {/* Confidence Intervals */}
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Confidence Intervals
                  </Typography>
                  <div className="space-y-3">
                    {monteCarloSimulation.confidenceIntervals.map((interval, index) => (
                      <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                        <span className="font-medium">
                          {formatPercent(interval.level * 100)} Confidence Interval
                        </span>
                        <span className="text-lg font-semibold">
                          {formatCurrency(interval.lower)} - {formatCurrency(interval.upper)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>

              {/* Percentile Analysis */}
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Percentile Analysis
                  </Typography>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>5th Percentile:</span>
                        <span className="font-semibold">{formatCurrency(monteCarloSimulation.results.percentile5)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>10th Percentile:</span>
                        <span className="font-semibold">{formatCurrency(monteCarloSimulation.results.percentile10)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>25th Percentile:</span>
                        <span className="font-semibold">{formatCurrency(monteCarloSimulation.results.percentile25)}</span>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>75th Percentile:</span>
                        <span className="font-semibold">{formatCurrency(monteCarloSimulation.results.percentile75)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>90th Percentile:</span>
                        <span className="font-semibold">{formatCurrency(monteCarloSimulation.results.percentile90)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>95th Percentile:</span>
                        <span className="font-semibold">{formatCurrency(monteCarloSimulation.results.percentile95)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Stress Testing Tab */}
          {activeTab === 'stress-test' && (
            <div className="space-y-6">
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Stress Test Scenarios
                  </Typography>
                  <div className="space-y-4">
                    {stressTestScenarios.map((scenario, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <Typography variant="h4" className="font-semibold">
                              {scenario.name}
                            </Typography>
                            <Typography variant="body2" className="text-gray-600">
                              {scenario.description}
                            </Typography>
                          </div>
                          <div className="text-right">
                            <Typography variant="h4" className="font-bold text-red-600">
                              {formatPercent(scenario.expectedLoss * 100)}
                            </Typography>
                            <Typography variant="body2" className="text-gray-600">
                              Expected Loss
                            </Typography>
                          </div>
                        </div>
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <div className="flex justify-between py-1">
                              <span>Market Shock:</span>
                              <span>{formatPercent(scenario.marketShock * 100)}</span>
                            </div>
                            <div className="flex justify-between py-1">
                              <span>Correlation Shock:</span>
                              <span>{formatPercent(scenario.correlationShock * 100)}</span>
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between py-1">
                              <span>Volatility Shock:</span>
                              <span>{formatPercent(scenario.volatilityShock * 100)}</span>
                            </div>
                            <div className="flex justify-between py-1">
                              <span>VaR (95%):</span>
                              <span>{formatPercent(scenario.var95 * 100)}</span>
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between py-1">
                              <span>VaR (99%):</span>
                              <span>{formatPercent(scenario.var99 * 100)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Correlation Tab */}
          {activeTab === 'correlation' && (
            <div className="space-y-6">
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Correlation Matrix
                  </Typography>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2"></th>
                          {correlationMatrix.symbols.map(symbol => (
                            <th key={symbol} className="text-center py-2 font-medium">
                              {symbol}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {correlationMatrix.symbols.map((symbol, rowIndex) => (
                          <tr key={symbol} className="border-b">
                            <td className="py-2 font-medium">{symbol}</td>
                            {correlationMatrix.symbols.map((_, colIndex) => {
                              const correlation = correlationMatrix.matrix[rowIndex][colIndex]
                              const intensity = Math.abs(correlation)
                              const colorClass = intensity > 0.7 ? 'bg-red-100' : 
                                                intensity > 0.4 ? 'bg-yellow-100' : 
                                                intensity > 0.2 ? 'bg-green-100' : 'bg-gray-100'
                              
                              return (
                                <td key={colIndex} className={`text-center py-2 ${colorClass}`}>
                                  {formatNumber(correlation, 2)}
                                </td>
                              )
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>

              <Grid cols={3} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-blue-600">
                      {formatNumber(correlationMatrix.averageCorrelation, 3)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Average Correlation
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-red-600">
                      {formatNumber(correlationMatrix.maxCorrelation, 3)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Maximum Correlation
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-green-600">
                      {formatNumber(correlationMatrix.minCorrelation, 3)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Minimum Correlation
                    </Typography>
                  </div>
                </Card>
              </Grid>
            </div>
          )}

          {/* Value at Risk Tab */}
          {activeTab === 'var' && (
            <div className="space-y-6">
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Value at Risk Analysis
                  </Typography>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <Typography variant="h4" className="font-semibold mb-3">
                        Portfolio VaR
                      </Typography>
                      {portfolioRiskMetrics && (
                        <div className="space-y-2">
                          <div className="flex justify-between py-2 border-b">
                            <span>VaR (95%):</span>
                            <span className="font-semibold text-red-600">
                              {formatPercent(portfolioRiskMetrics.var95 * 100)}
                            </span>
                          </div>
                          <div className="flex justify-between py-2 border-b">
                            <span>VaR (99%):</span>
                            <span className="font-semibold text-red-600">
                              {formatPercent(portfolioRiskMetrics.var99 * 100)}
                            </span>
                          </div>
                          <div className="flex justify-between py-2 border-b">
                            <span>CVaR (95%):</span>
                            <span className="font-semibold text-red-600">
                              {formatPercent(portfolioRiskMetrics.cvar95 * 100)}
                            </span>
                          </div>
                          <div className="flex justify-between py-2 border-b">
                            <span>CVaR (99%):</span>
                            <span className="font-semibold text-red-600">
                              {formatPercent(portfolioRiskMetrics.cvar99 * 100)}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                    <div>
                      <Typography variant="h4" className="font-semibold mb-3">
                        Individual Asset VaR
                      </Typography>
                      <div className="space-y-2">
                        {selectedSymbols.map(symbol => {
                          const metrics = riskMetrics[symbol]
                          if (!metrics) return null
                          
                          return (
                            <div key={symbol} className="flex justify-between py-1 text-sm">
                              <span>{symbol}:</span>
                              <span className="font-semibold">
                                {formatPercent(metrics.var95 * 100)} / {formatPercent(metrics.var99 * 100)}
                              </span>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}

export default RiskAnalysis
