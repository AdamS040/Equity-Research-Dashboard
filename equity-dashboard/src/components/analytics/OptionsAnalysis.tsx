import React, { useState, useEffect, useMemo } from 'react'
import { Card, Button, Input, Typography, Grid, Flex } from '../ui'
import { formatCurrency, formatPercent, formatNumber } from '../../utils'
import { 
  OptionsChain,
  OptionContract,
  OptionsStrategy,
  OptionsLeg,
  ProfitLossPoint,
  GreeksAnalysis,
  VolatilitySkew
} from '../../types/analytics'
import { calculateBlackScholes } from '../../utils/financial-calculations'

interface OptionsAnalysisProps {
  symbol?: string
  underlyingPrice?: number
  onResults?: (results: GreeksAnalysis) => void
}

export const OptionsAnalysis: React.FC<OptionsAnalysisProps> = ({
  symbol = 'AAPL',
  underlyingPrice = 150,
  onResults
}) => {
  const [activeTab, setActiveTab] = useState<'chain' | 'greeks' | 'strategy' | 'volatility'>('chain')
  const [selectedExpiration, setSelectedExpiration] = useState<string>('2024-03-15')
  const [selectedStrike, setSelectedStrike] = useState<number>(150)
  const [selectedOptionType, setSelectedOptionType] = useState<'call' | 'put'>('call')
  
  // Options pricing parameters
  const [pricingParams, setPricingParams] = useState({
    underlyingPrice,
    riskFreeRate: 0.05,
    dividendYield: 0.02,
    volatility: 0.25,
    timeToExpiration: 30 // days
  })

  // Generate sample options chain
  const optionsChain = useMemo((): OptionsChain => {
    const strikes = [120, 130, 140, 145, 150, 155, 160, 170, 180, 190]
    const calls: OptionContract[] = []
    const puts: OptionContract[] = []
    
    strikes.forEach(strike => {
      const timeToExp = pricingParams.timeToExpiration / 365
      const callGreeks = calculateBlackScholes(
        pricingParams.underlyingPrice,
        strike,
        timeToExp,
        pricingParams.riskFreeRate,
        pricingParams.volatility,
        'call'
      )
      
      const putGreeks = calculateBlackScholes(
        pricingParams.underlyingPrice,
        strike,
        timeToExp,
        pricingParams.riskFreeRate,
        pricingParams.volatility,
        'put'
      )
      
      const intrinsicValueCall = Math.max(0, pricingParams.underlyingPrice - strike)
      const intrinsicValuePut = Math.max(0, strike - pricingParams.underlyingPrice)
      
      calls.push({
        strike,
        bid: callGreeks.price * 0.98,
        ask: callGreeks.price * 1.02,
        last: callGreeks.price,
        volume: Math.floor(Math.random() * 10000),
        openInterest: Math.floor(Math.random() * 50000),
        impliedVolatility: pricingParams.volatility + (Math.random() - 0.5) * 0.05,
        delta: callGreeks.delta,
        gamma: callGreeks.gamma,
        theta: callGreeks.theta,
        vega: callGreeks.vega,
        rho: callGreeks.rho,
        intrinsicValue: intrinsicValueCall,
        timeValue: callGreeks.price - intrinsicValueCall
      })
      
      puts.push({
        strike,
        bid: putGreeks.price * 0.98,
        ask: putGreeks.price * 1.02,
        last: putGreeks.price,
        volume: Math.floor(Math.random() * 10000),
        openInterest: Math.floor(Math.random() * 50000),
        impliedVolatility: pricingParams.volatility + (Math.random() - 0.5) * 0.05,
        delta: putGreeks.delta,
        gamma: putGreeks.gamma,
        theta: putGreeks.theta,
        vega: putGreeks.vega,
        rho: putGreeks.rho,
        intrinsicValue: intrinsicValuePut,
        timeValue: putGreeks.price - intrinsicValuePut
      })
    })
    
    return {
      symbol,
      expirationDate: selectedExpiration,
      calls,
      puts,
      underlyingPrice: pricingParams.underlyingPrice,
      impliedVolatility: pricingParams.volatility,
      timeToExpiration: pricingParams.timeToExpiration
    }
  }, [symbol, selectedExpiration, pricingParams])

  // Greeks analysis
  const greeksAnalysis = useMemo((): GreeksAnalysis => {
    const selectedCall = optionsChain.calls.find(c => c.strike === selectedStrike)
    const selectedPut = optionsChain.puts.find(p => p.strike === selectedStrike)
    const selectedOption = selectedOptionType === 'call' ? selectedCall : selectedPut
    
    if (!selectedOption) {
      return {
        symbol,
        delta: 0,
        gamma: 0,
        theta: 0,
        vega: 0,
        rho: 0,
        impliedVolatility: 0,
        historicalVolatility: 0,
        volatilitySkew: []
      }
    }
    
    // Generate volatility skew
    const volatilitySkew: VolatilitySkew[] = optionsChain.calls.map(call => ({
      strike: call.strike,
      impliedVolatility: call.impliedVolatility,
      moneyness: call.strike / pricingParams.underlyingPrice
    }))
    
    return {
      symbol,
      delta: selectedOption.delta,
      gamma: selectedOption.gamma,
      theta: selectedOption.theta,
      vega: selectedOption.vega,
      rho: selectedOption.rho,
      impliedVolatility: selectedOption.impliedVolatility,
      historicalVolatility: pricingParams.volatility,
      volatilitySkew
    }
  }, [symbol, selectedStrike, selectedOptionType, optionsChain, pricingParams])

  // Options strategies
  const [strategies, setStrategies] = useState<OptionsStrategy[]>([
    {
      name: 'Long Call',
      description: 'Buy a call option to profit from upward price movement',
      legs: [
        {
          type: 'call',
          action: 'buy',
          strike: 150,
          premium: 5.50,
          quantity: 1,
          expiration: '2024-03-15'
        }
      ],
      maxProfit: Infinity,
      maxLoss: 5.50,
      breakevenPoints: [155.50],
      profitLossDiagram: []
    },
    {
      name: 'Covered Call',
      description: 'Sell a call option against owned stock',
      legs: [
        {
          type: 'call',
          action: 'sell',
          strike: 160,
          premium: 3.20,
          quantity: 1,
          expiration: '2024-03-15'
        }
      ],
      maxProfit: 13.20,
      maxLoss: -146.80,
      breakevenPoints: [146.80],
      profitLossDiagram: []
    },
    {
      name: 'Straddle',
      description: 'Buy both call and put at the same strike',
      legs: [
        {
          type: 'call',
          action: 'buy',
          strike: 150,
          premium: 5.50,
          quantity: 1,
          expiration: '2024-03-15'
        },
        {
          type: 'put',
          action: 'buy',
          strike: 150,
          premium: 4.20,
          quantity: 1,
          expiration: '2024-03-15'
        }
      ],
      maxProfit: Infinity,
      maxLoss: 9.70,
      breakevenPoints: [140.30, 159.70],
      profitLossDiagram: []
    }
  ])

  const [selectedStrategy, setSelectedStrategy] = useState<OptionsStrategy>(strategies[0])

  // Calculate P&L diagram for selected strategy
  const profitLossDiagram = useMemo((): ProfitLossPoint[] => {
    const points: ProfitLossPoint[] = []
    const minPrice = pricingParams.underlyingPrice * 0.7
    const maxPrice = pricingParams.underlyingPrice * 1.3
    const step = (maxPrice - minPrice) / 50
    
    for (let price = minPrice; price <= maxPrice; price += step) {
      let totalPnL = 0
      
      selectedStrategy.legs.forEach(leg => {
        const timeToExp = pricingParams.timeToExpiration / 365
        const optionPrice = calculateBlackScholes(
          price,
          leg.strike,
          timeToExp,
          pricingParams.riskFreeRate,
          pricingParams.volatility,
          leg.type
        ).price
        
        const intrinsicValue = leg.type === 'call' 
          ? Math.max(0, price - leg.strike)
          : Math.max(0, leg.strike - price)
        
        const pnl = leg.action === 'buy' 
          ? (optionPrice - leg.premium) * leg.quantity
          : (leg.premium - optionPrice) * leg.quantity
        
        totalPnL += pnl
      })
      
      points.push({
        underlyingPrice: price,
        profitLoss: totalPnL
      })
    }
    
    return points
  }, [selectedStrategy, pricingParams])

  const handleParameterChange = (param: string, value: number) => {
    setPricingParams(prev => ({ ...prev, [param]: value }))
  }

  const handleStrategyChange = (strategy: OptionsStrategy) => {
    setSelectedStrategy(strategy)
  }

  useEffect(() => {
    if (onResults) {
      onResults(greeksAnalysis)
    }
  }, [greeksAnalysis, onResults])

  return (
    <div className="space-y-6">
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <Typography variant="h2" className="text-2xl font-bold">
              Options Analysis - {symbol}
            </Typography>
            <div className="flex gap-2">
              <Button variant="outline">
                Export
              </Button>
              <Button>
                Refresh Data
              </Button>
            </div>
          </div>

          {/* Pricing Parameters */}
          <div className="mb-6">
            <Typography variant="h3" className="text-lg font-semibold mb-3">
              Pricing Parameters
            </Typography>
            <Grid cols={5} gap={4}>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Underlying Price
                </label>
                <Input
                  type="number"
                  value={pricingParams.underlyingPrice}
                  onChange={(e) => handleParameterChange('underlyingPrice', Number(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Risk-Free Rate
                </label>
                <Input
                  type="number"
                  step="0.01"
                  value={pricingParams.riskFreeRate}
                  onChange={(e) => handleParameterChange('riskFreeRate', Number(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dividend Yield
                </label>
                <Input
                  type="number"
                  step="0.01"
                  value={pricingParams.dividendYield}
                  onChange={(e) => handleParameterChange('dividendYield', Number(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Volatility
                </label>
                <Input
                  type="number"
                  step="0.01"
                  value={pricingParams.volatility}
                  onChange={(e) => handleParameterChange('volatility', Number(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Days to Expiration
                </label>
                <Input
                  type="number"
                  value={pricingParams.timeToExpiration}
                  onChange={(e) => handleParameterChange('timeToExpiration', Number(e.target.value))}
                  className="w-full"
                />
              </div>
            </Grid>
          </div>

          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200 mb-6">
            {[
              { key: 'chain', label: 'Options Chain' },
              { key: 'greeks', label: 'Greeks Analysis' },
              { key: 'strategy', label: 'Strategy Builder' },
              { key: 'volatility', label: 'Volatility Analysis' }
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

          {/* Options Chain Tab */}
          {activeTab === 'chain' && (
            <div className="space-y-6">
              <div className="flex gap-4 items-center mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Expiration Date
                  </label>
                  <select
                    value={selectedExpiration}
                    onChange={(e) => setSelectedExpiration(e.target.value)}
                    className="border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="2024-03-15">March 15, 2024</option>
                    <option value="2024-04-19">April 19, 2024</option>
                    <option value="2024-05-17">May 17, 2024</option>
                    <option value="2024-06-21">June 21, 2024</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Option Type
                  </label>
                  <select
                    value={selectedOptionType}
                    onChange={(e) => setSelectedOptionType(e.target.value as 'call' | 'put')}
                    className="border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="call">Calls</option>
                    <option value="put">Puts</option>
                  </select>
                </div>
              </div>

              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Options Chain - {selectedExpiration}
                  </Typography>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Strike</th>
                          <th className="text-right py-2">Bid</th>
                          <th className="text-right py-2">Ask</th>
                          <th className="text-right py-2">Last</th>
                          <th className="text-right py-2">Volume</th>
                          <th className="text-right py-2">OI</th>
                          <th className="text-right py-2">IV</th>
                          <th className="text-right py-2">Delta</th>
                          <th className="text-right py-2">Gamma</th>
                          <th className="text-right py-2">Theta</th>
                          <th className="text-right py-2">Vega</th>
                          <th className="text-right py-2">Intrinsic</th>
                          <th className="text-right py-2">Time Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(selectedOptionType === 'call' ? optionsChain.calls : optionsChain.puts).map((option) => (
                          <tr 
                            key={option.strike} 
                            className={`border-b hover:bg-gray-50 cursor-pointer ${
                              selectedStrike === option.strike ? 'bg-blue-50' : ''
                            }`}
                            onClick={() => setSelectedStrike(option.strike)}
                          >
                            <td className="py-2 font-medium">{option.strike}</td>
                            <td className="text-right py-2">{formatCurrency(option.bid)}</td>
                            <td className="text-right py-2">{formatCurrency(option.ask)}</td>
                            <td className="text-right py-2 font-semibold">{formatCurrency(option.last)}</td>
                            <td className="text-right py-2">{formatNumber(option.volume, 0)}</td>
                            <td className="text-right py-2">{formatNumber(option.openInterest, 0)}</td>
                            <td className="text-right py-2">{formatPercent(option.impliedVolatility * 100)}</td>
                            <td className="text-right py-2">{formatNumber(option.delta, 3)}</td>
                            <td className="text-right py-2">{formatNumber(option.gamma, 3)}</td>
                            <td className="text-right py-2">{formatNumber(option.theta, 3)}</td>
                            <td className="text-right py-2">{formatNumber(option.vega, 3)}</td>
                            <td className="text-right py-2">{formatCurrency(option.intrinsicValue)}</td>
                            <td className="text-right py-2">{formatCurrency(option.timeValue)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Greeks Analysis Tab */}
          {activeTab === 'greeks' && (
            <div className="space-y-6">
              <div className="flex gap-4 items-center mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Strike Price
                  </label>
                  <select
                    value={selectedStrike}
                    onChange={(e) => setSelectedStrike(Number(e.target.value))}
                    className="border border-gray-300 rounded-md px-3 py-2"
                  >
                    {optionsChain.calls.map(call => (
                      <option key={call.strike} value={call.strike}>{call.strike}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Option Type
                  </label>
                  <select
                    value={selectedOptionType}
                    onChange={(e) => setSelectedOptionType(e.target.value as 'call' | 'put')}
                    className="border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="call">Call</option>
                    <option value="put">Put</option>
                  </select>
                </div>
              </div>

              <Grid cols={5} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-blue-600">
                      {formatNumber(greeksAnalysis.delta, 3)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Delta
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      Price sensitivity
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-green-600">
                      {formatNumber(greeksAnalysis.gamma, 3)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Gamma
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      Delta sensitivity
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-red-600">
                      {formatNumber(greeksAnalysis.theta, 3)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Theta
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      Time decay
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-purple-600">
                      {formatNumber(greeksAnalysis.vega, 3)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Vega
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      Volatility sensitivity
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-orange-600">
                      {formatNumber(greeksAnalysis.rho, 3)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Rho
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      Interest rate sensitivity
                    </Typography>
                  </div>
                </Card>
              </Grid>

              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Greeks Explanation
                  </Typography>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="mb-2">
                        <span className="font-semibold text-blue-600">Delta:</span> Measures the rate of change of the option price with respect to the underlying asset price.
                      </div>
                      <div className="mb-2">
                        <span className="font-semibold text-green-600">Gamma:</span> Measures the rate of change of delta with respect to the underlying asset price.
                      </div>
                      <div className="mb-2">
                        <span className="font-semibold text-red-600">Theta:</span> Measures the rate of change of the option price with respect to time decay.
                      </div>
                    </div>
                    <div>
                      <div className="mb-2">
                        <span className="font-semibold text-purple-600">Vega:</span> Measures the rate of change of the option price with respect to volatility.
                      </div>
                      <div className="mb-2">
                        <span className="font-semibold text-orange-600">Rho:</span> Measures the rate of change of the option price with respect to interest rates.
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Strategy Builder Tab */}
          {activeTab === 'strategy' && (
            <div className="space-y-6">
              <div className="flex gap-4 items-center mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Select Strategy
                  </label>
                  <select
                    value={selectedStrategy.name}
                    onChange={(e) => {
                      const strategy = strategies.find(s => s.name === e.target.value)
                      if (strategy) setSelectedStrategy(strategy)
                    }}
                    className="border border-gray-300 rounded-md px-3 py-2"
                  >
                    {strategies.map(strategy => (
                      <option key={strategy.name} value={strategy.name}>{strategy.name}</option>
                    ))}
                  </select>
                </div>
                <Button>
                  Create Custom Strategy
                </Button>
              </div>

              <Grid cols={2} gap={6}>
                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      Strategy Details
                    </Typography>
                    <div className="space-y-3">
                      <div>
                        <Typography variant="h4" className="font-medium">{selectedStrategy.name}</Typography>
                        <Typography variant="body2" className="text-gray-600">
                          {selectedStrategy.description}
                        </Typography>
                      </div>
                      <div>
                        <Typography variant="h4" className="font-medium mb-2">Strategy Legs</Typography>
                        {selectedStrategy.legs.map((leg, index) => (
                          <div key={index} className="flex items-center gap-2 text-sm">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              leg.action === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {leg.action.toUpperCase()}
                            </span>
                            <span className="font-medium">{leg.quantity}x</span>
                            <span>{leg.type.toUpperCase()}</span>
                            <span className="font-semibold">{leg.strike}</span>
                            <span className="text-gray-500">@ {formatCurrency(leg.premium)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </Card>

                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      Risk Profile
                    </Typography>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span>Max Profit:</span>
                        <span className={`font-semibold ${
                          selectedStrategy.maxProfit === Infinity ? 'text-green-600' : 'text-blue-600'
                        }`}>
                          {selectedStrategy.maxProfit === Infinity ? 'Unlimited' : formatCurrency(selectedStrategy.maxProfit)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Max Loss:</span>
                        <span className="font-semibold text-red-600">
                          {formatCurrency(selectedStrategy.maxLoss)}
                        </span>
                      </div>
                      <div>
                        <span>Breakeven Points:</span>
                        <div className="mt-1">
                          {selectedStrategy.breakevenPoints.map((point, index) => (
                            <span key={index} className="inline-block bg-gray-100 px-2 py-1 rounded text-sm mr-2">
                              {formatCurrency(point)}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              </Grid>

              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    P&L Diagram
                  </Typography>
                  <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <Typography variant="h4" className="mb-2">P&L Chart</Typography>
                      <Typography variant="body2">
                        Chart visualization would be implemented here
                      </Typography>
                      <div className="mt-4 text-sm">
                        <div>Max Profit: {selectedStrategy.maxProfit === Infinity ? 'Unlimited' : formatCurrency(selectedStrategy.maxProfit)}</div>
                        <div>Max Loss: {formatCurrency(selectedStrategy.maxLoss)}</div>
                        <div>Breakeven: {selectedStrategy.breakevenPoints.map(p => formatCurrency(p)).join(', ')}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Volatility Analysis Tab */}
          {activeTab === 'volatility' && (
            <div className="space-y-6">
              <Grid cols={2} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-blue-600">
                      {formatPercent(greeksAnalysis.impliedVolatility * 100)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Implied Volatility
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-green-600">
                      {formatPercent(greeksAnalysis.historicalVolatility * 100)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Historical Volatility
                    </Typography>
                  </div>
                </Card>
              </Grid>

              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Volatility Skew
                  </Typography>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Strike</th>
                          <th className="text-right py-2">Implied Volatility</th>
                          <th className="text-right py-2">Moneyness</th>
                          <th className="text-right py-2">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {greeksAnalysis.volatilitySkew.map((skew, index) => (
                          <tr key={index} className="border-b">
                            <td className="py-2 font-medium">{skew.strike}</td>
                            <td className="text-right py-2">{formatPercent(skew.impliedVolatility * 100)}</td>
                            <td className="text-right py-2">{formatNumber(skew.moneyness, 3)}</td>
                            <td className="text-right py-2">
                              <span className={`px-2 py-1 rounded text-xs ${
                                skew.moneyness < 0.95 ? 'bg-red-100 text-red-800' :
                                skew.moneyness > 1.05 ? 'bg-green-100 text-green-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {skew.moneyness < 0.95 ? 'ITM' : skew.moneyness > 1.05 ? 'OTM' : 'ATM'}
                              </span>
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

export default OptionsAnalysis
