import React, { useState, useEffect, useMemo } from 'react'
import { Card, Button, Input, Typography, Grid, Flex } from '../ui'
import { formatCurrency, formatPercent, formatNumber } from '../../utils'
import { 
  ComparableCompany, 
  ComparableMetrics, 
  ComparableValuation,
  PeerRanking 
} from '../../types/analytics'

interface ComparableAnalysisProps {
  symbol?: string
  onResults?: (results: ComparableValuation) => void
}

export const ComparableAnalysis: React.FC<ComparableAnalysisProps> = ({
  symbol = 'AAPL',
  onResults
}) => {
  const [targetCompany, setTargetCompany] = useState<ComparableCompany>({
    symbol: 'AAPL',
    name: 'Apple Inc.',
    marketCap: 3000000000000,
    enterpriseValue: 2900000000000,
    revenue: 365000000000,
    ebitda: 110000000000,
    netIncome: 95000000000,
    sharesOutstanding: 16000000000,
    price: 187.5,
    pe: 31.6,
    pb: 45.2,
    ps: 8.2,
    evRevenue: 7.9,
    evEbitda: 26.4,
    peg: 1.8,
    roe: 0.32,
    roa: 0.12,
    debtToEquity: 0.3,
    currentRatio: 1.1,
    industry: 'Technology Hardware',
    sector: 'Technology'
  })

  const [peerCompanies, setPeerCompanies] = useState<ComparableCompany[]>([
    {
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      marketCap: 2800000000000,
      enterpriseValue: 2750000000000,
      revenue: 200000000000,
      ebitda: 85000000000,
      netIncome: 72000000000,
      sharesOutstanding: 7500000000,
      price: 373.3,
      pe: 29.2,
      pb: 12.8,
      ps: 14.0,
      evRevenue: 13.8,
      evEbitda: 32.4,
      peg: 1.6,
      roe: 0.44,
      roa: 0.15,
      debtToEquity: 0.2,
      currentRatio: 2.5,
      industry: 'Software',
      sector: 'Technology'
    },
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      marketCap: 1800000000000,
      enterpriseValue: 1750000000000,
      revenue: 280000000000,
      ebitda: 80000000000,
      netIncome: 60000000000,
      sharesOutstanding: 13000000000,
      price: 138.5,
      pe: 25.8,
      pb: 5.2,
      ps: 6.4,
      evRevenue: 6.3,
      evEbitda: 21.9,
      peg: 1.2,
      roe: 0.18,
      roa: 0.08,
      debtToEquity: 0.1,
      currentRatio: 3.2,
      industry: 'Internet Services',
      sector: 'Technology'
    },
    {
      symbol: 'AMZN',
      name: 'Amazon.com Inc.',
      marketCap: 1500000000000,
      enterpriseValue: 1600000000000,
      revenue: 500000000000,
      ebitda: 60000000000,
      netIncome: 30000000000,
      sharesOutstanding: 10000000000,
      price: 150.0,
      pe: 50.0,
      pb: 8.5,
      ps: 3.0,
      evRevenue: 3.2,
      evEbitda: 26.7,
      peg: 2.5,
      roe: 0.15,
      roa: 0.05,
      debtToEquity: 0.4,
      currentRatio: 1.0,
      industry: 'E-commerce',
      sector: 'Consumer Discretionary'
    },
    {
      symbol: 'TSLA',
      name: 'Tesla Inc.',
      marketCap: 800000000000,
      enterpriseValue: 850000000000,
      revenue: 80000000000,
      ebitda: 15000000000,
      netIncome: 12000000000,
      sharesOutstanding: 3200000000,
      price: 250.0,
      pe: 66.7,
      pb: 15.2,
      ps: 10.0,
      evRevenue: 10.6,
      evEbitda: 56.7,
      peg: 3.3,
      roe: 0.23,
      roa: 0.08,
      debtToEquity: 0.2,
      currentRatio: 1.8,
      industry: 'Electric Vehicles',
      sector: 'Consumer Discretionary'
    },
    {
      symbol: 'NVDA',
      name: 'NVIDIA Corporation',
      marketCap: 1200000000000,
      enterpriseValue: 1180000000000,
      revenue: 60000000000,
      ebitda: 35000000000,
      netIncome: 30000000000,
      sharesOutstanding: 2500000000,
      price: 480.0,
      pe: 40.0,
      pb: 25.8,
      ps: 20.0,
      evRevenue: 19.7,
      evEbitda: 33.7,
      peg: 2.0,
      roe: 0.45,
      roa: 0.20,
      debtToEquity: 0.1,
      currentRatio: 4.5,
      industry: 'Semiconductors',
      sector: 'Technology'
    }
  ])

  const [selectedPeers, setSelectedPeers] = useState<string[]>(['MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA'])
  const [activeTab, setActiveTab] = useState<'peers' | 'multiples' | 'ranking' | 'valuation'>('peers')
  const [filterIndustry, setFilterIndustry] = useState<string>('All')
  const [sortBy, setSortBy] = useState<keyof ComparableCompany>('marketCap')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Calculate comparable metrics
  const comparableMetrics = useMemo((): ComparableMetrics => {
    const filteredPeers = peerCompanies.filter(peer => selectedPeers.includes(peer.symbol))
    
    if (filteredPeers.length === 0) {
      return {
        pe: { min: 0, max: 0, median: 0, mean: 0, percentile25: 0, percentile75: 0, standardDeviation: 0 },
        pb: { min: 0, max: 0, median: 0, mean: 0, percentile25: 0, percentile75: 0, standardDeviation: 0 },
        ps: { min: 0, max: 0, median: 0, mean: 0, percentile25: 0, percentile75: 0, standardDeviation: 0 },
        evRevenue: { min: 0, max: 0, median: 0, mean: 0, percentile25: 0, percentile75: 0, standardDeviation: 0 },
        evEbitda: { min: 0, max: 0, median: 0, mean: 0, percentile25: 0, percentile75: 0, standardDeviation: 0 },
        peg: { min: 0, max: 0, median: 0, mean: 0, percentile25: 0, percentile75: 0, standardDeviation: 0 }
      }
    }

    const calculateMetric = (values: number[]) => {
      const sorted = [...values].sort((a, b) => a - b)
      const n = values.length
      const mean = values.reduce((sum, val) => sum + val, 0) / n
      const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / (n - 1)
      
      return {
        min: sorted[0],
        max: sorted[n - 1],
        median: n % 2 === 0 ? (sorted[n / 2 - 1] + sorted[n / 2]) / 2 : sorted[Math.floor(n / 2)],
        mean,
        percentile25: sorted[Math.floor(n * 0.25)],
        percentile75: sorted[Math.floor(n * 0.75)],
        standardDeviation: Math.sqrt(variance)
      }
    }

    return {
      pe: calculateMetric(filteredPeers.map(p => p.pe)),
      pb: calculateMetric(filteredPeers.map(p => p.pb)),
      ps: calculateMetric(filteredPeers.map(p => p.ps)),
      evRevenue: calculateMetric(filteredPeers.map(p => p.evRevenue)),
      evEbitda: calculateMetric(filteredPeers.map(p => p.evEbitda)),
      peg: calculateMetric(filteredPeers.map(p => p.peg))
    }
  }, [peerCompanies, selectedPeers, filterIndustry])

  // Calculate comparable valuation
  const comparableValuation = useMemo((): ComparableValuation => {
    const peBased = targetCompany.netIncome * comparableMetrics.pe.median
    const pbBased = targetCompany.equity * comparableMetrics.pb.median
    const psBased = targetCompany.revenue * comparableMetrics.ps.median
    const evRevenueBased = targetCompany.revenue * comparableMetrics.evRevenue.median
    const evEbitdaBased = targetCompany.ebitda * comparableMetrics.evEbitda.median

    const valuations = [peBased, pbBased, psBased, evRevenueBased, evEbitdaBased]
    const average = valuations.reduce((sum, val) => sum + val, 0) / valuations.length
    const median = [...valuations].sort((a, b) => a - b)[Math.floor(valuations.length / 2)]

    // Weighted average (give more weight to EV-based multiples)
    const weightedAverage = (peBased * 0.2 + pbBased * 0.2 + psBased * 0.2 + evRevenueBased * 0.2 + evEbitdaBased * 0.2)

    return {
      peBased,
      pbBased,
      psBased,
      evRevenueBased,
      evEbitdaBased,
      average,
      median,
      weightedAverage
    }
  }, [targetCompany, comparableMetrics])

  // Calculate peer rankings
  const peerRankings = useMemo((): PeerRanking[] => {
    const filteredPeers = peerCompanies.filter(peer => selectedPeers.includes(peer.symbol))
    
    return filteredPeers.map(peer => {
      // Normalize metrics (0-100 scale)
      const valuationScore = Math.max(0, 100 - Math.abs(peer.pe - comparableMetrics.pe.median) * 2)
      const profitabilityScore = (peer.roe * 50 + peer.roa * 50) * 100
      const growthScore = Math.max(0, 100 - peer.peg * 20) // Lower PEG is better
      const financialHealthScore = (peer.currentRatio * 20 + (1 - peer.debtToEquity) * 30) * 100
      
      const overallScore = (valuationScore * 0.3 + profitabilityScore * 0.3 + growthScore * 0.2 + financialHealthScore * 0.2)
      
      return {
        symbol: peer.symbol,
        name: peer.name,
        overallScore: Math.min(100, Math.max(0, overallScore)),
        valuationScore: Math.min(100, Math.max(0, valuationScore)),
        profitabilityScore: Math.min(100, Math.max(0, profitabilityScore)),
        growthScore: Math.min(100, Math.max(0, growthScore)),
        financialHealthScore: Math.min(100, Math.max(0, financialHealthScore)),
        rank: 0 // Will be set after sorting
      }
    }).sort((a, b) => b.overallScore - a.overallScore)
    .map((peer, index) => ({ ...peer, rank: index + 1 }))
  }, [peerCompanies, selectedPeers, comparableMetrics])

  // Filtered and sorted peers
  const filteredPeers = useMemo(() => {
    let filtered = peerCompanies.filter(peer => 
      filterIndustry === 'All' || peer.industry === filterIndustry
    )
    
    filtered.sort((a, b) => {
      const aVal = a[sortBy] as number
      const bVal = b[sortBy] as number
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal
    })
    
    return filtered
  }, [peerCompanies, filterIndustry, sortBy, sortOrder])

  const industries = useMemo(() => {
    const uniqueIndustries = Array.from(new Set(peerCompanies.map(p => p.industry)))
    return ['All', ...uniqueIndustries]
  }, [peerCompanies])

  const handlePeerSelection = (symbol: string, selected: boolean) => {
    if (selected) {
      setSelectedPeers(prev => [...prev, symbol])
    } else {
      setSelectedPeers(prev => prev.filter(s => s !== symbol))
    }
  }

  const handleSort = (field: keyof ComparableCompany) => {
    if (sortBy === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('desc')
    }
  }

  useEffect(() => {
    if (onResults) {
      onResults(comparableValuation)
    }
  }, [comparableValuation, onResults])

  return (
    <div className="space-y-6">
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <Typography variant="h2" className="text-2xl font-bold">
              Comparable Analysis - {targetCompany.symbol}
            </Typography>
            <div className="flex gap-2">
              <Button variant="outline">
                Export
              </Button>
              <Button>
                Add Peer
              </Button>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200 mb-6">
            {[
              { key: 'peers', label: 'Peer Selection' },
              { key: 'multiples', label: 'Valuation Multiples' },
              { key: 'ranking', label: 'Peer Ranking' },
              { key: 'valuation', label: 'Valuation Summary' }
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

          {/* Peer Selection Tab */}
          {activeTab === 'peers' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex gap-4 items-center">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Filter by Industry
                  </label>
                  <select
                    value={filterIndustry}
                    onChange={(e) => setFilterIndustry(e.target.value)}
                    className="border border-gray-300 rounded-md px-3 py-2"
                  >
                    {industries.map(industry => (
                      <option key={industry} value={industry}>{industry}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sort by
                  </label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as keyof ComparableCompany)}
                    className="border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="marketCap">Market Cap</option>
                    <option value="pe">P/E Ratio</option>
                    <option value="pb">P/B Ratio</option>
                    <option value="ps">P/S Ratio</option>
                    <option value="evEbitda">EV/EBITDA</option>
                    <option value="roe">ROE</option>
                    <option value="roa">ROA</option>
                  </select>
                </div>
                <Button
                  variant="outline"
                  onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
                >
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </Button>
              </div>

              {/* Peer Companies Table */}
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Peer Companies ({filteredPeers.length})
                  </Typography>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">
                            <input
                              type="checkbox"
                              checked={selectedPeers.length === filteredPeers.length}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedPeers(filteredPeers.map(p => p.symbol))
                                } else {
                                  setSelectedPeers([])
                                }
                              }}
                            />
                          </th>
                          <th className="text-left py-2 cursor-pointer" onClick={() => handleSort('symbol')}>
                            Symbol {sortBy === 'symbol' && (sortOrder === 'asc' ? '↑' : '↓')}
                          </th>
                          <th className="text-left py-2">Name</th>
                          <th className="text-right py-2 cursor-pointer" onClick={() => handleSort('marketCap')}>
                            Market Cap {sortBy === 'marketCap' && (sortOrder === 'asc' ? '↑' : '↓')}
                          </th>
                          <th className="text-right py-2 cursor-pointer" onClick={() => handleSort('pe')}>
                            P/E {sortBy === 'pe' && (sortOrder === 'asc' ? '↑' : '↓')}
                          </th>
                          <th className="text-right py-2 cursor-pointer" onClick={() => handleSort('pb')}>
                            P/B {sortBy === 'pb' && (sortOrder === 'asc' ? '↑' : '↓')}
                          </th>
                          <th className="text-right py-2 cursor-pointer" onClick={() => handleSort('ps')}>
                            P/S {sortBy === 'ps' && (sortOrder === 'asc' ? '↑' : '↓')}
                          </th>
                          <th className="text-right py-2 cursor-pointer" onClick={() => handleSort('evEbitda')}>
                            EV/EBITDA {sortBy === 'evEbitda' && (sortOrder === 'asc' ? '↑' : '↓')}
                          </th>
                          <th className="text-right py-2 cursor-pointer" onClick={() => handleSort('roe')}>
                            ROE {sortBy === 'roe' && (sortOrder === 'asc' ? '↑' : '↓')}
                          </th>
                          <th className="text-left py-2">Industry</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredPeers.map((peer) => (
                          <tr key={peer.symbol} className="border-b hover:bg-gray-50">
                            <td className="py-2">
                              <input
                                type="checkbox"
                                checked={selectedPeers.includes(peer.symbol)}
                                onChange={(e) => handlePeerSelection(peer.symbol, e.target.checked)}
                              />
                            </td>
                            <td className="py-2 font-medium">{peer.symbol}</td>
                            <td className="py-2">{peer.name}</td>
                            <td className="text-right py-2">{formatCurrency(peer.marketCap)}</td>
                            <td className="text-right py-2">{formatNumber(peer.pe, 1)}</td>
                            <td className="text-right py-2">{formatNumber(peer.pb, 1)}</td>
                            <td className="text-right py-2">{formatNumber(peer.ps, 1)}</td>
                            <td className="text-right py-2">{formatNumber(peer.evEbitda, 1)}</td>
                            <td className="text-right py-2">{formatPercent(peer.roe * 100)}</td>
                            <td className="py-2">{peer.industry}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Valuation Multiples Tab */}
          {activeTab === 'multiples' && (
            <div className="space-y-6">
              <Grid cols={3} gap={4}>
                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      P/E Ratio
                    </Typography>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Min:</span>
                        <span>{formatNumber(comparableMetrics.pe.min, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>25th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.pe.percentile25, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Median:</span>
                        <span className="font-semibold">{formatNumber(comparableMetrics.pe.median, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>75th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.pe.percentile75, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Max:</span>
                        <span>{formatNumber(comparableMetrics.pe.max, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Mean:</span>
                        <span>{formatNumber(comparableMetrics.pe.mean, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Std Dev:</span>
                        <span>{formatNumber(comparableMetrics.pe.standardDeviation, 1)}</span>
                      </div>
                    </div>
                  </div>
                </Card>

                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      P/B Ratio
                    </Typography>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Min:</span>
                        <span>{formatNumber(comparableMetrics.pb.min, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>25th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.pb.percentile25, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Median:</span>
                        <span className="font-semibold">{formatNumber(comparableMetrics.pb.median, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>75th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.pb.percentile75, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Max:</span>
                        <span>{formatNumber(comparableMetrics.pb.max, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Mean:</span>
                        <span>{formatNumber(comparableMetrics.pb.mean, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Std Dev:</span>
                        <span>{formatNumber(comparableMetrics.pb.standardDeviation, 1)}</span>
                      </div>
                    </div>
                  </div>
                </Card>

                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      P/S Ratio
                    </Typography>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Min:</span>
                        <span>{formatNumber(comparableMetrics.ps.min, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>25th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.ps.percentile25, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Median:</span>
                        <span className="font-semibold">{formatNumber(comparableMetrics.ps.median, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>75th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.ps.percentile75, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Max:</span>
                        <span>{formatNumber(comparableMetrics.ps.max, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Mean:</span>
                        <span>{formatNumber(comparableMetrics.ps.mean, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Std Dev:</span>
                        <span>{formatNumber(comparableMetrics.ps.standardDeviation, 1)}</span>
                      </div>
                    </div>
                  </div>
                </Card>

                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      EV/Revenue
                    </Typography>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Min:</span>
                        <span>{formatNumber(comparableMetrics.evRevenue.min, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>25th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.evRevenue.percentile25, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Median:</span>
                        <span className="font-semibold">{formatNumber(comparableMetrics.evRevenue.median, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>75th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.evRevenue.percentile75, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Max:</span>
                        <span>{formatNumber(comparableMetrics.evRevenue.max, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Mean:</span>
                        <span>{formatNumber(comparableMetrics.evRevenue.mean, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Std Dev:</span>
                        <span>{formatNumber(comparableMetrics.evRevenue.standardDeviation, 1)}</span>
                      </div>
                    </div>
                  </div>
                </Card>

                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      EV/EBITDA
                    </Typography>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Min:</span>
                        <span>{formatNumber(comparableMetrics.evEbitda.min, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>25th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.evEbitda.percentile25, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Median:</span>
                        <span className="font-semibold">{formatNumber(comparableMetrics.evEbitda.median, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>75th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.evEbitda.percentile75, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Max:</span>
                        <span>{formatNumber(comparableMetrics.evEbitda.max, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Mean:</span>
                        <span>{formatNumber(comparableMetrics.evEbitda.mean, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Std Dev:</span>
                        <span>{formatNumber(comparableMetrics.evEbitda.standardDeviation, 1)}</span>
                      </div>
                    </div>
                  </div>
                </Card>

                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      PEG Ratio
                    </Typography>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Min:</span>
                        <span>{formatNumber(comparableMetrics.peg.min, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>25th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.peg.percentile25, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Median:</span>
                        <span className="font-semibold">{formatNumber(comparableMetrics.peg.median, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>75th Percentile:</span>
                        <span>{formatNumber(comparableMetrics.peg.percentile75, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Max:</span>
                        <span>{formatNumber(comparableMetrics.peg.max, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Mean:</span>
                        <span>{formatNumber(comparableMetrics.peg.mean, 1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Std Dev:</span>
                        <span>{formatNumber(comparableMetrics.peg.standardDeviation, 1)}</span>
                      </div>
                    </div>
                  </div>
                </Card>
              </Grid>
            </div>
          )}

          {/* Peer Ranking Tab */}
          {activeTab === 'ranking' && (
            <div className="space-y-6">
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Peer Ranking Analysis
                  </Typography>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Rank</th>
                          <th className="text-left py-2">Company</th>
                          <th className="text-right py-2">Overall Score</th>
                          <th className="text-right py-2">Valuation</th>
                          <th className="text-right py-2">Profitability</th>
                          <th className="text-right py-2">Growth</th>
                          <th className="text-right py-2">Financial Health</th>
                        </tr>
                      </thead>
                      <tbody>
                        {peerRankings.map((peer) => (
                          <tr key={peer.symbol} className="border-b">
                            <td className="py-2 font-bold">#{peer.rank}</td>
                            <td className="py-2">
                              <div>
                                <div className="font-medium">{peer.symbol}</div>
                                <div className="text-gray-500 text-xs">{peer.name}</div>
                              </div>
                            </td>
                            <td className="text-right py-2">
                              <div className="font-bold text-lg">{formatNumber(peer.overallScore, 0)}</div>
                            </td>
                            <td className="text-right py-2">{formatNumber(peer.valuationScore, 0)}</td>
                            <td className="text-right py-2">{formatNumber(peer.profitabilityScore, 0)}</td>
                            <td className="text-right py-2">{formatNumber(peer.growthScore, 0)}</td>
                            <td className="text-right py-2">{formatNumber(peer.financialHealthScore, 0)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Valuation Summary Tab */}
          {activeTab === 'valuation' && (
            <div className="space-y-6">
              <Grid cols={3} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-blue-600">
                      {formatCurrency(comparableValuation.average)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Average Valuation
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-green-600">
                      {formatCurrency(comparableValuation.median)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Median Valuation
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-purple-600">
                      {formatCurrency(comparableValuation.weightedAverage)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Weighted Average
                    </Typography>
                  </div>
                </Card>
              </Grid>

              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Valuation Breakdown
                  </Typography>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>P/E Based:</span>
                        <span className="font-semibold">{formatCurrency(comparableValuation.peBased)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>P/B Based:</span>
                        <span className="font-semibold">{formatCurrency(comparableValuation.pbBased)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>P/S Based:</span>
                        <span className="font-semibold">{formatCurrency(comparableValuation.psBased)}</span>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between py-2 border-b">
                        <span>EV/Revenue Based:</span>
                        <span className="font-semibold">{formatCurrency(comparableValuation.evRevenueBased)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>EV/EBITDA Based:</span>
                        <span className="font-semibold">{formatCurrency(comparableValuation.evEbitdaBased)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b">
                        <span>Current Market Cap:</span>
                        <span className="font-semibold">{formatCurrency(targetCompany.marketCap)}</span>
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

export default ComparableAnalysis
