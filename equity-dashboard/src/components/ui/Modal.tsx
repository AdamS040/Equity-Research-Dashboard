import React, { useEffect, useRef } from 'react'
import { clsx } from 'clsx'
import { ModalProps } from '../../types/design-system'

/**
 * Modal component with backdrop and accessibility features
 * 
 * @example
 * ```tsx
 * <Modal
 *   isOpen={isOpen}
 *   onClose={onClose}
 *   title="Confirm Action"
 *   size="md"
 * >
 *   <p>Are you sure you want to proceed?</p>
 * </Modal>
 * ```
 */
export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  size = 'md',
  closeOnBackdropClick = true,
  closeOnEscape = true,
  showCloseButton = true,
  children,
  footer,
  className,
  ...props
}) => {
  const modalRef = useRef<HTMLDivElement>(null)
  const previousActiveElement = useRef<HTMLElement | null>(null)

  // Handle escape key
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, closeOnEscape, onClose])

  // Handle focus management
  useEffect(() => {
    if (isOpen) {
      // Store the currently focused element
      previousActiveElement.current = document.activeElement as HTMLElement
      
      // Focus the modal
      setTimeout(() => {
        modalRef.current?.focus()
      }, 0)
    } else {
      // Restore focus to the previously focused element
      if (previousActiveElement.current) {
        previousActiveElement.current.focus()
      }
    }
  }, [isOpen])

  // Handle backdrop click
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (closeOnBackdropClick && e.target === e.currentTarget) {
      onClose()
    }
  }

  const sizeClasses = {
    xs: 'max-w-xs',
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-full mx-4',
  }

  const modalClasses = clsx(
    'relative bg-white rounded-lg shadow-xl',
    'w-full mx-auto',
    sizeClasses[size],
    className
  )

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-modal overflow-y-auto"
      aria-labelledby={title ? 'modal-title' : undefined}
      aria-modal="true"
      role="dialog"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        aria-hidden="true"
        onClick={handleBackdropClick}
      />
      
      {/* Modal container */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div
          ref={modalRef}
          className={modalClasses}
          tabIndex={-1}
          {...props}
        >
          {/* Header */}
          {(title || showCloseButton) && (
            <div className="flex items-center justify-between p-6 border-b border-neutral-200">
              {title && (
                <h3
                  id="modal-title"
                  className="text-lg font-semibold text-neutral-900"
                >
                  {title}
                </h3>
              )}
              {showCloseButton && (
                <button
                  type="button"
                  className="text-neutral-400 hover:text-neutral-600 transition-colors"
                  onClick={onClose}
                  aria-label="Close modal"
                >
                  <svg
                    className="h-6 w-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              )}
            </div>
          )}
          
          {/* Body */}
          <div className="p-6">
            {children}
          </div>
          
          {/* Footer */}
          {footer && (
            <div className="flex items-center justify-end space-x-3 p-6 border-t border-neutral-200 bg-neutral-50 rounded-b-lg">
              {footer}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

Modal.displayName = 'Modal'
