import { useEffect, useRef, useCallback } from 'react'

interface PerformanceMetrics {
  renderTime: number
  componentName: string
  timestamp: number
}

interface PerformanceHook {
  measureRender: (componentName: string) => () => void
  getMetrics: () => PerformanceMetrics[]
  clearMetrics: () => void
}

export const usePerformance = (): PerformanceHook => {
  const metricsRef = useRef<PerformanceMetrics[]>([])
  const renderStartTimeRef = useRef<number>(0)

  const measureRender = useCallback((componentName: string) => {
    renderStartTimeRef.current = performance.now()
    
    return () => {
      const renderTime = performance.now() - renderStartTimeRef.current
      
      metricsRef.current.push({
        renderTime,
        componentName,
        timestamp: Date.now()
      })
      
      // Keep only last 100 metrics to prevent memory leaks
      if (metricsRef.current.length > 100) {
        metricsRef.current = metricsRef.current.slice(-100)
      }
    }
  }, [])

  const getMetrics = useCallback(() => {
    return [...metricsRef.current]
  }, [])

  const clearMetrics = useCallback(() => {
    metricsRef.current = []
  }, [])

  return {
    measureRender,
    getMetrics,
    clearMetrics
  }
}

// Hook for monitoring component re-renders
export const useRenderCount = (componentName: string) => {
  const renderCountRef = useRef(0)
  const prevPropsRef = useRef<any>()
  const prevStateRef = useRef<any>()

  useEffect(() => {
    renderCountRef.current += 1
    
    if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'development') {
      console.log(`${componentName} rendered ${renderCountRef.current} times`)
    }
  })

  const logRender = useCallback((props?: any, state?: any) => {
    if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'development') {
      const propsChanged = JSON.stringify(props) !== JSON.stringify(prevPropsRef.current)
      const stateChanged = JSON.stringify(state) !== JSON.stringify(prevStateRef.current)
      
      console.log(`${componentName} render #${renderCountRef.current}:`, {
        propsChanged,
        stateChanged,
        props,
        state
      })
      
      prevPropsRef.current = props
      prevStateRef.current = state
    }
  }, [componentName])

  return {
    renderCount: renderCountRef.current,
    logRender
  }
}

// Hook for measuring async operations
export const useAsyncPerformance = () => {
  const operationsRef = useRef<Map<string, number>>(new Map())

  const startOperation = useCallback((operationName: string) => {
    operationsRef.current.set(operationName, performance.now())
  }, [])

  const endOperation = useCallback((operationName: string) => {
    const startTime = operationsRef.current.get(operationName)
    if (startTime) {
      const duration = performance.now() - startTime
      operationsRef.current.delete(operationName)
      
      if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'development') {
        console.log(`${operationName} took ${duration.toFixed(2)}ms`)
      }
      
      return duration
    }
    return 0
  }, [])

  return {
    startOperation,
    endOperation
  }
}

// Hook for memory usage monitoring
export const useMemoryMonitor = () => {
  const checkMemory = useCallback(() => {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      return {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit,
        usage: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100
      }
    }
    return null
  }, [])

  const logMemoryUsage = useCallback((label?: string) => {
    const memory = checkMemory()
    if (memory && typeof process !== 'undefined' && process.env?.NODE_ENV === 'development') {
      console.log(`${label || 'Memory usage'}:`, {
        used: `${(memory.used / 1024 / 1024).toFixed(2)} MB`,
        total: `${(memory.total / 1024 / 1024).toFixed(2)} MB`,
        limit: `${(memory.limit / 1024 / 1024).toFixed(2)} MB`,
        usage: `${memory.usage.toFixed(2)}%`
      })
    }
  }, [checkMemory])

  return {
    checkMemory,
    logMemoryUsage
  }
}
