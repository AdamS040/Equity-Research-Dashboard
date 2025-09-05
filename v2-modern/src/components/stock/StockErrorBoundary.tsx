import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Card, CardBody, Button } from '../ui'
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: ErrorInfo
}

export class StockErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ error, errorInfo })
    this.props.onError?.(error, errorInfo)
    
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Stock component error:', error, errorInfo)
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <Card className="mb-6">
          <CardBody>
            <div className="text-center py-12">
              <ExclamationTriangleIcon className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                Something went wrong
              </h3>
              <p className="text-neutral-600 mb-4">
                There was an error loading the stock data. Please try again.
              </p>
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="text-left bg-neutral-100 p-4 rounded-lg mb-4">
                  <summary className="cursor-pointer font-medium text-neutral-700 mb-2">
                    Error Details (Development Only)
                  </summary>
                  <pre className="text-xs text-red-600 whitespace-pre-wrap">
                    {this.state.error.toString()}
                    {this.state.errorInfo?.componentStack}
                  </pre>
                </details>
              )}
              <Button
                onClick={this.handleRetry}
                leftIcon={<ArrowPathIcon className="w-4 h-4" />}
              >
                Try Again
              </Button>
            </div>
          </CardBody>
        </Card>
      )
    }

    return this.props.children
  }
}

// Higher-order component for wrapping stock components with error boundary
export function withStockErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode
) {
  return function WrappedComponent(props: P) {
    return (
      <StockErrorBoundary fallback={fallback}>
        <Component {...props} />
      </StockErrorBoundary>
    )
  }
}
