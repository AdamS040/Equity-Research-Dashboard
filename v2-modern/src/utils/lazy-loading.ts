/**
 * Advanced Lazy Loading Utilities
 * 
 * Provides optimized lazy loading with preloading capabilities,
 * error boundaries, and performance monitoring
 */

import React, { ComponentType, lazy, Suspense } from 'react'
import { ErrorBoundary } from '../components/ErrorBoundary'

// Simplified lazy loading with basic retry mechanism
export function createLazyComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  retries: number = 2
): T {
  return lazy(() => {
    return new Promise<{ default: T }>((resolve, reject) => {
      let attempts = 0

      const attemptImport = async () => {
        try {
          const module = await importFn()
          
          // Ensure we have a valid default export
          if (module.default && typeof module.default === 'function') {
            resolve(module)
          } else {
            throw new Error('Module does not have a valid default export')
          }
        } catch (error) {
          attempts++
          console.warn(`Lazy loading attempt ${attempts} failed:`, error)
          
          if (attempts < retries) {
            // Simple exponential backoff
            const delay = Math.min(1000 * Math.pow(2, attempts - 1), 3000)
            setTimeout(attemptImport, delay)
          } else {
            console.error('Lazy loading failed after all retries:', error)
            reject(error)
          }
        }
      }

      attemptImport()
    })
  })
}

// Network status check
export function isOnline(): boolean {
  return navigator.onLine
}

// Check if we have a good connection
export function hasGoodConnection(): boolean {
  if (!('connection' in navigator)) return true
  
  const connection = (navigator as any).connection
  if (!connection) return true
  
  // Skip preloading on slow connections
  return !['slow-2g', '2g'].includes(connection.effectiveType)
}

// Preload function for critical components
export function preloadComponent(importFn: () => Promise<any>): void {
  // Only preload if we have a good connection
  if (!hasGoodConnection()) {
    return
  }

  // Preload after a short delay to not block initial render
  setTimeout(() => {
    importFn().catch((error) => {
      console.warn('Preload failed:', error)
    })
  }, 100)
}

// Performance monitoring utilities for lazy loading
export function createPerformanceMonitor() {
  const startTime = performance.now()

  const handleLoadStart = () => {
    console.log('Component load started')
  }

  const handleLoadComplete = () => {
    const loadTime = performance.now() - startTime
    console.log(`Component load completed in ${loadTime.toFixed(2)}ms`)
    
    // Log performance metrics
    if (loadTime > 1000) {
      console.warn(`Slow component load: ${loadTime.toFixed(2)}ms`)
    }
  }

  return {
    startTime,
    handleLoadStart,
    handleLoadComplete
  }
}

// Route-based preloading strategy
export class RoutePreloader {
  private preloadedRoutes = new Set<string>()
  private preloadQueue: Array<() => Promise<any>> = []
  private isProcessing = false

  // Preload a route component
  preloadRoute(routePath: string, importFn: () => Promise<any>): void {
    if (this.preloadedRoutes.has(routePath)) {
      return
    }

    this.preloadQueue.push(async () => {
      try {
        await importFn()
        this.preloadedRoutes.add(routePath)
        console.log(`Preloaded route: ${routePath}`)
      } catch (error) {
        console.warn(`Failed to preload route ${routePath}:`, error)
      }
    })

    this.processQueue()
  }

  // Process preload queue with throttling
  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.preloadQueue.length === 0) {
      return
    }

    this.isProcessing = true

    while (this.preloadQueue.length > 0) {
      const preloadFn = this.preloadQueue.shift()
      if (preloadFn) {
        await preloadFn()
        // Small delay between preloads to not block the main thread
        await new Promise(resolve => setTimeout(resolve, 50))
      }
    }

    this.isProcessing = false
  }

  // Check if route is preloaded
  isPreloaded(routePath: string): boolean {
    return this.preloadedRoutes.has(routePath)
  }
}

// Global preloader instance
export const routePreloader = new RoutePreloader()

// Performance monitoring for lazy loading
export class LazyLoadMonitor {
  private loadTimes = new Map<string, number>()
  private errorCount = new Map<string, number>()

  recordLoadStart(componentName: string): number {
    const startTime = performance.now()
    this.loadTimes.set(`${componentName}_start`, startTime)
    return startTime
  }

  recordLoadComplete(componentName: string): number {
    const startTime = this.loadTimes.get(`${componentName}_start`)
    if (!startTime) return 0

    const loadTime = performance.now() - startTime
    this.loadTimes.set(`${componentName}_complete`, loadTime)
    
    // Log slow loads
    if (loadTime > 1000) {
      console.warn(`Slow lazy load for ${componentName}: ${loadTime.toFixed(2)}ms`)
    }

    return loadTime
  }

  recordError(componentName: string): void {
    const currentCount = this.errorCount.get(componentName) || 0
    this.errorCount.set(componentName, currentCount + 1)
  }

  getStats() {
    return {
      loadTimes: Object.fromEntries(this.loadTimes),
      errorCounts: Object.fromEntries(this.errorCount)
    }
  }
}

// Global monitor instance
export const lazyLoadMonitor = new LazyLoadMonitor()
