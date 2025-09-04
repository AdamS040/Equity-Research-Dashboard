import { useState } from 'react'
import { 
  TrendingUpIcon, 
  TrendingDownIcon, 
  ChartBarIcon,
  CurrencyDollarIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { cn, formatCurrency, formatPercent, getChangeColor } from '../utils'

// Mock data for demonstration
const mockData = [
  { name: 'Jan', value: 4000, change: 5.2 },
  { name: 'Feb', value: 3000, change: -2.1 },
  { name: 'Mar', value: 5000, change: 8.7 },
  { name: 'Apr', value: 4500, change: -1.3 },
  { name: 'May', value: 6000, change: 12.4 },
  { name: 'Jun', value: 5500, change: -3.2 },
]

const mockStocks = [
  { symbol: 'AAPL', name: 'Apple Inc.', price: 175.43, change: 2.34, changePercent: 1.35 },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 142.56, change: -1.23, changePercent: -0.85 },
  { symbol: 'MSFT', name: 'Microsoft Corp.', price: 378.85, change: 5.67, changePercent: 1.52 },
  { symbol: 'TSLA', name: 'Tesla Inc.', price: 248.50, change: -3.21, changePercent: -1.27 },
]

const mockMetrics = [
  { label: 'Total Portfolio Value', value: '$125,430.50', change: 2.34, changePercent: 1.89 },
  { label: 'Total Return', value: '$15,230.50', change: 1.23, changePercent: 8.78 },
  { label: 'Today\'s P&L', value: '$2,340.00', change: -0.45, changePercent: -0.19 },
  { label: 'Win Rate', value: '68.5%', change: 0, changePercent: 0 },
]

export const Dashboard = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('1M')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Dashboard</h1>
          <p className="text-neutral-600">Welcome back! Here's your portfolio overview.</p>
        </div>
        <div className="flex space-x-2">
          {['1D', '1W', '1M', '3M', '1Y'].map((period) => (
            <button
              key={period}
              onClick={() => setSelectedPeriod(period)}
              className={cn(
                'px-3 py-1 text-sm font-medium rounded-lg transition-colors',
                selectedPeriod === period
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-neutral-600 hover:bg-neutral-100'
              )}
            >
              {period}
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {mockMetrics.map((metric, index) => (
          <div key={index} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-neutral-600">{metric.label}</p>
                <p className="text-2xl font-bold text-neutral-900 mt-1">{metric.value}</p>
              </div>
              <div className={cn(
                'flex items-center space-x-1 px-2 py-1 rounded-full text-sm',
                metric.change >= 0 ? 'bg-success-50 text-success-700' : 'bg-danger-50 text-danger-700'
              )}>
                {metric.change >= 0 ? (
                  <ArrowUpIcon className="w-4 h-4" />
                ) : (
                  <ArrowDownIcon className="w-4 h-4" />
                )}
                <span>{formatPercent(metric.changePercent)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Chart and Top Holdings */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Portfolio Performance Chart */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-neutral-900">Portfolio Performance</h2>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                <span className="text-sm text-neutral-600">Portfolio Value</span>
              </div>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mockData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Holdings */}
        <div className="card">
          <h2 className="text-lg font-semibold text-neutral-900 mb-6">Top Holdings</h2>
          <div className="space-y-4">
            {mockStocks.map((stock) => (
              <div key={stock.symbol} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-neutral-900">{stock.symbol}</p>
                  <p className="text-sm text-neutral-600">{stock.name}</p>
                </div>
                <div className="text-right">
                  <p className="font-medium text-neutral-900">{formatCurrency(stock.price)}</p>
                  <p className={cn('text-sm', getChangeColor(stock.change))}>
                    {stock.change >= 0 ? '+' : ''}{formatPercent(stock.changePercent)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-lg font-semibold text-neutral-900 mb-6">Recent Activity</h2>
        <div className="space-y-4">
          {[
            { action: 'Bought', symbol: 'AAPL', shares: 10, price: 175.43, time: '2 hours ago' },
            { action: 'Sold', symbol: 'GOOGL', shares: 5, price: 142.56, time: '1 day ago' },
            { action: 'Bought', symbol: 'MSFT', shares: 8, price: 378.85, time: '2 days ago' },
          ].map((activity, index) => (
            <div key={index} className="flex items-center justify-between py-3 border-b border-neutral-200 last:border-b-0">
              <div className="flex items-center space-x-3">
                <div className={cn(
                  'w-8 h-8 rounded-full flex items-center justify-center',
                  activity.action === 'Bought' ? 'bg-success-100' : 'bg-danger-100'
                )}>
                  {activity.action === 'Bought' ? (
                    <TrendingUpIcon className="w-4 h-4 text-success-600" />
                  ) : (
                    <TrendingDownIcon className="w-4 h-4 text-danger-600" />
                  )}
                </div>
                <div>
                  <p className="font-medium text-neutral-900">
                    {activity.action} {activity.shares} shares of {activity.symbol}
                  </p>
                  <p className="text-sm text-neutral-600">{activity.time}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-medium text-neutral-900">{formatCurrency(activity.price)}</p>
                <p className="text-sm text-neutral-600">per share</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
