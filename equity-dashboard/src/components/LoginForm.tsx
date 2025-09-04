/**
 * Login Form Component
 * 
 * Handles user authentication
 */

import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useLogin } from '../hooks/api/useAuth'
import { Button, Input, Card, CardBody, CardHeader, ErrorDisplay } from './ui'

interface LoginFormData {
  email: string
  password: string
}

export const LoginForm: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const loginMutation = useLogin()
  
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
  })
  const [errors, setErrors] = useState<Partial<LoginFormData>>({})

  // Get redirect path from location state
  const from = (location.state as any)?.from?.pathname || '/'

  const validateForm = (): boolean => {
    const newErrors: Partial<LoginFormData> = {}

    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid'
    }

    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    try {
      await loginMutation.mutateAsync(formData)
      navigate(from, { replace: true })
    } catch (error) {
      // Error is handled by the mutation
      console.error('Login failed:', error)
    }
  }

  const handleInputChange = (field: keyof LoginFormData) => (value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-bold text-neutral-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-sm text-neutral-600">
            Or{' '}
            <Link
              to="/register"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              create a new account
            </Link>
          </p>
        </div>

        <Card>
          <CardBody>
            <form onSubmit={handleSubmit} className="space-y-6">
              {loginMutation.error && (
                <ErrorDisplay
                  error={loginMutation.error}
                  variant="inline"
                  onDismiss={() => loginMutation.reset()}
                />
              )}

              <div>
                <Input
                  label="Email address"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange('email')}
                  state={errors.email ? 'error' : 'default'}
                  errorMessage={errors.email}
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div>
                <Input
                  label="Password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange('password')}
                  state={errors.password ? 'error' : 'default'}
                  errorMessage={errors.password}
                  placeholder="Enter your password"
                  required
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-neutral-300 rounded"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-neutral-900">
                    Remember me
                  </label>
                </div>

                <div className="text-sm">
                  <Link
                    to="/forgot-password"
                    className="font-medium text-primary-600 hover:text-primary-500"
                  >
                    Forgot your password?
                  </Link>
                </div>
              </div>

              <div>
                <Button
                  type="submit"
                  fullWidth
                  loading={loginMutation.isPending}
                  disabled={loginMutation.isPending}
                >
                  {loginMutation.isPending ? 'Signing in...' : 'Sign in'}
                </Button>
              </div>
            </form>
          </CardBody>
        </Card>

        <div className="text-center">
          <p className="text-sm text-neutral-600">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              Sign up here
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
