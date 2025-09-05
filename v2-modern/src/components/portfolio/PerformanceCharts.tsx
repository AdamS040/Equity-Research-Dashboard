/**
 * Performance Charts Component
 * 
 * Portfolio value over time, cumulative returns, rolling returns, and benchmark comparison
 */

import React, { useState, useMemo } from 'react'
import { 
  ChartBarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  CalendarIcon
} from '@heroicons/react/24/outline'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar
} from 'recharts'
import { Card, Button, Badge } from '../ui'
import { usePortfolioStore } from '../../store/portfolio'
import { PerformanceData, PerformanceChartFilters } from '../../types/portfolio'
import { formatCurrency, formatPercent, getChangeColor } from '../../utils'

const PERIOD_OPTIONS = [
  { value: '1d', label: '1 Day' },
  { value: '1w', label: '1 Week' },
  { value: '1m', label: '1 Month' },
  { value: '3m', label: '3 Months' },
  { value: '6m', label: '6 Months' },
  { value: '1y', label: '1 Year' },
  { value: 'all', label: 'All Time' }
]

const BENCHMARK_OPTIONS = [
  { value: 'SPY', label: 'S&P 500 (SPY)' },
  { value: 'QQQ', label: 'NASDAQ (QQQ)' },
  { value: 'IWM', label: 'Russell 2000 (IWM)' },
  { value: 'VTI', label: 'Total Stock Market (VTI)' }
]

export const PerformanceCharts: React.FC = () => {
  const {
    selectedPortfolio,
    performanceData,
    performanceFilters,
    setPerformanceFilters
  } = usePortfolioStore()

  const [activeChart, setActiveChart] = useState<'value' | 'returns' | 'drawdown' | 'rolling'>('value')

  // Mock performance data - in real app, this would come from API
  const mockPerformanceData: PerformanceData[] = useMemo(() => {
    const data: PerformanceData[] = []
    const startDate = new Date()
    const days = performanceFilters.period === '1d' ? 1 : 
                 performanceFilters.period === '1w' ? 7 :
                 performanceFilters.period === '1m' ? 30 :
                 performanceFilters.period === '3m' ? 90 :
                 performanceFilters.period === '6m' ? 180 :
                 performanceFilters.period === '1y' ? 365 : 1095

    let portfolioValue = selectedPortfolio?.totalValue || 100000
    let benchmarkValue = 100000
    let cumulativeReturn = 0

    for (let i = days; i >= 0; i--) {
      const date = new Date(startDate)
      date.setDate(date.getDate() - i)
      
      // Generate realistic price movements
      const portfolioReturn = (Math.random() - 0.5) * 0.04 // ±2% daily volatility
      const benchmarkReturn = (Math.random() - 0.5) * 0.025 // ±1.25% daily volatility
      
      portfolioValue *= (1 + portfolioReturn)
      benchmarkValue *= (1 + benchmarkReturn)
      
      const dailyReturn = portfolioReturn
      cumulativeReturn += dailyReturn
      
      const drawdown = Math.min(0, portfolioValue / (selectedPortfolio?.totalValue || 100000) - 1)

      data.push({
        date: date.toISOString().split('T')[0],
        portfolioValue,
        benchmarkValue,
        returns: dailyReturn * 100,
        cumulativeReturns: cumulativeReturn * 100,
        drawdown: drawdown * 100
      })
    }

    return data
  }, [performanceFilters.period, selectedPortfolio])

  // Calculate rolling returns (30-day)
  const rollingReturnsData = useMemo(() => {
    if (mockPerformanceData.length < 30) return []
    
    return mockPerformanceData.slice(29).map((point, index) => {
      const startValue = mockPerformanceData[index].portfolioValue
      const endValue = point.portfolioValue
      const rollingReturn = ((endValue - startValue) / startValue) * 100
      
      return {
        ...point,
        rollingReturn
      }
    })
  }, [mockPerformanceData])

  // Calculate performance metrics
  const performanceMetrics = useMemo(() => {
    if (mockPerformanceData.length === 0) return null

    const portfolioReturns = mockPerformanceData.map(d => d.returns)
    const benchmarkReturns = mockPerformanceData.map(d => 
      ((d.benchmarkValue - mockPerformanceData[0].benchmarkValue) / mockPerformanceData[0].benchmarkValue) * 100
    )

    const portfolioTotalReturn = ((mockPerformanceData[mockPerformanceData.length - 1].portfolioValue - mockPerformanceData[0].portfolioValue) / mockPerformanceData[0].portfolioValue) * 100
    const benchmarkTotalReturn = ((mockPerformanceData[mockPerformanceData.length - 1].benchmarkValue - mockPerformanceData[0].benchmarkValue) / mockPerformanceData[0].benchmarkValue) * 100

    const portfolioVolatility = Math.sqrt(portfolioReturns.reduce((sum, r) => sum + r * r, 0) / portfolioReturns.length)
    const benchmarkVolatility = Math.sqrt(benchmarkReturns.reduce((sum, r) => sum + r * r, 0) / benchmarkReturns.length)

    const maxDrawdown = Math.min(...mockPerformanceData.map(d => d.drawdown))
    const sharpeRatio = portfolioTotalReturn / portfolioVolatility

    return {
      portfolioTotalReturn,
      benchmarkTotalReturn,
      excessReturn: portfolioTotalReturn - benchmarkTotalReturn,
      portfolioVolatility,
      benchmarkVolatility,
      maxDrawdown,
      sharpeRatio
    }
  }, [mockPerformanceData])

  const ChartButton: React.FC<{
    chart: 'value' | 'returns' | 'drawdown' | 'rolling'
    children: React.ReactNode
  }> = ({ chart, children }) => (
    <Button
      variant={activeChart === chart ? 'primary' : 'outline'}
      size="sm"
      onClick={() => setActiveChart(chart)}
    >
      {children}
    </Button>
  )

  const CustomTooltip: React.FC<any> = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-neutral-800 p-3 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-neutral-900 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.name.includes('Return') || entry.name.includes('Drawdown') 
                ? formatPercent(entry.value / 100) 
                : formatCurrency(entry.value)}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

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
      {/* Performance Metrics */}
      {performanceMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-600">Portfolio Return</span>
              <Badge variant={performanceMetrics.portfolioTotalReturn >= 0 ? 'success' : 'danger'}>
                {performanceMetrics.portfolioTotalReturn >= 0 ? '+' : ''}{formatPercent(performanceMetrics.portfolioTotalReturn / 100)}
              </Badge>
            </div>
            <div className="text-2xl font-bold text-neutral-900">
              {formatPercent(performanceMetrics.portfolioTotalReturn / 100)}
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-600">Benchmark Return</span>
              <Badge variant={performanceMetrics.benchmarkTotalReturn >= 0 ? 'success' : 'danger'}>
                {performanceMetrics.benchmarkTotalReturn >= 0 ? '+' : ''}{formatPercent(performanceMetrics.benchmarkTotalReturn / 100)}
              </Badge>
            </div>
            <div className="text-2xl font-bold text-neutral-900">
              {formatPercent(performanceMetrics.benchmarkTotalReturn / 100)}
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-600">Excess Return</span>
              <Badge variant={performanceMetrics.excessReturn >= 0 ? 'success' : 'danger'}>
                {performanceMetrics.excessReturn >= 0 ? '+' : ''}{formatPercent(performanceMetrics.excessReturn / 100)}
              </Badge>
            </div>
            <div className="text-2xl font-bold text-neutral-900">
              {formatPercent(performanceMetrics.excessReturn / 100)}
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-600">Max Drawdown</span>
              <Badge variant={performanceMetrics.maxDrawdown > -0.1 ? 'success' : 'danger'}>
                {formatPercent(performanceMetrics.maxDrawdown / 100)}
              </Badge>
            </div>
            <div className="text-2xl font-bold text-neutral-900">
              {formatPercent(performanceMetrics.maxDrawdown / 100)}
            </div>
          </Card>
        </div>
      )}

      {/* Chart Controls */}
      <Card className="p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4 lg:mb-0">Performance Analysis</h2>
          
          <div className="flex flex-wrap items-center gap-4">
            {/* Period Selection */}
            <div className="flex items-center space-x-2">
              <CalendarIcon className="w-4 h-4 text-neutral-500" />
              <select
                value={performanceFilters.period}
                onChange={(e) => setPerformanceFilters({ period: e.target.value as any })}
                className="text-sm border border-neutral-300 rounded-md px-3 py-1"
              >
                {PERIOD_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Benchmark Selection */}
            <div className="flex items-center space-x-2">
              <ChartBarIcon className="w-4 h-4 text-neutral-500" />
              <select
                value={performanceFilters.benchmark}
                onChange={(e) => setPerformanceFilters({ benchmark: e.target.value })}
                className="text-sm border border-neutral-300 rounded-md px-3 py-1"
              >
                {BENCHMARK_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Chart Type Buttons */}
        <div className="flex flex-wrap gap-2 mb-6">
          <ChartButton chart="value">Portfolio Value</ChartButton>
          <ChartButton chart="returns">Cumulative Returns</ChartButton>
          <ChartButton chart="drawdown">Drawdown</ChartButton>
          <ChartButton chart="rolling">Rolling Returns</ChartButton>
        </div>

        {/* Chart */}
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            {activeChart === 'value' && (
              <AreaChart data={mockPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis 
                  tickFormatter={(value) => formatCurrency(value)}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="portfolioValue"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.3}
                  name="Portfolio Value"
                />
                <Area
                  type="monotone"
                  dataKey="benchmarkValue"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.3}
                  name={`${performanceFilters.benchmark} Benchmark`}
                />
              </AreaChart>
            )}

            {activeChart === 'returns' && (
              <LineChart data={mockPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis 
                  tickFormatter={(value) => formatPercent(value / 100)}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="cumulativeReturns"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="Portfolio Returns"
                />
                <Line
                  type="monotone"
                  dataKey="returns"
                  stroke="#10b981"
                  strokeWidth={2}
                  name="Daily Returns"
                />
              </LineChart>
            )}

            {activeChart === 'drawdown' && (
              <AreaChart data={mockPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis 
                  tickFormatter={(value) => formatPercent(value / 100)}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="drawdown"
                  stroke="#ef4444"
                  fill="#ef4444"
                  fillOpacity={0.3}
                  name="Drawdown"
                />
              </AreaChart>
            )}

            {activeChart === 'rolling' && (
              <BarChart data={rollingReturnsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis 
                  tickFormatter={(value) => formatPercent(value / 100)}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar
                  dataKey="rollingReturn"
                  fill="#8b5cf6"
                  name="30-Day Rolling Returns"
                />
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  )
}
