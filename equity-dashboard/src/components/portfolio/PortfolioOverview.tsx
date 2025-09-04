/**
 * Portfolio Overview Component
 * 
 * Displays portfolio summary with total value, P&L, performance metrics, and asset allocation
 */

import React from 'react'
import { 
  ArrowUpIcon, 
  ArrowDownIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { Card, Badge, Spinner } from '../ui'
import { usePortfolioStore } from '../../store/portfolio'
import { formatCurrency, formatPercent, getChangeColor } from '../../utils'

const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', 
  '#8b5cf6', '#06b6d4', '#f97316', '#84cc16',
  '#ec4899', '#6366f1', '#14b8a6', '#f43f5e'
]

export const PortfolioOverview: React.FC = () => {
  const {
    selectedPortfolio,
    portfolioMetrics,
    assetAllocation,
    sectorAllocation,
    isLoading,
    error
  } = usePortfolioStore()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="flex items-center space-x-2 text-red-600">
          <ExclamationTriangleIcon className="w-5 h-5" />
          <span>Error loading portfolio data: {error}</span>
        </div>
      </Card>
    )
  }

  if (!selectedPortfolio || !portfolioMetrics) {
    return (
      <Card className="p-6">
        <div className="text-center text-neutral-600">
          <p>No portfolio selected or data available</p>
        </div>
      </Card>
    )
  }

  const pieData = assetAllocation.map(item => ({
    name: item.symbol,
    value: item.value,
    weight: item.weight,
    color: item.color
  }))

  const sectorPieData = sectorAllocation.map(item => ({
    name: item.sector,
    value: item.value,
    weight: item.weight,
    color: item.color
  }))

  const MetricCard: React.FC<{
    title: string
    value: string
    change?: number
    changePercent?: number
    icon: React.ReactNode
    trend?: 'up' | 'down' | 'neutral'
  }> = ({ title, value, change, changePercent, icon, trend = 'neutral' }) => (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          {icon}
          <h3 className="text-sm font-medium text-neutral-600">{title}</h3>
        </div>
        {trend !== 'neutral' && (
          <div className={`flex items-center space-x-1 ${
            trend === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            {trend === 'up' ? (
              <ArrowUpIcon className="w-4 h-4" />
            ) : (
              <ArrowDownIcon className="w-4 h-4" />
            )}
          </div>
        )}
      </div>
      <div className="space-y-1">
        <div className="text-2xl font-bold text-neutral-900">{value}</div>
        {change !== undefined && changePercent !== undefined && (
          <div className="flex items-center space-x-2">
            <span className={`text-sm font-medium ${getChangeColor(change)}`}>
              {change >= 0 ? '+' : ''}{formatCurrency(change)}
            </span>
            <span className={`text-sm ${getChangeColor(change)}`}>
              ({change >= 0 ? '+' : ''}{formatPercent(changePercent)})
            </span>
          </div>
        )}
      </div>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Value"
          value={formatCurrency(portfolioMetrics.totalValue)}
          change={portfolioMetrics.dayChange}
          changePercent={portfolioMetrics.dayChangePercent}
          icon={<ArrowTrendingUpIcon className="w-5 h-5 text-blue-600" />}
          trend={portfolioMetrics.dayChange >= 0 ? 'up' : 'down'}
        />
        
        <MetricCard
          title="Total Return"
          value={formatCurrency(portfolioMetrics.totalReturn)}
          changePercent={portfolioMetrics.totalReturnPercent}
          icon={<ArrowTrendingUpIcon className="w-5 h-5 text-green-600" />}
          trend={portfolioMetrics.totalReturn >= 0 ? 'up' : 'down'}
        />
        
        <MetricCard
          title="Sharpe Ratio"
          value={portfolioMetrics.sharpeRatio.toFixed(2)}
          icon={<ShieldCheckIcon className="w-5 h-5 text-purple-600" />}
          trend={portfolioMetrics.sharpeRatio >= 1 ? 'up' : portfolioMetrics.sharpeRatio >= 0.5 ? 'neutral' : 'down'}
        />
        
        <MetricCard
          title="Beta"
          value={portfolioMetrics.beta.toFixed(2)}
          icon={<ArrowTrendingDownIcon className="w-5 h-5 text-orange-600" />}
          trend={portfolioMetrics.beta <= 1 ? 'up' : 'down'}
        />
      </div>

      {/* Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Risk Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-neutral-600">VaR (95%)</span>
              <Badge variant={portfolioMetrics.var95 < -0.05 ? 'danger' : 'success'}>
                {formatPercent(portfolioMetrics.var95)}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-neutral-600">VaR (99%)</span>
              <Badge variant={portfolioMetrics.var99 < -0.1 ? 'danger' : 'success'}>
                {formatPercent(portfolioMetrics.var99)}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-neutral-600">Max Drawdown</span>
              <Badge variant={portfolioMetrics.maxDrawdown < -0.2 ? 'danger' : 'warning'}>
                {formatPercent(portfolioMetrics.maxDrawdown)}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-neutral-600">Volatility</span>
              <Badge variant={portfolioMetrics.volatility > 0.3 ? 'danger' : 'success'}>
                {formatPercent(portfolioMetrics.volatility)}
              </Badge>
            </div>
          </div>
        </Card>

        {/* Asset Allocation Chart */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Asset Allocation</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number, name: string, props: any) => [
                    formatCurrency(value),
                    `${props.payload.name} (${formatPercent(props.payload.weight)})`
                  ]}
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }} 
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Sector Allocation Chart */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Sector Allocation</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sectorPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {sectorPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number, name: string, props: any) => [
                    formatCurrency(value),
                    `${props.payload.name} (${formatPercent(props.payload.weight)})`
                  ]}
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }} 
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Top Holdings */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Top Holdings</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-200">
                <th className="text-left py-3 px-4 font-medium text-neutral-600">Symbol</th>
                <th className="text-left py-3 px-4 font-medium text-neutral-600">Name</th>
                <th className="text-right py-3 px-4 font-medium text-neutral-600">Value</th>
                <th className="text-right py-3 px-4 font-medium text-neutral-600">Weight</th>
                <th className="text-right py-3 px-4 font-medium text-neutral-600">Return</th>
              </tr>
            </thead>
            <tbody>
              {selectedPortfolio.holdings
                .sort((a, b) => b.marketValue - a.marketValue)
                .slice(0, 10)
                .map((holding) => (
                <tr key={holding.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                  <td className="py-3 px-4 font-medium text-neutral-900">{holding.symbol}</td>
                  <td className="py-3 px-4 text-neutral-600">{holding.symbol}</td>
                  <td className="py-3 px-4 text-right font-medium">
                    {formatCurrency(holding.marketValue)}
                  </td>
                  <td className="py-3 px-4 text-right">
                    {formatPercent(holding.weight)}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span className={getChangeColor(holding.unrealizedGain)}>
                      {formatPercent(holding.unrealizedGainPercent)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
