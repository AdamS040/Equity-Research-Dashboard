/**
 * Design System UI Components
 * 
 * This file exports all the UI components from the design system.
 * Import components individually or use the barrel export.
 * 
 * @example
 * ```tsx
 * import { Button, Input, Card } from '@/components/ui'
 * 
 * // Or import individually
 * import { Button } from '@/components/ui/Button'
 * ```
 */

// Base Components
export { Button } from './Button'
export { Input } from './Input'
export { Card, CardHeader, CardBody, CardFooter } from './Card'
export { Badge } from './Badge'
export { Spinner } from './Spinner'
export { Modal } from './Modal'

// Layout Components
export { Container } from './Container'
export { Grid, GridItem } from './Grid'
export { Flex } from './Flex'

// Typography Components
export { Heading, Text, Code } from './Typography'

// Re-export types for convenience
export type {
  // Base component props
  ButtonProps,
  InputProps,
  CardProps,
  CardHeaderProps,
  CardBodyProps,
  CardFooterProps,
  BadgeProps,
  SpinnerProps,
  ModalProps,
  
  // Layout component props
  ContainerProps,
  GridProps,
  GridItemProps,
  FlexProps,
  
  // Typography component props
  HeadingProps,
  TextProps,
  CodeProps,
  
  // Common types
  Size,
  ColorVariant,
  Variant,
  BaseComponentProps,
} from '../../types/design-system'
