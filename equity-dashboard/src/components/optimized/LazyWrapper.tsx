/**
 * Lazy Wrapper Component
 * 
 * Enhanced Suspense wrapper with performance monitoring
 */

import React, { Suspense, useEffect } from 'react'
import { ErrorBoundary } from '../ErrorBoundary'

interface LazyWrapperProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  onLoadStart?: () => void
  onLoadComplete?: () => void
  onError?: (error: Error) => void
}

// Default fallback component
const DefaultFallback = () => (
  <div className="flex items-center justify-center min-h-[400px]">
    <div className="text-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      <p className="mt-4 text-neutral-600">Loading...</p>
    </div>
  </div>
)

export const LazyWrapper: React.FC<LazyWrapperProps> = ({
  children,
  fallback,
  onLoadStart,
  onLoadComplete,
  onError
}) => {
  const startTime = performance.now()

  useEffect(() => {
    onLoadStart?.()
  }, [onLoadStart])

  const handleLoadComplete = () => {
    const loadTime = performance.now() - startTime
    onLoadComplete?.()
    
    // Log performance metrics
    if (loadTime > 1000) {
      console.warn(`Slow component load: ${loadTime.toFixed(2)}ms`)
    }
  }

  return (
    <ErrorBoundary onError={onError}>
      <Suspense 
        fallback={
          <div>
            {fallback || <DefaultFallback />}
          </div>
        }
      >
        <div onLoad={handleLoadComplete}>
          {children}
        </div>
      </Suspense>
    </ErrorBoundary>
  )
}
