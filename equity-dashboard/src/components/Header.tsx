import { useState } from 'react'
import { 
  MagnifyingGlassIcon, 
  BellIcon, 
  UserCircleIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/react/24/outline'
import { cn } from '../utils'

interface HeaderProps {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
}

export const Header = ({ sidebarOpen, setSidebarOpen }: HeaderProps) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  
  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  return (
    <header className="bg-white shadow-sm border-b border-neutral-200">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Search */}
          <div className="flex-1 max-w-lg">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-400" />
              <input
                type="text"
                placeholder="Search stocks, symbols..."
                className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
          
          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-neutral-100 transition-colors"
              title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            >
              {theme === 'light' ? (
                <MoonIcon className="w-5 h-5 text-neutral-600" />
              ) : (
                <SunIcon className="w-5 h-5 text-neutral-600" />
              )}
            </button>
            
            {/* Notifications */}
            <button className="p-2 rounded-lg hover:bg-neutral-100 transition-colors relative">
              <BellIcon className="w-5 h-5 text-neutral-600" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-danger-500 rounded-full"></span>
            </button>
            
            {/* User profile */}
            <button className="flex items-center space-x-2 p-2 rounded-lg hover:bg-neutral-100 transition-colors">
              <UserCircleIcon className="w-8 h-8 text-neutral-600" />
              <span className="hidden md:block text-sm font-medium text-neutral-700">
                John Doe
              </span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
