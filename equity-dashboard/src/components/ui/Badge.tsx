import React, { forwardRef } from 'react'
import { clsx } from 'clsx'
import { BadgeProps } from '../../types/design-system'

/**
 * Badge component for status indicators and labels
 * 
 * @example
 * ```tsx
 * <Badge color="success" shape="pill">
 *   Active
 * </Badge>
 * 
 * <Badge color="danger" count={5} max={99} />
 * 
 * <Badge color="warning" dot />
 * ```
 */
export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      children,
      className,
      color = 'primary',
      shape = 'rounded',
      outlined = false,
      dot = false,
      max,
      count,
      size = 'base',
      ...props
    },
    ref
  ) => {
    // Determine what to display
    const displayContent = (() => {
      if (dot) {
        return null
      }
      
      if (count !== undefined) {
        if (max !== undefined && count > max) {
          return `${max}+`
        }
        return count.toString()
      }
      
      return children
    })()

    const badgeClasses = clsx(
      // Base styles
      'inline-flex items-center justify-center font-medium transition-colors duration-200',
      
      // Size variants
      {
        'h-4 w-4 text-xs': size === 'xs' && dot,
        'h-5 w-5 text-xs': size === 'sm' && dot,
        'h-6 w-6 text-xs': size === 'base' && dot,
        'h-7 w-7 text-sm': size === 'lg' && dot,
        'h-8 w-8 text-sm': size === 'xl' && dot,
        'h-10 w-10 text-base': size === '2xl' && dot,
        'h-12 w-12 text-lg': size === '3xl' && dot,
        'h-14 w-14 text-xl': size === '4xl' && dot,
        
        'px-1.5 py-0.5 text-xs min-w-[1.25rem]': size === 'xs' && !dot,
        'px-2 py-0.5 text-xs min-w-[1.5rem]': size === 'sm' && !dot,
        'px-2.5 py-0.5 text-sm min-w-[1.75rem]': size === 'base' && !dot,
        'px-3 py-1 text-sm min-w-[2rem]': size === 'lg' && !dot,
        'px-3.5 py-1 text-base min-w-[2.25rem]': size === 'xl' && !dot,
        'px-4 py-1.5 text-base min-w-[2.5rem]': size === '2xl' && !dot,
        'px-5 py-2 text-lg min-w-[3rem]': size === '3xl' && !dot,
        'px-6 py-2.5 text-xl min-w-[3.5rem]': size === '4xl' && !dot,
      },
      
      // Shape variants
      {
        'rounded': shape === 'rounded',
        'rounded-full': shape === 'pill',
        'rounded-none': shape === 'square',
      },
      
      // Color and variant combinations
      {
        // Primary colors
        'bg-primary-100 text-primary-800 border-primary-200': 
          color === 'primary' && !outlined && !dot,
        'bg-primary-600 text-white': 
          color === 'primary' && !outlined && dot,
        'border border-primary-500 text-primary-600 bg-transparent': 
          color === 'primary' && outlined,
        
        // Secondary colors
        'bg-secondary-100 text-secondary-800 border-secondary-200': 
          color === 'secondary' && !outlined && !dot,
        'bg-secondary-600 text-white': 
          color === 'secondary' && !outlined && dot,
        'border border-secondary-500 text-secondary-600 bg-transparent': 
          color === 'secondary' && outlined,
        
        // Success colors
        'bg-success-100 text-success-800 border-success-200': 
          color === 'success' && !outlined && !dot,
        'bg-success-600 text-white': 
          color === 'success' && !outlined && dot,
        'border border-success-500 text-success-600 bg-transparent': 
          color === 'success' && outlined,
        
        // Warning colors
        'bg-warning-100 text-warning-800 border-warning-200': 
          color === 'warning' && !outlined && !dot,
        'bg-warning-600 text-white': 
          color === 'warning' && !outlined && dot,
        'border border-warning-500 text-warning-600 bg-transparent': 
          color === 'warning' && outlined,
        
        // Danger colors
        'bg-danger-100 text-danger-800 border-danger-200': 
          color === 'danger' && !outlined && !dot,
        'bg-danger-600 text-white': 
          color === 'danger' && !outlined && dot,
        'border border-danger-500 text-danger-600 bg-transparent': 
          color === 'danger' && outlined,
        
        // Neutral colors
        'bg-neutral-100 text-neutral-800 border-neutral-200': 
          color === 'neutral' && !outlined && !dot,
        'bg-neutral-600 text-white': 
          color === 'neutral' && !outlined && dot,
        'border border-neutral-500 text-neutral-600 bg-transparent': 
          color === 'neutral' && outlined,
      },
      
      className
    )

    return (
      <span ref={ref} className={badgeClasses} {...props}>
        {displayContent}
      </span>
    )
  }
)

Badge.displayName = 'Badge'
