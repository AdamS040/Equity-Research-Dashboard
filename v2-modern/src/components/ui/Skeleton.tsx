import React from 'react'
import { clsx } from 'clsx'
import { motion } from 'framer-motion'

export interface SkeletonProps {
  className?: string
  variant?: 'text' | 'rectangular' | 'circular' | 'card' | 'chart' | 'table'
  width?: string | number
  height?: string | number
  lines?: number
  animated?: boolean
  children?: React.ReactNode
}

/**
 * Skeleton component for loading states
 * 
 * @example
 * ```tsx
 * <Skeleton variant="text" lines={3} />
 * <Skeleton variant="card" width="300px" height="200px" />
 * <Skeleton variant="chart" />
 * ```
 */
export const Skeleton: React.FC<SkeletonProps> = ({
  className,
  variant = 'rectangular',
  width,
  height,
  lines = 1,
  animated = true,
  children,
}) => {
  const baseClasses = clsx(
    'bg-neutral-200 dark:bg-neutral-700',
    {
      'animate-pulse': animated,
    },
    className
  )

  const getVariantClasses = () => {
    switch (variant) {
      case 'text':
        return 'h-4 rounded'
      case 'circular':
        return 'rounded-full'
      case 'card':
        return 'rounded-lg'
      case 'chart':
        return 'rounded-lg'
      case 'table':
        return 'rounded'
      default:
        return 'rounded'
    }
  }

  const getVariantStyles = () => {
    const styles: React.CSSProperties = {}
    
    if (width) {
      styles.width = typeof width === 'number' ? `${width}px` : width
    }
    
    if (height) {
      styles.height = typeof height === 'number' ? `${height}px` : height
    }

    return styles
  }

  const renderSkeleton = () => {
    if (variant === 'text' && lines > 1) {
      return (
        <div className="space-y-2">
          {Array.from({ length: lines }).map((_, index) => (
            <div
              key={index}
              className={clsx(baseClasses, getVariantClasses())}
              style={{
                ...getVariantStyles(),
                width: index === lines - 1 ? '75%' : width || '100%',
              }}
            />
          ))}
        </div>
      )
    }

    if (variant === 'card') {
      return (
        <div className={clsx(baseClasses, 'p-4 space-y-3')} style={getVariantStyles()}>
          <div className={clsx(baseClasses, 'h-4 w-3/4 rounded')} />
          <div className={clsx(baseClasses, 'h-3 w-1/2 rounded')} />
          <div className={clsx(baseClasses, 'h-3 w-2/3 rounded')} />
          <div className="flex justify-between items-center mt-4">
            <div className={clsx(baseClasses, 'h-6 w-16 rounded')} />
            <div className={clsx(baseClasses, 'h-4 w-20 rounded')} />
          </div>
        </div>
      )
    }

    if (variant === 'chart') {
      return (
        <div className={clsx(baseClasses, 'p-4')} style={getVariantStyles()}>
          <div className="flex justify-between items-center mb-4">
            <div className={clsx(baseClasses, 'h-4 w-32 rounded')} />
            <div className={clsx(baseClasses, 'h-4 w-20 rounded')} />
          </div>
          <div className="space-y-2">
            {Array.from({ length: 8 }).map((_, index) => (
              <div
                key={index}
                className={clsx(baseClasses, 'h-2 rounded')}
                style={{
                  width: `${Math.random() * 40 + 30}%`,
                }}
              />
            ))}
          </div>
        </div>
      )
    }

    if (variant === 'table') {
      return (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, rowIndex) => (
            <div key={rowIndex} className="flex space-x-4">
              {Array.from({ length: 4 }).map((_, colIndex) => (
                <div
                  key={colIndex}
                  className={clsx(baseClasses, 'h-4 rounded flex-1')}
                />
              ))}
            </div>
          ))}
        </div>
      )
    }

    return (
      <div
        className={clsx(baseClasses, getVariantClasses())}
        style={getVariantStyles()}
      />
    )
  }

  if (animated) {
    return (
      <motion.div
        initial={{ opacity: 0.6 }}
        animate={{ opacity: [0.6, 1, 0.6] }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        {renderSkeleton()}
      </motion.div>
    )
  }

  return renderSkeleton()
}

// Pre-built skeleton components for common use cases
export const SkeletonCard: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton variant="card" {...props} />
)

export const SkeletonText: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton variant="text" {...props} />
)

export const SkeletonChart: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton variant="chart" {...props} />
)

export const SkeletonTable: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton variant="table" {...props} />
)

export const SkeletonAvatar: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton variant="circular" width={40} height={40} {...props} />
)
