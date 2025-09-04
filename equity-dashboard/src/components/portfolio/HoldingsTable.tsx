/**
 * Holdings Table Component
 * 
 * Sortable and filterable holdings list with position management functionality
 */

import React, { useState, useMemo } from 'react'
import { 
  MagnifyingGlassIcon,
  FunnelIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  CheckIcon
} from '@heroicons/react/24/outline'
import { Card, Button, Input, Badge, Spinner } from '../ui'
import { usePortfolioStore } from '../../store/portfolio'
import { HoldingsTableFilters } from '../../types/portfolio'
import { formatCurrency, formatPercent, getChangeColor } from '../../utils'

export const HoldingsTable: React.FC = () => {
  const {
    selectedPortfolio,
    holdingsFilters,
    selectedHoldings,
    isLoading,
    setHoldingsFilters,
    setSelectedHoldings,
    toggleHoldingSelection,
    selectAllHoldings,
    clearHoldingSelection,
    setShowAddPositionModal,
    setShowEditPositionModal,
    setEditingPosition,
    removeHolding
  } = usePortfolioStore()

  const [showFilters, setShowFilters] = useState(false)

  // Filter and sort holdings
  const filteredHoldings = useMemo(() => {
    if (!selectedPortfolio) return []

    let filtered = selectedPortfolio.holdings.filter(holding => {
      // Search filter
      if (holdingsFilters.search) {
        const searchLower = holdingsFilters.search.toLowerCase()
        if (!holding.symbol.toLowerCase().includes(searchLower)) {
          return false
        }
      }

      // Weight filters
      if (holding.weight < holdingsFilters.minWeight || holding.weight > holdingsFilters.maxWeight) {
        return false
      }

      // Return filters
      if (holding.unrealizedGainPercent < holdingsFilters.minReturn || 
          holding.unrealizedGainPercent > holdingsFilters.maxReturn) {
        return false
      }

      return true
    })

    // Sort holdings
    filtered.sort((a, b) => {
      let aValue: any, bValue: any

      switch (holdingsFilters.sortBy) {
        case 'symbol':
          aValue = a.symbol
          bValue = b.symbol
          break
        case 'value':
          aValue = a.marketValue
          bValue = b.marketValue
          break
        case 'weight':
          aValue = a.weight
          bValue = b.weight
          break
        case 'return':
          aValue = a.unrealizedGain
          bValue = b.unrealizedGain
          break
        case 'returnPercent':
          aValue = a.unrealizedGainPercent
          bValue = b.unrealizedGainPercent
          break
        default:
          aValue = a.marketValue
          bValue = b.marketValue
      }

      if (holdingsFilters.sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

    return filtered
  }, [selectedPortfolio, holdingsFilters])

  const handleSort = (column: HoldingsTableFilters['sortBy']) => {
    const newOrder = holdingsFilters.sortBy === column && holdingsFilters.sortOrder === 'desc' 
      ? 'asc' 
      : 'desc'
    
    setHoldingsFilters({
      sortBy: column,
      sortOrder: newOrder
    })
  }

  const handleEditPosition = (holding: any) => {
    setEditingPosition(holding)
    setShowEditPositionModal(true)
  }

  const handleDeletePosition = async (holdingId: string) => {
    if (window.confirm('Are you sure you want to remove this position?')) {
      await removeHolding(holdingId)
    }
  }

  const handleBulkDelete = async () => {
    if (window.confirm(`Are you sure you want to remove ${selectedHoldings.length} positions?`)) {
      for (const holdingId of selectedHoldings) {
        await removeHolding(holdingId)
      }
      clearHoldingSelection()
    }
  }

  const SortButton: React.FC<{
    column: HoldingsTableFilters['sortBy']
    children: React.ReactNode
  }> = ({ column, children }) => (
    <button
      onClick={() => handleSort(column)}
      className="flex items-center space-x-1 hover:text-neutral-900"
    >
      <span>{children}</span>
      {holdingsFilters.sortBy === column && (
        holdingsFilters.sortOrder === 'asc' ? (
          <ChevronUpIcon className="w-4 h-4" />
        ) : (
          <ChevronDownIcon className="w-4 h-4" />
        )
      )}
    </button>
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!selectedPortfolio) {
    return (
      <Card className="p-6">
        <div className="text-center text-neutral-600">
          <p>No portfolio selected</p>
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-neutral-900">Holdings</h2>
          <p className="text-sm text-neutral-600">
            {filteredHoldings.length} of {selectedPortfolio.holdings.length} positions
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            <FunnelIcon className="w-4 h-4 mr-2" />
            Filters
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => setShowAddPositionModal(true)}
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            Add Position
          </Button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="mb-6 p-4 bg-neutral-50 rounded-lg space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Search
              </label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
                <Input
                  type="text"
                  placeholder="Search symbols..."
                  value={holdingsFilters.search}
                  onChange={(e) => setHoldingsFilters({ search: e.target.value })}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Min Weight (%)
              </label>
              <Input
                type="number"
                min="0"
                max="100"
                value={holdingsFilters.minWeight}
                onChange={(e) => setHoldingsFilters({ minWeight: Number(e.target.value) })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Max Weight (%)
              </label>
              <Input
                type="number"
                min="0"
                max="100"
                value={holdingsFilters.maxWeight}
                onChange={(e) => setHoldingsFilters({ maxWeight: Number(e.target.value) })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Min Return (%)
              </label>
              <Input
                type="number"
                value={holdingsFilters.minReturn}
                onChange={(e) => setHoldingsFilters({ minReturn: Number(e.target.value) })}
              />
            </div>
          </div>
        </div>
      )}

      {/* Bulk Actions */}
      {selectedHoldings.length > 0 && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm text-blue-700">
              {selectedHoldings.length} position{selectedHoldings.length !== 1 ? 's' : ''} selected
            </span>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={clearHoldingSelection}
              >
                Clear Selection
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={handleBulkDelete}
              >
                <TrashIcon className="w-4 h-4 mr-2" />
                Delete Selected
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-neutral-200">
              <th className="text-left py-3 px-4 font-medium text-neutral-600 w-12">
                <input
                  type="checkbox"
                  checked={selectedHoldings.length === filteredHoldings.length && filteredHoldings.length > 0}
                  onChange={(e) => {
                    if (e.target.checked) {
                      selectAllHoldings()
                    } else {
                      clearHoldingSelection()
                    }
                  }}
                  className="rounded border-neutral-300"
                />
              </th>
              <th className="text-left py-3 px-4 font-medium text-neutral-600">
                <SortButton column="symbol">Symbol</SortButton>
              </th>
              <th className="text-left py-3 px-4 font-medium text-neutral-600">Name</th>
              <th className="text-right py-3 px-4 font-medium text-neutral-600">Shares</th>
              <th className="text-right py-3 px-4 font-medium text-neutral-600">Avg Price</th>
              <th className="text-right py-3 px-4 font-medium text-neutral-600">Current Price</th>
              <th className="text-right py-3 px-4 font-medium text-neutral-600">
                <SortButton column="value">Market Value</SortButton>
              </th>
              <th className="text-right py-3 px-4 font-medium text-neutral-600">
                <SortButton column="weight">Weight</SortButton>
              </th>
              <th className="text-right py-3 px-4 font-medium text-neutral-600">
                <SortButton column="return">Unrealized P&L</SortButton>
              </th>
              <th className="text-right py-3 px-4 font-medium text-neutral-600">
                <SortButton column="returnPercent">Return %</SortButton>
              </th>
              <th className="text-center py-3 px-4 font-medium text-neutral-600">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredHoldings.map((holding) => (
              <tr 
                key={holding.id} 
                className="border-b border-neutral-100 hover:bg-neutral-50"
              >
                <td className="py-3 px-4">
                  <input
                    type="checkbox"
                    checked={selectedHoldings.includes(holding.id)}
                    onChange={() => toggleHoldingSelection(holding.id)}
                    className="rounded border-neutral-300"
                  />
                </td>
                <td className="py-3 px-4 font-medium text-neutral-900">
                  {holding.symbol}
                </td>
                <td className="py-3 px-4 text-neutral-600">
                  {holding.symbol} {/* In real app, this would be the company name */}
                </td>
                <td className="py-3 px-4 text-right">
                  {holding.shares.toLocaleString()}
                </td>
                <td className="py-3 px-4 text-right">
                  {formatCurrency(holding.averagePrice)}
                </td>
                <td className="py-3 px-4 text-right">
                  {formatCurrency(holding.currentPrice)}
                </td>
                <td className="py-3 px-4 text-right font-medium">
                  {formatCurrency(holding.marketValue)}
                </td>
                <td className="py-3 px-4 text-right">
                  {formatPercent(holding.weight)}
                </td>
                <td className="py-3 px-4 text-right">
                  <span className={getChangeColor(holding.unrealizedGain)}>
                    {holding.unrealizedGain >= 0 ? '+' : ''}{formatCurrency(holding.unrealizedGain)}
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <Badge 
                    variant={holding.unrealizedGainPercent >= 0 ? 'success' : 'danger'}
                  >
                    {holding.unrealizedGainPercent >= 0 ? '+' : ''}{formatPercent(holding.unrealizedGainPercent)}
                  </Badge>
                </td>
                <td className="py-3 px-4 text-center">
                  <div className="flex items-center justify-center space-x-2">
                    <button
                      onClick={() => handleEditPosition(holding)}
                      className="p-1 text-neutral-400 hover:text-blue-600"
                      title="Edit position"
                    >
                      <PencilIcon className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeletePosition(holding.id)}
                      className="p-1 text-neutral-400 hover:text-red-600"
                      title="Delete position"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredHoldings.length === 0 && (
        <div className="text-center py-8 text-neutral-600">
          <p>No holdings match your current filters</p>
        </div>
      )}
    </Card>
  )
}
