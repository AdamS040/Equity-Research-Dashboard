import { memo, useState, useMemo } from 'react'
import { 
  ArrowUpIcon, 
  ArrowDownIcon,
  ExclamationTriangleIcon,
  EyeIcon
} from '@heroicons/react/24/outline'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid,
  Legend
} from 'recharts'
import { useSectorPerformance } from '../../hooks/api/useStocks'
import { Spinner } from '../ui/Spinner'
import { ErrorDisplay } from '../ErrorDisplay'
import { cn, formatPercent } from '../../utils'

interface SectorData {
  sector: string
  change: number
  changePercent: number
  topGainers: string[]
  topLosers: string[]
  marketCap?: number
  weight?: number
}

interface SectorPerformanceProps {
  className?: string
}

// Mock data for development
const mockSectorData: SectorData[] = [
  {
    sector: 'Technology',
    change: 45.67,
    changePercent: 1.23,
    topGainers: ['AAPL', 'MSFT', 'GOOGL'],
    topLosers: ['META', 'NFLX'],
    marketCap: 8500000000000,
    weight: 28.5
  },
  {
    sector: 'Healthcare',
    change: -12.34,
    changePercent: -0.45,
    topGainers: ['JNJ', 'PFE'],
    topLosers: ['MRNA', 'BNTX'],
    marketCap: 4200000000000,
    weight: 14.2
  },
  {
    sector: 'Financial Services',
    change: 23.45,
    changePercent: 0.78,
    topGainers: ['JPM', 'BAC', 'WFC'],
    topLosers: ['GS'],
    marketCap: 3800000000000,
    weight: 12.8
  },
  {
    sector: 'Consumer Discretionary',
    change: -8.90,
    changePercent: -0.32,
    topGainers: ['AMZN', 'TSLA'],
    topLosers: ['HD', 'LOW'],
    marketCap: 3200000000000,
    weight: 10.7
  },
  {
    sector: 'Communication Services',
    change: 15.67,
    changePercent: 0.56,
    topGainers: ['GOOGL', 'META'],
    topLosers: ['NFLX'],
    marketCap: 2800000000000,
    weight: 9.4
  },
  {
    sector: 'Industrials',
    change: 8.90,
    changePercent: 0.34,
    topGainers: ['BA', 'CAT'],
    topLosers: ['GE'],
    marketCap: 2500000000000,
    weight: 8.4
  },
  {
    sector: 'Consumer Staples',
    change: -5.43,
    changePercent: -0.21,
    topGainers: ['PG', 'KO'],
    topLosers: ['WMT'],
    marketCap: 1800000000000,
    weight: 6.0
  },
  {
    sector: 'Energy',
    change: 34.56,
    changePercent: 2.15,
    topGainers: ['XOM', 'CVX'],
    topLosers: ['SLB'],
    marketCap: 1200000000000,
    weight: 4.0
  }
]

const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', 
  '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
]

const SectorCard = memo(({ 
  sector, 
  isSelected, 
  onClick 
}: { 
  sector: SectorData
  isSelected: boolean
  onClick: () => void
}) => {
  const isPositive = sector.changePercent >= 0

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      className={cn(
        'card cursor-pointer transition-all duration-200 hover:shadow-md',
        isSelected 
          ? 'ring-2 ring-primary-500 bg-primary-50' 
          : 'hover:bg-neutral-50'
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className={cn(
            'w-3 h-3 rounded-full',
            isPositive ? 'bg-success-500' : 'bg-danger-500'
          )}></div>
          <h3 className="font-medium text-neutral-900">{sector.sector}</h3>
        </div>
        <div className="flex items-center space-x-1">
          {isPositive ? (
            <ArrowUpIcon className="w-4 h-4 text-success-600" />
          ) : (
            <ArrowDownIcon className="w-4 h-4 text-danger-600" />
          )}
          <span className={cn(
            'text-sm font-medium',
            isPositive ? 'text-success-600' : 'text-danger-600'
          )}>
            {isPositive ? '+' : ''}{formatPercent(sector.changePercent)}
          </span>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-neutral-600">Change</span>
          <span className={cn(
            'font-medium',
            isPositive ? 'text-success-600' : 'text-danger-600'
          )}>
            {isPositive ? '+' : ''}${sector.change.toFixed(2)}
          </span>
        </div>
        
        {sector.weight && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-neutral-600">Weight</span>
            <span className="font-medium text-neutral-900">
              {sector.weight.toFixed(1)}%
            </span>
          </div>
        )}

        <div className="pt-2 border-t border-neutral-200">
          <div className="flex items-center justify-between text-xs text-neutral-600">
            <span>Top Movers</span>
            <div className="flex items-center space-x-1">
              <span className="text-success-600">↑{sector.topGainers.length}</span>
              <span className="text-danger-600">↓{sector.topLosers.length}</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
})

SectorCard.displayName = 'SectorCard'

const SectorDetailModal = memo(({ 
  sector, 
  isOpen, 
  onClose 
}: { 
  sector: SectorData | null
  isOpen: boolean
  onClose: () => void
}) => {
  if (!sector) return null

  const isPositive = sector.changePercent >= 0

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white dark:bg-neutral-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-neutral-900">
                  {sector.sector} Sector Analysis
                </h2>
                <button
                  onClick={onClose}
                  className="text-neutral-400 hover:text-neutral-600 transition-colors"
                >
                  <EyeIcon className="w-6 h-6" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="card">
                    <h3 className="font-medium text-neutral-900 mb-3">Performance</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-neutral-600">Change</span>
                        <span className={cn(
                          'font-medium',
                          isPositive ? 'text-success-600' : 'text-danger-600'
                        )}>
                          {isPositive ? '+' : ''}${sector.change.toFixed(2)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-neutral-600">Change %</span>
                        <span className={cn(
                          'font-medium',
                          isPositive ? 'text-success-600' : 'text-danger-600'
                        )}>
                          {isPositive ? '+' : ''}{formatPercent(sector.changePercent)}
                        </span>
                      </div>
                      {sector.weight && (
                        <div className="flex items-center justify-between">
                          <span className="text-neutral-600">Market Weight</span>
                          <span className="font-medium text-neutral-900">
                            {sector.weight.toFixed(1)}%
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="card">
                    <h3 className="font-medium text-neutral-900 mb-3">Top Gainers</h3>
                    <div className="space-y-2">
                      {sector.topGainers.map((symbol) => (
                        <div key={symbol} className="flex items-center justify-between">
                          <span className="font-medium text-neutral-900">{symbol}</span>
                          <span className="text-success-600 text-sm">↑</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="card">
                    <h3 className="font-medium text-neutral-900 mb-3">Top Losers</h3>
                    <div className="space-y-2">
                      {sector.topLosers.map((symbol) => (
                        <div key={symbol} className="flex items-center justify-between">
                          <span className="font-medium text-neutral-900">{symbol}</span>
                          <span className="text-danger-600 text-sm">↓</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {sector.marketCap && (
                    <div className="card">
                      <h3 className="font-medium text-neutral-900 mb-3">Market Cap</h3>
                      <div className="text-2xl font-bold text-neutral-900">
                        ${(sector.marketCap / 1e12).toFixed(2)}T
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
})

SectorDetailModal.displayName = 'SectorDetailModal'

export const SectorPerformance = memo(({ className }: SectorPerformanceProps) => {
  const { data: sectorData, isLoading, error, isError } = useSectorPerformance()
  const [selectedSector, setSelectedSector] = useState<SectorData | null>(null)
  const [viewMode, setViewMode] = useState<'chart' | 'list'>('chart')

  const sectors = sectorData || mockSectorData

  const chartData = useMemo(() => {
    return sectors.map((sector, index) => ({
      name: sector.sector,
      value: Math.abs(sector.changePercent),
      change: sector.change,
      changePercent: sector.changePercent,
      fill: COLORS[index % COLORS.length]
    }))
  }, [sectors])

  const barChartData = useMemo(() => {
    return sectors.map((sector) => ({
      sector: sector.sector,
      change: sector.changePercent,
      changeValue: sector.change
    }))
  }, [sectors])

  if (isLoading) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-neutral-900">Sector Performance</h2>
          <div className="flex items-center space-x-2">
            <Spinner size="sm" />
            <span className="text-sm text-neutral-600">Loading...</span>
          </div>
        </div>
        <div className="card animate-pulse">
          <div className="h-80 bg-neutral-200 rounded-lg"></div>
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-neutral-900">Sector Performance</h2>
          <div className="flex items-center space-x-2 text-danger-600">
            <ExclamationTriangleIcon className="w-4 h-4" />
            <span className="text-sm">Error loading data</span>
          </div>
        </div>
        <ErrorDisplay 
          error={error} 
          message="Failed to load sector performance data"
          className="min-h-[300px]"
        />
      </div>
    )
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white dark:bg-neutral-800 p-3 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-lg">
          <p className="font-medium text-neutral-900">{data.name}</p>
          <p className="text-sm text-neutral-600">
            Change: {data.changePercent >= 0 ? '+' : ''}{formatPercent(data.changePercent)}
          </p>
          <p className="text-sm text-neutral-600">
            Value: ${data.change >= 0 ? '+' : ''}{data.change.toFixed(2)}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-neutral-900">Sector Performance</h2>
        <div className="flex items-center space-x-2">
          <div className="flex bg-neutral-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('chart')}
              className={cn(
                'px-3 py-1 text-sm font-medium rounded-md transition-colors',
                viewMode === 'chart'
                  ? 'bg-white dark:bg-neutral-800 text-primary-700 dark:text-primary-300 shadow-sm'
                  : 'text-neutral-600 hover:text-neutral-900'
              )}
            >
              Chart
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                'px-3 py-1 text-sm font-medium rounded-md transition-colors',
                viewMode === 'list'
                  ? 'bg-white dark:bg-neutral-800 text-primary-700 dark:text-primary-300 shadow-sm'
                  : 'text-neutral-600 hover:text-neutral-900'
              )}
            >
              List
            </button>
          </div>
        </div>
      </div>

      {viewMode === 'chart' ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="font-medium text-neutral-900 mb-4">Performance Distribution</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3 className="font-medium text-neutral-900 mb-4">Change Comparison</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="sector" 
                    stroke="#6b7280"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis stroke="#6b7280" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                    formatter={(value: number) => [formatPercent(value), 'Change %']}
                  />
                  <Bar 
                    dataKey="change" 
                    fill="#3b82f6"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {sectors.map((sector) => (
            <SectorCard
              key={sector.sector}
              sector={sector}
              isSelected={selectedSector?.sector === sector.sector}
              onClick={() => setSelectedSector(sector)}
            />
          ))}
        </div>
      )}

      <SectorDetailModal
        sector={selectedSector}
        isOpen={!!selectedSector}
        onClose={() => setSelectedSector(null)}
      />
    </div>
  )
})

SectorPerformance.displayName = 'SectorPerformance'
