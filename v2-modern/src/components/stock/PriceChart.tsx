import React, { useState, useMemo } from 'react'
import { clsx } from 'clsx'
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Button, 
  Spinner 
} from '../ui'
import { 
  ChartBarIcon,
  AdjustmentsHorizontalIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline'
import { 
  ComposedChart, 
  Line, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  ReferenceLine
} from 'recharts'
import { HistoricalData } from '../../types/api'

interface PriceChartProps {
  symbol: string
  data: HistoricalData[]
  loading?: boolean
  onTimeframeChange?: (timeframe: string) => void
}

interface TechnicalIndicator {
  name: string
  data: number[]
  color: string
  visible: boolean
}

const TIMEFRAMES = [
  { value: '1d', label: '1D', interval: '5m' },
  { value: '5d', label: '5D', interval: '15m' },
  { value: '1m', label: '1M', interval: '1d' },
  { value: '3m', label: '3M', interval: '1d' },
  { value: '1y', label: '1Y', interval: '1d' },
  { value: '5y', label: '5Y', interval: '1wk' }
]

export const PriceChart: React.FC<PriceChartProps> = ({
  symbol,
  data,
  loading = false,
  onTimeframeChange
}) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1y')
  const [showVolume, setShowVolume] = useState(true)
  const [showIndicators, setShowIndicators] = useState(true)
  const [visibleIndicators, setVisibleIndicators] = useState({
    sma20: true,
    sma50: true,
    sma200: true,
    bollinger: false
  })

  // Calculate technical indicators
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return []

    return data.map((item, index) => {
      const result: any = {
        date: new Date(item.date).toLocaleDateString(),
        timestamp: item.date,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume,
        adjustedClose: item.adjustedClose
      }

      // Calculate Simple Moving Averages
      if (index >= 19) {
        const sma20Data = data.slice(index - 19, index + 1)
        result.sma20 = sma20Data.reduce((sum, d) => sum + d.close, 0) / 20
      }

      if (index >= 49) {
        const sma50Data = data.slice(index - 49, index + 1)
        result.sma50 = sma50Data.reduce((sum, d) => sum + d.close, 0) / 50
      }

      if (index >= 199) {
        const sma200Data = data.slice(index - 199, index + 1)
        result.sma200 = sma200Data.reduce((sum, d) => sum + d.close, 0) / 200
      }

      // Calculate Bollinger Bands (simplified)
      if (index >= 19) {
        const sma20Data = data.slice(index - 19, index + 1)
        const sma20 = sma20Data.reduce((sum, d) => sum + d.close, 0) / 20
        const variance = sma20Data.reduce((sum, d) => sum + Math.pow(d.close - sma20, 2), 0) / 20
        const stdDev = Math.sqrt(variance)
        
        result.bbUpper = sma20 + (2 * stdDev)
        result.bbMiddle = sma20
        result.bbLower = sma20 - (2 * stdDev)
      }

      return result
    })
  }, [data])

  const handleTimeframeChange = (timeframe: string) => {
    setSelectedTimeframe(timeframe)
    onTimeframeChange?.(timeframe)
  }

  const toggleIndicator = (indicator: string) => {
    setVisibleIndicators(prev => ({
      ...prev,
      [indicator]: !prev[indicator as keyof typeof prev]
    }))
  }

  const formatTooltipValue = (value: number, name: string) => {
    if (name === 'volume') {
      return [new Intl.NumberFormat('en-US', { notation: 'compact' }).format(value), 'Volume']
    }
    return [`$${value.toFixed(2)}`, name]
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-neutral-800 p-3 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-lg">
          <p className="font-medium text-neutral-900 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.name === 'volume' 
                ? new Intl.NumberFormat('en-US', { notation: 'compact' }).format(entry.value)
                : `$${entry.value.toFixed(2)}`
              }
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  if (loading) {
    return (
      <Card className="mb-6">
        <CardHeader 
          title="Price Chart" 
          subtitle={`${symbol} - Loading chart data...`}
        />
        <CardBody className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </CardBody>
      </Card>
    )
  }

  if (!data || data.length === 0) {
    return (
      <Card className="mb-6">
        <CardHeader 
          title="Price Chart" 
          subtitle={`${symbol} - No data available`}
        />
        <CardBody className="flex items-center justify-center py-12">
          <div className="text-center">
            <ChartBarIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <p className="text-neutral-600">No chart data available for this symbol</p>
          </div>
        </CardBody>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Main Price Chart */}
      <Card>
        <CardHeader 
          title="Price Chart" 
          subtitle={`${symbol} - ${selectedTimeframe} timeframe`}
          actions={
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowIndicators(!showIndicators)}
                leftIcon={showIndicators ? <EyeSlashIcon className="w-4 h-4" /> : <EyeIcon className="w-4 h-4" />}
              >
                {showIndicators ? 'Hide' : 'Show'} Indicators
              </Button>
            </div>
          }
        />
        <CardBody>
          {/* Timeframe Selector */}
          <div className="flex flex-wrap gap-2 mb-6">
            {TIMEFRAMES.map((timeframe) => (
              <Button
                key={timeframe.value}
                variant={selectedTimeframe === timeframe.value ? 'solid' : 'outline'}
                size="sm"
                onClick={() => handleTimeframeChange(timeframe.value)}
              >
                {timeframe.label}
              </Button>
            ))}
          </div>

          {/* Chart */}
          <div className="h-96 mb-4">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  stroke="#666"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  domain={['dataMin - 5', 'dataMax + 5']}
                  stroke="#666"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `$${value.toFixed(0)}`}
                />
                <Tooltip content={<CustomTooltip />} />
                
                {/* Volume Bars */}
                {showVolume && (
                  <Bar 
                    dataKey="volume" 
                    fill="#e5e7eb" 
                    opacity={0.3}
                    yAxisId="volume"
                  />
                )}
                
                {/* Price Area */}
                <Area
                  type="monotone"
                  dataKey="close"
                  stroke="#3b82f6"
                  fill="url(#priceGradient)"
                  strokeWidth={2}
                />
                
                {/* Technical Indicators */}
                {showIndicators && (
                  <>
                    {visibleIndicators.sma20 && (
                      <Line
                        type="monotone"
                        dataKey="sma20"
                        stroke="#f59e0b"
                        strokeWidth={1}
                        dot={false}
                        name="SMA 20"
                      />
                    )}
                    {visibleIndicators.sma50 && (
                      <Line
                        type="monotone"
                        dataKey="sma50"
                        stroke="#10b981"
                        strokeWidth={1}
                        dot={false}
                        name="SMA 50"
                      />
                    )}
                    {visibleIndicators.sma200 && (
                      <Line
                        type="monotone"
                        dataKey="sma200"
                        stroke="#8b5cf6"
                        strokeWidth={1}
                        dot={false}
                        name="SMA 200"
                      />
                    )}
                    {visibleIndicators.bollinger && (
                      <>
                        <Line
                          type="monotone"
                          dataKey="bbUpper"
                          stroke="#ef4444"
                          strokeWidth={1}
                          dot={false}
                          strokeDasharray="5 5"
                          name="BB Upper"
                        />
                        <Line
                          type="monotone"
                          dataKey="bbMiddle"
                          stroke="#ef4444"
                          strokeWidth={1}
                          dot={false}
                          name="BB Middle"
                        />
                        <Line
                          type="monotone"
                          dataKey="bbLower"
                          stroke="#ef4444"
                          strokeWidth={1}
                          dot={false}
                          strokeDasharray="5 5"
                          name="BB Lower"
                        />
                      </>
                    )}
                  </>
                )}
                
                {/* Gradient Definition */}
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05}/>
                  </linearGradient>
                </defs>
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Indicator Controls */}
          {showIndicators && (
            <div className="flex flex-wrap gap-2">
              <Button
                variant={visibleIndicators.sma20 ? 'solid' : 'outline'}
                size="sm"
                onClick={() => toggleIndicator('sma20')}
              >
                SMA 20
              </Button>
              <Button
                variant={visibleIndicators.sma50 ? 'solid' : 'outline'}
                size="sm"
                onClick={() => toggleIndicator('sma50')}
              >
                SMA 50
              </Button>
              <Button
                variant={visibleIndicators.sma200 ? 'solid' : 'outline'}
                size="sm"
                onClick={() => toggleIndicator('sma200')}
              >
                SMA 200
              </Button>
              <Button
                variant={visibleIndicators.bollinger ? 'solid' : 'outline'}
                size="sm"
                onClick={() => toggleIndicator('bollinger')}
              >
                Bollinger Bands
              </Button>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Volume Chart */}
      {showVolume && (
        <Card>
          <CardHeader 
            title="Volume" 
            subtitle={`${symbol} - Trading volume`}
          />
          <CardBody>
            <div className="h-32">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#666"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis 
                    stroke="#666"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => new Intl.NumberFormat('en-US', { notation: 'compact' }).format(value)}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar 
                    dataKey="volume" 
                    fill="#6b7280"
                    opacity={0.7}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}
