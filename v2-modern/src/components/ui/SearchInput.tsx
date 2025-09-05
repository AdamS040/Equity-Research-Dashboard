import { memo, useState, useEffect, useCallback } from 'react'
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { cn, debounce } from '../../utils'

interface SearchInputProps {
  placeholder?: string
  value: string
  onChange: (value: string) => void
  onClear?: () => void
  debounceMs?: number
  className?: string
  disabled?: boolean
  showClearButton?: boolean
}

export const SearchInput = memo(({
  placeholder = 'Search...',
  value,
  onChange,
  onClear,
  debounceMs = 300,
  className,
  disabled = false,
  showClearButton = true
}: SearchInputProps) => {
  const [localValue, setLocalValue] = useState(value)

  // Debounced onChange handler
  const debouncedOnChange = useCallback(
    debounce((searchValue: string) => {
      onChange(searchValue)
    }, debounceMs),
    [onChange, debounceMs]
  )

  // Update local value when external value changes
  useEffect(() => {
    setLocalValue(value)
  }, [value])

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setLocalValue(newValue)
    debouncedOnChange(newValue)
  }

  // Handle clear
  const handleClear = () => {
    setLocalValue('')
    onChange('')
    onClear?.()
  }

  // Handle key down
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      handleClear()
    }
  }

  return (
    <div className={cn('relative', className)}>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon className="h-5 w-5 text-neutral-400" />
        </div>
        
        <input
          type="text"
          value={localValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className={cn(
            'block w-full pl-10 pr-10 py-2 border border-neutral-300 rounded-lg',
            'focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'disabled:bg-neutral-50 disabled:text-neutral-500 disabled:cursor-not-allowed',
            'placeholder:text-neutral-400',
            'transition-colors duration-200'
          )}
        />
        
        {showClearButton && localValue && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <button
              type="button"
              onClick={handleClear}
              disabled={disabled}
              className={cn(
                'text-neutral-400 hover:text-neutral-600 transition-colors',
                'disabled:cursor-not-allowed disabled:hover:text-neutral-400'
              )}
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  )
})

SearchInput.displayName = 'SearchInput'
