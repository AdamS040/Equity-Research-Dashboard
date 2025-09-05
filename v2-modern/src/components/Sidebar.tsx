import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  HomeIcon, 
  ChartBarIcon, 
  DocumentTextIcon, 
  Cog6ToothIcon,
  XMarkIcon,
  Bars3Icon,
  BuildingOfficeIcon,
  ChartPieIcon
} from '@heroicons/react/24/outline'
import { cn } from '../utils'

const navigation = [
  { 
    name: 'Dashboard', 
    href: '/', 
    icon: HomeIcon,
    description: 'Overview and key metrics'
  },
  { 
    name: 'Stock Analysis', 
    href: '/analysis', 
    icon: ChartBarIcon,
    description: 'Individual stock research'
  },
  { 
    name: 'Portfolio', 
    href: '/portfolio', 
    icon: ChartPieIcon,
    description: 'Portfolio management'
  },
  { 
    name: 'Reports', 
    href: '/research', 
    icon: DocumentTextIcon,
    description: 'Research reports'
  },
  { 
    name: 'Settings', 
    href: '/settings', 
    icon: Cog6ToothIcon,
    description: 'Application settings'
  },
]

interface SidebarProps {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
}

export const Sidebar = ({ sidebarOpen, setSidebarOpen }: SidebarProps) => {
  const location = useLocation()
  
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  const sidebarVariants = {
    open: {
      width: 256, // w-64
      transition: {
        duration: 0.3,
        ease: [0.4, 0, 0.2, 1]
      }
    },
    closed: {
      width: 64, // w-16
      transition: {
        duration: 0.3,
        ease: [0.4, 0, 0.2, 1]
      }
    }
  }

  const contentVariants = {
    open: {
      opacity: 1,
      transition: {
        duration: 0.2,
        delay: 0.1
      }
    },
    closed: {
      opacity: 0,
      transition: {
        duration: 0.1
      }
    }
  }

  return (
    <>
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
            onClick={toggleSidebar}
          />
        )}
      </AnimatePresence>
      
      {/* Sidebar */}
      <motion.div 
        variants={sidebarVariants}
        animate={sidebarOpen ? "open" : "closed"}
        className="fixed inset-y-0 left-0 z-50 bg-white dark:bg-neutral-900 shadow-xl border-r border-neutral-200 dark:border-neutral-700 lg:translate-x-0"
        initial={false}
        role="navigation"
        aria-label="Main navigation"
        id="navigation"
      >
        {/* Header */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-neutral-200 dark:border-neutral-700">
          <AnimatePresence mode="wait">
            {sidebarOpen ? (
              <motion.div
                key="logo-text"
                variants={contentVariants}
                initial="closed"
                animate="open"
                exit="closed"
                className="flex items-center space-x-3"
              >
                <BuildingOfficeIcon className="w-8 h-8 text-primary-600 dark:text-primary-400" />
                <div>
                  <h1 className="text-lg font-bold text-primary-600 dark:text-primary-400">Equity</h1>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400">Research Dashboard</p>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="logo-icon"
                variants={contentVariants}
                initial="closed"
                animate="open"
                exit="closed"
                className="flex justify-center w-full"
              >
                <BuildingOfficeIcon className="w-8 h-8 text-primary-600 dark:text-primary-400" />
              </motion.div>
            )}
          </AnimatePresence>
          
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
            aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          >
            {sidebarOpen ? (
              <XMarkIcon className="w-5 h-5 text-neutral-600 dark:text-neutral-400" />
            ) : (
              <Bars3Icon className="w-5 h-5 text-neutral-600 dark:text-neutral-400" />
            )}
          </button>
        </div>
        
        {/* Navigation */}
        <nav className="mt-6 px-3">
          <ul className="space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={cn(
                      'group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200 relative',
                      isActive
                        ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 shadow-sm'
                        : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 hover:text-neutral-900 dark:hover:text-neutral-100'
                    )}
                    title={!sidebarOpen ? item.name : undefined}
                  >
                    {/* Active indicator */}
                    {isActive && (
                      <motion.div
                        layoutId="activeIndicator"
                        className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary-600 rounded-r-full"
                        transition={{ type: "spring", stiffness: 500, damping: 30 }}
                      />
                    )}
                    
                    <item.icon className={cn(
                      "w-5 h-5 flex-shrink-0 transition-colors",
                      isActive ? "text-primary-600 dark:text-primary-400" : "text-neutral-500 dark:text-neutral-400 group-hover:text-neutral-700 dark:group-hover:text-neutral-300"
                    )} />
                    
                    <AnimatePresence>
                      {sidebarOpen && (
                        <motion.div
                          variants={contentVariants}
                          initial="closed"
                          animate="open"
                          exit="closed"
                          className="ml-3 flex-1"
                        >
                          <div className="font-medium">{item.name}</div>
                          <div className="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">
                            {item.description}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-neutral-200 dark:border-neutral-700">
          <AnimatePresence>
            {sidebarOpen && (
              <motion.div
                variants={contentVariants}
                initial="closed"
                animate="open"
                exit="closed"
                className="text-xs text-neutral-500 dark:text-neutral-400 text-center"
              >
                <p>Equity Research Dashboard</p>
                <p className="mt-1">v1.0.0</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </>
  )
}
