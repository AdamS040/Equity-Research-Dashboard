/**
 * Performance Dashboard Component
 * 
 * Displays real-time performance metrics and monitoring data
 */

import React, { memo, useState, useEffect, useCallback } from 'react'
import { Card, CardHeader, CardBody, Badge, Button, Progress } from '../ui'
import { usePerformanceMonitoring } from '../../utils/performanceMonitor'
import { useBundleAnalysis } from '../../utils/bundleAnalysis'
import { useMemoryMonitor } from '../../hooks/usePerformance'

interface PerformanceDashboardProps {
  className?: string
  showDetails?: boolean
}

// Performance metric card component
const MetricCard = memo<{
  title: string
  value: string | number
  unit?: string
  status: 'good' | 'warning' | 'poor'
  description?: string
  trend?: 'up' | 'down' | 'stable'
}>(({ title, value, unit = '', status, description, trend }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'good': return 'text-green-600 bg-green-50'
      case 'warning': return 'text-yellow-600 bg-yellow-50'
      case 'poor': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return '↗'
      case 'down': return '↘'
      case 'stable': return '→'
      default: return ''
    }
  }

  return (
    <Card className="h-full">
      <CardBody className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-700">{title}</h3>
          <Badge className={getStatusColor()}>
            {status}
          </Badge>
        </div>
        <div className="flex items-baseline">
          <span className="text-2xl font-bold text-gray-900">
            {typeof value === 'number' ? value.toFixed(1) : value}
          </span>
          {unit && <span className="ml-1 text-sm text-gray-500">{unit}</span>}
          {trend && (
            <span className="ml-2 text-sm text-gray-400">{getTrendIcon()}</span>
          )}
        </div>
        {description && (
          <p className="mt-2 text-xs text-gray-500">{description}</p>
        )}
      </CardBody>
    </Card>
  )
})

MetricCard.displayName = 'MetricCard'

// Core Web Vitals section
const CoreWebVitalsSection = memo<{ coreWebVitals: any }>(({ coreWebVitals }) => {
  const getLCPStatus = (value: number | null) => {
    if (!value) return 'warning'
    if (value <= 2500) return 'good'
    if (value <= 4000) return 'warning'
    return 'poor'
  }

  const getFIDStatus = (value: number | null) => {
    if (!value) return 'warning'
    if (value <= 100) return 'good'
    if (value <= 300) return 'warning'
    return 'poor'
  }

  const getCLSStatus = (value: number | null) => {
    if (!value) return 'warning'
    if (value <= 0.1) return 'good'
    if (value <= 0.25) return 'warning'
    return 'poor'
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Core Web Vitals</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          title="Largest Contentful Paint"
          value={coreWebVitals.lcp || 0}
          unit="ms"
          status={getLCPStatus(coreWebVitals.lcp)}
          description="Loading performance"
        />
        <MetricCard
          title="First Input Delay"
          value={coreWebVitals.fid || 0}
          unit="ms"
          status={getFIDStatus(coreWebVitals.fid)}
          description="Interactivity"
        />
        <MetricCard
          title="Cumulative Layout Shift"
          value={coreWebVitals.cls || 0}
          unit=""
          status={getCLSStatus(coreWebVitals.cls)}
          description="Visual stability"
        />
      </div>
    </div>
  )
})

CoreWebVitalsSection.displayName = 'CoreWebVitalsSection'

// Bundle analysis section
const BundleAnalysisSection = memo<{ bundleStats: any }>(({ bundleStats }) => {
  if (!bundleStats) return null

  const getSizeStatus = (size: number) => {
    if (size <= 500 * 1024) return 'good'
    if (size <= 1000 * 1024) return 'warning'
    return 'poor'
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Bundle Analysis</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Bundle Size"
          value={(bundleStats.totalSize / 1024).toFixed(1)}
          unit="KB"
          status={getSizeStatus(bundleStats.totalSize)}
          description="All JavaScript and CSS"
        />
        <MetricCard
          title="Total Chunks"
          value={bundleStats.totalChunks}
          unit=""
          status="good"
          description="Number of bundles"
        />
        <MetricCard
          title="Vendor Size"
          value={(bundleStats.vendorSize / 1024).toFixed(1)}
          unit="KB"
          status={getSizeStatus(bundleStats.vendorSize)}
          description="Third-party libraries"
        />
        <MetricCard
          title="App Size"
          value={(bundleStats.appSize / 1024).toFixed(1)}
          unit="KB"
          status={getSizeStatus(bundleStats.appSize)}
          description="Application code"
        />
      </div>
    </div>
  )
})

BundleAnalysisSection.displayName = 'BundleAnalysisSection'

// Memory usage section
const MemorySection = memo<{ memoryInfo: any }>(({ memoryInfo }) => {
  if (!memoryInfo.usedJSHeapSize) return null

  const usedMB = memoryInfo.usedJSHeapSize / (1024 * 1024)
  const totalMB = memoryInfo.totalJSHeapSize / (1024 * 1024)
  const limitMB = memoryInfo.jsHeapSizeLimit / (1024 * 1024)
  const usagePercent = (usedMB / limitMB) * 100

  const getMemoryStatus = (percent: number) => {
    if (percent <= 50) return 'good'
    if (percent <= 80) return 'warning'
    return 'poor'
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Memory Usage</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          title="Used Memory"
          value={usedMB.toFixed(1)}
          unit="MB"
          status={getMemoryStatus(usagePercent)}
          description="Currently allocated"
        />
        <MetricCard
          title="Total Memory"
          value={totalMB.toFixed(1)}
          unit="MB"
          status="good"
          description="Total allocated"
        />
        <MetricCard
          title="Memory Limit"
          value={limitMB.toFixed(1)}
          unit="MB"
          status="good"
          description="Browser limit"
        />
      </div>
      <div className="mt-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Memory Usage</span>
          <span>{usagePercent.toFixed(1)}%</span>
        </div>
        <Progress 
          value={usagePercent} 
          max={100}
          className="h-2"
        />
      </div>
    </div>
  )
})

MemorySection.displayName = 'MemorySection'

// Main performance dashboard component
export const PerformanceDashboard = memo<PerformanceDashboardProps>(({
  className = '',
  showDetails = false
}) => {
  const { coreWebVitals, summary, recordCustomMetric } = usePerformanceMonitoring()
  const { bundleStats, performanceMetrics } = useBundleAnalysis()
  const memoryInfo = useMemoryMonitor()
  const [isExpanded, setIsExpanded] = useState(showDetails)

  const handleExportReport = useCallback(() => {
    const report = {
      timestamp: new Date().toISOString(),
      coreWebVitals,
      bundleStats,
      performanceMetrics,
      memoryInfo,
      summary
    }

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `performance-report-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }, [coreWebVitals, bundleStats, performanceMetrics, memoryInfo, summary])

  const handleRefresh = useCallback(() => {
    recordCustomMetric('dashboard-refresh', Date.now())
    window.location.reload()
  }, [recordCustomMetric])

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Performance Dashboard</h1>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportReport}
          >
            Export Report
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Core Web Vitals */}
      {coreWebVitals && (
        <CoreWebVitalsSection coreWebVitals={coreWebVitals} />
      )}

      {/* Bundle Analysis */}
      {bundleStats && (
        <BundleAnalysisSection bundleStats={bundleStats} />
      )}

      {/* Memory Usage */}
      <MemorySection memoryInfo={memoryInfo} />

      {/* Detailed Metrics */}
      {isExpanded && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Detailed Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {performanceMetrics && (
              <>
                <MetricCard
                  title="Load Time"
                  value={performanceMetrics.loadTime}
                  unit="ms"
                  status="good"
                  description="Page load duration"
                />
                <MetricCard
                  title="Render Time"
                  value={performanceMetrics.renderTime}
                  unit="ms"
                  status="good"
                  description="First contentful paint"
                />
                <MetricCard
                  title="Cache Hit Rate"
                  value={(performanceMetrics.cacheHitRate * 100).toFixed(1)}
                  unit="%"
                  status="good"
                  description="Cache effectiveness"
                />
              </>
            )}
          </div>
        </div>
      )}

      {/* Performance Summary */}
      {summary && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold">Performance Summary</h3>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Metrics</h4>
                <ul className="space-y-1 text-sm text-gray-600">
                  <li>Total Metrics: {summary.totalMetrics}</li>
                  <li>Recent Metrics: {summary.recentMetrics}</li>
                  <li>Long Tasks: {summary.longTasks}</li>
                  <li>Layout Shifts: {summary.layoutShifts}</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Averages</h4>
                <ul className="space-y-1 text-sm text-gray-600">
                  <li>Load Time: {summary.averageLoadTime?.toFixed(1)}ms</li>
                  <li>Interaction Delay: {summary.averageInteractionDelay?.toFixed(1)}ms</li>
                </ul>
              </div>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
})

PerformanceDashboard.displayName = 'PerformanceDashboard'
