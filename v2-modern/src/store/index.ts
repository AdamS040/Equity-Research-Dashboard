import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { AppState, Stock, Portfolio } from '../types'

interface AppStore extends AppState {
  // Theme
  setTheme: (theme: 'light' | 'dark') => void
  toggleTheme: () => void
  
  // Sidebar
  setSidebarOpen: (open: boolean) => void
  toggleSidebar: () => void
  
  // Portfolio
  setSelectedPortfolio: (portfolioId: string | null) => void
  
  // Stock
  setSelectedStock: (symbol: string | null) => void
  
  // Watchlist
  watchlist: string[]
  addToWatchlist: (symbol: string) => void
  removeFromWatchlist: (symbol: string) => void
  isInWatchlist: (symbol: string) => boolean
}

export const useAppStore = create<AppStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      theme: 'light',
      sidebarOpen: true,
      selectedPortfolio: null,
      selectedStock: null,
      watchlist: [],
      
      // Theme actions
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
      
      // Sidebar actions
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
      // Portfolio actions
      setSelectedPortfolio: (portfolioId) => set({ selectedPortfolio: portfolioId }),
      
      // Stock actions
      setSelectedStock: (symbol) => set({ selectedStock: symbol }),
      
      // Watchlist actions
      addToWatchlist: (symbol) => set((state) => ({
        watchlist: [...state.watchlist, symbol]
      })),
      removeFromWatchlist: (symbol) => set((state) => ({
        watchlist: state.watchlist.filter(s => s !== symbol)
      })),
      isInWatchlist: (symbol) => get().watchlist.includes(symbol),
    }),
    {
      name: 'equity-dashboard-store',
    }
  )
)
