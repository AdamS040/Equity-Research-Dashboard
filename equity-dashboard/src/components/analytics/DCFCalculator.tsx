import React, { useState, useEffect, useMemo } from 'react'
import { Card, Button, Input, Typography, Grid, Flex } from '../ui'
import { formatCurrency, formatPercent, formatNumber } from '../../utils'
import { 
  DCFInputs, 
  DCFResults, 
  DCFScenario,
  MonteCarloResults 
} from '../../types/analytics'
import { 
  calculateDCF, 
  runMonteCarloSimulation,
  calculateWACC,
  calculateCostOfEquity 
} from '../../utils/financial-calculations'

interface DCFCalculatorProps {
  symbol?: string
  currentPrice?: number
  onResults?: (results: DCFResults) => void
}

export const DCFCalculator: React.FC<DCFCalculatorProps> = ({
  symbol = 'AAPL',
  currentPrice = 150,
  onResults
}) => {
  const [inputs, setInputs] = useState<DCFInputs>({
    symbol,
    currentPrice,
    revenue: 365000000000, // $365B
    revenueGrowthRate: 0.05, // 5%
    ebitdaMargin: 0.30, // 30%
    taxRate: 0.25, // 25%
    capex: 10000000000, // $10B
    workingCapital: 5000000000, // $5B
    terminalGrowthRate: 0.025, // 2.5%
    wacc: 0.08, // 8%
    beta: 1.2,
    riskFreeRate: 0.04, // 4%
    marketRiskPremium: 0.06, // 6%
    debtToEquity: 0.3, // 30%
    costOfDebt: 0.05, // 5%
    projectionYears: 10
  })

  const [scenarios, setScenarios] = useState<DCFScenario[]>([
    {
      name: 'Base Case',
      probability: 0.5,
      revenueGrowth: 0.05,
      ebitdaMargin: 0.30,
      terminalGrowth: 0.025,
      wacc: 0.08,
      fairValue: 0
    },
    {
      name: 'Bull Case',
      probability: 0.25,
      revenueGrowth: 0.08,
      ebitdaMargin: 0.35,
      terminalGrowth: 0.03,
      wacc: 0.07,
      fairValue: 0
    },
    {
      name: 'Bear Case',
      probability: 0.25,
      revenueGrowth: 0.02,
      ebitdaMargin: 0.25,
      terminalGrowth: 0.02,
      wacc: 0.09,
      fairValue: 0
    }
  ])

  const [activeTab, setActiveTab] = useState<'inputs' | 'results' | 'sensitivity' | 'monte-carlo' | 'scenarios'>('inputs')

  // Calculate WACC automatically
  const calculatedWACC = useMemo(() => {
    const costOfEquity = calculateCostOfEquity(
      inputs.riskFreeRate,
      inputs.beta,
      inputs.marketRiskPremium
    )
    
    // Assume market cap and debt values for calculation
    const equityValue = inputs.currentPrice * 1000000000 // Assume 1B shares
    const debtValue = equityValue * inputs.debtToEquity
    
    return calculateWACC(equityValue, debtValue, costOfEquity, inputs.costOfDebt, inputs.taxRate)
  }, [inputs.riskFreeRate, inputs.beta, inputs.marketRiskPremium, inputs.debtToEquity, inputs.costOfDebt, inputs.taxRate, inputs.currentPrice])

  // Calculate DCF results
  const dcfResults = useMemo(() => {
    const results = calculateDCF(inputs)
    if (onResults) {
      onResults(results)
    }
    return results
  }, [inputs, onResults])

  // Calculate scenario results
  const scenarioResults = useMemo(() => {
    return scenarios.map(scenario => {
      const scenarioInputs = {
        ...inputs,
        revenueGrowthRate: scenario.revenueGrowth,
        ebitdaMargin: scenario.ebitdaMargin,
        terminalGrowthRate: scenario.terminalGrowth,
        wacc: scenario.wacc
      }
      const result = calculateDCF(scenarioInputs)
      return { ...scenario, fairValue: result.fairValue }
    })
  }, [inputs, scenarios])

  const handleInputChange = (field: keyof DCFInputs, value: number) => {
    setInputs(prev => ({ ...prev, [field]: value }))
  }

  const handleScenarioChange = (index: number, field: keyof DCFScenario, value: number) => {
    setScenarios(prev => prev.map((scenario, i) => 
      i === index ? { ...scenario, [field]: value } : scenario
    ))
  }

  const resetToDefaults = () => {
    setInputs({
      symbol,
      currentPrice,
      revenue: 365000000000,
      revenueGrowthRate: 0.05,
      ebitdaMargin: 0.30,
      taxRate: 0.25,
      capex: 10000000000,
      workingCapital: 5000000000,
      terminalGrowthRate: 0.025,
      wacc: 0.08,
      beta: 1.2,
      riskFreeRate: 0.04,
      marketRiskPremium: 0.06,
      debtToEquity: 0.3,
      costOfDebt: 0.05,
      projectionYears: 10
    })
  }

  return (
    <div className="space-y-6">
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <Typography variant="h2" className="text-2xl font-bold">
              DCF Calculator - {inputs.symbol}
            </Typography>
            <div className="flex gap-2">
              <Button variant="outline" onClick={resetToDefaults}>
                Reset
              </Button>
              <Button onClick={() => setActiveTab('results')}>
                Calculate
              </Button>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200 mb-6">
            {[
              { key: 'inputs', label: 'Inputs' },
              { key: 'results', label: 'Results' },
              { key: 'sensitivity', label: 'Sensitivity' },
              { key: 'monte-carlo', label: 'Monte Carlo' },
              { key: 'scenarios', label: 'Scenarios' }
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

          {/* Inputs Tab */}
          {activeTab === 'inputs' && (
            <div className="space-y-6">
              <Grid cols={2} gap={6}>
                {/* Basic Information */}
                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      Basic Information
                    </Typography>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Current Price
                        </label>
                        <Input
                          type="number"
                          value={inputs.currentPrice}
                          onChange={(e) => handleInputChange('currentPrice', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Revenue (TTM)
                        </label>
                        <Input
                          type="number"
                          value={inputs.revenue}
                          onChange={(e) => handleInputChange('revenue', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Revenue Growth Rate
                        </label>
                        <Input
                          type="number"
                          step="0.01"
                          value={inputs.revenueGrowthRate}
                          onChange={(e) => handleInputChange('revenueGrowthRate', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          EBITDA Margin
                        </label>
                        <Input
                          type="number"
                          step="0.01"
                          value={inputs.ebitdaMargin}
                          onChange={(e) => handleInputChange('ebitdaMargin', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                    </div>
                  </div>
                </Card>

                {/* WACC Components */}
                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      WACC Components
                    </Typography>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Risk-Free Rate
                        </label>
                        <Input
                          type="number"
                          step="0.01"
                          value={inputs.riskFreeRate}
                          onChange={(e) => handleInputChange('riskFreeRate', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Beta
                        </label>
                        <Input
                          type="number"
                          step="0.1"
                          value={inputs.beta}
                          onChange={(e) => handleInputChange('beta', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Market Risk Premium
                        </label>
                        <Input
                          type="number"
                          step="0.01"
                          value={inputs.marketRiskPremium}
                          onChange={(e) => handleInputChange('marketRiskPremium', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Debt-to-Equity Ratio
                        </label>
                        <Input
                          type="number"
                          step="0.1"
                          value={inputs.debtToEquity}
                          onChange={(e) => handleInputChange('debtToEquity', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Terminal Value */}
                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      Terminal Value
                    </Typography>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Terminal Growth Rate
                        </label>
                        <Input
                          type="number"
                          step="0.01"
                          value={inputs.terminalGrowthRate}
                          onChange={(e) => handleInputChange('terminalGrowthRate', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          WACC
                        </label>
                        <Input
                          type="number"
                          step="0.01"
                          value={inputs.wacc}
                          onChange={(e) => handleInputChange('wacc', Number(e.target.value))}
                          className="w-full"
                        />
                        <p className="text-sm text-gray-500 mt-1">
                          Calculated WACC: {formatPercent(calculatedWACC * 100)}
                        </p>
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Other Assumptions */}
                <Card>
                  <div className="p-4">
                    <Typography variant="h3" className="text-lg font-semibold mb-4">
                      Other Assumptions
                    </Typography>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Tax Rate
                        </label>
                        <Input
                          type="number"
                          step="0.01"
                          value={inputs.taxRate}
                          onChange={(e) => handleInputChange('taxRate', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Cost of Debt
                        </label>
                        <Input
                          type="number"
                          step="0.01"
                          value={inputs.costOfDebt}
                          onChange={(e) => handleInputChange('costOfDebt', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Projection Years
                        </label>
                        <Input
                          type="number"
                          value={inputs.projectionYears}
                          onChange={(e) => handleInputChange('projectionYears', Number(e.target.value))}
                          className="w-full"
                        />
                      </div>
                    </div>
                  </div>
                </Card>
              </Grid>
            </div>
          )}

          {/* Results Tab */}
          {activeTab === 'results' && (
            <div className="space-y-6">
              {/* Key Results */}
              <Grid cols={4} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-blue-600">
                      {formatCurrency(dcfResults.fairValue)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Fair Value
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography 
                      variant="h3" 
                      className={`text-2xl font-bold ${
                        dcfResults.upside >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {formatCurrency(dcfResults.upside)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Upside/Downside
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography 
                      variant="h3" 
                      className={`text-2xl font-bold ${
                        dcfResults.upsidePercent >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {formatPercent(dcfResults.upsidePercent)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Upside %
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-2xl font-bold text-purple-600">
                      {formatCurrency(dcfResults.terminalValue)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Terminal Value
                    </Typography>
                  </div>
                </Card>
              </Grid>

              {/* Projections Table */}
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Financial Projections
                  </Typography>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Year</th>
                          <th className="text-right py-2">Revenue</th>
                          <th className="text-right py-2">EBITDA</th>
                          <th className="text-right py-2">Free Cash Flow</th>
                          <th className="text-right py-2">Present Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dcfResults.projections.map((projection) => (
                          <tr key={projection.year} className="border-b">
                            <td className="py-2">{projection.year}</td>
                            <td className="text-right py-2">
                              {formatCurrency(projection.revenue)}
                            </td>
                            <td className="text-right py-2">
                              {formatCurrency(projection.ebitda)}
                            </td>
                            <td className="text-right py-2">
                              {formatCurrency(projection.freeCashFlow)}
                            </td>
                            <td className="text-right py-2">
                              {formatCurrency(projection.presentValue)}
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

          {/* Sensitivity Analysis Tab */}
          {activeTab === 'sensitivity' && (
            <div className="space-y-6">
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Sensitivity Analysis
                  </Typography>
                  <div className="text-sm text-gray-600 mb-4">
                    Fair value sensitivity to changes in WACC and growth rate
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Growth Rate</th>
                          {dcfResults.sensitivityAnalysis.waccRange.results
                            .filter((_, i) => i % 5 === 0) // Show every 5th result
                            .map((result, i) => (
                              <th key={i} className="text-right py-2">
                                {formatPercent(result.wacc * 100)}
                              </th>
                            ))}
                        </tr>
                      </thead>
                      <tbody>
                        {Array.from(new Set(dcfResults.sensitivityAnalysis.results.map(r => r.growth)))
                          .filter((_, i) => i % 3 === 0) // Show every 3rd growth rate
                          .map((growth, i) => (
                            <tr key={i} className="border-b">
                              <td className="py-2">{formatPercent(growth * 100)}</td>
                              {dcfResults.sensitivityAnalysis.results
                                .filter(r => r.growth === growth)
                                .filter((_, i) => i % 5 === 0)
                                .map((result, j) => (
                                  <td key={j} className="text-right py-2">
                                    {formatCurrency(result.fairValue)}
                                  </td>
                                ))}
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Monte Carlo Tab */}
          {activeTab === 'monte-carlo' && (
            <div className="space-y-6">
              <Grid cols={3} gap={4}>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-blue-600">
                      {formatCurrency(dcfResults.monteCarloResults.mean)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Mean Fair Value
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-green-600">
                      {formatPercent(dcfResults.monteCarloResults.probabilityOfLoss * 100)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Probability of Loss
                    </Typography>
                  </div>
                </Card>
                <Card>
                  <div className="p-4 text-center">
                    <Typography variant="h3" className="text-xl font-bold text-purple-600">
                      {formatCurrency(dcfResults.monteCarloResults.percentile95)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      95th Percentile
                    </Typography>
                  </div>
                </Card>
              </Grid>

              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Monte Carlo Statistics
                  </Typography>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="flex justify-between py-1">
                        <span>5th Percentile:</span>
                        <span>{formatCurrency(dcfResults.monteCarloResults.percentile5)}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>25th Percentile:</span>
                        <span>{formatCurrency(dcfResults.monteCarloResults.percentile25)}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>Median:</span>
                        <span>{formatCurrency(dcfResults.monteCarloResults.median)}</span>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between py-1">
                        <span>75th Percentile:</span>
                        <span>{formatCurrency(dcfResults.monteCarloResults.percentile75)}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>90th Percentile:</span>
                        <span>{formatCurrency(dcfResults.monteCarloResults.percentile90)}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>95th Percentile:</span>
                        <span>{formatCurrency(dcfResults.monteCarloResults.percentile95)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Scenarios Tab */}
          {activeTab === 'scenarios' && (
            <div className="space-y-6">
              <Card>
                <div className="p-4">
                  <Typography variant="h3" className="text-lg font-semibold mb-4">
                    Scenario Analysis
                  </Typography>
                  <div className="space-y-4">
                    {scenarioResults.map((scenario, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <Typography variant="h4" className="font-semibold">
                            {scenario.name}
                          </Typography>
                          <Typography variant="h4" className="font-bold text-blue-600">
                            {formatCurrency(scenario.fairValue)}
                          </Typography>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <div className="flex justify-between py-1">
                              <span>Revenue Growth:</span>
                              <span>{formatPercent(scenario.revenueGrowth * 100)}</span>
                            </div>
                            <div className="flex justify-between py-1">
                              <span>EBITDA Margin:</span>
                              <span>{formatPercent(scenario.ebitdaMargin * 100)}</span>
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between py-1">
                              <span>Terminal Growth:</span>
                              <span>{formatPercent(scenario.terminalGrowth * 100)}</span>
                            </div>
                            <div className="flex justify-between py-1">
                              <span>WACC:</span>
                              <span>{formatPercent(scenario.wacc * 100)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
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

export default DCFCalculator
