import React from 'react'
import { clsx } from 'clsx'
import { 
  Card, 
  CardBody, 
  Button, 
  Badge, 
  Spinner 
} from '../ui'
import { 
  HeartIcon, 
  ShareIcon, 
  ArrowUpIcon, 
  ArrowDownIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline'
import { 
  HeartIcon as HeartSolidIcon 
} from '@heroicons/react/24/solid'
import { Stock, StockQuote } from '../../types/api'
import { useAddToWatchlist, useRemoveFromWatchlist, useWatchlist } from '../../hooks/api/useStocks'

interface StockHeaderProps {
  stock: Stock
  quote: StockQuote
  loading?: boolean
  onShare?: () => void
  onExport?: () => void
}

export const StockHeader: React.FC<StockHeaderProps> = ({
  stock,
  quote,
  loading = false,
  onShare,
  onExport
}) => {
  const { data: watchlist = [] } = useWatchlist()
  const addToWatchlist = useAddToWatchlist()
  const removeFromWatchlist = useRemoveFromWatchlist()
  
  const isInWatchlist = watchlist.includes(stock.symbol)
  const isPositive = quote.change >= 0
  const changeColor = isPositive ? 'text-green-600' : 'text-red-600'
  const changeIcon = isPositive ? ArrowUpIcon : ArrowDownIcon
  const ChangeIcon = changeIcon

  const handleWatchlistToggle = () => {
    if (isInWatchlist) {
      removeFromWatchlist.mutate(stock.symbol)
    } else {
      addToWatchlist.mutate(stock.symbol)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value)
  }

  const formatNumber = (value: number, decimals: number = 0) => {
    if (value >= 1e12) {
      return `${(value / 1e12).toFixed(decimals)}T`
    } else if (value >= 1e9) {
      return `${(value / 1e9).toFixed(decimals)}B`
    } else if (value >= 1e6) {
      return `${(value / 1e6).toFixed(decimals)}M`
    } else if (value >= 1e3) {
      return `${(value / 1e3).toFixed(decimals)}K`
    }
    return value.toFixed(decimals)
  }

  const formatVolume = (volume: number) => {
    return new Intl.NumberFormat('en-US', {
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(volume)
  }

  if (loading) {
    return (
      <Card className="mb-6">
        <CardBody className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </CardBody>
      </Card>
    )
  }

  return (
    <Card className="mb-6">
      <CardBody>
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
          {/* Stock Info */}
          <div className="flex-1">
            <div className="flex items-start gap-4 mb-4">
              {/* Company Logo */}
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">
                {stock.symbol.slice(0, 2)}
              </div>
              
              {/* Stock Details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-3xl font-bold text-neutral-900 truncate">
                    {stock.symbol}
                  </h1>
                  <Badge variant="outline" color="neutral">
                    {stock.exchange}
                  </Badge>
                </div>
                
                <h2 className="text-xl text-neutral-700 mb-2 truncate">
                  {stock.name}
                </h2>
                
                <div className="flex items-center gap-4 text-sm text-neutral-600">
                  <div className="flex items-center gap-1">
                    <BuildingOfficeIcon className="w-4 h-4" />
                    <span>{stock.sector}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <ChartBarIcon className="w-4 h-4" />
                    <span>{stock.industry}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Price and Change */}
            <div className="flex items-baseline gap-4 mb-4">
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold text-neutral-900">
                  {formatCurrency(quote.price)}
                </span>
                <div className={clsx('flex items-center gap-1', changeColor)}>
                  <ChangeIcon className="w-5 h-5" />
                  <span className="text-lg font-semibold">
                    {formatCurrency(Math.abs(quote.change))}
                  </span>
                  <span className="text-lg font-semibold">
                    ({isPositive ? '+' : ''}{quote.changePercent.toFixed(2)}%)
                  </span>
                </div>
              </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-neutral-50 rounded-lg p-3">
                <div className="text-sm text-neutral-600 mb-1">Market Cap</div>
                <div className="font-semibold text-neutral-900">
                  {formatNumber(quote.marketCap)}
                </div>
              </div>
              
              <div className="bg-neutral-50 rounded-lg p-3">
                <div className="text-sm text-neutral-600 mb-1">P/E Ratio</div>
                <div className="font-semibold text-neutral-900">
                  {quote.pe ? quote.pe.toFixed(2) : 'N/A'}
                </div>
              </div>
              
              <div className="bg-neutral-50 rounded-lg p-3">
                <div className="text-sm text-neutral-600 mb-1">Volume</div>
                <div className="font-semibold text-neutral-900">
                  {formatVolume(quote.volume)}
                </div>
              </div>
              
              <div className="bg-neutral-50 rounded-lg p-3">
                <div className="text-sm text-neutral-600 mb-1">Avg Volume</div>
                <div className="font-semibold text-neutral-900">
                  {formatVolume(quote.avgVolume)}
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col gap-3">
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleWatchlistToggle}
                loading={addToWatchlist.isPending || removeFromWatchlist.isPending}
                leftIcon={
                  isInWatchlist ? (
                    <HeartSolidIcon className="w-4 h-4 text-red-500" />
                  ) : (
                    <HeartIcon className="w-4 h-4" />
                  )
                }
              >
                {isInWatchlist ? 'In Watchlist' : 'Add to Watchlist'}
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={onShare}
                leftIcon={<ShareIcon className="w-4 h-4" />}
              >
                Share
              </Button>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={onExport}
              leftIcon={<CurrencyDollarIcon className="w-4 h-4" />}
            >
              Export Data
            </Button>
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-6 pt-6 border-t border-neutral-200">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-neutral-600">Open:</span>
              <span className="ml-2 font-medium">{formatCurrency(quote.open)}</span>
            </div>
            <div>
              <span className="text-neutral-600">High:</span>
              <span className="ml-2 font-medium">{formatCurrency(quote.high)}</span>
            </div>
            <div>
              <span className="text-neutral-600">Low:</span>
              <span className="ml-2 font-medium">{formatCurrency(quote.low)}</span>
            </div>
            <div>
              <span className="text-neutral-600">Previous Close:</span>
              <span className="ml-2 font-medium">{formatCurrency(quote.previousClose)}</span>
            </div>
          </div>
        </div>
      </CardBody>
    </Card>
  )
}
