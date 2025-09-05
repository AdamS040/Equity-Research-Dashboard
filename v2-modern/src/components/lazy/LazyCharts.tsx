/**
 * Lazy Loading Chart Components
 * 
 * Provides optimized lazy loading for heavy chart components
 * with intersection observer and preloading strategies
 */

import React, { Suspense, lazy, useState, useEffect, useRef, useCallback } from 'react'
import { createLazyComponent } from '../../utils/lazy-loading'
import { LazyWrapper } from '../optimized/LazyWrapper'

// Lazy load heavy chart components
const RechartsLineChart = createLazyComponent(() => import('recharts').then(module => ({ 
  default: module.LineChart 
})))
const RechartsBarChart = createLazyComponent(() => import('recharts').then(module => ({ 
  default: module.BarChart 
})))
const RechartsPieChart = createLazyComponent(() => import('recharts').then(module => ({ 
  default: module.PieChart 
})))
const RechartsAreaChart = createLazyComponent(() => import('recharts').then(module => ({ 
  default: module.AreaChart 
})))

// Lazy load chart components
const DCFCalculator = createLazyComponent(() => import('../analytics/DCFCalculator'))
const RiskAnalysis = createLazyComponent(() => import('../analytics/RiskAnalysis'))
const BacktestingEngine = createLazyComponent(() => import('../analytics/BacktestingEngine'))
const OptionsAnalysis = createLazyComponent(() => import('../analytics/OptionsAnalysis'))

// Chart loading fallback
const ChartFallback = ({ height = 300 }: { height?: number }) => (
  <div 
    className="flex items-center justify-center bg-gray-50 border border-gray-200 rounded-lg"
    style={{ height: `${height}px` }}
  >
    <div className="text-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      <p className="mt-2 text-sm text-gray-600">Loading chart...</p>
    </div>
  </div>
)

// Intersection Observer hook for lazy loading
function useIntersectionObserver(
  elementRef: React.RefObject<HTMLElement>,
  options: IntersectionObserverInit = {}
) {
  const [isIntersecting, setIsIntersecting] = useState(false)

  useEffect(() => {
    const element = elementRef.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting)
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options
      }
    )

    observer.observe(element)

    return () => {
      observer.unobserve(element)
    }
  }, [elementRef, options])

  return isIntersecting
}

// Lazy Chart Container
interface LazyChartContainerProps {
  children: React.ReactNode
  height?: number
  className?: string
  preload?: boolean
}

export const LazyChartContainer: React.FC<LazyChartContainerProps> = ({
  children,
  height = 300,
  className = '',
  preload = false
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const isIntersecting = useIntersectionObserver(containerRef)
  const [shouldLoad, setShouldLoad] = useState(preload)

  useEffect(() => {
    if (isIntersecting && !shouldLoad) {
      setShouldLoad(true)
    }
  }, [isIntersecting, shouldLoad])

  return (
    <div ref={containerRef} className={className}>
      {shouldLoad ? (
        <LazyWrapper fallback={<ChartFallback height={height} />}>
          {children}
        </LazyWrapper>
      ) : (
        <ChartFallback height={height} />
      )}
    </div>
  )
}

// Optimized Chart Components
export const LazyLineChart: React.FC<any> = (props) => (
  <LazyChartContainer height={props.height}>
    <RechartsLineChart {...props} />
  </LazyChartContainer>
)

export const LazyBarChart: React.FC<any> = (props) => (
  <LazyChartContainer height={props.height}>
    <RechartsBarChart {...props} />
  </LazyChartContainer>
)

export const LazyPieChart: React.FC<any> = (props) => (
  <LazyChartContainer height={props.height}>
    <RechartsPieChart {...props} />
  </LazyChartContainer>
)

export const LazyAreaChart: React.FC<any> = (props) => (
  <LazyChartContainer height={props.height}>
    <RechartsAreaChart {...props} />
  </LazyChartContainer>
)

// Analytics Components
export const LazyDCFCalculator: React.FC<any> = (props) => (
  <LazyChartContainer height={400}>
    <DCFCalculator {...props} />
  </LazyChartContainer>
)

export const LazyRiskAnalysis: React.FC<any> = (props) => (
  <LazyChartContainer height={400}>
    <RiskAnalysis {...props} />
  </LazyChartContainer>
)

export const LazyBacktestingEngine: React.FC<any> = (props) => (
  <LazyChartContainer height={500}>
    <BacktestingEngine {...props} />
  </LazyChartContainer>
)

export const LazyOptionsAnalysis: React.FC<any> = (props) => (
  <LazyChartContainer height={400}>
    <OptionsAnalysis {...props} />
  </LazyChartContainer>
)

// Chart preloader utility
export const preloadCharts = () => {
  // Preload commonly used chart components
  import('recharts').catch(() => {})
  import('../analytics/DCFCalculator').catch(() => {})
  import('../analytics/RiskAnalysis').catch(() => {})
}
