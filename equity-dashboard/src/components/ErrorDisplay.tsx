/**
 * Error Display Component
 * 
 * Displays API errors and other error states in a user-friendly way
 */

import React from 'react'
import { ExclamationTriangleIcon, ArrowPathIcon, XCircleIcon } from '@heroicons/react/24/outline'
import { Button, Card, CardBody, CardHeader, Heading, Text } from './ui'
import { ApiError } from '../types/api'

interface ErrorDisplayProps {
  error: Error | ApiError | unknown
  title?: string
  message?: string
  onRetry?: () => void
  onDismiss?: () => void
  showDetails?: boolean
  variant?: 'card' | 'inline' | 'fullscreen'
  className?: string
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  title,
  message,
  onRetry,
  onDismiss,
  showDetails = false,
  variant = 'card',
  className = '',
}) => {
  // Extract error information
  const getErrorInfo = () => {
    if (error instanceof ApiError) {
      return {
        title: title || 'API Error',
        message: message || error.message,
        status: error.status,
        code: error.code,
        details: error.details,
      }
    }

    if (error instanceof Error) {
      return {
        title: title || 'Error',
        message: message || error.message,
        status: null,
        code: null,
        details: error.stack,
      }
    }

    return {
      title: title || 'Unknown Error',
      message: message || 'An unexpected error occurred',
      status: null,
      code: null,
      details: String(error),
    }
  }

  const errorInfo = getErrorInfo()

  // Get appropriate icon based on error type
  const getErrorIcon = () => {
    if (error instanceof ApiError) {
      if (error.status >= 500) {
        return <XCircleIcon className="w-6 h-6 text-danger-500" />
      }
      if (error.status >= 400) {
        return <ExclamationTriangleIcon className="w-6 h-6 text-warning-500" />
      }
    }
    return <ExclamationTriangleIcon className="w-6 h-6 text-danger-500" />
  }

  // Get appropriate color based on error type
  const getErrorColor = () => {
    if (error instanceof ApiError) {
      if (error.status >= 500) return 'danger'
      if (error.status >= 400) return 'warning'
    }
    return 'danger'
  }

  const errorColor = getErrorColor()

  // Render based on variant
  if (variant === 'inline') {
    return (
      <div className={`flex items-center gap-2 p-3 bg-${errorColor}-50 border border-${errorColor}-200 rounded-lg ${className}`}>
        {getErrorIcon()}
        <div className="flex-1">
          <Text size="sm" weight="medium" className={`text-${errorColor}-800`}>
            {errorInfo.title}
          </Text>
          <Text size="sm" className={`text-${errorColor}-700`}>
            {errorInfo.message}
          </Text>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className={`text-${errorColor}-400 hover:text-${errorColor}-600`}
          >
            <XCircleIcon className="w-4 h-4" />
          </button>
        )}
      </div>
    )
  }

  if (variant === 'fullscreen') {
    return (
      <div className={`min-h-screen flex items-center justify-center bg-neutral-50 p-4 ${className}`}>
        <Card className="max-w-md w-full">
          <CardBody className="text-center">
            <div className="flex justify-center mb-4">
              {getErrorIcon()}
            </div>
            <Heading level={3} size="lg" className={`text-${errorColor}-800 mb-2`}>
              {errorInfo.title}
            </Heading>
            <Text color="neutral" className="mb-6">
              {errorInfo.message}
            </Text>

            {showDetails && errorInfo.details && (
              <details className="mb-6 text-left">
                <summary className="cursor-pointer text-sm font-medium text-neutral-700 mb-2">
                  Error Details
                </summary>
                <div className="p-3 bg-neutral-100 rounded text-xs font-mono text-neutral-800 overflow-auto">
                  <pre className="whitespace-pre-wrap">{errorInfo.details}</pre>
                </div>
              </details>
            )}

            <div className="flex gap-3 justify-center">
              {onRetry && (
                <Button onClick={onRetry} color={errorColor} leftIcon={<ArrowPathIcon className="w-4 h-4" />}>
                  Try Again
                </Button>
              )}
              {onDismiss && (
                <Button onClick={onDismiss} variant="outline" color={errorColor}>
                  Dismiss
                </Button>
              )}
            </div>
          </CardBody>
        </Card>
      </div>
    )
  }

  // Default card variant
  return (
    <Card className={`border-${errorColor}-200 ${className}`}>
      <CardHeader
        title={errorInfo.title}
        actions={
          onDismiss && (
            <button
              onClick={onDismiss}
              className={`text-${errorColor}-400 hover:text-${errorColor}-600`}
            >
              <XCircleIcon className="w-5 h-5" />
            </button>
          )
        }
      />
      <CardBody>
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            {getErrorIcon()}
            <div className="flex-1">
              <Text className={`text-${errorColor}-800`}>
                {errorInfo.message}
              </Text>
              
              {errorInfo.status && (
                <Text size="sm" className={`text-${errorColor}-600 mt-1`}>
                  Status: {errorInfo.status}
                  {errorInfo.code && ` (${errorInfo.code})`}
                </Text>
              )}
            </div>
          </div>

          {showDetails && errorInfo.details && (
            <details>
              <summary className="cursor-pointer text-sm font-medium text-neutral-700 mb-2">
                Error Details
              </summary>
              <div className="p-3 bg-neutral-100 rounded text-xs font-mono text-neutral-800 overflow-auto">
                <pre className="whitespace-pre-wrap">{errorInfo.details}</pre>
              </div>
            </details>
          )}

          {onRetry && (
            <div className="flex justify-end">
              <Button
                onClick={onRetry}
                variant="outline"
                color={errorColor}
                leftIcon={<ArrowPathIcon className="w-4 h-4" />}
              >
                Try Again
              </Button>
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  )
}

// Hook for handling API errors
export const useErrorHandler = () => {
  const handleError = (error: unknown, context?: string) => {
    console.error(`Error in ${context || 'unknown context'}:`, error)

    // Log to external service in production
    if (process.env.NODE_ENV === 'production') {
      // TODO: Send error to logging service
    }

    // Show user-friendly error message
    if (error instanceof ApiError) {
      switch (error.status) {
        case 401:
          // Handle authentication errors
          break
        case 403:
          // Handle authorization errors
          break
        case 404:
          // Handle not found errors
          break
        case 429:
          // Handle rate limiting
          break
        case 500:
          // Handle server errors
          break
        default:
          // Handle other errors
          break
      }
    }
  }

  return { handleError }
}
