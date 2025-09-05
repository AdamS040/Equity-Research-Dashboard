import { useState, useEffect } from 'react'
import { 
  ArrowTrendingUpIcon, 
  ArrowTrendingDownIcon, 
  ChartBarIcon,
  CurrencyDollarIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { cn, formatCurrency, formatPercent, getChangeColor } from '../utils'
import { 
  MarketIndices, 
  SectorPerformance, 
  TopMovers, 
  MarketSentiment 
} from '../components/dashboard'
import { 
  PageTransition, 
  StaggeredList, 
  HoverScale, 
  LoadingStates, 
  ChartLoadingState, 
  CardLoadingState,
  SkeletonCard,
  SkeletonChart,
  AnimatedCounter,
  FeedbackAnimation,
  PullToRefresh,
  MobileTabs,
  useTheme,
  useUserPreferences
} from '../components/ui'

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
  const [activeTab, setActiveTab] = useState<'overview' | 'portfolio'>('overview')
  const [isLoading, setIsLoading] = useState(true)
  const [showSuccess, setShowSuccess] = useState(false)
  const { colorScheme } = useTheme()
  const { preferences } = useUserPreferences()

  // Simulate loading
  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1500)
    return () => clearTimeout(timer)
  }, [])

  // Simulate refresh
  const handleRefresh = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsLoading(false)
    setShowSuccess(true)
    setTimeout(() => setShowSuccess(false), 3000)
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'portfolio', label: 'Portfolio', icon: '💼' }
  ]

  return (
    <PageTransition>
      <PullToRefresh onRefresh={handleRefresh}>
        <div className="space-y-6" id="main-content">
          {/* Success feedback */}
          <FeedbackAnimation type="success" show={showSuccess}>
            <div className="flex items-center space-x-2">
              <span>✅</span>
              <span>Data refreshed successfully!</span>
            </div>
          </FeedbackAnimation>

          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                Market Overview
              </h1>
              <p className="text-neutral-600 dark:text-neutral-400">
                Real-time market data and analysis
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              {/* Mobile-friendly tab navigation */}
              <div className="w-full sm:w-auto">
                <MobileTabs
                  tabs={tabs}
                  activeTab={activeTab}
                  onTabChange={(tabId) => setActiveTab(tabId as 'overview' | 'portfolio')}
                />
              </div>
              
              {/* Period Selector */}
              <div className="flex space-x-2">
                {['1D', '1W', '1M', '3M', '1Y'].map((period) => (
                  <HoverScale key={period}>
                    <button
                      onClick={() => setSelectedPeriod(period)}
                      className={cn(
                        'px-3 py-1 text-sm font-medium rounded-lg transition-colors',
                        'focus:outline-none focus:ring-2 focus:ring-primary-500',
                        selectedPeriod === period
                          ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                          : 'text-neutral-600 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800'
                      )}
                    >
                      {period}
                    </button>
                  </HoverScale>
                ))}
              </div>
            </div>
          </div>

          {/* Market Overview Tab */}
          {activeTab === 'overview' && (
            <StaggeredList className="space-y-6">
              {/* Market Indices */}
              <LoadingStates loading={isLoading} skeleton={<SkeletonCard />}>
                <MarketIndices />
              </LoadingStates>

              {/* Sector Performance */}
              <LoadingStates loading={isLoading} skeleton={<SkeletonChart />}>
                <SectorPerformance />
              </LoadingStates>

              {/* Top Movers */}
              <LoadingStates loading={isLoading} skeleton={<SkeletonCard />}>
                <TopMovers />
              </LoadingStates>

              {/* Market Sentiment */}
              <LoadingStates loading={isLoading} skeleton={<SkeletonCard />}>
                <MarketSentiment />
              </LoadingStates>
            </StaggeredList>
          )}

          {/* Portfolio Tab */}
          {activeTab === 'portfolio' && (
            <StaggeredList className="space-y-6">
              {/* Portfolio Metrics Cards */}
              <LoadingStates loading={isLoading} skeleton={<SkeletonCard />}>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {mockMetrics.map((metric, index) => (
                    <HoverScale key={index}>
                      <div className="card hover:shadow-lg transition-shadow duration-200">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
                              {metric.label}
                            </p>
                            <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mt-1">
                              <AnimatedCounter 
                                value={parseFloat(metric.value.replace(/[$,]/g, ''))} 
                                prefix={metric.value.includes('$') ? '$' : ''}
                                suffix={metric.value.includes('%') ? '%' : ''}
                                decimals={metric.value.includes('.') ? 2 : 0}
                              />
                            </p>
                          </div>
                          <div className={cn(
                            'flex items-center space-x-1 px-2 py-1 rounded-full text-sm',
                            metric.change >= 0 
                              ? 'bg-success-50 text-success-700 dark:bg-success-900/20 dark:text-success-400' 
                              : 'bg-danger-50 text-danger-700 dark:bg-danger-900/20 dark:text-danger-400'
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
                    </HoverScale>
                  ))}
                </div>
              </LoadingStates>

              {/* Chart and Top Holdings */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Portfolio Performance Chart */}
                <ChartLoadingState loading={isLoading}>
                  <div className="lg:col-span-2 card">
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
                        Portfolio Performance
                      </h2>
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-1">
                          <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                          <span className="text-sm text-neutral-600 dark:text-neutral-400">
                            Portfolio Value
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={mockData}>
                          <CartesianGrid 
                            strokeDasharray="3 3" 
                            stroke={colorScheme === 'dark' ? '#374151' : '#e5e7eb'} 
                          />
                          <XAxis 
                            dataKey="name" 
                            stroke={colorScheme === 'dark' ? '#9ca3af' : '#6b7280'} 
                          />
                          <YAxis 
                            stroke={colorScheme === 'dark' ? '#9ca3af' : '#6b7280'} 
                          />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: colorScheme === 'dark' ? '#1f2937' : 'white', 
                              border: `1px solid ${colorScheme === 'dark' ? '#374151' : '#e5e7eb'}`,
                              borderRadius: '8px',
                              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                              color: colorScheme === 'dark' ? '#f9fafb' : '#111827'
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
                </ChartLoadingState>

                {/* Top Holdings */}
                <CardLoadingState loading={isLoading}>
                  <div className="card">
                    <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-6">
                      Top Holdings
                    </h2>
                    <div className="space-y-4">
                      {mockStocks.map((stock) => (
                        <HoverScale key={stock.symbol}>
                          <div className="flex items-center justify-between p-2 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors">
                            <div>
                              <p className="font-medium text-neutral-900 dark:text-neutral-100">
                                {stock.symbol}
                              </p>
                              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                                {stock.name}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium text-neutral-900 dark:text-neutral-100">
                                {formatCurrency(stock.price)}
                              </p>
                              <p className={cn('text-sm', getChangeColor(stock.change))}>
                                {stock.change >= 0 ? '+' : ''}{formatPercent(stock.changePercent)}
                              </p>
                            </div>
                          </div>
                        </HoverScale>
                      ))}
                    </div>
                  </div>
                </CardLoadingState>
              </div>

              {/* Recent Activity */}
              <CardLoadingState loading={isLoading}>
                <div className="card">
                  <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-6">
                    Recent Activity
                  </h2>
                  <div className="space-y-4">
                    {[
                      { action: 'Bought', symbol: 'AAPL', shares: 10, price: 175.43, time: '2 hours ago' },
                      { action: 'Sold', symbol: 'GOOGL', shares: 5, price: 142.56, time: '1 day ago' },
                      { action: 'Bought', symbol: 'MSFT', shares: 8, price: 378.85, time: '2 days ago' },
                    ].map((activity, index) => (
                      <HoverScale key={index}>
                        <div className="flex items-center justify-between py-3 border-b border-neutral-200 dark:border-neutral-700 last:border-b-0 hover:bg-neutral-50 dark:hover:bg-neutral-800 rounded-lg px-2 transition-colors">
                          <div className="flex items-center space-x-3">
                            <div className={cn(
                              'w-8 h-8 rounded-full flex items-center justify-center',
                              activity.action === 'Bought' 
                                ? 'bg-success-100 dark:bg-success-900/20' 
                                : 'bg-danger-100 dark:bg-danger-900/20'
                            )}>
                              {activity.action === 'Bought' ? (
                                <ArrowTrendingUpIcon className="w-4 h-4 text-success-600 dark:text-success-400" />
                              ) : (
                                <ArrowTrendingDownIcon className="w-4 h-4 text-danger-600 dark:text-danger-400" />
                              )}
                            </div>
                            <div>
                              <p className="font-medium text-neutral-900 dark:text-neutral-100">
                                {activity.action} {activity.shares} shares of {activity.symbol}
                              </p>
                              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                                {activity.time}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-medium text-neutral-900 dark:text-neutral-100">
                              {formatCurrency(activity.price)}
                            </p>
                            <p className="text-sm text-neutral-600 dark:text-neutral-400">
                              per share
                            </p>
                          </div>
                        </div>
                      </HoverScale>
                    ))}
                  </div>
                </div>
              </CardLoadingState>
            </StaggeredList>
          )}
        </div>
      </PullToRefresh>
    </PageTransition>
  )
}
