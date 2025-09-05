/**
 * Bundle Analysis Utilities
 * 
 * Provides runtime bundle analysis and performance monitoring
 */

interface BundleInfo {
  name: string
  size: number
  gzipSize: number
  brotliSize: number
  dependencies: string[]
}

interface PerformanceMetrics {
  loadTime: number
  renderTime: number
  bundleSize: number
  chunkCount: number
  cacheHitRate: number
}

class BundleAnalyzer {
  private static instance: BundleAnalyzer
  private metrics: PerformanceMetrics[] = []
  private bundleInfo: BundleInfo[] = []

  static getInstance(): BundleAnalyzer {
    if (!BundleAnalyzer.instance) {
      BundleAnalyzer.instance = new BundleAnalyzer()
    }
    return BundleAnalyzer.instance
  }

  // Analyze current bundle
  analyzeBundle(): BundleInfo[] {
    const scripts = Array.from(document.querySelectorAll('script[src]'))
    const stylesheets = Array.from(document.querySelectorAll('link[rel="stylesheet"]'))
    
    const bundles: BundleInfo[] = []

    // Analyze JavaScript bundles
    scripts.forEach((script) => {
      const src = script.getAttribute('src')
      if (src) {
        bundles.push({
          name: this.extractBundleName(src),
          size: this.getResourceSize(src),
          gzipSize: 0, // Would need server-side calculation
          brotliSize: 0, // Would need server-side calculation
          dependencies: this.extractDependencies(src)
        })
      }
    })

    // Analyze CSS bundles
    stylesheets.forEach((link) => {
      const href = link.getAttribute('href')
      if (href) {
        bundles.push({
          name: this.extractBundleName(href),
          size: this.getResourceSize(href),
          gzipSize: 0,
          brotliSize: 0,
          dependencies: []
        })
      }
    })

    this.bundleInfo = bundles
    return bundles
  }

  // Measure performance metrics
  measurePerformance(): PerformanceMetrics {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    const paint = performance.getEntriesByType('paint')
    
    const loadTime = navigation.loadEventEnd - navigation.fetchStart
    const renderTime = paint.find(entry => entry.name === 'first-contentful-paint')?.startTime || 0
    
    const bundles = this.analyzeBundle()
    const bundleSize = bundles.reduce((total, bundle) => total + bundle.size, 0)
    const chunkCount = bundles.length

    const metrics: PerformanceMetrics = {
      loadTime,
      renderTime,
      bundleSize,
      chunkCount,
      cacheHitRate: this.calculateCacheHitRate()
    }

    this.metrics.push(metrics)
    return metrics
  }

  // Get bundle statistics
  getBundleStats() {
    const bundles = this.analyzeBundle()
    
    return {
      totalSize: bundles.reduce((sum, bundle) => sum + bundle.size, 0),
      totalChunks: bundles.length,
      largestChunk: bundles.reduce((largest, bundle) => 
        bundle.size > largest.size ? bundle : largest, bundles[0] || { size: 0, name: '' }),
      averageChunkSize: bundles.length > 0 ? 
        bundles.reduce((sum, bundle) => sum + bundle.size, 0) / bundles.length : 0,
      vendorSize: bundles
        .filter(bundle => bundle.name.includes('vendor'))
        .reduce((sum, bundle) => sum + bundle.size, 0),
      appSize: bundles
        .filter(bundle => !bundle.name.includes('vendor'))
        .reduce((sum, bundle) => sum + bundle.size, 0)
    }
  }

  // Get performance trends
  getPerformanceTrends() {
    if (this.metrics.length < 2) {
      return { trend: 'insufficient_data', change: 0 }
    }

    const recent = this.metrics.slice(-5) // Last 5 measurements
    const older = this.metrics.slice(-10, -5) // Previous 5 measurements

    const recentAvg = recent.reduce((sum, m) => sum + m.loadTime, 0) / recent.length
    const olderAvg = older.reduce((sum, m) => sum + m.loadTime, 0) / older.length

    const change = ((recentAvg - olderAvg) / olderAvg) * 100

    return {
      trend: change > 5 ? 'degrading' : change < -5 ? 'improving' : 'stable',
      change: Math.round(change * 100) / 100
    }
  }

  // Generate performance report
  generateReport(): string {
    const stats = this.getBundleStats()
    const trends = this.getPerformanceTrends()
    const latestMetrics = this.metrics[this.metrics.length - 1]

    return `
# Performance Report

## Bundle Analysis
- **Total Size**: ${(stats.totalSize / 1024).toFixed(2)} KB
- **Total Chunks**: ${stats.totalChunks}
- **Largest Chunk**: ${stats.largestChunk.name} (${(stats.largestChunk.size / 1024).toFixed(2)} KB)
- **Average Chunk Size**: ${(stats.averageChunkSize / 1024).toFixed(2)} KB
- **Vendor Size**: ${(stats.vendorSize / 1024).toFixed(2)} KB
- **App Size**: ${(stats.appSize / 1024).toFixed(2)} KB

## Performance Metrics
- **Load Time**: ${latestMetrics?.loadTime.toFixed(2)} ms
- **Render Time**: ${latestMetrics?.renderTime.toFixed(2)} ms
- **Cache Hit Rate**: ${(latestMetrics?.cacheHitRate * 100).toFixed(2)}%

## Trends
- **Performance Trend**: ${trends.trend}
- **Change**: ${trends.change}%

## Recommendations
${this.generateRecommendations(stats, latestMetrics)}
    `.trim()
  }

  // Private helper methods
  private extractBundleName(url: string): string {
    const filename = url.split('/').pop() || ''
    return filename.split('?')[0] // Remove query parameters
  }

  private getResourceSize(url: string): number {
    // This would need to be implemented with actual resource size measurement
    // For now, return estimated size based on URL patterns
    if (url.includes('vendor')) return 150 * 1024 // 150KB estimate
    if (url.includes('chunk')) return 50 * 1024 // 50KB estimate
    return 25 * 1024 // 25KB estimate
  }

  private extractDependencies(url: string): string[] {
    // This would analyze the actual bundle to extract dependencies
    // For now, return empty array
    return []
  }

  private calculateCacheHitRate(): number {
    // This would calculate actual cache hit rate
    // For now, return a placeholder value
    return 0.85
  }

  private generateRecommendations(stats: any, metrics: PerformanceMetrics | undefined): string {
    const recommendations: string[] = []

    if (stats.totalSize > 500 * 1024) {
      recommendations.push('- Consider code splitting to reduce bundle size')
    }

    if (stats.largestChunk.size > 200 * 1024) {
      recommendations.push('- Split large chunks into smaller ones')
    }

    if (stats.vendorSize > 300 * 1024) {
      recommendations.push('- Optimize vendor bundle size')
    }

    if (metrics && metrics.loadTime > 3000) {
      recommendations.push('- Optimize loading performance')
    }

    if (metrics && metrics.cacheHitRate < 0.8) {
      recommendations.push('- Improve caching strategy')
    }

    return recommendations.length > 0 ? recommendations.join('\n') : '- Performance looks good!'
  }
}

// Global bundle analyzer instance
export const bundleAnalyzer = BundleAnalyzer.getInstance()

// React hook for bundle analysis
export function useBundleAnalysis() {
  const [bundleStats, setBundleStats] = useState<any>(null)
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const analyze = useCallback(async () => {
    setIsAnalyzing(true)
    
    try {
      const stats = bundleAnalyzer.getBundleStats()
      const metrics = bundleAnalyzer.measurePerformance()
      
      setBundleStats(stats)
      setPerformanceMetrics(metrics)
    } catch (error) {
      console.error('Bundle analysis failed:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }, [])

  const generateReport = useCallback(() => {
    return bundleAnalyzer.generateReport()
  }, [])

  useEffect(() => {
    // Auto-analyze on mount
    analyze()
  }, [analyze])

  return {
    bundleStats,
    performanceMetrics,
    isAnalyzing,
    analyze,
    generateReport
  }
}

// Import React hooks
import { useState, useCallback, useEffect } from 'react'
