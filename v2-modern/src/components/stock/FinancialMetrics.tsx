import React, { useState, useMemo } from 'react'
import { clsx } from 'clsx'
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Badge, 
  Spinner 
} from '../ui'
import { 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyDollarIcon,
  BanknotesIcon,
  ScaleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts'
import { FinancialMetrics as FinancialMetricsType } from '../../types/api'

interface FinancialMetricsProps {
  symbol: string
  data: FinancialMetricsType[]
  loading?: boolean
}

interface MetricCategory {
  name: string
  icon: React.ComponentType<any>
  metrics: {
    name: string
    value: number
    unit: string
    trend: 'up' | 'down' | 'neutral'
    description: string
  }[]
}

export const FinancialMetrics: React.FC<FinancialMetricsProps> = ({
  symbol,
  data,
  loading = false
}) => {
  const [selectedPeriod, setSelectedPeriod] = useState<'annual' | 'quarterly'>('annual')
  const [selectedCategory, setSelectedCategory] = useState<'profitability' | 'liquidity' | 'leverage' | 'efficiency' | 'growth'>('profitability')

  // Process financial data
  const processedData = useMemo(() => {
    if (!data || data.length === 0) return { annual: [], quarterly: [] }

    const annual = data.filter(d => d.period === 'annual').sort((a, b) => b.year - a.year)
    const quarterly = data.filter(d => d.period === 'quarterly').sort((a, b) => {
      if (a.year !== b.year) return b.year - a.year
      return (b.quarter || 0) - (a.quarter || 0)
    })

    return { annual, quarterly }
  }, [data])

  const currentData = processedData[selectedPeriod]
  const latestData = currentData[0]

  // Define metric categories
  const metricCategories: Record<string, MetricCategory> = useMemo(() => {
    if (!latestData) return {}

    return {
      profitability: {
        name: 'Profitability',
        icon: ArrowTrendingUpIcon,
        metrics: [
          {
            name: 'Return on Equity (ROE)',
            value: latestData.roe,
            unit: '%',
            trend: latestData.roe > 15 ? 'up' : latestData.roe < 10 ? 'down' : 'neutral',
            description: 'Measures how effectively a company uses shareholders\' equity'
          },
          {
            name: 'Return on Assets (ROA)',
            value: latestData.roa,
            unit: '%',
            trend: latestData.roa > 5 ? 'up' : latestData.roa < 3 ? 'down' : 'neutral',
            description: 'Indicates how efficiently a company uses its assets'
          },
          {
            name: 'Gross Margin',
            value: latestData.grossMargin,
            unit: '%',
            trend: latestData.grossMargin > 40 ? 'up' : latestData.grossMargin < 20 ? 'down' : 'neutral',
            description: 'Percentage of revenue remaining after cost of goods sold'
          },
          {
            name: 'Operating Margin',
            value: latestData.operatingMargin,
            unit: '%',
            trend: latestData.operatingMargin > 15 ? 'up' : latestData.operatingMargin < 5 ? 'down' : 'neutral',
            description: 'Percentage of revenue remaining after operating expenses'
          },
          {
            name: 'Net Margin',
            value: latestData.netMargin,
            unit: '%',
            trend: latestData.netMargin > 10 ? 'up' : latestData.netMargin < 3 ? 'down' : 'neutral',
            description: 'Percentage of revenue remaining after all expenses'
          }
        ]
      },
      liquidity: {
        name: 'Liquidity',
        icon: BanknotesIcon,
        metrics: [
          {
            name: 'Current Ratio',
            value: latestData.currentRatio,
            unit: 'x',
            trend: latestData.currentRatio > 2 ? 'up' : latestData.currentRatio < 1 ? 'down' : 'neutral',
            description: 'Ability to pay short-term obligations with current assets'
          },
          {
            name: 'Quick Ratio',
            value: latestData.currentRatio * 0.8, // Approximation
            unit: 'x',
            trend: latestData.currentRatio > 1.5 ? 'up' : latestData.currentRatio < 0.8 ? 'down' : 'neutral',
            description: 'Ability to pay short-term obligations with liquid assets'
          },
          {
            name: 'Cash Ratio',
            value: latestData.currentRatio * 0.3, // Approximation
            unit: 'x',
            trend: latestData.currentRatio > 0.5 ? 'up' : latestData.currentRatio < 0.2 ? 'down' : 'neutral',
            description: 'Ability to pay short-term obligations with cash only'
          }
        ]
      },
      leverage: {
        name: 'Leverage',
        icon: ScaleIcon,
        metrics: [
          {
            name: 'Debt-to-Equity',
            value: latestData.debtToEquity,
            unit: 'x',
            trend: latestData.debtToEquity < 0.5 ? 'up' : latestData.debtToEquity > 1 ? 'down' : 'neutral',
            description: 'Ratio of total debt to shareholders\' equity'
          },
          {
            name: 'Interest Coverage',
            value: (latestData.operatingMargin * latestData.revenue) / (latestData.debtToEquity * latestData.equity * 0.05), // Approximation
            unit: 'x',
            trend: latestData.debtToEquity < 0.5 ? 'up' : latestData.debtToEquity > 1 ? 'down' : 'neutral',
            description: 'Ability to pay interest on outstanding debt'
          },
          {
            name: 'Debt-to-Assets',
            value: latestData.debtToEquity / (1 + latestData.debtToEquity),
            unit: '%',
            trend: latestData.debtToEquity < 0.5 ? 'up' : latestData.debtToEquity > 1 ? 'down' : 'neutral',
            description: 'Percentage of assets financed by debt'
          }
        ]
      },
      efficiency: {
        name: 'Efficiency',
        icon: ClockIcon,
        metrics: [
          {
            name: 'Asset Turnover',
            value: latestData.revenue / latestData.totalAssets,
            unit: 'x',
            trend: latestData.revenue / latestData.totalAssets > 1 ? 'up' : latestData.revenue / latestData.totalAssets < 0.5 ? 'down' : 'neutral',
            description: 'How efficiently a company uses its assets to generate revenue'
          },
          {
            name: 'Inventory Turnover',
            value: latestData.revenue / (latestData.totalAssets * 0.1), // Approximation
            unit: 'x',
            trend: 'neutral',
            description: 'How many times inventory is sold and replaced'
          },
          {
            name: 'Receivables Turnover',
            value: latestData.revenue / (latestData.totalAssets * 0.15), // Approximation
            unit: 'x',
            trend: 'neutral',
            description: 'How efficiently a company collects on its receivables'
          }
        ]
      },
      growth: {
        name: 'Growth',
        icon: ArrowTrendingUpIcon,
        metrics: [
          {
            name: 'Revenue Growth',
            value: currentData.length > 1 ? ((latestData.revenue - currentData[1].revenue) / currentData[1].revenue) * 100 : 0,
            unit: '%',
            trend: currentData.length > 1 && latestData.revenue > currentData[1].revenue ? 'up' : 'down',
            description: 'Year-over-year revenue growth rate'
          },
          {
            name: 'Earnings Growth',
            value: currentData.length > 1 ? ((latestData.netIncome - currentData[1].netIncome) / currentData[1].netIncome) * 100 : 0,
            unit: '%',
            trend: currentData.length > 1 && latestData.netIncome > currentData[1].netIncome ? 'up' : 'down',
            description: 'Year-over-year earnings growth rate'
          },
          {
            name: 'EPS Growth',
            value: currentData.length > 1 ? ((latestData.eps - currentData[1].eps) / currentData[1].eps) * 100 : 0,
            unit: '%',
            trend: currentData.length > 1 && latestData.eps > currentData[1].eps ? 'up' : 'down',
            description: 'Year-over-year earnings per share growth rate'
          }
        ]
      }
    }
  }, [latestData, currentData])

  const formatValue = (value: number, unit: string) => {
    if (unit === '%') {
      return `${value.toFixed(2)}%`
    } else if (unit === 'x') {
      return `${value.toFixed(2)}x`
    } else {
      return value.toFixed(2)
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />
      case 'down':
        return <ArrowTrendingDownIcon className="w-4 h-4 text-red-500" />
      default:
        return <div className="w-4 h-4 bg-neutral-400 rounded-full" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'down':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-neutral-600 bg-neutral-50 border-neutral-200'
    }
  }

  // Prepare chart data for trends
  const chartData = useMemo(() => {
    return currentData.map(item => ({
      year: item.year,
      quarter: item.quarter,
      period: item.quarter ? `Q${item.quarter} ${item.year}` : item.year.toString(),
      revenue: item.revenue,
      netIncome: item.netIncome,
      roe: item.roe,
      roa: item.roa,
      currentRatio: item.currentRatio,
      debtToEquity: item.debtToEquity
    }))
  }, [currentData])

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-neutral-800 p-3 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-lg">
          <p className="font-medium text-neutral-900 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value?.toFixed(2) || 'N/A'}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  if (loading) {
    return (
      <Card className="mb-6">
        <CardHeader 
          title="Financial Metrics" 
          subtitle={`${symbol} - Loading financial data...`}
        />
        <CardBody className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </CardBody>
      </Card>
    )
  }

  if (!data || data.length === 0) {
    return (
      <Card className="mb-6">
        <CardHeader 
          title="Financial Metrics" 
          subtitle={`${symbol} - No data available`}
        />
        <CardBody className="flex items-center justify-center py-12">
          <div className="text-center">
            <ChartBarIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <p className="text-neutral-600">No financial metrics data available</p>
          </div>
        </CardBody>
      </Card>
    )
  }

  const currentCategory = metricCategories[selectedCategory]

  return (
    <div className="space-y-6">
      {/* Period Selector */}
      <Card>
        <CardHeader 
          title="Financial Metrics" 
          subtitle={`${symbol} - ${selectedPeriod} data`}
          actions={
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedPeriod('annual')}
                className={clsx(
                  'px-3 py-1 rounded-md text-sm font-medium transition-colors',
                  selectedPeriod === 'annual'
                    ? 'bg-blue-100 text-blue-800'
                    : 'text-neutral-600 hover:text-neutral-900'
                )}
              >
                Annual
              </button>
              <button
                onClick={() => setSelectedPeriod('quarterly')}
                className={clsx(
                  'px-3 py-1 rounded-md text-sm font-medium transition-colors',
                  selectedPeriod === 'quarterly'
                    ? 'bg-blue-100 text-blue-800'
                    : 'text-neutral-600 hover:text-neutral-900'
                )}
              >
                Quarterly
              </button>
            </div>
          }
        />
        <CardBody>
          {/* Category Selector */}
          <div className="flex flex-wrap gap-2 mb-6">
            {Object.entries(metricCategories).map(([key, category]) => (
              <button
                key={key}
                onClick={() => setSelectedCategory(key as any)}
                className={clsx(
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  selectedCategory === key
                    ? 'bg-blue-100 text-blue-800'
                    : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100'
                )}
              >
                <category.icon className="w-4 h-4" />
                {category.name}
              </button>
            ))}
          </div>

          {/* Current Category Metrics */}
          {currentCategory && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {currentCategory.metrics.map((metric, index) => (
                <div
                  key={index}
                  className={clsx(
                    'p-4 rounded-lg border-2',
                    getTrendColor(metric.trend)
                  )}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-sm">{metric.name}</h3>
                    {getTrendIcon(metric.trend)}
                  </div>
                  <p className="text-2xl font-bold mb-1">
                    {formatValue(metric.value, metric.unit)}
                  </p>
                  <p className="text-xs opacity-75">
                    {metric.description}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Financial Trends Chart */}
      <Card>
        <CardHeader 
          title="Financial Trends" 
          subtitle={`${symbol} - ${selectedPeriod} trends`}
        />
        <CardBody>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="period" 
                  stroke="#666"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  stroke="#666"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => {
                    if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`
                    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`
                    if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`
                    return value.toFixed(0)
                  }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stackId="1"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.3}
                />
                <Area
                  type="monotone"
                  dataKey="netIncome"
                  stackId="2"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardBody>
      </Card>

      {/* Key Ratios Chart */}
      <Card>
        <CardHeader 
          title="Key Ratios" 
          subtitle={`${symbol} - Important financial ratios`}
        />
        <CardBody>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="period" 
                  stroke="#666"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  stroke="#666"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="roe"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  dot={false}
                  name="ROE (%)"
                />
                <Line
                  type="monotone"
                  dataKey="roa"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  dot={false}
                  name="ROA (%)"
                />
                <Line
                  type="monotone"
                  dataKey="currentRatio"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={false}
                  name="Current Ratio"
                />
                <Line
                  type="monotone"
                  dataKey="debtToEquity"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                  name="Debt/Equity"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
