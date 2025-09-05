/**
 * Portfolio Optimization Component
 * 
 * Modern Portfolio Theory implementation with efficient frontier, risk tolerance, and rebalancing
 */

import React, { useState, useMemo } from 'react'
import { 
  ChartBarIcon,
  AdjustmentsHorizontalIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalculatorIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline'
import { 
  ScatterChart, 
  Scatter, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar
} from 'recharts'
import { Card, Button, Badge, Spinner } from '../ui'
import { usePortfolioStore } from '../../store/portfolio'
import { OptimizationResult, EfficientFrontierPoint, RebalancingRecommendation, OptimizationFilters } from '../../types/portfolio'
import { formatCurrency, formatPercent, getChangeColor } from '../../utils'

const OPTIMIZATION_METHODS = [
  { value: 'max_sharpe', label: 'Maximum Sharpe Ratio' },
  { value: 'min_volatility', label: 'Minimum Volatility' },
  { value: 'target_return', label: 'Target Return' }
]

const RISK_TOLERANCE_LEVELS = [
  { value: 0.1, label: 'Conservative', color: '#10b981' },
  { value: 0.2, label: 'Moderate', color: '#f59e0b' },
  { value: 0.3, label: 'Aggressive', color: '#ef4444' }
]

export const PortfolioOptimization: React.FC = () => {
  const {
    selectedPortfolio,
    optimizationResults,
    efficientFrontier,
    rebalancingRecommendations,
    optimizationFilters,
    setOptimizationFilters,
    setShowOptimizationModal,
    setShowRebalancingModal
  } = usePortfolioStore()

  const [riskTolerance, setRiskTolerance] = useState(0.2)
  const [targetReturn, setTargetReturn] = useState(0.12)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [activeTab, setActiveTab] = useState<'frontier' | 'optimization' | 'rebalancing'>('frontier')

  // Mock efficient frontier data
  const mockEfficientFrontier: EfficientFrontierPoint[] = useMemo(() => {
    const points: EfficientFrontierPoint[] = []
    
    for (let i = 0; i <= 20; i++) {
      const return_ = 0.05 + (i / 20) * 0.15 // 5% to 20% returns
      const risk = 0.1 + Math.sqrt(return_ - 0.05) * 0.3 // Realistic risk-return relationship
      const sharpeRatio = (return_ - 0.02) / risk // Assuming 2% risk-free rate
      
      // Generate mock weights for 5 assets
      const weights: Record<string, number> = {}
      const symbols = selectedPortfolio?.holdings.map(h => h.symbol) || ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
      
      symbols.forEach((symbol, index) => {
        weights[symbol] = (1 / symbols.length) + (Math.random() - 0.5) * 0.1
      })
      
      // Normalize weights
      const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0)
      Object.keys(weights).forEach(symbol => {
        weights[symbol] = weights[symbol] / totalWeight
      })
      
      points.push({
        return: return_,
        risk,
        weights,
        sharpeRatio
      })
    }
    
    return points.sort((a, b) => a.risk - b.risk)
  }, [selectedPortfolio])

  // Mock optimization results
  const mockOptimizationResults: OptimizationResult[] = useMemo(() => {
    const results: OptimizationResult[] = []
    
    // Maximum Sharpe Ratio
    const maxSharpePoint = mockEfficientFrontier.reduce((max, point) => 
      point.sharpeRatio > max.sharpeRatio ? point : max
    )
    
    results.push({
      method: 'max_sharpe',
      weights: maxSharpePoint.weights,
      expectedReturn: maxSharpePoint.return,
      expectedRisk: maxSharpePoint.risk,
      sharpeRatio: maxSharpePoint.sharpeRatio,
      transactionCosts: 0.001 // 0.1% transaction costs
    })
    
    // Minimum Volatility
    const minVolPoint = mockEfficientFrontier.reduce((min, point) => 
      point.risk < min.risk ? point : min
    )
    
    results.push({
      method: 'min_volatility',
      weights: minVolPoint.weights,
      expectedReturn: minVolPoint.return,
      expectedRisk: minVolPoint.risk,
      sharpeRatio: minVolPoint.sharpeRatio,
      transactionCosts: 0.0008
    })
    
    // Target Return
    const targetPoint = mockEfficientFrontier.find(point => 
      Math.abs(point.return - targetReturn) < 0.01
    ) || mockEfficientFrontier[Math.floor(mockEfficientFrontier.length / 2)]
    
    results.push({
      method: 'target_return',
      weights: targetPoint.weights,
      expectedReturn: targetPoint.return,
      expectedRisk: targetPoint.risk,
      sharpeRatio: targetPoint.sharpeRatio,
      transactionCosts: 0.0012
    })
    
    return results
  }, [mockEfficientFrontier, targetReturn])

  // Mock rebalancing recommendations
  const mockRebalancingRecommendations: RebalancingRecommendation[] = useMemo(() => {
    if (!selectedPortfolio) return []
    
    const currentWeights = selectedPortfolio.holdings.reduce((acc, holding) => {
      acc[holding.symbol] = holding.weight / 100
      return acc
    }, {} as Record<string, number>)
    
    const targetWeights = mockOptimizationResults[0].weights // Use max Sharpe weights
    
    return selectedPortfolio.holdings.map(holding => {
      const currentWeight = currentWeights[holding.symbol] || 0
      const targetWeight = targetWeights[holding.symbol] || 0
      const weightDiff = targetWeight - currentWeight
      
      const currentShares = holding.shares
      const targetShares = Math.round((targetWeight * selectedPortfolio.totalValue) / holding.currentPrice)
      const sharesToTrade = targetShares - currentShares
      
      const action = sharesToTrade > 0 ? 'buy' : sharesToTrade < 0 ? 'sell' : 'hold'
      const estimatedCost = Math.abs(sharesToTrade) * holding.currentPrice
      
      const priority = Math.abs(weightDiff) > 0.05 ? 'high' : 
                      Math.abs(weightDiff) > 0.02 ? 'medium' : 'low'
      
      return {
        symbol: holding.symbol,
        currentWeight,
        targetWeight,
        currentShares,
        targetShares,
        action,
        sharesToTrade,
        estimatedCost,
        priority
      }
    }).filter(rec => rec.action !== 'hold')
  }, [selectedPortfolio, mockOptimizationResults])

  const handleOptimize = async () => {
    setIsOptimizing(true)
    
    // Simulate API call
    setTimeout(() => {
      setIsOptimizing(false)
    }, 2000)
  }

  const handleRebalance = () => {
    setShowRebalancingModal(true)
  }

  const OptimizationCard: React.FC<{
    result: OptimizationResult
    isSelected?: boolean
    onClick?: () => void
  }> = ({ result, isSelected, onClick }) => (
    <Card 
      className={`p-4 cursor-pointer transition-all ${
        isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-neutral-50'
      }`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-neutral-900">
          {OPTIMIZATION_METHODS.find(m => m.value === result.method)?.label}
        </h3>
        <Badge variant={result.sharpeRatio > 1 ? 'success' : 'warning'}>
          Sharpe: {result.sharpeRatio.toFixed(2)}
        </Badge>
      </div>
      
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-neutral-600">Expected Return</span>
          <span className="font-medium text-green-600">
            {formatPercent(result.expectedReturn)}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-neutral-600">Expected Risk</span>
          <span className="font-medium text-orange-600">
            {formatPercent(result.expectedRisk)}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-neutral-600">Transaction Costs</span>
          <span className="font-medium text-neutral-900">
            {formatPercent(result.transactionCosts)}
          </span>
        </div>
      </div>
    </Card>
  )

  const RebalancingCard: React.FC<{
    recommendation: RebalancingRecommendation
  }> = ({ recommendation }) => (
    <div className="p-4 border border-neutral-200 rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium text-neutral-900">{recommendation.symbol}</h4>
        <div className="flex items-center space-x-2">
          <Badge 
            variant={recommendation.action === 'buy' ? 'success' : 'danger'}
          >
            {recommendation.action.toUpperCase()}
          </Badge>
          <Badge 
            variant={recommendation.priority === 'high' ? 'danger' : 
                     recommendation.priority === 'medium' ? 'warning' : 'success'}
          >
            {recommendation.priority}
          </Badge>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-neutral-600">Current Weight</div>
          <div className="font-medium">{formatPercent(recommendation.currentWeight)}</div>
        </div>
        <div>
          <div className="text-neutral-600">Target Weight</div>
          <div className="font-medium">{formatPercent(recommendation.targetWeight)}</div>
        </div>
        <div>
          <div className="text-neutral-600">Shares to {recommendation.action}</div>
          <div className="font-medium">{Math.abs(recommendation.sharesToTrade).toLocaleString()}</div>
        </div>
        <div>
          <div className="text-neutral-600">Estimated Cost</div>
          <div className="font-medium">{formatCurrency(recommendation.estimatedCost)}</div>
        </div>
      </div>
    </div>
  )

  if (!selectedPortfolio) {
    return (
      <Card className="p-6">
        <div className="text-center text-neutral-600">
          <p>No portfolio selected</p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Optimization Controls */}
      <Card className="p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4 lg:mb-0">Portfolio Optimization</h2>
          
          <div className="flex flex-wrap items-center gap-4">
            {/* Risk Tolerance Slider */}
            <div className="flex items-center space-x-3">
              <span className="text-sm text-neutral-600">Risk Tolerance:</span>
              <input
                type="range"
                min="0.1"
                max="0.3"
                step="0.05"
                value={riskTolerance}
                onChange={(e) => setRiskTolerance(Number(e.target.value))}
                className="w-24"
              />
              <span className="text-sm font-medium">
                {RISK_TOLERANCE_LEVELS.find(level => level.value === riskTolerance)?.label}
              </span>
            </div>

            {/* Target Return */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-neutral-600">Target Return:</span>
              <input
                type="number"
                min="0.05"
                max="0.25"
                step="0.01"
                value={targetReturn}
                onChange={(e) => setTargetReturn(Number(e.target.value))}
                className="w-20 text-sm border border-neutral-300 rounded px-2 py-1"
              />
              <span className="text-sm text-neutral-600">%</span>
            </div>

            <Button
              variant="primary"
              onClick={handleOptimize}
              disabled={isOptimizing}
            >
              {isOptimizing ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Optimizing...
                </>
              ) : (
                <>
                  <CalculatorIcon className="w-4 h-4 mr-2" />
                  Optimize
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-6">
          <Button
            variant={activeTab === 'frontier' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('frontier')}
          >
            Efficient Frontier
          </Button>
          <Button
            variant={activeTab === 'optimization' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('optimization')}
          >
            Optimization Results
          </Button>
          <Button
            variant={activeTab === 'rebalancing' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('rebalancing')}
          >
            Rebalancing
          </Button>
        </div>
      </Card>

      {/* Efficient Frontier */}
      {activeTab === 'frontier' && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Efficient Frontier</h3>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  type="number" 
                  dataKey="risk" 
                  name="Risk"
                  tickFormatter={(value) => formatPercent(value)}
                />
                <YAxis 
                  type="number" 
                  dataKey="return" 
                  name="Return"
                  tickFormatter={(value) => formatPercent(value)}
                />
                <Tooltip 
                  formatter={(value: number, name: string) => [
                    formatPercent(value),
                    name === 'return' ? 'Expected Return' : 'Expected Risk'
                  ]}
                />
                <Scatter
                  data={mockEfficientFrontier}
                  fill="#3b82f6"
                  name="Efficient Frontier"
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <LightBulbIcon className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">Optimization Insights</span>
            </div>
            <p className="text-sm text-blue-800">
              The efficient frontier shows the optimal risk-return combinations. Points on the curve represent 
              portfolios that offer the highest expected return for a given level of risk, or the lowest risk 
              for a given expected return.
            </p>
          </div>
        </Card>
      )}

      {/* Optimization Results */}
      {activeTab === 'optimization' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {mockOptimizationResults.map((result, index) => (
              <OptimizationCard
                key={result.method}
                result={result}
                isSelected={index === 0}
              />
            ))}
          </div>

          {/* Selected Optimization Details */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Optimal Portfolio Allocation</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-neutral-900 mb-3">Target Weights</h4>
                <div className="space-y-2">
                  {Object.entries(mockOptimizationResults[0].weights).map(([symbol, weight]) => (
                    <div key={symbol} className="flex items-center justify-between">
                      <span className="text-sm text-neutral-600">{symbol}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-neutral-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${weight * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium w-12 text-right">
                          {formatPercent(weight)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-neutral-900 mb-3">Performance Metrics</h4>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Expected Return</span>
                    <span className="font-medium text-green-600">
                      {formatPercent(mockOptimizationResults[0].expectedReturn)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Expected Risk</span>
                    <span className="font-medium text-orange-600">
                      {formatPercent(mockOptimizationResults[0].expectedRisk)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Sharpe Ratio</span>
                    <span className="font-medium text-blue-600">
                      {mockOptimizationResults[0].sharpeRatio.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Transaction Costs</span>
                    <span className="font-medium text-neutral-900">
                      {formatPercent(mockOptimizationResults[0].transactionCosts)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Rebalancing Recommendations */}
      {activeTab === 'rebalancing' && (
        <div className="space-y-6">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-neutral-900">Rebalancing Recommendations</h3>
              <Button
                variant="primary"
                onClick={handleRebalance}
              >
                <AdjustmentsHorizontalIcon className="w-4 h-4 mr-2" />
                Execute Rebalancing
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockRebalancingRecommendations.map((recommendation) => (
                <RebalancingCard
                  key={recommendation.symbol}
                  recommendation={recommendation}
                />
              ))}
            </div>
            
            {mockRebalancingRecommendations.length === 0 && (
              <div className="text-center py-8 text-neutral-600">
                <p>No rebalancing needed. Your portfolio is already optimized.</p>
              </div>
            )}
          </Card>

          {/* Rebalancing Summary */}
          {mockRebalancingRecommendations.length > 0 && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">Rebalancing Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {mockRebalancingRecommendations.filter(r => r.action === 'buy').length}
                  </div>
                  <div className="text-sm text-green-800">Buy Orders</div>
                </div>
                <div className="text-center p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {mockRebalancingRecommendations.filter(r => r.action === 'sell').length}
                  </div>
                  <div className="text-sm text-red-800">Sell Orders</div>
                </div>
                <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {formatCurrency(mockRebalancingRecommendations.reduce((sum, r) => sum + r.estimatedCost, 0))}
                  </div>
                  <div className="text-sm text-blue-800">Total Transaction Value</div>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
