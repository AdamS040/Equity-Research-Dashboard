import React, { createContext, useContext, useEffect, useState } from 'react'
import { clsx } from 'clsx'

// Theme types
export type Theme = 'light' | 'dark' | 'system'
export type ColorScheme = 'light' | 'dark'

interface ThemeContextType {
  theme: Theme
  colorScheme: ColorScheme
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

// Theme provider
export interface ThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: Theme
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ 
  children, 
  defaultTheme = 'system' 
}) => {
  const [theme, setTheme] = useState<Theme>(defaultTheme)
  const [colorScheme, setColorScheme] = useState<ColorScheme>('light')

  // Get system theme preference
  const getSystemTheme = (): ColorScheme => {
    if (typeof window !== 'undefined') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return 'light'
  }

  // Apply theme to document
  const applyTheme = (scheme: ColorScheme) => {
    const root = document.documentElement
    
    if (scheme === 'dark') {
      root.classList.add('dark')
      root.classList.remove('light')
    } else {
      root.classList.add('light')
      root.classList.remove('dark')
    }
    
    setColorScheme(scheme)
  }

  // Handle theme changes
  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)

    // Also update user preferences if they exist
    const userPreferences = localStorage.getItem('user-preferences')
    if (userPreferences) {
      try {
        const parsed = JSON.parse(userPreferences)
        parsed.theme = newTheme
        localStorage.setItem('user-preferences', JSON.stringify(parsed))
      } catch (error) {
        console.error('Failed to update user preferences:', error)
      }
    }

    if (newTheme === 'system') {
      const systemTheme = getSystemTheme()
      applyTheme(systemTheme)
    } else {
      applyTheme(newTheme)
    }
  }

  // Toggle between light and dark
  const toggleTheme = () => {
    const newTheme = colorScheme === 'light' ? 'dark' : 'light'
    handleThemeChange(newTheme)
  }

  useEffect(() => {
    // Load saved theme from localStorage or user preferences
    const savedTheme = localStorage.getItem('theme') as Theme
    const userPreferences = localStorage.getItem('user-preferences')
    let themeToUse = savedTheme || 'system'
    
    if (userPreferences) {
      try {
        const parsed = JSON.parse(userPreferences)
        if (parsed.theme) {
          themeToUse = parsed.theme
        }
      } catch (error) {
        console.error('Failed to parse user preferences:', error)
      }
    }
    
    if (themeToUse) {
      setTheme(themeToUse)
    }

    // Apply initial theme
    if (themeToUse === 'system') {
      const systemTheme = getSystemTheme()
      applyTheme(systemTheme)
    } else if (themeToUse) {
      applyTheme(themeToUse)
    } else {
      applyTheme(getSystemTheme())
    }

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      const currentTheme = localStorage.getItem('theme') as Theme || 'system'
      if (currentTheme === 'system') {
        applyTheme(e.matches ? 'dark' : 'light')
      }
    }

    mediaQuery.addEventListener('change', handleSystemThemeChange)
    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange)
  }, [])

  const value: ThemeContextType = {
    theme,
    colorScheme,
    setTheme: handleThemeChange,
    toggleTheme,
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

// Theme toggle button
export interface ThemeToggleProps {
  className?: string
  showLabel?: boolean
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ className, showLabel = false }) => {
  const { colorScheme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className={clsx(
        'flex items-center space-x-2 p-2 rounded-lg',
        'hover:bg-neutral-100 dark:hover:bg-neutral-800',
        'focus:outline-none focus:ring-2 focus:ring-primary-500',
        'transition-colors duration-200',
        className
      )}
      aria-label={`Switch to ${colorScheme === 'light' ? 'dark' : 'light'} theme`}
    >
      {colorScheme === 'light' ? (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      ) : (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      )}
      {showLabel && (
        <span className="text-sm font-medium">
          {colorScheme === 'light' ? 'Dark' : 'Light'} Mode
        </span>
      )}
    </button>
  )
}

// Theme selector dropdown
export interface ThemeSelectorProps {
  className?: string
}

export const ThemeSelector: React.FC<ThemeSelectorProps> = ({ className }) => {
  const { theme, setTheme } = useTheme()

  const themes = [
    { value: 'light', label: 'Light', icon: '☀️' },
    { value: 'dark', label: 'Dark', icon: '🌙' },
    { value: 'system', label: 'System', icon: '💻' },
  ] as const

  return (
    <div className={clsx('space-y-2', className)}>
      <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300">
        Theme
      </label>
      <div className="space-y-1">
        {themes.map((themeOption) => (
          <label
            key={themeOption.value}
            className={clsx(
              'flex items-center space-x-3 p-2 rounded-lg cursor-pointer',
              'hover:bg-neutral-100 dark:hover:bg-neutral-800',
              'transition-colors duration-200',
              {
                'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300': 
                  theme === themeOption.value,
              }
            )}
          >
            <input
              type="radio"
              name="theme"
              value={themeOption.value}
              checked={theme === themeOption.value}
              onChange={(e) => setTheme(e.target.value as Theme)}
              className="sr-only"
            />
            <span className="text-lg">{themeOption.icon}</span>
            <span className="text-sm font-medium">{themeOption.label}</span>
          </label>
        ))}
      </div>
    </div>
  )
}

// User preferences context
interface UserPreferencesContextType {
  preferences: {
    theme: Theme
    fontSize: 'small' | 'medium' | 'large'
    reducedMotion: boolean
    highContrast: boolean
    dashboardLayout: 'grid' | 'list'
    defaultTimeframe: '1D' | '5D' | '1M' | '3M' | '1Y' | '5Y'
    notifications: {
      priceAlerts: boolean
      newsUpdates: boolean
      marketOpen: boolean
    }
  }
  updatePreference: <K extends keyof UserPreferencesContextType['preferences']>(
    key: K,
    value: UserPreferencesContextType['preferences'][K]
  ) => void
  resetPreferences: () => void
}

const UserPreferencesContext = createContext<UserPreferencesContextType | undefined>(undefined)

export const useUserPreferences = () => {
  const context = useContext(UserPreferencesContext)
  if (!context) {
    throw new Error('useUserPreferences must be used within a UserPreferencesProvider')
  }
  return context
}

// User preferences provider
export interface UserPreferencesProviderProps {
  children: React.ReactNode
}

export const UserPreferencesProvider: React.FC<UserPreferencesProviderProps> = ({ children }) => {
  const { setTheme } = useTheme()
  
  const defaultPreferences = {
    theme: 'system' as Theme,
    fontSize: 'medium' as 'small' | 'medium' | 'large',
    reducedMotion: false,
    highContrast: false,
    dashboardLayout: 'grid' as 'grid' | 'list',
    defaultTimeframe: '1M' as '1D' | '5D' | '1M' | '3M' | '1Y' | '5Y',
    notifications: {
      priceAlerts: true,
      newsUpdates: true,
      marketOpen: true,
    },
  }

  const [preferences, setPreferences] = useState(defaultPreferences)

  useEffect(() => {
    // Load preferences from localStorage
    const savedPreferences = localStorage.getItem('user-preferences')
    if (savedPreferences) {
      try {
        const parsed = JSON.parse(savedPreferences)
        setPreferences({ ...defaultPreferences, ...parsed })
      } catch (error) {
        console.error('Failed to parse user preferences:', error)
      }
    }
  }, [])

  const updatePreference = <K extends keyof typeof preferences>(
    key: K,
    value: typeof preferences[K]
  ) => {
    setPreferences(prev => {
      const updated = { ...prev, [key]: value }
      localStorage.setItem('user-preferences', JSON.stringify(updated))
      
      // If updating theme, also update the ThemeProvider
      if (key === 'theme') {
        setTheme(value as Theme)
      }
      
      return updated
    })
  }

  const resetPreferences = () => {
    setPreferences(defaultPreferences)
    localStorage.removeItem('user-preferences')
  }

  const value: UserPreferencesContextType = {
    preferences,
    updatePreference,
    resetPreferences,
  }

  return (
    <UserPreferencesContext.Provider value={value}>
      {children}
    </UserPreferencesContext.Provider>
  )
}

// Settings panel component
export const SettingsPanel: React.FC = () => {
  const { preferences, updatePreference } = useUserPreferences()

  const themes = [
    { value: 'light', label: 'Light', icon: '☀️' },
    { value: 'dark', label: 'Dark', icon: '🌙' },
    { value: 'system', label: 'System', icon: '💻' },
  ] as const

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-semibold mb-4 text-neutral-900 dark:text-neutral-100">Preferences</h2>
        
        <div className="space-y-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300">
              Theme
            </label>
            <div className="space-y-1">
              {themes.map((themeOption) => (
                <label
                  key={themeOption.value}
                  className={clsx(
                    'flex items-center space-x-3 p-2 rounded-lg cursor-pointer',
                    'hover:bg-neutral-100 dark:hover:bg-neutral-800',
                    'transition-colors duration-200',
                    {
                      'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300': 
                        preferences.theme === themeOption.value,
                    }
                  )}
                >
                  <input
                    type="radio"
                    name="theme"
                    value={themeOption.value}
                    checked={preferences.theme === themeOption.value}
                    onChange={(e) => updatePreference('theme', e.target.value as Theme)}
                    className="sr-only"
                  />
                  <span className="text-lg">{themeOption.icon}</span>
                  <span className="text-sm font-medium">{themeOption.label}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Dashboard Layout
            </label>
            <div className="flex space-x-2">
              <button
                onClick={() => updatePreference('dashboardLayout', 'grid')}
                className={clsx(
                  'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  preferences.dashboardLayout === 'grid'
                    ? 'bg-primary-600 text-white'
                    : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300'
                )}
              >
                Grid
              </button>
              <button
                onClick={() => updatePreference('dashboardLayout', 'list')}
                className={clsx(
                  'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  preferences.dashboardLayout === 'list'
                    ? 'bg-primary-600 text-white'
                    : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300'
                )}
              >
                List
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Default Timeframe
            </label>
            <select
              value={preferences.defaultTimeframe}
              onChange={(e) => updatePreference('defaultTimeframe', e.target.value as any)}
              className="block w-full rounded-md border-neutral-300 dark:border-neutral-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-neutral-800 dark:text-neutral-300"
            >
              <option value="1D">1 Day</option>
              <option value="5D">5 Days</option>
              <option value="1M">1 Month</option>
              <option value="3M">3 Months</option>
              <option value="1Y">1 Year</option>
              <option value="5Y">5 Years</option>
            </select>
          </div>

          <div>
            <h3 className="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
              Notifications
            </h3>
            <div className="space-y-2">
              {Object.entries(preferences.notifications).map(([key, value]) => (
                <label key={key} className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={value}
                    onChange={(e) => updatePreference('notifications', {
                      ...preferences.notifications,
                      [key]: e.target.checked,
                    })}
                    className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
