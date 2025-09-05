/**
 * Optimized Stock Card Component
 * 
 * Demonstrates React performance optimization techniques:
 * - React.memo for preventing unnecessary re-renders
 * - useMemo for expensive calculations
 * - useCallback for stable function references
 * - Virtual scrolling for large lists
 */

import React, { memo, useMemo, useCallback, useState } from 'react'
import { Card, CardHeader, CardBody, Badge, Button } from '../ui'
import { usePerformanceMonitor, useDebouncedCallback } from '../../hooks/usePerformance'
import { Stock, StockQuote } from '../../types/api'

interface OptimizedStockCardProps {
  stock: Stock
  quote: StockQuote
  onAddToWatchlist: (symbol: string) => void
  onRemoveFromWatchlist: (symbol: string) => void
  isInWatchlist: boolean
  onViewDetails: (symbol: string) => void
}

// Memoized price change component
const PriceChange = memo<{
  change: number
  changePercent: number
}>(({ change, changePercent }) => {
  const isPositive = change >= 0
  const colorClass = isPositive ? 'text-green-600' : 'text-red-600'
  const bgColorClass = isPositive ? 'bg-green-50' : 'bg-red-50'
  
  return (
    <div className={`inline-flex items-center px-2 py-1 rounded-full text-sm font-medium ${bgColorClass} ${colorClass}`}>
      <span className="mr-1">{isPositive ? '↗' : '↘'}</span>
      <span>${Math.abs(change).toFixed(2)} ({Math.abs(changePercent).toFixed(2)}%)</span>
    </div>
  )
})

PriceChange.displayName = 'PriceChange'

// Memoized watchlist button
const WatchlistButton = memo<{
  isInWatchlist: boolean
  onToggle: () => void
  loading?: boolean
}>(({ isInWatchlist, onToggle, loading = false }) => {
  return (
    <Button
      size="sm"
      variant={isInWatchlist ? "primary" : "outline"}
      onClick={onToggle}
      disabled={loading}
      className="min-w-[100px]"
    >
      {loading ? '...' : isInWatchlist ? 'Remove' : 'Add'}
    </Button>
  )
})

WatchlistButton.displayName = 'WatchlistButton'

// Main optimized stock card component
export const OptimizedStockCard = memo<OptimizedStockCardProps>(({
  stock,
  quote,
  onAddToWatchlist,
  onRemoveFromWatchlist,
  isInWatchlist,
  onViewDetails
}) => {
  // Performance monitoring
  usePerformanceMonitor(`StockCard-${stock.symbol}`)

  // Memoized calculations
  const marketCap = useMemo(() => {
    if (!quote.marketCap) return 'N/A'
    const value = quote.marketCap
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
    return `$${value.toLocaleString()}`
  }, [quote.marketCap])

  const peRatio = useMemo(() => {
    if (!quote.peRatio) return 'N/A'
    return quote.peRatio.toFixed(2)
  }, [quote.peRatio])

  const volume = useMemo(() => {
    if (!quote.volume) return 'N/A'
    const value = quote.volume
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`
    return value.toLocaleString()
  }, [quote.volume])

  // Stable callback references
  const handleToggleWatchlist = useCallback(() => {
    if (isInWatchlist) {
      onRemoveFromWatchlist(stock.symbol)
    } else {
      onAddToWatchlist(stock.symbol)
    }
  }, [isInWatchlist, onAddToWatchlist, onRemoveFromWatchlist, stock.symbol])

  const handleViewDetails = useCallback(() => {
    onViewDetails(stock.symbol)
  }, [onViewDetails, stock.symbol])

  // Debounced watchlist toggle to prevent rapid clicks
  const debouncedToggleWatchlist = useDebouncedCallback(handleToggleWatchlist, 300)

  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{stock.symbol}</h3>
            <p className="text-sm text-gray-600 truncate max-w-[200px]">{stock.name}</p>
          </div>
          <Badge variant={stock.sector ? "secondary" : "outline"}>
            {stock.sector || 'Unknown'}
          </Badge>
        </div>
      </CardHeader>
      
      <CardBody className="pt-0">
        <div className="space-y-4">
          {/* Price and Change */}
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-gray-900">
                ${quote.price?.toFixed(2) || 'N/A'}
              </div>
              <PriceChange 
                change={quote.change || 0} 
                changePercent={quote.changePercent || 0} 
              />
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Market Cap:</span>
              <div className="font-medium">{marketCap}</div>
            </div>
            <div>
              <span className="text-gray-500">P/E Ratio:</span>
              <div className="font-medium">{peRatio}</div>
            </div>
            <div>
              <span className="text-gray-500">Volume:</span>
              <div className="font-medium">{volume}</div>
            </div>
            <div>
              <span className="text-gray-500">52W High:</span>
              <div className="font-medium">${quote.fiftyTwoWeekHigh?.toFixed(2) || 'N/A'}</div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <WatchlistButton
              isInWatchlist={isInWatchlist}
              onToggle={debouncedToggleWatchlist}
            />
            <Button
              size="sm"
              variant="outline"
              onClick={handleViewDetails}
              className="flex-1"
            >
              View Details
            </Button>
          </div>
        </div>
      </CardBody>
    </Card>
  )
})

OptimizedStockCard.displayName = 'OptimizedStockCard'

// Comparison function for React.memo
export const areStockCardPropsEqual = (
  prevProps: OptimizedStockCardProps,
  nextProps: OptimizedStockCardProps
): boolean => {
  return (
    prevProps.stock.symbol === nextProps.stock.symbol &&
    prevProps.stock.name === nextProps.stock.name &&
    prevProps.stock.sector === nextProps.stock.sector &&
    prevProps.quote.price === nextProps.quote.price &&
    prevProps.quote.change === nextProps.quote.change &&
    prevProps.quote.changePercent === nextProps.quote.changePercent &&
    prevProps.quote.marketCap === nextProps.quote.marketCap &&
    prevProps.quote.peRatio === nextProps.quote.peRatio &&
    prevProps.quote.volume === nextProps.quote.volume &&
    prevProps.quote.fiftyTwoWeekHigh === nextProps.quote.fiftyTwoWeekHigh &&
    prevProps.isInWatchlist === nextProps.isInWatchlist
  )
}

// Export memoized component with custom comparison
export const MemoizedStockCard = memo(OptimizedStockCard, areStockCardPropsEqual)
