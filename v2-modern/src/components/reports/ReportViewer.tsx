import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { 
  ArrowDownTrayIcon, 
  ShareIcon, 
  PencilIcon,
  EyeIcon,
  PrinterIcon,
  DocumentTextIcon,
  ChartBarIcon,
  TableCellsIcon
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
import { useReport } from '../../hooks/api/useReports'

interface ReportViewerProps {
  reportId: string
  onClose?: () => void
  onEdit?: () => void
  onExport?: () => void
  onShare?: () => void
  readOnly?: boolean
}

const ReportViewer: React.FC<ReportViewerProps> = ({
  reportId,
  onClose,
  onEdit,
  onExport,
  onShare,
  readOnly = false
}) => {
  const { reducedMotion } = useAccessibility()
  const [activeTab, setActiveTab] = useState<'view' | 'comments' | 'versions'>('view')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const {
    data: report,
    isLoading: reportLoading,
    error: reportError
  } = useReport(reportId)

  useEffect(() => {
    if (reportLoading) {
      setIsLoading(true)
    } else {
      setIsLoading(false)
    }
    
    if (reportError) {
      setError(reportError instanceof Error ? reportError.message : 'Failed to load report')
    }
  }, [reportLoading, reportError])

  const formatDate = useCallback((dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }, [])

  const getStatusColor = useCallback((status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'generating': return 'warning'
      case 'failed': return 'danger'
      case 'draft': return 'neutral'
      default: return 'neutral'
    }
  }, [])

  const getTypeIcon = useCallback((type: string) => {
    switch (type) {
      case 'portfolio_performance': return <ChartBarIcon className="w-5 h-5" />
      case 'risk_analysis': return <DocumentTextIcon className="w-5 h-5" />
      case 'dcf_analysis': return <DocumentTextIcon className="w-5 h-5" />
      case 'comparable_analysis': return <DocumentTextIcon className="w-5 h-5" />
      case 'market_research': return <DocumentTextIcon className="w-5 h-5" />
      default: return <DocumentTextIcon className="w-5 h-5" />
    }
  }, [])

  const renderSection = useCallback((section: any) => {
    switch (section.type) {
      case 'text':
        return (
          <div className="prose max-w-none">
            <div dangerouslySetInnerHTML={{ __html: section.content }} />
          </div>
        )
      
      case 'chart':
        return (
          <div className="bg-neutral-50 dark:bg-neutral-800 rounded-lg p-6">
            <Heading level={3} size="lg" color="neutral" className="mb-4">{section.title}</Heading>
            <div className="h-64 bg-white dark:bg-neutral-700 rounded border border-neutral-200 dark:border-neutral-600 flex items-center justify-center">
              <div className="text-center">
                <ChartBarIcon className="w-12 h-12 text-neutral-400 dark:text-neutral-500 mx-auto mb-2" />
                <Text size="sm" color="neutral">Chart visualization would be rendered here</Text>
              </div>
            </div>
          </div>
        )
      
      case 'table':
        return (
          <div className="bg-neutral-50 dark:bg-neutral-800 rounded-lg p-6">
            <Heading level={3} size="lg" color="neutral" className="mb-4">{section.title}</Heading>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white dark:bg-neutral-700 rounded-lg shadow">
                <thead className="bg-neutral-50 dark:bg-neutral-800">
                  <tr>
                    {section.columns?.map((column: any, index: number) => (
                      <th key={index} className="px-6 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                        {column.title}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-neutral-700 divide-y divide-neutral-200 dark:divide-neutral-600">
                  {section.data?.map((row: any, index: number) => (
                    <tr key={index}>
                      {section.columns?.map((column: any, colIndex: number) => (
                        <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-neutral-900 dark:text-neutral-100">
                          {row[column.key]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )
      
      case 'metric':
        return (
          <div className="bg-neutral-50 dark:bg-neutral-800 rounded-lg p-6">
            <Heading level={3} size="lg" color="neutral" className="mb-4">{section.title}</Heading>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {section.metrics?.map((metric: any, index: number) => (
                <div key={index} className="bg-white dark:bg-neutral-700 rounded-lg p-4 shadow-sm">
                  <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">{metric.value}</div>
                  <Text size="sm" color="neutral" className="mt-1">{metric.name}</Text>
                  {metric.change !== undefined && (
                    <Text size="xs" color={metric.change > 0 ? 'success' : metric.change < 0 ? 'danger' : 'neutral'} className="mt-1">
                      {metric.change > 0 ? '+' : ''}{metric.change}%
                    </Text>
                  )}
                </div>
              ))}
            </div>
          </div>
        )
      
      default:
        return (
          <div className="bg-neutral-50 dark:bg-neutral-800 rounded-lg p-6">
            <Heading level={3} size="lg" color="neutral" className="mb-4">{section.title}</Heading>
            <Text size="sm" color="neutral">Unknown section type: {section.type}</Text>
          </div>
        )
    }
  }, [])

  const renderReportContent = useCallback(() => {
    if (!report?.content) {
      return (
        <div className="text-center py-12">
          <DocumentTextIcon className="w-12 h-12 text-neutral-400 dark:text-neutral-500 mx-auto mb-4" />
          <Heading level={3} size="lg" color="neutral" className="mb-2">No content available</Heading>
          <Text size="sm" color="neutral">This report doesn't have any content yet.</Text>
        </div>
      )
    }

    return (
      <div className="space-y-8">
        {report.content.sections?.map((section: any, index: number) => (
          <div key={section.id || index}>
            {renderSection(section)}
          </div>
        ))}
      </div>
    )
  }, [report?.content, renderSection])

  const renderComments = useCallback(() => (
    <div className="space-y-4">
      <div className="text-center py-12">
        <DocumentTextIcon className="w-12 h-12 text-neutral-400 dark:text-neutral-500 mx-auto mb-4" />
        <Heading level={3} size="lg" color="neutral" className="mb-2">No comments yet</Heading>
        <Text size="sm" color="neutral">Comments feature coming soon.</Text>
      </div>
    </div>
  ), [])

  const renderVersions = useCallback(() => (
    <div className="space-y-4">
      <div className="text-center py-12">
        <DocumentTextIcon className="w-12 h-12 text-neutral-400 dark:text-neutral-500 mx-auto mb-4" />
        <Heading level={3} size="lg" color="neutral" className="mb-2">No versions available</Heading>
        <Text size="sm" color="neutral">Version history feature coming soon.</Text>
      </div>
    </div>
  ), [])

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error) {
    return <ErrorDisplay error={error} />
  }

  if (!report) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="w-12 h-12 text-neutral-400 dark:text-neutral-500 mx-auto mb-4" />
        <Heading level={3} size="lg" color="neutral" className="mb-2">Report not found</Heading>
        <Text size="sm" color="neutral">The requested report could not be found.</Text>
      </div>
    )
  }

  const tabs = useMemo(() => [
    { id: 'view', label: 'Report', icon: EyeIcon },
    { id: 'comments', label: 'Comments', icon: DocumentTextIcon },
    { id: 'versions', label: 'Versions', icon: DocumentTextIcon }
  ], [])

  return (
    <div className={clsx(
      "space-y-6",
      reducedMotion ? "" : "transition-all duration-200"
    )}>
      {/* Header */}
      <div className="border-b border-neutral-200 dark:border-neutral-700 pb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              {getTypeIcon(report.type)}
              <Heading level={1} size="2xl" color="neutral">{report.title}</Heading>
              <Badge color={getStatusColor(report.status)}>
                {report.status}
              </Badge>
            </div>
            
            <Text size="sm" color="neutral" className="mb-4">{report.description}</Text>
            
            <div className="flex items-center gap-6 text-sm text-neutral-500 dark:text-neutral-400">
              <span>Created: {formatDate(report.created_at)}</span>
              <span>Updated: {formatDate(report.updated_at)}</span>
              <span>Views: {report.view_count || 0}</span>
              <span>Exports: {report.export_count || 0}</span>
              <span>Shares: {report.share_count || 0}</span>
            </div>
            
            {report.tags && report.tags.length > 0 && (
              <div className="flex items-center gap-2 mt-3" role="group" aria-label="Report tags">
                {report.tags.map((tag: string, index: number) => (
                  <Badge key={index} size="sm">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
          </div>
          
          {!readOnly && (
            <div className="flex items-center gap-2 ml-4" role="group" aria-label="Report actions">
              <Button
                variant="outline"
                size="sm"
                onClick={onEdit}
                className="flex items-center gap-2"
                aria-label="Edit report"
              >
                <PencilIcon className="w-4 h-4" />
                Edit
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={onExport}
                className="flex items-center gap-2"
                aria-label="Export report"
              >
                <ArrowDownTrayIcon className="w-4 h-4" />
                Export
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={onShare}
                className="flex items-center gap-2"
                aria-label="Share report"
              >
                <ShareIcon className="w-4 h-4" />
                Share
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.print()}
                className="flex items-center gap-2"
                aria-label="Print report"
              >
                <PrinterIcon className="w-4 h-4" />
                Print
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-neutral-200 dark:border-neutral-700">
        <nav className="-mb-px flex space-x-8" role="tablist" aria-label="Report sections">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={clsx(
                "flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm",
                reducedMotion ? "" : "transition-colors duration-200",
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-300 hover:border-neutral-300 dark:hover:border-neutral-600'
              )}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`tabpanel-${tab.id}`}
              aria-label={`${tab.label} tab`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="min-h-96" role="tabpanel" id={`tabpanel-${activeTab}`} aria-labelledby={`tab-${activeTab}`}>
        {activeTab === 'view' && renderReportContent()}
        {activeTab === 'comments' && renderComments()}
        {activeTab === 'versions' && renderVersions()}
      </div>
    </div>
  )
}

export default ReportViewer