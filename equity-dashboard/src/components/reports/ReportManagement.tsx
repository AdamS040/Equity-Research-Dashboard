/**
 * Report Management Component
 * 
 * Saved reports list with search, filter, versioning, and analytics
 */

import React, { useState, useCallback, useMemo } from 'react'
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Button, 
  Input, 
  Badge, 
  Modal, 
  Spinner,
  Grid,
  GridItem,
  Flex,
  Heading,
  Text,
  Container
} from '../ui'
import { 
  SavedReport,
  ReportSearchFilters,
  ReportSearchResult,
  ReportVersion,
  ReportComment,
  ReportSchedule,
  ReportAnalytics,
  ReportUsageAnalytics
} from '../../types/reports'
import { searchUtils, versionUtils, formatDate } from '../../utils/reports'
import { 
  useReports, 
  useDeleteReport, 
  useDuplicateReport,
  useAddToFavorites,
  useRemoveFromFavorites,
  useReportHistory,
  useReportComments,
  useReportSchedules,
  useReportAnalytics
} from '../../hooks/api/useReports'

interface ReportManagementProps {
  onSelectReport?: (report: SavedReport) => void
  onEditReport?: (report: SavedReport) => void
  onCreateReport?: () => void
  showCreateButton?: boolean
  showEditButton?: boolean
  showDeleteButton?: boolean
  showDuplicateButton?: boolean
  showFavoritesButton?: boolean
  showAnalytics?: boolean
}

export const ReportManagement: React.FC<ReportManagementProps> = ({
  onSelectReport,
  onEditReport,
  onCreateReport,
  showCreateButton = true,
  showEditButton = true,
  showDeleteButton = true,
  showDuplicateButton = true,
  showFavoritesButton = true,
  showAnalytics = true,
}) => {
  const [searchFilters, setSearchFilters] = useState<ReportSearchFilters>({
    query: '',
    type: '',
    status: '',
    author: '',
    tags: [],
    sortBy: 'updatedAt',
    sortOrder: 'desc',
    page: 1,
    limit: 20,
  })
  const [selectedReport, setSelectedReport] = useState<SavedReport | null>(null)
  const [showReportModal, setShowReportModal] = useState(false)
  const [showVersionModal, setShowVersionModal] = useState(false)
  const [showCommentModal, setShowCommentModal] = useState(false)
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [showAnalyticsModal, setShowAnalyticsModal] = useState(false)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [activeTab, setActiveTab] = useState<'reports' | 'favorites' | 'schedules' | 'analytics'>('reports')

  // API hooks
  const { data: reportsData, isLoading: reportsLoading } = useReports(searchFilters)
  const { data: favoritesData, isLoading: favoritesLoading } = useReports({ ...searchFilters, favorites: true })
  const { data: schedulesData, isLoading: schedulesLoading } = useReports({ ...searchFilters, schedules: true })
  const { data: analyticsData, isLoading: analyticsLoading } = useReports({ ...searchFilters, analytics: true })
  
  const deleteReportMutation = useDeleteReport()
  const duplicateReportMutation = useDuplicateReport()
  const addToFavoritesMutation = useAddToFavorites()
  const removeFromFavoritesMutation = useRemoveFromFavorites()

  // Get current data based on active tab
  const currentData = useMemo(() => {
    switch (activeTab) {
      case 'favorites':
        return favoritesData
      case 'schedules':
        return schedulesData
      case 'analytics':
        return analyticsData
      default:
        return reportsData
    }
  }, [activeTab, reportsData, favoritesData, schedulesData, analyticsData])

  const isLoading = useMemo(() => {
    switch (activeTab) {
      case 'favorites':
        return favoritesLoading
      case 'schedules':
        return schedulesLoading
      case 'analytics':
        return analyticsLoading
      default:
        return reportsLoading
    }
  }, [activeTab, reportsLoading, favoritesLoading, schedulesLoading, analyticsLoading])

  // Handle search and filters
  const handleSearchChange = useCallback((query: string) => {
    setSearchFilters(prev => ({ ...prev, query, page: 1 }))
  }, [])

  const handleFilterChange = useCallback((key: string, value: any) => {
    setSearchFilters(prev => ({ ...prev, [key]: value, page: 1 }))
  }, [])

  const handleSortChange = useCallback((sortBy: string, sortOrder: 'asc' | 'desc') => {
    setSearchFilters(prev => ({ ...prev, sortBy, sortOrder }))
  }, [])

  const handlePageChange = useCallback((page: number) => {
    setSearchFilters(prev => ({ ...prev, page }))
  }, [])

  // Report actions
  const handleSelectReport = useCallback((report: SavedReport) => {
    if (onSelectReport) {
      onSelectReport(report)
    } else {
      setSelectedReport(report)
      setShowReportModal(true)
    }
  }, [onSelectReport])

  const handleEditReport = useCallback((report: SavedReport) => {
    if (onEditReport) {
      onEditReport(report)
    }
  }, [onEditReport])

  const handleDeleteReport = useCallback(async (reportId: string) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      try {
        await deleteReportMutation.mutateAsync(reportId)
      } catch (error) {
        console.error('Failed to delete report:', error)
      }
    }
  }, [deleteReportMutation])

  const handleDuplicateReport = useCallback(async (report: SavedReport) => {
    try {
      await duplicateReportMutation.mutateAsync({
        reportId: report.id,
        title: `${report.title} (Copy)`,
      })
    } catch (error) {
      console.error('Failed to duplicate report:', error)
    }
  }, [duplicateReportMutation])

  const handleToggleFavorite = useCallback(async (report: SavedReport) => {
    try {
      if (report.isFavorite) {
        await removeFromFavoritesMutation.mutateAsync(report.id)
      } else {
        await addToFavoritesMutation.mutateAsync(report.id)
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error)
    }
  }, [addToFavoritesMutation, removeFromFavoritesMutation])

  const handleCreateReport = useCallback(() => {
    if (onCreateReport) {
      onCreateReport()
    }
  }, [onCreateReport])

  // Modal handlers
  const handleShowVersions = useCallback((report: SavedReport) => {
    setSelectedReport(report)
    setShowVersionModal(true)
  }, [])

  const handleShowComments = useCallback((report: SavedReport) => {
    setSelectedReport(report)
    setShowCommentModal(true)
  }, [])

  const handleShowSchedules = useCallback((report: SavedReport) => {
    setSelectedReport(report)
    setShowScheduleModal(true)
  }, [])

  const handleShowAnalytics = useCallback((report: SavedReport) => {
    setSelectedReport(report)
    setShowAnalyticsModal(true)
  }, [])

  if (isLoading) {
    return (
      <Container>
        <Flex justify="center" align="center" style={{ height: '200px' }}>
          <Spinner size="lg" />
        </Flex>
      </Container>
    )
  }

  return (
    <Container>
      {/* Header */}
      <Card mb="lg">
        <CardBody>
          <Flex justify="between" align="center">
            <div>
              <Heading level={2}>Report Management</Heading>
              <Text color="gray" size="sm">
                Manage your saved reports, versions, and analytics
              </Text>
            </div>
            {showCreateButton && (
              <Button variant="primary" onClick={handleCreateReport}>
                Create New Report
              </Button>
            )}
          </Flex>
        </CardBody>
      </Card>

      {/* Tabs */}
      <Card mb="lg">
        <CardBody>
          <Flex gap="md">
            <Button
              variant={activeTab === 'reports' ? 'primary' : 'outline'}
              onClick={() => setActiveTab('reports')}
            >
              All Reports ({currentData?.total || 0})
            </Button>
            {showFavoritesButton && (
              <Button
                variant={activeTab === 'favorites' ? 'primary' : 'outline'}
                onClick={() => setActiveTab('favorites')}
              >
                Favorites ({favoritesData?.total || 0})
              </Button>
            )}
            <Button
              variant={activeTab === 'schedules' ? 'primary' : 'outline'}
              onClick={() => setActiveTab('schedules')}
            >
              Scheduled ({schedulesData?.total || 0})
            </Button>
            {showAnalytics && (
              <Button
                variant={activeTab === 'analytics' ? 'primary' : 'outline'}
                onClick={() => setActiveTab('analytics')}
              >
                Analytics
              </Button>
            )}
          </Flex>
        </CardBody>
      </Card>

      {/* Search and Filters */}
      {activeTab !== 'analytics' && (
        <Card mb="lg">
          <CardBody>
            <Grid columns={4} gap="md">
              <GridItem>
                <Input
                  placeholder="Search reports..."
                  value={searchFilters.query}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  leftIcon="search"
                />
              </GridItem>
              <GridItem>
                <select
                  value={searchFilters.type}
                  onChange={(e) => handleFilterChange('type', e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px' }}
                >
                  <option value="">All Types</option>
                  <option value="full">Full Analysis</option>
                  <option value="valuation">Valuation</option>
                  <option value="risk">Risk Analysis</option>
                  <option value="technical">Technical Analysis</option>
                  <option value="custom">Custom</option>
                </select>
              </GridItem>
              <GridItem>
                <select
                  value={searchFilters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px' }}
                >
                  <option value="">All Statuses</option>
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                  <option value="archived">Archived</option>
                </select>
              </GridItem>
              <GridItem>
                <Flex gap="sm">
                  <Button
                    variant={viewMode === 'grid' ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('grid')}
                  >
                    Grid
                  </Button>
                  <Button
                    variant={viewMode === 'list' ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('list')}
                  >
                    List
                  </Button>
                </Flex>
              </GridItem>
            </Grid>
          </CardBody>
        </Card>
      )}

      {/* Content based on active tab */}
      {activeTab === 'analytics' ? (
        <AnalyticsView data={analyticsData} />
      ) : (
        <>
          {/* Reports List/Grid */}
          {viewMode === 'grid' ? (
            <Grid columns={3} gap="lg">
              {currentData?.reports?.map((report) => (
                <GridItem key={report.id}>
                  <ReportCard
                    report={report}
                    onSelect={() => handleSelectReport(report)}
                    onEdit={showEditButton ? () => handleEditReport(report) : undefined}
                    onDelete={showDeleteButton ? () => handleDeleteReport(report.id) : undefined}
                    onDuplicate={showDuplicateButton ? () => handleDuplicateReport(report) : undefined}
                    onToggleFavorite={showFavoritesButton ? () => handleToggleFavorite(report) : undefined}
                    onShowVersions={() => handleShowVersions(report)}
                    onShowComments={() => handleShowComments(report)}
                    onShowSchedules={() => handleShowSchedules(report)}
                    onShowAnalytics={showAnalytics ? () => handleShowAnalytics(report) : undefined}
                  />
                </GridItem>
              ))}
            </Grid>
          ) : (
            <div>
              {currentData?.reports?.map((report) => (
                <ReportListItem
                  key={report.id}
                  report={report}
                  onSelect={() => handleSelectReport(report)}
                  onEdit={showEditButton ? () => handleEditReport(report) : undefined}
                  onDelete={showDeleteButton ? () => handleDeleteReport(report.id) : undefined}
                  onDuplicate={showDuplicateButton ? () => handleDuplicateReport(report) : undefined}
                  onToggleFavorite={showFavoritesButton ? () => handleToggleFavorite(report) : undefined}
                  onShowVersions={() => handleShowVersions(report)}
                  onShowComments={() => handleShowComments(report)}
                  onShowSchedules={() => handleShowSchedules(report)}
                  onShowAnalytics={showAnalytics ? () => handleShowAnalytics(report) : undefined}
                />
              ))}
            </div>
          )}

          {/* Pagination */}
          {currentData && currentData.total > currentData.limit && (
            <Card mt="lg">
              <CardBody>
                <Flex justify="center" align="center" gap="md">
                  <Button
                    variant="outline"
                    disabled={!currentData.hasPrev}
                    onClick={() => handlePageChange(currentData.page - 1)}
                  >
                    Previous
                  </Button>
                  <Text>
                    Page {currentData.page} of {Math.ceil(currentData.total / currentData.limit)}
                  </Text>
                  <Button
                    variant="outline"
                    disabled={!currentData.hasNext}
                    onClick={() => handlePageChange(currentData.page + 1)}
                  >
                    Next
                  </Button>
                </Flex>
              </CardBody>
            </Card>
          )}
        </>
      )}

      {/* Modals */}
      {showReportModal && selectedReport && (
        <ReportDetailsModal
          report={selectedReport}
          onClose={() => setShowReportModal(false)}
          onEdit={() => handleEditReport(selectedReport)}
          onDelete={() => handleDeleteReport(selectedReport.id)}
          onDuplicate={() => handleDuplicateReport(selectedReport)}
          onToggleFavorite={() => handleToggleFavorite(selectedReport)}
        />
      )}

      {showVersionModal && selectedReport && (
        <VersionHistoryModal
          report={selectedReport}
          onClose={() => setShowVersionModal(false)}
        />
      )}

      {showCommentModal && selectedReport && (
        <CommentsModal
          report={selectedReport}
          onClose={() => setShowCommentModal(false)}
        />
      )}

      {showScheduleModal && selectedReport && (
        <SchedulesModal
          report={selectedReport}
          onClose={() => setShowScheduleModal(false)}
        />
      )}

      {showAnalyticsModal && selectedReport && (
        <ReportAnalyticsModal
          report={selectedReport}
          onClose={() => setShowAnalyticsModal(false)}
        />
      )}
    </Container>
  )
}

// Report Card Component
interface ReportCardProps {
  report: SavedReport
  onSelect: () => void
  onEdit?: () => void
  onDelete?: () => void
  onDuplicate?: () => void
  onToggleFavorite?: () => void
  onShowVersions: () => void
  onShowComments: () => void
  onShowSchedules: () => void
  onShowAnalytics?: () => void
}

const ReportCard: React.FC<ReportCardProps> = ({
  report,
  onSelect,
  onEdit,
  onDelete,
  onDuplicate,
  onToggleFavorite,
  onShowVersions,
  onShowComments,
  onShowSchedules,
  onShowAnalytics,
}) => {
  return (
    <Card hoverable onClick={onSelect} style={{ cursor: 'pointer', height: '100%' }}>
      <CardHeader>
        <Flex justify="between" align="start">
          <div style={{ flex: 1 }}>
            <Heading level={4} mb="xs">{report.title}</Heading>
            <Text color="gray" size="sm">{report.type} • {report.status}</Text>
          </div>
          <Flex gap="xs">
            {onToggleFavorite && (
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  onToggleFavorite()
                }}
              >
                {report.isFavorite ? '❤️' : '🤍'}
              </Button>
            )}
            {onEdit && (
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  onEdit()
                }}
              >
                Edit
              </Button>
            )}
          </Flex>
        </Flex>
      </CardHeader>
      <CardBody>
        <Flex direction="column" gap="sm">
          <Flex gap="sm" wrap>
            <Badge variant="secondary">{report.type}</Badge>
            <Badge variant={report.status === 'published' ? 'success' : 'secondary'}>
              {report.status}
            </Badge>
            {report.isShared && <Badge variant="info">Shared</Badge>}
          </Flex>
          
          <Flex justify="between" align="center">
            <Text size="sm" color="gray">
              {report.metadata.author}
            </Text>
            <Text size="sm" color="gray">
              v{report.version}
            </Text>
          </Flex>

          <Flex justify="between" align="center">
            <Text size="sm" color="gray">
              {report.viewCount} views
            </Text>
            <Text size="sm" color="gray">
              {formatDate(report.updatedAt, 'relative')}
            </Text>
          </Flex>

          {report.tags.length > 0 && (
            <Flex gap="xs" wrap>
              {report.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" size="sm">
                  {tag}
                </Badge>
              ))}
              {report.tags.length > 3 && (
                <Badge variant="outline" size="sm">
                  +{report.tags.length - 3}
                </Badge>
              )}
            </Flex>
          )}

          <Flex gap="sm" justify="center">
            <Button variant="ghost" size="sm" onClick={(e) => {
              e.stopPropagation()
              onShowVersions()
            }}>
              Versions
            </Button>
            <Button variant="ghost" size="sm" onClick={(e) => {
              e.stopPropagation()
              onShowComments()
            }}>
              Comments
            </Button>
            <Button variant="ghost" size="sm" onClick={(e) => {
              e.stopPropagation()
              onShowSchedules()
            }}>
              Schedules
            </Button>
            {onShowAnalytics && (
              <Button variant="ghost" size="sm" onClick={(e) => {
                e.stopPropagation()
                onShowAnalytics()
              }}>
                Analytics
              </Button>
            )}
          </Flex>
        </Flex>
      </CardBody>
    </Card>
  )
}

// Report List Item Component
interface ReportListItemProps {
  report: SavedReport
  onSelect: () => void
  onEdit?: () => void
  onDelete?: () => void
  onDuplicate?: () => void
  onToggleFavorite?: () => void
  onShowVersions: () => void
  onShowComments: () => void
  onShowSchedules: () => void
  onShowAnalytics?: () => void
}

const ReportListItem: React.FC<ReportListItemProps> = ({
  report,
  onSelect,
  onEdit,
  onDelete,
  onDuplicate,
  onToggleFavorite,
  onShowVersions,
  onShowComments,
  onShowSchedules,
  onShowAnalytics,
}) => {
  return (
    <Card hoverable onClick={onSelect} style={{ cursor: 'pointer', marginBottom: '16px' }}>
      <CardBody>
        <Flex justify="between" align="center">
          <Flex direction="column" gap="xs" style={{ flex: 1 }}>
            <Flex align="center" gap="md">
              <Heading level={4}>{report.title}</Heading>
              <Flex gap="sm">
                <Badge variant="secondary">{report.type}</Badge>
                <Badge variant={report.status === 'published' ? 'success' : 'secondary'}>
                  {report.status}
                </Badge>
                {report.isShared && <Badge variant="info">Shared</Badge>}
                {report.isFavorite && <Badge variant="warning">Favorite</Badge>}
              </Flex>
            </Flex>
            <Flex gap="md" align="center">
              <Text size="sm" color="gray">
                Author: {report.metadata.author}
              </Text>
              <Text size="sm" color="gray">
                Version: {report.version}
              </Text>
              <Text size="sm" color="gray">
                Views: {report.viewCount}
              </Text>
              <Text size="sm" color="gray">
                Updated: {formatDate(report.updatedAt, 'relative')}
              </Text>
            </Flex>
            {report.tags.length > 0 && (
              <Flex gap="xs" wrap>
                {report.tags.map((tag) => (
                  <Badge key={tag} variant="outline" size="sm">
                    {tag}
                  </Badge>
                ))}
              </Flex>
            )}
          </Flex>
          <Flex gap="sm">
            {onToggleFavorite && (
              <Button variant="ghost" size="sm" onClick={(e) => {
                e.stopPropagation()
                onToggleFavorite()
              }}>
                {report.isFavorite ? '❤️' : '🤍'}
              </Button>
            )}
            {onEdit && (
              <Button variant="ghost" size="sm" onClick={(e) => {
                e.stopPropagation()
                onEdit()
              }}>
                Edit
              </Button>
            )}
            {onDuplicate && (
              <Button variant="ghost" size="sm" onClick={(e) => {
                e.stopPropagation()
                onDuplicate()
              }}>
                Duplicate
              </Button>
            )}
            {onDelete && (
              <Button variant="ghost" size="sm" onClick={(e) => {
                e.stopPropagation()
                onDelete()
              }}>
                Delete
              </Button>
            )}
          </Flex>
        </Flex>
      </CardBody>
    </Card>
  )
}

// Analytics View Component
interface AnalyticsViewProps {
  data: any
}

const AnalyticsView: React.FC<AnalyticsViewProps> = ({ data }) => {
  return (
    <Grid columns={2} gap="lg">
      <GridItem>
        <Card>
          <CardHeader>
            <Heading level={4}>Report Statistics</Heading>
          </CardHeader>
          <CardBody>
            <Flex direction="column" gap="md">
              <div>
                <Text weight="medium">Total Reports</Text>
                <Text size="lg" color="primary">{data?.totalReports || 0}</Text>
              </div>
              <div>
                <Text weight="medium">Total Views</Text>
                <Text size="lg" color="primary">{data?.totalViews || 0}</Text>
              </div>
              <div>
                <Text weight="medium">Total Downloads</Text>
                <Text size="lg" color="primary">{data?.totalDownloads || 0}</Text>
              </div>
              <div>
                <Text weight="medium">Total Shares</Text>
                <Text size="lg" color="primary">{data?.totalShares || 0}</Text>
              </div>
            </Flex>
          </CardBody>
        </Card>
      </GridItem>
      <GridItem>
        <Card>
          <CardHeader>
            <Heading level={4}>Popular Reports</Heading>
          </CardHeader>
          <CardBody>
            <div>
              {data?.popularReports?.slice(0, 5).map((report: any, index: number) => (
                <div key={report.id} style={{ 
                  padding: '8px', 
                  border: '1px solid #e5e7eb', 
                  borderRadius: '4px',
                  marginBottom: '8px'
                }}>
                  <Flex justify="between" align="center">
                    <div>
                      <Text weight="medium">{report.title}</Text>
                      <Text size="sm" color="gray">{report.views} views</Text>
                    </div>
                    <Badge variant="secondary">#{index + 1}</Badge>
                  </Flex>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </GridItem>
    </Grid>
  )
}

// Modal Components (simplified for brevity)
const ReportDetailsModal: React.FC<any> = ({ report, onClose }) => (
  <Modal isOpen={true} onClose={onClose} title={report.title} size="lg">
    <div style={{ padding: '16px' }}>
      <Text>Report details would be shown here...</Text>
    </div>
  </Modal>
)

const VersionHistoryModal: React.FC<any> = ({ report, onClose }) => (
  <Modal isOpen={true} onClose={onClose} title={`Version History - ${report.title}`} size="lg">
    <div style={{ padding: '16px' }}>
      <Text>Version history would be shown here...</Text>
    </div>
  </Modal>
)

const CommentsModal: React.FC<any> = ({ report, onClose }) => (
  <Modal isOpen={true} onClose={onClose} title={`Comments - ${report.title}`} size="lg">
    <div style={{ padding: '16px' }}>
      <Text>Comments would be shown here...</Text>
    </div>
  </Modal>
)

const SchedulesModal: React.FC<any> = ({ report, onClose }) => (
  <Modal isOpen={true} onClose={onClose} title={`Schedules - ${report.title}`} size="lg">
    <div style={{ padding: '16px' }}>
      <Text>Schedules would be shown here...</Text>
    </div>
  </Modal>
)

const ReportAnalyticsModal: React.FC<any> = ({ report, onClose }) => (
  <Modal isOpen={true} onClose={onClose} title={`Analytics - ${report.title}`} size="lg">
    <div style={{ padding: '16px' }}>
      <Text>Report analytics would be shown here...</Text>
    </div>
  </Modal>
)

export default ReportManagement
