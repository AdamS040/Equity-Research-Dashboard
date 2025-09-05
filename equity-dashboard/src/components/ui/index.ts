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
export { ErrorDisplay } from '../ErrorDisplay'

// Layout Components
export { Container } from './Container'
export { Grid, GridItem } from './Grid'
export { Flex } from './Flex'

// Typography Components
export { Heading, Text, Code } from './Typography'

// Loading & Error States
export { 
  Skeleton, 
  SkeletonCard, 
  SkeletonText, 
  SkeletonChart, 
  SkeletonTable, 
  SkeletonAvatar 
} from './Skeleton'
export { 
  LoadingStates, 
  ChartLoadingState, 
  TableLoadingState, 
  CardLoadingState,
  ProgressiveChartLoader,
  OptimisticWrapper
} from './LoadingStates'
export { 
  ErrorStates, 
  NetworkError, 
  TimeoutError, 
  AuthError, 
  ErrorFallback 
} from './ErrorStates'

// Animations & Interactions
export { 
  PageTransition, 
  StaggeredList, 
  HoverScale, 
  LoadingPulse, 
  FeedbackAnimation, 
  ChartLoadingAnimation, 
  AnimatedCounter, 
  Swipeable,
  fadeInUp,
  fadeInScale,
  slideInFromLeft,
  slideInFromRight,
  staggerContainer,
  staggerItem
} from './Animations'

// Accessibility
export { 
  AccessibilityProvider, 
  useAccessibility, 
  SkipLinks, 
  FocusTrap, 
  ScreenReaderOnly, 
  AccessibleButton, 
  AccessibleField, 
  LiveRegion, 
  AccessibilitySettings 
} from './Accessibility'

// Theme & Preferences
export { 
  ThemeProvider, 
  useTheme, 
  ThemeToggle, 
  ThemeSelector, 
  UserPreferencesProvider, 
  useUserPreferences, 
  SettingsPanel 
} from './ThemeProvider'

// Mobile Components
export { 
  PullToRefresh, 
  SwipeableCard, 
  BottomSheet, 
  CollapsibleSection, 
  TouchButton, 
  MobileInput, 
  MobileTabs 
} from './MobileComponents'

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
