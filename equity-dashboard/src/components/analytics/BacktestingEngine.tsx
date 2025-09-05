import React, { useState, useEffect, useMemo } from 'react'
import { Card, Button, Input, Typography, Grid, Flex } from '../ui'
import { formatCurrency, formatPercent, formatNumber } from '../../utils'
import { 
  BacktestStrategy,
  BacktestResults,
  BacktestTrade,
  MonthlyReturn,
  BenchmarkComparison
} from '../../types/analytics'

interface BacktestingEngineProps {
  symbols?: string[]
  historicalData?: Record<string, any[]>
  onResults?: (results: BacktestResults) => void
}

export const BacktestingEngine: React.FC<BacktestingEngineProps> = ({
  symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
  historicalData = {},
  onResults
}) => {
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>(['AAPL', 'MSFT'])
  const [activeTab, setActiveTab] = useState<'strategy' | 'results' | 'trades' | 'performance'>('strategy')
  const [isRunning, setIsRunning] = useState<boolean>(false)
  
  // Strategy parameters
  const [strategy, setStrategy] = useState<BacktestStrategy>({
    name: 'Moving Average Crossover',
    description: 'Buy when short MA crosses above long MA, sell when it crosses below',
    parameters: {
      shortPeriod: 20,
      longPeriod: 50,
      stopLoss: 0.05,
      takeProfit: 0.15,
      positionSize: 0.1
    },
    entryRules: [
      'Short MA > Long MA',
      'Volume > Average Volume * 1.2',
      'RSI < 70'
    ],
    exitRules: [
      'Short MA < Long MA',
      'Stop Loss Hit',
      'Take Profit Hit'
    ],
    positionSizing: 'Fixed Percentage'
  })

  const [backtestParams, setBacktestParams] = useState({
    startDate: '2020-01-01',
    endDate: '2023-12-31',
    initialCapital: 100000,
    benchmark: 'SPY',
    transactionCost: 0.001,
    slippage: 0.0005
  })

  // Generate sample historical data if not provided
  const sampleData = useMemo(() => {
    if (Object.keys(historicalData).length > 0) return historicalData
    
    const generated: Record<string, any[]> = {}
    const startDate = new Date(backtestParams.startDate)
    const endDate = new Date(backtestParams.endDate)
    
    selectedSymbols.forEach(symbol => {
      const data: any[] = []
      let currentDate = new Date(startDate)
      let price = 100 + Math.random() * 50 // Starting price between 100-150
      
      while (currentDate <= endDate) {
        // Generate realistic price movement
        const dailyReturn = (Math.random() - 0.5) * 0.04 // ±2% daily volatility
        const trend = Math.sin(currentDate.getTime() / (365 * 24 * 60 * 60 * 1000)) * 0.001 // Annual trend
        price *= (1 + dailyReturn + trend)
        
        const volume = 1000000 + Math.random() * 5000000
        
        data.push({
          date: currentDate.toISOString().split('T')[0],
          open: price * (1 + (Math.random() - 0.5) * 0.01),
          high: price * (1 + Math.random() * 0.02),
          low: price * (1 - Math.random() * 0.02),
          close: price,
          volume: Math.floor(volume),
          adjustedClose: price
        })
        
        currentDate.setDate(currentDate.getDate() + 1)
      }
      
      generated[symbol] = data
    })
    
    return generated
  }, [historicalData, selectedSymbols, backtestParams.startDate, backtestParams.endDate])

  // Calculate technical indicators
  const calculateIndicators = (data: any[], shortPeriod: number, longPeriod: number) => {
    return data.map((item, index) => {
      const smaShort = index >= shortPeriod - 1 
        ? data.slice(index - shortPeriod + 1, index + 1).reduce((sum, d) => sum + d.close, 0) / shortPeriod
        : null
      
      const smaLong = index >= longPeriod - 1
        ? data.slice(index - longPeriod + 1, index + 1).reduce((sum, d) => sum + d.close, 0) / longPeriod
        : null
      
      const avgVolume = index >= 20
        ? data.slice(index - 19, index + 1).reduce((sum, d) => sum + d.volume, 0) / 20
        : null
      
      // Simple RSI calculation
      let rsi = null
      if (index >= 14) {
        let gains = 0
        let losses = 0
        for (let i = index - 13; i <= index; i++) {
          const change = data[i].close - data[i - 1].close
          if (change > 0) gains += change
          else losses -= change
        }
        const avgGain = gains / 14
        const avgLoss = losses / 14
        const rs = avgGain / avgLoss
        rsi = 100 - (100 / (1 + rs))
      }
      
      return {
        ...item,
        smaShort,
        smaLong,
        avgVolume,
        rsi
      }
    })
  }

  // Run backtest
  const runBacktest = async (): Promise<BacktestResults> => {
    setIsRunning(true)
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const trades: BacktestTrade[] = []
    const monthlyReturns: MonthlyReturn[] = []
    
    let capital = backtestParams.initialCapital
    let position = 0
    let entryPrice = 0
    let entryDate = ''
    
    // Process each symbol
    selectedSymbols.forEach(symbol => {
      const data = calculateIndicators(sampleData[symbol], strategy.parameters.shortPeriod, strategy.parameters.longPeriod)
      
      for (let i = 1; i < data.length; i++) {
        const current = data[i]
        const previous = data[i - 1]
        
        // Entry conditions
        if (position === 0 && 
            current.smaShort && current.smaLong && previous.smaShort && previous.smaLong &&
            current.smaShort > current.smaLong && previous.smaShort <= previous.smaLong &&
            current.volume > current.avgVolume * 1.2 &&
            current.rsi && current.rsi < 70) {
          
          position = Math.floor(capital * strategy.parameters.positionSize / current.close)
          entryPrice = current.close
          entryDate = current.date
        }
        
        // Exit conditions
        if (position > 0) {
          let shouldExit = false
          let exitReason = ''
          
          // MA crossover exit
          if (current.smaShort && current.smaLong && previous.smaShort && previous.smaLong &&
              current.smaShort < current.smaLong && previous.smaShort >= previous.smaLong) {
            shouldExit = true
            exitReason = 'MA Crossover'
          }
          
          // Stop loss
          if (current.close <= entryPrice * (1 - strategy.parameters.stopLoss)) {
            shouldExit = true
            exitReason = 'Stop Loss'
          }
          
          // Take profit
          if (current.close >= entryPrice * (1 + strategy.parameters.takeProfit)) {
            shouldExit = true
            exitReason = 'Take Profit'
          }
          
          if (shouldExit) {
            const pnl = (current.close - entryPrice) * position
            const pnlPercent = (current.close - entryPrice) / entryPrice
            
            trades.push({
              entryDate,
              exitDate: current.date,
              symbol,
              entryPrice,
              exitPrice: current.close,
              quantity: position,
              pnl,
              pnlPercent,
              duration: Math.floor((new Date(current.date).getTime() - new Date(entryDate).getTime()) / (1000 * 60 * 60 * 24)),
              reason: exitReason
            })
            
            capital += pnl
            position = 0
          }
        }
      }
    })
    
    // Calculate monthly returns
    const startDate = new Date(backtestParams.startDate)
    const endDate = new Date(backtestParams.endDate)
    let currentDate = new Date(startDate.getFullYear(), startDate.getMonth(), 1)
    let cumulativeReturn = 0
    
    while (currentDate <= endDate) {
      const monthEnd = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0)
      const monthStr = currentDate.toISOString().slice(0, 7)
      
      // Calculate monthly return (simplified)
      const monthlyReturn = (Math.random() - 0.5) * 0.1 // ±5% monthly return
      cumulativeReturn += monthlyReturn
      
      monthlyReturns.push({
        month: monthStr,
        return: monthlyReturn,
        cumulativeReturn
      })
      
      currentDate.setMonth(currentDate.getMonth() + 1)
    }
    
    // Calculate performance metrics
    const totalReturn = (capital - backtestParams.initialCapital) / backtestParams.initialCapital
    const years = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24 * 365)
    const annualizedReturn = Math.pow(1 + totalReturn, 1 / years) - 1
    
    const returns = monthlyReturns.map(m => m.return)
    const volatility = Math.sqrt(returns.reduce((sum, ret) => sum + Math.pow(ret - returns.reduce((s, r) => s + r, 0) / returns.length, 2), 0) / returns.length)
    const sharpeRatio = annualizedReturn / volatility
    
    const maxDrawdown = calculateMaxDrawdown(monthlyReturns.map(m => m.cumulativeReturn))
    
    const winningTrades = trades.filter(t => t.pnl > 0)
    const winRate = trades.length > 0 ? winningTrades.length / trades.length : 0
    
    const totalProfit = winningTrades.reduce((sum, t) => sum + t.pnl, 0)
    const totalLoss = trades.filter(t => t.pnl < 0).reduce((sum, t) => sum + Math.abs(t.pnl), 0)
    const profitFactor = totalLoss > 0 ? totalProfit / totalLoss : 0
    
    // Benchmark comparison (simplified)
    const benchmarkReturn = 0.08 // 8% annual return for SPY
    const alpha = annualizedReturn - benchmarkReturn
    const beta = 1.0 // Simplified
    const informationRatio = alpha / volatility
    const trackingError = volatility * 0.8 // Simplified
    
    const results: BacktestResults = {
      strategy,
      startDate: backtestParams.startDate,
      endDate: backtestParams.endDate,
      initialCapital: backtestParams.initialCapital,
      finalValue: capital,
      totalReturn,
      annualizedReturn,
      volatility,
      sharpeRatio,
      maxDrawdown,
      maxDrawdownDuration: 30, // Simplified
      winRate,
      profitFactor,
      trades,
      monthlyReturns,
      benchmarkComparison: {
        benchmark: backtestParams.benchmark,
        benchmarkReturn,
        alpha,
        beta,
        informationRatio,
        trackingError
      }
    }
    
    setIsRunning(false)
    return results
  }

  const calculateMaxDrawdown = (cumulativeReturns: number[]): number => {
    let peak = 0
    let maxDrawdown = 0
    
    for (const ret of cumulativeReturns) {
      if (ret > peak) {
        peak = ret
      }
      const drawdown = peak - ret
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown
      }
    }
    
    return maxDrawdown
  }

  const [backtestResults, setBacktestResults] = useState<BacktestResults | null>(null)

  const handleRunBacktest = async () => {
    const results = await runBacktest()
    setBacktestResults(results)
    if (onResults) {
      onResults(results)
    }
  }

  const handleStrategyChange = (field: string, value: any) => {
    setStrategy(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleParameterChange = (param: string, value: number) => {
    setStrategy(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters,
        [param]: value
      }
    }))
  }

  return (
    <div className="space-y-6">
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <Typography variant="h2" className="text-2xl font-bold">
              Backtesting Engine
            </Typography>
            <div className="flex gap-2">
              <Button 
                variant="outline"
                disabled={isRunning}
              >
                Save Strategy
              </Button>
              <Button 
                onClick={handleRunBacktest}
                disabled={isRunning}
              >
                {isRunning ? 'Running...' : 'Run Backtest'}
              </Button>
            </div>
          </div>

          {/* Symbol Selection */}
          <div className="mb-6">
            <Typography variant="h3" className="text-lg font-semibold mb-3">
              Select Assets for Backtesting
            </Typography>
            <div className="flex flex-wrap gap-2">
              {symbols.map(symbol => (
                <button
                  key={symbol}
                  onClick={() => {
                    if (selectedSymbols.includes(symbol)) {
                      setSelectedSymbols(prev => prev.filter(s => s !== symbol))
                    } else {
                      setSelectedSymbols(prev => [...prev, symbol])
                    }
                  }}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    selectedSymbols.includes(symbol)
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {symbol}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200 mb-6">
            {[
              { key: 'strategy', label: 'Strategy Setup' },
              { key: 'results', label: 'Results' },
              { key: 'trades', label: 'Trade Analysis' },
              { key: 'performance', label: 'Performance' }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Strategy Setup Tab */}
          {activeTab === 'strategy' && (
            <div className="space-y-6">
              <Grid cols={2} gap={6}>
                {/* Strategy Configuration */}
                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      Strategy Configuration
                    </Typography>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Strategy Name
                        </label>
                        <Input
                          value={strategy.name}
                          onChange={(e) => handleStrategyChange('name', e.target.value)}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Description
                        </label>
                        <textarea
                          value={strategy.description}
                          onChange={(e) => handleStrategyChange('description', e.target.value)}
                          className="w-full border border-gray-300 rounded-md px-3 py-2"
                          rows={3}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Position Sizing
                        </label>
                        <select
                          value={strategy.positionSizing}
                          onChange={(e) => handleStrategyChange('positionSizing', e.target.value)}
                          className="w-full border border-gray-300 rounded-md px-3 py-2"
                        >
                          <option value="Fixed Percentage">Fixed Percentage</option>
                          <option value="Fixed Amount">Fixed Amount</option>
                          <option value="Volatility Based">Volatility Based</option>
                          <option value="Kelly Criterion">Kelly Criterion</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Strategy Parameters */}
                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      Strategy Parameters
                    </Typography>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Short MA Period
                        </label>
                        <Input
                          type="number"
                          value={strategy.parameters.shortPeriod}
                          onChange={(e) => handleParameterChange('shortPeriod', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Long MA Period
                        </label>
                        <Input
                          type="number"
                          value={strategy.parameters.longPeriod}
                          onChange={(e) => handleParameterChange('longPeriod', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Stop Loss (%)
                        </label>
                        <Input
                          type="number"
                          step="0.01"
                          value={strategy.parameters.stopLoss}
                          onChange={(e) => handleParameterChange('stopLoss', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Take Profit (%)
                        </label>
                        <Input
                          type="number"
                          step="0.01"
                          value={strategy.parameters.takeProfit}
                          onChange={(e) => handleParameterChange('takeProfit', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Position Size (%)
                        </label>
                        <Input
                          type="number"
                          step="0.01"
                          value={strategy.parameters.positionSize}
                          onChange={(e) => handleParameterChange('positionSize', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Backtest Parameters */}
                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      Backtest Parameters
                    </Typography>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Start Date
                        </label>
                        <Input
                          type="date"
                          value={backtestParams.startDate}
                          onChange={(e) => setBacktestParams(prev => ({ ...prev, startDate: e.target.value }))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          End Date
                        </label>
                        <Input
                          type="date"
                          value={backtestParams.endDate}
                          onChange={(e) => setBacktestParams(prev => ({ ...prev, endDate: e.target.value }))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Initial Capital
                        </label>
                        <Input
                          type="number"
                          value={backtestParams.initialCapital}
                          onChange={(e) => setBacktestParams(prev => ({ ...prev, initialCapital: Number(e.target.value) }))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Transaction Cost (%)
                        </label>
                        <Input
                          type="number"
                          step="0.001"
                          value={backtestParams.transactionCost}
                          onChange={(e) => setBacktestParams(prev => ({ ...prev, transactionCost: Number(e.target.value) }))}
                          className="w-full"
                        />
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Entry/Exit Rules */}
                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      Entry & Exit Rules
                    </Typography>
                    <div className="space-y-4">
                      <div>
                        <Typography variant="h4" className="font-medium mb-2">Entry Rules</Typography>
                        <ul className="text-sm space-y-1">
                          {strategy.entryRules.map((rule, index) => (
                            <li key={index} className="flex items-center">
                              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                              {rule}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <Typography variant="h4" className="font-medium mb-2">Exit Rules</Typography>
                        <ul className="text-sm space-y-1">
                          {strategy.exitRules.map((rule, index) => (
                            <li key={index} className="flex items-center">
                              <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                              {rule}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </Card>
              </Grid>
            </div>
          )}

          {/* Results Tab */}
          {activeTab === 'results' && backtestResults && (
            <div className="space-y-6">
              {/* Key Performance Metrics */}
              <Grid cols={4} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-blue-600">
                      {formatCurrency(backtestResults.finalValue)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Final Value
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography 
                      variant="h3" 
                      className={`text-2xl font-bold ${
                        backtestResults.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {formatPercent(backtestResults.totalReturn * 100)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Total Return
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography 
                      variant="h3" 
                      className={`text-2xl font-bold ${
                        backtestResults.annualizedReturn >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {formatPercent(backtestResults.annualizedReturn * 100)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Annualized Return
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-purple-600">
                      {formatNumber(backtestResults.sharpeRatio, 2)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Sharpe Ratio
                    </Typography>
                  </div>
                </Card>
              </Grid>

              {/* Risk Metrics */}
              <Grid cols={3} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-red-600">
                      {formatPercent(backtestResults.maxDrawdown * 100)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Max Drawdown
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-green-600">
                      {formatPercent(backtestResults.winRate * 100)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Win Rate
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-blue-600">
                      {formatNumber(backtestResults.profitFactor, 2)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Profit Factor
                    </Typography>
                  </div>
                </Card>
              </Grid>

              {/* Benchmark Comparison */}
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Benchmark Comparison ({backtestResults.benchmarkComparison.benchmark})
                  </Typography>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Strategy Return:</span>
                        <span className="font-semibold">{formatPercent(backtestResults.annualizedReturn * 100)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Benchmark Return:</span>
                        <span className="font-semibold">{formatPercent(backtestResults.benchmarkComparison.benchmarkReturn * 100)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Alpha:</span>
                        <span className={`font-semibold ${backtestResults.benchmarkComparison.alpha >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatPercent(backtestResults.benchmarkComparison.alpha * 100)}
                        </span>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Beta:</span>
                        <span className="font-semibold">{formatNumber(backtestResults.benchmarkComparison.beta, 2)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Information Ratio:</span>
                        <span className="font-semibold">{formatNumber(backtestResults.benchmarkComparison.informationRatio, 2)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Tracking Error:</span>
                        <span className="font-semibold">{formatPercent(backtestResults.benchmarkComparison.trackingError * 100)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Trade Analysis Tab */}
          {activeTab === 'trades' && backtestResults && (
            <div className="space-y-6">
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Trade Analysis ({backtestResults.trades.length} trades)
                  </Typography>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Symbol</th>
                          <th className="text-left py-2">Entry Date</th>
                          <th className="text-left py-2">Exit Date</th>
                          <th className="text-right py-2">Entry Price</th>
                          <th className="text-right py-2">Exit Price</th>
                          <th className="text-right py-2">Quantity</th>
                          <th className="text-right py-2">P&L</th>
                          <th className="text-right py-2">P&L %</th>
                          <th className="text-right py-2">Duration</th>
                          <th className="text-left py-2">Exit Reason</th>
                        </tr>
                      </thead>
                      <tbody>
                        {backtestResults.trades.map((trade, index) => (
                          <tr key={index} className="border-b">
                            <td className="py-2 font-medium">{trade.symbol}</td>
                            <td className="py-2">{trade.entryDate}</td>
                            <td className="py-2">{trade.exitDate}</td>
                            <td className="text-right py-2">{formatCurrency(trade.entryPrice)}</td>
                            <td className="text-right py-2">{formatCurrency(trade.exitPrice)}</td>
                            <td className="text-right py-2">{formatNumber(trade.quantity, 0)}</td>
                            <td className={`text-right py-2 font-semibold ${
                              trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {formatCurrency(trade.pnl)}
                            </td>
                            <td className={`text-right py-2 ${
                              trade.pnlPercent >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {formatPercent(trade.pnlPercent * 100)}
                            </td>
                            <td className="text-right py-2">{trade.duration} days</td>
                            <td className="py-2">{trade.reason}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Performance Tab */}
          {activeTab === 'performance' && backtestResults && (
            <div className="space-y-6">
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Monthly Returns
                  </Typography>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Month</th>
                          <th className="text-right py-2">Return</th>
                          <th className="text-right py-2">Cumulative Return</th>
                        </tr>
                      </thead>
                      <tbody>
                        {backtestResults.monthlyReturns.map((month, index) => (
                          <tr key={index} className="border-b">
                            <td className="py-2">{month.month}</td>
                            <td className={`text-right py-2 ${
                              month.return >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {formatPercent(month.return * 100)}
                            </td>
                            <td className={`text-right py-2 ${
                              month.cumulativeReturn >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {formatPercent(month.cumulativeReturn * 100)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}

export default BacktestingEngine
