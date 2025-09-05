import React from 'react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import { Button, Card, CardBody, CardHeader, Heading, Text } from './index'
import { ExclamationTriangleIcon, ArrowPathIcon, WifiIcon } from '@heroicons/react/24/outline'

export interface ErrorStatesProps {
  error: Error | string | null
  onRetry?: () => void
  onDismiss?: () => void
  variant?: 'inline' | 'card' | 'fullscreen'
  showDetails?: boolean
  className?: string
}

/**
 * ErrorStates component for displaying user-friendly error messages
 * 
 * @example
 * ```tsx
 * <ErrorStates 
 *   error={error} 
 *   onRetry={() => refetch()} 
 *   variant="card"
 * />
 * ```
 */
export const ErrorStates: React.FC<ErrorStatesProps> = ({
  error,
  onRetry,
  onDismiss,
  variant = 'inline',
  showDetails = false,
  className,
}) => {
  if (!error) return null

  const errorMessage = typeof error === 'string' ? error : error.message
  const errorDetails = typeof error === 'object' ? error.stack : undefined

  const getErrorIcon = () => {
    if (errorMessage.toLowerCase().includes('network') || errorMessage.toLowerCase().includes('fetch')) {
      return <WifiIcon className="h-6 w-6" />
    }
    return <ExclamationTriangleIcon className="h-6 w-6" />
  }

  const getErrorTitle = () => {
    if (errorMessage.toLowerCase().includes('network') || errorMessage.toLowerCase().includes('fetch')) {
      return 'Connection Error'
    }
    if (errorMessage.toLowerCase().includes('timeout')) {
      return 'Request Timeout'
    }
    if (errorMessage.toLowerCase().includes('unauthorized')) {
      return 'Authentication Required'
    }
    return 'Something went wrong'
  }

  const getErrorDescription = () => {
    if (errorMessage.toLowerCase().includes('network') || errorMessage.toLowerCase().includes('fetch')) {
      return 'Please check your internet connection and try again.'
    }
    if (errorMessage.toLowerCase().includes('timeout')) {
      return 'The request is taking longer than expected. Please try again.'
    }
    if (errorMessage.toLowerCase().includes('unauthorized')) {
      return 'Please log in again to continue.'
    }
    return 'An unexpected error occurred. Please try again or contact support if the problem persists.'
  }

  const content = (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className={clsx(
        'flex items-start space-x-3 p-4',
        {
          'bg-danger-50 border border-danger-200 rounded-lg': variant === 'inline',
          'text-danger-800': variant === 'inline',
        },
        className
      )}
    >
      <div className="flex-shrink-0 text-danger-600">
        {getErrorIcon()}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="space-y-2">
          <Heading size="sm" color="danger">
            {getErrorTitle()}
          </Heading>
          <Text size="sm" color="neutral">
            {getErrorDescription()}
          </Text>
          
          {showDetails && errorDetails && (
            <details className="mt-3">
              <summary className="cursor-pointer text-xs font-medium text-neutral-600 hover:text-neutral-800">
                Technical Details
              </summary>
              <div className="mt-2 p-2 bg-neutral-100 rounded text-xs font-mono text-neutral-700 overflow-auto max-h-32">
                <div className="mb-1 font-semibold">Error:</div>
                <div className="mb-2">{errorMessage}</div>
                <div className="font-semibold">Stack:</div>
                <pre className="whitespace-pre-wrap text-xs">{errorDetails}</pre>
              </div>
            </details>
          )}
        </div>
        
        <div className="flex space-x-2 mt-4">
          {onRetry && (
            <Button
              size="sm"
              variant="outline"
              color="danger"
              onClick={onRetry}
              className="flex items-center space-x-1"
            >
              <ArrowPathIcon className="h-4 w-4" />
              <span>Try Again</span>
            </Button>
          )}
          {onDismiss && (
            <Button
              size="sm"
              variant="ghost"
              color="neutral"
              onClick={onDismiss}
            >
              Dismiss
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  )

  if (variant === 'card') {
    return (
      <Card className="border-danger-200">
        <CardBody>
          {content}
        </CardBody>
      </Card>
    )
  }

  if (variant === 'fullscreen') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50 p-4">
        <Card className="max-w-md w-full">
          <CardHeader title={getErrorTitle()} />
          <CardBody>
            {content}
          </CardBody>
        </Card>
      </div>
    )
  }

  return content
}

// Specialized error components
export const NetworkError: React.FC<{ onRetry?: () => void }> = ({ onRetry }) => (
  <ErrorStates
    error="Network connection failed"
    onRetry={onRetry}
    variant="card"
  />
)

export const TimeoutError: React.FC<{ onRetry?: () => void }> = ({ onRetry }) => (
  <ErrorStates
    error="Request timeout"
    onRetry={onRetry}
    variant="card"
  />
)

export const AuthError: React.FC<{ onRetry?: () => void }> = ({ onRetry }) => (
  <ErrorStates
    error="Authentication required"
    onRetry={onRetry}
    variant="card"
  />
)

// Error boundary fallback component
export const ErrorFallback: React.FC<{
  error: Error
  resetError: () => void
  variant?: 'inline' | 'card' | 'fullscreen'
}> = ({ error, resetError, variant = 'fullscreen' }) => (
  <ErrorStates
    error={error}
    onRetry={resetError}
    variant={variant}
    showDetails={process.env.NODE_ENV === 'development'}
  />
)
