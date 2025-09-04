import React, { forwardRef } from 'react'
import { clsx } from 'clsx'
import { GridProps, GridItemProps, ResponsiveGridSpan } from '../../types/design-system'

/**
 * Grid component for responsive grid layouts
 * 
 * @example
 * ```tsx
 * <Grid cols={12} gap={4}>
 *   <GridItem span={6}>Half width</GridItem>
 *   <GridItem span={6}>Half width</GridItem>
 * </Grid>
 * 
 * <Grid responsive>
 *   <GridItem span={{ default: 12, md: 6, lg: 4 }}>
 *     Responsive item
 *   </GridItem>
 * </Grid>
 * ```
 */
export const Grid = forwardRef<HTMLDivElement, GridProps>(
  (
    {
      children,
      className,
      cols = 12,
      gap = 'base',
      responsive = true,
      ...props
    },
    ref
  ) => {
    const gridClasses = clsx(
      'grid',
      
      // Column count
      {
        'grid-cols-1': cols === 1,
        'grid-cols-2': cols === 2,
        'grid-cols-3': cols === 3,
        'grid-cols-4': cols === 4,
        'grid-cols-5': cols === 5,
        'grid-cols-6': cols === 6,
        'grid-cols-7': cols === 7,
        'grid-cols-8': cols === 8,
        'grid-cols-9': cols === 9,
        'grid-cols-10': cols === 10,
        'grid-cols-11': cols === 11,
        'grid-cols-12': cols === 12,
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
      
      // Responsive grid
      {
        'sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4': responsive && cols === 12,
        'sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3': responsive && cols === 6,
        'sm:grid-cols-2 md:grid-cols-3': responsive && cols === 4,
        'sm:grid-cols-2': responsive && cols === 2,
      },
      
      className
    )

    return (
      <div ref={ref} className={gridClasses} {...props}>
        {children}
      </div>
    )
  }
)

/**
 * GridItem component for individual grid items
 */
export const GridItem = forwardRef<HTMLDivElement, GridItemProps>(
  (
    {
      children,
      className,
      span,
      start,
      end,
      ...props
    },
    ref
  ) => {
    const getSpanClasses = (spanValue: number | ResponsiveGridSpan | undefined) => {
      if (!spanValue) return ''
      
      if (typeof spanValue === 'number') {
        return {
          'col-span-1': spanValue === 1,
          'col-span-2': spanValue === 2,
          'col-span-3': spanValue === 3,
          'col-span-4': spanValue === 4,
          'col-span-5': spanValue === 5,
          'col-span-6': spanValue === 6,
          'col-span-7': spanValue === 7,
          'col-span-8': spanValue === 8,
          'col-span-9': spanValue === 9,
          'col-span-10': spanValue === 10,
          'col-span-11': spanValue === 11,
          'col-span-12': spanValue === 12,
        }
      }
      
      // Responsive span
      const classes: Record<string, boolean> = {}
      if (spanValue.default) {
        Object.assign(classes, getSpanClasses(spanValue.default))
      }
      if (spanValue.sm) {
        classes[`sm:col-span-${spanValue.sm}`] = true
      }
      if (spanValue.md) {
        classes[`md:col-span-${spanValue.md}`] = true
      }
      if (spanValue.lg) {
        classes[`lg:col-span-${spanValue.lg}`] = true
      }
      if (spanValue.xl) {
        classes[`xl:col-span-${spanValue.xl}`] = true
      }
      if (spanValue['2xl']) {
        classes[`2xl:col-span-${spanValue['2xl']}`] = true
      }
      
      return classes
    }

    const getStartClasses = (startValue: number | ResponsiveGridSpan | undefined) => {
      if (!startValue) return ''
      
      if (typeof startValue === 'number') {
        return {
          'col-start-1': startValue === 1,
          'col-start-2': startValue === 2,
          'col-start-3': startValue === 3,
          'col-start-4': startValue === 4,
          'col-start-5': startValue === 5,
          'col-start-6': startValue === 6,
          'col-start-7': startValue === 7,
          'col-start-8': startValue === 8,
          'col-start-9': startValue === 9,
          'col-start-10': startValue === 10,
          'col-start-11': startValue === 11,
          'col-start-12': startValue === 12,
        }
      }
      
      // Responsive start
      const classes: Record<string, boolean> = {}
      if (startValue.default) {
        Object.assign(classes, getStartClasses(startValue.default))
      }
      if (startValue.sm) {
        classes[`sm:col-start-${startValue.sm}`] = true
      }
      if (startValue.md) {
        classes[`md:col-start-${startValue.md}`] = true
      }
      if (startValue.lg) {
        classes[`lg:col-start-${startValue.lg}`] = true
      }
      if (startValue.xl) {
        classes[`xl:col-start-${startValue.xl}`] = true
      }
      if (startValue['2xl']) {
        classes[`2xl:col-start-${startValue['2xl']}`] = true
      }
      
      return classes
    }

    const getEndClasses = (endValue: number | ResponsiveGridSpan | undefined) => {
      if (!endValue) return ''
      
      if (typeof endValue === 'number') {
        return {
          'col-end-1': endValue === 1,
          'col-end-2': endValue === 2,
          'col-end-3': endValue === 3,
          'col-end-4': endValue === 4,
          'col-end-5': endValue === 5,
          'col-end-6': endValue === 6,
          'col-end-7': endValue === 7,
          'col-end-8': endValue === 8,
          'col-end-9': endValue === 9,
          'col-end-10': endValue === 10,
          'col-end-11': endValue === 11,
          'col-end-12': endValue === 12,
        }
      }
      
      // Responsive end
      const classes: Record<string, boolean> = {}
      if (endValue.default) {
        Object.assign(classes, getEndClasses(endValue.default))
      }
      if (endValue.sm) {
        classes[`sm:col-end-${endValue.sm}`] = true
      }
      if (endValue.md) {
        classes[`md:col-end-${endValue.md}`] = true
      }
      if (endValue.lg) {
        classes[`lg:col-end-${endValue.lg}`] = true
      }
      if (endValue.xl) {
        classes[`xl:col-end-${endValue.xl}`] = true
      }
      if (endValue['2xl']) {
        classes[`2xl:col-end-${endValue['2xl']}`] = true
      }
      
      return classes
    }

    const itemClasses = clsx(
      getSpanClasses(span),
      getStartClasses(start),
      getEndClasses(end),
      className
    )

    return (
      <div ref={ref} className={itemClasses} {...props}>
        {children}
      </div>
    )
  }
)

Grid.displayName = 'Grid'
GridItem.displayName = 'GridItem'
