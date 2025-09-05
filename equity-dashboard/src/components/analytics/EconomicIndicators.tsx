import React, { useState, useEffect, useMemo } from 'react'
import { Card, Button, Input, Typography, Grid, Flex } from '../ui'
import { formatCurrency, formatPercent, formatNumber, formatDate } from '../../utils'
import { 
  EconomicIndicator,
  EconomicCalendar,
  EconomicEvent,
  InterestRateData,
  InflationData,
  GDPData,
  EmploymentData,
  MarketSentiment
} from '../../types/analytics'

interface EconomicIndicatorsProps {
  onResults?: (results: EconomicIndicator[]) => void
}

export const EconomicIndicators: React.FC<EconomicIndicatorsProps> = ({
  onResults
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'calendar' | 'rates' | 'inflation' | 'gdp' | 'employment' | 'sentiment'>('overview')
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0])
  const [selectedCountry, setSelectedCountry] = useState<string>('US')

  // Sample economic indicators data
  const economicIndicators = useMemo((): EconomicIndicator[] => [
    {
      name: 'Federal Funds Rate',
      symbol: 'FEDFUNDS',
      value: 5.25,
      previousValue: 5.00,
      change: 0.25,
      changePercent: 5.0,
      unit: '%',
      frequency: 'Monthly',
      lastUpdated: '2024-01-31',
      source: 'Federal Reserve',
      description: 'The interest rate at which depository institutions lend reserve balances to other depository institutions overnight'
    },
    {
      name: 'Consumer Price Index',
      symbol: 'CPI',
      value: 308.417,
      previousValue: 307.051,
      change: 1.366,
      changePercent: 0.44,
      unit: 'Index',
      frequency: 'Monthly',
      lastUpdated: '2024-01-31',
      source: 'Bureau of Labor Statistics',
      description: 'A measure of the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services'
    },
    {
      name: 'Core CPI',
      symbol: 'CPILFESL',
      value: 312.083,
      previousValue: 311.690,
      change: 0.393,
      changePercent: 0.13,
      unit: 'Index',
      frequency: 'Monthly',
      lastUpdated: '2024-01-31',
      source: 'Bureau of Labor Statistics',
      description: 'Consumer Price Index excluding food and energy prices'
    },
    {
      name: 'Unemployment Rate',
      symbol: 'UNRATE',
      value: 3.7,
      previousValue: 3.8,
      change: -0.1,
      changePercent: -2.63,
      unit: '%',
      frequency: 'Monthly',
      lastUpdated: '2024-01-31',
      source: 'Bureau of Labor Statistics',
      description: 'The percentage of the labor force that is unemployed'
    },
    {
      name: 'Non-Farm Payrolls',
      symbol: 'PAYEMS',
      value: 157366,
      previousValue: 157000,
      change: 366,
      changePercent: 0.23,
      unit: 'Thousands',
      frequency: 'Monthly',
      lastUpdated: '2024-01-31',
      source: 'Bureau of Labor Statistics',
      description: 'Total number of paid U.S. workers excluding farm workers, government employees, and employees of nonprofit organizations'
    },
    {
      name: 'GDP Growth Rate',
      symbol: 'GDPC1',
      value: 2.5,
      previousValue: 2.1,
      change: 0.4,
      changePercent: 19.05,
      unit: '%',
      frequency: 'Quarterly',
      lastUpdated: '2024-01-31',
      source: 'Bureau of Economic Analysis',
      description: 'The annualized rate of growth of the gross domestic product'
    },
    {
      name: '10-Year Treasury Yield',
      symbol: 'DGS10',
      value: 4.25,
      previousValue: 4.15,
      change: 0.10,
      changePercent: 2.41,
      unit: '%',
      frequency: 'Daily',
      lastUpdated: '2024-01-31',
      source: 'Federal Reserve',
      description: 'The yield on 10-year U.S. Treasury bonds'
    },
    {
      name: 'VIX',
      symbol: 'VIX',
      value: 18.5,
      previousValue: 20.2,
      change: -1.7,
      changePercent: -8.42,
      unit: 'Index',
      frequency: 'Daily',
      lastUpdated: '2024-01-31',
      source: 'CBOE',
      description: 'The Chicago Board Options Exchange Volatility Index, a measure of market expectations of volatility'
    }
  ], [])

  // Economic calendar data
  const economicCalendar = useMemo((): EconomicCalendar[] => {
    const calendar: EconomicCalendar[] = []
    const today = new Date()
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(today)
      date.setDate(date.getDate() + i)
      const dateStr = date.toISOString().split('T')[0]
      
      const events: EconomicEvent[] = [
        {
          time: '08:30',
          country: 'US',
          event: 'Non-Farm Payrolls',
          importance: 'High',
          actual: i === 0 ? 157366 : null,
          forecast: 157000,
          previous: 156500,
          unit: 'K',
        },
        {
          time: '10:00',
          country: 'US',
          event: 'ISM Manufacturing PMI',
          importance: 'Medium',
          actual: i === 1 ? 49.1 : null,
          forecast: 49.5,
          previous: 48.7,
          unit: 'Index',
        },
        {
          time: '14:00',
          country: 'US',
          event: 'FOMC Meeting Minutes',
          importance: 'High',
          actual: null,
          forecast: null,
          previous: null,
          unit: '',
        }
      ]
      
      calendar.push({
        date: dateStr,
        events: events.filter((_, index) => index < (i % 3) + 1) // Vary number of events
      })
    }
    
    return calendar
  }, [])

  // Interest rate data
  const interestRateData = useMemo((): InterestRateData => ({
    rate: 5.25,
    previousRate: 5.00,
    change: 0.25,
    effectiveDate: '2024-01-31',
    nextMeeting: '2024-03-20',
    targetRange: {
      lower: 5.00,
      upper: 5.50
    }
  }), [])

  // Inflation data
  const inflationData = useMemo((): InflationData => ({
    cpi: 308.417,
    cpiChange: 0.44,
    coreCpi: 312.083,
    coreCpiChange: 0.13,
    pce: 121.5,
    pceChange: 0.35,
    corePce: 118.2,
    corePceChange: 0.25,
    lastUpdated: '2024-01-31',
  }), [])

  // GDP data
  const gdpData = useMemo((): GDPData => ({
    gdp: 28000000, // $28 trillion
    gdpGrowth: 2.5,
    gdpPerCapita: 85000,
    gdpPerCapitaGrowth: 1.8,
    lastUpdated: '2024-01-31',
    quarter: 'Q4 2023'
  }), [])

  // Employment data
  const employmentData = useMemo((): EmploymentData => ({
    unemploymentRate: 3.7,
    unemploymentRateChange: -0.1,
    nonFarmPayrolls: 157366,
    nonFarmPayrollsChange: 366,
    laborForceParticipation: 62.5,
    laborForceParticipationChange: 0.1,
    lastUpdated: '2024-01-31'
  }), [])

  // Market sentiment data
  const marketSentiment = useMemo((): MarketSentiment => ({
    vix: 18.5,
    vixChange: -1.7,
    fearGreedIndex: 65,
    putCallRatio: 0.85,
    insiderTrading: -0.2,
    institutionalFlow: 2.5,
    retailFlow: -1.8,
    lastUpdated: '2024-01-31'
  }), [])

  const countries = ['US', 'EU', 'UK', 'JP', 'CN', 'CA', 'AU']
  const importanceLevels = ['Low', 'Medium', 'High']

  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'High': return 'bg-red-100 text-red-800'
      case 'Medium': return 'bg-yellow-100 text-yellow-800'
      case 'Low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-green-600'
    if (change < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  useEffect(() => {
    if (onResults) {
      onResults(economicIndicators)
    }
  }, [economicIndicators, onResults])

  return (
    <div className="space-y-6">
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <Typography variant="h2" className="text-2xl font-bold">
              Economic Indicators
            </Typography>
            <div className="flex gap-2">
              <Button variant="outline">
                Export Data
              </Button>
              <Button>
                Refresh
              </Button>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-4 items-center mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Country
              </label>
              <select
                value={selectedCountry}
                onChange={(e) => setSelectedCountry(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2"
              >
                {countries.map(country => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date
              </label>
              <Input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full"
              />
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200 mb-6">
            {[
              { key: 'overview', label: 'Overview' },
              { key: 'calendar', label: 'Economic Calendar' },
              { key: 'rates', label: 'Interest Rates' },
              { key: 'inflation', label: 'Inflation' },
              { key: 'gdp', label: 'GDP' },
              { key: 'employment', label: 'Employment' },
              { key: 'sentiment', label: 'Market Sentiment' }
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

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <Grid cols={4} gap={4}>
                {economicIndicators.slice(0, 8).map((indicator, index) => (
                  <Card key={index}>
                    <div className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Typography variant="h4" className="font-semibold text-sm">
                          {indicator.name}
                        </Typography>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          indicator.change >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {indicator.change >= 0 ? '+' : ''}{formatPercent(indicator.changePercent)}
                        </span>
                      </div>
                      <Typography variant="h3" className="text-xl font-bold mb-1">
                        {formatNumber(indicator.value, 2)} {indicator.unit}
                      </Typography>
                      <Typography variant="body2" className="text-gray-600 mb-2">
                        Previous: {formatNumber(indicator.previousValue, 2)} {indicator.unit}
                      </Typography>
                      <Typography variant="caption" className="text-gray-500">
                        {indicator.frequency} • {formatDate(indicator.lastUpdated)}
                      </Typography>
                    </div>
                  </Card>
                ))}
              </Grid>
            </div>
          )}

          {/* Economic Calendar Tab */}
          {activeTab === 'calendar' && (
            <div className="space-y-6">
              {economicCalendar.map((day, index) => (
                <Card key={index}>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      {formatDate(day.date)}
                    </Typography>
                    <div className="space-y-3">
                      {day.events.map((event, eventIndex) => (
                        <div key={eventIndex} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                          <div className="flex items-center gap-4">
                            <span className="font-mono text-sm text-gray-600">
                              {event.time}
                            </span>
                            <div>
                              <Typography variant="h4" className="font-medium">
                                {event.event}
                              </Typography>
                              <Typography variant="body2" className="text-gray-600">
                                {event.country}
                              </Typography>
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getImportanceColor(event.importance)}`}>
                              {event.importance}
                            </span>
                            <div className="text-right text-sm">
                              {event.actual !== null && (
                                <div className="font-semibold">
                                  {formatNumber(event.actual, 1)} {event.unit}
                                </div>
                              )}
                              {event.forecast !== null && (
                                <div className="text-gray-600">
                                  Est: {formatNumber(event.forecast, 1)} {event.unit}
                                </div>
                              )}
                              {event.previous !== null && (
                                <div className="text-gray-500">
                                  Prev: {formatNumber(event.previous, 1)} {event.unit}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Interest Rates Tab */}
          {activeTab === 'rates' && (
            <div className="space-y-6">
              <Grid cols={3} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-blue-600">
                      {formatPercent(interestRateData.rate)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Current Rate
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography 
                      variant="h3" 
                      className={`text-2xl font-bold ${getChangeColor(interestRateData.change)}`}
                    >
                      {interestRateData.change >= 0 ? '+' : ''}{formatPercent(interestRateData.change)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Change
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-purple-600">
                      {formatDate(interestRateData.nextMeeting)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Next Meeting
                    </Typography>
                  </div>
                </Card>
              </Grid>

              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Interest Rate Details
                  </Typography>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Current Rate:</span>
                        <span className="font-semibold">{formatPercent(interestRateData.rate)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Previous Rate:</span>
                        <span className="font-semibold">{formatPercent(interestRateData.previousRate)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Change:</span>
                        <span className={`font-semibold ${getChangeColor(interestRateData.change)}`}>
                          {interestRateData.change >= 0 ? '+' : ''}{formatPercent(interestRateData.change)}
                        </span>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Target Range:</span>
                        <span className="font-semibold">
                          {formatPercent(interestRateData.targetRange.lower)} - {formatPercent(interestRateData.targetRange.upper)}
                        </span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Effective Date:</span>
                        <span className="font-semibold">{formatDate(interestRateData.effectiveDate)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Next Meeting:</span>
                        <span className="font-semibold">{formatDate(interestRateData.nextMeeting)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Inflation Tab */}
          {activeTab === 'inflation' && (
            <div className="space-y-6">
              <Grid cols={4} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-blue-600">
                      {formatNumber(inflationData.cpi, 1)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      CPI
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      {formatPercent(inflationData.cpiChange)} MoM
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-green-600">
                      {formatNumber(inflationData.coreCpi, 1)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Core CPI
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      {formatPercent(inflationData.coreCpiChange)} MoM
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-purple-600">
                      {formatNumber(inflationData.pce, 1)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      PCE
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      {formatPercent(inflationData.pceChange)} MoM
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-orange-600">
                      {formatNumber(inflationData.corePce, 1)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Core PCE
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      {formatPercent(inflationData.corePceChange)} MoM
                    </Typography>
                  </div>
                </Card>
              </Grid>
            </div>
          )}

          {/* GDP Tab */}
          {activeTab === 'gdp' && (
            <div className="space-y-6">
              <Grid cols={3} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-blue-600">
                      {formatCurrency(gdpData.gdp)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      GDP
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography 
                      variant="h3" 
                      className={`text-2xl font-bold ${getChangeColor(gdpData.gdpGrowth)}`}
                    >
                      {formatPercent(gdpData.gdpGrowth)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      GDP Growth
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-green-600">
                      {formatCurrency(gdpData.gdpPerCapita)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      GDP Per Capita
                    </Typography>
                  </div>
                </Card>
              </Grid>

              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    GDP Details - {gdpData.quarter}
                  </Typography>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>GDP:</span>
                        <span className="font-semibold">{formatCurrency(gdpData.gdp)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>GDP Growth:</span>
                        <span className={`font-semibold ${getChangeColor(gdpData.gdpGrowth)}`}>
                          {formatPercent(gdpData.gdpGrowth)}
                        </span>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>GDP Per Capita:</span>
                        <span className="font-semibold">{formatCurrency(gdpData.gdpPerCapita)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Per Capita Growth:</span>
                        <span className={`font-semibold ${getChangeColor(gdpData.gdpPerCapitaGrowth)}`}>
                          {formatPercent(gdpData.gdpPerCapitaGrowth)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Employment Tab */}
          {activeTab === 'employment' && (
            <div className="space-y-6">
              <Grid cols={3} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-blue-600">
                      {formatPercent(employmentData.unemploymentRate)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Unemployment Rate
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      {employmentData.unemploymentRateChange >= 0 ? '+' : ''}{formatPercent(employmentData.unemploymentRateChange)} MoM
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-green-600">
                      {formatNumber(employmentData.nonFarmPayrolls, 0)}K
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Non-Farm Payrolls
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      {employmentData.nonFarmPayrollsChange >= 0 ? '+' : ''}{formatNumber(employmentData.nonFarmPayrollsChange, 0)}K MoM
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-purple-600">
                      {formatPercent(employmentData.laborForceParticipation)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Labor Force Participation
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      {employmentData.laborForceParticipationChange >= 0 ? '+' : ''}{formatPercent(employmentData.laborForceParticipationChange)} MoM
                    </Typography>
                  </div>
                </Card>
              </Grid>
            </div>
          )}

          {/* Market Sentiment Tab */}
          {activeTab === 'sentiment' && (
            <div className="space-y-6">
              <Grid cols={4} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-blue-600">
                      {formatNumber(marketSentiment.vix, 1)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      VIX
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      {marketSentiment.vixChange >= 0 ? '+' : ''}{formatNumber(marketSentiment.vixChange, 1)} Change
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-green-600">
                      {marketSentiment.fearGreedIndex}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Fear & Greed Index
                    </Typography>
                    <Typography variant="caption" className="text-gray-500">
                      {marketSentiment.fearGreedIndex > 50 ? 'Greed' : 'Fear'}
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-purple-600">
                      {formatNumber(marketSentiment.putCallRatio, 2)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Put/Call Ratio
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-orange-600">
                      {formatNumber(marketSentiment.institutionalFlow, 1)}B
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Institutional Flow
                    </Typography>
                  </div>
                </Card>
              </Grid>

              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Market Sentiment Details
                  </Typography>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>VIX:</span>
                        <span className="font-semibold">{formatNumber(marketSentiment.vix, 1)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Fear & Greed Index:</span>
                        <span className="font-semibold">{marketSentiment.fearGreedIndex}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Put/Call Ratio:</span>
                        <span className="font-semibold">{formatNumber(marketSentiment.putCallRatio, 2)}</span>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Insider Trading:</span>
                        <span className={`font-semibold ${getChangeColor(marketSentiment.insiderTrading)}`}>
                          {formatNumber(marketSentiment.insiderTrading, 1)}B
                        </span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Institutional Flow:</span>
                        <span className={`font-semibold ${getChangeColor(marketSentiment.institutionalFlow)}`}>
                          {formatNumber(marketSentiment.institutionalFlow, 1)}B
                        </span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Retail Flow:</span>
                        <span className={`font-semibold ${getChangeColor(marketSentiment.retailFlow)}`}>
                          {formatNumber(marketSentiment.retailFlow, 1)}B
                        </span>
                      </div>
                    </div>
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

export default EconomicIndicators
