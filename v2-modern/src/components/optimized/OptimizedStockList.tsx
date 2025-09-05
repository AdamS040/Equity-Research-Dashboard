/**
 * Optimized Stock List Component
 * 
 * Demonstrates virtual scrolling and performance optimization
 * for large lists of stock data
 */

import React, { memo, useMemo, useCallback, useState, useRef, useEffect } from 'react'
import { useVirtualScrolling, usePerformanceMonitor } from '../../hooks/usePerformance'
import { OptimizedStockCard } from './OptimizedStockCard'
import { Stock, StockQuote } from '../../types/api'
import { Input, Button, Select } from '../ui'

interface StockWithQuote {
  stock: Stock
  quote: StockQuote
  isInWatchlist: boolean
}

interface OptimizedStockListProps {
  stocks: StockWithQuote[]
  onAddToWatchlist: (symbol: string) => void
  onRemoveFromWatchlist: (symbol: string) => void
  onViewDetails: (symbol: string) => void
  loading?: boolean
  height?: number
}

// Memoized filter component
const StockFilters = memo<{
  searchTerm: string
  onSearchChange: (term: string) => void
  sortBy: string
  onSortChange: (sort: string) => void
  filterBy: string
  onFilterChange: (filter: string) => void
}>(({ searchTerm, onSearchChange, sortBy, onSortChange, filterBy, onFilterChange }) => {
  return (
    <div className="flex gap-4 p-4 bg-white border-b border-gray-200">
      <Input
        placeholder="Search stocks..."
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
        className="flex-1"
      />
      <Select value={sortBy} onChange={(e) => onSortChange(e.target.value)}>
        <option value="symbol">Symbol</option>
        <option value="name">Name</option>
        <option value="price">Price</option>
        <option value="change">Change</option>
        <option value="marketCap">Market Cap</option>
      </Select>
      <Select value={filterBy} onChange={(e) => onFilterChange(e.target.value)}>
        <option value="all">All Sectors</option>
        <option value="technology">Technology</option>
        <option value="healthcare">Healthcare</option>
        <option value="finance">Finance</option>
        <option value="energy">Energy</option>
        <option value="consumer">Consumer</option>
      </Select>
    </div>
  )
})

StockFilters.displayName = 'StockFilters'

// Memoized list item component
const StockListItem = memo<{
  item: StockWithQuote
  index: number
  onAddToWatchlist: (symbol: string) => void
  onRemoveFromWatchlist: (symbol: string) => void
  onViewDetails: (symbol: string) => void
}>(({ item, onAddToWatchlist, onRemoveFromWatchlist, onViewDetails }) => {
  return (
    <div className="p-2">
      <OptimizedStockCard
        stock={item.stock}
        quote={item.quote}
        isInWatchlist={item.isInWatchlist}
        onAddToWatchlist={onAddToWatchlist}
        onRemoveFromWatchlist={onRemoveFromWatchlist}
        onViewDetails={onViewDetails}
      />
    </div>
  )
})

StockListItem.displayName = 'StockListItem'

// Main optimized stock list component
export const OptimizedStockList = memo<OptimizedStockListProps>(({
  stocks,
  onAddToWatchlist,
  onRemoveFromWatchlist,
  onViewDetails,
  loading = false,
  height = 600
}) => {
  // Performance monitoring
  usePerformanceMonitor('StockList')

  // State for filtering and sorting
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('symbol')
  const [filterBy, setFilterBy] = useState('all')

  // Memoized filtered and sorted stocks
  const filteredStocks = useMemo(() => {
    let filtered = stocks

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(item =>
        item.stock.symbol.toLowerCase().includes(term) ||
        item.stock.name.toLowerCase().includes(term)
      )
    }

    // Apply sector filter
    if (filterBy !== 'all') {
      filtered = filtered.filter(item =>
        item.stock.sector?.toLowerCase() === filterBy.toLowerCase()
      )
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'symbol':
          return a.stock.symbol.localeCompare(b.stock.symbol)
        case 'name':
          return a.stock.name.localeCompare(b.stock.name)
        case 'price':
          return (b.quote.price || 0) - (a.quote.price || 0)
        case 'change':
          return (b.quote.changePercent || 0) - (a.quote.changePercent || 0)
        case 'marketCap':
          return (b.quote.marketCap || 0) - (a.quote.marketCap || 0)
        default:
          return 0
      }
    })

    return filtered
  }, [stocks, searchTerm, sortBy, filterBy])

  // Virtual scrolling setup
  const itemHeight = 200 // Approximate height of each stock card
  const {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll
  } = useVirtualScrolling(filteredStocks, itemHeight, height - 100, 3)

  // Stable callback references
  const handleAddToWatchlist = useCallback((symbol: string) => {
    onAddToWatchlist(symbol)
  }, [onAddToWatchlist])

  const handleRemoveFromWatchlist = useCallback((symbol: string) => {
    onRemoveFromWatchlist(symbol)
  }, [onRemoveFromWatchlist])

  const handleViewDetails = useCallback((symbol: string) => {
    onViewDetails(symbol)
  }, [onViewDetails])

  // Render loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height: `${height}px` }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading stocks...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <StockFilters
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        sortBy={sortBy}
        onSortChange={setSortBy}
        filterBy={filterBy}
        onFilterChange={setFilterBy}
      />
      
      <div className="relative">
        <div
          className="overflow-auto"
          style={{ height: `${height - 100}px` }}
          onScroll={handleScroll}
        >
          <div style={{ height: totalHeight, position: 'relative' }}>
            <div style={{ transform: `translateY(${offsetY}px)` }}>
              {visibleItems.map(({ item, index }) => (
                <StockListItem
                  key={`${item.stock.symbol}-${index}`}
                  item={item}
                  index={index}
                  onAddToWatchlist={handleAddToWatchlist}
                  onRemoveFromWatchlist={handleRemoveFromWatchlist}
                  onViewDetails={handleViewDetails}
                />
              ))}
            </div>
          </div>
        </div>
        
        {/* Results count */}
        <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2">
          <p className="text-sm text-gray-600">
            Showing {filteredStocks.length} of {stocks.length} stocks
          </p>
        </div>
      </div>
    </div>
  )
})

OptimizedStockList.displayName = 'OptimizedStockList'

// Export with custom comparison for React.memo
export const MemoizedStockList = memo(OptimizedStockList, (prevProps, nextProps) => {
  return (
    prevProps.stocks.length === nextProps.stocks.length &&
    prevProps.loading === nextProps.loading &&
    prevProps.height === nextProps.height &&
    // Deep comparison for stocks array
    prevProps.stocks.every((prevStock, index) => {
      const nextStock = nextProps.stocks[index]
      return (
        prevStock.stock.symbol === nextStock.stock.symbol &&
        prevStock.quote.price === nextStock.quote.price &&
        prevStock.quote.change === nextStock.quote.change &&
        prevStock.isInWatchlist === nextStock.isInWatchlist
      )
    })
  )
})
