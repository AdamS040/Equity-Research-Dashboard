import { useEffect, useRef, useCallback, useState } from 'react'

// Hook for managing focus trap in modals and dropdowns
export const useFocusTrap = (isActive: boolean) => {
  const containerRef = useRef<HTMLElement>(null)

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!isActive || !containerRef.current) return

    const focusableElements = containerRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0] as HTMLElement
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

    if (event.key === 'Tab') {
      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault()
          lastElement?.focus()
        }
      } else {
        if (document.activeElement === lastElement) {
          event.preventDefault()
          firstElement?.focus()
        }
      }
    }
  }, [isActive])

  useEffect(() => {
    if (isActive) {
      document.addEventListener('keydown', handleKeyDown)
      // Focus the first element when trap becomes active
      const firstElement = containerRef.current?.querySelector(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      ) as HTMLElement
      firstElement?.focus()
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isActive, handleKeyDown])

  return containerRef
}

// Hook for managing keyboard navigation in lists
export const useKeyboardNavigation = (
  items: any[],
  onSelect: (item: any, index: number) => void,
  isActive: boolean
) => {
  const [focusedIndex, setFocusedIndex] = useState(-1)

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!isActive) return

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        setFocusedIndex(prev => (prev + 1) % items.length)
        break
      case 'ArrowUp':
        event.preventDefault()
        setFocusedIndex(prev => (prev - 1 + items.length) % items.length)
        break
      case 'Enter':
      case ' ':
        event.preventDefault()
        if (focusedIndex >= 0 && focusedIndex < items.length) {
          onSelect(items[focusedIndex], focusedIndex)
        }
        break
      case 'Escape':
        setFocusedIndex(-1)
        break
    }
  }, [isActive, items, focusedIndex, onSelect])

  useEffect(() => {
    if (isActive) {
      document.addEventListener('keydown', handleKeyDown)
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isActive, handleKeyDown])

  return { focusedIndex, setFocusedIndex }
}

// Hook for managing ARIA live regions for screen readers
export const useAriaLive = () => {
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const liveRegion = document.createElement('div')
    liveRegion.setAttribute('aria-live', priority)
    liveRegion.setAttribute('aria-atomic', 'true')
    liveRegion.className = 'sr-only'
    liveRegion.textContent = message
    
    document.body.appendChild(liveRegion)
    
    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(liveRegion)
    }, 1000)
  }, [])

  return { announce }
}

// Hook for managing reduced motion preferences
export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return prefersReducedMotion
}

// Hook for managing high contrast preferences
export const useHighContrast = () => {
  const [prefersHighContrast, setPrefersHighContrast] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)')
    setPrefersHighContrast(mediaQuery.matches)

    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersHighContrast(event.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return prefersHighContrast
}

// Utility function to generate unique IDs for ARIA relationships
export const useId = (prefix: string = 'id') => {
  const [id] = useState(() => `${prefix}-${Math.random().toString(36).substr(2, 9)}`)
  return id
}

// Hook for managing skip links
export const useSkipLinks = () => {
  const skipLinks = [
    { href: '#main-content', text: 'Skip to main content' },
    { href: '#navigation', text: 'Skip to navigation' },
    { href: '#search', text: 'Skip to search' },
  ]

  return skipLinks
}
