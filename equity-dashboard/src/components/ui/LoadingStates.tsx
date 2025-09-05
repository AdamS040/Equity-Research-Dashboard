import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { clsx } from 'clsx'
import { Skeleton, SkeletonCard, SkeletonChart, SkeletonTable } from './Skeleton'
import { Spinner } from './Spinner'

export interface LoadingStatesProps {
  loading: boolean
  children: React.ReactNode
  skeleton?: React.ReactNode
  spinner?: React.ReactNode
  delay?: number
  className?: string
}

/**
 * LoadingStates component that shows skeleton or spinner while loading
 * 
 * @example
 * ```tsx
 * <LoadingStates loading={isLoading}>
 *   <DataComponent />
 * </LoadingStates>
 * 
 * <LoadingStates 
 *   loading={isLoading} 
 *   skeleton={<SkeletonCard />}
 *   delay={300}
 * >
 *   <DataComponent />
 * </LoadingStates>
 * ```
 */
export const LoadingStates: React.FC<LoadingStatesProps> = ({
  loading,
  children,
  skeleton,
  spinner,
  delay = 0,
  className,
}) => {
  const [showLoading, setShowLoading] = React.useState(loading)

  React.useEffect(() => {
    if (loading) {
      const timer = setTimeout(() => setShowLoading(true), delay)
      return () => clearTimeout(timer)
    } else {
      setShowLoading(false)
    }
  }, [loading, delay])

  const defaultSkeleton = <SkeletonCard />
  const defaultSpinner = <Spinner variant="ring" centered text="Loading..." />

  return (
    <div className={className}>
      <AnimatePresence mode="wait">
        {showLoading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {skeleton || defaultSkeleton}
          </motion.div>
        ) : (
          <motion.div
            key="content"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Specialized loading components for different content types
export const ChartLoadingState: React.FC<{ loading: boolean; children: React.ReactNode }> = ({
  loading,
  children,
}) => (
  <LoadingStates
    loading={loading}
    skeleton={<SkeletonChart width="100%" height="300px" />}
    delay={200}
  >
    {children}
  </LoadingStates>
)

export const TableLoadingState: React.FC<{ loading: boolean; children: React.ReactNode }> = ({
  loading,
  children,
}) => (
  <LoadingStates
    loading={loading}
    skeleton={<SkeletonTable />}
    delay={150}
  >
    {children}
  </LoadingStates>
)

export const CardLoadingState: React.FC<{ loading: boolean; children: React.ReactNode }> = ({
  loading,
  children,
}) => (
  <LoadingStates
    loading={loading}
    skeleton={<SkeletonCard />}
    delay={100}
  >
    {children}
  </LoadingStates>
)

// Progressive loading component for charts
export const ProgressiveChartLoader: React.FC<{
  loading: boolean
  children: React.ReactNode
  stages?: Array<{ delay: number; component: React.ReactNode }>
}> = ({ loading, children, stages = [] }) => {
  const [currentStage, setCurrentStage] = React.useState(0)

  React.useEffect(() => {
    if (!loading) {
      setCurrentStage(0)
      return
    }

    const timers = stages.map((stage, index) =>
      setTimeout(() => setCurrentStage(index + 1), stage.delay)
    )

    return () => timers.forEach(clearTimeout)
  }, [loading, stages])

  if (!loading) {
    return <>{children}</>
  }

  const currentStageComponent = stages[currentStage]?.component || <SkeletonChart />

  return (
    <motion.div
      key={currentStage}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      {currentStageComponent}
    </motion.div>
  )
}

// Optimistic update wrapper
export const OptimisticWrapper: React.FC<{
  optimistic: boolean
  children: React.ReactNode
  fallback?: React.ReactNode
}> = ({ optimistic, children, fallback }) => {
  return (
    <AnimatePresence mode="wait">
      {optimistic ? (
        <motion.div
          key="optimistic"
          initial={{ opacity: 0.7, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="relative"
        >
          {children}
          <div className="absolute inset-0 bg-primary-100 bg-opacity-20 rounded pointer-events-none" />
        </motion.div>
      ) : (
        <motion.div
          key="normal"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          {fallback || children}
        </motion.div>
      )}
    </AnimatePresence>
  )
}
