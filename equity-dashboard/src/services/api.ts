import { Stock, StockQuote, HistoricalData, FinancialMetrics, DCFAnalysis, ComparableAnalysis, RiskMetrics, MonteCarloSimulation } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })
  
  if (!response.ok) {
    throw new ApiError(response.status, `API Error: ${response.statusText}`)
  }
  
  return response.json()
}

export const stockApi = {
  // Get stock information
  getStock: (symbol: string): Promise<Stock> =>
    fetchApi<Stock>(`/stocks/${symbol}`),
  
  // Get stock quote
  getQuote: (symbol: string): Promise<StockQuote> =>
    fetchApi<StockQuote>(`/stocks/${symbol}/quote`),
  
  // Get historical data
  getHistoricalData: (symbol: string, period: string = '1y'): Promise<HistoricalData[]> =>
    fetchApi<HistoricalData[]>(`/stocks/${symbol}/history?period=${period}`),
  
  // Get financial metrics
  getFinancialMetrics: (symbol: string): Promise<FinancialMetrics> =>
    fetchApi<FinancialMetrics>(`/stocks/${symbol}/metrics`),
  
  // Search stocks
  searchStocks: (query: string): Promise<Stock[]> =>
    fetchApi<Stock[]>(`/stocks/search?q=${encodeURIComponent(query)}`),
}

export const analysisApi = {
  // DCF Analysis
  getDCFAnalysis: (symbol: string): Promise<DCFAnalysis> =>
    fetchApi<DCFAnalysis>(`/analysis/${symbol}/dcf`),
  
  // Comparable Analysis
  getComparableAnalysis: (symbol: string): Promise<ComparableAnalysis> =>
    fetchApi<ComparableAnalysis>(`/analysis/${symbol}/comparable`),
  
  // Risk Analysis
  getRiskMetrics: (symbol: string): Promise<RiskMetrics> =>
    fetchApi<RiskMetrics>(`/analysis/${symbol}/risk`),
  
  // Monte Carlo Simulation
  getMonteCarloSimulation: (symbol: string, simulations: number = 10000): Promise<MonteCarloSimulation> =>
    fetchApi<MonteCarloSimulation>(`/analysis/${symbol}/monte-carlo?simulations=${simulations}`),
}

export const portfolioApi = {
  // Get all portfolios
  getPortfolios: (): Promise<any[]> =>
    fetchApi<any[]>('/portfolios'),
  
  // Get portfolio by ID
  getPortfolio: (id: string): Promise<any> =>
    fetchApi<any>(`/portfolios/${id}`),
  
  // Create portfolio
  createPortfolio: (data: any): Promise<any> =>
    fetchApi<any>('/portfolios', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // Update portfolio
  updatePortfolio: (id: string, data: any): Promise<any> =>
    fetchApi<any>(`/portfolios/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // Delete portfolio
  deletePortfolio: (id: string): Promise<void> =>
    fetchApi<void>(`/portfolios/${id}`, {
      method: 'DELETE',
    }),
}

export { ApiError }
