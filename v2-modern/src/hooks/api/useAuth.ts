/**
 * Authentication Hooks
 * 
 * React Query hooks for authentication operations
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { authService } from '../../services/api/auth'
import { AuthToken, LoginRequest, RegisterRequest } from '../../types/api'
import { storage } from '../../utils'
import { useAuth as useAuthContext } from '../../components/AuthProvider'

export const useLogin = () => {
  const queryClient = useQueryClient()
  const { setUser, setTokens } = useAuthContext()

  return useMutation({
    mutationFn: (credentials: LoginRequest) => authService.login(credentials),
    onSuccess: (data) => {
      storage.set('accessToken', data.token)
      storage.set('refreshToken', data.refreshToken)
      setUser(data.user)
      setTokens({ accessToken: data.token, refreshToken: data.refreshToken })
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })
}

export const useRegister = () => {
  const queryClient = useQueryClient()
  const { setUser, setTokens } = useAuthContext()

  return useMutation({
    mutationFn: (userData: RegisterRequest) => authService.register(userData),
    onSuccess: (data) => {
      storage.set('accessToken', data.token)
      storage.set('refreshToken', data.refreshToken)
      setUser(data.user)
      setTokens({ accessToken: data.token, refreshToken: data.refreshToken })
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })
}

export const useLogout = () => {
  const queryClient = useQueryClient()
  const { clearAuth } = useAuthContext()

  return useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      clearAuth()
      queryClient.clear()
    },
  })
}

