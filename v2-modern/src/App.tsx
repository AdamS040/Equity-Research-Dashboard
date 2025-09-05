import { Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Suspense, lazy, useEffect } from 'react'
import { ErrorBoundary } from './components/ErrorBoundary'
import { AuthProvider } from './components/AuthProvider'
import { ProtectedRoute } from './components/ProtectedRoute'
import { LoginForm } from './components/LoginForm'
import { RegisterForm } from './components/RegisterForm'
import { Layout } from './components/Layout'
import { SkipLinks } from './components/SkipLinks'
import { Spinner } from './components/ui/Spinner'
import { createLazyComponent, routePreloader, lazyLoadMonitor } from './utils/lazy-loading'
import { LazyWrapper } from './components/optimized/LazyWrapper'
import { performanceMonitor } from './utils/performanceMonitor'
import { serviceWorkerManager } from './utils/serviceWorker'
import { 
  ThemeProvider, 
  UserPreferencesProvider, 
  AccessibilityProvider 
} from './components/ui'

// Enhanced lazy loading with retry mechanism and preloading
const Dashboard = createLazyComponent(() => import('./pages/Dashboard').then(module => ({ default: module.Dashboard })))
const Portfolio = createLazyComponent(() => import('./pages/Portfolio').then(module => ({ default: module.Portfolio })))
const Research = createLazyComponent(() => import('./pages/Research').then(module => ({ default: module.Research })))
const Analysis = createLazyComponent(() => import('./pages/Analysis').then(module => ({ default: module.Analysis })))
const StockAnalysis = createLazyComponent(() => import('./pages/StockAnalysis').then(module => ({ default: module.StockAnalysis })))
const Settings = createLazyComponent(() => import('./pages/Settings').then(module => ({ default: module.Settings })))

// Preload critical routes after initial load
const preloadCriticalRoutes = () => {
  // Preload most commonly used routes
  routePreloader.preloadRoute('/portfolio', () => import('./pages/Portfolio'))
  routePreloader.preloadRoute('/research', () => import('./pages/Research'))
}

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        // Don't retry on 401/403 errors
        if (error?.status === 401 || error?.status === 403) return false
        return failureCount < 3
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
})

// Enhanced loading component with performance monitoring
const PageLoader = ({ componentName }: { componentName?: string }) => {
  useEffect(() => {
    if (componentName) {
      lazyLoadMonitor.recordLoadStart(componentName)
    }
  }, [componentName])

  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center">
        <Spinner size="lg" />
        <p className="mt-4 text-neutral-600">Loading page...</p>
      </div>
    </div>
  )
}

// Enhanced route wrapper with performance monitoring
const ProtectedRouteWrapper = ({ 
  children, 
  componentName 
}: { 
  children: React.ReactNode
  componentName?: string 
}) => (
  <ProtectedRoute>
    <Layout>
      <LazyWrapper
        onLoadStart={() => componentName && lazyLoadMonitor.recordLoadStart(componentName)}
        onLoadComplete={() => componentName && lazyLoadMonitor.recordLoadComplete(componentName)}
        onError={(error) => componentName && lazyLoadMonitor.recordError(componentName)}
        fallback={<PageLoader componentName={componentName} />}
      >
        {children}
      </LazyWrapper>
    </Layout>
  </ProtectedRoute>
)

function App() {
  // Initialize performance monitoring and service worker
  useEffect(() => {
    // Initialize performance monitoring
    performanceMonitor.setEnabled(true)
    
    // Register service worker
    serviceWorkerManager.register()
    
    // Preload critical routes after initial render
    const timer = setTimeout(preloadCriticalRoutes, 2000) // Preload after 2 seconds
    
    return () => {
      clearTimeout(timer)
      performanceMonitor.cleanup()
    }
  }, [])

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <UserPreferencesProvider>
            <AccessibilityProvider>
              <AuthProvider>
                <div className="min-h-screen">
                  <SkipLinks 
                    links={[
                      { href: '#main-content', label: 'Skip to main content' },
                      { href: '#navigation', label: 'Skip to navigation' },
                      { href: '#sidebar', label: 'Skip to sidebar' }
                    ]} 
                  />
                  <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginForm />} />
              <Route path="/register" element={<RegisterForm />} />
              
              {/* Protected routes with enhanced lazy loading */}
              <Route
                path="/"
                element={
                  <ProtectedRouteWrapper componentName="Dashboard">
                    <Dashboard />
                  </ProtectedRouteWrapper>
                }
              />
              <Route
                path="/portfolio"
                element={
                  <ProtectedRouteWrapper componentName="Portfolio">
                    <Portfolio />
                  </ProtectedRouteWrapper>
                }
              />
              <Route
                path="/research"
                element={
                  <ProtectedRouteWrapper componentName="Research">
                    <Research />
                  </ProtectedRouteWrapper>
                }
              />
              <Route
                path="/analysis"
                element={
                  <ProtectedRouteWrapper componentName="Analysis">
                    <Analysis />
                  </ProtectedRouteWrapper>
                }
              />
              <Route
                path="/stock/:symbol"
                element={
                  <ProtectedRouteWrapper componentName="StockAnalysis">
                    <StockAnalysis />
                  </ProtectedRouteWrapper>
                }
              />
              <Route
                path="/settings"
                element={
                  <ProtectedRouteWrapper componentName="Settings">
                    <Settings />
                  </ProtectedRouteWrapper>
                }
              />
              
                    {/* Catch all route */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </div>
              </AuthProvider>
            </AccessibilityProvider>
          </UserPreferencesProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
