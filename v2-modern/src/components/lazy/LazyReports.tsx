/**
 * Lazy Loading Report Components
 * 
 * Provides optimized lazy loading for heavy report components
 * with virtualization and progressive loading
 */

import React, { Suspense, lazy, useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { createLazyComponent } from '../../utils/lazy-loading'
import { LazyWrapper } from '../optimized/LazyWrapper'

// Lazy load heavy report components
const ReportGenerator = createLazyComponent(() => import('../reports/ReportGenerator'))
const ReportBuilder = createLazyComponent(() => import('../reports/ReportBuilder'))
const ReportViewer = createLazyComponent(() => import('../reports/ReportViewer'))
const ReportTemplates = createLazyComponent(() => import('../reports/ReportTemplates'))
const ReportExporter = createLazyComponent(() => import('../reports/ReportExporter'))
const ReportSharing = createLazyComponent(() => import('../reports/ReportSharing'))

// Report loading fallback
const ReportFallback = ({ height = 400, message = 'Loading report...' }: { 
  height?: number
  message?: string 
}) => (
  <div 
    className="flex items-center justify-center bg-gray-50 border border-gray-200 rounded-lg"
    style={{ height: `${height}px` }}
  >
    <div className="text-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      <p className="mt-2 text-sm text-gray-600">{message}</p>
    </div>
  </div>
)

// Virtualized list for large report lists
interface VirtualizedReportListProps {
  items: any[]
  itemHeight: number
  containerHeight: number
  renderItem: (item: any, index: number) => React.ReactNode
  className?: string
}

export const VirtualizedReportList: React.FC<VirtualizedReportListProps> = ({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  className = ''
}) => {
  const [scrollTop, setScrollTop] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)

  const visibleStart = Math.floor(scrollTop / itemHeight)
  const visibleEnd = Math.min(
    visibleStart + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  )

  const visibleItems = useMemo(() => {
    return items.slice(visibleStart, visibleEnd).map((item, index) => ({
      item,
      index: visibleStart + index
    }))
  }, [items, visibleStart, visibleEnd])

  const totalHeight = items.length * itemHeight
  const offsetY = visibleStart * itemHeight

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop)
  }, [])

  return (
    <div
      ref={containerRef}
      className={`overflow-auto ${className}`}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map(({ item, index }) => (
            <div key={index} style={{ height: itemHeight }}>
              {renderItem(item, index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Progressive loading for report content
interface ProgressiveReportLoaderProps {
  reportId: string
  onLoadComplete?: () => void
  height?: number
}

export const ProgressiveReportLoader: React.FC<ProgressiveReportLoaderProps> = ({
  reportId,
  onLoadComplete,
  height = 400
}) => {
  const [loadingStage, setLoadingStage] = useState<'metadata' | 'content' | 'charts' | 'complete'>('metadata')
  const [loadedSections, setLoadedSections] = useState<Set<string>>(new Set())

  useEffect(() => {
    const loadProgressively = async () => {
      // Stage 1: Load metadata
      setLoadingStage('metadata')
      await new Promise(resolve => setTimeout(resolve, 100))
      setLoadedSections(prev => new Set([...prev, 'metadata']))

      // Stage 2: Load content
      setLoadingStage('content')
      await new Promise(resolve => setTimeout(resolve, 200))
      setLoadedSections(prev => new Set([...prev, 'content']))

      // Stage 3: Load charts
      setLoadingStage('charts')
      await new Promise(resolve => setTimeout(resolve, 300))
      setLoadedSections(prev => new Set([...prev, 'charts']))

      // Complete
      setLoadingStage('complete')
      onLoadComplete?.()
    }

    loadProgressively()
  }, [reportId, onLoadComplete])

  const getLoadingMessage = () => {
    switch (loadingStage) {
      case 'metadata': return 'Loading report metadata...'
      case 'content': return 'Loading report content...'
      case 'charts': return 'Loading charts and visualizations...'
      case 'complete': return 'Report loaded successfully!'
      default: return 'Loading report...'
    }
  }

  return (
    <div 
      className="flex items-center justify-center bg-gray-50 border border-gray-200 rounded-lg"
      style={{ height: `${height}px` }}
    >
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-2 text-sm text-gray-600">{getLoadingMessage()}</p>
        <div className="mt-4 w-48 bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ 
              width: `${(loadedSections.size / 3) * 100}%` 
            }}
          />
        </div>
      </div>
    </div>
  )
}

// Lazy Report Components
export const LazyReportGenerator: React.FC<any> = (props) => (
  <LazyWrapper fallback={<ReportFallback height={500} message="Loading report generator..." />}>
    <ReportGenerator {...props} />
  </LazyWrapper>
)

export const LazyReportBuilder: React.FC<any> = (props) => (
  <LazyWrapper fallback={<ReportFallback height={600} message="Loading report builder..." />}>
    <ReportBuilder {...props} />
  </LazyWrapper>
)

export const LazyReportViewer: React.FC<any> = (props) => (
  <LazyWrapper fallback={<ProgressiveReportLoader reportId={props.reportId} height={500} />}>
    <ReportViewer {...props} />
  </LazyWrapper>
)

export const LazyReportTemplates: React.FC<any> = (props) => (
  <LazyWrapper fallback={<ReportFallback height={400} message="Loading templates..." />}>
    <ReportTemplates {...props} />
  </LazyWrapper>
)

export const LazyReportExporter: React.FC<any> = (props) => (
  <LazyWrapper fallback={<ReportFallback height={300} message="Loading exporter..." />}>
    <ReportExporter {...props} />
  </LazyWrapper>
)

export const LazyReportSharing: React.FC<any> = (props) => (
  <LazyWrapper fallback={<ReportFallback height={300} message="Loading sharing options..." />}>
    <ReportSharing {...props} />
  </LazyWrapper>
)

// Report preloader utility
export const preloadReports = () => {
  // Preload commonly used report components
  import('../reports/ReportGenerator').catch(() => {})
  import('../reports/ReportViewer').catch(() => {})
  import('../reports/ReportTemplates').catch(() => {})
}

// Export all lazy components
export {
  ReportGenerator,
  ReportBuilder,
  ReportViewer,
  ReportTemplates,
  ReportExporter,
  ReportSharing
}
