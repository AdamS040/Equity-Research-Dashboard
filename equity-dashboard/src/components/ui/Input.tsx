import React, { forwardRef, useState } from 'react'
import { clsx } from 'clsx'
import { InputProps } from '../../types/design-system'

/**
 * Input component with validation states and icons
 * 
 * @example
 * ```tsx
 * <Input
 *   label="Email"
 *   type="email"
 *   placeholder="Enter your email"
 *   state="error"
 *   errorMessage="Please enter a valid email"
 * />
 * 
 * <Input
 *   type="search"
 *   placeholder="Search stocks..."
 *   leftIcon={<SearchIcon />}
 *   clearable
 * />
 * ```
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type = 'text',
      label,
      helperText,
      errorMessage,
      state = 'default',
      placeholder,
      required = false,
      disabled = false,
      leftIcon,
      rightIcon,
      clearable = false,
      onChange,
      onClear,
      size = 'base',
      value,
      ...props
    },
    ref
  ) => {
    const [internalValue, setInternalValue] = useState(value || '')
    const currentValue = value !== undefined ? value : internalValue

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value
      if (value === undefined) {
        setInternalValue(newValue)
      }
      if (onChange) {
        onChange(newValue)
      }
    }

    const handleClear = () => {
      if (value === undefined) {
        setInternalValue('')
      }
      if (onClear) {
        onClear()
      }
      if (onChange) {
        onChange('')
      }
    }

    const inputClasses = clsx(
      // Base styles
      'w-full border rounded-lg transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-0',
      'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-neutral-50',
      'placeholder:text-neutral-400',
      
      // Size variants
      {
        'px-2 py-1 text-xs': size === 'xs',
        'px-3 py-1.5 text-sm': size === 'sm',
        'px-3 py-2 text-base': size === 'base',
        'px-4 py-2.5 text-lg': size === 'lg',
        'px-4 py-3 text-xl': size === 'xl',
        'px-5 py-3.5 text-2xl': size === '2xl',
        'px-6 py-4 text-3xl': size === '3xl',
        'px-6 py-5 text-4xl': size === '4xl',
      },
      
      // Icon padding adjustments
      {
        'pl-8': leftIcon && size === 'xs',
        'pl-9': leftIcon && size === 'sm',
        'pl-10': leftIcon && (size === 'base' || size === 'lg'),
        'pl-12': leftIcon && size === 'xl',
        'pl-14': leftIcon && size === '2xl',
        'pl-16': leftIcon && size === '3xl',
        'pl-20': leftIcon && size === '4xl',
      },
      {
        'pr-8': (rightIcon || clearable) && size === 'xs',
        'pr-9': (rightIcon || clearable) && size === 'sm',
        'pr-10': (rightIcon || clearable) && (size === 'base' || size === 'lg'),
        'pr-12': (rightIcon || clearable) && size === 'xl',
        'pr-14': (rightIcon || clearable) && size === '2xl',
        'pr-16': (rightIcon || clearable) && size === '3xl',
        'pr-20': (rightIcon || clearable) && size === '4xl',
      },
      
      // State variants
      {
        'border-neutral-300 focus:ring-primary-500 focus:border-primary-500': 
          state === 'default',
        'border-danger-500 focus:ring-danger-500 focus:border-danger-500': 
          state === 'error',
        'border-success-500 focus:ring-success-500 focus:border-success-500': 
          state === 'success',
        'border-warning-500 focus:ring-warning-500 focus:border-warning-500': 
          state === 'warning',
      },
      
      className
    )

    const labelClasses = clsx(
      'block text-sm font-medium mb-1',
      {
        'text-neutral-700': state === 'default',
        'text-danger-600': state === 'error',
        'text-success-600': state === 'success',
        'text-warning-600': state === 'warning',
      }
    )

    const helperTextClasses = clsx(
      'text-xs mt-1',
      {
        'text-neutral-500': state === 'default',
        'text-danger-600': state === 'error',
        'text-success-600': state === 'success',
        'text-warning-600': state === 'warning',
      }
    )

    const iconSizeClasses = {
      xs: 'h-3 w-3',
      sm: 'h-4 w-4',
      base: 'h-4 w-4',
      lg: 'h-5 w-5',
      xl: 'h-5 w-5',
      '2xl': 'h-6 w-6',
      '3xl': 'h-7 w-7',
      '4xl': 'h-8 w-8',
    }

    return (
      <div className="w-full">
        {/* Label */}
        {label && (
          <label className={labelClasses}>
            {label}
            {required && <span className="text-danger-500 ml-1">*</span>}
          </label>
        )}
        
        {/* Input container */}
        <div className="relative">
          {/* Left icon */}
          {leftIcon && (
            <div className={clsx(
              'absolute left-0 top-1/2 transform -translate-y-1/2 flex items-center',
              {
                'pl-2': size === 'xs',
                'pl-3': size === 'sm',
                'pl-3': size === 'base' || size === 'lg',
                'pl-4': size === 'xl',
                'pl-4': size === '2xl',
                'pl-5': size === '3xl' || size === '4xl',
              }
            )}>
              <div className={clsx(iconSizeClasses[size], 'text-neutral-400')}>
                {leftIcon}
              </div>
            </div>
          )}
          
          {/* Input field */}
          <input
            ref={ref}
            type={type}
            className={inputClasses}
            placeholder={placeholder}
            disabled={disabled}
            value={currentValue}
            onChange={handleChange}
            {...props}
          />
          
          {/* Right icon or clear button */}
          <div className={clsx(
            'absolute right-0 top-1/2 transform -translate-y-1/2 flex items-center',
            {
              'pr-2': size === 'xs',
              'pr-3': size === 'sm',
              'pr-3': size === 'base' || size === 'lg',
              'pr-4': size === 'xl',
              'pr-4': size === '2xl',
              'pr-5': size === '3xl' || size === '4xl',
            }
          )}>
            {clearable && currentValue && (
              <button
                type="button"
                onClick={handleClear}
                className={clsx(
                  iconSizeClasses[size],
                  'text-neutral-400 hover:text-neutral-600 transition-colors'
                )}
              >
                <svg
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}
            {!clearable && rightIcon && (
              <div className={clsx(iconSizeClasses[size], 'text-neutral-400')}>
                {rightIcon}
              </div>
            )}
          </div>
        </div>
        
        {/* Helper text or error message */}
        {(helperText || errorMessage) && (
          <div className={helperTextClasses}>
            {errorMessage || helperText}
          </div>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
