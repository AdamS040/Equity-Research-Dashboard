import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence, PanInfo } from 'framer-motion'
import { clsx } from 'clsx'
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline'

// Pull to refresh component
export interface PullToRefreshProps {
  onRefresh: () => Promise<void>
  children: React.ReactNode
  threshold?: number
  className?: string
}

export const PullToRefresh: React.FC<PullToRefreshProps> = ({
  onRefresh,
  children,
  threshold = 80,
  className,
}) => {
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [pullDistance, setPullDistance] = useState(0)
  const [isPulling, setIsPulling] = useState(false)

  const handleDrag = (event: any, info: PanInfo) => {
    if (info.offset.y > 0 && window.scrollY === 0) {
      const distance = Math.min(info.offset.y, threshold * 1.5)
      setPullDistance(distance)
      setIsPulling(distance > 0)
    }
  }

  const handleDragEnd = async (event: any, info: PanInfo) => {
    if (info.offset.y > threshold && window.scrollY === 0) {
      setIsRefreshing(true)
      try {
        await onRefresh()
      } finally {
        setIsRefreshing(false)
      }
    }
    setPullDistance(0)
    setIsPulling(false)
  }

  const progress = Math.min(pullDistance / threshold, 1)

  return (
    <div className={clsx('relative', className)}>
      <AnimatePresence>
        {isPulling && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute top-0 left-0 right-0 z-10 flex justify-center items-center py-4"
            style={{ transform: `translateY(${Math.min(pullDistance, threshold)}px)` }}
          >
            <div className="flex flex-col items-center space-y-2">
              <motion.div
                animate={{ rotate: progress * 360 }}
                className="w-6 h-6 border-2 border-primary-600 border-t-transparent rounded-full"
              />
              <span className="text-sm text-primary-600 font-medium">
                {progress >= 1 ? 'Release to refresh' : 'Pull to refresh'}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        drag="y"
        dragConstraints={{ top: 0, bottom: 0 }}
        dragElastic={0.1}
        onDrag={handleDrag}
        onDragEnd={handleDragEnd}
        animate={{ y: isRefreshing ? 60 : 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        {children}
      </motion.div>
    </div>
  )
}

// Swipeable card component
export interface SwipeableCardProps {
  children: React.ReactNode
  onSwipeLeft?: () => void
  onSwipeRight?: () => void
  leftAction?: React.ReactNode
  rightAction?: React.ReactNode
  threshold?: number
  className?: string
}

export const SwipeableCard: React.FC<SwipeableCardProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  leftAction,
  rightAction,
  threshold = 100,
  className,
}) => {
  const [dragX, setDragX] = useState(0)
  const [isDragging, setIsDragging] = useState(false)

  const handleDrag = (event: any, info: PanInfo) => {
    setDragX(info.offset.x)
    setIsDragging(true)
  }

  const handleDragEnd = (event: any, info: PanInfo) => {
    if (Math.abs(info.offset.x) > threshold) {
      if (info.offset.x > 0 && onSwipeRight) {
        onSwipeRight()
      } else if (info.offset.x < 0 && onSwipeLeft) {
        onSwipeLeft()
      }
    }
    setDragX(0)
    setIsDragging(false)
  }

  return (
    <div className={clsx('relative overflow-hidden', className)}>
      {/* Background actions */}
      <div className="absolute inset-0 flex">
        {leftAction && (
          <div className="flex-1 bg-danger-500 flex items-center justify-end pr-4">
            {leftAction}
          </div>
        )}
        {rightAction && (
          <div className="flex-1 bg-success-500 flex items-center justify-start pl-4">
            {rightAction}
          </div>
        )}
      </div>

      {/* Card content */}
      <motion.div
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        dragElastic={0.1}
        onDrag={handleDrag}
        onDragEnd={handleDragEnd}
        animate={{ x: dragX }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className="relative bg-white dark:bg-neutral-800 shadow-sm"
        style={{ zIndex: 1 }}
      >
        {children}
      </motion.div>
    </div>
  )
}

// Bottom sheet component
export interface BottomSheetProps {
  isOpen: boolean
  onClose: () => void
  children: React.ReactNode
  title?: string
  className?: string
}

export const BottomSheet: React.FC<BottomSheetProps> = ({
  isOpen,
  onClose,
  children,
  title,
  className,
}) => {
  const [dragY, setDragY] = useState(0)
  const [isDragging, setIsDragging] = useState(false)

  const handleDrag = (event: any, info: PanInfo) => {
    if (info.offset.y > 0) {
      setDragY(info.offset.y)
      setIsDragging(true)
    }
  }

  const handleDragEnd = (event: any, info: PanInfo) => {
    if (info.offset.y > 100) {
      onClose()
    }
    setDragY(0)
    setIsDragging(false)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
          />

          {/* Bottom sheet */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: isDragging ? dragY : 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={{ top: 0, bottom: 0.2 }}
            onDrag={handleDrag}
            onDragEnd={handleDragEnd}
            className={clsx(
              'fixed bottom-0 left-0 right-0 bg-white dark:bg-neutral-800 rounded-t-xl shadow-xl z-50',
              'max-h-[80vh] overflow-hidden',
              className
            )}
          >
            {/* Handle */}
            <div className="flex justify-center py-3">
              <div className="w-12 h-1 bg-neutral-300 dark:bg-neutral-600 rounded-full" />
            </div>

            {/* Header */}
            {title && (
              <div className="px-4 pb-4 border-b border-neutral-200 dark:border-neutral-700">
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
                  {title}
                </h3>
              </div>
            )}

            {/* Content */}
            <div className="px-4 py-4 overflow-y-auto max-h-[calc(80vh-80px)]">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// Collapsible section component
export interface CollapsibleSectionProps {
  title: string
  children: React.ReactNode
  defaultOpen?: boolean
  className?: string
}

export const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  title,
  children,
  defaultOpen = false,
  className,
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className={clsx('border-b border-neutral-200 dark:border-neutral-700', className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between py-4 text-left"
      >
        <span className="font-medium text-neutral-900 dark:text-neutral-100">
          {title}
        </span>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDownIcon className="w-5 h-5 text-neutral-500" />
        </motion.div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="pb-4">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Touch-friendly button
export interface TouchButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'danger' | 'success'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  className?: string
}

export const TouchButton: React.FC<TouchButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  className,
  ...props
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'primary':
        return 'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800'
      case 'secondary':
        return 'bg-neutral-200 text-neutral-900 hover:bg-neutral-300 active:bg-neutral-400 dark:bg-neutral-700 dark:text-neutral-100 dark:hover:bg-neutral-600'
      case 'danger':
        return 'bg-danger-600 text-white hover:bg-danger-700 active:bg-danger-800'
      case 'success':
        return 'bg-success-600 text-white hover:bg-success-700 active:bg-success-800'
      default:
        return 'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800'
    }
  }

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-3 py-2 text-sm'
      case 'lg':
        return 'px-6 py-4 text-lg'
      default:
        return 'px-4 py-3 text-base'
    }
  }

  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      transition={{ duration: 0.1 }}
      className={clsx(
        'rounded-lg font-medium transition-colors duration-200',
        'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        getVariantClasses(),
        getSizeClasses(),
        {
          'w-full': fullWidth,
        },
        className
      )}
      {...props}
    >
      {children}
    </motion.button>
  )
}

// Mobile-optimized input
export interface MobileInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  className?: string
}

export const MobileInput: React.FC<MobileInputProps> = ({
  label,
  error,
  className,
  ...props
}) => {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300">
          {label}
        </label>
      )}
      <input
        {...props}
        className={clsx(
          'w-full px-4 py-3 text-base rounded-lg border border-neutral-300 dark:border-neutral-600',
          'bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
          'placeholder-neutral-500 dark:placeholder-neutral-400',
          {
            'border-danger-500 focus:ring-danger-500': error,
          },
          className
        )}
      />
      {error && (
        <p className="text-sm text-danger-600">{error}</p>
      )}
    </div>
  )
}

// Mobile navigation tabs
export interface MobileTabsProps {
  tabs: Array<{ id: string; label: string; icon?: React.ReactNode }>
  activeTab: string
  onTabChange: (tabId: string) => void
  className?: string
}

export const MobileTabs: React.FC<MobileTabsProps> = ({
  tabs,
  activeTab,
  onTabChange,
  className,
}) => {
  return (
    <div className={clsx('flex bg-neutral-100 dark:bg-neutral-800 rounded-lg p-1', className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={clsx(
            'flex-1 flex items-center justify-center space-x-2 py-2 px-3 rounded-md text-sm font-medium transition-colors',
            {
              'bg-white dark:bg-neutral-700 text-primary-600 dark:text-primary-400 shadow-sm': 
                activeTab === tab.id,
              'text-neutral-600 dark:text-neutral-400': activeTab !== tab.id,
            }
          )}
        >
          {tab.icon && <span>{tab.icon}</span>}
          <span>{tab.label}</span>
        </button>
      ))}
    </div>
  )
}
