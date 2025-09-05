import React, { useState } from 'react'
import { 
  ChartBarIcon, 
  CalculatorIcon, 
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { formatCurrency, formatPercent, getChangeColor } from '../utils'

// Mock data for analysis
const mockDCFData = {
  symbol: 'AAPL',
  currentPrice: 175.43,
  fairValue: 200.00,
  upside: 24.57,
  upsidePercent: 14.0,
  assumptions: {
    growthRate: 8.5,
    terminalGrowthRate: 2.5,
    discountRate: 10.0,
    taxRate: 21.0
  },
  projections: {
    years: [2024, 2025, 2026, 2027, 2028],
    revenue: [394000, 428000, 465000, 505000, 548000],
    ebitda: [125000, 136000, 148000, 161000, 175000],
    freeCashFlow: [95000, 103000, 112000, 122000, 133000],
    terminalValue: 1850000
  }
}

const mockComparableData = {
  symbol: 'AAPL',
  peers: [
    { symbol: 'MSFT', name: 'Microsoft Corp.', marketCap: 2800000, pe: 28.5, pb: 12.3, ps: 8.2, evEbitda: 20.1 },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', marketCap: 1800000, pe: 25.2, pb: 6.8, ps: 5.9, evEbitda: 15.3 },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', marketCap: 1500000, pe: 45.8, pb: 8.1, ps: 2.8, evEbitda: 18.7 },
    { symbol: 'META', name: 'Meta Platforms Inc.', marketCap: 800000, pe: 22.1, pb: 4.2, ps: 6.5, evEbitda: 12.9 }
  ],
  valuation: {
    peBased: 195.50,
    pbBased: 205.20,
    psBased: 198.80,
    evEbitdaBased: 202.10,
    average: 200.40
  }
}

const mockRiskData = {
  beta: 1.25,
  volatility: 28.5,
  sharpeRatio: 1.45,
  maxDrawdown: -15.2,
  var95: -8.5,
  var99: -12.3
}

const mockMonteCarloData = {
  symbol: 'AAPL',
  simulations: 10000,
  timeHorizon: 252,
  results: {
    mean: 185.50,
    median: 182.30,
    percentile5: 145.20,
    percentile25: 165.80,
    percentile75: 198.40,
    percentile95: 235.60,
    probabilityOfLoss: 0.15,
    expectedReturn: 0.12
  }
}

export const Analysis = () => {
  // Defensive check for React hooks
  if (typeof useState !== 'function') {
    console.error('useState is not available - React may not be properly initialized')
    return <div>Loading...</div>
  }
  
  const [activeTab, setActiveTab] = useState('dcf')

  const tabs = [
    { id: 'dcf', name: 'DCF Analysis', icon: CalculatorIcon },
    { id: 'comparable', name: 'Comparable Analysis', icon: ChartBarIcon },
    { id: 'risk', name: 'Risk Analysis', icon: ExclamationTriangleIcon },
    { id: 'monte-carlo', name: 'Monte Carlo', icon: ArrowTrendingUpIcon }
  ]

  const renderDCFAnalysis = () => (
    <div className="space-y-6">
      {/* DCF Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">DCF Summary</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-neutral-600">Current Price</span>
              <span className="font-medium">{formatCurrency(mockDCFData.currentPrice)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Fair Value</span>
              <span className="font-medium text-success-600">{formatCurrency(mockDCFData.fairValue)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Upside</span>
              <span className="font-medium text-success-600">
                {formatCurrency(mockDCFData.upside)} ({formatPercent(mockDCFData.upsidePercent)})
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Key Assumptions</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-neutral-600">Growth Rate</span>
              <span className="font-medium">{formatPercent(mockDCFData.assumptions.growthRate)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Terminal Growth</span>
              <span className="font-medium">{formatPercent(mockDCFData.assumptions.terminalGrowthRate)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Discount Rate</span>
              <span className="font-medium">{formatPercent(mockDCFData.assumptions.discountRate)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Tax Rate</span>
              <span className="font-medium">{formatPercent(mockDCFData.assumptions.taxRate)}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Recommendation</h3>
          <div className="text-center">
            <div className="text-3xl font-bold text-success-600 mb-2">BUY</div>
            <div className="text-sm text-neutral-600 mb-4">
              Fair value suggests {formatPercent(mockDCFData.upsidePercent)} upside potential
            </div>
            <div className="w-full bg-neutral-200 rounded-full h-2">
              <div 
                className="bg-success-500 h-2 rounded-full" 
                style={{ width: `${Math.min(mockDCFData.upsidePercent * 2, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* DCF Projections Chart */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-6">5-Year Projections</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockDCFData.projections.years.map((year, index) => ({
              year,
              revenue: mockDCFData.projections.revenue[index],
              ebitda: mockDCFData.projections.ebitda[index],
              freeCashFlow: mockDCFData.projections.freeCashFlow[index]
            }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="year" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip 
                formatter={(value: number) => formatCurrency(value)}
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }} 
              />
              <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} name="Revenue" />
              <Line type="monotone" dataKey="ebitda" stroke="#10b981" strokeWidth={2} name="EBITDA" />
              <Line type="monotone" dataKey="freeCashFlow" stroke="#f59e0b" strokeWidth={2} name="Free Cash Flow" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )

  const renderComparableAnalysis = () => (
    <div className="space-y-6">
      {/* Valuation Summary */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-6">Valuation Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-neutral-900">{formatCurrency(mockComparableData.valuation.peBased)}</div>
            <div className="text-sm text-neutral-600">P/E Based</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-neutral-900">{formatCurrency(mockComparableData.valuation.pbBased)}</div>
            <div className="text-sm text-neutral-600">P/B Based</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-neutral-900">{formatCurrency(mockComparableData.valuation.psBased)}</div>
            <div className="text-sm text-neutral-600">P/S Based</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-success-600">{formatCurrency(mockComparableData.valuation.average)}</div>
            <div className="text-sm text-neutral-600">Average</div>
          </div>
        </div>
      </div>

      {/* Peer Comparison Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-6">Peer Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200">
                <th className="text-left py-3 px-4 font-medium text-neutral-600">Company</th>
                <th className="text-right py-3 px-4 font-medium text-neutral-600">Market Cap</th>
                <th className="text-right py-3 px-4 font-medium text-neutral-600">P/E</th>
                <th className="text-right py-3 px-4 font-medium text-neutral-600">P/B</th>
                <th className="text-right py-3 px-4 font-medium text-neutral-600">P/S</th>
                <th className="text-right py-3 px-4 font-medium text-neutral-600">EV/EBITDA</th>
              </tr>
            </thead>
            <tbody>
              {mockComparableData.peers.map((peer) => (
                <tr key={peer.symbol} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="py-3 px-4">
                    <div>
                      <div className="font-medium text-neutral-900">{peer.symbol}</div>
                      <div className="text-sm text-neutral-600">{peer.name}</div>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-right">{formatCurrency(peer.marketCap)}</td>
                  <td className="py-3 px-4 text-right">{peer.pe}</td>
                  <td className="py-3 px-4 text-right">{peer.pb}</td>
                  <td className="py-3 px-4 text-right">{peer.ps}</td>
                  <td className="py-3 px-4 text-right">{peer.evEbitda}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const renderRiskAnalysis = () => (
    <div className="space-y-6">
      {/* Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Market Risk</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-neutral-600">Beta</span>
              <span className="font-medium">{mockRiskData.beta}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Volatility</span>
              <span className="font-medium">{formatPercent(mockRiskData.volatility)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Sharpe Ratio</span>
              <span className="font-medium">{mockRiskData.sharpeRatio}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Downside Risk</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-neutral-600">Max Drawdown</span>
              <span className="font-medium text-danger-600">{formatPercent(mockRiskData.maxDrawdown)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">VaR (95%)</span>
              <span className="font-medium text-danger-600">{formatPercent(mockRiskData.var95)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">VaR (99%)</span>
              <span className="font-medium text-danger-600">{formatPercent(mockRiskData.var99)}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Risk Assessment</h3>
          <div className="text-center">
            <div className="text-2xl font-bold text-warning-600 mb-2">MODERATE</div>
            <div className="text-sm text-neutral-600 mb-4">
              Beta of {mockRiskData.beta} indicates higher volatility than market
            </div>
            <div className="w-full bg-neutral-200 rounded-full h-2">
              <div 
                className="bg-warning-500 h-2 rounded-full" 
                style={{ width: `${(mockRiskData.beta - 0.5) * 50}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderMonteCarlo = () => (
    <div className="space-y-6">
      {/* Monte Carlo Results */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Price Distribution</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-neutral-600">Mean</span>
              <span className="font-medium">{formatCurrency(mockMonteCarloData.results.mean)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Median</span>
              <span className="font-medium">{formatCurrency(mockMonteCarloData.results.median)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">5th Percentile</span>
              <span className="font-medium text-danger-600">{formatCurrency(mockMonteCarloData.results.percentile5)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">95th Percentile</span>
              <span className="font-medium text-success-600">{formatCurrency(mockMonteCarloData.results.percentile95)}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Risk Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-neutral-600">Expected Return</span>
              <span className="font-medium text-success-600">{formatPercent(mockMonteCarloData.results.expectedReturn * 100)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Probability of Loss</span>
              <span className="font-medium text-danger-600">{formatPercent(mockMonteCarloData.results.probabilityOfLoss * 100)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Simulations</span>
              <span className="font-medium">{mockMonteCarloData.simulations.toLocaleString()}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Confidence Intervals</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-neutral-600">25th Percentile</span>
              <span className="font-medium">{formatCurrency(mockMonteCarloData.results.percentile25)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">75th Percentile</span>
              <span className="font-medium">{formatCurrency(mockMonteCarloData.results.percentile75)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Range</span>
              <span className="font-medium">
                {formatCurrency(mockMonteCarloData.results.percentile75 - mockMonteCarloData.results.percentile25)}
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Outlook</h3>
          <div className="text-center">
            <div className="text-2xl font-bold text-success-600 mb-2">POSITIVE</div>
            <div className="text-sm text-neutral-600 mb-4">
              {formatPercent((1 - mockMonteCarloData.results.probabilityOfLoss) * 100)} probability of positive returns
            </div>
            <div className="w-full bg-neutral-200 rounded-full h-2">
              <div 
                className="bg-success-500 h-2 rounded-full" 
                style={{ width: `${(1 - mockMonteCarloData.results.probabilityOfLoss) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Stock Analysis</h1>
        <p className="text-neutral-600">Comprehensive analysis tools for equity research and valuation.</p>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-neutral-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <div className="card">
        {activeTab === 'dcf' && renderDCFAnalysis()}
        {activeTab === 'comparable' && renderComparableAnalysis()}
        {activeTab === 'risk' && renderRiskAnalysis()}
        {activeTab === 'monte-carlo' && renderMonteCarlo()}
      </div>
    </div>
  )
}
