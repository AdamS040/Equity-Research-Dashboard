import React, { forwardRef } from 'react'
import { clsx } from 'clsx'
import { HeadingProps, TextProps, CodeProps } from '../../types/design-system'

/**
 * Heading component for page and section titles
 * 
 * @example
 * ```tsx
 * <Heading level={1} size="3xl" weight="bold">
 *   Page Title
 * </Heading>
 * 
 * <Heading level={2} display>
 *   Display Heading
 * </Heading>
 * ```
 */
export const Heading = forwardRef<HTMLHeadingElement, HeadingProps>(
  (
    {
      children,
      className,
      level = 1,
      size,
      weight = 'semibold',
      color = 'neutral',
      display = false,
      truncate = false,
      center = false,
      uppercase = false,
      lowercase = false,
      capitalize = false,
      ...props
    },
    ref
  ) => {
    // Default size based on level if not provided
    const defaultSizes = {
      1: '4xl',
      2: '3xl',
      3: '2xl',
      4: 'xl',
      5: 'lg',
      6: 'base',
    } as const

    const headingSize = size || defaultSizes[level]
    const isDisplay = display || level === 1

    const headingClasses = clsx(
      // Base styles
      'font-display leading-tight',
      
      // Size variants
      {
        'text-xs': headingSize === 'xs',
        'text-sm': headingSize === 'sm',
        'text-base': headingSize === 'base',
        'text-lg': headingSize === 'lg',
        'text-xl': headingSize === 'xl',
        'text-2xl': headingSize === '2xl',
        'text-3xl': headingSize === '3xl',
        'text-4xl': headingSize === '4xl',
        'text-5xl': headingSize === '5xl',
        'text-6xl': headingSize === '6xl',
      },
      
      // Weight variants
      {
        'font-light': weight === 'light',
        'font-normal': weight === 'normal',
        'font-medium': weight === 'medium',
        'font-semibold': weight === 'semibold',
        'font-bold': weight === 'bold',
        'font-extrabold': weight === 'extrabold',
        'font-black': weight === 'black',
      },
      
      // Color variants
      {
        'text-primary-600': color === 'primary',
        'text-secondary-600': color === 'secondary',
        'text-success-600': color === 'success',
        'text-warning-600': color === 'warning',
        'text-danger-600': color === 'danger',
        'text-neutral-900': color === 'neutral',
        'text-inherit': color === 'inherit',
        'text-current': color === 'current',
      },
      
      // Text transformations
      {
        'truncate': truncate,
        'text-center': center,
        'uppercase': uppercase,
        'lowercase': lowercase,
        'capitalize': capitalize,
      },
      
      // Display variant
      {
        'tracking-tight': isDisplay,
      },
      
      className
    )

    const HeadingTag = `h${level}` as keyof JSX.IntrinsicElements

    return (
      <HeadingTag ref={ref} className={headingClasses} {...props}>
        {children}
      </HeadingTag>
    )
  }
)

/**
 * Text component for body text and paragraphs
 * 
 * @example
 * ```tsx
 * <Text size="base" color="neutral">
 *   Regular paragraph text
 * </Text>
 * 
 * <Text italic underline>
 *   Styled text
 * </Text>
 * ```
 */
export const Text = forwardRef<HTMLParagraphElement, TextProps>(
  (
    {
      children,
      className,
      size = 'base',
      weight = 'normal',
      color = 'neutral',
      italic = false,
      underline = false,
      strikethrough = false,
      truncate = false,
      center = false,
      uppercase = false,
      lowercase = false,
      capitalize = false,
      ...props
    },
    ref
  ) => {
    const textClasses = clsx(
      // Base styles
      'font-sans',
      
      // Size variants
      {
        'text-xs': size === 'xs',
        'text-sm': size === 'sm',
        'text-base': size === 'base',
        'text-lg': size === 'lg',
        'text-xl': size === 'xl',
        'text-2xl': size === '2xl',
        'text-3xl': size === '3xl',
        'text-4xl': size === '4xl',
        'text-5xl': size === '5xl',
        'text-6xl': size === '6xl',
      },
      
      // Weight variants
      {
        'font-light': weight === 'light',
        'font-normal': weight === 'normal',
        'font-medium': weight === 'medium',
        'font-semibold': weight === 'semibold',
        'font-bold': weight === 'bold',
        'font-extrabold': weight === 'extrabold',
        'font-black': weight === 'black',
      },
      
      // Color variants
      {
        'text-primary-600': color === 'primary',
        'text-secondary-600': color === 'secondary',
        'text-success-600': color === 'success',
        'text-warning-600': color === 'warning',
        'text-danger-600': color === 'danger',
        'text-neutral-700': color === 'neutral',
        'text-inherit': color === 'inherit',
        'text-current': color === 'current',
      },
      
      // Text decorations
      {
        'italic': italic,
        'underline': underline,
        'line-through': strikethrough,
      },
      
      // Text transformations
      {
        'truncate': truncate,
        'text-center': center,
        'uppercase': uppercase,
        'lowercase': lowercase,
        'capitalize': capitalize,
      },
      
      className
    )

    return (
      <p ref={ref} className={textClasses} {...props}>
        {children}
      </p>
    )
  }
)

/**
 * Code component for displaying code snippets
 * 
 * @example
 * ```tsx
 * <Code inline>const value = 42;</Code>
 * 
 * <Code background="neutral" size="sm">
 *   function example() {
 *     return "Hello World";
 *   }
 * </Code>
 * ```
 */
export const Code = forwardRef<HTMLElement, CodeProps>(
  (
    {
      children,
      className,
      inline = false,
      size = 'sm',
      weight = 'normal',
      color = 'neutral',
      background = 'neutral',
      ...props
    },
    ref
  ) => {
    const codeClasses = clsx(
      // Base styles
      'font-mono',
      
      // Inline vs block
      {
        'inline-block px-1.5 py-0.5 rounded text-xs': inline,
        'block p-4 rounded-lg text-sm': !inline,
      },
      
      // Size variants (only for block)
      {
        'text-xs': size === 'xs' && !inline,
        'text-sm': size === 'sm' && !inline,
        'text-base': size === 'base' && !inline,
        'text-lg': size === 'lg' && !inline,
        'text-xl': size === 'xl' && !inline,
      },
      
      // Weight variants
      {
        'font-light': weight === 'light',
        'font-normal': weight === 'normal',
        'font-medium': weight === 'medium',
        'font-semibold': weight === 'semibold',
        'font-bold': weight === 'bold',
        'font-extrabold': weight === 'extrabold',
        'font-black': weight === 'black',
      },
      
      // Color variants
      {
        'text-primary-600': color === 'primary',
        'text-secondary-600': color === 'secondary',
        'text-success-600': color === 'success',
        'text-warning-600': color === 'warning',
        'text-danger-600': color === 'danger',
        'text-neutral-800': color === 'neutral',
        'text-inherit': color === 'inherit',
        'text-current': color === 'current',
      },
      
      // Background variants
      {
        'bg-primary-50': background === 'primary',
        'bg-secondary-50': background === 'secondary',
        'bg-success-50': background === 'success',
        'bg-warning-50': background === 'warning',
        'bg-danger-50': background === 'danger',
        'bg-neutral-100': background === 'neutral',
      },
      
      className
    )

    const CodeTag = inline ? 'code' : 'pre'

    return (
      <CodeTag ref={ref} className={codeClasses} {...props}>
        {inline ? children : <code>{children}</code>}
      </CodeTag>
    )
  }
)

Heading.displayName = 'Heading'
Text.displayName = 'Text'
Code.displayName = 'Code'
