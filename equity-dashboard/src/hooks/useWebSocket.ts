import { useEffect, useRef, useCallback, useState } from 'react'

interface WebSocketOptions {
  url: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  onMessage?: (data: any) => void
}

interface WebSocketHook {
  isConnected: boolean
  isConnecting: boolean
  error: string | null
  sendMessage: (message: any) => void
  disconnect: () => void
  reconnect: () => void
}

export const useWebSocket = ({
  url,
  reconnectInterval = 5000,
  maxReconnectAttempts = 5,
  onOpen,
  onClose,
  onError,
  onMessage
}: WebSocketOptions): WebSocketHook => {
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const isManualDisconnect = useRef(false)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    setIsConnecting(true)
    setError(null)

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        setIsConnecting(false)
        setReconnectAttempts(0)
        setError(null)
        onOpen?.()
      }

      ws.onclose = () => {
        setIsConnected(false)
        setIsConnecting(false)
        onClose?.()

        // Only attempt to reconnect if it wasn't a manual disconnect
        if (!isManualDisconnect.current && reconnectAttempts < maxReconnectAttempts) {
          setReconnectAttempts(prev => prev + 1)
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect()
          }, reconnectInterval)
        }
      }

      ws.onerror = (event) => {
        setError('WebSocket connection error')
        setIsConnecting(false)
        onError?.(event)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage?.(data)
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }
    } catch (err) {
      setError('Failed to create WebSocket connection')
      setIsConnecting(false)
    }
  }, [url, reconnectInterval, maxReconnectAttempts, reconnectAttempts, onOpen, onClose, onError, onMessage])

  const disconnect = useCallback(() => {
    isManualDisconnect.current = true
    
    if (reconnectTimeoutRef.current) {
      window.clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setIsConnected(false)
    setIsConnecting(false)
  }, [])

  const reconnect = useCallback(() => {
    disconnect()
    isManualDisconnect.current = false
    setReconnectAttempts(0)
    connect()
  }, [disconnect, connect])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify(message))
      } catch (err) {
        setError('Failed to send message')
      }
    } else {
      setError('WebSocket is not connected')
    }
  }, [])

  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    isConnecting,
    error,
    sendMessage,
    disconnect,
    reconnect
  }
}

// Specialized hook for market data WebSocket
export const useMarketDataWebSocket = () => {
  const [marketData, setMarketData] = useState<any>(null)

  const handleMessage = useCallback((data: any) => {
    setMarketData(data)
  }, [])

  const ws = useWebSocket({
    url: (typeof process !== 'undefined' && process.env?.REACT_APP_WS_URL) || 'ws://localhost:8000/ws/market-data',
    onMessage: handleMessage,
    onError: (error) => {
      console.error('Market data WebSocket error:', error)
    }
  })

  return {
    ...ws,
    marketData
  }
}

// Hook for real-time stock quotes
export const useStockQuotesWebSocket = (symbols: string[]) => {
  const [quotes, setQuotes] = useState<Record<string, any>>({})

  const handleMessage = useCallback((data: any) => {
    if (data.type === 'quote' && data.symbol) {
      setQuotes(prev => ({
        ...prev,
        [data.symbol]: data
      }))
    }
  }, [])

  const ws = useWebSocket({
    url: (typeof process !== 'undefined' && process.env?.REACT_APP_WS_URL) || 'ws://localhost:8000/ws/stock-quotes',
    onMessage: handleMessage,
    onError: (error) => {
      console.error('Stock quotes WebSocket error:', error)
    }
  })

  // Subscribe to symbols when connected
  useEffect(() => {
    if (ws.isConnected && symbols.length > 0) {
      ws.sendMessage({
        type: 'subscribe',
        symbols
      })
    }
  }, [ws.isConnected, symbols, ws.sendMessage])

  return {
    ...ws,
    quotes
  }
}
