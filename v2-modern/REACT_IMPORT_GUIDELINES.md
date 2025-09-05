# React Import Guidelines

## Overview

This document outlines the proper way to import React and React hooks to prevent "Cannot read properties of null (reading 'useState')" errors.

## The Problem

Inconsistent React import patterns can cause React hooks to be `null` during lazy loading, especially when:
- Components are loaded asynchronously
- There are complex retry mechanisms in lazy loading
- React Strict Mode causes multiple mount/unmount cycles

## The Solution

### ✅ Correct Import Pattern

Always import React explicitly when using hooks:

```typescript
import React, { useState, useEffect, useCallback } from 'react'
```

### ❌ Incorrect Import Pattern

Do not import hooks without the React namespace:

```typescript
import { useState, useEffect } from 'react'  // Can cause issues
```

## Why This Matters

When you import hooks without the React namespace, they rely on the React runtime being properly initialized. During lazy loading with complex retry mechanisms, there can be brief moments where the React context is not fully established, causing hooks to be `null`.

## Files That Were Fixed

The following files were updated to use consistent React imports:

- `src/pages/Settings.tsx`
- `src/pages/Analysis.tsx`
- `src/components/Header.tsx`
- `src/hooks/useWebWorker.ts`
- `src/hooks/useWebSocket.ts`
- `src/hooks/usePerformance.ts`
- `src/components/dashboard/MarketIndices.tsx`
- `src/hooks/api/useMarketData.ts`

## Additional Improvements

### 1. Simplified Lazy Loading

The `createLazyComponent` function was simplified to reduce complexity and potential timing issues.

### 2. Defensive Programming

Added defensive checks in critical components:

```typescript
export const Settings = () => {
  // Defensive check for React hooks
  if (typeof useState !== 'function') {
    console.error('useState is not available - React may not be properly initialized')
    return <div>Loading...</div>
  }
  
  const [activeTab, setActiveTab] = useState('profile')
  // ... rest of component
}
```

### 3. React Validation Utilities

Created `src/utils/reactValidation.ts` with utilities to validate React imports and prevent future issues.

### 4. Enhanced Error Boundaries

Updated error boundaries to provide better context for React hook errors.

## Best Practices

1. **Always import React explicitly** when using hooks
2. **Use the validation utilities** in development mode
3. **Keep lazy loading simple** - avoid overly complex retry mechanisms
4. **Add defensive checks** in critical components
5. **Monitor console warnings** for React import issues

## Development Tools

Use the React validation utilities in development:

```typescript
import { useReactValidation, withReactValidation } from './utils/reactValidation'

// In a component
const MyComponent = () => {
  useReactValidation() // Validates React imports on mount
  // ... component logic
}

// As a HOC
export default withReactValidation(MyComponent)
```

## Testing

To test if the fixes work:

1. Clear browser cache
2. Navigate to Settings page
3. Navigate to Analysis page
4. Refresh the page multiple times
5. Check browser console for any React hook errors

The errors should no longer occur, and if they do, the enhanced error boundaries will provide better context.
