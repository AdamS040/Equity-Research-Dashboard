import React, { useState, useCallback, useMemo } from 'react'
import { 
  DocumentTextIcon, 
  PlusIcon, 
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  TrashIcon,
  ClockIcon,
  ChartBarIcon,
  DocumentDuplicateIcon
} from '@heroicons/react/24/outline'
import { useReports, Report } from '../hooks/api/useReports'
import { 
  Button, 
  Input, 
  Modal, 
  Card, 
  Badge, 
  Spinner, 
  ErrorDisplay, 
  Heading, 
  Text,
  useAccessibility
} from '../components/ui'
import { clsx } from 'clsx'
import ReportBuilder from '../components/reports/ReportBuilder'
import ReportViewer from '../components/reports/ReportViewer'
import ReportExport from '../components/reports/ReportExport'
import ReportTemplates from '../components/reports/ReportTemplates'

// Report interface is now imported from useReports hook

interface ReportFilters {
  type: string
  status: string
  search: string
  tags: string[]
}

const Reports: React.FC = () => {
  const { reducedMotion } = useAccessibility()
  const [activeTab, setActiveTab] = useState<'list' | 'builder' | 'templates' | 'scheduled'>('list')
  const [selectedReport, setSelectedReport] = useState<Report | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showViewModal, setShowViewModal] = useState(false)
  const [showExportModal, setShowExportModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [filters, setFilters] = useState<ReportFilters>({
    type: '',
    status: '',
    search: '',
    tags: []
  })
  const [page, setPage] = useState(1)

  const {
    data: reportsData,
    isLoading,
    error
  } = useReports({
    page,
    limit: 20,
    ...filters
  })

  const handleCreateReport = useCallback(() => {
    setShowCreateModal(true)
  }, [])

  const handleViewReport = useCallback((report: Report) => {
    setSelectedReport(report)
    setShowViewModal(true)
  }, [])

  const handleExportReport = useCallback((report: Report) => {
    setSelectedReport(report)
    setShowExportModal(true)
  }, [])

  const handleDeleteReport = useCallback((report: Report) => {
    setSelectedReport(report)
    setShowDeleteModal(true)
  }, [])

  const handleFilterChange = useCallback((key: keyof ReportFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setPage(1)
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

  const formatDate = useCallback((dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }, [])

  const renderReportList = useCallback(() => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Heading level={1} size="2xl" color="neutral">Reports</Heading>
          <Text size="sm" color="neutral" className="mt-1">Manage and generate financial reports</Text>
        </div>
        <Button
          onClick={handleCreateReport}
          className="flex items-center gap-2"
          aria-label="Create new report"
        >
          <PlusIcon className="w-5 h-5" />
          Create Report
        </Button>
      </div>

      {/* Filters */}
      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Search
            </label>
            <div className="relative">
              <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 dark:text-neutral-500" />
              <Input
                placeholder="Search reports..."
                value={filters.search}
                onChange={(value: string) => handleFilterChange('search', value)}
                className="pl-10"
                aria-label="Search reports"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Type
            </label>
            <select
              value={filters.type}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleFilterChange('type', e.target.value)}
              className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-800 dark:text-neutral-100"
              aria-label="Filter by report type"
            >
              <option value="">All Types</option>
              <option value="portfolio_performance">Portfolio Performance</option>
              <option value="risk_analysis">Risk Analysis</option>
              <option value="dcf_analysis">DCF Analysis</option>
              <option value="comparable_analysis">Comparable Analysis</option>
              <option value="market_research">Market Research</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleFilterChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-800 dark:text-neutral-100"
              aria-label="Filter by report status"
            >
              <option value="">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="generating">Generating</option>
              <option value="failed">Failed</option>
              <option value="draft">Draft</option>
            </select>
          </div>

          <div className="flex items-end">
            <Button
              variant="outline"
              onClick={() => setFilters({ type: '', status: '', search: '', tags: [] })}
              className="w-full"
              aria-label="Clear all filters"
            >
              Clear Filters
            </Button>
          </div>
        </div>
      </Card>

      {/* Reports List */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : error ? (
        <ErrorDisplay error={error} />
              ) : (
                <div className="space-y-4" role="list" aria-label="Reports list">
                  {reportsData?.reports?.map((report: Report) => (
                    <Card key={report.id} className={clsx(
                      "p-6 hover:shadow-lg",
                      reducedMotion ? "" : "transition-shadow duration-200"
                    )} role="listitem">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            {getTypeIcon(report.type)}
                            <Heading level={3} size="lg" color="neutral">
                              {report.title}
                            </Heading>
                            <Badge color={getStatusColor(report.status)}>
                              {report.status}
                            </Badge>
                          </div>

                          <Text size="sm" color="neutral" className="mb-3">{report.description}</Text>

                          <div className="flex items-center gap-6 text-sm text-neutral-500 dark:text-neutral-400">
                            <span>Created: {formatDate(report.created_at)}</span>
                            <span>Views: {report.view_count}</span>
                            <span>Exports: {report.export_count}</span>
                            <span>Shares: {report.share_count}</span>
                          </div>

                          {report.tags && report.tags.length > 0 && (
                            <div className="flex items-center gap-2 mt-3" role="group" aria-label="Report tags">
                              {report.tags.map((tag, index) => (
                                <Badge key={index} size="sm">
                                  {tag}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>

                        <div className="flex items-center gap-2 ml-4" role="group" aria-label={`Actions for ${report.title}`}>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewReport(report)}
                            aria-label={`View ${report.title} report`}
                          >
                            <EyeIcon className="w-4 h-4" />
                          </Button>

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleExportReport(report)}
                            aria-label={`Export ${report.title} report`}
                          >
                            <ArrowDownTrayIcon className="w-4 h-4" />
                          </Button>

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteReport(report)}
                            aria-label={`Delete ${report.title} report`}
                            className="text-danger-600 hover:text-danger-700 dark:text-danger-400 dark:hover:text-danger-300"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
          
                  {reportsData?.reports?.length === 0 && (
                    <Card className="p-12 text-center">
                      <DocumentTextIcon className="w-12 h-12 text-neutral-400 dark:text-neutral-500 mx-auto mb-4" />
                      <Heading level={3} size="lg" color="neutral" className="mb-2">No reports found</Heading>
                      <Text size="sm" color="neutral" className="mb-6">
                        Get started by creating your first report
                      </Text>
                      <Button onClick={handleCreateReport} aria-label="Create your first report">
                        <PlusIcon className="w-5 h-5 mr-2" />
                        Create Report
                      </Button>
                    </Card>
                  )}
        </div>
      )}

      {/* Pagination */}
      {reportsData && reportsData.total > 20 && (
        <div className="flex items-center justify-between">
          <Text size="sm" color="neutral">
            Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, reportsData.total)} of {reportsData.total} reports
          </Text>
          <div className="flex items-center gap-2" role="group" aria-label="Pagination controls">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page - 1)}
              disabled={!reportsData.has_prev}
              aria-label="Go to previous page"
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={!reportsData.has_next}
              aria-label="Go to next page"
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  ), [reportsData, isLoading, error, filters, page, handleCreateReport, handleViewReport, handleExportReport, handleDeleteReport, getTypeIcon, getStatusColor, formatDate, reducedMotion])

  const renderTabContent = useCallback(() => {
    switch (activeTab) {
      case 'list':
        return renderReportList()
      case 'builder':
        return <ReportBuilder onClose={() => setActiveTab('list')} />
      case 'templates':
        return <ReportTemplates onClose={() => setActiveTab('list')} />
      case 'scheduled':
        return (
          <div className="text-center py-12">
            <ClockIcon className="w-12 h-12 text-neutral-400 dark:text-neutral-500 mx-auto mb-4" />
            <Heading level={3} size="lg" color="neutral" className="mb-2">Scheduled Reports</Heading>
            <Text size="sm" color="neutral">Coming Soon</Text>
          </div>
        )
      default:
        return renderReportList()
    }
  }, [activeTab, renderReportList])

  const tabs = useMemo(() => [
    { id: 'list', label: 'All Reports', icon: DocumentTextIcon },
    { id: 'builder', label: 'Report Builder', icon: PlusIcon },
    { id: 'templates', label: 'Templates', icon: DocumentDuplicateIcon },
    { id: 'scheduled', label: 'Scheduled', icon: ClockIcon }
  ], [])

  return (
    <div className="space-y-6">
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
      <div role="tabpanel" id={`tabpanel-${activeTab}`} aria-labelledby={`tab-${activeTab}`}>
        {renderTabContent()}
      </div>

      {/* Modals */}
      {showCreateModal && (
        <Modal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          title="Create New Report"
          size="lg"
        >
          <ReportBuilder onClose={() => setShowCreateModal(false)} />
        </Modal>
      )}

      {showViewModal && selectedReport && (
        <Modal
          isOpen={showViewModal}
          onClose={() => setShowViewModal(false)}
          title={selectedReport.title}
          size="xl"
        >
          <ReportViewer
            reportId={selectedReport.id}
            onClose={() => setShowViewModal(false)}
          />
        </Modal>
      )}

      {showExportModal && selectedReport && (
        <Modal
          isOpen={showExportModal}
          onClose={() => setShowExportModal(false)}
          title={`Export ${selectedReport.title}`}
          size="md"
        >
          <ReportExport
            reportId={selectedReport.id}
            reportTitle={selectedReport.title}
            onClose={() => setShowExportModal(false)}
          />
        </Modal>
      )}

      {showDeleteModal && selectedReport && (
        <Modal
          isOpen={showDeleteModal}
          onClose={() => setShowDeleteModal(false)}
          title="Delete Report"
          size="sm"
        >
          <div className="space-y-4">
            <Text size="sm" color="neutral">
              Are you sure you want to delete "{selectedReport.title}"? This action cannot be undone.
            </Text>
            <div className="flex justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => setShowDeleteModal(false)}
                aria-label="Cancel delete operation"
              >
                Cancel
              </Button>
              <Button
                onClick={() => {
                  // Handle delete
                  setShowDeleteModal(false)
                }}
                aria-label={`Confirm delete ${selectedReport.title}`}
                className="bg-danger-600 hover:bg-danger-700 text-white"
              >
                Delete
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}

export default Reports
