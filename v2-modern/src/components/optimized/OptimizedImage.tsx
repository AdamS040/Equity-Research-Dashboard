/**
 * Optimized Image Component
 * 
 * Provides image optimization with:
 * - Lazy loading with intersection observer
 * - WebP format with fallbacks
 * - Progressive loading
 * - Error handling and retry
 * - Responsive images
 */

import React, { memo, useState, useRef, useCallback, useEffect } from 'react'
import { useIntersectionObserver } from '../../hooks/usePerformance'

interface OptimizedImageProps {
  src: string
  alt: string
  width?: number
  height?: number
  className?: string
  placeholder?: string
  fallback?: string
  priority?: boolean
  quality?: number
  sizes?: string
  onLoad?: () => void
  onError?: () => void
  loading?: 'lazy' | 'eager'
}

// Image loading states
type ImageState = 'loading' | 'loaded' | 'error' | 'placeholder'

// Placeholder component
const ImagePlaceholder = memo<{
  width?: number
  height?: number
  className?: string
}>(({ width, height, className }) => (
  <div
    className={`bg-gray-200 animate-pulse flex items-center justify-center ${className}`}
    style={{ width, height }}
  >
    <svg
      className="w-8 h-8 text-gray-400"
      fill="currentColor"
      viewBox="0 0 20 20"
    >
      <path
        fillRule="evenodd"
        d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
        clipRule="evenodd"
      />
    </svg>
  </div>
))

ImagePlaceholder.displayName = 'ImagePlaceholder'

// Error component
const ImageError = memo<{
  width?: number
  height?: number
  className?: string
  onRetry?: () => void
}>(({ width, height, className, onRetry }) => (
  <div
    className={`bg-gray-100 flex flex-col items-center justify-center text-gray-500 ${className}`}
    style={{ width, height }}
  >
    <svg
      className="w-8 h-8 mb-2"
      fill="currentColor"
      viewBox="0 0 20 20"
    >
      <path
        fillRule="evenodd"
        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
        clipRule="evenodd"
      />
    </svg>
    <p className="text-xs text-center">Failed to load</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="mt-2 text-xs text-blue-600 hover:text-blue-800"
      >
        Retry
      </button>
    )}
  </div>
))

ImageError.displayName = 'ImageError'

// Progressive loading component
const ProgressiveImage = memo<{
  src: string
  alt: string
  width?: number
  height?: number
  className?: string
  onLoad?: () => void
  onError?: () => void
}>(({ src, alt, width, height, className, onLoad, onError }) => {
  const [imageState, setImageState] = useState<ImageState>('loading')
  const [currentSrc, setCurrentSrc] = useState<string>('')
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    setCurrentSrc(src)
    setImageState('loading')
  }, [src])

  const handleLoad = useCallback(() => {
    setImageState('loaded')
    onLoad?.()
  }, [onLoad])

  const handleError = useCallback(() => {
    setImageState('error')
    onError?.()
  }, [onError])

  const handleRetry = useCallback(() => {
    setImageState('loading')
    // Force reload by adding timestamp
    setCurrentSrc(`${src}?retry=${Date.now()}`)
  }, [src])

  if (imageState === 'error') {
    return (
      <ImageError
        width={width}
        height={height}
        className={className}
        onRetry={handleRetry}
      />
    )
  }

  return (
    <div className="relative" style={{ width, height }}>
      {imageState === 'loading' && (
        <ImagePlaceholder
          width={width}
          height={height}
          className="absolute inset-0"
        />
      )}
      <img
        ref={imgRef}
        src={currentSrc}
        alt={alt}
        width={width}
        height={height}
        className={`${className} ${imageState === 'loaded' ? 'opacity-100' : 'opacity-0'} transition-opacity duration-300`}
        onLoad={handleLoad}
        onError={handleError}
        loading="lazy"
        decoding="async"
      />
    </div>
  )
})

ProgressiveImage.displayName = 'ProgressiveImage'

// Main optimized image component
export const OptimizedImage = memo<OptimizedImageProps>(({
  src,
  alt,
  width,
  height,
  className = '',
  placeholder,
  fallback,
  priority = false,
  quality = 80,
  sizes,
  onLoad,
  onError,
  loading = 'lazy'
}) => {
  const [imageState, setImageState] = useState<ImageState>('placeholder')
  const [retryCount, setRetryCount] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)
  const maxRetries = 3

  // Intersection observer for lazy loading
  const { isIntersecting, hasIntersected } = useIntersectionObserver(containerRef, {
    threshold: 0.1,
    rootMargin: '50px'
  })

  // Generate optimized image URLs
  const generateOptimizedSrc = useCallback((originalSrc: string, format: 'webp' | 'jpeg' = 'webp') => {
    // In a real implementation, this would use an image optimization service
    // like Cloudinary, ImageKit, or Next.js Image Optimization
    const params = new URLSearchParams({
      format,
      quality: quality.toString(),
      ...(width && { w: width.toString() }),
      ...(height && { h: height.toString() })
    })
    
    return `${originalSrc}?${params.toString()}`
  }, [quality, width, height])

  // Handle image load
  const handleLoad = useCallback(() => {
    setImageState('loaded')
    onLoad?.()
  }, [onLoad])

  // Handle image error
  const handleError = useCallback(() => {
    if (retryCount < maxRetries) {
      setRetryCount(prev => prev + 1)
      setImageState('loading')
      // Retry with different format or fallback
      setTimeout(() => {
        setImageState('placeholder')
      }, 1000)
    } else {
      setImageState('error')
      onError?.()
    }
  }, [retryCount, maxRetries, onError])

  // Handle retry
  const handleRetry = useCallback(() => {
    setRetryCount(0)
    setImageState('placeholder')
  }, [])

  // Determine if image should load
  const shouldLoad = priority || hasIntersected

  // Generate source sets for responsive images
  const srcSet = useMemo(() => {
    if (!shouldLoad) return ''
    
    const baseSrc = generateOptimizedSrc(src, 'webp')
    const fallbackSrc = generateOptimizedSrc(src, 'jpeg')
    
    return `${baseSrc} 1x, ${fallbackSrc} 2x`
  }, [src, shouldLoad, generateOptimizedSrc])

  // Render based on state
  if (!shouldLoad) {
    return (
      <div ref={containerRef} style={{ width, height }}>
        <ImagePlaceholder
          width={width}
          height={height}
          className={className}
        />
      </div>
    )
  }

  if (imageState === 'error') {
    return (
      <div ref={containerRef} style={{ width, height }}>
        <ImageError
          width={width}
          height={height}
          className={className}
          onRetry={handleRetry}
        />
      </div>
    )
  }

  return (
    <div ref={containerRef} style={{ width, height }}>
      <picture>
        {/* WebP source for modern browsers */}
        <source
          srcSet={generateOptimizedSrc(src, 'webp')}
          type="image/webp"
          sizes={sizes}
        />
        {/* JPEG fallback */}
        <source
          srcSet={generateOptimizedSrc(src, 'jpeg')}
          type="image/jpeg"
          sizes={sizes}
        />
        {/* Fallback image */}
        <ProgressiveImage
          src={fallback || generateOptimizedSrc(src, 'jpeg')}
          alt={alt}
          width={width}
          height={height}
          className={className}
          onLoad={handleLoad}
          onError={handleError}
        />
      </picture>
    </div>
  )
})

OptimizedImage.displayName = 'OptimizedImage'

// Hook for image preloading
export function useImagePreload(src: string) {
  const [isLoaded, setIsLoaded] = useState(false)
  const [isError, setIsError] = useState(false)

  useEffect(() => {
    if (!src) return

    const img = new Image()
    img.onload = () => setIsLoaded(true)
    img.onerror = () => setIsError(true)
    img.src = src

    return () => {
      img.onload = null
      img.onerror = null
    }
  }, [src])

  return { isLoaded, isError }
}

// Utility function to generate responsive image URLs
export function generateResponsiveImageUrl(
  baseUrl: string,
  options: {
    width?: number
    height?: number
    quality?: number
    format?: 'webp' | 'jpeg' | 'png'
    devicePixelRatio?: number
  } = {}
) {
  const {
    width,
    height,
    quality = 80,
    format = 'webp',
    devicePixelRatio = 1
  } = options

  const params = new URLSearchParams({
    format,
    quality: quality.toString(),
    ...(width && { w: (width * devicePixelRatio).toString() }),
    ...(height && { h: (height * devicePixelRatio).toString() })
  })

  return `${baseUrl}?${params.toString()}`
}

// Export with custom comparison for React.memo
export const MemoizedOptimizedImage = memo(OptimizedImage, (prevProps, nextProps) => {
  return (
    prevProps.src === nextProps.src &&
    prevProps.alt === nextProps.alt &&
    prevProps.width === nextProps.width &&
    prevProps.height === nextProps.height &&
    prevProps.className === nextProps.className &&
    prevProps.priority === nextProps.priority &&
    prevProps.quality === nextProps.quality
  )
})
