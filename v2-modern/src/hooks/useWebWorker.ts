/**
 * Web Worker Hook
 * 
 * Provides a React hook for using Web Workers for heavy calculations
 */

import React, { useCallback, useRef, useEffect, useState } from 'react'

interface WorkerMessage {
  id: string
  type: string
  data: any
}

interface WorkerResponse {
  id: string
  type: 'SUCCESS' | 'ERROR'
  data?: any
  error?: string
}

interface UseWebWorkerOptions {
  onSuccess?: (data: any) => void
  onError?: (error: string) => void
  timeout?: number
}

export function useWebWorker(workerScript: string, options: UseWebWorkerOptions = {}) {
  const workerRef = useRef<Worker | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any>(null)
  const messageIdRef = useRef(0)
  const timeoutRef = useRef<number>()

  // Initialize worker
  useEffect(() => {
    try {
      workerRef.current = new Worker(workerScript)
      
      workerRef.current.onmessage = (e: MessageEvent<WorkerResponse>) => {
        const { id, type, data, error } = e.data
        
        if (type === 'SUCCESS') {
          setResult(data)
          setError(null)
          setIsLoading(false)
          options.onSuccess?.(data)
        } else if (type === 'ERROR') {
          setError(error || 'Unknown error')
          setResult(null)
          setIsLoading(false)
          options.onError?.(error || 'Unknown error')
        }
        
        // Clear timeout
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current)
        }
      }
      
      workerRef.current.onerror = (error) => {
        setError(`Worker error: ${error.message}`)
        setResult(null)
        setIsLoading(false)
        options.onError?.(error.message)
      }
    } catch (error) {
      setError(`Failed to create worker: ${error}`)
    }

    return () => {
      if (workerRef.current) {
        workerRef.current.terminate()
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [workerScript, options])

  // Send message to worker
  const postMessage = useCallback((type: string, data: any) => {
    if (!workerRef.current) {
      setError('Worker not initialized')
      return Promise.reject('Worker not initialized')
    }

    return new Promise((resolve, reject) => {
      const id = `msg_${++messageIdRef.current}`
      setIsLoading(true)
      setError(null)
      setResult(null)

      // Set up timeout
      if (options.timeout) {
        timeoutRef.current = setTimeout(() => {
          setError('Worker timeout')
          setIsLoading(false)
          reject('Worker timeout')
        }, options.timeout)
      }

      // Store resolve/reject for this message
      const originalOnMessage = workerRef.current!.onmessage
      workerRef.current!.onmessage = (e: MessageEvent<WorkerResponse>) => {
        const response = e.data
        if (response.id === id) {
          if (response.type === 'SUCCESS') {
            resolve(response.data)
          } else {
            reject(response.error || 'Unknown error')
          }
          // Restore original handler
          workerRef.current!.onmessage = originalOnMessage
        } else {
          // Pass through other messages
          originalOnMessage?.(e)
        }
      }

      const message: WorkerMessage = { id, type, data }
      workerRef.current.postMessage(message)
    })
  }, [options.timeout])

  // Specific calculation methods
  const calculatePortfolioOptimization = useCallback((data: any) => {
    return postMessage('CALCULATE_PORTFOLIO_OPTIMIZATION', data)
  }, [postMessage])

  const calculateRiskMetrics = useCallback((data: any) => {
    return postMessage('CALCULATE_RISK_METRICS', data)
  }, [postMessage])

  const calculateMonteCarlo = useCallback((data: any) => {
    return postMessage('CALCULATE_MONTE_CARLO', data)
  }, [postMessage])

  const calculateTechnicalIndicators = useCallback((data: any) => {
    return postMessage('CALCULATE_TECHNICAL_INDICATORS', data)
  }, [postMessage])

  return {
    isLoading,
    error,
    result,
    postMessage,
    calculatePortfolioOptimization,
    calculateRiskMetrics,
    calculateMonteCarlo,
    calculateTechnicalIndicators
  }
}

// Specific hook for calculations worker
export function useCalculationsWorker(options: UseWebWorkerOptions = {}) {
  return useWebWorker('/workers/calculations.worker.js', {
    timeout: 30000, // 30 second timeout for calculations
    ...options
  })
}
