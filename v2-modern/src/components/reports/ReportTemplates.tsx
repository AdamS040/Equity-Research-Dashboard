import React, { useState, useCallback, useMemo } from 'react'
import { 
  DocumentTextIcon, 
  ChartBarIcon, 
  TableCellsIcon,
  PlusIcon,
  EyeIcon,
  DocumentDuplicateIcon,
  StarIcon
} from '@heroicons/react/24/outline'
import { 
  Button, 
  Card, 
  Badge, 
  Input, 
  Spinner, 
  ErrorDisplay, 
  Heading, 
  Text,
  useAccessibility
} from '../ui'
import { clsx } from 'clsx'

interface ReportTemplate {
  id: string
  name: string
  description: string
  type: string
  category: string
  tags: string[]
  usage_count: number
  rating: number
}

interface ReportTemplatesProps {
  onSelectTemplate?: (template: ReportTemplate) => void
  onCreateCustom?: () => void
  onClose?: () => void
}

const ReportTemplates: React.FC<ReportTemplatesProps> = ({
  onSelectTemplate,
  onCreateCustom,
  onClose
}) => {
  const { reducedMotion } = useAccessibility()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Mock data
  const templates = useMemo((): ReportTemplate[] => [
    {
      id: '1',
      name: 'Portfolio Performance Report',
      description: 'Comprehensive portfolio analysis with performance metrics and charts',
      type: 'portfolio_performance',
      category: 'portfolio',
      tags: ['portfolio', 'performance', 'analysis'],
      usage_count: 1250,
      rating: 4.8
    },
    {
      id: '2',
      name: 'Risk Analysis Report',
      description: 'Detailed risk assessment with VaR and stress testing',
      type: 'risk_analysis',
      category: 'risk',
      tags: ['risk', 'var', 'stress-testing'],
      usage_count: 890,
      rating: 4.6
    },
    {
      id: '3',
      name: 'DCF Valuation Report',
      description: 'Discounted Cash Flow analysis with sensitivity analysis',
      type: 'dcf_analysis',
      category: 'valuation',
      tags: ['dcf', 'valuation', 'cash-flow'],
      usage_count: 650,
      rating: 4.7
    }
  ], [])

  const categories = useMemo(() => [
    { id: 'all', name: 'All Categories' },
    { id: 'portfolio', name: 'Portfolio' },
    { id: 'risk', name: 'Risk' },
    { id: 'valuation', name: 'Valuation' }
  ], [])

  const filteredTemplates = useMemo(() => {
    return templates.filter(template => {
      const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           template.description.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory
      return matchesSearch && matchesCategory
    })
  }, [templates, searchQuery, selectedCategory])

  const getTypeIcon = useCallback((type: string) => {
    switch (type) {
      case 'portfolio_performance': return <ChartBarIcon className="w-5 h-5" />
      case 'risk_analysis': return <DocumentTextIcon className="w-5 h-5" />
      case 'dcf_analysis': return <DocumentTextIcon className="w-5 h-5" />
      default: return <DocumentTextIcon className="w-5 h-5" />
    }
  }, [])

  const getCategoryColor = useCallback((category: string) => {
    switch (category) {
      case 'portfolio': return 'primary'
      case 'risk': return 'danger'
      case 'valuation': return 'success'
      default: return 'neutral'
    }
  }, [])

  const renderStars = useCallback((rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <StarIcon
        key={i}
        className={clsx(
          'w-4 h-4',
          i < Math.floor(rating) ? 'text-warning-400 fill-current' : 'text-neutral-300 dark:text-neutral-600'
        )}
      />
    ))
  }, [])

  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value)
  }, [])

  const handleCategoryChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCategory(e.target.value)
  }, [])

  const handleClearFilters = useCallback(() => {
    setSearchQuery('')
    setSelectedCategory('all')
  }, [])

  return (
    <div className={clsx(
      "space-y-6",
      reducedMotion ? "" : "transition-all duration-200"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Heading level={2} size="xl" color="neutral">Report Templates</Heading>
          <Text size="sm" color="neutral" className="mt-1">Choose from pre-built templates or create your own</Text>
        </div>
        <div className="flex items-center gap-2" role="group" aria-label="Template actions">
          <Button 
            variant="outline" 
            onClick={onCreateCustom}
            aria-label="Create custom template"
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            Create Custom
          </Button>
          {onClose && (
            <Button 
              variant="outline" 
              onClick={onClose}
              aria-label="Close templates"
            >
              Close
            </Button>
          )}
        </div>
      </div>

      {/* Filters */}
      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Search Templates
            </label>
            <Input
              placeholder="Search by name or description..."
              value={searchQuery}
              onChange={handleSearchChange}
              aria-label="Search templates"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Category
            </label>
            <select
              value={selectedCategory}
              onChange={handleCategoryChange}
              className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-800 dark:text-neutral-100"
              aria-label="Filter by category"
            >
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <Button
              variant="outline"
              onClick={handleClearFilters}
              className="w-full"
              aria-label="Clear all filters"
            >
              Clear Filters
            </Button>
          </div>
        </div>
      </Card>

      {/* Results */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : error ? (
        <ErrorDisplay error={error} />
      ) : filteredTemplates.length === 0 ? (
        <Card className="p-12 text-center">
          <DocumentTextIcon className="w-12 h-12 text-neutral-400 dark:text-neutral-500 mx-auto mb-4" />
          <Heading level={3} size="lg" color="neutral" className="mb-2">No templates found</Heading>
          <Text size="sm" color="neutral" className="mb-6">
            Try adjusting your search criteria or create a custom template
          </Text>
          <Button onClick={onCreateCustom} aria-label="Create custom template">
            <PlusIcon className="w-5 h-5 mr-2" />
            Create Custom Template
          </Button>
        </Card>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-4">
            <Text size="sm" color="neutral">
              Showing {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''}
            </Text>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" role="list" aria-label="Report templates">
            {filteredTemplates.map((template) => (
              <Card 
                key={template.id} 
                className={clsx(
                  "p-6 cursor-pointer",
                  reducedMotion ? "" : "hover:shadow-lg transition-shadow duration-200"
                )}
                role="listitem"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    {getTypeIcon(template.type)}
                    <div>
                      <Heading level={3} size="sm" color="neutral" className="font-semibold">{template.name}</Heading>
                      <Badge color={getCategoryColor(template.category)} size="sm">
                        {template.category}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    {renderStars(template.rating)}
                    <Text size="sm" color="neutral" className="ml-1">({template.rating})</Text>
                  </div>
                </div>
                
                <Text size="sm" color="neutral" className="mb-4">
                  {template.description}
                </Text>
                
                <div className="flex flex-wrap gap-1 mb-4" role="group" aria-label="Template tags">
                  {template.tags.slice(0, 3).map((tag, index) => (
                    <Badge key={index} size="sm">
                      {tag}
                    </Badge>
                  ))}
                </div>
                
                <div className="flex items-center justify-between text-sm text-neutral-500 dark:text-neutral-400 mb-4">
                  <span>Used {template.usage_count} times</span>
                </div>
                
                <div className="flex gap-2" role="group" aria-label={`Actions for ${template.name}`}>
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => onSelectTemplate?.(template)}
                    aria-label={`Use ${template.name} template`}
                  >
                    <DocumentDuplicateIcon className="w-4 h-4 mr-1" />
                    Use Template
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {/* Preview logic */}}
                    aria-label={`Preview ${template.name} template`}
                  >
                    <EyeIcon className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ReportTemplates