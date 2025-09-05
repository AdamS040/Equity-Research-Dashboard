/**
 * Stock Data Service
 * 
 * Handles stock market data, quotes, historical data, and analysis
 */

import { apiClient } from './base'
import {
  Stock,
  StockQuote,
  HistoricalData,
  FinancialMetrics,
  StockNews,
  StockSearchResult,
  DCFAnalysis,
  ComparableAnalysis,
  RiskAnalysis,
  MonteCarloSimulation,
  ApiResponse,
  PaginatedResponse,
  RequestParams,
} from '../../types/api'

export class StockService {
  private readonly basePath = '/stocks'

  /**
   * Search for stocks
   */
  async searchStocks(query: string, limit: number = 10): Promise<StockSearchResult[]> {
    const response = await apiClient.get<StockSearchResult[]>(
      `${this.basePath}/search`,
      {
        params: { q: query, limit: limit.toString() },
      }
    )
    return response.data
  }

  /**
   * Get stock information
   */
  async getStock(symbol: string): Promise<Stock> {
    const response = await apiClient.get<Stock>(`${this.basePath}/${symbol}`)
    return response.data
  }

  /**
   * Get stock quote (real-time price data)
   */
  async getQuote(symbol: string): Promise<StockQuote> {
    const response = await apiClient.get<StockQuote>(`${this.basePath}/${symbol}/quote`)
    return response.data
  }

  /**
   * Get multiple stock quotes
   */
  async getQuotes(symbols: string[]): Promise<StockQuote[]> {
    const response = await apiClient.post<StockQuote[]>(
      `${this.basePath}/quotes`,
      { symbols }
    )
    return response.data
  }

  /**
   * Get historical price data
   */
  async getHistoricalData(
    symbol: string,
    period: string = '1y',
    interval: string = '1d'
  ): Promise<HistoricalData[]> {
    const response = await apiClient.get<HistoricalData[]>(
      `${this.basePath}/${symbol}/historical`,
      {
        params: { period, interval },
      }
    )
    return response.data
  }

  /**
   * Get financial metrics
   */
  async getFinancialMetrics(
    symbol: string,
    period: 'annual' | 'quarterly' = 'annual'
  ): Promise<FinancialMetrics[]> {
    const response = await apiClient.get<FinancialMetrics[]>(
      `${this.basePath}/${symbol}/metrics`,
      {
        params: { period },
      }
    )
    return response.data
  }

  /**
   * Get stock news
   */
  async getNews(
    symbol: string,
    params: RequestParams = {}
  ): Promise<PaginatedResponse<StockNews>> {
    const response = await apiClient.get<PaginatedResponse<StockNews>>(
      `${this.basePath}/${symbol}/news`,
      { params }
    )
    return response.data
  }

  /**
   * Get market overview
   */
  async getMarketOverview(): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/market/overview`)
    return response.data
  }

  /**
   * Get sector performance
   */
  async getSectorPerformance(): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/market/sectors`)
    return response.data
  }

  /**
   * Get market movers
   */
  async getMarketMovers(): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/market/movers`)
    return response.data
  }

  /**
   * Get trending stocks
   */
  async getTrendingStocks(): Promise<StockQuote[]> {
    const response = await apiClient.get<StockQuote[]>(`${this.basePath}/trending`)
    return response.data
  }

  /**
   * Get similar stocks
   */
  async getSimilarStocks(symbol: string): Promise<Stock[]> {
    const response = await apiClient.get<Stock[]>(`${this.basePath}/${symbol}/similar`)
    return response.data
  }

  /**
   * Get stock recommendations
   */
  async getRecommendations(symbol: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${symbol}/recommendations`)
    return response.data
  }

  /**
   * Get earnings calendar
   */
  async getEarningsCalendar(
    startDate: string,
    endDate: string
  ): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/earnings/calendar`, {
      params: { startDate, endDate },
    })
    return response.data
  }

  /**
   * Get dividend history
   */
  async getDividendHistory(symbol: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${symbol}/dividends`)
    return response.data
  }

  /**
   * Get stock splits
   */
  async getStockSplits(symbol: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${symbol}/splits`)
    return response.data
  }

  /**
   * Get insider trading data
   */
  async getInsiderTrading(symbol: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${symbol}/insider-trading`)
    return response.data
  }

  /**
   * Get institutional holdings
   */
  async getInstitutionalHoldings(symbol: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${symbol}/institutional-holdings`)
    return response.data
  }

  /**
   * Get analyst estimates
   */
  async getAnalystEstimates(symbol: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${symbol}/estimates`)
    return response.data
  }

  /**
   * Get price targets
   */
  async getPriceTargets(symbol: string): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/${symbol}/price-targets`)
    return response.data
  }

  /**
   * Get technical indicators
   */
  async getTechnicalIndicators(
    symbol: string,
    indicators: string[] = ['sma', 'ema', 'rsi', 'macd']
  ): Promise<any> {
    const response = await apiClient.post(`${this.basePath}/${symbol}/technical`, {
      indicators,
    })
    return response.data
  }

  /**
   * Get options data
   */
  async getOptionsData(symbol: string, expirationDate?: string): Promise<any> {
    const params: any = {}
    if (expirationDate) {
      params.expirationDate = expirationDate
    }
    
    const response = await apiClient.get(`${this.basePath}/${symbol}/options`, {
      params,
    })
    return response.data
  }

  /**
   * Get options chain
   */
  async getOptionsChain(symbol: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${symbol}/options/chain`)
    return response.data
  }

  /**
   * Get implied volatility
   */
  async getImpliedVolatility(symbol: string): Promise<any> {
    const response = await apiClient.get(`${this.basePath}/${symbol}/volatility`)
    return response.data
  }

  /**
   * Get DCF analysis
   */
  async getDCFAnalysis(symbol: string): Promise<DCFAnalysis> {
    const response = await apiClient.get<DCFAnalysis>(`${this.basePath}/${symbol}/analysis/dcf`)
    return response.data
  }

  /**
   * Create custom DCF analysis
   */
  async createDCFAnalysis(symbol: string, assumptions: any): Promise<DCFAnalysis> {
    const response = await apiClient.post<DCFAnalysis>(
      `${this.basePath}/${symbol}/analysis/dcf`,
      assumptions
    )
    return response.data
  }

  /**
   * Get comparable analysis
   */
  async getComparableAnalysis(symbol: string): Promise<ComparableAnalysis> {
    const response = await apiClient.get<ComparableAnalysis>(
      `${this.basePath}/${symbol}/analysis/comparable`
    )
    return response.data
  }

  /**
   * Create custom comparable analysis
   */
  async createComparableAnalysis(
    symbol: string,
    peerSymbols: string[]
  ): Promise<ComparableAnalysis> {
    const response = await apiClient.post<ComparableAnalysis>(
      `${this.basePath}/${symbol}/analysis/comparable`,
      { peerSymbols }
    )
    return response.data
  }

  /**
   * Get risk analysis
   */
  async getRiskAnalysis(symbol: string): Promise<RiskAnalysis> {
    const response = await apiClient.get<RiskAnalysis>(
      `${this.basePath}/${symbol}/analysis/risk`
    )
    return response.data
  }

  /**
   * Get Monte Carlo simulation
   */
  async getMonteCarloSimulation(
    symbol: string,
    parameters: any
  ): Promise<MonteCarloSimulation> {
    const response = await apiClient.post<MonteCarloSimulation>(
      `${this.basePath}/${symbol}/analysis/monte-carlo`,
      parameters
    )
    return response.data
  }

  /**
   * Get all analysis for a stock
   */
  async getAllAnalysis(symbol: string): Promise<{
    dcf: DCFAnalysis
    comparable: ComparableAnalysis
    risk: RiskAnalysis
  }> {
    const response = await apiClient.get(`${this.basePath}/${symbol}/analysis`)
    return response.data
  }

  /**
   * Get watchlist for user
   */
  async getWatchlist(): Promise<string[]> {
    const response = await apiClient.get<string[]>(`${this.basePath}/watchlist`)
    return response.data
  }

  /**
   * Add stock to watchlist
   */
  async addToWatchlist(symbol: string): Promise<void> {
    await apiClient.post(`${this.basePath}/watchlist`, { symbol })
  }

  /**
   * Remove stock from watchlist
   */
  async removeFromWatchlist(symbol: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/watchlist/${symbol}`)
  }

  /**
   * Get user's saved analyses
   */
  async getSavedAnalyses(): Promise<any[]> {
    const response = await apiClient.get(`${this.basePath}/analyses/saved`)
    return response.data
  }

  /**
   * Save analysis
   */
  async saveAnalysis(analysisId: string, name: string): Promise<void> {
    await apiClient.post(`${this.basePath}/analyses/saved`, {
      analysisId,
      name,
    })
  }

  /**
   * Delete saved analysis
   */
  async deleteSavedAnalysis(analysisId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/analyses/saved/${analysisId}`)
  }
}

// Create singleton instance
export const stockService = new StockService()
