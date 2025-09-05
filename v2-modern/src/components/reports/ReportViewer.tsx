/**
 * Report Viewer Component
 * 
 * Full-screen report viewing with interactive charts, annotations, and bookmarks
 */

import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react'
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
  ReportViewer as ReportViewerType,
  Annotation,
  Bookmark,
  Highlight,
  Note,
  AnnotationPosition
} from '../../types/reports'
import { annotationUtils, formatDate } from '../../utils/reports'
import { 
  useReport,
  useAddReportComment,
  useReportComments,
  useReportVersions
} from '../../hooks/api/useReports'

interface ReportViewerProps {
  reportId: string
  onClose?: () => void
  onEdit?: () => void
  onExport?: () => void
  onShare?: () => void
  readOnly?: boolean
  showAnnotations?: boolean
  showBookmarks?: boolean
  showComments?: boolean
  showVersions?: boolean
}

export const ReportViewer: React.FC<ReportViewerProps> = ({
  reportId,
  onClose,
  onEdit,
  onExport,
  onShare,
  readOnly = false,
  showAnnotations = true,
  showBookmarks = true,
  showComments = true,
  showVersions = true,
}) => {
  const [viewer, setViewer] = useState<ReportViewerType | null>(null)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [zoom, setZoom] = useState(100)
  const [currentSection, setCurrentSection] = useState<string>('')
  const [showAnnotationModal, setShowAnnotationModal] = useState(false)
  const [showBookmarkModal, setShowBookmarkModal] = useState(false)
  const [showCommentModal, setShowCommentModal] = useState(false)
  const [showVersionModal, setShowVersionModal] = useState(false)
  const [selectedAnnotation, setSelectedAnnotation] = useState<Annotation | null>(null)
  const [selectedBookmark, setSelectedBookmark] = useState<Bookmark | null>(null)
  const [annotationPosition, setAnnotationPosition] = useState<AnnotationPosition | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [sidebarTab, setSidebarTab] = useState<'outline' | 'annotations' | 'bookmarks' | 'comments' | 'versions'>('outline')
  
  const viewerRef = useRef<HTMLDivElement>(null)
  const [isLoading, setIsLoading] = useState(true)

  // API hooks
  const { data: report, isLoading: reportLoading } = useReport(reportId)
  const { data: comments } = useReportComments(reportId, showComments)
  const { data: versions } = useReportVersions(reportId, showVersions)
  const addCommentMutation = useAddReportComment()

  // Initialize viewer
  useEffect(() => {
    if (report) {
      const initialViewer: ReportViewerType = {
        report,
        currentSection: report.content.sections[0]?.id || '',
        viewMode: 'full',
        zoom: 100,
        annotations: [],
        bookmarks: [],
        highlights: [],
        notes: [],
        isFullscreen: false,
        isPrintMode: false,
        showComments: showComments,
        showAnnotations: showAnnotations,
        showBookmarks: showBookmarks,
        showHighlights: true,
        showNotes: true,
      }
      setViewer(initialViewer)
      setCurrentSection(initialViewer.currentSection)
      setIsLoading(false)
    }
  }, [report, showComments, showAnnotations, showBookmarks])

  // Handle fullscreen toggle
  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      viewerRef.current?.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }, [])

  // Handle zoom
  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(prev + 25, 200))
  }, [])

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(prev - 25, 50))
  }, [])

  const handleZoomReset = useCallback(() => {
    setZoom(100)
  }, [])

  // Handle section navigation
  const handleSectionClick = useCallback((sectionId: string) => {
    setCurrentSection(sectionId)
    setViewer(prev => prev ? { ...prev, currentSection: sectionId } : null)
    
    // Scroll to section
    const element = document.getElementById(`section-${sectionId}`)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }, [])

  // Handle annotation creation
  const handleCreateAnnotation = useCallback((position: AnnotationPosition) => {
    setAnnotationPosition(position)
    setShowAnnotationModal(true)
  }, [])

  const handleSaveAnnotation = useCallback((annotationData: Partial<Annotation>) => {
    if (annotationPosition && viewer) {
      const newAnnotation = annotationUtils.createAnnotation({
        ...annotationData,
        position: annotationPosition,
        author: 'Current User', // This would come from auth context
      })
      
      setViewer(prev => prev ? {
        ...prev,
        annotations: [...prev.annotations, newAnnotation]
      } : null)
      
      setShowAnnotationModal(false)
      setAnnotationPosition(null)
    }
  }, [annotationPosition, viewer])

  // Handle bookmark creation
  const handleCreateBookmark = useCallback((sectionId: string) => {
    setSelectedBookmark({
      id: '',
      title: '',
      sectionId,
      position: 0,
      description: '',
      createdAt: new Date().toISOString(),
    })
    setShowBookmarkModal(true)
  }, [])

  const handleSaveBookmark = useCallback((bookmarkData: Partial<Bookmark>) => {
    if (viewer) {
      const newBookmark = annotationUtils.createBookmark({
        ...bookmarkData,
        sectionId: selectedBookmark?.sectionId || '',
        position: 0,
      })
      
      setViewer(prev => prev ? {
        ...prev,
        bookmarks: [...prev.bookmarks, newBookmark]
      } : null)
      
      setShowBookmarkModal(false)
      setSelectedBookmark(null)
    }
  }, [viewer, selectedBookmark])

  // Handle comment creation
  const handleCreateComment = useCallback((sectionId: string) => {
    setShowCommentModal(true)
  }, [])

  const handleSaveComment = useCallback(async (comment: string) => {
    try {
      await addCommentMutation.mutateAsync({
        reportId,
        comment,
      })
      setShowCommentModal(false)
    } catch (error) {
      console.error('Failed to add comment:', error)
    }
  }, [reportId, addCommentMutation])

  // Handle print
  const handlePrint = useCallback(() => {
    window.print()
  }, [])

  // Handle text selection for highlighting
  const handleTextSelection = useCallback(() => {
    const selection = window.getSelection()
    if (selection && selection.toString().trim()) {
      const range = selection.getRangeAt(0)
      const rect = range.getBoundingClientRect()
      
      // Create highlight
      const newHighlight = annotationUtils.createHighlight({
        text: selection.toString(),
        sectionId: currentSection,
        startOffset: range.startOffset,
        endOffset: range.endOffset,
        color: '#ffff00',
        author: 'Current User',
      })
      
      setViewer(prev => prev ? {
        ...prev,
        highlights: [...prev.highlights, newHighlight]
      } : null)
    }
  }, [currentSection])

  if (isLoading || reportLoading) {
    return (
      <Container>
        <Flex justify="center" align="center" style={{ height: '200px' }}>
          <Spinner size="lg" />
        </Flex>
      </Container>
    )
  }

  if (!report || !viewer) {
    return (
      <Container>
        <Card>
          <CardBody>
            <Text color="red">Report not found</Text>
          </CardBody>
        </Card>
      </Container>
    )
  }

  return (
    <div 
      ref={viewerRef}
      style={{ 
        height: '100vh', 
        display: 'flex', 
        flexDirection: 'column',
        backgroundColor: '#ffffff'
      }}
    >
      {/* Header */}
      <div style={{ 
        padding: '16px', 
        borderBottom: '1px solid #e5e7eb',
        backgroundColor: '#f9fafb'
      }}>
        <Flex justify="between" align="center">
          <div>
            <Heading level={3}>{report.title}</Heading>
            <Text color="gray" size="sm">
              {report.metadata.author} • v{report.version} • {formatDate(report.updatedAt)}
            </Text>
          </div>
          <Flex gap="md" align="center">
            <Flex gap="sm" align="center">
              <Button variant="ghost" size="sm" onClick={handleZoomOut}>
                -
              </Button>
              <Text size="sm">{zoom}%</Text>
              <Button variant="ghost" size="sm" onClick={handleZoomIn}>
                +
              </Button>
              <Button variant="ghost" size="sm" onClick={handleZoomReset}>
                Reset
              </Button>
            </Flex>
            <Button variant="ghost" size="sm" onClick={() => setSidebarOpen(!sidebarOpen)}>
              {sidebarOpen ? 'Hide' : 'Show'} Sidebar
            </Button>
            <Button variant="ghost" size="sm" onClick={toggleFullscreen}>
              {isFullscreen ? 'Exit' : 'Enter'} Fullscreen
            </Button>
            {!readOnly && onEdit && (
              <Button variant="outline" size="sm" onClick={onEdit}>
                Edit
              </Button>
            )}
            {onExport && (
              <Button variant="outline" size="sm" onClick={onExport}>
                Export
              </Button>
            )}
            {onShare && (
              <Button variant="outline" size="sm" onClick={onShare}>
                Share
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={handlePrint}>
              Print
            </Button>
            {onClose && (
              <Button variant="ghost" size="sm" onClick={onClose}>
                Close
              </Button>
            )}
          </Flex>
        </Flex>
      </div>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Sidebar */}
        {sidebarOpen && (
          <div style={{ 
            width: '300px', 
            borderRight: '1px solid #e5e7eb',
            backgroundColor: '#f9fafb',
            overflow: 'auto'
          }}>
            <div style={{ padding: '16px' }}>
              <Flex gap="sm" mb="md">
                <Button
                  variant={sidebarTab === 'outline' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setSidebarTab('outline')}
                >
                  Outline
                </Button>
                {showAnnotations && (
                  <Button
                    variant={sidebarTab === 'annotations' ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setSidebarTab('annotations')}
                  >
                    Notes
                  </Button>
                )}
                {showBookmarks && (
                  <Button
                    variant={sidebarTab === 'bookmarks' ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setSidebarTab('bookmarks')}
                  >
                    Bookmarks
                  </Button>
                )}
                {showComments && (
                  <Button
                    variant={sidebarTab === 'comments' ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setSidebarTab('comments')}
                  >
                    Comments
                  </Button>
                )}
                {showVersions && (
                  <Button
                    variant={sidebarTab === 'versions' ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setSidebarTab('versions')}
                  >
                    Versions
                  </Button>
                )}
              </Flex>

              {/* Sidebar Content */}
              {sidebarTab === 'outline' && (
                <ReportOutline
                  sections={report.content.sections}
                  currentSection={currentSection}
                  onSectionClick={handleSectionClick}
                />
              )}

              {sidebarTab === 'annotations' && (
                <AnnotationsPanel
                  annotations={viewer.annotations}
                  onAnnotationClick={(annotation) => setSelectedAnnotation(annotation)}
                />
              )}

              {sidebarTab === 'bookmarks' && (
                <BookmarksPanel
                  bookmarks={viewer.bookmarks}
                  onBookmarkClick={(bookmark) => handleSectionClick(bookmark.sectionId)}
                />
              )}

              {sidebarTab === 'comments' && (
                <CommentsPanel
                  comments={comments || []}
                  onCommentClick={(comment) => handleSectionClick(comment.sectionId || '')}
                />
              )}

              {sidebarTab === 'versions' && (
                <VersionsPanel
                  versions={versions || []}
                  currentVersion={report.version}
                />
              )}
            </div>
          </div>
        )}

        {/* Main Content */}
        <div style={{ 
          flex: 1, 
          overflow: 'auto',
          padding: '24px',
          transform: `scale(${zoom / 100})`,
          transformOrigin: 'top left',
          width: `${100 / (zoom / 100)}%`,
          height: `${100 / (zoom / 100)}%`
        }}>
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            {/* Report Content */}
            <ReportContent
              report={report}
              viewer={viewer}
              onTextSelection={handleTextSelection}
              onCreateAnnotation={handleCreateAnnotation}
              onCreateBookmark={handleCreateBookmark}
              onCreateComment={handleCreateComment}
              readOnly={readOnly}
            />
          </div>
        </div>
      </div>

      {/* Modals */}
      {showAnnotationModal && (
        <AnnotationModal
          position={annotationPosition}
          onSave={handleSaveAnnotation}
          onClose={() => setShowAnnotationModal(false)}
        />
      )}

      {showBookmarkModal && (
        <BookmarkModal
          bookmark={selectedBookmark}
          onSave={handleSaveBookmark}
          onClose={() => setShowBookmarkModal(false)}
        />
      )}

      {showCommentModal && (
        <CommentModal
          onSave={handleSaveComment}
          onClose={() => setShowCommentModal(false)}
        />
      )}
    </div>
  )
}

// Report Outline Component
interface ReportOutlineProps {
  sections: any[]
  currentSection: string
  onSectionClick: (sectionId: string) => void
}

const ReportOutline: React.FC<ReportOutlineProps> = ({ sections, currentSection, onSectionClick }) => {
  return (
    <div>
      <Heading level={5} mb="md">Table of Contents</Heading>
      <div>
        {sections.map((section, index) => (
          <div
            key={section.id}
            onClick={() => onSectionClick(section.id)}
            style={{
              padding: '8px 12px',
              cursor: 'pointer',
              borderRadius: '4px',
              backgroundColor: currentSection === section.id ? '#e0f2fe' : 'transparent',
              border: currentSection === section.id ? '1px solid #0ea5e9' : '1px solid transparent',
              marginBottom: '4px',
            }}
          >
            <Text size="sm" weight={currentSection === section.id ? 'medium' : 'normal'}>
              {index + 1}. {section.title}
            </Text>
          </div>
        ))}
      </div>
    </div>
  )
}

// Annotations Panel Component
interface AnnotationsPanelProps {
  annotations: Annotation[]
  onAnnotationClick: (annotation: Annotation) => void
}

const AnnotationsPanel: React.FC<AnnotationsPanelProps> = ({ annotations, onAnnotationClick }) => {
  return (
    <div>
      <Heading level={5} mb="md">Annotations ({annotations.length})</Heading>
      <div>
        {annotations.map((annotation) => (
          <div
            key={annotation.id}
            onClick={() => onAnnotationClick(annotation)}
            style={{
              padding: '8px 12px',
              cursor: 'pointer',
              borderRadius: '4px',
              border: '1px solid #e5e7eb',
              marginBottom: '8px',
            }}
          >
            <Text size="sm" weight="medium">{annotation.type}</Text>
            <Text size="sm" color="gray" style={{ 
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }}>
              {annotation.content}
            </Text>
            <Text size="xs" color="gray">
              {formatDate(annotation.createdAt, 'relative')}
            </Text>
          </div>
        ))}
      </div>
    </div>
  )
}

// Bookmarks Panel Component
interface BookmarksPanelProps {
  bookmarks: Bookmark[]
  onBookmarkClick: (sectionId: string) => void
}

const BookmarksPanel: React.FC<BookmarksPanelProps> = ({ bookmarks, onBookmarkClick }) => {
  return (
    <div>
      <Heading level={5} mb="md">Bookmarks ({bookmarks.length})</Heading>
      <div>
        {bookmarks.map((bookmark) => (
          <div
            key={bookmark.id}
            onClick={() => onBookmarkClick(bookmark.sectionId)}
            style={{
              padding: '8px 12px',
              cursor: 'pointer',
              borderRadius: '4px',
              border: '1px solid #e5e7eb',
              marginBottom: '8px',
            }}
          >
            <Text size="sm" weight="medium">🔖 {bookmark.title}</Text>
            {bookmark.description && (
              <Text size="sm" color="gray">{bookmark.description}</Text>
            )}
            <Text size="xs" color="gray">
              {formatDate(bookmark.createdAt, 'relative')}
            </Text>
          </div>
        ))}
      </div>
    </div>
  )
}

// Comments Panel Component
interface CommentsPanelProps {
  comments: any[]
  onCommentClick: (sectionId: string) => void
}

const CommentsPanel: React.FC<CommentsPanelProps> = ({ comments, onCommentClick }) => {
  return (
    <div>
      <Heading level={5} mb="md">Comments ({comments.length})</Heading>
      <div>
        {comments.map((comment) => (
          <div
            key={comment.id}
            onClick={() => onCommentClick(comment.sectionId || '')}
            style={{
              padding: '8px 12px',
              cursor: 'pointer',
              borderRadius: '4px',
              border: '1px solid #e5e7eb',
              marginBottom: '8px',
            }}
          >
            <Text size="sm" weight="medium">{comment.author}</Text>
            <Text size="sm" color="gray" style={{ 
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }}>
              {comment.content}
            </Text>
            <Text size="xs" color="gray">
              {formatDate(comment.createdAt, 'relative')}
            </Text>
          </div>
        ))}
      </div>
    </div>
  )
}

// Versions Panel Component
interface VersionsPanelProps {
  versions: any[]
  currentVersion: string
}

const VersionsPanel: React.FC<VersionsPanelProps> = ({ versions, currentVersion }) => {
  return (
    <div>
      <Heading level={5} mb="md">Version History</Heading>
      <div>
        {versions.map((version) => (
          <div
            key={version.id}
            style={{
              padding: '8px 12px',
              borderRadius: '4px',
              border: version.version === currentVersion ? '1px solid #10b981' : '1px solid #e5e7eb',
              backgroundColor: version.version === currentVersion ? '#f0fdf4' : 'white',
              marginBottom: '8px',
            }}
          >
            <Text size="sm" weight="medium">
              v{version.version} {version.version === currentVersion && '(Current)'}
            </Text>
            <Text size="sm" color="gray">{version.title}</Text>
            <Text size="xs" color="gray">
              {version.author} • {formatDate(version.createdAt, 'relative')}
            </Text>
            {version.changes.length > 0 && (
              <div style={{ marginTop: '4px' }}>
                {version.changes.slice(0, 2).map((change: string, index: number) => (
                  <Text key={index} size="xs" color="gray">• {change}</Text>
                ))}
                {version.changes.length > 2 && (
                  <Text size="xs" color="gray">• +{version.changes.length - 2} more changes</Text>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// Report Content Component
interface ReportContentProps {
  report: SavedReport
  viewer: ReportViewerType
  onTextSelection: () => void
  onCreateAnnotation: (position: AnnotationPosition) => void
  onCreateBookmark: (sectionId: string) => void
  onCreateComment: (sectionId: string) => void
  readOnly: boolean
}

const ReportContent: React.FC<ReportContentProps> = ({
  report,
  viewer,
  onTextSelection,
  onCreateAnnotation,
  onCreateBookmark,
  onCreateComment,
  readOnly,
}) => {
  return (
    <div>
      {/* Executive Summary */}
      {report.content.summary && (
        <Card mb="lg" id="section-executive-summary">
          <CardHeader>
            <Flex justify="between" align="center">
              <Heading level={2}>Executive Summary</Heading>
              {!readOnly && (
                <Flex gap="sm">
                  <Button variant="ghost" size="sm" onClick={() => onCreateBookmark('executive-summary')}>
                    🔖
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => onCreateComment('executive-summary')}>
                    💬
                  </Button>
                </Flex>
              )}
            </Flex>
          </CardHeader>
          <CardBody>
            <Text onMouseUp={onTextSelection}>{report.content.summary.executive}</Text>
          </CardBody>
        </Card>
      )}

      {/* Sections */}
      {report.content.sections.map((section, index) => (
        <Card key={section.id} mb="lg" id={`section-${section.id}`}>
          <CardHeader>
            <Flex justify="between" align="center">
              <Heading level={3}>{section.title}</Heading>
              {!readOnly && (
                <Flex gap="sm">
                  <Button variant="ghost" size="sm" onClick={() => onCreateBookmark(section.id)}>
                    🔖
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => onCreateComment(section.id)}>
                    💬
                  </Button>
                </Flex>
              )}
            </Flex>
          </CardHeader>
          <CardBody>
            {section.type === 'text' ? (
              <div onMouseUp={onTextSelection}>
                <Text>{section.content}</Text>
              </div>
            ) : (
              <div style={{ 
                padding: '40px', 
                textAlign: 'center', 
                backgroundColor: '#f9fafb',
                borderRadius: '4px',
                border: '1px dashed #d1d5db'
              }}>
                <Text color="gray">
                  {section.type} content will be rendered here
                </Text>
              </div>
            )}
          </CardBody>
        </Card>
      ))}

      {/* Charts */}
      {report.content.charts.map((chart) => (
        <Card key={chart.id} mb="lg">
          <CardHeader>
            <Heading level={4}>{chart.title}</Heading>
          </CardHeader>
          <CardBody>
            <div style={{ 
              height: '300px', 
              backgroundColor: '#f9fafb',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px dashed #d1d5db'
            }}>
              <Text color="gray">{chart.type} chart will be rendered here</Text>
            </div>
          </CardBody>
        </Card>
      ))}

      {/* Tables */}
      {report.content.tables.map((table) => (
        <Card key={table.id} mb="lg">
          <CardHeader>
            <Heading level={4}>{table.title}</Heading>
          </CardHeader>
          <CardBody>
            <div style={{ 
              padding: '20px', 
              backgroundColor: '#f9fafb',
              borderRadius: '4px',
              textAlign: 'center',
              border: '1px dashed #d1d5db'
            }}>
              <Text color="gray">Table will be rendered here</Text>
            </div>
          </CardBody>
        </Card>
      ))}

      {/* Recommendations */}
      {report.content.recommendations.length > 0 && (
        <Card mb="lg">
          <CardHeader>
            <Heading level={3}>Recommendations</Heading>
          </CardHeader>
          <CardBody>
            <ul>
              {report.content.recommendations.map((rec, index) => (
                <li key={index} style={{ marginBottom: '8px' }}>
                  <Text onMouseUp={onTextSelection}>{rec.rationale}</Text>
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>
      )}

      {/* Citations */}
      {report.content.citations.length > 0 && (
        <Card mb="lg">
          <CardHeader>
            <Heading level={3}>References</Heading>
          </CardHeader>
          <CardBody>
            <div>
              {report.content.citations.map((citation, index) => (
                <div key={citation.id} style={{ marginBottom: '8px' }}>
                  <Text size="sm">
                    [{index + 1}] {citation.source} - {citation.date}
                  </Text>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}

// Modal Components
const AnnotationModal: React.FC<any> = ({ position, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    type: 'note',
    content: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <Modal isOpen={true} onClose={onClose} title="Add Annotation" size="md">
      <form onSubmit={handleSubmit}>
        <div style={{ padding: '16px' }}>
          <Flex direction="column" gap="md">
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Type
              </label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px' }}
              >
                <option value="note">Note</option>
                <option value="highlight">Highlight</option>
                <option value="comment">Comment</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Content
              </label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                placeholder="Enter annotation content"
                rows={4}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  border: '1px solid #d1d5db', 
                  borderRadius: '4px',
                  resize: 'vertical'
                }}
                required
              />
            </div>
          </Flex>
        </div>
        <Flex justify="end" gap="md" style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Add Annotation
          </Button>
        </Flex>
      </form>
    </Modal>
  )
}

const BookmarkModal: React.FC<any> = ({ bookmark, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    title: bookmark?.title || '',
    description: bookmark?.description || '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <Modal isOpen={true} onClose={onClose} title="Add Bookmark" size="md">
      <form onSubmit={handleSubmit}>
        <div style={{ padding: '16px' }}>
          <Flex direction="column" gap="md">
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Title *
              </label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Enter bookmark title"
                required
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Enter bookmark description"
                rows={3}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  border: '1px solid #d1d5db', 
                  borderRadius: '4px',
                  resize: 'vertical'
                }}
              />
            </div>
          </Flex>
        </div>
        <Flex justify="end" gap="md" style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Add Bookmark
          </Button>
        </Flex>
      </form>
    </Modal>
  )
}

const CommentModal: React.FC<any> = ({ onSave, onClose }) => {
  const [comment, setComment] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(comment)
  }

  return (
    <Modal isOpen={true} onClose={onClose} title="Add Comment" size="md">
      <form onSubmit={handleSubmit}>
        <div style={{ padding: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
              Comment *
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Enter your comment"
              rows={4}
              style={{ 
                width: '100%', 
                padding: '8px', 
                border: '1px solid #d1d5db', 
                borderRadius: '4px',
                resize: 'vertical'
              }}
              required
            />
          </div>
        </div>
        <Flex justify="end" gap="md" style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Add Comment
          </Button>
        </Flex>
      </form>
    </Modal>
  )
}

export default ReportViewer
