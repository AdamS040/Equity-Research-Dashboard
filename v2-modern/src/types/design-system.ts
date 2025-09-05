/**
 * Design System Type Definitions
 * 
 * This file contains all TypeScript interfaces and types for the equity research dashboard
 * design system components. It provides type safety and IntelliSense support for all
 * UI components and their props.
 */

import { ReactNode, ButtonHTMLAttributes, InputHTMLAttributes, HTMLAttributes } from 'react'

// ============================================================================
// BASE TYPES
// ============================================================================

/**
 * Common size variants used across components
 */
export type Size = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl'

/**
 * Color variants for components
 */
export type ColorVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'neutral'

/**
 * Visual variants for components
 */
export type Variant = 'solid' | 'outline' | 'ghost' | 'link'

/**
 * Common component props that are shared across multiple components
 */
export interface BaseComponentProps {
  /** Additional CSS classes to apply */
  className?: string
  /** Whether the component is disabled */
  disabled?: boolean
  /** Whether the component is in a loading state */
  loading?: boolean
  /** Size variant of the component */
  size?: Size
  /** Content to render inside the component */
  children?: ReactNode
}

// ============================================================================
// BUTTON COMPONENT
// ============================================================================

/**
 * Props for the Button component
 */
export interface ButtonProps extends BaseComponentProps, Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'size'> {
  /** Visual variant of the button */
  variant?: Variant
  /** Color variant of the button */
  color?: ColorVariant
  /** Whether the button should take full width */
  fullWidth?: boolean
  /** Icon to display before the button text */
  leftIcon?: ReactNode
  /** Icon to display after the button text */
  rightIcon?: ReactNode
  /** Loading text to display when in loading state */
  loadingText?: string
  /** Click handler */
  onClick?: () => void
}

// ============================================================================
// INPUT COMPONENT
// ============================================================================

/**
 * Input type variants
 */
export type InputType = 'text' | 'email' | 'password' | 'number' | 'search' | 'tel' | 'url'

/**
 * Input validation state
 */
export type InputState = 'default' | 'error' | 'success' | 'warning'

/**
 * Props for the Input component
 */
export interface InputProps extends BaseComponentProps, Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Type of input */
  type?: InputType
  /** Label for the input */
  label?: string
  /** Helper text to display below the input */
  helperText?: string
  /** Error message to display */
  errorMessage?: string
  /** Validation state */
  state?: InputState
  /** Placeholder text */
  placeholder?: string
  /** Whether the input is required */
  required?: boolean
  /** Icon to display before the input */
  leftIcon?: ReactNode
  /** Icon to display after the input */
  rightIcon?: ReactNode
  /** Whether to show a clear button */
  clearable?: boolean
  /** Callback when the input value changes */
  onChange?: (value: string) => void
  /** Callback when the input is cleared */
  onClear?: () => void
}

// ============================================================================
// CARD COMPONENT
// ============================================================================

/**
 * Props for the Card component
 */
export interface CardProps extends BaseComponentProps, HTMLAttributes<HTMLDivElement> {
  /** Whether the card has a shadow */
  shadow?: boolean
  /** Whether the card has a border */
  bordered?: boolean
  /** Whether the card is clickable */
  clickable?: boolean
  /** Whether the card is hoverable */
  hoverable?: boolean
  /** Padding variant */
  padding?: Size
}

/**
 * Props for the CardHeader component
 */
export interface CardHeaderProps extends BaseComponentProps, HTMLAttributes<HTMLDivElement> {
  /** Title of the card */
  title?: string
  /** Subtitle of the card */
  subtitle?: string
  /** Action elements to display on the right */
  actions?: ReactNode
}

/**
 * Props for the CardBody component
 */
export interface CardBodyProps extends BaseComponentProps, HTMLAttributes<HTMLDivElement> {
  /** Whether the body has no padding */
  noPadding?: boolean
}

/**
 * Props for the CardFooter component
 */
export interface CardFooterProps extends BaseComponentProps, HTMLAttributes<HTMLDivElement> {
  /** Whether the footer has no padding */
  noPadding?: boolean
}

// ============================================================================
// BADGE COMPONENT
// ============================================================================

/**
 * Badge shape variants
 */
export type BadgeShape = 'rounded' | 'pill' | 'square'

/**
 * Props for the Badge component
 */
export interface BadgeProps extends BaseComponentProps, HTMLAttributes<HTMLSpanElement> {
  /** Color variant of the badge */
  color?: ColorVariant
  /** Shape variant of the badge */
  shape?: BadgeShape
  /** Whether the badge is outlined */
  outlined?: boolean
  /** Whether the badge has a dot indicator */
  dot?: boolean
  /** Maximum number to display before showing "+N" */
  max?: number
  /** Number to display in the badge */
  count?: number
}

// ============================================================================
// SPINNER COMPONENT
// ============================================================================

/**
 * Spinner animation variants
 */
export type SpinnerVariant = 'dots' | 'pulse' | 'ring' | 'bars'

/**
 * Props for the Spinner component
 */
export interface SpinnerProps extends BaseComponentProps, HTMLAttributes<HTMLDivElement> {
  /** Animation variant */
  variant?: SpinnerVariant
  /** Color variant */
  color?: ColorVariant
  /** Whether the spinner should be centered */
  centered?: boolean
  /** Text to display below the spinner */
  text?: string
}

// ============================================================================
// MODAL COMPONENT
// ============================================================================

/**
 * Modal size variants
 */
export type ModalSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full'

/**
 * Props for the Modal component
 */
export interface ModalProps extends BaseComponentProps {
  /** Whether the modal is open */
  isOpen: boolean
  /** Callback when the modal should close */
  onClose: () => void
  /** Title of the modal */
  title?: string
  /** Size variant of the modal */
  size?: ModalSize
  /** Whether the modal can be closed by clicking the backdrop */
  closeOnBackdropClick?: boolean
  /** Whether the modal can be closed by pressing escape */
  closeOnEscape?: boolean
  /** Whether to show the close button */
  showCloseButton?: boolean
  /** Content to render in the modal */
  children: ReactNode
  /** Footer content */
  footer?: ReactNode
}

// ============================================================================
// LAYOUT COMPONENTS
// ============================================================================

/**
 * Container size variants
 */
export type ContainerSize = 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'

/**
 * Props for the Container component
 */
export interface ContainerProps extends BaseComponentProps, HTMLAttributes<HTMLDivElement> {
  /** Maximum width of the container */
  maxWidth?: ContainerSize
  /** Whether the container is fluid (no max-width) */
  fluid?: boolean
  /** Whether the container has horizontal padding */
  padded?: boolean
}

/**
 * Grid column span (1-12)
 */
export type GridSpan = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12

/**
 * Responsive grid spans
 */
export interface ResponsiveGridSpan {
  /** Default span */
  default?: GridSpan
  /** Small screen span (sm) */
  sm?: GridSpan
  /** Medium screen span (md) */
  md?: GridSpan
  /** Large screen span (lg) */
  lg?: GridSpan
  /** Extra large screen span (xl) */
  xl?: GridSpan
  /** 2XL screen span (2xl) */
  '2xl'?: GridSpan
}

/**
 * Props for the Grid component
 */
export interface GridProps extends BaseComponentProps, HTMLAttributes<HTMLDivElement> {
  /** Number of columns in the grid */
  cols?: GridSpan
  /** Gap between grid items */
  gap?: Size
  /** Whether the grid is responsive */
  responsive?: boolean
}

/**
 * Props for the GridItem component
 */
export interface GridItemProps extends BaseComponentProps, HTMLAttributes<HTMLDivElement> {
  /** Column span */
  span?: GridSpan | ResponsiveGridSpan
  /** Column start position */
  start?: GridSpan | ResponsiveGridSpan
  /** Column end position */
  end?: GridSpan | ResponsiveGridSpan
}

/**
 * Flex direction variants
 */
export type FlexDirection = 'row' | 'column' | 'row-reverse' | 'column-reverse'

/**
 * Flex wrap variants
 */
export type FlexWrap = 'nowrap' | 'wrap' | 'wrap-reverse'

/**
 * Flex justify content variants
 */
export type JustifyContent = 'start' | 'end' | 'center' | 'between' | 'around' | 'evenly'

/**
 * Flex align items variants
 */
export type AlignItems = 'start' | 'end' | 'center' | 'baseline' | 'stretch'

/**
 * Props for the Flex component
 */
export interface FlexProps extends BaseComponentProps, HTMLAttributes<HTMLDivElement> {
  /** Flex direction */
  direction?: FlexDirection
  /** Flex wrap */
  wrap?: FlexWrap
  /** Justify content */
  justify?: JustifyContent
  /** Align items */
  align?: AlignItems
  /** Gap between items */
  gap?: Size
  /** Whether the flex container should take full width */
  fullWidth?: boolean
  /** Whether the flex container should take full height */
  fullHeight?: boolean
}

// ============================================================================
// TYPOGRAPHY COMPONENTS
// ============================================================================

/**
 * Text size variants
 */
export type TextSize = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl'

/**
 * Font weight variants
 */
export type FontWeight = 'light' | 'normal' | 'medium' | 'semibold' | 'bold' | 'extrabold' | 'black'

/**
 * Text color variants
 */
export type TextColor = ColorVariant | 'inherit' | 'current'

/**
 * Props for typography components
 */
export interface TypographyProps extends BaseComponentProps, HTMLAttributes<HTMLElement> {
  /** Text size */
  size?: TextSize
  /** Font weight */
  weight?: FontWeight
  /** Text color */
  color?: TextColor
  /** Whether the text should be truncated */
  truncate?: boolean
  /** Whether the text should be centered */
  center?: boolean
  /** Whether the text should be uppercase */
  uppercase?: boolean
  /** Whether the text should be lowercase */
  lowercase?: boolean
  /** Whether the text should be capitalized */
  capitalize?: boolean
}

/**
 * Props for the Heading component
 */
export interface HeadingProps extends TypographyProps {
  /** Heading level (1-6) */
  level?: 1 | 2 | 3 | 4 | 5 | 6
  /** Whether to use display font size */
  display?: boolean
}

/**
 * Props for the Text component
 */
export interface TextProps extends TypographyProps {
  /** Whether the text should be italic */
  italic?: boolean
  /** Whether the text should be underlined */
  underline?: boolean
  /** Whether the text should be strikethrough */
  strikethrough?: boolean
}

/**
 * Props for the Code component
 */
export interface CodeProps extends TypographyProps {
  /** Whether the code should be inline */
  inline?: boolean
  /** Background color for the code block */
  background?: ColorVariant
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Utility type to make specific properties required
 */
export type RequireFields<T, K extends keyof T> = T & Required<Pick<T, K>>

/**
 * Utility type to make specific properties optional
 */
export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

/**
 * Utility type for component refs
 */
export type ComponentRef<T> = React.RefObject<T>

/**
 * Utility type for forward refs
 */
export type ForwardRefComponent<T, P> = React.ForwardRefExoticComponent<
  React.PropsWithoutRef<P> & React.RefAttributes<T>
>
