import React from 'react'
import { motion, AnimatePresence, Variants } from 'framer-motion'
import { clsx } from 'clsx'

// Common animation variants
export const fadeInUp: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
}

export const fadeInScale: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
}

export const slideInFromLeft: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
}

export const slideInFromRight: Variants = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
}

export const staggerContainer: Variants = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
}

export const staggerItem: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
}

// Page transition wrapper
export interface PageTransitionProps {
  children: React.ReactNode
  className?: string
}

export const PageTransition: React.FC<PageTransitionProps> = ({ children, className }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ duration: 0.3, ease: 'easeInOut' }}
    className={className}
  >
    {children}
  </motion.div>
)

// Staggered list animation
export interface StaggeredListProps {
  children: React.ReactNode
  className?: string
  delay?: number
}

export const StaggeredList: React.FC<StaggeredListProps> = ({ 
  children, 
  className, 
  delay = 0.1 
}) => (
  <motion.div
    variants={staggerContainer}
    initial="initial"
    animate="animate"
    className={className}
  >
    {React.Children.map(children, (child, index) => (
      <motion.div
        key={index}
        variants={staggerItem}
        transition={{ delay: index * delay }}
      >
        {child}
      </motion.div>
    ))}
  </motion.div>
)

// Hover animations
export interface HoverScaleProps {
  children: React.ReactNode
  scale?: number
  className?: string
  whileHover?: any
  whileTap?: any
}

export const HoverScale: React.FC<HoverScaleProps> = ({ 
  children, 
  scale = 1.05, 
  className,
  whileHover,
  whileTap 
}) => (
  <motion.div
    whileHover={whileHover || { scale, transition: { duration: 0.2 } }}
    whileTap={whileTap || { scale: 0.95, transition: { duration: 0.1 } }}
    className={className}
  >
    {children}
  </motion.div>
)

// Loading pulse animation
export interface LoadingPulseProps {
  children: React.ReactNode
  className?: string
}

export const LoadingPulse: React.FC<LoadingPulseProps> = ({ children, className }) => (
  <motion.div
    animate={{ opacity: [0.5, 1, 0.5] }}
    transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
    className={className}
  >
    {children}
  </motion.div>
)

// Success/Error feedback animations
export interface FeedbackAnimationProps {
  children: React.ReactNode
  type: 'success' | 'error' | 'info'
  show: boolean
  className?: string
}

export const FeedbackAnimation: React.FC<FeedbackAnimationProps> = ({ 
  children, 
  type, 
  show, 
  className 
}) => {
  const getTypeStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-success-50 border-success-200 text-success-800'
      case 'error':
        return 'bg-danger-50 border-danger-200 text-danger-800'
      case 'info':
        return 'bg-primary-50 border-primary-200 text-primary-800'
      default:
        return 'bg-neutral-50 border-neutral-200 text-neutral-800'
    }
  }

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: -10 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className={clsx(
            'p-4 rounded-lg border',
            getTypeStyles(),
            className
          )}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Chart loading animation
export interface ChartLoadingAnimationProps {
  children: React.ReactNode
  loading: boolean
  className?: string
}

export const ChartLoadingAnimation: React.FC<ChartLoadingAnimationProps> = ({ 
  children, 
  loading, 
  className 
}) => (
  <motion.div
    animate={loading ? { opacity: 0.6 } : { opacity: 1 }}
    transition={{ duration: 0.3 }}
    className={className}
  >
    {children}
  </motion.div>
)

// Counter animation
export interface AnimatedCounterProps {
  value: number
  duration?: number
  className?: string
  prefix?: string
  suffix?: string
  decimals?: number
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
  value,
  duration = 1,
  className,
  prefix = '',
  suffix = '',
  decimals = 0,
}) => {
  const [displayValue, setDisplayValue] = React.useState(0)

  React.useEffect(() => {
    const startTime = Date.now()
    const startValue = displayValue
    const endValue = value

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / (duration * 1000), 1)
      
      // Easing function (ease-out)
      const easeOut = 1 - Math.pow(1 - progress, 3)
      
      const currentValue = startValue + (endValue - startValue) * easeOut
      setDisplayValue(currentValue)

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }, [value, duration, displayValue])

  return (
    <span className={className}>
      {prefix}{displayValue.toFixed(decimals)}{suffix}
    </span>
  )
}

// Gesture-based interactions for mobile
export interface SwipeableProps {
  children: React.ReactNode
  onSwipeLeft?: () => void
  onSwipeRight?: () => void
  onSwipeUp?: () => void
  onSwipeDown?: () => void
  threshold?: number
  className?: string
}

export const Swipeable: React.FC<SwipeableProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  threshold = 50,
  className,
}) => {
  const [dragStart, setDragStart] = React.useState<{ x: number; y: number } | null>(null)

  const handleDragStart = (event: any, info: any) => {
    setDragStart({ x: info.point.x, y: info.point.y })
  }

  const handleDragEnd = (event: any, info: any) => {
    if (!dragStart) return

    const deltaX = info.point.x - dragStart.x
    const deltaY = info.point.y - dragStart.y

    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      // Horizontal swipe
      if (Math.abs(deltaX) > threshold) {
        if (deltaX > 0 && onSwipeRight) {
          onSwipeRight()
        } else if (deltaX < 0 && onSwipeLeft) {
          onSwipeLeft()
        }
      }
    } else {
      // Vertical swipe
      if (Math.abs(deltaY) > threshold) {
        if (deltaY > 0 && onSwipeDown) {
          onSwipeDown()
        } else if (deltaY < 0 && onSwipeUp) {
          onSwipeUp()
        }
      }
    }

    setDragStart(null)
  }

  return (
    <motion.div
      drag
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragElastic={0.1}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      className={className}
    >
      {children}
    </motion.div>
  )
}
