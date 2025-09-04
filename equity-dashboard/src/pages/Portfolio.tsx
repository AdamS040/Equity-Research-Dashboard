import { useState } from 'react'
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon,
  EyeIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { cn, formatCurrency, formatPercent, getChangeColor } from '../utils'

// Mock data
const mockPortfolios = [
  {
    id: '1',
    name: 'Growth Portfolio',
    description: 'High-growth technology stocks',
    totalValue: 125430.50,
    totalReturn: 15230.50,
    totalReturnPercent: 13.8,
    holdings: [
      { symbol: 'AAPL', name: 'Apple Inc.', shares: 100, value: 17543.00, weight: 14.0 },
      { symbol: 'GOOGL', name: 'Alphabet Inc.', shares: 50, value: 7128.00, weight: 5.7 },
      { symbol: 'MSFT', name: 'Microsoft Corp.', shares: 30, value: 11365.50, weight: 9.1 },
      { symbol: 'TSLA', name: 'Tesla Inc.', shares: 20, value: 4970.00, weight: 4.0 },
    ]
  },
  {
    id: '2',
    name: 'Dividend Portfolio',
    description: 'Stable dividend-paying stocks',
    totalValue: 87520.25,
    totalReturn: 5230.25,
    totalReturnPercent: 6.4,
    holdings: [
      { symbol: 'JNJ', name: 'Johnson & Johnson', shares: 200, value: 31200.00, weight: 35.6 },
      { symbol: 'PG', name: 'Procter & Gamble', shares: 150, value: 22500.00, weight: 25.7 },
      { symbol: 'KO', name: 'Coca-Cola Co.', shares: 300, value: 18000.00, weight: 20.6 },
    ]
  }
]

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

export const Portfolio = () => {
  const [selectedPortfolio, setSelectedPortfolio] = useState(mockPortfolios[0])
  const [showCreateModal, setShowCreateModal] = useState(false)

  const pieData = selectedPortfolio.holdings.map(holding => ({
    name: holding.symbol,
    value: holding.value,
    weight: holding.weight
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Portfolio Management</h1>
          <p className="text-neutral-600">Manage your investment portfolios and track performance.</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Create Portfolio</span>
        </button>
      </div>

      {/* Portfolio Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mockPortfolios.map((portfolio) => (
          <div
            key={portfolio.id}
            onClick={() => setSelectedPortfolio(portfolio)}
            className={cn(
              'card cursor-pointer transition-all duration-200 hover:shadow-md',
              selectedPortfolio.id === portfolio.id
                ? 'ring-2 ring-primary-500 bg-primary-50'
                : 'hover:bg-neutral-50'
            )}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-neutral-900">{portfolio.name}</h3>
              <div className="flex space-x-1">
                <button className="p-1 text-neutral-400 hover:text-neutral-600">
                  <EyeIcon className="w-4 h-4" />
                </button>
                <button className="p-1 text-neutral-400 hover:text-neutral-600">
                  <PencilIcon className="w-4 h-4" />
                </button>
                <button className="p-1 text-neutral-400 hover:text-danger-600">
                  <TrashIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
            <p className="text-sm text-neutral-600 mb-4">{portfolio.description}</p>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-neutral-600">Total Value</span>
                <span className="font-medium">{formatCurrency(portfolio.totalValue)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-neutral-600">Total Return</span>
                <div className="text-right">
                  <div className={cn('font-medium', getChangeColor(portfolio.totalReturn))}>
                    {portfolio.totalReturn >= 0 ? '+' : ''}{formatCurrency(portfolio.totalReturn)}
                  </div>
                  <div className={cn('text-sm', getChangeColor(portfolio.totalReturn))}>
                    {portfolio.totalReturn >= 0 ? '+' : ''}{formatPercent(portfolio.totalReturnPercent)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Portfolio Details */}
      {selectedPortfolio && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Holdings Table */}
          <div className="lg:col-span-2 card">
            <h2 className="text-lg font-semibold text-neutral-900 mb-6">Holdings</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-neutral-200">
                    <th className="text-left py-3 px-4 font-medium text-neutral-600">Symbol</th>
                    <th className="text-left py-3 px-4 font-medium text-neutral-600">Name</th>
                    <th className="text-right py-3 px-4 font-medium text-neutral-600">Shares</th>
                    <th className="text-right py-3 px-4 font-medium text-neutral-600">Value</th>
                    <th className="text-right py-3 px-4 font-medium text-neutral-600">Weight</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedPortfolio.holdings.map((holding) => (
                    <tr key={holding.symbol} className="border-b border-neutral-100 hover:bg-neutral-50">
                      <td className="py-3 px-4 font-medium text-neutral-900">{holding.symbol}</td>
                      <td className="py-3 px-4 text-neutral-600">{holding.name}</td>
                      <td className="py-3 px-4 text-right">{holding.shares.toLocaleString()}</td>
                      <td className="py-3 px-4 text-right font-medium">{formatCurrency(holding.value)}</td>
                      <td className="py-3 px-4 text-right">{formatPercent(holding.weight)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Portfolio Allocation Chart */}
          <div className="card">
            <h2 className="text-lg font-semibold text-neutral-900 mb-6">Allocation</h2>
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
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => formatCurrency(value)}
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 space-y-2">
              {pieData.map((item, index) => (
                <div key={item.name} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    />
                    <span className="text-sm text-neutral-600">{item.name}</span>
                  </div>
                  <span className="text-sm font-medium text-neutral-900">
                    {formatPercent(item.weight)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Create Portfolio Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">Create New Portfolio</h3>
              <form className="space-y-4">
                <div>
                  <label className="label">Portfolio Name</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="Enter portfolio name"
                  />
                </div>
                <div>
                  <label className="label">Description</label>
                  <textarea
                    className="input"
                    rows={3}
                    placeholder="Enter portfolio description"
                  />
                </div>
                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-primary flex-1"
                  >
                    Create Portfolio
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
