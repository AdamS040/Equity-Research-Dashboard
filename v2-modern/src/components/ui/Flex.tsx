import React, { forwardRef } from 'react'
import { clsx } from 'clsx'
import { FlexProps } from '../../types/design-system'

/**
 * Flex component for flexible layouts
 * 
 * @example
 * ```tsx
 * <Flex direction="row" justify="between" align="center" gap={4}>
 *   <div>Left content</div>
 *   <div>Right content</div>
 * </Flex>
 * 
 * <Flex direction="column" gap={2} fullWidth>
 *   <div>Item 1</div>
 *   <div>Item 2</div>
 * </Flex>
 * ```
 */
export const Flex = forwardRef<HTMLDivElement, FlexProps>(
  (
    {
      children,
      className,
      direction = 'row',
      wrap = 'nowrap',
      justify = 'start',
      align = 'start',
      gap,
      fullWidth = false,
      fullHeight = false,
      ...props
    },
    ref
  ) => {
    const flexClasses = clsx(
      'flex',
      
      // Direction variants
      {
        'flex-row': direction === 'row',
        'flex-col': direction === 'column',
        'flex-row-reverse': direction === 'row-reverse',
        'flex-col-reverse': direction === 'column-reverse',
      },
      
      // Wrap variants
      {
        'flex-nowrap': wrap === 'nowrap',
        'flex-wrap': wrap === 'wrap',
        'flex-wrap-reverse': wrap === 'wrap-reverse',
      },
      
      // Justify content variants
      {
        'justify-start': justify === 'start',
        'justify-end': justify === 'end',
        'justify-center': justify === 'center',
        'justify-between': justify === 'between',
        'justify-around': justify === 'around',
        'justify-evenly': justify === 'evenly',
      },
      
      // Align items variants
      {
        'items-start': align === 'start',
        'items-end': align === 'end',
        'items-center': align === 'center',
        'items-baseline': align === 'baseline',
        'items-stretch': align === 'stretch',
      },
      
      // Gap variants
      {
        'gap-1': gap === 'xs',
        'gap-2': gap === 'sm',
        'gap-3': gap === 'base',
        'gap-4': gap === 'lg',
        'gap-5': gap === 'xl',
        'gap-6': gap === '2xl',
        'gap-8': gap === '3xl',
        'gap-10': gap === '4xl',
      },
      
      // Size variants
      {
        'w-full': fullWidth,
        'h-full': fullHeight,
      },
      
      className
    )

    return (
      <div ref={ref} className={flexClasses} {...props}>
        {children}
      </div>
    )
  }
)

Flex.displayName = 'Flex'
