import { memo, useMemo, useState } from 'react'
import { cn } from '../../utils'

interface VirtualTableProps<T> {
  data: T[]
  height: number
  itemHeight: number
  renderRow: (item: T, index: number) => React.ReactNode
  className?: string
  header?: React.ReactNode
  footer?: React.ReactNode
}

export const VirtualTable = memo(<T,>({
  data,
  height,
  itemHeight,
  renderRow,
  className,
  header,
  footer
}: VirtualTableProps<T>) => {
  return (
    <div className={cn('w-full', className)}>
      {header && (
        <div className="sticky top-0 z-10 bg-white border-b border-neutral-200">
          {header}
        </div>
      )}
      
      <div style={{ height, overflowY: 'auto' }}>
        {data.map((item, index) => (
          <div key={index} style={{ height: itemHeight }} className="flex items-center">
            {renderRow(item, index)}
          </div>
        ))}
      </div>
      
      {footer && (
        <div className="sticky bottom-0 z-10 bg-white border-t border-neutral-200">
          {footer}
        </div>
      )}
    </div>
  )
})

VirtualTable.displayName = 'VirtualTable'

// Hook for virtual scrolling with search and filtering
export const useVirtualTable = <T,>(
  data: T[],
  searchTerm: string = '',
  filterFn?: (item: T, searchTerm: string) => boolean
) => {
  const [scrollOffset, setScrollOffset] = useState(0)
  const [isScrolling, setIsScrolling] = useState(false)

  const filteredData = useMemo(() => {
    if (!searchTerm && !filterFn) return data
    
    return data.filter(item => {
      if (filterFn) {
        return filterFn(item, searchTerm)
      }
      
      // Default search implementation
      return JSON.stringify(item).toLowerCase().includes(searchTerm.toLowerCase())
    })
  }, [data, searchTerm, filterFn])

  const scrollToTop = () => {
    setScrollOffset(0)
  }

  const scrollToItem = (index: number) => {
    setScrollOffset(index * 50) // Assuming 50px item height
  }

  return {
    filteredData,
    scrollOffset,
    isScrolling,
    setIsScrolling,
    scrollToTop,
    scrollToItem
  }
}
