import { memo } from 'react'
import { 
  ArrowUpIcon, 
  ArrowDownIcon,
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'
import { useMarketOverview } from '../../hooks/api/useStocks'
import { Spinner } from '../ui/Spinner'
import { ErrorDisplay } from '../ErrorDisplay'
import { cn, formatCurrency, formatPercent } from '../../utils'

interface MarketIndex {
  symbol: string
  name: string
  value: number
  change: number
  changePercent: number
  timestamp: string
}

interface MarketIndicesProps {
  className?: string
}

// Mock data for development
const mockIndices: MarketIndex[] = [
  {
    symbol: 'SPX',
    name: 'S&P 500',
    value: 4567.89,
    change: 23.45,
    changePercent: 0.52,
    timestamp: new Date().toISOString()
  },
  {
    symbol: 'IXIC',
    name: 'NASDAQ',
    value: 14234.56,
    change: -45.67,
    changePercent: -0.32,
    timestamp: new Date().toISOString()
  },
  {
    symbol: 'DJI',
    name: 'DOW',
    value: 34567.89,
    change: 123.45,
    changePercent: 0.36,
    timestamp: new Date().toISOString()
  },
  {
    symbol: 'VIX',
    name: 'VIX',
    value: 18.45,
    change: -1.23,
    changePercent: -6.25,
    timestamp: new Date().toISOString()
  }
]

const IndexCard = memo(({ index }: { index: MarketIndex }) => {
  const isPositive = index.change >= 0
  const isVIX = index.symbol === 'VIX'
  
  // VIX has inverse interpretation - lower is better
  const vixIsPositive = isVIX ? index.change < 0 : isPositive

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="card hover:shadow-lg transition-shadow duration-200"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={cn(
            'w-10 h-10 rounded-lg flex items-center justify-center',
            isVIX 
              ? (vixIsPositive ? 'bg-success-100' : 'bg-danger-100')
              : (isPositive ? 'bg-success-100' : 'bg-danger-100')
          )}>
            <ChartBarIcon className={cn(
              'w-5 h-5',
              isVIX 
                ? (vixIsPositive ? 'text-success-600' : 'text-danger-600')
                : (isPositive ? 'text-success-600' : 'text-danger-600')
            )} />
          </div>
          <div>
            <h3 className="font-semibold text-neutral-900">{index.symbol}</h3>
            <p className="text-sm text-neutral-600">{index.name}</p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="flex items-center space-x-1">
            {isVIX ? (
              vixIsPositive ? (
                <ArrowDownIcon className="w-4 h-4 text-success-600" />
              ) : (
                <ArrowUpIcon className="w-4 h-4 text-danger-600" />
              )
            ) : (
              isPositive ? (
                <ArrowUpIcon className="w-4 h-4 text-success-600" />
              ) : (
                <ArrowDownIcon className="w-4 h-4 text-danger-600" />
              )
            )}
            <span className={cn(
              'text-sm font-medium',
              isVIX 
                ? (vixIsPositive ? 'text-success-600' : 'text-danger-600')
                : (isPositive ? 'text-success-600' : 'text-danger-600')
            )}>
              {isVIX ? (vixIsPositive ? '↓' : '↑') : (isPositive ? '↑' : '↓')}
            </span>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold text-neutral-900">
            {isVIX ? index.value.toFixed(2) : formatCurrency(index.value)}
          </span>
          <div className={cn(
            'px-2 py-1 rounded-full text-xs font-medium',
            isVIX 
              ? (vixIsPositive ? 'bg-success-50 text-success-700' : 'bg-danger-50 text-danger-700')
              : (isPositive ? 'bg-success-50 text-success-700' : 'bg-danger-50 text-danger-700')
          )}>
            {isVIX ? (vixIsPositive ? '↓' : '↑') : (isPositive ? '+' : '')}
            {formatPercent(Math.abs(index.changePercent))}
          </div>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-neutral-600">Change</span>
          <span className={cn(
            'font-medium',
            isVIX 
              ? (vixIsPositive ? 'text-success-600' : 'text-danger-600')
              : (isPositive ? 'text-success-600' : 'text-danger-600')
          )}>
            {isVIX ? (vixIsPositive ? '-' : '+') : (isPositive ? '+' : '')}
            {isVIX ? Math.abs(index.change).toFixed(2) : formatCurrency(Math.abs(index.change))}
          </span>
        </div>

        {isVIX && (
          <div className="mt-3 p-2 bg-neutral-50 rounded-lg">
            <div className="flex items-center justify-between text-xs">
              <span className="text-neutral-600">Sentiment</span>
              <span className={cn(
                'font-medium',
                vixIsPositive ? 'text-success-600' : 'text-danger-600'
              )}>
                {vixIsPositive ? 'Low Fear' : 'High Fear'}
              </span>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
})

IndexCard.displayName = 'IndexCard'

export const MarketIndices = memo(({ className }: MarketIndicesProps) => {
  const { data: marketData, isLoading, error, isError } = useMarketOverview()

  if (isLoading) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-neutral-900">Market Indices</h2>
          <div className="flex items-center space-x-2">
            <Spinner size="sm" />
            <span className="text-sm text-neutral-600">Loading...</span>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="card animate-pulse">
              <div className="h-32 bg-neutral-200 rounded-lg"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-neutral-900">Market Indices</h2>
          <div className="flex items-center space-x-2 text-danger-600">
            <ExclamationTriangleIcon className="w-4 h-4" />
            <span className="text-sm">Error loading data</span>
          </div>
        </div>
        <ErrorDisplay 
          error={error} 
          message="Failed to load market indices data"
          className="min-h-[200px]"
        />
      </div>
    )
  }

  // Use mock data for now since API might not be fully implemented
  const indices = marketData?.indices || mockIndices

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-neutral-900">Market Indices</h2>
        <div className="flex items-center space-x-2 text-sm text-neutral-600">
          <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
          <span>Live</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {indices.map((index: MarketIndex, indexKey: number) => (
          <IndexCard key={index.symbol || indexKey} index={index} />
        ))}
      </div>
    </div>
  )
})

MarketIndices.displayName = 'MarketIndices'
