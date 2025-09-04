/**
 * Risk Analysis Component
 * 
 * VaR calculations, maximum drawdown, correlation matrix, beta analysis, and stress testing
 */

import React, { useState, useMemo } from 'react'
import { 
  ShieldExclamationIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  Cell
} from 'recharts'
import { Card, Button, Badge, Spinner } from '../ui'
import { usePortfolioStore } from '../../store/portfolio'
import { RiskMetrics, CorrelationMatrix, StressTestScenario, RiskAnalysisFilters } from '../../types/portfolio'
import { formatCurrency, formatPercent, getChangeColor } from '../../utils'

const CONFIDENCE_LEVELS = [
  { value: 95, label: '95%' },
  { value: 99, label: '99%' }
]

const TIME_HORIZONS = [
  { value: 1, label: '1 Day' },
  { value: 7, label: '1 Week' },
  { value: 30, label: '1 Month' },
  { value: 90, label: '3 Months' }
]

const STRESS_SCENARIOS = [
  {
    id: 'market_crash',
    name: 'Market Crash',
    description: 'S&P 500 drops 20% in one month',
    impact: -0.15,
    probability: 0.05
  },
  {
    id: 'recession',
    name: 'Economic Recession',
    description: 'GDP contracts 2% for two consecutive quarters',
    impact: -0.25,
    probability: 0.10
  },
  {
    id: 'interest_rate_hike',
    name: 'Interest Rate Hike',
    description: 'Fed raises rates by 2%',
    impact: -0.08,
    probability: 0.20
  },
  {
    id: 'inflation_spike',
    name: 'Inflation Spike',
    description: 'CPI increases to 8% annually',
    impact: -0.12,
    probability: 0.15
  },
  {
    id: 'tech_bubble',
    name: 'Tech Bubble Burst',
    description: 'Technology sector drops 30%',
    impact: -0.20,
    probability: 0.08
  }
]

export const RiskAnalysis: React.FC = () => {
  const {
    selectedPortfolio,
    riskMetrics,
    correlationMatrix,
    stressTestScenarios,
    riskFilters,
    setRiskFilters
  } = usePortfolioStore()

  const [activeTab, setActiveTab] = useState<'var' | 'correlation' | 'stress' | 'beta'>('var')

  // Mock risk metrics - in real app, this would come from API
  const mockRiskMetrics: RiskMetrics = useMemo(() => {
    if (!selectedPortfolio) return {
      var95: -0.05,
      var99: -0.08,
      expectedShortfall: -0.07,
      maxDrawdown: -0.15,
      volatility: 0.18,
      sharpeRatio: 1.2,
      beta: 0.95,
      alpha: 0.02,
      trackingError: 0.08,
      informationRatio: 0.25
    }

    // Calculate based on portfolio holdings
    const totalValue = selectedPortfolio.totalValue
    const weightedVolatility = selectedPortfolio.holdings.reduce((sum, holding) => {
      const weight = holding.weight / 100
      const stockVolatility = 0.2 + Math.random() * 0.3 // Mock volatility between 20-50%
      return sum + (weight * stockVolatility)
    }, 0)

    return {
      var95: -0.05 - Math.random() * 0.02,
      var99: -0.08 - Math.random() * 0.03,
      expectedShortfall: -0.07 - Math.random() * 0.02,
      maxDrawdown: -0.15 - Math.random() * 0.05,
      volatility: weightedVolatility,
      sharpeRatio: 0.8 + Math.random() * 0.8,
      beta: 0.7 + Math.random() * 0.6,
      alpha: -0.02 + Math.random() * 0.04,
      trackingError: 0.05 + Math.random() * 0.06,
      informationRatio: -0.1 + Math.random() * 0.4
    }
  }, [selectedPortfolio])

  // Mock correlation matrix
  const mockCorrelationMatrix: CorrelationMatrix = useMemo(() => {
    if (!selectedPortfolio) return { symbols: [], matrix: [] }

    const symbols = selectedPortfolio.holdings.map(h => h.symbol)
    const matrix: number[][] = []

    for (let i = 0; i < symbols.length; i++) {
      matrix[i] = []
      for (let j = 0; j < symbols.length; j++) {
        if (i === j) {
          matrix[i][j] = 1.0
        } else {
          // Generate realistic correlation values
          matrix[i][j] = -0.3 + Math.random() * 0.8
        }
      }
    }

    return { symbols, matrix }
  }, [selectedPortfolio])

  // Mock stress test scenarios with portfolio impact
  const mockStressScenarios: StressTestScenario[] = useMemo(() => {
    if (!selectedPortfolio) return []

    return STRESS_SCENARIOS.map(scenario => ({
      ...scenario,
      portfolioImpact: scenario.impact * (0.8 + Math.random() * 0.4) // Vary impact based on portfolio composition
    }))
  }, [selectedPortfolio])

  // VaR calculation over time
  const varTimeSeries = useMemo(() => {
    const data = []
    const days = 30
    
    for (let i = 0; i < days; i++) {
      const date = new Date()
      date.setDate(date.getDate() - (days - i))
      
      // Simulate VaR changes over time
      const baseVar95 = mockRiskMetrics.var95
      const baseVar99 = mockRiskMetrics.var99
      const volatility = 0.1 + Math.random() * 0.1
      
      data.push({
        date: date.toISOString().split('T')[0],
        var95: baseVar95 * (1 + (Math.random() - 0.5) * volatility),
        var99: baseVar99 * (1 + (Math.random() - 0.5) * volatility),
        portfolioValue: (selectedPortfolio?.totalValue || 100000) * (1 + (Math.random() - 0.5) * 0.02)
      })
    }
    
    return data
  }, [mockRiskMetrics, selectedPortfolio])

  const getCorrelationColor = (value: number): string => {
    const absValue = Math.abs(value)
    if (absValue < 0.2) return '#10b981' // Green for low correlation
    if (absValue < 0.5) return '#f59e0b' // Yellow for medium correlation
    if (absValue < 0.8) return '#f97316' // Orange for high correlation
    return '#ef4444' // Red for very high correlation
  }

  const RiskMetricCard: React.FC<{
    title: string
    value: string | number
    description: string
    variant: 'success' | 'warning' | 'danger' | 'info'
    icon: React.ReactNode
  }> = ({ title, value, description, variant, icon }) => (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {icon}
          <h3 className="text-sm font-medium text-neutral-700">{title}</h3>
        </div>
        <Badge variant={variant}>
          {typeof value === 'number' ? formatPercent(value) : value}
        </Badge>
      </div>
      <p className="text-xs text-neutral-600">{description}</p>
    </Card>
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
      {/* Risk Controls */}
      <Card className="p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4 lg:mb-0">Risk Analysis</h2>
          
          <div className="flex flex-wrap items-center gap-4">
            {/* Confidence Level */}
            <div className="flex items-center space-x-2">
              <ShieldExclamationIcon className="w-4 h-4 text-neutral-500" />
              <select
                value={riskFilters.confidenceLevel}
                onChange={(e) => setRiskFilters({ confidenceLevel: Number(e.target.value) as 95 | 99 })}
                className="text-sm border border-neutral-300 rounded-md px-3 py-1"
              >
                {CONFIDENCE_LEVELS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label} Confidence
                  </option>
                ))}
              </select>
            </div>

            {/* Time Horizon */}
            <div className="flex items-center space-x-2">
              <ChartBarIcon className="w-4 h-4 text-neutral-500" />
              <select
                value={riskFilters.timeHorizon}
                onChange={(e) => setRiskFilters({ timeHorizon: Number(e.target.value) })}
                className="text-sm border border-neutral-300 rounded-md px-3 py-1"
              >
                {TIME_HORIZONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-6">
          <Button
            variant={activeTab === 'var' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('var')}
          >
            Value at Risk
          </Button>
          <Button
            variant={activeTab === 'correlation' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('correlation')}
          >
            Correlation Matrix
          </Button>
          <Button
            variant={activeTab === 'stress' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('stress')}
          >
            Stress Testing
          </Button>
          <Button
            variant={activeTab === 'beta' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('beta')}
          >
            Beta Analysis
          </Button>
        </div>
      </Card>

      {/* Risk Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <RiskMetricCard
          title="VaR (95%)"
          value={mockRiskMetrics.var95}
          description="Maximum expected loss with 95% confidence"
          variant={mockRiskMetrics.var95 > -0.05 ? 'success' : mockRiskMetrics.var95 > -0.1 ? 'warning' : 'danger'}
          icon={<ShieldExclamationIcon className="w-4 h-4 text-blue-600" />}
        />
        
        <RiskMetricCard
          title="VaR (99%)"
          value={mockRiskMetrics.var99}
          description="Maximum expected loss with 99% confidence"
          variant={mockRiskMetrics.var99 > -0.08 ? 'success' : mockRiskMetrics.var99 > -0.15 ? 'warning' : 'danger'}
          icon={<ShieldExclamationIcon className="w-4 h-4 text-purple-600" />}
        />
        
        <RiskMetricCard
          title="Max Drawdown"
          value={mockRiskMetrics.maxDrawdown}
          description="Largest peak-to-trough decline"
          variant={mockRiskMetrics.maxDrawdown > -0.1 ? 'success' : mockRiskMetrics.maxDrawdown > -0.2 ? 'warning' : 'danger'}
          icon={<ExclamationTriangleIcon className="w-4 h-4 text-red-600" />}
        />
        
        <RiskMetricCard
          title="Volatility"
          value={mockRiskMetrics.volatility}
          description="Annualized standard deviation"
          variant={mockRiskMetrics.volatility < 0.2 ? 'success' : mockRiskMetrics.volatility < 0.3 ? 'warning' : 'danger'}
          icon={<ChartBarIcon className="w-4 h-4 text-orange-600" />}
        />
      </div>

      {/* VaR Analysis */}
      {activeTab === 'var' && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Value at Risk Over Time</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={varTimeSeries}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis 
                  tickFormatter={(value) => formatPercent(value)}
                />
                <Tooltip 
                  formatter={(value: number, name: string) => [
                    formatPercent(value),
                    name === 'var95' ? 'VaR (95%)' : name === 'var99' ? 'VaR (99%)' : 'Portfolio Value'
                  ]}
                />
                <Line
                  type="monotone"
                  dataKey="var95"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="VaR (95%)"
                />
                <Line
                  type="monotone"
                  dataKey="var99"
                  stroke="#ef4444"
                  strokeWidth={2}
                  name="VaR (99%)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      )}

      {/* Correlation Matrix */}
      {activeTab === 'correlation' && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Correlation Matrix</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="text-left py-2 px-3 font-medium text-neutral-600"></th>
                  {mockCorrelationMatrix.symbols.map(symbol => (
                    <th key={symbol} className="text-center py-2 px-3 font-medium text-neutral-600 text-sm">
                      {symbol}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {mockCorrelationMatrix.matrix.map((row, i) => (
                  <tr key={mockCorrelationMatrix.symbols[i]}>
                    <td className="text-left py-2 px-3 font-medium text-neutral-600 text-sm">
                      {mockCorrelationMatrix.symbols[i]}
                    </td>
                    {row.map((value, j) => (
                      <td key={j} className="text-center py-2 px-3">
                        <div
                          className="inline-block px-2 py-1 rounded text-xs font-medium text-white"
                          style={{ backgroundColor: getCorrelationColor(value) }}
                        >
                          {value.toFixed(2)}
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 flex items-center space-x-4 text-sm text-neutral-600">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded" style={{ backgroundColor: '#10b981' }}></div>
              <span>Low Correlation (&lt;0.2)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded" style={{ backgroundColor: '#f59e0b' }}></div>
              <span>Medium Correlation (0.2-0.5)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded" style={{ backgroundColor: '#f97316' }}></div>
              <span>High Correlation (0.5-0.8)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded" style={{ backgroundColor: '#ef4444' }}></div>
              <span>Very High Correlation (&gt;0.8)</span>
            </div>
          </div>
        </Card>
      )}

      {/* Stress Testing */}
      {activeTab === 'stress' && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Stress Test Scenarios</h3>
          <div className="space-y-4">
            {mockStressScenarios.map((scenario) => (
              <div key={scenario.id} className="p-4 border border-neutral-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-neutral-900">{scenario.name}</h4>
                  <Badge variant={scenario.portfolioImpact > -0.1 ? 'success' : scenario.portfolioImpact > -0.2 ? 'warning' : 'danger'}>
                    {formatPercent(scenario.portfolioImpact)}
                  </Badge>
                </div>
                <p className="text-sm text-neutral-600 mb-2">{scenario.description}</p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-neutral-500">Probability: {formatPercent(scenario.probability)}</span>
                  <span className="text-neutral-500">
                    Expected Impact: {formatCurrency((selectedPortfolio?.totalValue || 0) * scenario.portfolioImpact)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Beta Analysis */}
      {activeTab === 'beta' && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Beta Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-neutral-900 mb-3">Portfolio Beta</h4>
              <div className="text-3xl font-bold text-neutral-900 mb-2">
                {mockRiskMetrics.beta.toFixed(2)}
              </div>
              <p className="text-sm text-neutral-600">
                {mockRiskMetrics.beta < 1 
                  ? 'Portfolio is less volatile than the market' 
                  : mockRiskMetrics.beta > 1 
                    ? 'Portfolio is more volatile than the market'
                    : 'Portfolio moves in line with the market'
                }
              </p>
            </div>
            
            <div>
              <h4 className="font-medium text-neutral-900 mb-3">Risk-Adjusted Metrics</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-neutral-600">Sharpe Ratio</span>
                  <Badge variant={mockRiskMetrics.sharpeRatio > 1 ? 'success' : 'warning'}>
                    {mockRiskMetrics.sharpeRatio.toFixed(2)}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-neutral-600">Alpha</span>
                  <Badge variant={mockRiskMetrics.alpha > 0 ? 'success' : 'danger'}>
                    {formatPercent(mockRiskMetrics.alpha)}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-neutral-600">Information Ratio</span>
                  <Badge variant={mockRiskMetrics.informationRatio > 0.5 ? 'success' : 'warning'}>
                    {mockRiskMetrics.informationRatio.toFixed(2)}
                  </Badge>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
