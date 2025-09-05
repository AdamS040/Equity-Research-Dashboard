/**
 * Service Worker Registration and Management
 * 
 * Handles service worker registration, updates, and communication
 */

interface ServiceWorkerMessage {
  type: string
  payload?: any
}

class ServiceWorkerManager {
  private registration: ServiceWorkerRegistration | null = null
  private isSupportedFlag = 'serviceWorker' in navigator

  async register(): Promise<ServiceWorkerRegistration | null> {
    if (!this.isSupportedFlag) {
      console.log('Service Worker not supported')
      return null
    }

    try {
      this.registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      })

      console.log('Service Worker registered successfully:', this.registration)

      // Handle updates
      this.registration.addEventListener('updatefound', () => {
        const newWorker = this.registration!.installing
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New service worker is available
              this.showUpdateNotification()
            }
          })
        }
      })

      return this.registration
    } catch (error) {
      console.error('Service Worker registration failed:', error)
      return null
    }
  }

  async unregister(): Promise<boolean> {
    if (!this.registration) {
      return false
    }

    try {
      const result = await this.registration.unregister()
      console.log('Service Worker unregistered:', result)
      return result
    } catch (error) {
      console.error('Service Worker unregistration failed:', error)
      return false
    }
  }

  async update(): Promise<void> {
    if (!this.registration) {
      return
    }

    try {
      await this.registration.update()
      console.log('Service Worker update triggered')
    } catch (error) {
      console.error('Service Worker update failed:', error)
    }
  }

  async skipWaiting(): Promise<void> {
    if (!this.registration || !this.registration.waiting) {
      return
    }

    try {
      this.registration.waiting.postMessage({ type: 'SKIP_WAITING' })
      console.log('Skip waiting message sent')
    } catch (error) {
      console.error('Skip waiting failed:', error)
    }
  }

  async sendMessage(message: ServiceWorkerMessage): Promise<any> {
    if (!navigator.serviceWorker.controller) {
      throw new Error('No service worker controller available')
    }

    return new Promise((resolve, reject) => {
      const messageChannel = new MessageChannel()
      
      messageChannel.port1.onmessage = (event) => {
        if (event.data.error) {
          reject(new Error(event.data.error))
        } else {
          resolve(event.data)
        }
      }

      navigator.serviceWorker.controller.postMessage(message, [messageChannel.port2])
    })
  }

  async getCacheStats(): Promise<any> {
    try {
      return await this.sendMessage({ type: 'GET_CACHE_STATS' })
    } catch (error) {
      console.error('Failed to get cache stats:', error)
      return null
    }
  }

  async clearCache(cacheName?: string): Promise<void> {
    try {
      await this.sendMessage({ 
        type: 'CLEAR_CACHE', 
        payload: { cacheName } 
      })
      console.log('Cache cleared:', cacheName || 'all')
    } catch (error) {
      console.error('Failed to clear cache:', error)
    }
  }

  async preloadAssets(urls: string[]): Promise<void> {
    try {
      await this.sendMessage({ 
        type: 'PRELOAD_ASSETS', 
        payload: { urls } 
      })
      console.log('Assets preloaded:', urls.length)
    } catch (error) {
      console.error('Failed to preload assets:', error)
    }
  }

  private showUpdateNotification(): void {
    // Show a notification to the user about the update
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Update Available', {
        body: 'A new version of the app is available. Click to update.',
        icon: '/favicon.ico',
        tag: 'app-update'
      })
    }

    // Dispatch custom event for UI to handle
    window.dispatchEvent(new CustomEvent('sw-update-available'))
  }

  isUpdateAvailable(): boolean {
    return !!(this.registration && this.registration.waiting)
  }

  getRegistration(): ServiceWorkerRegistration | null {
    return this.registration
  }

  isSupported(): boolean {
    return this.isSupportedFlag
  }
}

// Global service worker manager instance
export const serviceWorkerManager = new ServiceWorkerManager()

// React hook for service worker
export function useServiceWorker() {
  const [isSupported, setIsSupported] = useState(false)
  const [isRegistered, setIsRegistered] = useState(false)
  const [isUpdateAvailable, setIsUpdateAvailable] = useState(false)
  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null)

  useEffect(() => {
    const initServiceWorker = async () => {
      const supported = serviceWorkerManager.isSupported()
      setIsSupported(supported)

      if (supported) {
        const reg = await serviceWorkerManager.register()
        setIsRegistered(!!reg)
        setRegistration(reg)

        // Listen for update events
        const handleUpdateAvailable = () => {
          setIsUpdateAvailable(true)
        }

        window.addEventListener('sw-update-available', handleUpdateAvailable)

        return () => {
          window.removeEventListener('sw-update-available', handleUpdateAvailable)
        }
      }
    }

    initServiceWorker()
  }, [])

  const updateServiceWorker = useCallback(async () => {
    await serviceWorkerManager.skipWaiting()
    window.location.reload()
  }, [])

  const clearCache = useCallback(async (cacheName?: string) => {
    await serviceWorkerManager.clearCache(cacheName)
  }, [])

  const preloadAssets = useCallback(async (urls: string[]) => {
    await serviceWorkerManager.preloadAssets(urls)
  }, [])

  return {
    isSupported,
    isRegistered,
    isUpdateAvailable,
    registration,
    updateServiceWorker,
    clearCache,
    preloadAssets
  }
}

// Utility functions
export async function registerServiceWorker(): Promise<boolean> {
  try {
    const registration = await serviceWorkerManager.register()
    return !!registration
  } catch (error) {
    console.error('Service Worker registration failed:', error)
    return false
  }
}

export async function unregisterServiceWorker(): Promise<boolean> {
  return await serviceWorkerManager.unregister()
}

export function isServiceWorkerSupported(): boolean {
  return serviceWorkerManager.isSupported()
}

// Import React hooks
import { useState, useEffect, useCallback } from 'react'
