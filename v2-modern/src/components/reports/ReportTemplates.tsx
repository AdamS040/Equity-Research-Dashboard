/**
 * Report Templates Component
 * 
 * Pre-built report templates with preview, custom creation, and versioning
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
  ReportTemplate, 
  ReportSectionTemplate, 
  ReportChartTemplate, 
  ReportTableTemplate,
  ValidationResult 
} from '../../types/reports'
import { templateUtils } from '../../utils/reports'
import { useReportTemplates, useCreateFromTemplate, useSaveAsTemplate } from '../../hooks/api/useReports'

interface ReportTemplatesProps {
  onSelectTemplate?: (template: ReportTemplate) => void
  onCreateCustom?: () => void
  onEditTemplate?: (template: ReportTemplate) => void
  showCreateButton?: boolean
  showEditButton?: boolean
  filterByType?: string
  filterByCategory?: string
}

export const ReportTemplates: React.FC<ReportTemplatesProps> = ({
  onSelectTemplate,
  onCreateCustom,
  onEditTemplate,
  showCreateButton = true,
  showEditButton = false,
  filterByType,
  filterByCategory,
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<ReportTemplate | null>(null)
  const [sortBy, setSortBy] = useState<'name' | 'rating' | 'usage' | 'created'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  // API hooks
  const { data: templates = [], isLoading, error } = useReportTemplates(filterByType)
  const createFromTemplateMutation = useCreateFromTemplate()
  const saveAsTemplateMutation = useSaveAsTemplate()

  // Filter and sort templates
  const filteredTemplates = useMemo(() => {
    let filtered = templates

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(template =>
        template.name.toLowerCase().includes(query) ||
        template.description.toLowerCase().includes(query) ||
        template.tags.some(tag => tag.toLowerCase().includes(query))
      )
    }

    // Apply category filter
    if (filterByCategory) {
      filtered = filtered.filter(template => template.category === filterByCategory)
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any, bValue: any

      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase()
          bValue = b.name.toLowerCase()
          break
        case 'rating':
          aValue = a.rating
          bValue = b.rating
          break
        case 'usage':
          aValue = a.usageCount
          bValue = b.usageCount
          break
        case 'created':
          aValue = new Date(a.createdAt)
          bValue = new Date(b.createdAt)
          break
        default:
          aValue = a.name.toLowerCase()
          bValue = b.name.toLowerCase()
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1
      return 0
    })

    return filtered
  }, [templates, searchQuery, filterByCategory, sortBy, sortOrder])

  // Template actions
  const handleSelectTemplate = useCallback((template: ReportTemplate) => {
    if (onSelectTemplate) {
      onSelectTemplate(template)
    } else {
      setSelectedTemplate(template)
      setShowPreview(true)
    }
  }, [onSelectTemplate])

  const handleCreateFromTemplate = useCallback(async (template: ReportTemplate) => {
    try {
      await createFromTemplateMutation.mutateAsync({
        templateId: template.id,
        data: {
          title: `Report based on ${template.name}`,
          type: template.type,
        }
      })
      setShowPreview(false)
    } catch (error) {
      console.error('Failed to create report from template:', error)
    }
  }, [createFromTemplateMutation])

  const handleEditTemplate = useCallback((template: ReportTemplate) => {
    setEditingTemplate(template)
    setShowEditModal(true)
  }, [])

  const handleSaveTemplate = useCallback(async (templateData: Partial<ReportTemplate>) => {
    if (!editingTemplate) return

    try {
      await saveAsTemplateMutation.mutateAsync({
        reportId: editingTemplate.id,
        name: templateData.name || editingTemplate.name,
        description: templateData.description || editingTemplate.description,
        isPublic: templateData.isPublic || false,
      })
      setShowEditModal(false)
      setEditingTemplate(null)
    } catch (error) {
      console.error('Failed to save template:', error)
    }
  }, [editingTemplate, saveAsTemplateMutation])

  const handleCreateCustom = useCallback(() => {
    if (onCreateCustom) {
      onCreateCustom()
    } else {
      setShowCreateModal(true)
    }
  }, [onCreateCustom])

  if (isLoading) {
    return (
      <Container>
        <Flex justify="center" align="center" style={{ height: '200px' }}>
          <Spinner size="lg" />
        </Flex>
      </Container>
    )
  }

  if (error) {
    return (
      <Container>
        <Card>
          <CardBody>
            <Text color="red">Error loading templates: {error.message}</Text>
          </CardBody>
        </Card>
      </Container>
    )
  }

  return (
    <Container>
      {/* Header */}
      <Flex justify="between" align="center" mb="lg">
        <div>
          <Heading level={2}>Report Templates</Heading>
          <Text color="gray" size="sm">
            Choose from pre-built templates or create your own
          </Text>
        </div>
        {showCreateButton && (
          <Button onClick={handleCreateCustom} variant="primary">
            Create Custom Template
          </Button>
        )}
      </Flex>

      {/* Filters and Search */}
      <Card mb="lg">
        <CardBody>
          <Grid columns={4} gap="md">
            <GridItem>
              <Input
                placeholder="Search templates..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                leftIcon="search"
              />
            </GridItem>
            <GridItem>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px' }}
              >
                <option value="name">Sort by Name</option>
                <option value="rating">Sort by Rating</option>
                <option value="usage">Sort by Usage</option>
                <option value="created">Sort by Created</option>
              </select>
            </GridItem>
            <GridItem>
              <select
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value as any)}
                style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px' }}
              >
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
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

      {/* Templates Grid/List */}
      {viewMode === 'grid' ? (
        <Grid columns={3} gap="lg">
          {filteredTemplates.map((template) => (
            <GridItem key={template.id}>
              <TemplateCard
                template={template}
                onSelect={() => handleSelectTemplate(template)}
                onEdit={showEditButton ? () => handleEditTemplate(template) : undefined}
              />
            </GridItem>
          ))}
        </Grid>
      ) : (
        <div>
          {filteredTemplates.map((template) => (
            <TemplateListItem
              key={template.id}
              template={template}
              onSelect={() => handleSelectTemplate(template)}
              onEdit={showEditButton ? () => handleEditTemplate(template) : undefined}
            />
          ))}
        </div>
      )}

      {/* Template Preview Modal */}
      {showPreview && selectedTemplate && (
        <TemplatePreviewModal
          template={selectedTemplate}
          onClose={() => setShowPreview(false)}
          onCreateReport={() => handleCreateFromTemplate(selectedTemplate)}
          isCreating={createFromTemplateMutation.isPending}
        />
      )}

      {/* Create Custom Template Modal */}
      {showCreateModal && (
        <CreateTemplateModal
          onClose={() => setShowCreateModal(false)}
          onSave={handleSaveTemplate}
        />
      )}

      {/* Edit Template Modal */}
      {showEditModal && editingTemplate && (
        <EditTemplateModal
          template={editingTemplate}
          onClose={() => setShowEditModal(false)}
          onSave={handleSaveTemplate}
        />
      )}
    </Container>
  )
}

// Template Card Component
interface TemplateCardProps {
  template: ReportTemplate
  onSelect: () => void
  onEdit?: () => void
}

const TemplateCard: React.FC<TemplateCardProps> = ({ template, onSelect, onEdit }) => {
  return (
    <Card hoverable onClick={onSelect} style={{ cursor: 'pointer', height: '100%' }}>
      <CardHeader>
        <Flex justify="between" align="start">
          <div>
            <Heading level={4} mb="xs">{template.name}</Heading>
            <Text color="gray" size="sm">{template.description}</Text>
          </div>
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
      </CardHeader>
      <CardBody>
        <Flex direction="column" gap="sm">
          <Flex gap="sm" wrap>
            <Badge variant="secondary">{template.type}</Badge>
            <Badge variant="outline">{template.category}</Badge>
            {template.isPublic && <Badge variant="success">Public</Badge>}
            {template.isDefault && <Badge variant="primary">Default</Badge>}
          </Flex>
          
          <Flex justify="between" align="center">
            <Text size="sm" color="gray">
              {template.sections.length} sections, {template.charts.length} charts
            </Text>
            <Flex align="center" gap="xs">
              <span>⭐</span>
              <Text size="sm">{template.rating.toFixed(1)}</Text>
            </Flex>
          </Flex>

          <Flex justify="between" align="center">
            <Text size="sm" color="gray">
              Used {template.usageCount} times
            </Text>
            <Text size="sm" color="gray">
              v{template.version}
            </Text>
          </Flex>

          {template.tags.length > 0 && (
            <Flex gap="xs" wrap>
              {template.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" size="sm">
                  {tag}
                </Badge>
              ))}
              {template.tags.length > 3 && (
                <Badge variant="outline" size="sm">
                  +{template.tags.length - 3}
                </Badge>
              )}
            </Flex>
          )}
        </Flex>
      </CardBody>
    </Card>
  )
}

// Template List Item Component
interface TemplateListItemProps {
  template: ReportTemplate
  onSelect: () => void
  onEdit?: () => void
}

const TemplateListItem: React.FC<TemplateListItemProps> = ({ template, onSelect, onEdit }) => {
  return (
    <Card hoverable onClick={onSelect} style={{ cursor: 'pointer', marginBottom: '16px' }}>
      <CardBody>
        <Flex justify="between" align="center">
          <Flex direction="column" gap="xs" style={{ flex: 1 }}>
            <Flex align="center" gap="md">
              <Heading level={4}>{template.name}</Heading>
              <Flex gap="sm">
                <Badge variant="secondary">{template.type}</Badge>
                <Badge variant="outline">{template.category}</Badge>
                {template.isPublic && <Badge variant="success">Public</Badge>}
                {template.isDefault && <Badge variant="primary">Default</Badge>}
              </Flex>
            </Flex>
            <Text color="gray">{template.description}</Text>
            <Flex gap="md" align="center">
              <Text size="sm" color="gray">
                {template.sections.length} sections, {template.charts.length} charts, {template.tables.length} tables
              </Text>
              <Flex align="center" gap="xs">
                <span>⭐</span>
                <Text size="sm">{template.rating.toFixed(1)}</Text>
              </Flex>
              <Text size="sm" color="gray">
                Used {template.usageCount} times
              </Text>
              <Text size="sm" color="gray">
                v{template.version}
              </Text>
            </Flex>
            {template.tags.length > 0 && (
              <Flex gap="xs" wrap>
                {template.tags.map((tag) => (
                  <Badge key={tag} variant="outline" size="sm">
                    {tag}
                  </Badge>
                ))}
              </Flex>
            )}
          </Flex>
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
      </CardBody>
    </Card>
  )
}

// Template Preview Modal
interface TemplatePreviewModalProps {
  template: ReportTemplate
  onClose: () => void
  onCreateReport: () => void
  isCreating: boolean
}

const TemplatePreviewModal: React.FC<TemplatePreviewModalProps> = ({
  template,
  onClose,
  onCreateReport,
  isCreating,
}) => {
  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={`Preview: ${template.name}`}
      size="xl"
    >
      <div style={{ maxHeight: '70vh', overflow: 'auto' }}>
        {/* Template Info */}
        <Card mb="lg">
          <CardBody>
            <Grid columns={2} gap="lg">
              <GridItem>
                <Heading level={4} mb="sm">Template Details</Heading>
                <Flex direction="column" gap="xs">
                  <Text><strong>Type:</strong> {template.type}</Text>
                  <Text><strong>Category:</strong> {template.category}</Text>
                  <Text><strong>Version:</strong> {template.version}</Text>
                  <Text><strong>Author:</strong> {template.author}</Text>
                  <Text><strong>Rating:</strong> ⭐ {template.rating.toFixed(1)}</Text>
                  <Text><strong>Usage:</strong> {template.usageCount} times</Text>
                </Flex>
              </GridItem>
              <GridItem>
                <Heading level={4} mb="sm">Description</Heading>
                <Text>{template.description}</Text>
                {template.tags.length > 0 && (
                  <div style={{ marginTop: '12px' }}>
                    <Text size="sm" color="gray" mb="xs">Tags:</Text>
                    <Flex gap="xs" wrap>
                      {template.tags.map((tag) => (
                        <Badge key={tag} variant="outline" size="sm">
                          {tag}
                        </Badge>
                      ))}
                    </Flex>
                  </div>
                )}
              </GridItem>
            </Grid>
          </CardBody>
        </Card>

        {/* Sections Preview */}
        <Card mb="lg">
          <CardHeader>
            <Heading level={4}>Sections ({template.sections.length})</Heading>
          </CardHeader>
          <CardBody>
            <div>
              {template.sections.map((section, index) => (
                <div key={section.id} style={{ 
                  padding: '12px', 
                  border: '1px solid #e5e7eb', 
                  borderRadius: '4px',
                  marginBottom: '8px',
                  backgroundColor: section.required ? '#f9fafb' : '#ffffff'
                }}>
                  <Flex justify="between" align="center">
                    <div>
                      <Text weight="medium">{index + 1}. {section.title}</Text>
                      <Text size="sm" color="gray">{section.type}</Text>
                    </div>
                    {section.required && (
                      <Badge variant="warning" size="sm">Required</Badge>
                    )}
                  </Flex>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Charts Preview */}
        {template.charts.length > 0 && (
          <Card mb="lg">
            <CardHeader>
              <Heading level={4}>Charts ({template.charts.length})</Heading>
            </CardHeader>
            <CardBody>
              <div>
                {template.charts.map((chart, index) => (
                  <div key={chart.id} style={{ 
                    padding: '12px', 
                    border: '1px solid #e5e7eb', 
                    borderRadius: '4px',
                    marginBottom: '8px'
                  }}>
                    <Flex justify="between" align="center">
                      <div>
                        <Text weight="medium">{index + 1}. {chart.title}</Text>
                        <Text size="sm" color="gray">{chart.type} chart</Text>
                      </div>
                      {chart.required && (
                        <Badge variant="warning" size="sm">Required</Badge>
                      )}
                    </Flex>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}

        {/* Tables Preview */}
        {template.tables.length > 0 && (
          <Card mb="lg">
            <CardHeader>
              <Heading level={4}>Tables ({template.tables.length})</Heading>
            </CardHeader>
            <CardBody>
              <div>
                {template.tables.map((table, index) => (
                  <div key={table.id} style={{ 
                    padding: '12px', 
                    border: '1px solid #e5e7eb', 
                    borderRadius: '4px',
                    marginBottom: '8px'
                  }}>
                    <Flex justify="between" align="center">
                      <div>
                        <Text weight="medium">{index + 1}. {table.title}</Text>
                        <Text size="sm" color="gray">Data table</Text>
                      </div>
                      {table.required && (
                        <Badge variant="warning" size="sm">Required</Badge>
                      )}
                    </Flex>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}

        {/* Parameters Preview */}
        {template.parameters.length > 0 && (
          <Card mb="lg">
            <CardHeader>
              <Heading level={4}>Parameters ({template.parameters.length})</Heading>
            </CardHeader>
            <CardBody>
              <div>
                {template.parameters.map((param, index) => (
                  <div key={param.id} style={{ 
                    padding: '12px', 
                    border: '1px solid #e5e7eb', 
                    borderRadius: '4px',
                    marginBottom: '8px'
                  }}>
                    <Flex justify="between" align="center">
                      <div>
                        <Text weight="medium">{param.label}</Text>
                        <Text size="sm" color="gray">{param.type} - {param.description}</Text>
                      </div>
                      {param.required && (
                        <Badge variant="error" size="sm">Required</Badge>
                      )}
                    </Flex>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}
      </div>

      {/* Modal Actions */}
      <Flex justify="end" gap="md" style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
        <Button variant="outline" onClick={onClose}>
          Close
        </Button>
        <Button 
          variant="primary" 
          onClick={onCreateReport}
          disabled={isCreating}
        >
          {isCreating ? <Spinner size="sm" /> : 'Create Report'}
        </Button>
      </Flex>
    </Modal>
  )
}

// Create Template Modal
interface CreateTemplateModalProps {
  onClose: () => void
  onSave: (data: Partial<ReportTemplate>) => void
}

const CreateTemplateModal: React.FC<CreateTemplateModalProps> = ({ onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'custom' as const,
    category: 'equity' as const,
    isPublic: false,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <Modal isOpen={true} onClose={onClose} title="Create Custom Template" size="md">
      <form onSubmit={handleSubmit}>
        <div style={{ padding: '16px' }}>
          <Flex direction="column" gap="md">
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Template Name *
              </label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter template name"
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
                placeholder="Enter template description"
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

            <Grid columns={2} gap="md">
              <GridItem>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                  Type
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                  style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px' }}
                >
                  <option value="full">Full Analysis</option>
                  <option value="valuation">Valuation</option>
                  <option value="risk">Risk Analysis</option>
                  <option value="technical">Technical Analysis</option>
                  <option value="custom">Custom</option>
                </select>
              </GridItem>
              <GridItem>
                <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                  Category
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value as any })}
                  style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px' }}
                >
                  <option value="equity">Equity</option>
                  <option value="portfolio">Portfolio</option>
                  <option value="market">Market</option>
                  <option value="sector">Sector</option>
                </select>
              </GridItem>
            </Grid>

            <div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={formData.isPublic}
                  onChange={(e) => setFormData({ ...formData, isPublic: e.target.checked })}
                />
                <span>Make this template public</span>
              </label>
            </div>
          </Flex>
        </div>

        <Flex justify="end" gap="md" style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Create Template
          </Button>
        </Flex>
      </form>
    </Modal>
  )
}

// Edit Template Modal
interface EditTemplateModalProps {
  template: ReportTemplate
  onClose: () => void
  onSave: (data: Partial<ReportTemplate>) => void
}

const EditTemplateModal: React.FC<EditTemplateModalProps> = ({ template, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: template.name,
    description: template.description,
    isPublic: template.isPublic,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <Modal isOpen={true} onClose={onClose} title="Edit Template" size="md">
      <form onSubmit={handleSubmit}>
        <div style={{ padding: '16px' }}>
          <Flex direction="column" gap="md">
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                Template Name *
              </label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter template name"
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
                placeholder="Enter template description"
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

            <div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={formData.isPublic}
                  onChange={(e) => setFormData({ ...formData, isPublic: e.target.checked })}
                />
                <span>Make this template public</span>
              </label>
            </div>
          </Flex>
        </div>

        <Flex justify="end" gap="md" style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Save Changes
          </Button>
        </Flex>
      </form>
    </Modal>
  )
}

export default ReportTemplates
