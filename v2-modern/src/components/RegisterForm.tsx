/**
 * Register Form Component
 * 
 * Handles user registration
 */

import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useRegister } from '../hooks/api/useAuth'
import { Button, Input, Card, CardBody, ErrorDisplay } from './ui'

interface RegisterFormData {
  firstName: string
  lastName: string
  email: string
  password: string
  confirmPassword: string
  agreeToTerms: boolean
}

export const RegisterForm: React.FC = () => {
  const navigate = useNavigate()
  const registerMutation = useRegister()
  
  const [formData, setFormData] = useState<RegisterFormData>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
  })
  const [errors, setErrors] = useState<Partial<RegisterFormData>>({})

  const validateForm = (): boolean => {
    const newErrors: Partial<RegisterFormData> = {}

    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required'
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required'
    }

    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid'
    }

    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters'
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password'
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }

    if (!formData.agreeToTerms) {
      newErrors.agreeToTerms = 'You must agree to the terms and conditions'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    try {
      await registerMutation.mutateAsync({
        firstName: formData.firstName,
        lastName: formData.lastName,
        email: formData.email,
        password: formData.password,
      })
      navigate('/')
    } catch (error) {
      // Error is handled by the mutation
      console.error('Registration failed:', error)
    }
  }

  const handleInputChange = (field: keyof RegisterFormData) => (value: string | boolean) => {
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
            Create your account
          </h2>
          <p className="mt-2 text-sm text-neutral-600">
            Or{' '}
            <Link
              to="/login"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              sign in to your existing account
            </Link>
          </p>
        </div>

        <Card>
          <CardBody>
            <form onSubmit={handleSubmit} className="space-y-6">
              {registerMutation.error && (
                <ErrorDisplay
                  error={registerMutation.error}
                  variant="inline"
                  onDismiss={() => registerMutation.reset()}
                />
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Input
                    label="First name"
                    value={formData.firstName}
                    onChange={handleInputChange('firstName')}
                    state={errors.firstName ? 'error' : 'default'}
                    errorMessage={errors.firstName}
                    placeholder="Enter your first name"
                    required
                  />
                </div>
                <div>
                  <Input
                    label="Last name"
                    value={formData.lastName}
                    onChange={handleInputChange('lastName')}
                    state={errors.lastName ? 'error' : 'default'}
                    errorMessage={errors.lastName}
                    placeholder="Enter your last name"
                    required
                  />
                </div>
              </div>

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
                  placeholder="Create a password"
                  required
                />
              </div>

              <div>
                <Input
                  label="Confirm password"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange('confirmPassword')}
                  state={errors.confirmPassword ? 'error' : 'default'}
                  errorMessage={errors.confirmPassword}
                  placeholder="Confirm your password"
                  required
                />
              </div>

              <div className="flex items-center">
                <input
                  id="agree-to-terms"
                  name="agree-to-terms"
                  type="checkbox"
                  checked={formData.agreeToTerms}
                  onChange={(e) => handleInputChange('agreeToTerms')(e.target.checked)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-neutral-300 rounded"
                />
                <label htmlFor="agree-to-terms" className="ml-2 block text-sm text-neutral-900">
                  I agree to the{' '}
                  <Link to="/terms" className="text-primary-600 hover:text-primary-500">
                    Terms and Conditions
                  </Link>{' '}
                  and{' '}
                  <Link to="/privacy" className="text-primary-600 hover:text-primary-500">
                    Privacy Policy
                  </Link>
                </label>
              </div>

              {errors.agreeToTerms && (
                <p className="text-sm text-danger-600">{errors.agreeToTerms}</p>
              )}

              <div>
                <Button
                  type="submit"
                  fullWidth
                  loading={registerMutation.isPending}
                  disabled={registerMutation.isPending}
                >
                  {registerMutation.isPending ? 'Creating account...' : 'Create account'}
                </Button>
              </div>
            </form>
          </CardBody>
        </Card>

        <div className="text-center">
          <p className="text-sm text-neutral-600">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
