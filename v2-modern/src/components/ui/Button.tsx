import React, { forwardRef } from 'react'
import { clsx } from 'clsx'
import { ButtonProps } from '../../types/design-system'

/**
 * Button component with multiple variants and states
 * 
 * @example
 * ```tsx
 * <Button variant="solid" color="primary" size="md">
 *   Click me
 * </Button>
 * 
 * <Button variant="outline" color="secondary" loading>
 *   Loading...
 * </Button>
 * ```
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      className,
      variant = 'solid',
      color = 'primary',
      size = 'base',
      disabled = false,
      loading = false,
      fullWidth = false,
      leftIcon,
      rightIcon,
      loadingText,
      onClick,
      type = 'button',
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading

    const baseClasses = clsx(
      // Base styles
      'inline-flex items-center justify-center font-medium transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'relative overflow-hidden',
      
      // Size variants
      {
        'px-2 py-1 text-xs rounded': size === 'xs',
        'px-3 py-1.5 text-sm rounded-md': size === 'sm',
        'px-4 py-2 text-base rounded-lg': size === 'base',
        'px-5 py-2.5 text-lg rounded-lg': size === 'lg',
        'px-6 py-3 text-xl rounded-xl': size === 'xl',
        'px-8 py-4 text-2xl rounded-xl': size === '2xl',
        'px-10 py-5 text-3xl rounded-2xl': size === '3xl',
        'px-12 py-6 text-4xl rounded-2xl': size === '4xl',
      },
      
      // Width
      {
        'w-full': fullWidth,
      },
      
      // Variant and color combinations
      {
        // Solid variants
        'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500': 
          variant === 'solid' && color === 'primary',
        'bg-secondary-600 text-white hover:bg-secondary-700 focus:ring-secondary-500': 
          variant === 'solid' && color === 'secondary',
        'bg-success-600 text-white hover:bg-success-700 focus:ring-success-500': 
          variant === 'solid' && color === 'success',
        'bg-warning-600 text-white hover:bg-warning-700 focus:ring-warning-500': 
          variant === 'solid' && color === 'warning',
        'bg-danger-600 text-white hover:bg-danger-700 focus:ring-danger-500': 
          variant === 'solid' && color === 'danger',
        'bg-neutral-600 text-white hover:bg-neutral-700 focus:ring-neutral-500': 
          variant === 'solid' && color === 'neutral',
        
        // Outline variants
        'border-2 border-primary-600 text-primary-600 bg-transparent hover:bg-primary-600 hover:text-white focus:ring-primary-500': 
          variant === 'outline' && color === 'primary',
        'border-2 border-secondary-600 text-secondary-600 bg-transparent hover:bg-secondary-600 hover:text-white focus:ring-secondary-500': 
          variant === 'outline' && color === 'secondary',
        'border-2 border-success-600 text-success-600 bg-transparent hover:bg-success-600 hover:text-white focus:ring-success-500': 
          variant === 'outline' && color === 'success',
        'border-2 border-warning-600 text-warning-600 bg-transparent hover:bg-warning-600 hover:text-white focus:ring-warning-500': 
          variant === 'outline' && color === 'warning',
        'border-2 border-danger-600 text-danger-600 bg-transparent hover:bg-danger-600 hover:text-white focus:ring-danger-500': 
          variant === 'outline' && color === 'danger',
        'border-2 border-neutral-600 text-neutral-600 bg-transparent hover:bg-neutral-600 hover:text-white focus:ring-neutral-500': 
          variant === 'outline' && color === 'neutral',
        
        // Ghost variants
        'text-primary-600 bg-transparent hover:bg-primary-50 focus:ring-primary-500': 
          variant === 'ghost' && color === 'primary',
        'text-secondary-600 bg-transparent hover:bg-secondary-50 focus:ring-secondary-500': 
          variant === 'ghost' && color === 'secondary',
        'text-success-600 bg-transparent hover:bg-success-50 focus:ring-success-500': 
          variant === 'ghost' && color === 'success',
        'text-warning-600 bg-transparent hover:bg-warning-50 focus:ring-warning-500': 
          variant === 'ghost' && color === 'warning',
        'text-danger-600 bg-transparent hover:bg-danger-50 focus:ring-danger-500': 
          variant === 'ghost' && color === 'danger',
        'text-neutral-600 bg-transparent hover:bg-neutral-50 focus:ring-neutral-500': 
          variant === 'ghost' && color === 'neutral',
        
        // Link variants
        'text-primary-600 bg-transparent hover:text-primary-700 hover:underline focus:ring-primary-500 p-0': 
          variant === 'link' && color === 'primary',
        'text-secondary-600 bg-transparent hover:text-secondary-700 hover:underline focus:ring-secondary-500 p-0': 
          variant === 'link' && color === 'secondary',
        'text-success-600 bg-transparent hover:text-success-700 hover:underline focus:ring-success-500 p-0': 
          variant === 'link' && color === 'success',
        'text-warning-600 bg-transparent hover:text-warning-700 hover:underline focus:ring-warning-500 p-0': 
          variant === 'link' && color === 'warning',
        'text-danger-600 bg-transparent hover:text-danger-700 hover:underline focus:ring-danger-500 p-0': 
          variant === 'link' && color === 'danger',
        'text-neutral-600 bg-transparent hover:text-neutral-700 hover:underline focus:ring-neutral-500 p-0': 
          variant === 'link' && color === 'neutral',
      },
      
      className
    )

    const handleClick = () => {
      if (!isDisabled && onClick) {
        onClick()
      }
    }

    return (
      <button
        ref={ref}
        type={type}
        className={baseClasses}
        disabled={isDisabled}
        onClick={handleClick}
        {...props}
      >
        {/* Loading spinner */}
        {loading && (
          <svg
            className={clsx(
              'animate-spin -ml-1 mr-2',
              {
                'h-3 w-3': size === 'xs',
                'h-4 w-4': size === 'sm',
                'h-5 w-5': size === 'base',
                'h-6 w-6': size === 'lg',
                'h-7 w-7': size === 'xl',
                'h-8 w-8': size === '2xl',
                'h-9 w-9': size === '3xl',
                'h-10 w-10': size === '4xl',
              }
            )}
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
        )}
        
        {/* Left icon */}
        {!loading && leftIcon && (
          <span className={clsx('mr-2', { 'mr-1': size === 'xs' })}>
            {leftIcon}
          </span>
        )}
        
        {/* Button content */}
        <span className={loading ? 'opacity-0' : 'opacity-100'}>
          {loading && loadingText ? loadingText : children}
        </span>
        
        {/* Right icon */}
        {!loading && rightIcon && (
          <span className={clsx('ml-2', { 'ml-1': size === 'xs' })}>
            {rightIcon}
          </span>
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'
