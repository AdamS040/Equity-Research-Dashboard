import React, { useState, useCallback, useMemo } from 'react'
import { 
  ArrowDownTrayIcon, 
  DocumentTextIcon,
  DocumentIcon,
  TableCellsIcon,
  PhotoIcon,
  ShareIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { 
  Button, 
  Card, 
  Badge, 
  Spinner, 
  ErrorDisplay, 
  Heading, 
  Text,
  useAccessibility
} from '../ui'
import { clsx } from 'clsx'

interface ReportExportProps {
  reportId: string
  reportTitle: string
  onClose: () => void
  onExportComplete?: (exportData: any) => void
}

const ReportExport: React.FC<ReportExportProps> = ({
  reportId,
  reportTitle,
  onClose,
  onExportComplete
}) => {
  const { reducedMotion } = useAccessibility()
  const [selectedFormat, setSelectedFormat] = useState<string>('pdf')
  const [isExporting, setIsExporting] = useState(false)
  const [exportProgress, setExportProgress] = useState(0)
  const [exportStatus, setExportStatus] = useState<'idle' | 'exporting' | 'completed' | 'error'>('idle')
  const [error, setError] = useState<string | null>(null)
  const [exportOptions, setExportOptions] = useState({
    includeCharts: true,
    includeTables: true,
    includeMetadata: true,
    quality: 'high',
    pageSize: 'A4',
    orientation: 'portrait'
  })

  const exportFormats = useMemo(() => [
    {
      id: 'pdf',
      name: 'PDF Document',
      description: 'Professional PDF with charts and tables',
      icon: DocumentTextIcon,
      color: 'danger',
      features: ['High quality', 'Print ready', 'Charts included', 'Tables included']
    },
    {
      id: 'excel',
      name: 'Excel Workbook',
      description: 'Excel file with multiple sheets and data',
      icon: TableCellsIcon,
      color: 'success',
      features: ['Multiple sheets', 'Formulas', 'Charts', 'Data tables']
    },
    {
      id: 'html',
      name: 'HTML Document',
      description: 'Interactive HTML with responsive design',
      icon: DocumentIcon,
      color: 'primary',
      features: ['Interactive', 'Responsive', 'Web ready', 'Charts included']
    },
    {
      id: 'image',
      name: 'Image (PNG)',
      description: 'High-quality image export',
      icon: PhotoIcon,
      color: 'warning',
      features: ['High resolution', 'PNG format', 'Chart export', 'Print ready']
    },
    {
      id: 'csv',
      name: 'CSV Data',
      description: 'Comma-separated values for data analysis',
      icon: TableCellsIcon,
      color: 'neutral',
      features: ['Data only', 'Analysis ready', 'Small file size', 'Universal format']
    }
  ], [])

  const handleExport = useCallback(async () => {
    try {
      setIsExporting(true)
      setExportStatus('exporting')
      setError(null)
      setExportProgress(0)

      // Simulate export progress
      const progressInterval = setInterval(() => {
        setExportProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))

      clearInterval(progressInterval)
      setExportProgress(100)
      setExportStatus('completed')

      // Simulate download
      const blob = new Blob(['Mock export data'], { type: 'application/octet-stream' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${reportTitle.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${selectedFormat}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      onExportComplete?.({
        format: selectedFormat,
        reportId,
        timestamp: new Date().toISOString()
      })

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed')
      setExportStatus('error')
    } finally {
      setIsExporting(false)
    }
  }, [selectedFormat, reportTitle, reportId, onExportComplete])

  const getFormatIcon = useCallback((formatId: string) => {
    const format = exportFormats.find(f => f.id === formatId)
    return format ? format.icon : DocumentTextIcon
  }, [exportFormats])

  const getFormatColor = useCallback((formatId: string) => {
    const format = exportFormats.find(f => f.id === formatId)
    return format ? format.color : 'neutral'
  }, [exportFormats])

  const handlePageSizeChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setExportOptions(prev => ({ ...prev, pageSize: e.target.value }))
  }, [])

  const handleOrientationChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setExportOptions(prev => ({ ...prev, orientation: e.target.value }))
  }, [])

  const handleQualityChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setExportOptions(prev => ({ ...prev, quality: e.target.value }))
  }, [])

  const handleOptionChange = useCallback((key: string, value: boolean) => {
    setExportOptions(prev => ({ ...prev, [key]: value }))
  }, [])

  const renderExportOptions = useCallback(() => {
    if (selectedFormat === 'pdf') {
      return (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Page Size
            </label>
            <select
              value={exportOptions.pageSize}
              onChange={handlePageSizeChange}
              className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-800 dark:text-neutral-100"
              aria-label="Page size"
            >
              <option value="A4">A4</option>
              <option value="A3">A3</option>
              <option value="Letter">Letter</option>
              <option value="Legal">Legal</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Orientation
            </label>
            <select
              value={exportOptions.orientation}
              onChange={handleOrientationChange}
              className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-800 dark:text-neutral-100"
              aria-label="Page orientation"
            >
              <option value="portrait">Portrait</option>
              <option value="landscape">Landscape</option>
            </select>
          </div>
        </div>
      )
    }

    if (selectedFormat === 'image') {
      return (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Quality
            </label>
            <select
              value={exportOptions.quality}
              onChange={handleQualityChange}
              className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-800 dark:text-neutral-100"
              aria-label="Image quality"
            >
              <option value="high">High (300 DPI)</option>
              <option value="medium">Medium (150 DPI)</option>
              <option value="low">Low (72 DPI)</option>
            </select>
          </div>
        </div>
      )
    }

    return null
  }, [selectedFormat, exportOptions.pageSize, exportOptions.orientation, exportOptions.quality, handlePageSizeChange, handleOrientationChange, handleQualityChange])

  const renderExportProgress = useCallback(() => {
    if (exportStatus !== 'exporting') return null

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Text size="sm" color="neutral" className="font-medium">Exporting...</Text>
          <Text size="sm" color="neutral">{exportProgress}%</Text>
        </div>
        <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
          <div 
            className={clsx(
              "h-2 rounded-full",
              reducedMotion ? "" : "transition-all duration-300",
              "bg-primary-600"
            )}
            style={{ width: `${exportProgress}%` }}
          />
        </div>
      </div>
    )
  }, [exportStatus, exportProgress, reducedMotion])

  const renderExportStatus = useCallback(() => {
    if (exportStatus === 'completed') {
      return (
        <div className="flex items-center gap-3 p-4 bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800 rounded-lg">
          <CheckCircleIcon className="w-6 h-6 text-success-600 dark:text-success-400" />
          <div>
            <Heading level={4} size="sm" color="success" className="font-medium">Export completed successfully!</Heading>
            <Text size="sm" color="success">Your report has been downloaded.</Text>
          </div>
        </div>
      )
    }

    if (exportStatus === 'error') {
      return (
        <div className="flex items-center gap-3 p-4 bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg">
          <ExclamationTriangleIcon className="w-6 h-6 text-danger-600 dark:text-danger-400" />
          <div>
            <Heading level={4} size="sm" color="danger" className="font-medium">Export failed</Heading>
            <Text size="sm" color="danger">There was an error exporting your report.</Text>
          </div>
        </div>
      )
    }

    return null
  }, [exportStatus])

  return (
    <div className={clsx(
      "space-y-6",
      reducedMotion ? "" : "transition-all duration-200"
    )}>
      {/* Header */}
      <div className="text-center">
        <ArrowDownTrayIcon className="w-12 h-12 text-primary-600 dark:text-primary-400 mx-auto mb-4" />
        <Heading level={2} size="xl" color="neutral" className="mb-2">Export Report</Heading>
        <Text size="sm" color="neutral">Choose a format and options for your report export</Text>
      </div>

      {error && <ErrorDisplay error={error} />}

      {/* Format Selection */}
      <div>
        <Heading level={3} size="lg" color="neutral" className="mb-4">Select Export Format</Heading>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4" role="radiogroup" aria-label="Export format options">
          {exportFormats.map((format) => (
            <Card
              key={format.id}
              className={clsx(
                "p-4 cursor-pointer",
                reducedMotion ? "" : "transition-all duration-200",
                selectedFormat === format.id
                  ? 'ring-2 ring-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'hover:shadow-md'
              )}
              onClick={() => setSelectedFormat(format.id)}
              role="radio"
              aria-checked={selectedFormat === format.id}
              aria-label={`${format.name} export format`}
            >
              <div className="flex items-start gap-3">
                <div className={clsx(
                  "p-2 rounded-lg",
                  format.color === 'primary' && "bg-primary-100 dark:bg-primary-900/30",
                  format.color === 'success' && "bg-success-100 dark:bg-success-900/30",
                  format.color === 'warning' && "bg-warning-100 dark:bg-warning-900/30",
                  format.color === 'danger' && "bg-danger-100 dark:bg-danger-900/30",
                  format.color === 'neutral' && "bg-neutral-100 dark:bg-neutral-800"
                )}>
                  <format.icon className={clsx(
                    "w-6 h-6",
                    format.color === 'primary' && "text-primary-600 dark:text-primary-400",
                    format.color === 'success' && "text-success-600 dark:text-success-400",
                    format.color === 'warning' && "text-warning-600 dark:text-warning-400",
                    format.color === 'danger' && "text-danger-600 dark:text-danger-400",
                    format.color === 'neutral' && "text-neutral-600 dark:text-neutral-400"
                  )} />
                </div>
                <div className="flex-1">
                  <Heading level={4} size="sm" color="neutral" className="font-medium">{format.name}</Heading>
                  <Text size="sm" color="neutral" className="mb-3">{format.description}</Text>
                  <div className="flex flex-wrap gap-1" role="group" aria-label="Format features">
                    {format.features.map((feature, index) => (
                      <Badge key={index} size="sm">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="flex-shrink-0">
                  <input
                    type="radio"
                    checked={selectedFormat === format.id}
                    onChange={() => setSelectedFormat(format.id)}
                    className="w-4 h-4 text-primary-600 border-neutral-300 focus:ring-primary-500 dark:border-neutral-600"
                    aria-label={`Select ${format.name} format`}
                  />
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Export Options */}
      {renderExportOptions() && (
        <div>
          <Heading level={3} size="lg" color="neutral" className="mb-4">Export Options</Heading>
          <Card className="p-4">
            {renderExportOptions()}
          </Card>
        </div>
      )}

      {/* General Options */}
      <div>
        <Heading level={3} size="lg" color="neutral" className="mb-4">Content Options</Heading>
        <Card className="p-4">
          <div className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={exportOptions.includeCharts}
                onChange={(e) => handleOptionChange('includeCharts', e.target.checked)}
                className="w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500 dark:border-neutral-600"
                aria-label="Include charts and visualizations"
              />
              <Text size="sm" color="neutral" className="ml-2">Include charts and visualizations</Text>
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={exportOptions.includeTables}
                onChange={(e) => handleOptionChange('includeTables', e.target.checked)}
                className="w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500 dark:border-neutral-600"
                aria-label="Include data tables"
              />
              <Text size="sm" color="neutral" className="ml-2">Include data tables</Text>
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={exportOptions.includeMetadata}
                onChange={(e) => handleOptionChange('includeMetadata', e.target.checked)}
                className="w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500 dark:border-neutral-600"
                aria-label="Include report metadata"
              />
              <Text size="sm" color="neutral" className="ml-2">Include report metadata</Text>
            </label>
          </div>
        </Card>
      </div>

      {/* Export Progress */}
      {renderExportProgress()}

      {/* Export Status */}
      {renderExportStatus()}

      {/* Actions */}
      <div className="flex justify-end gap-3" role="group" aria-label="Export actions">
        <Button 
          variant="outline" 
          onClick={onClose}
          aria-label="Cancel export"
        >
          Cancel
        </Button>
        <Button 
          onClick={handleExport}
          disabled={isExporting}
          className="flex items-center gap-2"
          aria-label={isExporting ? 'Exporting report' : 'Export report'}
        >
          {isExporting ? (
            <Spinner size="sm" />
          ) : (
            <ArrowDownTrayIcon className="w-4 h-4" />
          )}
          {isExporting ? 'Exporting...' : 'Export Report'}
        </Button>
      </div>
    </div>
  )
}

export default ReportExport