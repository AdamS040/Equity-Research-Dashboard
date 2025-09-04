/**
 * Add Position Modal Component
 * 
 * Modal for adding new positions with stock search, validation, and real-time preview
 */

import React, { useState, useEffect, useMemo } from 'react'
import { 
  XMarkIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { Modal, Button, Input, Spinner } from '../ui'
import { usePortfolioStore } from '../../store/portfolio'
import { PositionFormData, StockSearchResult } from '../../types/portfolio'
import { formatCurrency, formatPercent } from '../../utils'

interface AddPositionModalProps {
  isOpen: boolean
  onClose: () => void
}

export const AddPositionModal: React.FC<AddPositionModalProps> = ({ isOpen, onClose }) => {
  const { selectedPortfolio, addHolding } = usePortfolioStore()
  
  const [formData, setFormData] = useState<PositionFormData>({
    symbol: '',
    shares: 0,
    purchasePrice: 0,
    purchaseDate: new Date().toISOString().split('T')[0],
    commission: 0,
    fees: 0
  })

  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<StockSearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showSearchResults, setShowSearchResults] = useState(false)
  const [selectedStock, setSelectedStock] = useState<StockSearchResult | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Mock stock search - in real app, this would be an API call
  const mockStocks: StockSearchResult[] = [
    { symbol: 'AAPL', name: 'Apple Inc.', exchange: 'NASDAQ', price: 175.43, change: 2.15, changePercent: 1.24, marketCap: 2800000000000, sector: 'Technology' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', exchange: 'NASDAQ', price: 142.56, change: -1.23, changePercent: -0.86, marketCap: 1800000000000, sector: 'Technology' },
    { symbol: 'MSFT', name: 'Microsoft Corporation', exchange: 'NASDAQ', price: 378.85, change: 4.32, changePercent: 1.15, marketCap: 2800000000000, sector: 'Technology' },
    { symbol: 'TSLA', name: 'Tesla Inc.', exchange: 'NASDAQ', price: 248.50, change: -5.20, changePercent: -2.05, marketCap: 800000000000, sector: 'Automotive' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', exchange: 'NASDAQ', price: 155.20, change: 1.80, changePercent: 1.17, marketCap: 1600000000000, sector: 'Consumer Discretionary' },
    { symbol: 'META', name: 'Meta Platforms Inc.', exchange: 'NASDAQ', price: 485.30, change: 8.45, changePercent: 1.77, marketCap: 1200000000000, sector: 'Technology' },
    { symbol: 'NVDA', name: 'NVIDIA Corporation', exchange: 'NASDAQ', price: 875.20, change: 15.30, changePercent: 1.78, marketCap: 2200000000000, sector: 'Technology' },
    { symbol: 'JNJ', name: 'Johnson & Johnson', exchange: 'NYSE', price: 156.80, change: 0.45, changePercent: 0.29, marketCap: 400000000000, sector: 'Healthcare' },
    { symbol: 'PG', name: 'Procter & Gamble Co.', exchange: 'NYSE', price: 150.25, change: -0.80, changePercent: -0.53, marketCap: 350000000000, sector: 'Consumer Staples' },
    { symbol: 'KO', name: 'Coca-Cola Company', exchange: 'NYSE', price: 60.15, change: 0.25, changePercent: 0.42, marketCap: 260000000000, sector: 'Consumer Staples' }
  ]

  // Search stocks
  useEffect(() => {
    if (searchQuery.length < 2) {
      setSearchResults([])
      setShowSearchResults(false)
      return
    }

    setIsSearching(true)
    const timeoutId = setTimeout(() => {
      const filtered = mockStocks.filter(stock =>
        stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
        stock.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setSearchResults(filtered)
      setShowSearchResults(true)
      setIsSearching(false)
    }, 300)

    return () => clearTimeout(timeoutId)
  }, [searchQuery])

  // Calculate position metrics
  const positionMetrics = useMemo(() => {
    const totalCost = (formData.shares * formData.purchasePrice) + formData.commission + formData.fees
    const currentValue = selectedStock ? formData.shares * selectedStock.price : 0
    const unrealizedGain = currentValue - totalCost
    const unrealizedGainPercent = totalCost > 0 ? (unrealizedGain / totalCost) * 100 : 0
    const weight = selectedPortfolio ? (currentValue / (selectedPortfolio.totalValue + currentValue)) * 100 : 0

    return {
      totalCost,
      currentValue,
      unrealizedGain,
      unrealizedGainPercent,
      weight
    }
  }, [formData, selectedStock, selectedPortfolio])

  // Form validation
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.symbol.trim()) {
      newErrors.symbol = 'Symbol is required'
    }

    if (formData.shares <= 0) {
      newErrors.shares = 'Shares must be greater than 0'
    }

    if (formData.purchasePrice <= 0) {
      newErrors.purchasePrice = 'Purchase price must be greater than 0'
    }

    if (!formData.purchaseDate) {
      newErrors.purchaseDate = 'Purchase date is required'
    }

    if (formData.commission < 0) {
      newErrors.commission = 'Commission cannot be negative'
    }

    if (formData.fees < 0) {
      newErrors.fees = 'Fees cannot be negative'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleStockSelect = (stock: StockSearchResult) => {
    setSelectedStock(stock)
    setFormData(prev => ({ ...prev, symbol: stock.symbol }))
    setSearchQuery(stock.symbol)
    setShowSearchResults(false)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm() || !selectedStock || !selectedPortfolio) {
      return
    }

    setIsSubmitting(true)
    
    try {
      const newHolding = {
        id: `holding_${Date.now()}`,
        symbol: formData.symbol,
        shares: formData.shares,
        averagePrice: formData.purchasePrice,
        currentPrice: selectedStock.price,
        marketValue: positionMetrics.currentValue,
        costBasis: positionMetrics.totalCost,
        unrealizedGain: positionMetrics.unrealizedGain,
        unrealizedGainPercent: positionMetrics.unrealizedGainPercent,
        weight: positionMetrics.weight,
        addedAt: new Date().toISOString(),
        lastUpdated: new Date().toISOString()
      }

      await addHolding(newHolding)
      handleClose()
    } catch (error) {
      console.error('Error adding position:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClose = () => {
    setFormData({
      symbol: '',
      shares: 0,
      purchasePrice: 0,
      purchaseDate: new Date().toISOString().split('T')[0],
      commission: 0,
      fees: 0
    })
    setSearchQuery('')
    setSelectedStock(null)
    setSearchResults([])
    setShowSearchResults(false)
    setErrors({})
    onClose()
  }

  if (!isOpen) return null

  return (
    <Modal isOpen={isOpen} onClose={handleClose} size="lg">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-neutral-900">Add New Position</h2>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-neutral-100 rounded-lg"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Stock Search */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Stock Symbol *
            </label>
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
              <Input
                type="text"
                placeholder="Search for a stock symbol..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setShowSearchResults(searchQuery.length >= 2)}
                className="pl-10"
                error={errors.symbol}
              />
              {isSearching && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <Spinner size="sm" />
                </div>
              )}
            </div>

            {/* Search Results */}
            {showSearchResults && searchResults.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-neutral-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                {searchResults.map((stock) => (
                  <button
                    key={stock.symbol}
                    type="button"
                    onClick={() => handleStockSelect(stock)}
                    className="w-full px-4 py-3 text-left hover:bg-neutral-50 border-b border-neutral-100 last:border-b-0"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-neutral-900">{stock.symbol}</div>
                        <div className="text-sm text-neutral-600">{stock.name}</div>
                        <div className="text-xs text-neutral-500">{stock.exchange} • {stock.sector}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium text-neutral-900">{formatCurrency(stock.price)}</div>
                        <div className={`text-sm ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {stock.change >= 0 ? '+' : ''}{formatPercent(stock.changePercent / 100)}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {selectedStock && (
              <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <CheckIcon className="w-4 h-4 text-green-600" />
                  <span className="text-sm text-green-800">
                    Selected: {selectedStock.name} ({selectedStock.symbol})
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Position Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Number of Shares *
              </label>
              <Input
                type="number"
                min="0"
                step="0.01"
                value={formData.shares}
                onChange={(e) => setFormData(prev => ({ ...prev, shares: Number(e.target.value) }))}
                error={errors.shares}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Purchase Price *
              </label>
              <Input
                type="number"
                min="0"
                step="0.01"
                value={formData.purchasePrice}
                onChange={(e) => setFormData(prev => ({ ...prev, purchasePrice: Number(e.target.value) }))}
                error={errors.purchasePrice}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Purchase Date *
              </label>
              <Input
                type="date"
                value={formData.purchaseDate}
                onChange={(e) => setFormData(prev => ({ ...prev, purchaseDate: e.target.value }))}
                error={errors.purchaseDate}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Commission
              </label>
              <Input
                type="number"
                min="0"
                step="0.01"
                value={formData.commission}
                onChange={(e) => setFormData(prev => ({ ...prev, commission: Number(e.target.value) }))}
                error={errors.commission}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Fees
              </label>
              <Input
                type="number"
                min="0"
                step="0.01"
                value={formData.fees}
                onChange={(e) => setFormData(prev => ({ ...prev, fees: Number(e.target.value) }))}
                error={errors.fees}
              />
            </div>
          </div>

          {/* Position Preview */}
          {selectedStock && formData.shares > 0 && formData.purchasePrice > 0 && (
            <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-lg">
              <h3 className="text-sm font-medium text-neutral-900 mb-3">Position Preview</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-neutral-600">Total Cost</div>
                  <div className="font-medium">{formatCurrency(positionMetrics.totalCost)}</div>
                </div>
                <div>
                  <div className="text-neutral-600">Current Value</div>
                  <div className="font-medium">{formatCurrency(positionMetrics.currentValue)}</div>
                </div>
                <div>
                  <div className="text-neutral-600">Unrealized P&L</div>
                  <div className={`font-medium ${positionMetrics.unrealizedGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {positionMetrics.unrealizedGain >= 0 ? '+' : ''}{formatCurrency(positionMetrics.unrealizedGain)}
                  </div>
                </div>
                <div>
                  <div className="text-neutral-600">Return %</div>
                  <div className={`font-medium ${positionMetrics.unrealizedGainPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {positionMetrics.unrealizedGainPercent >= 0 ? '+' : ''}{formatPercent(positionMetrics.unrealizedGainPercent / 100)}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Form Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-neutral-200">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting || !selectedStock || !validateForm()}
            >
              {isSubmitting ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Adding Position...
                </>
              ) : (
                'Add Position'
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  )
}
