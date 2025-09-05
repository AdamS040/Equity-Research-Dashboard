import { memo } from 'react'
import { 
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ScaleIcon
} from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'
import { 
  RadialBarChart, 
  RadialBar, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell,
  Tooltip,
  Legend
} from 'recharts'
import { useMarketOverview } from '../../hooks/api/useStocks'
import { Spinner } from '../ui/Spinner'
import { ErrorDisplay } from '../ErrorDisplay'
import { cn } from '../../utils'

interface MarketSentimentProps {
  className?: string
}

interface SentimentData {
  fearGreedIndex: number
  vixLevel: number
  marketBreadth: {
    advancing: number
    declining: number
    unchanged: number
  }
  putCallRatio: number
  highLowRatio: number
  timestamp: string
}

// Mock data for development
const mockSentimentData: SentimentData = {
  fearGreedIndex: 45, // 0-100 scale
  vixLevel: 18.5,
  marketBreadth: {
    advancing: 1250,
    declining: 1850,
    unchanged: 400
  },
  putCallRatio: 0.85,
  highLowRatio: 0.65,
  timestamp: new Date().toISOString()
}

const SentimentGauge = memo(({ 
  value, 
  label, 
  color, 
  max = 100 
}: { 
  value: number
  label: string
  color: string
  max?: number
}) => {
  const percentage = (value / max) * 100
  const data = [{ value: percentage, fill: color }]

  const getSentimentLabel = (val: number) => {
    if (val >= 80) return 'Extreme Greed'
    if (val >= 60) return 'Greed'
    if (val >= 40) return 'Neutral'
    if (val >= 20) return 'Fear'
    return 'Extreme Fear'
  }

  const getSentimentColor = (val: number) => {
    if (val >= 80) return 'text-danger-600'
    if (val >= 60) return 'text-warning-600'
    if (val >= 40) return 'text-neutral-600'
    if (val >= 20) return 'text-warning-600'
    return 'text-danger-600'
  }

  return (
    <div className="card text-center">
      <h3 className="font-medium text-neutral-900 mb-4">{label}</h3>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="60%"
            outerRadius="90%"
            startAngle={180}
            endAngle={0}
            data={data}
          >
            <RadialBar
              dataKey="value"
              cornerRadius={10}
              fill={color}
            />
            <text
              x="50%"
              y="50%"
              textAnchor="middle"
              dominantBaseline="middle"
              className="text-2xl font-bold text-neutral-900"
            >
              {value}
            </text>
          </RadialBarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-2">
        <p className={cn('text-sm font-medium', getSentimentColor(value))}>
          {getSentimentLabel(value)}
        </p>
      </div>
    </div>
  )
})

SentimentGauge.displayName = 'SentimentGauge'

const MarketBreadthChart = memo(({ 
  advancing, 
  declining, 
  unchanged 
}: { 
  advancing: number
  declining: number
  unchanged: number
}) => {
  const total = advancing + declining + unchanged
  const data = [
    { name: 'Advancing', value: advancing, fill: '#10b981' },
    { name: 'Declining', value: declining, fill: '#ef4444' },
    { name: 'Unchanged', value: unchanged, fill: '#6b7280' }
  ]

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      const percentage = ((data.value / total) * 100).toFixed(1)
      return (
        <div className="bg-white p-3 border border-neutral-200 rounded-lg shadow-lg">
          <p className="font-medium text-neutral-900">{data.name}</p>
          <p className="text-sm text-neutral-600">
            {data.value.toLocaleString()} ({percentage}%)
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="card">
      <h3 className="font-medium text-neutral-900 mb-4">Market Breadth</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-success-500 rounded-full"></div>
            <span className="text-sm text-neutral-600">Advancing</span>
          </div>
          <span className="text-sm font-medium text-neutral-900">
            {advancing.toLocaleString()}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-danger-500 rounded-full"></div>
            <span className="text-sm text-neutral-600">Declining</span>
          </div>
          <span className="text-sm font-medium text-neutral-900">
            {declining.toLocaleString()}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-neutral-500 rounded-full"></div>
            <span className="text-sm text-neutral-600">Unchanged</span>
          </div>
          <span className="text-sm font-medium text-neutral-900">
            {unchanged.toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  )
})

MarketBreadthChart.displayName = 'MarketBreadthChart'

const SentimentIndicator = memo(({ 
  title, 
  value, 
  description, 
  trend, 
  color 
}: { 
  title: string
  value: string | number
  description: string
  trend: 'up' | 'down' | 'neutral'
  color: string
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <ArrowTrendingUpIcon className="w-4 h-4 text-success-600" />
      case 'down':
        return <ArrowTrendingDownIcon className="w-4 h-4 text-danger-600" />
      default:
        return <ScaleIcon className="w-4 h-4 text-neutral-600" />
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="card"
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-neutral-900">{title}</h3>
        {getTrendIcon()}
      </div>
      <div className="space-y-2">
        <div className="text-2xl font-bold text-neutral-900">{value}</div>
        <p className="text-sm text-neutral-600">{description}</p>
        <div className="flex items-center space-x-2">
          <div className={cn('w-2 h-2 rounded-full', color)}></div>
          <span className="text-xs text-neutral-500">Current Level</span>
        </div>
      </div>
    </motion.div>
  )
})

SentimentIndicator.displayName = 'SentimentIndicator'

export const MarketSentiment = memo(({ className }: MarketSentimentProps) => {
  const { isLoading, error, isError } = useMarketOverview()

  // Use mock data for now since API might not be fully implemented
  const sentimentData = mockSentimentData

  if (isLoading) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-neutral-900">Market Sentiment</h2>
          <div className="flex items-center space-x-2">
            <Spinner size="sm" />
            <span className="text-sm text-neutral-600">Loading...</span>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="card animate-pulse">
              <div className="h-48 bg-neutral-200 rounded-lg"></div>
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
          <h2 className="text-lg font-semibold text-neutral-900">Market Sentiment</h2>
          <div className="flex items-center space-x-2 text-danger-600">
            <ExclamationTriangleIcon className="w-4 h-4" />
            <span className="text-sm">Error loading data</span>
          </div>
        </div>
        <ErrorDisplay 
          error={error} 
          message="Failed to load market sentiment data"
          className="min-h-[400px]"
        />
      </div>
    )
  }

  const getFearGreedColor = (value: number) => {
    if (value >= 80) return '#ef4444' // Extreme Greed - Red
    if (value >= 60) return '#f59e0b' // Greed - Orange
    if (value >= 40) return '#6b7280' // Neutral - Gray
    if (value >= 20) return '#f59e0b' // Fear - Orange
    return '#ef4444' // Extreme Fear - Red
  }

  const getVIXColor = (value: number) => {
    if (value >= 30) return '#ef4444' // High Fear - Red
    if (value >= 20) return '#f59e0b' // Moderate Fear - Orange
    return '#10b981' // Low Fear - Green
  }

  const getVIXInterpretation = (value: number) => {
    if (value >= 30) return 'High Fear - Market Stress'
    if (value >= 20) return 'Moderate Fear - Some Concern'
    return 'Low Fear - Market Calm'
  }

  const getPutCallInterpretation = (ratio: number) => {
    if (ratio >= 1.0) return 'Bearish - More puts than calls'
    if (ratio >= 0.8) return 'Neutral to Bearish'
    return 'Bullish - More calls than puts'
  }

  const getHighLowInterpretation = (ratio: number) => {
    if (ratio >= 0.7) return 'Bullish - Many new highs'
    if (ratio >= 0.3) return 'Neutral'
    return 'Bearish - Few new highs'
  }

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-neutral-900">Market Sentiment</h2>
        <div className="flex items-center space-x-2 text-sm text-neutral-600">
          <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
          <span>Live</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fear & Greed Index */}
        <SentimentGauge
          value={sentimentData.fearGreedIndex}
          label="Fear & Greed Index"
          color={getFearGreedColor(sentimentData.fearGreedIndex)}
        />

        {/* Market Breadth */}
        <MarketBreadthChart
          advancing={sentimentData.marketBreadth.advancing}
          declining={sentimentData.marketBreadth.declining}
          unchanged={sentimentData.marketBreadth.unchanged}
        />

        {/* VIX Level */}
        <SentimentIndicator
          title="VIX Level"
          value={sentimentData.vixLevel.toFixed(2)}
          description={getVIXInterpretation(sentimentData.vixLevel)}
          trend={sentimentData.vixLevel >= 20 ? 'up' : 'down'}
          color={getVIXColor(sentimentData.vixLevel)}
        />

        {/* Put/Call Ratio */}
        <SentimentIndicator
          title="Put/Call Ratio"
          value={sentimentData.putCallRatio.toFixed(2)}
          description={getPutCallInterpretation(sentimentData.putCallRatio)}
          trend={sentimentData.putCallRatio >= 1.0 ? 'up' : 'down'}
          color={sentimentData.putCallRatio >= 1.0 ? '#ef4444' : '#10b981'}
        />

        {/* High/Low Ratio */}
        <SentimentIndicator
          title="High/Low Ratio"
          value={sentimentData.highLowRatio.toFixed(2)}
          description={getHighLowInterpretation(sentimentData.highLowRatio)}
          trend={sentimentData.highLowRatio >= 0.7 ? 'up' : 'down'}
          color={sentimentData.highLowRatio >= 0.7 ? '#10b981' : '#ef4444'}
        />

        {/* Market Summary */}
        <div className="card">
          <h3 className="font-medium text-neutral-900 mb-4">Market Summary</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-600">Overall Sentiment</span>
              <span className={cn(
                'text-sm font-medium',
                sentimentData.fearGreedIndex >= 60 ? 'text-danger-600' :
                sentimentData.fearGreedIndex >= 40 ? 'text-neutral-600' : 'text-warning-600'
              )}>
                {sentimentData.fearGreedIndex >= 80 ? 'Extreme Greed' :
                 sentimentData.fearGreedIndex >= 60 ? 'Greed' :
                 sentimentData.fearGreedIndex >= 40 ? 'Neutral' :
                 sentimentData.fearGreedIndex >= 20 ? 'Fear' : 'Extreme Fear'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-600">Market Breadth</span>
              <span className={cn(
                'text-sm font-medium',
                sentimentData.marketBreadth.advancing > sentimentData.marketBreadth.declining 
                  ? 'text-success-600' : 'text-danger-600'
              )}>
                {sentimentData.marketBreadth.advancing > sentimentData.marketBreadth.declining 
                  ? 'Positive' : 'Negative'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-600">Volatility</span>
              <span className={cn(
                'text-sm font-medium',
                sentimentData.vixLevel >= 20 ? 'text-danger-600' : 'text-success-600'
              )}>
                {sentimentData.vixLevel >= 20 ? 'High' : 'Low'}
              </span>
            </div>
            <div className="pt-3 border-t border-neutral-200">
              <p className="text-xs text-neutral-500">
                Last updated: {new Date(sentimentData.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
})

MarketSentiment.displayName = 'MarketSentiment'
