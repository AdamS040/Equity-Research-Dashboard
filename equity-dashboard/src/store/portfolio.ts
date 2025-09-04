/**
 * Portfolio Store
 * 
 * Zustand store for portfolio state management
 */

import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import {
  Portfolio,
  PortfolioHolding,
  PortfolioMetrics,
  AssetAllocation,
  SectorAllocation,
  PerformanceData,
  RiskMetrics,
  CorrelationMatrix,
  StressTestScenario,
  OptimizationResult,
  EfficientFrontierPoint,
  RebalancingRecommendation,
  HoldingsTableFilters,
  PerformanceChartFilters,
  RiskAnalysisFilters,
  OptimizationFilters,
} from '../types/portfolio'

interface PortfolioState {
  // Portfolio Data
  portfolios: Portfolio[]
  selectedPortfolio: Portfolio | null
  portfolioMetrics: PortfolioMetrics | null
  assetAllocation: AssetAllocation[]
  sectorAllocation: SectorAllocation[]
  performanceData: PerformanceData[]
  riskMetrics: RiskMetrics | null
  correlationMatrix: CorrelationMatrix | null
  stressTestScenarios: StressTestScenario[]
  optimizationResults: OptimizationResult[]
  efficientFrontier: EfficientFrontierPoint[]
  rebalancingRecommendations: RebalancingRecommendation[]
  
  // UI State
  isLoading: boolean
  error: string | null
  activeTab: 'overview' | 'holdings' | 'performance' | 'risk' | 'optimization'
  
  // Filters
  holdingsFilters: HoldingsTableFilters
  performanceFilters: PerformanceChartFilters
  riskFilters: RiskAnalysisFilters
  optimizationFilters: OptimizationFilters
  
  // Modal States
  showAddPositionModal: boolean
  showEditPositionModal: boolean
  showOptimizationModal: boolean
  showRebalancingModal: boolean
  
  // Selected Items
  selectedHoldings: string[]
  editingPosition: PortfolioHolding | null
  
  // Actions
  setPortfolios: (portfolios: Portfolio[]) => void
  setSelectedPortfolio: (portfolio: Portfolio | null) => void
  setPortfolioMetrics: (metrics: PortfolioMetrics | null) => void
  setAssetAllocation: (allocation: AssetAllocation[]) => void
  setSectorAllocation: (allocation: SectorAllocation[]) => void
  setPerformanceData: (data: PerformanceData[]) => void
  setRiskMetrics: (metrics: RiskMetrics | null) => void
  setCorrelationMatrix: (matrix: CorrelationMatrix | null) => void
  setStressTestScenarios: (scenarios: StressTestScenario[]) => void
  setOptimizationResults: (results: OptimizationResult[]) => void
  setEfficientFrontier: (frontier: EfficientFrontierPoint[]) => void
  setRebalancingRecommendations: (recommendations: RebalancingRecommendation[]) => void
  
  // UI Actions
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setActiveTab: (tab: 'overview' | 'holdings' | 'performance' | 'risk' | 'optimization') => void
  
  // Filter Actions
  setHoldingsFilters: (filters: Partial<HoldingsTableFilters>) => void
  setPerformanceFilters: (filters: Partial<PerformanceChartFilters>) => void
  setRiskFilters: (filters: Partial<RiskAnalysisFilters>) => void
  setOptimizationFilters: (filters: Partial<OptimizationFilters>) => void
  resetFilters: () => void
  
  // Modal Actions
  setShowAddPositionModal: (show: boolean) => void
  setShowEditPositionModal: (show: boolean) => void
  setShowOptimizationModal: (show: boolean) => void
  setShowRebalancingModal: (show: boolean) => void
  
  // Selection Actions
  setSelectedHoldings: (holdings: string[]) => void
  toggleHoldingSelection: (holdingId: string) => void
  selectAllHoldings: () => void
  clearHoldingSelection: () => void
  setEditingPosition: (position: PortfolioHolding | null) => void
  
  // Portfolio Actions
  addPortfolio: (portfolio: Portfolio) => void
  updatePortfolio: (portfolio: Portfolio) => void
  removePortfolio: (portfolioId: string) => void
  addHolding: (holding: PortfolioHolding) => void
  updateHolding: (holding: PortfolioHolding) => void
  removeHolding: (holdingId: string) => void
  bulkUpdateHoldings: (holdings: PortfolioHolding[]) => void
  
  // Utility Actions
  refreshPortfolioData: () => void
  clearError: () => void
  resetState: () => void
}

const defaultHoldingsFilters: HoldingsTableFilters = {
  search: '',
  sector: '',
  minWeight: 0,
  maxWeight: 100,
  minReturn: -100,
  maxReturn: 100,
  sortBy: 'value',
  sortOrder: 'desc',
}

const defaultPerformanceFilters: PerformanceChartFilters = {
  period: '1y',
  benchmark: 'SPY',
  showDrawdown: true,
  showRollingReturns: false,
}

const defaultRiskFilters: RiskAnalysisFilters = {
  confidenceLevel: 95,
  timeHorizon: 30,
  stressTestScenarios: [],
  showCorrelationMatrix: true,
}

const defaultOptimizationFilters: OptimizationFilters = {
  method: 'max_sharpe',
  constraints: {
    maxWeight: 0.1,
    minWeight: 0,
    sectorLimits: {},
    excludeSymbols: [],
  },
}

export const usePortfolioStore = create<PortfolioState>()(
  devtools(
    (set, get) => ({
      // Initial state
      portfolios: [],
      selectedPortfolio: null,
      portfolioMetrics: null,
      assetAllocation: [],
      sectorAllocation: [],
      performanceData: [],
      riskMetrics: null,
      correlationMatrix: null,
      stressTestScenarios: [],
      optimizationResults: [],
      efficientFrontier: [],
      rebalancingRecommendations: [],
      
      // UI state
      isLoading: false,
      error: null,
      activeTab: 'overview',
      
      // Filters
      holdingsFilters: defaultHoldingsFilters,
      performanceFilters: defaultPerformanceFilters,
      riskFilters: defaultRiskFilters,
      optimizationFilters: defaultOptimizationFilters,
      
      // Modal states
      showAddPositionModal: false,
      showEditPositionModal: false,
      showOptimizationModal: false,
      showRebalancingModal: false,
      
      // Selected items
      selectedHoldings: [],
      editingPosition: null,
      
      // Data setters
      setPortfolios: (portfolios) => set({ portfolios }),
      setSelectedPortfolio: (portfolio) => set({ selectedPortfolio: portfolio }),
      setPortfolioMetrics: (metrics) => set({ portfolioMetrics: metrics }),
      setAssetAllocation: (allocation) => set({ assetAllocation: allocation }),
      setSectorAllocation: (allocation) => set({ sectorAllocation: allocation }),
      setPerformanceData: (data) => set({ performanceData: data }),
      setRiskMetrics: (metrics) => set({ riskMetrics: metrics }),
      setCorrelationMatrix: (matrix) => set({ correlationMatrix: matrix }),
      setStressTestScenarios: (scenarios) => set({ stressTestScenarios: scenarios }),
      setOptimizationResults: (results) => set({ optimizationResults: results }),
      setEfficientFrontier: (frontier) => set({ efficientFrontier: frontier }),
      setRebalancingRecommendations: (recommendations) => set({ rebalancingRecommendations: recommendations }),
      
      // UI actions
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
      setActiveTab: (tab) => set({ activeTab: tab }),
      
      // Filter actions
      setHoldingsFilters: (filters) => set((state) => ({
        holdingsFilters: { ...state.holdingsFilters, ...filters }
      })),
      setPerformanceFilters: (filters) => set((state) => ({
        performanceFilters: { ...state.performanceFilters, ...filters }
      })),
      setRiskFilters: (filters) => set((state) => ({
        riskFilters: { ...state.riskFilters, ...filters }
      })),
      setOptimizationFilters: (filters) => set((state) => ({
        optimizationFilters: { ...state.optimizationFilters, ...filters }
      })),
      resetFilters: () => set({
        holdingsFilters: defaultHoldingsFilters,
        performanceFilters: defaultPerformanceFilters,
        riskFilters: defaultRiskFilters,
        optimizationFilters: defaultOptimizationFilters,
      }),
      
      // Modal actions
      setShowAddPositionModal: (show) => set({ showAddPositionModal: show }),
      setShowEditPositionModal: (show) => set({ showEditPositionModal: show }),
      setShowOptimizationModal: (show) => set({ showOptimizationModal: show }),
      setShowRebalancingModal: (show) => set({ showRebalancingModal: show }),
      
      // Selection actions
      setSelectedHoldings: (holdings) => set({ selectedHoldings: holdings }),
      toggleHoldingSelection: (holdingId) => set((state) => ({
        selectedHoldings: state.selectedHoldings.includes(holdingId)
          ? state.selectedHoldings.filter(id => id !== holdingId)
          : [...state.selectedHoldings, holdingId]
      })),
      selectAllHoldings: () => set((state) => ({
        selectedHoldings: state.selectedPortfolio?.holdings.map(h => h.id) || []
      })),
      clearHoldingSelection: () => set({ selectedHoldings: [] }),
      setEditingPosition: (position) => set({ editingPosition: position }),
      
      // Portfolio actions
      addPortfolio: (portfolio) => set((state) => ({
        portfolios: [...state.portfolios, portfolio]
      })),
      updatePortfolio: (portfolio) => set((state) => ({
        portfolios: state.portfolios.map(p => p.id === portfolio.id ? portfolio : p),
        selectedPortfolio: state.selectedPortfolio?.id === portfolio.id ? portfolio : state.selectedPortfolio
      })),
      removePortfolio: (portfolioId) => set((state) => ({
        portfolios: state.portfolios.filter(p => p.id !== portfolioId),
        selectedPortfolio: state.selectedPortfolio?.id === portfolioId ? null : state.selectedPortfolio
      })),
      addHolding: (holding) => set((state) => {
        if (!state.selectedPortfolio) return state
        const updatedPortfolio = {
          ...state.selectedPortfolio,
          holdings: [...state.selectedPortfolio.holdings, holding]
        }
        return {
          selectedPortfolio: updatedPortfolio,
          portfolios: state.portfolios.map(p => p.id === updatedPortfolio.id ? updatedPortfolio : p)
        }
      }),
      updateHolding: (holding) => set((state) => {
        if (!state.selectedPortfolio) return state
        const updatedPortfolio = {
          ...state.selectedPortfolio,
          holdings: state.selectedPortfolio.holdings.map(h => h.id === holding.id ? holding : h)
        }
        return {
          selectedPortfolio: updatedPortfolio,
          portfolios: state.portfolios.map(p => p.id === updatedPortfolio.id ? updatedPortfolio : p)
        }
      }),
      removeHolding: (holdingId) => set((state) => {
        if (!state.selectedPortfolio) return state
        const updatedPortfolio = {
          ...state.selectedPortfolio,
          holdings: state.selectedPortfolio.holdings.filter(h => h.id !== holdingId)
        }
        return {
          selectedPortfolio: updatedPortfolio,
          portfolios: state.portfolios.map(p => p.id === updatedPortfolio.id ? updatedPortfolio : p),
          selectedHoldings: state.selectedHoldings.filter(id => id !== holdingId)
        }
      }),
      bulkUpdateHoldings: (holdings) => set((state) => {
        if (!state.selectedPortfolio) return state
        const updatedPortfolio = {
          ...state.selectedPortfolio,
          holdings: holdings
        }
        return {
          selectedPortfolio: updatedPortfolio,
          portfolios: state.portfolios.map(p => p.id === updatedPortfolio.id ? updatedPortfolio : p)
        }
      }),
      
      // Utility actions
      refreshPortfolioData: () => {
        // This would trigger a refresh of all portfolio data
        set({ isLoading: true })
        // Implementation would depend on API calls
      },
      clearError: () => set({ error: null }),
      resetState: () => set({
        portfolios: [],
        selectedPortfolio: null,
        portfolioMetrics: null,
        assetAllocation: [],
        sectorAllocation: [],
        performanceData: [],
        riskMetrics: null,
        correlationMatrix: null,
        stressTestScenarios: [],
        optimizationResults: [],
        efficientFrontier: [],
        rebalancingRecommendations: [],
        isLoading: false,
        error: null,
        activeTab: 'overview',
        holdingsFilters: defaultHoldingsFilters,
        performanceFilters: defaultPerformanceFilters,
        riskFilters: defaultRiskFilters,
        optimizationFilters: defaultOptimizationFilters,
        showAddPositionModal: false,
        showEditPositionModal: false,
        showOptimizationModal: false,
        showRebalancingModal: false,
        selectedHoldings: [],
        editingPosition: null,
      }),
    }),
    {
      name: 'portfolio-store',
    }
  )
)
