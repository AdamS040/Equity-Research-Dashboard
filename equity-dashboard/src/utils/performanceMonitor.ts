/**
 * Performance Monitoring System
 * 
 * Comprehensive performance tracking including:
 * - Core Web Vitals
 * - Custom metrics
 * - Error tracking
 * - User experience metrics
 */

interface PerformanceMetric {
  name: string
  value: number
  timestamp: number
  type: 'timing' | 'counter' | 'gauge'
  tags?: Record<string, string>
}

interface CoreWebVitals {
  lcp: number | null // Largest Contentful Paint
  fid: number | null // First Input Delay
  cls: number | null // Cumulative Layout Shift
  fcp: number | null // First Contentful Paint
  ttfb: number | null // Time to First Byte
}

interface UserExperienceMetrics {
  pageLoadTime: number
  timeToInteractive: number
  firstPaint: number
  firstContentfulPaint: number
  domContentLoaded: number
  windowLoad: number
}

class PerformanceMonitor {
  private static instance: PerformanceMonitor
  private metrics: PerformanceMetric[] = []
  private observers: PerformanceObserver[] = []
  private isEnabled = true

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor()
    }
    return PerformanceMonitor.instance
  }

  constructor() {
    this.initializeObservers()
    this.trackPageLoad()
    this.trackUserInteractions()
  }

  // Initialize performance observers
  private initializeObservers() {
    if (!('PerformanceObserver' in window)) {
      console.warn('PerformanceObserver not supported')
      return
    }

    // Observe navigation timing
    try {
      const navObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric({
            name: entry.name,
            value: entry.startTime,
            timestamp: Date.now(),
            type: 'timing',
            tags: { category: 'navigation' }
          })
        }
      })
      navObserver.observe({ entryTypes: ['navigation'] })
      this.observers.push(navObserver)
    } catch (error) {
      console.warn('Navigation observer failed:', error)
    }

    // Observe paint timing
    try {
      const paintObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric({
            name: entry.name,
            value: entry.startTime,
            timestamp: Date.now(),
            type: 'timing',
            tags: { category: 'paint' }
          })
        }
      })
      paintObserver.observe({ entryTypes: ['paint'] })
      this.observers.push(paintObserver)
    } catch (error) {
      console.warn('Paint observer failed:', error)
    }

    // Observe layout shifts
    try {
      const clsObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const layoutShiftEntry = entry as any
          if (layoutShiftEntry.hadRecentInput) continue
          
          this.recordMetric({
            name: 'layout-shift',
            value: layoutShiftEntry.value,
            timestamp: Date.now(),
            type: 'gauge',
            tags: { category: 'layout' }
          })
        }
      })
      clsObserver.observe({ entryTypes: ['layout-shift'] })
      this.observers.push(clsObserver)
    } catch (error) {
      console.warn('Layout shift observer failed:', error)
    }

    // Observe long tasks
    try {
      const longTaskObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric({
            name: 'long-task',
            value: entry.duration,
            timestamp: Date.now(),
            type: 'timing',
            tags: { category: 'long-task' }
          })
        }
      })
      longTaskObserver.observe({ entryTypes: ['longtask'] })
      this.observers.push(longTaskObserver)
    } catch (error) {
      console.warn('Long task observer failed:', error)
    }
  }

  // Track page load performance
  private trackPageLoad() {
    window.addEventListener('load', () => {
      setTimeout(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
        const paint = performance.getEntriesByType('paint')
        
        const metrics: UserExperienceMetrics = {
          pageLoadTime: navigation.loadEventEnd - navigation.fetchStart,
          timeToInteractive: this.calculateTimeToInteractive(),
          firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
          firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
          windowLoad: navigation.loadEventEnd - navigation.fetchStart
        }

        this.recordUserExperienceMetrics(metrics)
      }, 0)
    })
  }

  // Track user interactions
  private trackUserInteractions() {
    let interactionCount = 0
    let totalInteractionDelay = 0

    const trackInteraction = (event: Event) => {
      const startTime = performance.now()
      
      requestAnimationFrame(() => {
        const delay = performance.now() - startTime
        interactionCount++
        totalInteractionDelay += delay

        this.recordMetric({
          name: 'interaction-delay',
          value: delay,
          timestamp: Date.now(),
          type: 'timing',
          tags: { 
            category: 'interaction',
            type: event.type 
          }
        })
      })
    }

    // Track various user interactions
    ['click', 'keydown', 'scroll', 'touchstart'].forEach(eventType => {
      document.addEventListener(eventType, trackInteraction, { passive: true })
    })

    // Track average interaction delay
    setInterval(() => {
      if (interactionCount > 0) {
        this.recordMetric({
          name: 'avg-interaction-delay',
          value: totalInteractionDelay / interactionCount,
          timestamp: Date.now(),
          type: 'gauge',
          tags: { category: 'interaction' }
        })
        
        interactionCount = 0
        totalInteractionDelay = 0
      }
    }, 10000) // Every 10 seconds
  }

  // Calculate Time to Interactive (simplified)
  private calculateTimeToInteractive(): number {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    const longTasks = performance.getEntriesByType('longtask')
    
    if (longTasks.length === 0) {
      return navigation.domContentLoadedEventEnd - navigation.fetchStart
    }

    const lastLongTask = longTasks[longTasks.length - 1]
    return lastLongTask.startTime + lastLongTask.duration
  }

  // Record a performance metric
  recordMetric(metric: PerformanceMetric) {
    if (!this.isEnabled) return

    this.metrics.push(metric)
    
    // Keep only last 1000 metrics to prevent memory issues
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000)
    }

    // Send to analytics service (if configured)
    this.sendToAnalytics(metric)
  }

  // Record user experience metrics
  recordUserExperienceMetrics(metrics: UserExperienceMetrics) {
    Object.entries(metrics).forEach(([name, value]) => {
      this.recordMetric({
        name,
        value,
        timestamp: Date.now(),
        type: 'timing',
        tags: { category: 'user-experience' }
      })
    })
  }

  // Get Core Web Vitals
  getCoreWebVitals(): CoreWebVitals {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    const paint = performance.getEntriesByType('paint')
    
    return {
      lcp: this.getLargestContentfulPaint(),
      fid: this.getFirstInputDelay(),
      cls: this.getCumulativeLayoutShift(),
      fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime || null,
      ttfb: navigation.responseStart - navigation.requestStart
    }
  }

  // Get Largest Contentful Paint
  private getLargestContentfulPaint(): number | null {
    const lcpEntries = performance.getEntriesByType('largest-contentful-paint')
    if (lcpEntries.length === 0) return null
    
    const lastEntry = lcpEntries[lcpEntries.length - 1]
    return lastEntry.startTime
  }

  // Get First Input Delay
  private getFirstInputDelay(): number | null {
    const fidEntries = performance.getEntriesByType('first-input')
    if (fidEntries.length === 0) return null
    
    const entry = fidEntries[0] as any
    return entry.processingStart - entry.startTime
  }

  // Get Cumulative Layout Shift
  private getCumulativeLayoutShift(): number | null {
    const clsEntries = performance.getEntriesByType('layout-shift')
    let cls = 0
    
    for (const entry of clsEntries) {
      if (!(entry as any).hadRecentInput) {
        cls += (entry as any).value
      }
    }
    
    return cls
  }

  // Get performance summary
  getPerformanceSummary() {
    const coreWebVitals = this.getCoreWebVitals()
    const recentMetrics = this.metrics.slice(-100)
    
    const summary = {
      coreWebVitals,
      totalMetrics: this.metrics.length,
      recentMetrics: recentMetrics.length,
      averageLoadTime: this.getAverageMetric('pageLoadTime'),
      averageInteractionDelay: this.getAverageMetric('interaction-delay'),
      longTasks: this.getMetricCount('long-task'),
      layoutShifts: this.getMetricCount('layout-shift')
    }

    return summary
  }

  // Get average value for a metric
  private getAverageMetric(metricName: string): number {
    const metrics = this.metrics.filter(m => m.name === metricName)
    if (metrics.length === 0) return 0
    
    const sum = metrics.reduce((total, metric) => total + metric.value, 0)
    return sum / metrics.length
  }

  // Get count of a specific metric
  private getMetricCount(metricName: string): number {
    return this.metrics.filter(m => m.name === metricName).length
  }

  // Send metrics to analytics service
  private sendToAnalytics(metric: PerformanceMetric) {
    // This would integrate with your analytics service
    // For now, just log to console in development
    if (typeof window !== 'undefined' && (window as any).process?.env?.NODE_ENV === 'development') {
      console.log('Performance metric:', metric)
    }
  }

  // Enable/disable monitoring
  setEnabled(enabled: boolean) {
    this.isEnabled = enabled
  }

  // Clear all metrics
  clearMetrics() {
    this.metrics = []
  }

  // Cleanup observers
  cleanup() {
    this.observers.forEach(observer => observer.disconnect())
    this.observers = []
  }
}

// Global performance monitor instance
export const performanceMonitor = PerformanceMonitor.getInstance()

// React hook for performance monitoring
export function usePerformanceMonitoring() {
  const [coreWebVitals, setCoreWebVitals] = useState<CoreWebVitals | null>(null)
  const [summary, setSummary] = useState<any>(null)

  useEffect(() => {
    const updateMetrics = () => {
      setCoreWebVitals(performanceMonitor.getCoreWebVitals())
      setSummary(performanceMonitor.getPerformanceSummary())
    }

    // Update metrics immediately
    updateMetrics()

    // Update metrics every 5 seconds
    const interval = setInterval(updateMetrics, 5000)

    return () => clearInterval(interval)
  }, [])

  const recordCustomMetric = useCallback((name: string, value: number, tags?: Record<string, string>) => {
    performanceMonitor.recordMetric({
      name,
      value,
      timestamp: Date.now(),
      type: 'timing',
      tags
    })
  }, [])

  const getPerformanceReport = useCallback(() => {
    return performanceMonitor.getPerformanceSummary()
  }, [])

  return {
    coreWebVitals,
    summary,
    recordCustomMetric,
    getPerformanceReport
  }
}

// Import React hooks
import { useState, useEffect, useCallback } from 'react'
