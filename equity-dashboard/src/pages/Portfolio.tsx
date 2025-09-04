/**
 * Updated Portfolio Page
 * 
 * Main portfolio management page with comprehensive portfolio system
 */

import React, { useState, useEffect } from 'react'
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon,
  EyeIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline'
import { Card, Button, Spinner } from '../components/ui'
import { usePortfolioStore } from '../store/portfolio'
import { 
  PortfolioOverview, 
  HoldingsTable, 
  AddPositionModal, 
  PerformanceCharts, 
  RiskAnalysis, 
  PortfolioOptimization 
} from '../components/portfolio'
import { formatCurrency, formatPercent, getChangeColor } from '../utils'

// Mock portfolios data
const mockPortfolios = [
  {
    id: '1',
    name: 'Growth Portfolio',
    description: 'High-growth technology stocks',
    userId: 'user1',
    holdings: [
      { 
        id: 'h1', symbol: 'AAPL', shares: 100, averagePrice: 150.00, currentPrice: 175.43,
        marketValue: 17543.00, costBasis: 15000.00, unrealizedGain: 2543.00, 
        unrealizedGainPercent: 16.95, weight: 14.0, addedAt: '2024-01-15T10:00:00Z',
        lastUpdated: '2024-01-20T15:30:00Z'
      },
      { 
        id: 'h2', symbol: 'GOOGL', shares: 50, averagePrice: 140.00, currentPrice: 142.56,
        marketValue: 7128.00, costBasis: 7000.00, unrealizedGain: 128.00, 
        unrealizedGainPercent: 1.83, weight: 5.7, addedAt: '2024-01-10T09:00:00Z',
        lastUpdated: '2024-01-20T15:30:00Z'
      },
      { 
        id: 'h3', symbol: 'MSFT', shares: 30, averagePrice: 350.00, currentPrice: 378.85,
        marketValue: 11365.50, costBasis: 10500.00, unrealizedGain: 865.50, 
        unrealizedGainPercent: 8.24, weight: 9.1, addedAt: '2024-01-05T14:00:00Z',
        lastUpdated: '2024-01-20T15:30:00Z'
      },
      { 
        id: 'h4', symbol: 'TSLA', shares: 20, averagePrice: 200.00, currentPrice: 248.50,
        marketValue: 4970.00, costBasis: 4000.00, unrealizedGain: 970.00, 
        unrealizedGainPercent: 24.25, weight: 4.0, addedAt: '2024-01-12T11:00:00Z',
        lastUpdated: '2024-01-20T15:30:00Z'
      },
    ],
    totalValue: 125430.50,
    totalCost: 110000.00,
    totalReturn: 15430.50,
    totalReturnPercent: 14.03,
    dayChange: 1250.30,
    dayChangePercent: 1.01,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-20T15:30:00Z',
    settings: {
      rebalanceThreshold: 5,
      autoRebalance: false,
      riskTolerance: 'moderate',
      targetAllocation: {}
    }
  },
  {
    id: '2',
    name: 'Dividend Portfolio',
    description: 'Stable dividend-paying stocks',
    userId: 'user1',
    holdings: [
      { 
        id: 'h5', symbol: 'JNJ', shares: 200, averagePrice: 150.00, currentPrice: 156.80,
        marketValue: 31360.00, costBasis: 30000.00, unrealizedGain: 1360.00, 
        unrealizedGainPercent: 4.53, weight: 35.6, addedAt: '2024-01-08T10:00:00Z',
        lastUpdated: '2024-01-20T15:30:00Z'
      },
      { 
        id: 'h6', symbol: 'PG', shares: 150, averagePrice: 140.00, currentPrice: 150.25,
        marketValue: 22537.50, costBasis: 21000.00, unrealizedGain: 1537.50, 
        unrealizedGainPercent: 7.32, weight: 25.7, addedAt: '2024-01-06T09:00:00Z',
        lastUpdated: '2024-01-20T15:30:00Z'
      },
      { 
        id: 'h7', symbol: 'KO', shares: 300, averagePrice: 55.00, currentPrice: 60.15,
        marketValue: 18045.00, costBasis: 16500.00, unrealizedGain: 1545.00, 
        unrealizedGainPercent: 9.36, weight: 20.6, addedAt: '2024-01-03T14:00:00Z',
        lastUpdated: '2024-01-20T15:30:00Z'
      },
    ],
    totalValue: 87520.25,
    totalCost: 80000.00,
    totalReturn: 7520.25,
    totalReturnPercent: 9.40,
    dayChange: 450.15,
    dayChangePercent: 0.52,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-20T15:30:00Z',
    settings: {
      rebalanceThreshold: 3,
      autoRebalance: true,
      riskTolerance: 'conservative',
      targetAllocation: {}
    }
  }
]

export const Portfolio: React.FC = () => {
  const {
    portfolios,
    selectedPortfolio,
    activeTab,
    isLoading,
    setPortfolios,
    setSelectedPortfolio,
    setActiveTab,
    setShowAddPositionModal,
    showAddPositionModal
  } = usePortfolioStore()

  const [showCreateModal, setShowCreateModal] = useState(false)

  // Initialize with mock data
  useEffect(() => {
    if (portfolios.length === 0) {
      setPortfolios(mockPortfolios)
      setSelectedPortfolio(mockPortfolios[0])
    }
  }, [portfolios.length, setPortfolios, setSelectedPortfolio])

  const handlePortfolioSelect = (portfolio: any) => {
    setSelectedPortfolio(portfolio)
  }

  const TabButton: React.FC<{
    tab: 'overview' | 'holdings' | 'performance' | 'risk' | 'optimization'
    children: React.ReactNode
    icon: React.ReactNode
  }> = ({ tab, children, icon }) => (
    <Button
      variant={activeTab === tab ? 'primary' : 'outline'}
      size="sm"
      onClick={() => setActiveTab(tab)}
      className="flex items-center space-x-2"
    >
      {icon}
      <span>{children}</span>
    </Button>
  )

  const renderActiveTab = () => {
    if (!selectedPortfolio) return null

    switch (activeTab) {
      case 'overview':
        return <PortfolioOverview />
      case 'holdings':
        return <HoldingsTable />
      case 'performance':
        return <PerformanceCharts />
      case 'risk':
        return <RiskAnalysis />
      case 'optimization':
        return <PortfolioOptimization />
      default:
        return <PortfolioOverview />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Portfolio Management</h1>
          <p className="text-neutral-600">Manage your investment portfolios and track performance.</p>
        </div>
        <Button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Create Portfolio</span>
        </Button>
      </div>

      {/* Portfolio Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {portfolios.map((portfolio) => (
          <Card
            key={portfolio.id}
            className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
              selectedPortfolio?.id === portfolio.id
                ? 'ring-2 ring-blue-500 bg-blue-50'
                : 'hover:bg-neutral-50'
            }`}
            onClick={() => handlePortfolioSelect(portfolio)}
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-neutral-900">{portfolio.name}</h3>
                <div className="flex space-x-1">
                  <button className="p-1 text-neutral-400 hover:text-neutral-600">
                    <EyeIcon className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-neutral-400 hover:text-neutral-600">
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-neutral-400 hover:text-red-600">
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
                    <div className={`font-medium ${getChangeColor(portfolio.totalReturn)}`}>
                      {portfolio.totalReturn >= 0 ? '+' : ''}{formatCurrency(portfolio.totalReturn)}
                    </div>
                    <div className={`text-sm ${getChangeColor(portfolio.totalReturn)}`}>
                      {portfolio.totalReturn >= 0 ? '+' : ''}{formatPercent(portfolio.totalReturnPercent / 100)}
                    </div>
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-neutral-600">Day Change</span>
                  <div className="text-right">
                    <div className={`font-medium ${getChangeColor(portfolio.dayChange)}`}>
                      {portfolio.dayChange >= 0 ? '+' : ''}{formatCurrency(portfolio.dayChange)}
                    </div>
                    <div className={`text-sm ${getChangeColor(portfolio.dayChange)}`}>
                      {portfolio.dayChange >= 0 ? '+' : ''}{formatPercent(portfolio.dayChangePercent / 100)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Portfolio Details */}
      {selectedPortfolio && (
        <div className="space-y-6">
          {/* Tab Navigation */}
          <Card className="p-6">
            <div className="flex flex-wrap gap-2">
              <TabButton tab="overview" icon={<ChartBarIcon className="w-4 h-4" />}>
                Overview
              </TabButton>
              <TabButton tab="holdings" icon={<ChartBarIcon className="w-4 h-4" />}>
                Holdings
              </TabButton>
              <TabButton tab="performance" icon={<ChartBarIcon className="w-4 h-4" />}>
                Performance
              </TabButton>
              <TabButton tab="risk" icon={<ShieldCheckIcon className="w-4 h-4" />}>
                Risk Analysis
              </TabButton>
              <TabButton tab="optimization" icon={<AdjustmentsHorizontalIcon className="w-4 h-4" />}>
                Optimization
              </TabButton>
            </div>
          </Card>

          {/* Active Tab Content */}
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Spinner size="lg" />
            </div>
          ) : (
            renderActiveTab()
          )}
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
                  <label className="block text-sm font-medium text-neutral-700 mb-1">
                    Portfolio Name
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter portfolio name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1">
                    Description
                  </label>
                  <textarea
                    className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Enter portfolio description"
                  />
                </div>
                <div className="flex space-x-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    className="flex-1"
                  >
                    Create Portfolio
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Add Position Modal */}
      <AddPositionModal
        isOpen={showAddPositionModal}
        onClose={() => setShowAddPositionModal(false)}
      />
    </div>
  )
}