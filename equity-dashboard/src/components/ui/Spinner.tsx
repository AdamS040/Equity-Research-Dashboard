import React, { forwardRef } from 'react'
import { clsx } from 'clsx'
import { SpinnerProps } from '../../types/design-system'

/**
 * Spinner component for loading indicators
 * 
 * @example
 * ```tsx
 * <Spinner variant="dots" color="primary" size="lg" />
 * 
 * <Spinner variant="ring" text="Loading data..." centered />
 * ```
 */
export const Spinner = forwardRef<HTMLDivElement, SpinnerProps>(
  (
    {
      className,
      variant = 'dots',
      color = 'primary',
      size = 'base',
      centered = false,
      text,
      ...props
    },
    ref
  ) => {
    const sizeClasses = {
      xs: 'h-3 w-3',
      sm: 'h-4 w-4',
      base: 'h-6 w-6',
      lg: 'h-8 w-8',
      xl: 'h-10 w-10',
      '2xl': 'h-12 w-12',
      '3xl': 'h-16 w-16',
      '4xl': 'h-20 w-20',
    }

    const colorClasses = {
      primary: 'text-primary-600',
      secondary: 'text-secondary-600',
      success: 'text-success-600',
      warning: 'text-warning-600',
      danger: 'text-danger-600',
      neutral: 'text-neutral-600',
    }

    const containerClasses = clsx(
      'inline-flex flex-col items-center',
      {
        'justify-center min-h-[200px]': centered,
      },
      className
    )

    const spinnerClasses = clsx(
      sizeClasses[size],
      colorClasses[color],
      'animate-spin'
    )

    const textClasses = clsx(
      'mt-2 text-sm font-medium',
      colorClasses[color]
    )

    const renderSpinner = () => {
      switch (variant) {
        case 'dots':
          return (
            <div className="flex space-x-1">
              <div className={clsx('rounded-full bg-current animate-bounce', sizeClasses[size])} style={{ animationDelay: '0ms' }} />
              <div className={clsx('rounded-full bg-current animate-bounce', sizeClasses[size])} style={{ animationDelay: '150ms' }} />
              <div className={clsx('rounded-full bg-current animate-bounce', sizeClasses[size])} style={{ animationDelay: '300ms' }} />
            </div>
          )
        
        case 'pulse':
          return (
            <div className={clsx('rounded-full bg-current animate-pulse', sizeClasses[size])} />
          )
        
        case 'ring':
          return (
            <div className={clsx('relative', sizeClasses[size])}>
              <div className={clsx('absolute inset-0 rounded-full border-2 border-current opacity-25')} />
              <div className={clsx('absolute inset-0 rounded-full border-2 border-current border-t-transparent animate-spin')} />
            </div>
          )
        
        case 'bars':
          return (
            <div className="flex space-x-1 items-end">
              <div className={clsx('bg-current animate-pulse', 'w-1', {
                'h-2': size === 'xs',
                'h-3': size === 'sm',
                'h-4': size === 'base',
                'h-5': size === 'lg',
                'h-6': size === 'xl',
                'h-8': size === '2xl',
                'h-10': size === '3xl',
                'h-12': size === '4xl',
              })} style={{ animationDelay: '0ms' }} />
              <div className={clsx('bg-current animate-pulse', 'w-1', {
                'h-3': size === 'xs',
                'h-4': size === 'sm',
                'h-5': size === 'base',
                'h-6': size === 'lg',
                'h-7': size === 'xl',
                'h-9': size === '2xl',
                'h-11': size === '3xl',
                'h-13': size === '4xl',
              })} style={{ animationDelay: '150ms' }} />
              <div className={clsx('bg-current animate-pulse', 'w-1', {
                'h-2': size === 'xs',
                'h-3': size === 'sm',
                'h-4': size === 'base',
                'h-5': size === 'lg',
                'h-6': size === 'xl',
                'h-8': size === '2xl',
                'h-10': size === '3xl',
                'h-12': size === '4xl',
              })} style={{ animationDelay: '300ms' }} />
              <div className={clsx('bg-current animate-pulse', 'w-1', {
                'h-4': size === 'xs',
                'h-5': size === 'sm',
                'h-6': size === 'base',
                'h-7': size === 'lg',
                'h-8': size === 'xl',
                'h-10': size === '2xl',
                'h-12': size === '3xl',
                'h-14': size === '4xl',
              })} style={{ animationDelay: '450ms' }} />
            </div>
          )
        
        default:
          return (
            <svg
              className={spinnerClasses}
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          )
      }
    }

    return (
      <div ref={ref} className={containerClasses} {...props}>
        <div className={colorClasses[color]}>
          {renderSpinner()}
        </div>
        {text && (
          <div className={textClasses}>
            {text}
          </div>
        )}
      </div>
    )
  }
)

Spinner.displayName = 'Spinner'
