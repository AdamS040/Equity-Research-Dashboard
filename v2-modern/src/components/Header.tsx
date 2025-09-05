import { useState, useRef, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MagnifyingGlassIcon, 
  BellIcon, 
  UserCircleIcon,
  SunIcon,
  MoonIcon,
  ChevronDownIcon,
  Bars3Icon,
  HomeIcon,
  ChartBarIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
  ChartPieIcon,
  ArrowRightOnRectangleIcon,
  UserIcon,
  CogIcon
} from '@heroicons/react/24/outline'
import { cn, debounce } from '../utils'

interface HeaderProps {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
}

// Mock stock data for autocomplete
const mockStocks = [
  { symbol: 'AAPL', name: 'Apple Inc.', price: 175.43, change: 2.34 },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 142.56, change: -1.23 },
  { symbol: 'MSFT', name: 'Microsoft Corporation', price: 378.85, change: 5.67 },
  { symbol: 'AMZN', name: 'Amazon.com Inc.', price: 151.94, change: -0.89 },
  { symbol: 'TSLA', name: 'Tesla Inc.', price: 248.50, change: 12.45 },
  { symbol: 'META', name: 'Meta Platforms Inc.', price: 324.12, change: 3.21 },
  { symbol: 'NVDA', name: 'NVIDIA Corporation', price: 875.28, change: 45.67 },
  { symbol: 'NFLX', name: 'Netflix Inc.', price: 485.73, change: -2.15 },
]

const routeMap = {
  '/': { name: 'Dashboard', icon: HomeIcon },
  '/analysis': { name: 'Stock Analysis', icon: ChartBarIcon },
  '/portfolio': { name: 'Portfolio', icon: ChartPieIcon },
  '/research': { name: 'Reports', icon: DocumentTextIcon },
  '/settings': { name: 'Settings', icon: Cog6ToothIcon },
}

export const Header = ({ sidebarOpen, setSidebarOpen }: HeaderProps) => {
  const location = useLocation()
  const navigate = useNavigate()
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<typeof mockStocks>([])
  const [showSearchResults, setShowSearchResults] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  
  const searchRef = useRef<HTMLDivElement>(null)
  const userMenuRef = useRef<HTMLDivElement>(null)
  const notificationsRef = useRef<HTMLDivElement>(null)

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  const handleSearch = debounce((query: string) => {
    if (query.length > 0) {
      const results = mockStocks.filter(
        stock => 
          stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
          stock.name.toLowerCase().includes(query.toLowerCase())
      )
      setSearchResults(results)
      setShowSearchResults(true)
    } else {
      setSearchResults([])
      setShowSearchResults(false)
    }
  }, 300)

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value
    setSearchQuery(query)
    handleSearch(query)
  }

  const handleStockSelect = (stock: typeof mockStocks[0]) => {
    setSearchQuery(stock.symbol)
    setShowSearchResults(false)
    navigate(`/analysis?symbol=${stock.symbol}`)
  }

  const getBreadcrumbs = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean)
    const breadcrumbs = [{ name: 'Dashboard', href: '/', icon: HomeIcon }]
    
    pathSegments.forEach((segment, index) => {
      const href = '/' + pathSegments.slice(0, index + 1).join('/')
      const route = routeMap[href as keyof typeof routeMap]
      if (route) {
        breadcrumbs.push({ name: route.name, href, icon: route.icon })
      }
    })
    
    return breadcrumbs
  }

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchResults(false)
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false)
      }
      if (notificationsRef.current && !notificationsRef.current.contains(event.target as Node)) {
        setShowNotifications(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const breadcrumbs = getBreadcrumbs()

  return (
    <header className="bg-white shadow-sm border-b border-neutral-200 sticky top-0 z-30" id="search">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Mobile menu button */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 rounded-lg hover:bg-neutral-100 transition-colors"
            aria-label="Toggle sidebar"
          >
            <Bars3Icon className="w-5 h-5 text-neutral-600" />
          </button>

          {/* Breadcrumbs */}
          <div className="hidden lg:flex items-center space-x-2 text-sm">
            {breadcrumbs.map((crumb, index) => (
              <div key={crumb.href} className="flex items-center">
                {index > 0 && (
                  <ArrowRightOnRectangleIcon className="w-4 h-4 text-neutral-400 mx-2 rotate-90" />
                )}
                <span className={cn(
                  "flex items-center space-x-1",
                  index === breadcrumbs.length - 1 
                    ? "text-neutral-900 font-medium" 
                    : "text-neutral-500"
                )}>
                  <crumb.icon className="w-4 h-4" />
                  <span>{crumb.name}</span>
                </span>
              </div>
            ))}
          </div>
          
          {/* Search */}
          <div className="flex-1 max-w-lg mx-4" ref={searchRef}>
            <div className="relative">
              <label htmlFor="stock-search" className="sr-only">
                Search stocks and symbols
              </label>
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-400" aria-hidden="true" />
              <input
                id="stock-search"
                type="text"
                placeholder="Search stocks, symbols..."
                value={searchQuery}
                onChange={handleSearchChange}
                onFocus={() => searchResults.length > 0 && setShowSearchResults(true)}
                className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                aria-expanded={showSearchResults}
                aria-haspopup="listbox"
                aria-autocomplete="list"
                role="combobox"
                aria-describedby="search-results"
              />
              
              {/* Search Results Dropdown */}
              <AnimatePresence>
                {showSearchResults && searchResults.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="absolute top-full left-0 right-0 mt-1 bg-white border border-neutral-200 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto"
                    id="search-results"
                    role="listbox"
                    aria-label="Search results"
                  >
                    {searchResults.map((stock) => (
                      <button
                        key={stock.symbol}
                        onClick={() => handleStockSelect(stock)}
                        className="w-full px-4 py-3 text-left hover:bg-neutral-50 border-b border-neutral-100 last:border-b-0"
                        role="option"
                        aria-label={`${stock.symbol} - ${stock.name}, Price: $${stock.price.toFixed(2)}, Change: ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium text-neutral-900">{stock.symbol}</div>
                            <div className="text-sm text-neutral-500">{stock.name}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium text-neutral-900">
                              ${stock.price.toFixed(2)}
                            </div>
                            <div className={cn(
                              "text-sm",
                              stock.change >= 0 ? "text-success-600" : "text-danger-600"
                            )}>
                              {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}
                            </div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
          
          {/* Right side actions */}
          <div className="flex items-center space-x-2">
            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-neutral-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
              title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            >
              {theme === 'light' ? (
                <MoonIcon className="w-5 h-5 text-neutral-600" />
              ) : (
                <SunIcon className="w-5 h-5 text-neutral-600" />
              )}
            </button>
            
            {/* Notifications */}
            <div className="relative" ref={notificationsRef}>
              <button 
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 rounded-lg hover:bg-neutral-100 transition-colors relative focus:outline-none focus:ring-2 focus:ring-primary-500"
                aria-label="Notifications"
              >
                <BellIcon className="w-5 h-5 text-neutral-600" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-danger-500 rounded-full"></span>
              </button>
              
              <AnimatePresence>
                {showNotifications && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="absolute right-0 top-full mt-1 w-80 bg-white border border-neutral-200 rounded-lg shadow-lg z-50"
                  >
                    <div className="p-4 border-b border-neutral-200">
                      <h3 className="font-medium text-neutral-900">Notifications</h3>
                    </div>
                    <div className="p-4">
                      <div className="text-sm text-neutral-500 text-center">
                        No new notifications
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            
            {/* User profile */}
            <div className="relative" ref={userMenuRef}>
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 p-2 rounded-lg hover:bg-neutral-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
                aria-label="User menu"
              >
                <UserCircleIcon className="w-8 h-8 text-neutral-600" />
                <span className="hidden md:block text-sm font-medium text-neutral-700">
                  John Doe
                </span>
                <ChevronDownIcon className="w-4 h-4 text-neutral-500" />
              </button>
              
              <AnimatePresence>
                {showUserMenu && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="absolute right-0 top-full mt-1 w-48 bg-white border border-neutral-200 rounded-lg shadow-lg z-50"
                  >
                    <div className="py-1">
                      <button className="w-full px-4 py-2 text-left text-sm text-neutral-700 hover:bg-neutral-50 flex items-center space-x-2">
                        <UserIcon className="w-4 h-4" />
                        <span>Profile</span>
                      </button>
                      <button className="w-full px-4 py-2 text-left text-sm text-neutral-700 hover:bg-neutral-50 flex items-center space-x-2">
                        <CogIcon className="w-4 h-4" />
                        <span>Settings</span>
                      </button>
                      <div className="border-t border-neutral-200 my-1"></div>
                      <button className="w-full px-4 py-2 text-left text-sm text-danger-600 hover:bg-danger-50 flex items-center space-x-2">
                        <ArrowRightOnRectangleIcon className="w-4 h-4" />
                        <span>Sign out</span>
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
