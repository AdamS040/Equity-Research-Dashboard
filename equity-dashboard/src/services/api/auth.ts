/**
 * Authentication Service
 * 
 * Handles user authentication, token management, and user operations
 */

import { apiClient } from './base'
import {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  RefreshTokenRequest,
  User,
  UserPreferences,
  ApiResponse,
} from '../../types/api'

export class AuthService {
  private readonly basePath = '/auth'

  /**
   * Login user with email and password
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    // Mock login for development - replace with real API call
    return new Promise((resolve) => {
      setTimeout(() => {
                              const mockResponse: AuthResponse = {
             user: {
               id: 'mock-user-id',
               firstName: 'John',
               lastName: 'Doe',
               email: credentials.email,
               role: 'user',
               isActive: true,
               createdAt: new Date().toISOString(),
               updatedAt: new Date().toISOString(),
             },
             token: 'mock-access-token',
             refreshToken: 'mock-refresh-token',
             expiresIn: 3600,
           }
        resolve(mockResponse)
      }, 1000)
    })
  }

  /**
   * Register new user
   */
  async register(userData: RegisterRequest): Promise<AuthResponse> {
    // Mock register for development - replace with real API call
    return new Promise((resolve) => {
      setTimeout(() => {
                              const mockResponse: AuthResponse = {
             user: {
               id: 'mock-user-id',
               firstName: userData.firstName,
               lastName: userData.lastName,
               email: userData.email,
               role: 'user',
               isActive: true,
               createdAt: new Date().toISOString(),
               updatedAt: new Date().toISOString(),
             },
             token: 'mock-access-token',
             refreshToken: 'mock-refresh-token',
             expiresIn: 3600,
           }
        resolve(mockResponse)
      }, 1000)
    })
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    // Mock logout for development - replace with real API call
    return new Promise((resolve) => {
      setTimeout(() => {
        this.clearTokens()
        resolve()
      }, 500)
    })
  }

  /**
   * Refresh authentication token
   */
  async refreshToken(): Promise<AuthResponse> {
    const refreshToken = this.getRefreshToken()
    
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await apiClient.post<AuthResponse>(
      `${this.basePath}/refresh`,
      { refreshToken } as RefreshTokenRequest,
      { skipAuth: true }
    )
    
    // Update tokens
    this.setTokens(response.data.token, response.data.refreshToken)
    
    return response.data
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>(`${this.basePath}/me`)
    return response.data
  }

  /**
   * Update user profile
   */
  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await apiClient.patch<User>(`${this.basePath}/me`, userData)
    return response.data
  }

  /**
   * Update user preferences
   */
  async updatePreferences(preferences: Partial<UserPreferences>): Promise<UserPreferences> {
    const response = await apiClient.patch<UserPreferences>(
      `${this.basePath}/me/preferences`,
      preferences
    )
    return response.data
  }

  /**
   * Change user password
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.patch(`${this.basePath}/me/password`, {
      currentPassword,
      newPassword,
    })
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<void> {
    await apiClient.post(
      `${this.basePath}/forgot-password`,
      { email },
      { skipAuth: true }
    )
  }

  /**
   * Reset password with token
   */
  async resetPassword(token: string, newPassword: string): Promise<void> {
    await apiClient.post(
      `${this.basePath}/reset-password`,
      { token, newPassword },
      { skipAuth: true }
    )
  }

  /**
   * Verify email address
   */
  async verifyEmail(token: string): Promise<void> {
    await apiClient.post(
      `${this.basePath}/verify-email`,
      { token },
      { skipAuth: true }
    )
  }

  /**
   * Resend email verification
   */
  async resendVerification(): Promise<void> {
    await apiClient.post(`${this.basePath}/resend-verification`)
  }

  /**
   * Delete user account
   */
  async deleteAccount(password: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/me`, {
      body: JSON.stringify({ password }),
    })
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = this.getAccessToken()
    return !!token && !this.isTokenExpired(token)
  }

  /**
   * Get access token from storage
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token')
  }

  /**
   * Get refresh token from storage
   */
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token')
  }

  /**
   * Set authentication tokens
   */
  private setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
    
    // Set token in API client
    apiClient.setAuthToken(accessToken)
  }

  /**
   * Clear authentication tokens
   */
  private clearTokens(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    
    // Clear token from API client
    apiClient.setAuthToken(null)
  }

  /**
   * Check if token is expired
   */
  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Date.now() / 1000
      return payload.exp < currentTime
    } catch {
      return true
    }
  }

  /**
   * Initialize authentication state
   */
  initialize(): void {
    const token = this.getAccessToken()
    if (token && !this.isTokenExpired(token)) {
      apiClient.setAuthToken(token)
    } else {
      this.clearTokens()
    }
  }
}

// Create singleton instance
export const authService = new AuthService()

// Initialize authentication on module load
authService.initialize()
