import React, { forwardRef } from 'react'
import { clsx } from 'clsx'
import { CardProps, CardHeaderProps, CardBodyProps, CardFooterProps } from '../../types/design-system'

/**
 * Card component with header, body, and footer sections
 * 
 * @example
 * ```tsx
 * <Card>
 *   <CardHeader title="Portfolio Overview" subtitle="Your investment summary" />
 *   <CardBody>
 *     <p>Card content goes here</p>
 *   </CardBody>
 *   <CardFooter>
 *     <Button>View Details</Button>
 *   </CardFooter>
 * </Card>
 * ```
 */
export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      children,
      className,
      shadow = true,
      bordered = true,
      clickable = false,
      hoverable = false,
      padding = 'base',
      ...props
    },
    ref
  ) => {
    const cardClasses = clsx(
      // Base styles
      'bg-white dark:bg-neutral-800 rounded-lg transition-all duration-200',
      
      // Shadow variants
      {
        'shadow-sm': shadow === true,
        'shadow-md': shadow === 'md',
        'shadow-lg': shadow === 'lg',
        'shadow-xl': shadow === 'xl',
        'shadow-none': shadow === false,
      },
      
      // Border variants
      {
        'border border-neutral-200': bordered === true,
        'border-2 border-neutral-300': bordered === 'thick',
        'border-0': bordered === false,
      },
      
      // Padding variants
      {
        'p-2': padding === 'xs',
        'p-3': padding === 'sm',
        'p-4': padding === 'base',
        'p-5': padding === 'lg',
        'p-6': padding === 'xl',
        'p-8': padding === '2xl',
        'p-10': padding === '3xl',
        'p-12': padding === '4xl',
        'p-0': padding === 'none',
      },
      
      // Interactive states
      {
        'cursor-pointer': clickable,
        'hover:shadow-md hover:-translate-y-0.5': hoverable,
        'hover:shadow-lg hover:-translate-y-1': clickable,
        'active:translate-y-0 active:shadow-sm': clickable,
      },
      
      className
    )

    return (
      <div ref={ref} className={cardClasses} {...props}>
        {children}
      </div>
    )
  }
)

/**
 * CardHeader component for card titles and actions
 */
export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  (
    {
      children,
      className,
      title,
      subtitle,
      actions,
      padding = 'base',
      ...props
    },
    ref
  ) => {
    const headerClasses = clsx(
      'flex items-start justify-between',
      {
        'p-2': padding === 'xs',
        'p-3': padding === 'sm',
        'p-4': padding === 'base',
        'p-5': padding === 'lg',
        'p-6': padding === 'xl',
        'p-8': padding === '2xl',
        'p-10': padding === '3xl',
        'p-12': padding === '4xl',
        'p-0': padding === 'none',
      },
      className
    )

    return (
      <div ref={ref} className={headerClasses} {...props}>
        <div className="flex-1 min-w-0">
          {title && (
            <h3 className="text-lg font-semibold text-neutral-900 truncate">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="mt-1 text-sm text-neutral-600 truncate">
              {subtitle}
            </p>
          )}
          {children}
        </div>
        {actions && (
          <div className="ml-4 flex-shrink-0">
            {actions}
          </div>
        )}
      </div>
    )
  }
)

/**
 * CardBody component for main card content
 */
export const CardBody = forwardRef<HTMLDivElement, CardBodyProps>(
  (
    {
      children,
      className,
      noPadding = false,
      padding = 'base',
      ...props
    },
    ref
  ) => {
    const bodyClasses = clsx(
      {
        'p-2': padding === 'xs' && !noPadding,
        'p-3': padding === 'sm' && !noPadding,
        'p-4': padding === 'base' && !noPadding,
        'p-5': padding === 'lg' && !noPadding,
        'p-6': padding === 'xl' && !noPadding,
        'p-8': padding === '2xl' && !noPadding,
        'p-10': padding === '3xl' && !noPadding,
        'p-12': padding === '4xl' && !noPadding,
        'p-0': noPadding,
      },
      className
    )

    return (
      <div ref={ref} className={bodyClasses} {...props}>
        {children}
      </div>
    )
  }
)

/**
 * CardFooter component for card actions and additional content
 */
export const CardFooter = forwardRef<HTMLDivElement, CardFooterProps>(
  (
    {
      children,
      className,
      noPadding = false,
      padding = 'base',
      ...props
    },
    ref
  ) => {
    const footerClasses = clsx(
      'flex items-center justify-between',
      {
        'p-2': padding === 'xs' && !noPadding,
        'p-3': padding === 'sm' && !noPadding,
        'p-4': padding === 'base' && !noPadding,
        'p-5': padding === 'lg' && !noPadding,
        'p-6': padding === 'xl' && !noPadding,
        'p-8': padding === '2xl' && !noPadding,
        'p-10': padding === '3xl' && !noPadding,
        'p-12': padding === '4xl' && !noPadding,
        'p-0': noPadding,
      },
      className
    )

    return (
      <div ref={ref} className={footerClasses} {...props}>
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'
CardHeader.displayName = 'CardHeader'
CardBody.displayName = 'CardBody'
CardFooter.displayName = 'CardFooter'
