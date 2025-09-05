/**
 * Lazy Loading Components Index
 * 
 * Centralized exports for all lazy-loaded components
 */

export * from './LazyCharts'
export * from './LazyReports'

// Re-export lazy loading utilities
export { 
  createLazyComponent, 
  routePreloader, 
  lazyLoadMonitor,
  preloadComponent 
} from '../../utils/lazy-loading'

// Re-export LazyWrapper component
export { LazyWrapper } from '../optimized/LazyWrapper'
