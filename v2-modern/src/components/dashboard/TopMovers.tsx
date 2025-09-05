import { memo, useState, useMemo, useCallback } from 'react'
import { 
  ArrowUpIcon, 
  ArrowDownIcon,
  ExclamationTriangleIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline'
import { motion, AnimatePresence } from 'framer-motion'
import { useMarketMovers } from '../../hooks/api/useStocks'
import { Spinner } from '../ui/Spinner'
import { ErrorDisplay } from '../ErrorDisplay'
import { SearchInput } from '../ui/SearchInput'
import { useRenderCount } from '../../hooks/usePerformance'
import { cn, formatCurrency, formatPercent, formatLargeNumber } from '../../utils'
import { StockQuote } from '../../types/api'

interface TopMoversProps {
  className?: string
}

type SortField = 'symbol' | 'price' | 'change' | 'changePercent' | 'volume'
type SortDirection = 'asc' | 'desc'
type MoverType = 'gainers' | 'losers' | 'mostActive'

// Mock data for development
const mockMovers = {
  gainers: [
    {
      symbol: 'NVDA',
      price: 485.23,
      change: 23.45,
      changePercent: 5.08,
      volume: 45678900,
      avgVolume: 35000000,
      high: 490.12,
      low: 460.78,
      open: 465.50,
      previousClose: 461.78,
      marketCap: 1200000000000,
      pe: 45.2,
      eps: 10.73,
      dividend: 0.16,
      dividendYield: 0.13,
      timestamp: new Date().toISOString()
    },
    {
      symbol: 'TSLA',
      price: 248.50,
      change: 12.34,
      changePercent: 5.22,
      volume: 78901200,
      avgVolume: 65000000,
      high: 252.30,
      low: 235.80,
      open: 238.90,
      previousClose: 236.16,
      marketCap: 790000000000,
      pe: 52.1,
      eps: 4.77,
      dividend: 0,
      dividendYield: 0,
      timestamp: new Date().toISOString()
    },
    {
      symbol: 'AMD',
      price: 142.67,
      change: 6.78,
      changePercent: 4.99,
      volume: 34567800,
      avgVolume: 28000000,
      high: 145.20,
      low: 135.90,
      open: 138.50,
      previousClose: 135.89,
      marketCap: 230000000000,
      pe: 28.5,
      eps: 5.01,
      dividend: 0,
      dividendYield: 0,
      timestamp: new Date().toISOString()
    }
  ],
  losers: [
    {
      symbol: 'META',
      price: 312.45,
      change: -18.90,
      changePercent: -5.70,
      volume: 23456700,
      avgVolume: 20000000,
      high: 335.20,
      low: 310.80,
      open: 332.10,
      previousClose: 331.35,
      marketCap: 790000000000,
      pe: 22.3,
      eps: 14.01,
      dividend: 0,
      dividendYield: 0,
      timestamp: new Date().toISOString()
    },
    {
      symbol: 'NFLX',
      price: 445.67,
      change: -22.34,
      changePercent: -4.78,
      volume: 12345600,
      avgVolume: 15000000,
      high: 470.50,
      low: 440.20,
      open: 468.90,
      previousClose: 468.01,
      marketCap: 195000000000,
      pe: 35.2,
      eps: 12.66,
      dividend: 0,
      dividendYield: 0,
      timestamp: new Date().toISOString()
    },
    {
      symbol: 'ZM',
      price: 67.89,
      change: -3.45,
      changePercent: -4.84,
      volume: 8901230,
      avgVolume: 12000000,
      high: 72.30,
      low: 66.50,
      open: 71.80,
      previousClose: 71.34,
      marketCap: 21000000000,
      pe: 15.8,
      eps: 4.30,
      dividend: 0,
      dividendYield: 0,
      timestamp: new Date().toISOString()
    }
  ],
  mostActive: [
    {
      symbol: 'AAPL',
      price: 175.43,
      change: 2.34,
      changePercent: 1.35,
      volume: 78901200,
      avgVolume: 55000000,
      high: 177.20,
      low: 173.80,
      open: 174.50,
      previousClose: 173.09,
      marketCap: 2800000000000,
      pe: 28.5,
      eps: 6.15,
      dividend: 0.96,
      dividendYield: 0.55,
      timestamp: new Date().toISOString()
    },
    {
      symbol: 'SPY',
      price: 456.78,
      change: 1.23,
      changePercent: 0.27,
      volume: 123456700,
      avgVolume: 80000000,
      high: 458.90,
      low: 455.20,
      open: 456.10,
      previousClose: 455.55,
      marketCap: 420000000000,
      pe: 19.2,
      eps: 23.78,
      dividend: 6.12,
      dividendYield: 1.34,
      timestamp: new Date().toISOString()
    },
    {
      symbol: 'QQQ',
      price: 378.45,
      change: -2.34,
      changePercent: -0.61,
      volume: 67890120,
      avgVolume: 45000000,
      high: 382.30,
      low: 376.80,
      open: 381.20,
      previousClose: 380.79,
      marketCap: 195000000000,
      pe: 24.1,
      eps: 15.70,
      dividend: 1.23,
      dividendYield: 0.32,
      timestamp: new Date().toISOString()
    }
  ]
}

const SortableHeader = memo(({ 
  field, 
  currentSort, 
  onSort, 
  children 
}: { 
  field: SortField
  currentSort: { field: SortField; direction: SortDirection }
  onSort: (field: SortField) => void
  children: React.ReactNode
}) => {
  const isActive = currentSort.field === field
  const direction = isActive ? currentSort.direction : null

  return (
    <th 
      className="px-4 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider cursor-pointer hover:bg-neutral-50 transition-colors"
      onClick={() => onSort(field)}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        <div className="flex flex-col">
          <ArrowUpIcon 
            className={cn(
              'w-3 h-3',
              isActive && direction === 'asc' ? 'text-primary-600' : 'text-neutral-400'
            )} 
          />
          <ArrowDownIcon 
            className={cn(
              'w-3 h-3 -mt-1',
              isActive && direction === 'desc' ? 'text-primary-600' : 'text-neutral-400'
            )} 
          />
        </div>
      </div>
    </th>
  )
})

SortableHeader.displayName = 'SortableHeader'

const StockRow = memo(({ stock }: { stock: StockQuote }) => {
  const isPositive = stock.change >= 0

  return (
    <motion.tr
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="hover:bg-neutral-50 transition-colors"
    >
      <td className="px-4 py-3 whitespace-nowrap">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={cn(
              'w-2 h-2 rounded-full',
              isPositive ? 'bg-success-500' : 'bg-danger-500'
            )}></div>
          </div>
          <div className="ml-3">
            <div className="text-sm font-medium text-neutral-900">{stock.symbol}</div>
          </div>
        </div>
      </td>
      <td className="px-4 py-3 whitespace-nowrap text-sm text-neutral-900">
        {formatCurrency(stock.price)}
      </td>
      <td className="px-4 py-3 whitespace-nowrap">
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
            {isPositive ? '+' : ''}{formatCurrency(stock.change)}
          </span>
        </div>
      </td>
      <td className="px-4 py-3 whitespace-nowrap">
        <span className={cn(
          'text-sm font-medium',
          isPositive ? 'text-success-600' : 'text-danger-600'
        )}>
          {isPositive ? '+' : ''}{formatPercent(stock.changePercent)}
        </span>
      </td>
      <td className="px-4 py-3 whitespace-nowrap text-sm text-neutral-900">
        {formatLargeNumber(stock.volume)}
      </td>
      <td className="px-4 py-3 whitespace-nowrap text-sm text-neutral-900">
        {formatLargeNumber(stock.avgVolume)}
      </td>
    </motion.tr>
  )
})

StockRow.displayName = 'StockRow'

const Pagination = memo(({ 
  currentPage, 
  totalPages, 
  onPageChange 
}: { 
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}) => {
  const pages = useMemo(() => {
    const pages = []
    const maxVisible = 5
    const start = Math.max(1, currentPage - Math.floor(maxVisible / 2))
    const end = Math.min(totalPages, start + maxVisible - 1)
    
    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
    return pages
  }, [currentPage, totalPages])

  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-neutral-200">
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className={cn(
            'p-2 rounded-md transition-colors',
            currentPage === 1
              ? 'text-neutral-400 cursor-not-allowed'
              : 'text-neutral-600 hover:bg-neutral-100'
          )}
        >
          <ChevronLeftIcon className="w-4 h-4" />
        </button>
        
        {pages.map((page) => (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            className={cn(
              'px-3 py-1 text-sm font-medium rounded-md transition-colors',
              page === currentPage
                ? 'bg-primary-100 text-primary-700'
                : 'text-neutral-600 hover:bg-neutral-100'
            )}
          >
            {page}
          </button>
        ))}
        
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className={cn(
            'p-2 rounded-md transition-colors',
            currentPage === totalPages
              ? 'text-neutral-400 cursor-not-allowed'
              : 'text-neutral-600 hover:bg-neutral-100'
          )}
        >
          <ChevronRightIcon className="w-4 h-4" />
        </button>
      </div>
      
      <div className="text-sm text-neutral-600">
        Page {currentPage} of {totalPages}
      </div>
    </div>
  )
})

Pagination.displayName = 'Pagination'

export const TopMovers = memo(({ className }: TopMoversProps) => {
  useRenderCount('TopMovers')
  const { data: moversData, isLoading, error, isError } = useMarketMovers()
  const [activeTab, setActiveTab] = useState<MoverType>('gainers')
  const [sortField, setSortField] = useState<SortField>('changePercent')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [currentPage, setCurrentPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const itemsPerPage = 10

  const movers = moversData || mockMovers
  const currentData = movers[activeTab] || []

  // Memoized search filter
  const filteredData = useMemo(() => {
    if (!searchTerm) return currentData
    
    return currentData.filter((stock: StockQuote) => 
      stock.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }, [currentData, searchTerm])

  const sortedData = useMemo(() => {
    return [...filteredData].sort((a, b) => {
      let aValue: any = a[sortField]
      let bValue: any = b[sortField]

      if (sortField === 'symbol') {
        aValue = aValue.toLowerCase()
        bValue = bValue.toLowerCase()
      }

      if (sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })
  }, [filteredData, sortField, sortDirection])

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    return sortedData.slice(startIndex, startIndex + itemsPerPage)
  }, [sortedData, currentPage, itemsPerPage])

  const totalPages = Math.ceil(sortedData.length / itemsPerPage)

  const handleSort = useCallback((field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
    setCurrentPage(1)
  }, [sortField, sortDirection])

  const handleSearch = useCallback((value: string) => {
    setSearchTerm(value)
    setCurrentPage(1)
  }, [])

  const handleTabChange = useCallback((tab: MoverType) => {
    setActiveTab(tab)
    setCurrentPage(1)
    setSearchTerm('')
  }, [])

  const tabs = [
    { key: 'gainers' as MoverType, label: 'Gainers', count: movers.gainers?.length || 0 },
    { key: 'losers' as MoverType, label: 'Losers', count: movers.losers?.length || 0 },
    { key: 'mostActive' as MoverType, label: 'Most Active', count: movers.mostActive?.length || 0 }
  ]

  if (isLoading) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-neutral-900">Top Movers</h2>
          <div className="flex items-center space-x-2">
            <Spinner size="sm" />
            <span className="text-sm text-neutral-600">Loading...</span>
          </div>
        </div>
        <div className="card animate-pulse">
          <div className="h-96 bg-neutral-200 rounded-lg"></div>
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-neutral-900">Top Movers</h2>
          <div className="flex items-center space-x-2 text-danger-600">
            <ExclamationTriangleIcon className="w-4 h-4" />
            <span className="text-sm">Error loading data</span>
          </div>
        </div>
        <ErrorDisplay 
          error={error} 
          message="Failed to load market movers data"
          className="min-h-[400px]"
        />
      </div>
    )
  }

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-neutral-900">Top Movers</h2>
        <div className="flex items-center space-x-2 text-sm text-neutral-600">
          <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
          <span>Live</span>
        </div>
      </div>

      {/* Tabs and Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex space-x-1 bg-neutral-100 rounded-lg p-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => handleTabChange(tab.key)}
              className={cn(
                'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors',
                activeTab === tab.key
                  ? 'bg-white dark:bg-neutral-800 text-primary-700 dark:text-primary-300 shadow-sm'
                  : 'text-neutral-600 hover:text-neutral-900'
              )}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </div>
        
        <div className="flex-1 max-w-sm">
          <SearchInput
            placeholder="Search symbols..."
            value={searchTerm}
            onChange={handleSearch}
            debounceMs={300}
          />
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-neutral-200">
            <thead className="bg-neutral-50">
              <tr>
                <SortableHeader
                  field="symbol"
                  currentSort={{ field: sortField, direction: sortDirection }}
                  onSort={handleSort}
                >
                  Symbol
                </SortableHeader>
                <SortableHeader
                  field="price"
                  currentSort={{ field: sortField, direction: sortDirection }}
                  onSort={handleSort}
                >
                  Price
                </SortableHeader>
                <SortableHeader
                  field="change"
                  currentSort={{ field: sortField, direction: sortDirection }}
                  onSort={handleSort}
                >
                  Change
                </SortableHeader>
                <SortableHeader
                  field="changePercent"
                  currentSort={{ field: sortField, direction: sortDirection }}
                  onSort={handleSort}
                >
                  Change %
                </SortableHeader>
                <SortableHeader
                  field="volume"
                  currentSort={{ field: sortField, direction: sortDirection }}
                  onSort={handleSort}
                >
                  Volume
                </SortableHeader>
                <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Avg Volume
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-neutral-800 divide-y divide-neutral-200 dark:divide-neutral-700">
              <AnimatePresence>
                {paginatedData.map((stock) => (
                  <StockRow key={stock.symbol} stock={stock} />
                ))}
              </AnimatePresence>
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        )}
      </div>
    </div>
  )
})

TopMovers.displayName = 'TopMovers'
