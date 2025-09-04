import { Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Suspense, lazy } from 'react'
import { ErrorBoundary } from './components/ErrorBoundary'
import { AuthProvider } from './components/AuthProvider'
import { ProtectedRoute } from './components/ProtectedRoute'
import { LoginForm } from './components/LoginForm'
import { RegisterForm } from './components/RegisterForm'
import { Layout } from './components/Layout'
import { SkipLinks } from './components/SkipLinks'
import { Spinner } from './components/ui/Spinner'

// Lazy load page components for code splitting
const Dashboard = lazy(() => import('./pages/Dashboard').then(module => ({ default: module.Dashboard })))
const Portfolio = lazy(() => import('./pages/Portfolio').then(module => ({ default: module.Portfolio })))
const Research = lazy(() => import('./pages/Research').then(module => ({ default: module.Research })))
const Analysis = lazy(() => import('./pages/Analysis').then(module => ({ default: module.Analysis })))
const StockAnalysis = lazy(() => import('./pages/StockAnalysis').then(module => ({ default: module.StockAnalysis })))
const Settings = lazy(() => import('./pages/Settings').then(module => ({ default: module.Settings })))

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

// Loading component for Suspense fallback
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[400px]">
    <div className="text-center">
      <Spinner size="lg" />
      <p className="mt-4 text-neutral-600">Loading page...</p>
    </div>
  </div>
)

// Route wrapper component for protected routes with lazy loading
const ProtectedRouteWrapper = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute>
    <Layout>
      <Suspense fallback={<PageLoader />}>
        {children}
      </Suspense>
    </Layout>
  </ProtectedRoute>
)

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <div className="min-h-screen bg-neutral-50">
            <SkipLinks />
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginForm />} />
              <Route path="/register" element={<RegisterForm />} />
              
              {/* Protected routes with lazy loading */}
              <Route
                path="/"
                element={
                  <ProtectedRouteWrapper>
                    <Dashboard />
                  </ProtectedRouteWrapper>
                }
              />
              <Route
                path="/portfolio"
                element={
                  <ProtectedRouteWrapper>
                    <Portfolio />
                  </ProtectedRouteWrapper>
                }
              />
              <Route
                path="/research"
                element={
                  <ProtectedRouteWrapper>
                    <Research />
                  </ProtectedRouteWrapper>
                }
              />
              <Route
                path="/analysis"
                element={
                  <ProtectedRouteWrapper>
                    <Analysis />
                  </ProtectedRouteWrapper>
                }
              />
              <Route
                path="/stock/:symbol"
                element={
                  <ProtectedRouteWrapper>
                    <StockAnalysis />
                  </ProtectedRouteWrapper>
                }
              />
              <Route
                path="/settings"
                element={
                  <ProtectedRouteWrapper>
                    <Settings />
                  </ProtectedRouteWrapper>
                }
              />
              
              {/* Catch all route */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
