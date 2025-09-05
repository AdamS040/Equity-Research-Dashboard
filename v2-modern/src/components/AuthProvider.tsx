/**
 * Authentication Provider
 * 
 * Provides authentication context and manages auth state
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, AuthToken } from '../types/api'
import { storage } from '../utils'

interface AuthContextType {
  user: User | null
  tokens: AuthToken | null
  isAuthenticated: boolean
  isLoading: boolean
  setUser: (user: User | null) => void
  setTokens: (tokens: AuthToken | null) => void
  clearAuth: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [tokens, setTokens] = useState<AuthToken | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadAuthData = () => {
      const storedAccessToken = storage.get<string | null>('accessToken', null)
      const storedRefreshToken = storage.get<string | null>('refreshToken', null)
      // In a real app, you'd also fetch user data based on the token
      // For now, we'll assume if tokens exist, user is "authenticated"
      if (storedAccessToken && storedRefreshToken) {
        setTokens({ accessToken: storedAccessToken, refreshToken: storedRefreshToken })
        // Mock user for now, replace with actual user data fetch
        setUser({ 
          id: 'mock-user-id', 
          firstName: 'John', 
          lastName: 'Doe', 
          email: 'john.doe@example.com', 
          role: 'user', 
          isActive: true,
          createdAt: new Date().toISOString(), 
          updatedAt: new Date().toISOString() 
        })
      }
      setIsLoading(false)
    }
    loadAuthData()
  }, [])

  const clearAuth = () => {
    storage.remove('accessToken')
    storage.remove('refreshToken')
    setUser(null)
    setTokens(null)
  }

  const isAuthenticated = !!tokens?.accessToken && !!user

  const value: AuthContextType = {
    user,
    tokens,
    isAuthenticated,
    isLoading,
    setUser,
    setTokens,
    clearAuth,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Hook to check if user has specific role
export const useRole = (requiredRole: string | string[]): boolean => {
  const { user } = useAuth()
  
  if (!user) return false
  
  const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole]
  return roles.includes(user.role)
}

// Hook to check if user has specific permission
export const usePermission = (permission: string): boolean => {
  const { user } = useAuth()
  
  if (!user) return false
  
  // Define role-based permissions
  const permissions: Record<string, string[]> = {
    user: ['read:own-data', 'write:own-data'],
    analyst: ['read:own-data', 'write:own-data', 'read:all-data', 'write:reports'],
    admin: ['read:all-data', 'write:all-data', 'admin:users', 'admin:system'],
  }
  
  const userPermissions = permissions[user.role] || []
  return userPermissions.includes(permission)
}
