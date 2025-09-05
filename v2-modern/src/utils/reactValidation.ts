/**
 * React Import Validation Utilities
 * 
 * Provides utilities to validate React imports and prevent common issues
 * that can cause "Cannot read properties of null" errors
 */

import React from 'react'

// Validate that React hooks are properly available
export function validateReactHooks(): boolean {
  const hooks = ['useState', 'useEffect', 'useCallback', 'useMemo', 'useRef']
  
  for (const hook of hooks) {
    if (typeof React[hook] !== 'function') {
      console.error(`React hook ${hook} is not available. This may indicate an import issue.`)
      return false
    }
  }
  
  return true
}

// Validate React import consistency
export function validateReactImport(): boolean {
  if (typeof React !== 'object' || React === null) {
    console.error('React is not properly imported or is null')
    return false
  }
  
  if (typeof React.createElement !== 'function') {
    console.error('React.createElement is not available - React may not be properly initialized')
    return false
  }
  
  return true
}

// Development-only validation that runs on component mount
export function useReactValidation(): void {
  React.useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      if (!validateReactImport()) {
        console.error('React import validation failed - check your import statements')
      }
      
      if (!validateReactHooks()) {
        console.error('React hooks validation failed - check your import statements')
      }
    }
  }, [])
}

// Higher-order component that validates React imports
export function withReactValidation<P extends object>(
  Component: React.ComponentType<P>
): React.ComponentType<P> {
  const WrappedComponent = (props: P) => {
    useReactValidation()
    return <Component {...props} />
  }
  
  WrappedComponent.displayName = `withReactValidation(${Component.displayName || Component.name})`
  
  return WrappedComponent
}

// Check if we're in a proper React context
export function isReactContextValid(): boolean {
  try {
    // Try to access React internals
    return typeof React.version === 'string' && React.version.length > 0
  } catch {
    return false
  }
}
