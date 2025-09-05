/**
 * Error Boundary Component
 * 
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI
 */

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Button, Card, CardBody, CardHeader, Heading, Text } from './ui'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo)
    }

    // Check for specific error types and provide helpful context
    if (error.message.includes('Failed to fetch dynamically imported module')) {
      console.warn('Dynamic import failed - this might be a network issue or module loading problem')
    }
    
    if (error.message.includes('Cannot read properties of null')) {
      console.warn('React hooks error detected - component may not be properly initialized')
      console.warn('This is often caused by inconsistent React imports or lazy loading timing issues')
    }
    
    if (error.message.includes('useState')) {
      console.warn('useState error detected - check React import consistency')
    }

    // Update state with error info
    this.setState({
      error,
      errorInfo,
    })

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    // Log error to external service in production
    if (process.env.NODE_ENV === 'production') {
      // TODO: Send error to logging service (e.g., Sentry, LogRocket)
      console.error('Production error:', error, errorInfo)
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-neutral-50 p-4">
          <Card className="max-w-md w-full">
            <CardHeader title="Something went wrong" />
            <CardBody>
              <div className="space-y-4">
                <Text color="neutral">
                  We're sorry, but something unexpected happened. Please try refreshing the page
                  or contact support if the problem persists.
                </Text>

                {process.env.NODE_ENV === 'development' && this.state.error && (
                  <details className="mt-4">
                    <summary className="cursor-pointer text-sm font-medium text-neutral-700">
                      Error Details (Development)
                    </summary>
                    <div className="mt-2 p-3 bg-neutral-100 rounded text-xs font-mono text-neutral-800 overflow-auto">
                      <div className="mb-2">
                        <strong>Error:</strong> {this.state.error.message}
                      </div>
                      {this.state.errorInfo && (
                        <div>
                          <strong>Stack:</strong>
                          <pre className="whitespace-pre-wrap mt-1">
                            {this.state.errorInfo.componentStack}
                          </pre>
                        </div>
                      )}
                    </div>
                  </details>
                )}

                <div className="flex gap-3">
                  <Button onClick={this.handleRetry} color="primary">
                    Try Again
                  </Button>
                  <Button
                    onClick={() => window.location.reload()}
                    variant="outline"
                    color="primary"
                  >
                    Refresh Page
                  </Button>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

// Higher-order component for easier usage
export const withErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) => {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  )

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`

  return WrappedComponent
}
