import React, { forwardRef } from 'react'
import { clsx } from 'clsx'
import { ContainerProps } from '../../types/design-system'

/**
 * Container component for responsive content layout
 * 
 * @example
 * ```tsx
 * <Container maxWidth="lg" padded>
 *   <h1>Page Content</h1>
 * </Container>
 * 
 * <Container fluid>
 *   <div>Full width content</div>
 * </Container>
 * ```
 */
export const Container = forwardRef<HTMLDivElement, ContainerProps>(
  (
    {
      children,
      className,
      maxWidth = 'xl',
      fluid = false,
      padded = true,
      ...props
    },
    ref
  ) => {
    const containerClasses = clsx(
      'w-full',
      
      // Max width variants
      {
        'max-w-xs mx-auto': maxWidth === 'sm' && !fluid,
        'max-w-sm mx-auto': maxWidth === 'md' && !fluid,
        'max-w-md mx-auto': maxWidth === 'lg' && !fluid,
        'max-w-lg mx-auto': maxWidth === 'xl' && !fluid,
        'max-w-xl mx-auto': maxWidth === '2xl' && !fluid,
        'max-w-2xl mx-auto': maxWidth === '3xl' && !fluid,
        'max-w-3xl mx-auto': maxWidth === '4xl' && !fluid,
        'max-w-4xl mx-auto': maxWidth === '5xl' && !fluid,
        'max-w-5xl mx-auto': maxWidth === '6xl' && !fluid,
        'max-w-6xl mx-auto': maxWidth === '7xl' && !fluid,
        'max-w-7xl mx-auto': maxWidth === 'full' && !fluid,
        'max-w-full': fluid,
      },
      
      // Padding
      {
        'px-4 sm:px-6 lg:px-8': padded && !fluid,
        'px-0': !padded,
      },
      
      className
    )

    return (
      <div ref={ref} className={containerClasses} {...props}>
        {children}
      </div>
    )
  }
)

Container.displayName = 'Container'
