/**
 * Base API Client
 * 
 * Provides a foundation for all API services with:
 * - Request/response interceptors
 * - Error handling
 * - Authentication token management
 * - Retry mechanisms
 */

import { ApiError, ApiResponse, PaginatedResponse } from '../../types/api'

export interface ApiConfig {
  baseURL: string
  timeout?: number
  retries?: number
  retryDelay?: number
}

export interface RequestConfig extends RequestInit {
  timeout?: number
  retries?: number
  skipAuth?: boolean
}

export class BaseApiClient {
  private baseURL: string
  private timeout: number
  private retries: number
  private retryDelay: number
  private authToken: string | null = null

  constructor(config: ApiConfig) {
    this.baseURL = config.baseURL
    this.timeout = config.timeout || 10000
    this.retries = config.retries || 3
    this.retryDelay = config.retryDelay || 1000
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string | null) {
    this.authToken = token
  }

  /**
   * Get authentication token
   */
  getAuthToken(): string | null {
    return this.authToken
  }

  /**
   * Make HTTP request with retry logic
   */
  async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const {
      timeout = this.timeout,
      retries = this.retries,
      skipAuth = false,
      ...requestConfig
    } = config

    const url = `${this.baseURL}${endpoint}`
    
    // Prepare headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...requestConfig.headers,
    }

    // Add authentication header if token exists and not skipped
    if (!skipAuth && this.authToken) {
      headers.Authorization = `Bearer ${this.authToken}`
    }

    // Create abort controller for timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    let lastError: Error | null = null

    // Retry logic
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, {
          ...requestConfig,
          headers,
          signal: controller.signal,
        })

        clearTimeout(timeoutId)

        // Handle HTTP errors
        if (!response.ok) {
          const errorData = await this.parseErrorResponse(response)
          throw new ApiError(response.status, errorData.message || 'Request failed')
        }

        // Parse successful response
        const data = await this.parseResponse<T>(response)
        return data

      } catch (error) {
        lastError = error as Error
        clearTimeout(timeoutId)

        // Don't retry on certain errors
        if (this.shouldNotRetry(error as Error, attempt)) {
          throw error
        }

        // Wait before retry (exponential backoff)
        if (attempt < retries) {
          await this.delay(this.retryDelay * Math.pow(2, attempt))
        }
      }
    }

    throw lastError || new Error('Request failed after all retries')
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'GET' })
  }

  /**
   * POST request
   */
  async post<T>(
    endpoint: string,
    data?: any,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  /**
   * PUT request
   */
  async put<T>(
    endpoint: string,
    data?: any,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  /**
   * PATCH request
   */
  async patch<T>(
    endpoint: string,
    data?: any,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' })
  }

  /**
   * Parse successful response
   */
  private async parseResponse<T>(response: Response): Promise<ApiResponse<T>> {
    const contentType = response.headers.get('content-type')
    
    if (contentType?.includes('application/json')) {
      const data = await response.json()
      return {
        data: data.data || data,
        success: data.success !== false,
        message: data.message,
        timestamp: data.timestamp || new Date().toISOString(),
      }
    }

    // Handle non-JSON responses
    const text = await response.text()
    return {
      data: text as unknown as T,
      success: true,
      timestamp: new Date().toISOString(),
    }
  }

  /**
   * Parse error response
   */
  private async parseErrorResponse(response: Response): Promise<any> {
    try {
      const contentType = response.headers.get('content-type')
      if (contentType?.includes('application/json')) {
        return await response.json()
      }
      return { message: await response.text() }
    } catch {
      return { message: 'Unknown error occurred' }
    }
  }

  /**
   * Determine if request should not be retried
   */
  private shouldNotRetry(error: Error, attempt: number): boolean {
    // Don't retry on authentication errors
    if (error instanceof ApiError) {
      return error.status === 401 || error.status === 403 || error.status === 404
    }

    // Don't retry on abort errors (timeout)
    if (error.name === 'AbortError') {
      return true
    }

    // Don't retry on network errors after first attempt
    if (error.name === 'TypeError' && attempt > 0) {
      return true
    }

    return false
  }

  /**
   * Delay utility for retry logic
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

// Create default API client instance
export const apiClient = new BaseApiClient({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  retries: 3,
  retryDelay: 1000,
})
