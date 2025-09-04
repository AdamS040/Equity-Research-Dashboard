import React, { useState, useMemo } from 'react'
import { clsx } from 'clsx'
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Badge, 
  Spinner 
} from '../ui'
import { 
  ChartBarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Area,
  ReferenceLine,
  ReferenceArea
} from 'recharts'
import { HistoricalData } from '../../types/api'

interface TechnicalAnalysisProps {
  symbol: string
  data: HistoricalData[]
  loading?: boolean
}

interface TechnicalSignal {
  type: 'buy' | 'sell' | 'hold'
  strength: 'weak' | 'moderate' | 'strong'
  description: string
  indicator: string
}

interface IndicatorData {
  rsi: number[]
  macd: {
    macd: number[]
    signal: number[]
    histogram: number[]
  }
  sma: {
    sma20: number[]
    sma50: number[]
    sma200: number[]
  }
  support: number
  resistance: number
}

export const TechnicalAnalysis: React.FC<TechnicalAnalysisProps> = ({
  symbol,
  data,
  loading = false
}) => {
  const [selectedIndicator, setSelectedIndicator] = useState<'rsi' | 'macd' | 'sma'>('rsi')

  // Calculate technical indicators
  const indicators = useMemo((): IndicatorData => {
    if (!data || data.length === 0) {
      return {
        rsi: [],
        macd: { macd: [], signal: [], histogram: [] },
        sma: { sma20: [], sma50: [], sma200: [] },
        support: 0,
        resistance: 0
      }
    }

    const closes = data.map(d => d.close)
    const highs = data.map(d => d.high)
    const lows = data.map(d => d.low)

    // Calculate RSI
    const rsi = calculateRSI(closes, 14)

    // Calculate MACD
    const macd = calculateMACD(closes)

    // Calculate Moving Averages
    const sma20 = calculateSMA(closes, 20)
    const sma50 = calculateSMA(closes, 50)
    const sma200 = calculateSMA(closes, 200)

    // Calculate Support and Resistance
    const support = Math.min(...lows.slice(-20))
    const resistance = Math.max(...highs.slice(-20))

    return {
      rsi,
      macd,
      sma: { sma20, sma50, sma200 },
      support,
      resistance
    }
  }, [data])

  // Generate trading signals
  const signals = useMemo((): TechnicalSignal[] => {
    if (!data || data.length === 0) return []

    const currentPrice = data[data.length - 1].close
    const currentRSI = indicators.rsi[indicators.rsi.length - 1]
    const currentMACD = indicators.macd.macd[indicators.macd.macd.length - 1]
    const currentSignal = indicators.macd.signal[indicators.macd.signal.length - 1]
    const currentSMA20 = indicators.sma.sma20[indicators.sma.sma20.length - 1]
    const currentSMA50 = indicators.sma.sma50[indicators.sma.sma50.length - 1]

    const signals: TechnicalSignal[] = []

    // RSI Signals
    if (currentRSI > 70) {
      signals.push({
        type: 'sell',
        strength: currentRSI > 80 ? 'strong' : 'moderate',
        description: `RSI is overbought at ${currentRSI.toFixed(1)}`,
        indicator: 'RSI'
      })
    } else if (currentRSI < 30) {
      signals.push({
        type: 'buy',
        strength: currentRSI < 20 ? 'strong' : 'moderate',
        description: `RSI is oversold at ${currentRSI.toFixed(1)}`,
        indicator: 'RSI'
      })
    }

    // MACD Signals
    if (currentMACD > currentSignal) {
      signals.push({
        type: 'buy',
        strength: 'moderate',
        description: 'MACD line is above signal line',
        indicator: 'MACD'
      })
    } else {
      signals.push({
        type: 'sell',
        strength: 'moderate',
        description: 'MACD line is below signal line',
        indicator: 'MACD'
      })
    }

    // Moving Average Signals
    if (currentPrice > currentSMA20 && currentSMA20 > currentSMA50) {
      signals.push({
        type: 'buy',
        strength: 'moderate',
        description: 'Price above short-term moving averages',
        indicator: 'MA'
      })
    } else if (currentPrice < currentSMA20 && currentSMA20 < currentSMA50) {
      signals.push({
        type: 'sell',
        strength: 'moderate',
        description: 'Price below short-term moving averages',
        indicator: 'MA'
      })
    }

    return signals
  }, [data, indicators])

  // Prepare chart data
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return []

    return data.map((item, index) => ({
      date: new Date(item.date).toLocaleDateString(),
      timestamp: item.date,
      close: item.close,
      rsi: indicators.rsi[index] || null,
      macd: indicators.macd.macd[index] || null,
      signal: indicators.macd.signal[index] || null,
      histogram: indicators.macd.histogram[index] || null,
      sma20: indicators.sma.sma20[index] || null,
      sma50: indicators.sma.sma50[index] || null,
      sma200: indicators.sma.sma200[index] || null
    }))
  }, [data, indicators])

  const getSignalIcon = (type: string) => {
    switch (type) {
      case 'buy':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />
      case 'sell':
        return <XCircleIcon className="w-5 h-5 text-red-500" />
      default:
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />
    }
  }

  const getSignalColor = (type: string, strength: string) => {
    if (type === 'buy') {
      return strength === 'strong' ? 'success' : 'success'
    } else if (type === 'sell') {
      return strength === 'strong' ? 'danger' : 'danger'
    }
    return 'warning'
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-neutral-200 rounded-lg shadow-lg">
          <p className="font-medium text-neutral-900 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value?.toFixed(2) || 'N/A'}
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
          title="Technical Analysis" 
          subtitle={`${symbol} - Loading technical indicators...`}
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
          title="Technical Analysis" 
          subtitle={`${symbol} - No data available`}
        />
        <CardBody className="flex items-center justify-center py-12">
          <div className="text-center">
            <ChartBarIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <p className="text-neutral-600">No technical analysis data available</p>
          </div>
        </CardBody>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Trading Signals */}
      <Card>
        <CardHeader 
          title="Trading Signals" 
          subtitle={`${symbol} - Current technical signals`}
        />
        <CardBody>
          {signals.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {signals.map((signal, index) => (
                <div
                  key={index}
                  className={clsx(
                    'p-4 rounded-lg border-2',
                    signal.type === 'buy' && 'border-green-200 bg-green-50',
                    signal.type === 'sell' && 'border-red-200 bg-red-50',
                    signal.type === 'hold' && 'border-yellow-200 bg-yellow-50'
                  )}
                >
                  <div className="flex items-center gap-3 mb-2">
                    {getSignalIcon(signal.type)}
                    <div>
                      <Badge 
                        color={getSignalColor(signal.type, signal.strength)}
                        variant="solid"
                      >
                        {signal.type.toUpperCase()}
                      </Badge>
                      <Badge 
                        color="neutral" 
                        variant="outline" 
                        className="ml-2"
                      >
                        {signal.strength}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm text-neutral-700 mb-1">
                    {signal.description}
                  </p>
                  <p className="text-xs text-neutral-500">
                    {signal.indicator}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <ExclamationTriangleIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
              <p className="text-neutral-600">No clear trading signals at this time</p>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Support and Resistance */}
      <Card>
        <CardHeader 
          title="Support & Resistance" 
          subtitle={`${symbol} - Key price levels`}
        />
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="text-center p-4 bg-red-50 rounded-lg border border-red-200">
              <TrendingDownIcon className="w-8 h-8 text-red-500 mx-auto mb-2" />
              <h3 className="font-semibold text-red-800 mb-1">Resistance</h3>
              <p className="text-2xl font-bold text-red-900">
                ${indicators.resistance.toFixed(2)}
              </p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
              <TrendingUpIcon className="w-8 h-8 text-green-500 mx-auto mb-2" />
              <h3 className="font-semibold text-green-800 mb-1">Support</h3>
              <p className="text-2xl font-bold text-green-900">
                ${indicators.support.toFixed(2)}
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Technical Indicators Chart */}
      <Card>
        <CardHeader 
          title="Technical Indicators" 
          subtitle={`${symbol} - ${selectedIndicator.toUpperCase()} analysis`}
          actions={
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedIndicator('rsi')}
                className={clsx(
                  'px-3 py-1 rounded-md text-sm font-medium transition-colors',
                  selectedIndicator === 'rsi'
                    ? 'bg-blue-100 text-blue-800'
                    : 'text-neutral-600 hover:text-neutral-900'
                )}
              >
                RSI
              </button>
              <button
                onClick={() => setSelectedIndicator('macd')}
                className={clsx(
                  'px-3 py-1 rounded-md text-sm font-medium transition-colors',
                  selectedIndicator === 'macd'
                    ? 'bg-blue-100 text-blue-800'
                    : 'text-neutral-600 hover:text-neutral-900'
                )}
              >
                MACD
              </button>
              <button
                onClick={() => setSelectedIndicator('sma')}
                className={clsx(
                  'px-3 py-1 rounded-md text-sm font-medium transition-colors',
                  selectedIndicator === 'sma'
                    ? 'bg-blue-100 text-blue-800'
                    : 'text-neutral-600 hover:text-neutral-900'
                )}
              >
                SMA
              </button>
            </div>
          }
        />
        <CardBody>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
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
                />
                <Tooltip content={<CustomTooltip />} />
                
                {selectedIndicator === 'rsi' && (
                  <>
                    <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="5 5" />
                    <ReferenceLine y={30} stroke="#10b981" strokeDasharray="5 5" />
                    <ReferenceLine y={50} stroke="#6b7280" strokeDasharray="2 2" />
                    <Line
                      type="monotone"
                      dataKey="rsi"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={false}
                    />
                  </>
                )}
                
                {selectedIndicator === 'macd' && (
                  <>
                    <Line
                      type="monotone"
                      dataKey="macd"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="signal"
                      stroke="#ef4444"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Area
                      type="monotone"
                      dataKey="histogram"
                      fill="#f59e0b"
                      fillOpacity={0.3}
                    />
                  </>
                )}
                
                {selectedIndicator === 'sma' && (
                  <>
                    <Line
                      type="monotone"
                      dataKey="close"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="sma20"
                      stroke="#f59e0b"
                      strokeWidth={1}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="sma50"
                      stroke="#10b981"
                      strokeWidth={1}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="sma200"
                      stroke="#8b5cf6"
                      strokeWidth={1}
                      dot={false}
                    />
                  </>
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

// Helper functions for technical calculations
function calculateRSI(prices: number[], period: number = 14): number[] {
  const rsi: number[] = []
  
  for (let i = 0; i < prices.length; i++) {
    if (i < period) {
      rsi.push(50) // Default neutral value
      continue
    }
    
    let gains = 0
    let losses = 0
    
    for (let j = i - period + 1; j <= i; j++) {
      const change = prices[j] - prices[j - 1]
      if (change > 0) {
        gains += change
      } else {
        losses += Math.abs(change)
      }
    }
    
    const avgGain = gains / period
    const avgLoss = losses / period
    
    if (avgLoss === 0) {
      rsi.push(100)
    } else {
      const rs = avgGain / avgLoss
      rsi.push(100 - (100 / (1 + rs)))
    }
  }
  
  return rsi
}

function calculateMACD(prices: number[]): { macd: number[], signal: number[], histogram: number[] } {
  const ema12 = calculateEMA(prices, 12)
  const ema26 = calculateEMA(prices, 26)
  
  const macd = ema12.map((val, i) => val - ema26[i])
  const signal = calculateEMA(macd, 9)
  const histogram = macd.map((val, i) => val - signal[i])
  
  return { macd, signal, histogram }
}

function calculateEMA(prices: number[], period: number): number[] {
  const ema: number[] = []
  const multiplier = 2 / (period + 1)
  
  for (let i = 0; i < prices.length; i++) {
    if (i === 0) {
      ema.push(prices[i])
    } else {
      ema.push((prices[i] * multiplier) + (ema[i - 1] * (1 - multiplier)))
    }
  }
  
  return ema
}

function calculateSMA(prices: number[], period: number): number[] {
  const sma: number[] = []
  
  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      sma.push(0)
      continue
    }
    
    const sum = prices.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0)
    sma.push(sum / period)
  }
  
  return sma
}
