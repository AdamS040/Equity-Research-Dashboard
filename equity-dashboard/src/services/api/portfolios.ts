/**
 * Portfolio Service
 * 
 * Handles portfolio management, holdings, performance, and optimization
 */

import { apiClient } from './base'
import {
  Portfolio,
  PortfolioHolding,
  PortfolioPerformance,
  PortfolioOptimization,
  OptimizationConstraints,
  ApiResponse,
  PaginatedResponse,
  RequestParams,
} from '../../types/api'

export interface CreatePortfolioRequest {
  name: string
  description?: string
  settings?: Partial<Portfolio['settings']>
}

export interface UpdatePortfolioRequest {
  name?: string
  description?: string
  settings?: Partial<Portfolio['settings']>
}

export interface AddHoldingRequest {
  symbol: string
  shares: number
  averagePrice: number
}

export interface UpdateHoldingRequest {
  shares?: number
  averagePrice?: number
}

export class PortfolioService {
  private readonly basePath = '/portfolios'

  /**
   * Get all portfolios for the current user
   */
  async getPortfolios(params: RequestParams = {}): Promise<PaginatedResponse<Portfolio>> {
    const response = await apiClient.get<PaginatedResponse<Portfolio>>(
      this.basePath,
      { params }
    )
    return response.data
  }

  /**
   * Get a specific portfolio
   */
  async getPortfolio(portfolioId: string): Promise<Portfolio> {
    const response = await apiClient.get<Portfolio>(`${this.basePath}/${portfolioId}`)
    return response.data
  }

  /**
   * Create a new portfolio
   */
  async createPortfolio(data: CreatePortfolioRequest): Promise<Portfolio> {
    const response = await apiClient.post<Portfolio>(this.basePath, data)
    return response.data
  }

  /**
   * Update portfolio
   */
  async updatePortfolio(portfolioId: string, data: UpdatePortfolioRequest): Promise<Portfolio> {
    const response = await apiClient.patch<Portfolio>(`${this.basePath}/${portfolioId}`, data)
    return response.data
  }

  /**
   * Delete portfolio
   */
  async deletePortfolio(portfolioId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/${portfolioId}`)
  }

  /**
   * Duplicate portfolio
   */
  async duplicatePortfolio(portfolioId: string, name: string): Promise<Portfolio> {
    const response = await apiClient.post<Portfolio>(
      `${this.basePath}/${portfolioId}/duplicate`,
      { name }
    )
    return response.data
  }

  /**
   * Get portfolio holdings
   */
  async getHoldings(portfolioId: string): Promise<PortfolioHolding[]> {
    const response = await apiClient.get<PortfolioHolding[]>(
      `${this.basePath}/${portfolioId}/holdings`
    )
    return response.data
  }

  /**
   * Add holding to portfolio
   */
  async addHolding(portfolioId: string, data: AddHoldingRequest): Promise<PortfolioHolding> {
    const response = await apiClient.post<PortfolioHolding>(
      `${this.basePath}/${portfolioId}/holdings`,
      data
    )
    return response.data
  }

  /**
   * Update holding
   */
  async updateHolding(
    portfolioId: string,
    holdingId: string,
    data: UpdateHoldingRequest
  ): Promise<PortfolioHolding> {
    const response = await apiClient.patch<PortfolioHolding>(
      `${this.basePath}/${portfolioId}/holdings/${holdingId}`,
      data
    )
    return response.data
  }

  /**
   * Remove holding from portfolio
   */
  async removeHolding(portfolioId: string, holdingId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/${portfolioId}/holdings/${holdingId}`)
  }

  /**
   * Bulk update holdings
   */
  async bulkUpdateHoldings(
    portfolioId: string,
    holdings: Array<{ id: string; shares: number; averagePrice: number }>
  ): Promise<PortfolioHolding[]> {
    const response = await apiClient.patch<PortfolioHolding[]>(
      `${this.basePath}/${portfolioId}/holdings/bulk`,
      { holdings }
    )
    return response.data
  }

  /**
   * Rebalance portfolio
   */
  async rebalancePortfolio(
    portfolioId: string,
    targetAllocation: Record<string, number>
  ): Promise<PortfolioHolding[]> {
    const response = await apiClient.post<PortfolioHolding[]>(
      `${this.basePath}/${portfolioId}/rebalance`,
      { targetAllocation }
    )
    return response.data
  }

  /**
   * Get portfolio performance
   */
  async getPerformance(
    portfolioId: string,
    period: string = '1y'
  ): Promise<PortfolioPerformance> {
    const response = await apiClient.get<PortfolioPerformance>(
      `${this.basePath}/${portfolioId}/performance`,
      { params: { period } }
    )
    return response.data
  }

  /**
   * Get portfolio performance history
   */
  async getPerformanceHistory(
    portfolioId: string,
    startDate: string,
    endDate: string
  ): Promise<any[]> {
    const response = await apiClient.get(
      `${this.basePath}/${portfolioId}/performance/history`,
      { params: { startDate, endDate } }
    )
    return response.data
  }

  /**
   * Get portfolio risk metrics
   */
  async getRiskMetrics(portfolioId: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${portfolioId}/risk`)
    return response.data
  }

  /**
   * Get portfolio allocation
   */
  async getAllocation(portfolioId: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${portfolioId}/allocation`)
    return response.data
  }

  /**
   * Get sector allocation
   */
  async getSectorAllocation(portfolioId: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${portfolioId}/allocation/sectors`)
    return response.data
  }

  /**
   * Get geographic allocation
   */
  async getGeographicAllocation(portfolioId: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${portfolioId}/allocation/geographic`)
    return response.data
  }

  /**
   * Get portfolio optimization
   */
  async getOptimization(
    portfolioId: string,
    constraints: OptimizationConstraints
  ): Promise<PortfolioOptimization> {
    const response = await apiClient.post<PortfolioOptimization>(
      `${this.basePath}/${portfolioId}/optimize`,
      constraints
    )
    return response.data
  }

  /**
   * Get efficient frontier
   */
  async getEfficientFrontier(portfolioId: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${portfolioId}/efficient-frontier`)
    return response.data
  }

  /**
   * Get portfolio correlation matrix
   */
  async getCorrelationMatrix(portfolioId: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${portfolioId}/correlation`)
    return response.data
  }

  /**
   * Get portfolio attribution analysis
   */
  async getAttributionAnalysis(portfolioId: string, period: string = '1y'): Promise<any> {
    const response = await apiClient.get(
      `${this.basePath}/${portfolioId}/attribution`,
      { params: { period } }
    )
    return response.data
  }

  /**
   * Get portfolio transactions
   */
  async getTransactions(
    portfolioId: string,
    params: RequestParams = {}
  ): Promise<PaginatedResponse<any>> {
    const response = await apiClient.get<PaginatedResponse<any>>(
      `${this.basePath}/${portfolioId}/transactions`,
      { params }
    )
    return response.data
  }

  /**
   * Add transaction
   */
  async addTransaction(portfolioId: string, transaction: any): Promise<any> {
    const response = await apiClient.post(
      `${this.basePath}/${portfolioId}/transactions`,
      transaction
    )
    return response.data
  }

  /**
   * Update transaction
   */
  async updateTransaction(portfolioId: string, transactionId: string, data: any): Promise<any> {
    const response = await apiClient.patch(
      `${this.basePath}/${portfolioId}/transactions/${transactionId}`,
      data
    )
    return response.data
  }

  /**
   * Delete transaction
   */
  async deleteTransaction(portfolioId: string, transactionId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/${portfolioId}/transactions/${transactionId}`)
  }

  /**
   * Get portfolio dividends
   */
  async getDividends(portfolioId: string, year?: number): Promise<any[]> {
    const params: any = {}
    if (year) params.year = year.toString()
    
    const response = await apiClient.get(
      `${this.basePath}/${portfolioId}/dividends`,
      { params }
    )
    return response.data
  }

  /**
   * Get portfolio tax lots
   */
  async getTaxLots(portfolioId: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${portfolioId}/tax-lots`)
    return response.data
  }

  /**
   * Get portfolio alerts
   */
  async getAlerts(portfolioId: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${portfolioId}/alerts`)
    return response.data
  }

  /**
   * Create portfolio alert
   */
  async createAlert(portfolioId: string, alert: any): Promise<any> {
    const response = await apiClient.post(`${this.basePath}/${portfolioId}/alerts`, alert)
    return response.data
  }

  /**
   * Update portfolio alert
   */
  async updateAlert(portfolioId: string, alertId: string, data: any): Promise<any> {
    const response = await apiClient.patch(
      `${this.basePath}/${portfolioId}/alerts/${alertId}`,
      data
    )
    return response.data
  }

  /**
   * Delete portfolio alert
   */
  async deleteAlert(portfolioId: string, alertId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/${portfolioId}/alerts/${alertId}`)
  }

  /**
   * Export portfolio data
   */
  async exportPortfolio(portfolioId: string, format: 'csv' | 'xlsx' | 'pdf' = 'csv'): Promise<Blob> {
    const response = await apiClient.get(
      `${this.basePath}/${portfolioId}/export`,
      { params: { format } }
    )
    return response.data
  }

  /**
   * Import portfolio data
   */
  async importPortfolio(portfolioId: string, file: File): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post(
      `${this.basePath}/${portfolioId}/import`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  }

  /**
   * Get portfolio templates
   */
  async getTemplates(): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/templates`)
    return response.data
  }

  /**
   * Create portfolio from template
   */
  async createFromTemplate(templateId: string, name: string): Promise<Portfolio> {
    const response = await apiClient.post<Portfolio>(
      `${this.basePath}/templates/${templateId}/create`,
      { name }
    )
    return response.data
  }

  /**
   * Get portfolio benchmarks
   */
  async getBenchmarks(portfolioId: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${portfolioId}/benchmarks`)
    return response.data
  }

  /**
   * Set portfolio benchmark
   */
  async setBenchmark(portfolioId: string, benchmarkSymbol: string): Promise<void> {
    await apiClient.patch(`${this.basePath}/${portfolioId}/benchmark`, {
      benchmarkSymbol,
    })
  }

  /**
   * Get portfolio comparison
   */
  async comparePortfolios(portfolioIds: string[]): Promise<any> {
    const response = await apiClient.post(`${this.basePath}/compare`, { portfolioIds })
    return response.data
  }
}

// Create singleton instance
export const portfolioService = new PortfolioService()
