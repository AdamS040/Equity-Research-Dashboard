import React, { createContext, useContext, useEffect, useState } from 'react'
import { clsx } from 'clsx'

// Accessibility context
interface AccessibilityContextType {
  reducedMotion: boolean
  highContrast: boolean
  fontSize: 'small' | 'medium' | 'large'
  setReducedMotion: (value: boolean) => void
  setHighContrast: (value: boolean) => void
  setFontSize: (size: 'small' | 'medium' | 'large') => void
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined)

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext)
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider')
  }
  return context
}

// Accessibility provider
export interface AccessibilityProviderProps {
  children: React.ReactNode
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children }) => {
  const [reducedMotion, setReducedMotion] = useState(false)
  const [highContrast, setHighContrast] = useState(false)
  const [fontSize, setFontSize] = useState<'small' | 'medium' | 'large'>('medium')

  useEffect(() => {
    // Check for user's motion preferences
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => setReducedMotion(e.matches)
    mediaQuery.addEventListener('change', handleChange)

    // Check for high contrast preferences
    const highContrastQuery = window.matchMedia('(prefers-contrast: high)')
    setHighContrast(highContrastQuery.matches)

    const handleContrastChange = (e: MediaQueryListEvent) => setHighContrast(e.matches)
    highContrastQuery.addEventListener('change', handleContrastChange)

    // Load saved preferences
    const savedFontSize = localStorage.getItem('accessibility-font-size') as 'small' | 'medium' | 'large'
    if (savedFontSize) {
      setFontSize(savedFontSize)
    }

    return () => {
      mediaQuery.removeEventListener('change', handleChange)
      highContrastQuery.removeEventListener('change', handleContrastChange)
    }
  }, [])

  useEffect(() => {
    // Apply font size to document
    const root = document.documentElement
    root.style.fontSize = fontSize === 'small' ? '14px' : fontSize === 'large' ? '18px' : '16px'
    localStorage.setItem('accessibility-font-size', fontSize)
  }, [fontSize])

  useEffect(() => {
    // Apply high contrast mode
    const root = document.documentElement
    if (highContrast) {
      root.classList.add('high-contrast')
    } else {
      root.classList.remove('high-contrast')
    }
  }, [highContrast])

  const value: AccessibilityContextType = {
    reducedMotion,
    highContrast,
    fontSize,
    setReducedMotion,
    setHighContrast,
    setFontSize,
  }

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  )
}

// Skip links component
export interface SkipLinksProps {
  links: Array<{ href: string; label: string }>
}

export const SkipLinks: React.FC<SkipLinksProps> = ({ links }) => (
  <div className="sr-only focus-within:not-sr-only">
    <div className="absolute top-0 left-0 z-50 p-2 space-y-1">
      {links.map((link, index) => (
        <a
          key={index}
          href={link.href}
          className="block px-4 py-2 bg-primary-600 text-white rounded shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        >
          {link.label}
        </a>
      ))}
    </div>
  </div>
)

// Focus trap component
export interface FocusTrapProps {
  children: React.ReactNode
  active: boolean
  className?: string
}

export const FocusTrap: React.FC<FocusTrapProps> = ({ children, active, className }) => {
  const containerRef = React.useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!active || !containerRef.current) return

    const focusableElements = containerRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0] as HTMLElement
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement?.focus()
          e.preventDefault()
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement?.focus()
          e.preventDefault()
        }
      }
    }

    document.addEventListener('keydown', handleTabKey)
    firstElement?.focus()

    return () => {
      document.removeEventListener('keydown', handleTabKey)
    }
  }, [active])

  return (
    <div ref={containerRef} className={className}>
      {children}
    </div>
  )
}

// Screen reader only text
export interface ScreenReaderOnlyProps {
  children: React.ReactNode
}

export const ScreenReaderOnly: React.FC<ScreenReaderOnlyProps> = ({ children }) => (
  <span className="sr-only">{children}</span>
)

// Accessible button with proper ARIA attributes
export interface AccessibleButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  loading?: boolean
  loadingText?: string
  className?: string
}

export const AccessibleButton: React.FC<AccessibleButtonProps> = ({
  children,
  loading = false,
  loadingText = 'Loading...',
  className,
  disabled,
  ...props
}) => {
  const { reducedMotion } = useAccessibility()

  return (
    <button
      {...props}
      disabled={disabled || loading}
      className={clsx(
        'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
      aria-disabled={disabled || loading}
      aria-busy={loading}
    >
      {loading ? (
        <>
          <ScreenReaderOnly>{loadingText}</ScreenReaderOnly>
          <span aria-hidden="true">{children}</span>
        </>
      ) : (
        children
      )}
    </button>
  )
}

// Accessible form field
export interface AccessibleFieldProps {
  label: string
  error?: string
  hint?: string
  required?: boolean
  children: React.ReactNode
  className?: string
}

export const AccessibleField: React.FC<AccessibleFieldProps> = ({
  label,
  error,
  hint,
  required = false,
  children,
  className,
}) => {
  const fieldId = React.useId()
  const errorId = React.useId()
  const hintId = React.useId()

  return (
    <div className={clsx('space-y-1', className)}>
      <label
        htmlFor={fieldId}
        className="block text-sm font-medium text-neutral-700"
      >
        {label}
        {required && (
          <span className="text-danger-500 ml-1" aria-label="required">
            *
          </span>
        )}
      </label>
      
      {hint && (
        <p id={hintId} className="text-sm text-neutral-500">
          {hint}
        </p>
      )}
      
      <div>
        {React.cloneElement(children as React.ReactElement, {
          id: fieldId,
          'aria-describedby': clsx(
            error ? errorId : undefined,
            hint ? hintId : undefined
          ),
          'aria-invalid': error ? 'true' : 'false',
          'aria-required': required,
        })}
      </div>
      
      {error && (
        <p id={errorId} className="text-sm text-danger-600" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}

// Live region for announcements
export interface LiveRegionProps {
  message: string
  politeness?: 'polite' | 'assertive'
}

export const LiveRegion: React.FC<LiveRegionProps> = ({ message, politeness = 'polite' }) => (
  <div
    aria-live={politeness}
    aria-atomic="true"
    className="sr-only"
  >
    {message}
  </div>
)

// Accessibility settings panel
export const AccessibilitySettings: React.FC = () => {
  const { reducedMotion, highContrast, fontSize, setReducedMotion, setHighContrast, setFontSize } = useAccessibility()

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Accessibility Settings</h3>
      
      <div className="space-y-4">
        <div>
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={reducedMotion}
              onChange={(e) => setReducedMotion(e.target.checked)}
              className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
            />
            <span>Reduce motion</span>
          </label>
          <p className="text-sm text-neutral-500 ml-6">
            Minimize animations and transitions
          </p>
        </div>

        <div>
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={highContrast}
              onChange={(e) => setHighContrast(e.target.checked)}
              className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
            />
            <span>High contrast</span>
          </label>
          <p className="text-sm text-neutral-500 ml-6">
            Increase color contrast for better visibility
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            Font Size
          </label>
          <select
            value={fontSize}
            onChange={(e) => setFontSize(e.target.value as 'small' | 'medium' | 'large')}
            className="block w-full rounded-md border-neutral-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </div>
      </div>
    </div>
  )
}
