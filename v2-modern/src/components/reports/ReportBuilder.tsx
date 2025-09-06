import React, { useState, useCallback, useMemo } from 'react'
import { 
  DocumentTextIcon, 
  ChartBarIcon, 
  TableCellsIcon,
  TrashIcon,
  EyeIcon,
  Cog6ToothIcon,
  CheckIcon
} from '@heroicons/react/24/outline'
import { 
  Button, 
  Input, 
  Card, 
  Badge, 
  Modal, 
  Spinner, 
  ErrorDisplay, 
  Heading, 
  Text,
  useAccessibility
} from '../ui'
import { clsx } from 'clsx'

interface ReportSection {
  id: string
  title: string
  type: 'text' | 'chart' | 'table' | 'metric'
  content: any
  order: number
  visible: boolean
}

interface ReportBuilderProps {
  initialReport?: any
  onClose: () => void
  onSave?: (report: any) => void
}

const ReportBuilder: React.FC<ReportBuilderProps> = ({
  initialReport,
  onClose,
  onSave
}) => {
  const { reducedMotion } = useAccessibility()
  
  const [report, setReport] = useState({
    title: initialReport?.title || '',
    description: initialReport?.description || '',
    type: initialReport?.type || 'custom_analysis',
    tags: initialReport?.tags || [],
    sections: initialReport?.sections || []
  })
  
  const [activeSection, setActiveSection] = useState<ReportSection | null>(null)
  const [showSectionModal, setShowSectionModal] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sectionTypes = useMemo(() => [
    { id: 'text', label: 'Text', icon: DocumentTextIcon },
    { id: 'chart', label: 'Chart', icon: ChartBarIcon },
    { id: 'table', label: 'Table', icon: TableCellsIcon },
    { id: 'metric', label: 'Metrics', icon: DocumentTextIcon }
  ], [])

  const handleAddSection = useCallback((type: string) => {
    const newSection: ReportSection = {
      id: `section_${Date.now()}`,
      title: `New ${type} Section`,
      type: type as any,
      content: getDefaultContent(type),
      order: report.sections.length,
      visible: true
    }
    
    setReport(prev => ({
      ...prev,
      sections: [...prev.sections, newSection]
    }))
    
    setActiveSection(newSection)
    setShowSectionModal(true)
  }, [report.sections.length])

  const handleEditSection = useCallback((section: ReportSection) => {
    setActiveSection(section)
    setShowSectionModal(true)
  }, [])

  const handleDeleteSection = useCallback((sectionId: string) => {
    setReport(prev => ({
      ...prev,
      sections: prev.sections.filter((s: ReportSection) => s.id !== sectionId)
    }))
  }, [])

  const handleUpdateSection = useCallback((updatedSection: ReportSection) => {
    setReport(prev => ({
      ...prev,
      sections: prev.sections.map((s: ReportSection) => 
        s.id === updatedSection.id ? updatedSection : s
      )
    }))
    setShowSectionModal(false)
    setActiveSection(null)
  }, [])

  const handleSave = async () => {
    try {
      setIsSaving(true)
      setError(null)
      // Save logic here
      onSave?.(report)
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save report')
    } finally {
      setIsSaving(false)
    }
  }

  const getDefaultContent = useCallback((type: string) => {
    switch (type) {
      case 'text':
        return { content: 'Enter your text content here...' }
      case 'chart':
        return { chartType: 'line', dataSource: '', title: 'Chart Title' }
      case 'table':
        return {
          columns: [
            { key: 'column1', title: 'Column 1' },
            { key: 'column2', title: 'Column 2' }
          ],
          data: [{ column1: 'Value 1', column2: 'Value 2' }]
        }
      case 'metric':
        return { metrics: [{ name: 'Metric 1', value: 0, change: 0 }] }
      default:
        return {}
    }
  }, [])

  const renderSectionPreview = useCallback((section: ReportSection) => {
    const baseClasses = "p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg"
    const titleClasses = "font-medium text-neutral-900 dark:text-neutral-100 mb-2"
    const textClasses = "text-neutral-600 dark:text-neutral-400 text-sm"
    
    switch (section.type) {
      case 'text':
        return (
          <div className={baseClasses}>
            <Heading level={4} size="sm" className={titleClasses}>{section.title}</Heading>
            <Text size="sm" color="neutral" className={textClasses}>
              {section.content.content || 'No content'}
            </Text>
          </div>
        )
      case 'chart':
        return (
          <div className={baseClasses}>
            <Heading level={4} size="sm" className={titleClasses}>{section.title}</Heading>
            <div className="h-32 bg-neutral-200 dark:bg-neutral-700 rounded flex items-center justify-center">
              <ChartBarIcon className="w-8 h-8 text-neutral-400 dark:text-neutral-500" />
              <Text size="sm" color="neutral" className="ml-2">Chart Preview</Text>
            </div>
          </div>
        )
      case 'table':
        return (
          <div className={baseClasses}>
            <Heading level={4} size="sm" className={titleClasses}>{section.title}</Heading>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-200 dark:border-neutral-700">
                    {section.content.columns?.map((col: any, index: number) => (
                      <th key={index} className="text-left py-2 px-3 font-medium text-neutral-700 dark:text-neutral-300">
                        {col.title}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {section.content.data?.slice(0, 3).map((row: any, index: number) => (
                    <tr key={index} className="border-b border-neutral-200 dark:border-neutral-700">
                      {section.content.columns?.map((col: any, colIndex: number) => (
                        <td key={colIndex} className="py-2 px-3 text-neutral-600 dark:text-neutral-400">
                          {row[col.key]}
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
          <div className={baseClasses}>
            <Heading level={4} size="sm" className={titleClasses}>{section.title}</Heading>
            <div className="grid grid-cols-2 gap-4">
              {section.content.metrics?.map((metric: any, index: number) => (
                <div key={index} className="text-center">
                  <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">{metric.value}</div>
                  <Text size="sm" color="neutral">{metric.name}</Text>
                </div>
              ))}
            </div>
          </div>
        )
      default:
        return (
          <div className={baseClasses}>
            <Text size="sm" color="neutral">Unknown section type</Text>
          </div>
        )
    }
  }, [])

  return (
    <div className={clsx(
      "space-y-6",
      reducedMotion ? "" : "transition-all duration-200"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Heading level={2} size="xl" color="neutral">
            {initialReport ? 'Edit Report' : 'Create New Report'}
          </Heading>
          <Text size="sm" color="neutral" className="mt-1">
            Build your report with sections
          </Text>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setShowPreview(!showPreview)}
            className="flex items-center gap-2"
            aria-label={showPreview ? 'Hide preview' : 'Show preview'}
          >
            <EyeIcon className="w-4 h-4" />
            {showPreview ? 'Hide Preview' : 'Preview'}
          </Button>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={isSaving || !report.title.trim()}
            className="flex items-center gap-2"
            aria-label={initialReport ? 'Update report' : 'Save report'}
          >
            {isSaving ? <Spinner size="sm" /> : <CheckIcon className="w-4 h-4" />}
            {initialReport ? 'Update' : 'Save'} Report
          </Button>
        </div>
      </div>

      {error && <ErrorDisplay error={error} />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Builder Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Report Details */}
          <Card className="p-6">
            <Heading level={3} size="lg" color="neutral" className="mb-4">Report Details</Heading>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                  Title *
                </label>
                <Input
                  value={report.title}
                  onChange={(value: string) => setReport(prev => ({ ...prev, title: value }))}
                  placeholder="Enter report title"
                  aria-label="Report title"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                  Description
                </label>
                <textarea
                  value={report.description}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setReport(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Enter report description"
                  rows={3}
                  className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-800 dark:text-neutral-100"
                  aria-label="Report description"
                />
              </div>
            </div>
          </Card>

          {/* Sections */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <Heading level={3} size="lg" color="neutral">Report Sections</Heading>
              <div className="flex items-center gap-2" role="group" aria-label="Add section types">
                {sectionTypes.map((type) => (
                  <Button
                    key={type.id}
                    variant="outline"
                    size="sm"
                    onClick={() => handleAddSection(type.id)}
                    className="flex items-center gap-1"
                    aria-label={`Add ${type.label.toLowerCase()} section`}
                  >
                    <type.icon className="w-4 h-4" />
                    {type.label}
                  </Button>
                ))}
              </div>
            </div>

            {report.sections.length === 0 ? (
              <div className="text-center py-12">
                <DocumentTextIcon className="w-12 h-12 text-neutral-400 dark:text-neutral-500 mx-auto mb-4" />
                <Heading level={4} size="lg" color="neutral" className="mb-2">No sections yet</Heading>
                <Text size="sm" color="neutral" className="mb-6">Add sections to build your report</Text>
                <div className="flex justify-center gap-2" role="group" aria-label="Add first section">
                  {sectionTypes.map((type) => (
                    <Button
                      key={type.id}
                      variant="outline"
                      onClick={() => handleAddSection(type.id)}
                      className="flex items-center gap-2"
                      aria-label={`Add ${type.label.toLowerCase()} section`}
                    >
                      <type.icon className="w-4 h-4" />
                      {type.label}
                    </Button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4" role="list" aria-label="Report sections">
                {report.sections
                  .sort((a: ReportSection, b: ReportSection) => a.order - b.order)
                  .map((section: ReportSection) => (
                    <div key={section.id} className="border border-neutral-200 dark:border-neutral-700 rounded-lg" role="listitem">
                      <div className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800 rounded-t-lg">
                        <div className="flex items-center gap-3">
                          <Badge>{section.type}</Badge>
                          <Heading level={4} size="sm" color="neutral">{section.title}</Heading>
                        </div>
                        <div className="flex items-center gap-2" role="group" aria-label={`Actions for ${section.title}`}>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditSection(section)}
                            aria-label={`Edit ${section.title} section`}
                          >
                            <Cog6ToothIcon className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteSection(section.id)}
                            className="text-danger-600 hover:text-danger-700 dark:text-danger-400 dark:hover:text-danger-300"
                            aria-label={`Delete ${section.title} section`}
                          >
                            <TrashIcon className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="p-4">
                        {renderSectionPreview(section)}
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </Card>
        </div>

        {/* Preview Panel */}
        {showPreview && (
          <div className="space-y-6">
            <Card className="p-6">
              <Heading level={3} size="lg" color="neutral" className="mb-4">Preview</Heading>
              <div className="space-y-4">
                <div className="border-b border-neutral-200 dark:border-neutral-700 pb-4">
                  <Heading level={2} size="xl" color="neutral">
                    {report.title || 'Untitled Report'}
                  </Heading>
                  <Text size="sm" color="neutral" className="mt-1">
                    {report.description || 'No description'}
                  </Text>
                </div>
                
                {report.sections
                  .sort((a: ReportSection, b: ReportSection) => a.order - b.order)
                  .map((section: ReportSection) => (
                    <div key={section.id}>
                      <Heading level={3} size="lg" color="neutral" className="mb-2">{section.title}</Heading>
                      {renderSectionPreview(section)}
                    </div>
                  ))}
              </div>
            </Card>
          </div>
        )}
      </div>

      {/* Section Editor Modal */}
      {showSectionModal && activeSection && (
        <SectionEditor
          section={activeSection}
          onSave={handleUpdateSection}
          onClose={() => {
            setShowSectionModal(false)
            setActiveSection(null)
          }}
        />
      )}
    </div>
  )
}

// Section Editor Component
interface SectionEditorProps {
  section: ReportSection
  onSave: (section: ReportSection) => void
  onClose: () => void
}

const SectionEditor: React.FC<SectionEditorProps> = ({ section, onSave, onClose }) => {
  const { reducedMotion } = useAccessibility()
  const [editedSection, setEditedSection] = useState<ReportSection>({ ...section })

  const handleSave = useCallback(() => {
    onSave(editedSection)
  }, [editedSection, onSave])

  const renderEditor = useCallback(() => {
    const labelClasses = "block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2"
    const inputClasses = "w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-800 dark:text-neutral-100"
    
    switch (section.type) {
      case 'text':
        return (
          <div className="space-y-4">
            <div>
              <label className={labelClasses}>
                Content
              </label>
              <textarea
                value={editedSection.content.content || ''}
                onChange={(e) => setEditedSection(prev => ({
                  ...prev,
                  content: { ...prev.content, content: e.target.value }
                }))}
                rows={8}
                className={inputClasses}
                placeholder="Enter your text content..."
                aria-label="Section content"
              />
            </div>
          </div>
        )

      case 'chart':
        return (
          <div className="space-y-4">
            <div>
              <label className={labelClasses}>
                Chart Type
              </label>
              <select
                value={editedSection.content.chartType || 'line'}
                onChange={(e) => setEditedSection(prev => ({
                  ...prev,
                  content: { ...prev.content, chartType: e.target.value }
                }))}
                className={inputClasses}
                aria-label="Chart type"
              >
                <option value="line">Line Chart</option>
                <option value="bar">Bar Chart</option>
                <option value="pie">Pie Chart</option>
                <option value="area">Area Chart</option>
                <option value="scatter">Scatter Plot</option>
              </select>
            </div>

            <div>
              <label className={labelClasses}>
                Data Source
              </label>
              <Input
                value={editedSection.content.dataSource || ''}
                onChange={(value: string) => setEditedSection(prev => ({
                  ...prev,
                  content: { ...prev.content, dataSource: value }
                }))}
                placeholder="e.g., portfolio.performance"
                aria-label="Data source"
              />
            </div>
          </div>
        )
      
      default:
        return (
          <div className="text-center py-8">
            <Text size="sm" color="neutral">Editor for {section.type} coming soon</Text>
          </div>
        )
    }
  }, [section.type, editedSection.content])

  return (
    <Modal isOpen={true} onClose={onClose} title={`Edit ${section.type} Section`} size="lg">
      <div className={clsx(
        "space-y-6",
        reducedMotion ? "" : "transition-all duration-200"
      )}>
        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
            Section Title
          </label>
          <Input
            value={editedSection.title}
            onChange={(value: string) => setEditedSection(prev => ({ ...prev, title: value }))}
            placeholder="Enter section title"
            aria-label="Section title"
          />
        </div>

        {renderEditor()}

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave}>
            Save Section
          </Button>
        </div>
      </div>
    </Modal>
  )
}

export default ReportBuilder