import React, { useState } from 'react'
import { Card, Button, Typography, Grid, Flex } from '../components/ui'
import {
  DCFCalculator,
  ComparableAnalysis,
  RiskAnalysis,
  BacktestingEngine,
  OptionsAnalysis,
  EconomicIndicators
} from '../components/analytics'

const Analytics: React.FC = () => {
  const [activeTool, setActiveTool] = useState<string>('dcf')
  const [selectedSymbol, setSelectedSymbol] = useState<string>('AAPL')

  const analyticsTools = [
    {
      id: 'dcf',
      name: 'DCF Calculator',
      description: 'Discounted Cash Flow analysis with sensitivity and Monte Carlo simulation',
      icon: '💰',
      component: DCFCalculator
    },
    {
      id: 'comparable',
      name: 'Comparable Analysis',
      description: 'Peer company valuation and benchmarking analysis',
      icon: '📊',
      component: ComparableAnalysis
    },
    {
      id: 'risk',
      name: 'Risk Analysis',
      description: 'Portfolio risk metrics, VaR, and stress testing',
      icon: '⚠️',
      component: RiskAnalysis
    },
    {
      id: 'backtesting',
      name: 'Backtesting Engine',
      description: 'Historical strategy performance testing and optimization',
      icon: '🔄',
      component: BacktestingEngine
    },
    {
      id: 'options',
      name: 'Options Analysis',
      description: 'Options pricing, Greeks, and strategy analysis',
      icon: '📈',
      component: OptionsAnalysis
    },
    {
      id: 'economic',
      name: 'Economic Indicators',
      description: 'Key economic data and market sentiment analysis',
      icon: '🌍',
      component: EconomicIndicators
    }
  ]

  const ActiveComponent = analyticsTools.find(tool => tool.id === activeTool)?.component

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Typography variant="h1" className="text-3xl font-bold text-gray-900 mb-2">
            Financial Analytics Tools
          </Typography>
          <Typography variant="body1" className="text-gray-600">
            Advanced financial modeling and analysis tools for comprehensive equity research
          </Typography>
        </div>

        {/* Tool Selection */}
        <Card className="mb-8">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <Typography variant="h2" className="text-xl font-semibold">
                Select Analytics Tool
              </Typography>
              <div className="flex items-center gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Symbol
                  </label>
                  <input
                    type="text"
                    value={selectedSymbol}
                    onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
                    className="border border-gray-300 rounded-md px-3 py-2 w-24"
                    placeholder="AAPL"
                  />
                </div>
              </div>
            </div>

            <Grid cols={3} gap={4}>
              {analyticsTools.map((tool) => (
                <Card
                  key={tool.id}
                  className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                    activeTool === tool.id
                      ? 'ring-2 ring-blue-500 bg-blue-50'
                      : 'hover:bg-gray-50'
                  }`}
                  onClick={() => setActiveTool(tool.id)}
                >
                  <div className="p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-2xl">{tool.icon}</span>
                      <Typography variant="h3" className="font-semibold">
                        {tool.name}
                      </Typography>
                    </div>
                    <Typography variant="body2" className="text-gray-600">
                      {tool.description}
                    </Typography>
                  </div>
                </Card>
              ))}
            </Grid>
          </div>
        </Card>

        {/* Active Tool */}
        {ActiveComponent && (
          <div className="mb-8">
            <ActiveComponent symbol={selectedSymbol} />
          </div>
        )}

        {/* Quick Stats */}
        <Card>
          <div className="p-6">
            <Typography variant="h2" className="text-xl font-semibold mb-4">
              Analytics Overview
            </Typography>
            <Grid cols={4} gap={4}>
              <div className="text-center">
                <Typography variant="h3" className="text-2xl font-bold text-blue-600">
                  6
                </Typography>
                <Typography variant="body2" className="text-gray-600">
                  Analytics Tools
                </Typography>
              </div>
              <div className="text-center">
                <Typography variant="h3" className="text-2xl font-bold text-green-600">
                  15+
                </Typography>
                <Typography variant="body2" className="text-gray-600">
                  Financial Models
                </Typography>
              </div>
              <div className="text-center">
                <Typography variant="h3" className="text-2xl font-bold text-purple-600">
                  50+
                </Typography>
                <Typography variant="body2" className="text-gray-600">
                  Risk Metrics
                </Typography>
              </div>
              <div className="text-center">
                <Typography variant="h3" className="text-2xl font-bold text-orange-600">
                  100%
                </Typography>
                <Typography variant="body2" className="text-gray-600">
                  Real-time Data
                </Typography>
              </div>
            </Grid>
          </div>
        </Card>

        {/* Features */}
        <div className="mt-8">
          <Typography variant="h2" className="text-2xl font-bold text-gray-900 mb-6">
            Key Features
          </Typography>
          <Grid cols={2} gap={6}>
            <Card>
              <div className="p-6">
                <Typography variant="h3" className="text-lg font-semibold mb-3">
                  🎯 Advanced Financial Modeling
                </Typography>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• DCF analysis with Monte Carlo simulation</li>
                  <li>• Comparable company valuation</li>
                  <li>• Options pricing with Black-Scholes model</li>
                  <li>• Portfolio optimization algorithms</li>
                </ul>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <Typography variant="h3" className="text-lg font-semibold mb-3">
                  📊 Risk Management
                </Typography>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Value at Risk (VaR) calculations</li>
                  <li>• Stress testing scenarios</li>
                  <li>• Correlation analysis</li>
                  <li>• Greeks analysis for options</li>
                </ul>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <Typography variant="h3" className="text-lg font-semibold mb-3">
                  🔄 Backtesting & Strategy
                </Typography>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Historical strategy performance</li>
                  <li>• Portfolio optimization backtesting</li>
                  <li>• Risk-adjusted return analysis</li>
                  <li>• Benchmark comparison</li>
                </ul>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <Typography variant="h3" className="text-lg font-semibold mb-3">
                  🌍 Economic Analysis
                </Typography>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Real-time economic indicators</li>
                  <li>• Interest rate analysis</li>
                  <li>• Inflation tracking</li>
                  <li>• Market sentiment indicators</li>
                </ul>
              </div>
            </Card>
          </Grid>
        </div>
      </div>
    </div>
  )
}

export default Analytics
