/**
 * Report Builder Component
 * 
 * Drag-and-drop report builder with real-time preview and content validation
 */

import React, { useState, useCallback, useMemo, useRef } from 'react'
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd'
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
  ReportBuilder, 
  ReportSection, 
  ReportChart, 
  ReportTable,
  ValidationResult,
  DragItem,
  ReportSectionTemplate,
  ReportChartTemplate,
  ReportTableTemplate
} from '../../types/reports'
import { builderUtils, dragDropUtils, templateUtils } from '../../utils/reports'
import { useCreateReport, useUpdateReport } from '../../hooks/api/useReports'

interface ReportBuilderProps {
  initialBuilder?: ReportBuilder
  template?: any
  onSave?: (builder: ReportBuilder) => void
  onPreview?: (builder: ReportBuilder) => void
  onExport?: (builder: ReportBuilder) => void
  readOnly?: boolean
}

export const ReportBuilderComponent: React.FC<ReportBuilderProps> = ({
  initialBuilder,
  template,
  onSave,
  onPreview,
  onExport,
  readOnly = false,
}) => {
  const [builder, setBuilder] = useState<ReportBuilder>(() => 
    initialBuilder || builderUtils.createBuilder(template)
  )
  const [selectedSection, setSelectedSection] = useState<string | null>(null)
  const [showSectionModal, setShowSectionModal] = useState(false)
  const [showChartModal, setShowChartModal] = useState(false)
  const [showTableModal, setShowTableModal] = useState(false)
  const [editingItem, setEditingItem] = useState<any>(null)
  const [validation, setValidation] = useState<ValidationResult | null>(null)
  const [isPreviewMode, setIsPreviewMode] = useState(false)
  const [autoSave, setAutoSave] = useState(true)
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout>()

  // API hooks
  const createReportMutation = useCreateReport()
  const updateReportMutation = useUpdateReport()

  // Auto-save functionality
  const handleAutoSave = useCallback(() => {
    if (autoSave && !readOnly) {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current)
      }
      autoSaveTimeoutRef.current = setTimeout(() => {
        if (onSave) {
          onSave(builder)
        }
      }, 2000)
    }
  }, [builder, autoSave, onSave, readOnly])

  // Update builder and trigger auto-save
  const updateBuilder = useCallback((updates: Partial<ReportBuilder>) => {
    const newBuilder = { ...builder, ...updates, updatedAt: new Date().toISOString() }
    setBuilder(newBuilder)
    
    // Validate builder
    const validationResult = builderUtils.validateBuilder(newBuilder)
    setValidation(validationResult)
    
    handleAutoSave()
  }, [builder, handleAutoSave])

  // Handle drag and drop
  const handleDragEnd = useCallback((result: DropResult) => {
    if (!result.destination) return

    const { source, destination, draggableId } = result

    // Handle section reordering
    if (source.droppableId === 'sections' && destination.droppableId === 'sections') {
      const newSections = Array.from(builder.sections)
      const [reorderedSection] = newSections.splice(source.index, 1)
      newSections.splice(destination.index, 0, reorderedSection)

      // Update order numbers
      const updatedSections = newSections.map((section, index) => ({
        ...section,
        order: index + 1,
      }))

      updateBuilder({ sections: updatedSections })
    }

    // Handle adding new sections from template
    if (source.droppableId.startsWith('template-') && destination.droppableId === 'sections') {
      const templateType = source.droppableId.replace('template-', '')
      const templateId = draggableId

      if (templateType === 'section') {
        const sectionTemplate = template?.sections?.find((s: ReportSectionTemplate) => s.id === templateId)
        if (sectionTemplate) {
          const newSection: ReportSection = {
            id: `section-${Date.now()}`,
            templateId: sectionTemplate.id,
            title: sectionTemplate.title,
            type: sectionTemplate.type,
            content: sectionTemplate.content || '',
            order: destination.index + 1,
            config: sectionTemplate.config,
            isCollapsed: false,
            isValid: true,
            errors: [],
            warnings: [],
          }

          const updatedSections = [...builder.sections]
          updatedSections.splice(destination.index, 0, newSection)

          // Update order numbers
          const reorderedSections = updatedSections.map((section, index) => ({
            ...section,
            order: index + 1,
          }))

          updateBuilder({ sections: reorderedSections })
        }
      }
    }
  }, [builder.sections, template, updateBuilder])

  // Section actions
  const handleAddSection = useCallback(() => {
    setEditingItem(null)
    setShowSectionModal(true)
  }, [])

  const handleEditSection = useCallback((section: ReportSection) => {
    setEditingItem(section)
    setShowSectionModal(true)
  }, [])

  const handleDeleteSection = useCallback((sectionId: string) => {
    const updatedSections = builder.sections
      .filter(s => s.id !== sectionId)
      .map((section, index) => ({ ...section, order: index + 1 }))
    
    updateBuilder({ sections: updatedSections })
  }, [builder.sections, updateBuilder])

  const handleUpdateSection = useCallback((sectionId: string, updates: Partial<ReportSection>) => {
    const updatedSections = builder.sections.map(section =>
      section.id === sectionId ? { ...section, ...updates } : section
    )
    updateBuilder({ sections: updatedSections })
  }, [builder.sections, updateBuilder])

  // Chart actions
  const handleAddChart = useCallback(() => {
    setEditingItem(null)
    setShowChartModal(true)
  }, [])

  const handleEditChart = useCallback((chart: ReportChart) => {
    setEditingItem(chart)
    setShowChartModal(true)
  }, [])

  const handleDeleteChart = useCallback((chartId: string) => {
    const updatedCharts = builder.charts.filter(c => c.id !== chartId)
    updateBuilder({ charts: updatedCharts })
  }, [builder.charts, updateBuilder])

  // Table actions
  const handleAddTable = useCallback(() => {
    setEditingItem(null)
    setShowTableModal(true)
  }, [])

  const handleEditTable = useCallback((table: ReportTable) => {
    setEditingItem(table)
    setShowTableModal(true)
  }, [])

  const handleDeleteTable = useCallback((tableId: string) => {
    const updatedTables = builder.tables.filter(t => t.id !== tableId)
    updateBuilder({ tables: updatedTables })
  }, [builder.tables, updateBuilder])

  // Save report
  const handleSaveReport = useCallback(async () => {
    try {
      if (builder.id && builder.id.startsWith('temp-')) {
        // Create new report
        await createReportMutation.mutateAsync({
          title: builder.name,
          type: builder.template || 'custom',
          content: {
            sections: builder.sections,
            charts: builder.charts,
            tables: builder.tables,
            summary: { executive: '', keyFindings: [], recommendations: [], risks: [], opportunities: [], confidence: 0 },
            recommendations: [],
            disclaimers: [],
            citations: [],
            metadata: builder.metadata,
          },
        })
      } else {
        // Update existing report
        await updateReportMutation.mutateAsync({
          reportId: builder.id,
          data: {
            title: builder.name,
            content: {
              sections: builder.sections,
              charts: builder.charts,
              tables: builder.tables,
              summary: { executive: '', keyFindings: [], recommendations: [], risks: [], opportunities: [], confidence: 0 },
              recommendations: [],
              disclaimers: [],
              citations: [],
              metadata: builder.metadata,
            },
          },
        })
      }
    } catch (error) {
      console.error('Failed to save report:', error)
    }
  }, [builder, createReportMutation, updateReportMutation])

  // Preview mode toggle
  const togglePreviewMode = useCallback(() => {
    setIsPreviewMode(!isPreviewMode)
  }, [isPreviewMode])

  // Validation status
  const validationStatus = useMemo(() => {
    if (!validation) return { status: 'unknown', message: 'Not validated' }
    if (validation.isValid) return { status: 'valid', message: 'Report is valid' }
    return { status: 'invalid', message: `${validation.errors.length} errors, ${validation.warnings.length} warnings` }
  }, [validation])

  return (
    <Container>
      {/* Header */}
      <Card mb="lg">
        <CardBody>
          <Flex justify="between" align="center">
            <div>
              <Input
                value={builder.name}
                onChange={(e) => updateBuilder({ name: e.target.value })}
                placeholder="Report Name"
                style={{ fontSize: '1.5rem', fontWeight: 'bold', border: 'none', padding: 0 }}
                disabled={readOnly}
              />
              <Text color="gray" size="sm">
                {builder.sections.length} sections, {builder.charts.length} charts, {builder.tables.length} tables
              </Text>
            </div>
            <Flex gap="md" align="center">
              <Badge 
                variant={validationStatus.status === 'valid' ? 'success' : validationStatus.status === 'invalid' ? 'error' : 'secondary'}
              >
                {validationStatus.message}
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={togglePreviewMode}
              >
                {isPreviewMode ? 'Edit' : 'Preview'}
              </Button>
              {!readOnly && (
                <Button
                  variant="primary"
                  onClick={handleSaveReport}
                  disabled={createReportMutation.isPending || updateReportMutation.isPending}
                >
                  {(createReportMutation.isPending || updateReportMutation.isPending) ? (
                    <Spinner size="sm" />
                  ) : (
                    'Save Report'
                  )}
                </Button>
              )}
            </Flex>
          </Flex>
        </CardBody>
      </Card>

      <DragDropContext onDragEnd={handleDragEnd}>
        <Grid columns={isPreviewMode ? 1 : 3} gap="lg">
          {/* Left Panel - Template Sections */}
          {!isPreviewMode && (
            <GridItem>
              <Card>
                <CardHeader>
                  <Heading level={4}>Template Sections</Heading>
                </CardHeader>
                <CardBody>
                  <Flex direction="column" gap="sm">
                    {template?.sections?.map((sectionTemplate: ReportSectionTemplate) => (
                      <Droppable key={`template-section-${sectionTemplate.id}`} droppableId={`template-section-${sectionTemplate.id}`}>
                        {(provided) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.droppableProps}
                            style={{
                              padding: '12px',
                              border: '1px dashed #d1d5db',
                              borderRadius: '4px',
                              backgroundColor: '#f9fafb',
                              cursor: 'grab',
                            }}
                          >
                            <Draggable draggableId={sectionTemplate.id} index={0}>
                              {(provided) => (
                                <div
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                  {...provided.dragHandleProps}
                                >
                                  <Flex justify="between" align="center">
                                    <div>
                                      <Text weight="medium">{sectionTemplate.title}</Text>
                                      <Text size="sm" color="gray">{sectionTemplate.type}</Text>
                                    </div>
                                    {sectionTemplate.required && (
                                      <Badge variant="warning" size="sm">Required</Badge>
                                    )}
                                  </Flex>
                                </div>
                              )}
                            </Draggable>
                            {provided.placeholder}
                          </div>
                        )}
                      </Droppable>
                    ))}
                  </Flex>
                </CardBody>
              </Card>
            </GridItem>
          )}

          {/* Center Panel - Report Sections */}
          <GridItem span={isPreviewMode ? 1 : 2}>
            <Card>
              <CardHeader>
                <Flex justify="between" align="center">
                  <Heading level={4}>Report Sections</Heading>
                  {!readOnly && !isPreviewMode && (
                    <Button variant="outline" size="sm" onClick={handleAddSection}>
                      Add Section
                    </Button>
                  )}
                </Flex>
              </CardHeader>
              <CardBody>
                <Droppable droppableId="sections">
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      style={{
                        minHeight: '200px',
                        backgroundColor: snapshot.isDraggingOver ? '#f0f9ff' : 'transparent',
                        border: snapshot.isDraggingOver ? '2px dashed #3b82f6' : '1px dashed #d1d5db',
                        borderRadius: '4px',
                        padding: '8px',
                      }}
                    >
                      {builder.sections.length === 0 ? (
                        <div style={{ 
                          textAlign: 'center', 
                          padding: '40px', 
                          color: '#6b7280' 
                        }}>
                          <Text>Drag sections here or click "Add Section" to get started</Text>
                        </div>
                      ) : (
                        builder.sections.map((section, index) => (
                          <Draggable key={section.id} draggableId={section.id} index={index}>
                            {(provided, snapshot) => (
                              <div
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                style={{
                                  ...provided.draggableProps.style,
                                  marginBottom: '8px',
                                }}
                              >
                                <SectionCard
                                  section={section}
                                  isDragging={snapshot.isDragging}
                                  onEdit={() => handleEditSection(section)}
                                  onDelete={() => handleDeleteSection(section.id)}
                                  onToggleCollapse={() => handleUpdateSection(section.id, { isCollapsed: !section.isCollapsed })}
                                  readOnly={readOnly}
                                  dragHandleProps={provided.dragHandleProps}
                                />
                              </div>
                            )}
                          </Draggable>
                        ))
                      )}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </CardBody>
            </Card>

            {/* Charts Section */}
            <Card mt="lg">
              <CardHeader>
                <Flex justify="between" align="center">
                  <Heading level={4}>Charts</Heading>
                  {!readOnly && !isPreviewMode && (
                    <Button variant="outline" size="sm" onClick={handleAddChart}>
                      Add Chart
                    </Button>
                  )}
                </Flex>
              </CardHeader>
              <CardBody>
                {builder.charts.length === 0 ? (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '20px', 
                    color: '#6b7280' 
                  }}>
                    <Text>No charts added yet</Text>
                  </div>
                ) : (
                  <Grid columns={2} gap="md">
                    {builder.charts.map((chart) => (
                      <GridItem key={chart.id}>
                        <ChartCard
                          chart={chart}
                          onEdit={() => handleEditChart(chart)}
                          onDelete={() => handleDeleteChart(chart.id)}
                          readOnly={readOnly}
                        />
                      </GridItem>
                    ))}
                  </Grid>
                )}
              </CardBody>
            </Card>

            {/* Tables Section */}
            <Card mt="lg">
              <CardHeader>
                <Flex justify="between" align="center">
                  <Heading level={4}>Tables</Heading>
                  {!readOnly && !isPreviewMode && (
                    <Button variant="outline" size="sm" onClick={handleAddTable}>
                      Add Table
                    </Button>
                  )}
                </Flex>
              </CardHeader>
              <CardBody>
                {builder.tables.length === 0 ? (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '20px', 
                    color: '#6b7280' 
                  }}>
                    <Text>No tables added yet</Text>
                  </div>
                ) : (
                  <div>
                    {builder.tables.map((table) => (
                      <TableCard
                        key={table.id}
                        table={table}
                        onEdit={() => handleEditTable(table)}
                        onDelete={() => handleDeleteTable(table.id)}
                        readOnly={readOnly}
                      />
                    ))}
                  </div>
                )}
              </CardBody>
            </Card>
          </GridItem>
        </Grid>
      </DragDropContext>

      {/* Section Modal */}
      {showSectionModal && (
        <SectionModal
          section={editingItem}
          onClose={() => setShowSectionModal(false)}
          onSave={(sectionData) => {
            if (editingItem) {
              handleUpdateSection(editingItem.id, sectionData)
            } else {
              const newSection: ReportSection = {
                id: `section-${Date.now()}`,
                title: sectionData.title,
                type: sectionData.type,
                content: sectionData.content,
                order: builder.sections.length + 1,
                config: sectionData.config || {},
                isCollapsed: false,
                isValid: true,
                errors: [],
                warnings: [],
              }
              updateBuilder({ sections: [...builder.sections, newSection] })
            }
            setShowSectionModal(false)
          }}
        />
      )}

      {/* Chart Modal */}
      {showChartModal && (
        <ChartModal
          chart={editingItem}
          onClose={() => setShowChartModal(false)}
          onSave={(chartData) => {
            if (editingItem) {
              const updatedCharts = builder.charts.map(c =>
                c.id === editingItem.id ? { ...c, ...chartData } : c
              )
              updateBuilder({ charts: updatedCharts })
            } else {
              const newChart: ReportChart = {
                id: `chart-${Date.now()}`,
                title: chartData.title,
                type: chartData.type,
                dataSource: chartData.dataSource,
                data: null,
                config: chartData.config || {},
                order: builder.charts.length + 1,
                isVisible: true,
                isValid: false,
                errors: ['Data not loaded'],
              }
              updateBuilder({ charts: [...builder.charts, newChart] })
            }
            setShowChartModal(false)
          }}
        />
      )}

      {/* Table Modal */}
      {showTableModal && (
        <TableModal
          table={editingItem}
          onClose={() => setShowTableModal(false)}
          onSave={(tableData) => {
            if (editingItem) {
              const updatedTables = builder.tables.map(t =>
                t.id === editingItem.id ? { ...t, ...tableData } : t
              )
              updateBuilder({ tables: updatedTables })
            } else {
              const newTable: ReportTable = {
                id: `table-${Date.now()}`,
                title: tableData.title,
                dataSource: tableData.dataSource,
                headers: [],
                rows: [],
                config: tableData.config || {},
                order: builder.tables.length + 1,
                isVisible: true,
                isValid: false,
                errors: ['Data not loaded'],
              }
              updateBuilder({ tables: [...builder.tables, newTable] })
            }
            setShowTableModal(false)
          }}
        />
      )}
    </Container>
  )
}

// Section Card Component
interface SectionCardProps {
  section: ReportSection
  isDragging: boolean
  onEdit: () => void
  onDelete: () => void
  onToggleCollapse: () => void
  readOnly: boolean
  dragHandleProps: any
}

const SectionCard: React.FC<SectionCardProps> = ({
  section,
  isDragging,
  onEdit,
  onDelete,
  onToggleCollapse,
  readOnly,
  dragHandleProps,
}) => {
  return (
    <Card style={{ 
      opacity: isDragging ? 0.5 : 1,
      border: section.isValid ? '1px solid #e5e7eb' : '1px solid #ef4444',
    }}>
      <CardHeader>
        <Flex justify="between" align="center">
          <Flex align="center" gap="sm">
            <div {...dragHandleProps} style={{ cursor: 'grab' }}>
              <span>⋮⋮</span>
            </div>
            <div>
              <Heading level={5}>{section.title}</Heading>
              <Text size="sm" color="gray">{section.type}</Text>
            </div>
          </Flex>
          <Flex gap="sm" align="center">
            {!section.isValid && (
              <Badge variant="error" size="sm">
                {section.errors.length} errors
              </Badge>
            )}
            {section.warnings.length > 0 && (
              <Badge variant="warning" size="sm">
                {section.warnings.length} warnings
              </Badge>
            )}
            {!readOnly && (
              <>
                <Button variant="ghost" size="sm" onClick={onToggleCollapse}>
                  {section.isCollapsed ? 'Expand' : 'Collapse'}
                </Button>
                <Button variant="ghost" size="sm" onClick={onEdit}>
                  Edit
                </Button>
                <Button variant="ghost" size="sm" onClick={onDelete} color="red">
                  Delete
                </Button>
              </>
            )}
          </Flex>
        </Flex>
      </CardHeader>
      {!section.isCollapsed && (
        <CardBody>
          {section.type === 'text' ? (
            <div style={{ 
              minHeight: '100px', 
              padding: '12px', 
              border: '1px solid #e5e7eb', 
              borderRadius: '4px',
              backgroundColor: '#f9fafb'
            }}>
              {section.content || <Text color="gray">Click edit to add content</Text>}
            </div>
          ) : (
            <Text color="gray">Section content will be generated automatically</Text>
          )}
        </CardBody>
      )}
    </Card>
  )
}

// Chart Card Component
interface ChartCardProps {
  chart: ReportChart
  onEdit: () => void
  onDelete: () => void
  readOnly: boolean
}

const ChartCard: React.FC<ChartCardProps> = ({ chart, onEdit, onDelete, readOnly }) => {
  return (
    <Card>
      <CardHeader>
        <Flex justify="between" align="center">
          <div>
            <Heading level={5}>{chart.title}</Heading>
            <Text size="sm" color="gray">{chart.type} chart</Text>
          </div>
          {!readOnly && (
            <Flex gap="sm">
              <Button variant="ghost" size="sm" onClick={onEdit}>
                Edit
              </Button>
              <Button variant="ghost" size="sm" onClick={onDelete} color="red">
                Delete
              </Button>
            </Flex>
          )}
        </Flex>
      </CardHeader>
      <CardBody>
        <div style={{ 
          height: '200px', 
          backgroundColor: '#f9fafb', 
          border: '1px solid #e5e7eb',
          borderRadius: '4px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {chart.isValid ? (
            <Text color="gray">Chart will be rendered here</Text>
          ) : (
            <Text color="red">Chart has errors: {chart.errors.join(', ')}</Text>
          )}
        </div>
      </CardBody>
    </Card>
  )
}

// Table Card Component
interface TableCardProps {
  table: ReportTable
  onEdit: () => void
  onDelete: () => void
  readOnly: boolean
}

const TableCard: React.FC<TableCardProps> = ({ table, onEdit, onDelete, readOnly }) => {
  return (
    <Card mb="md">
      <CardHeader>
        <Flex justify="between" align="center">
          <div>
            <Heading level={5}>{table.title}</Heading>
            <Text size="sm" color="gray">Data table</Text>
          </div>
          {!readOnly && (
            <Flex gap="sm">
              <Button variant="ghost" size="sm" onClick={onEdit}>
                Edit
              </Button>
              <Button variant="ghost" size="sm" onClick={onDelete} color="red">
                Delete
              </Button>
            </Flex>
          )}
        </Flex>
      </CardHeader>
      <CardBody>
        <div style={{ 
          minHeight: '100px', 
          backgroundColor: '#f9fafb', 
          border: '1px solid #e5e7eb',
          borderRadius: '4px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {table.isValid ? (
            <Text color="gray">Table will be rendered here</Text>
          ) : (
            <Text color="red">Table has errors: {table.errors.join(', ')}</Text>
          )}
        </div>
      </CardBody>
    </Card>
  )
}

// Section Modal Component
interface SectionModalProps {
  section?: ReportSection | null
  onClose: () => void
  onSave: (data: Partial<ReportSection>) => void
}

const SectionModal: React.FC<SectionModalProps> = ({ section, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: section?.title || '',
    type: section?.type || 'text',
    content: section?.content || '',
    config: section?.config || {},
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={section ? 'Edit Section' : 'Add Section'}
      size="lg"
    >
      <form onSubmit={handleSubmit}>
        <div style={{ padding: '16px' }}>
          <Flex direction="column" gap="md">
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Section Title *
              </label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Enter section title"
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Section Type
              </label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px' }}
              >
                <option value="text">Text</option>
                <option value="analysis">Analysis</option>
                <option value="executive_summary">Executive Summary</option>
                <option value="risk_assessment">Risk Assessment</option>
                <option value="valuation">Valuation</option>
                <option value="technical_analysis">Technical Analysis</option>
                <option value="peer_comparison">Peer Comparison</option>
              </select>
            </div>

            {formData.type === 'text' && (
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                  Content
                </label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  placeholder="Enter section content"
                  rows={8}
                  style={{ 
                    width: '100%', 
                    padding: '8px', 
                    border: '1px solid #d1d5db', 
                    borderRadius: '4px',
                    resize: 'vertical'
                  }}
                />
              </div>
            )}
          </Flex>
        </div>

        <Flex justify="end" gap="md" style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            {section ? 'Update' : 'Add'} Section
          </Button>
        </Flex>
      </form>
    </Modal>
  )
}

// Chart Modal Component
interface ChartModalProps {
  chart?: ReportChart | null
  onClose: () => void
  onSave: (data: Partial<ReportChart>) => void
}

const ChartModal: React.FC<ChartModalProps> = ({ chart, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: chart?.title || '',
    type: chart?.type || 'line',
    dataSource: chart?.dataSource || '',
    config: chart?.config || {},
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={chart ? 'Edit Chart' : 'Add Chart'}
      size="md"
    >
      <form onSubmit={handleSubmit}>
        <div style={{ padding: '16px' }}>
          <Flex direction="column" gap="md">
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Chart Title *
              </label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Enter chart title"
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Chart Type
              </label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px' }}
              >
                <option value="line">Line Chart</option>
                <option value="bar">Bar Chart</option>
                <option value="pie">Pie Chart</option>
                <option value="scatter">Scatter Plot</option>
                <option value="candlestick">Candlestick Chart</option>
                <option value="heatmap">Heatmap</option>
                <option value="gauge">Gauge</option>
                <option value="treemap">Treemap</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Data Source
              </label>
              <Input
                value={formData.dataSource}
                onChange={(e) => setFormData({ ...formData, dataSource: e.target.value })}
                placeholder="Enter data source"
              />
            </div>
          </Flex>
        </div>

        <Flex justify="end" gap="md" style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            {chart ? 'Update' : 'Add'} Chart
          </Button>
        </Flex>
      </form>
    </Modal>
  )
}

// Table Modal Component
interface TableModalProps {
  table?: ReportTable | null
  onClose: () => void
  onSave: (data: Partial<ReportTable>) => void
}

const TableModal: React.FC<TableModalProps> = ({ table, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: table?.title || '',
    dataSource: table?.dataSource || '',
    config: table?.config || {},
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={table ? 'Edit Table' : 'Add Table'}
      size="md"
    >
      <form onSubmit={handleSubmit}>
        <div style={{ padding: '16px' }}>
          <Flex direction="column" gap="md">
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Table Title *
              </label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Enter table title"
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Data Source
              </label>
              <Input
                value={formData.dataSource}
                onChange={(e) => setFormData({ ...formData, dataSource: e.target.value })}
                placeholder="Enter data source"
              />
            </div>
          </Flex>
        </div>

        <Flex justify="end" gap="md" style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            {table ? 'Update' : 'Add'} Table
          </Button>
        </Flex>
      </form>
    </Modal>
  )
}

export default ReportBuilderComponent
