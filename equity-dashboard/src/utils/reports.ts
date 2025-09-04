/**
 * Report Utilities
 * 
 * Utility functions for report processing, validation, and formatting
 */

import {
  ReportTemplate,
  ReportBuilder,
  ReportSection,
  ReportChart,
  ReportTable,
  ValidationResult,
  ValidationError,
  ValidationWarning,
  ReportContent,
  ReportSummary,
  Citation,
  ChartConfig,
  TableConfig,
  ExportOptions,
  ReportSearchFilters,
  ReportSearchResult,
  SearchFacets,
  SavedReport,
  ReportVersion,
  ReportComment,
  Annotation,
  Bookmark,
  Highlight,
  Note,
  DragItem,
  DropResult,
} from '../types/reports'

// Template Management Utilities
export const templateUtils = {
  /**
   * Create a new report template
   */
  createTemplate: (data: Partial<ReportTemplate>): ReportTemplate => {
    return {
      id: generateId(),
      name: data.name || 'New Template',
      type: data.type || 'custom',
      description: data.description || '',
      category: data.category || 'equity',
      sections: data.sections || [],
      charts: data.charts || [],
      tables: data.tables || [],
      parameters: data.parameters || [],
      isPublic: data.isPublic || false,
      isDefault: data.isDefault || false,
      version: data.version || '1.0.0',
      author: data.author || '',
      tags: data.tags || [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      usageCount: 0,
      rating: 0,
    }
  },

  /**
   * Clone a template with modifications
   */
  cloneTemplate: (template: ReportTemplate, modifications: Partial<ReportTemplate>): ReportTemplate => {
    return {
      ...template,
      ...modifications,
      id: generateId(),
      name: modifications.name || `${template.name} (Copy)`,
      version: '1.0.0',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      usageCount: 0,
    }
  },

  /**
   * Validate template structure
   */
  validateTemplate: (template: ReportTemplate): ValidationResult => {
    const errors: ValidationError[] = []
    const warnings: ValidationWarning[] = []

    if (!template.name.trim()) {
      errors.push({
        field: 'name',
        message: 'Template name is required',
        code: 'REQUIRED_FIELD',
        severity: 'error',
      })
    }

    if (!template.description.trim()) {
      warnings.push({
        field: 'description',
        message: 'Template description is recommended',
        code: 'MISSING_DESCRIPTION',
        suggestion: 'Add a description to help users understand the template purpose',
      })
    }

    if (template.sections.length === 0) {
      errors.push({
        field: 'sections',
        message: 'Template must have at least one section',
        code: 'NO_SECTIONS',
        severity: 'error',
      })
    }

    // Validate sections
    template.sections.forEach((section, index) => {
      if (!section.title.trim()) {
        errors.push({
          field: `sections[${index}].title`,
          message: 'Section title is required',
          code: 'REQUIRED_FIELD',
          severity: 'error',
        })
      }
    })

    // Validate parameters
    template.parameters.forEach((param, index) => {
      if (!param.name.trim()) {
        errors.push({
          field: `parameters[${index}].name`,
          message: 'Parameter name is required',
          code: 'REQUIRED_FIELD',
          severity: 'error',
        })
      }
    })

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    }
  },

  /**
   * Get default templates
   */
  getDefaultTemplates: (): ReportTemplate[] => {
    return [
      {
        id: 'full-analysis',
        name: 'Full Equity Analysis',
        type: 'full',
        description: 'Comprehensive equity research report with all major sections',
        category: 'equity',
        sections: [
          {
            id: 'executive-summary',
            title: 'Executive Summary',
            type: 'executive_summary',
            order: 1,
            required: true,
            config: {},
          },
          {
            id: 'company-overview',
            title: 'Company Overview',
            type: 'text',
            order: 2,
            required: true,
            config: {},
          },
          {
            id: 'financial-analysis',
            title: 'Financial Analysis',
            type: 'analysis',
            order: 3,
            required: true,
            config: {},
          },
          {
            id: 'valuation',
            title: 'Valuation',
            type: 'valuation',
            order: 4,
            required: true,
            config: {},
          },
          {
            id: 'risk-assessment',
            title: 'Risk Assessment',
            type: 'risk_assessment',
            order: 5,
            required: true,
            config: {},
          },
          {
            id: 'technical-analysis',
            title: 'Technical Analysis',
            type: 'technical_analysis',
            order: 6,
            required: false,
            config: {},
          },
          {
            id: 'peer-comparison',
            title: 'Peer Comparison',
            type: 'peer_comparison',
            order: 7,
            required: false,
            config: {},
          },
        ],
        charts: [
          {
            id: 'price-chart',
            title: 'Price Chart',
            type: 'candlestick',
            dataSource: 'price_data',
            config: {},
            order: 1,
            required: true,
          },
          {
            id: 'financial-metrics',
            title: 'Financial Metrics',
            type: 'bar',
            dataSource: 'financial_data',
            config: {},
            order: 2,
            required: true,
          },
        ],
        tables: [
          {
            id: 'financial-statements',
            title: 'Financial Statements',
            dataSource: 'financial_statements',
            columns: [],
            config: {},
            order: 1,
            required: true,
          },
        ],
        parameters: [
          {
            id: 'symbol',
            name: 'symbol',
            type: 'symbol',
            label: 'Stock Symbol',
            description: 'The stock symbol to analyze',
            required: true,
          },
          {
            id: 'timeframe',
            name: 'timeframe',
            type: 'select',
            label: 'Analysis Timeframe',
            description: 'The time period for analysis',
            required: true,
            options: [
              { value: '1y', label: '1 Year' },
              { value: '2y', label: '2 Years' },
              { value: '5y', label: '5 Years' },
            ],
            defaultValue: '1y',
          },
        ],
        isPublic: true,
        isDefault: true,
        version: '1.0.0',
        author: 'System',
        tags: ['equity', 'analysis', 'comprehensive'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        usageCount: 0,
        rating: 4.5,
      },
      {
        id: 'valuation-only',
        name: 'Valuation Analysis',
        type: 'valuation',
        description: 'Focused valuation analysis with DCF and comparable methods',
        category: 'equity',
        sections: [
          {
            id: 'executive-summary',
            title: 'Executive Summary',
            type: 'executive_summary',
            order: 1,
            required: true,
            config: {},
          },
          {
            id: 'valuation',
            title: 'Valuation Analysis',
            type: 'valuation',
            order: 2,
            required: true,
            config: {},
          },
          {
            id: 'peer-comparison',
            title: 'Peer Comparison',
            type: 'peer_comparison',
            order: 3,
            required: true,
            config: {},
          },
        ],
        charts: [
          {
            id: 'dcf-model',
            title: 'DCF Model',
            type: 'line',
            dataSource: 'dcf_data',
            config: {},
            order: 1,
            required: true,
          },
        ],
        tables: [
          {
            id: 'valuation-metrics',
            title: 'Valuation Metrics',
            dataSource: 'valuation_metrics',
            columns: [],
            config: {},
            order: 1,
            required: true,
          },
        ],
        parameters: [
          {
            id: 'symbol',
            name: 'symbol',
            type: 'symbol',
            label: 'Stock Symbol',
            description: 'The stock symbol to analyze',
            required: true,
          },
        ],
        isPublic: true,
        isDefault: true,
        version: '1.0.0',
        author: 'System',
        tags: ['valuation', 'dcf', 'comparable'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        usageCount: 0,
        rating: 4.2,
      },
    ]
  },
}

// Report Builder Utilities
export const builderUtils = {
  /**
   * Create a new report builder
   */
  createBuilder: (template?: ReportTemplate): ReportBuilder => {
    const builder: ReportBuilder = {
      id: generateId(),
      name: 'New Report',
      template: template?.id,
      sections: [],
      charts: [],
      tables: [],
      parameters: {},
      metadata: {
        author: '',
        version: '1.0.0',
        tags: [],
        language: 'en',
        format: 'pdf',
        generatedAt: new Date().toISOString(),
        dataAsOf: new Date().toISOString(),
        sources: [],
        methodology: '',
        assumptions: [],
        disclaimers: [],
        compliance: {
          regulatory: [],
          disclosures: [],
          conflicts: [],
          certifications: [],
        },
      },
      status: 'draft',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    if (template) {
      builder.sections = template.sections.map(sectionTemplate => ({
        id: generateId(),
        templateId: sectionTemplate.id,
        title: sectionTemplate.title,
        type: sectionTemplate.type,
        content: sectionTemplate.content || '',
        order: sectionTemplate.order,
        config: sectionTemplate.config,
        isCollapsed: false,
        isValid: true,
        errors: [],
        warnings: [],
      }))

      builder.charts = template.charts.map(chartTemplate => ({
        id: generateId(),
        templateId: chartTemplate.id,
        title: chartTemplate.title,
        type: chartTemplate.type,
        dataSource: chartTemplate.dataSource,
        data: null,
        config: chartTemplate.config,
        order: chartTemplate.order,
        isVisible: true,
        isValid: false,
        errors: ['Data not loaded'],
      }))

      builder.tables = template.tables.map(tableTemplate => ({
        id: generateId(),
        templateId: tableTemplate.id,
        title: tableTemplate.title,
        dataSource: tableTemplate.dataSource,
        headers: [],
        rows: [],
        config: tableTemplate.config,
        order: tableTemplate.order,
        isVisible: true,
        isValid: false,
        errors: ['Data not loaded'],
      }))
    }

    return builder
  },

  /**
   * Add a new section to the builder
   */
  addSection: (builder: ReportBuilder, section: Omit<ReportSection, 'id'>): ReportBuilder => {
    const newSection: ReportSection = {
      ...section,
      id: generateId(),
    }

    return {
      ...builder,
      sections: [...builder.sections, newSection].sort((a, b) => a.order - b.order),
      updatedAt: new Date().toISOString(),
    }
  },

  /**
   * Update a section in the builder
   */
  updateSection: (builder: ReportBuilder, sectionId: string, updates: Partial<ReportSection>): ReportBuilder => {
    return {
      ...builder,
      sections: builder.sections.map(section =>
        section.id === sectionId ? { ...section, ...updates } : section
      ),
      updatedAt: new Date().toISOString(),
    }
  },

  /**
   * Remove a section from the builder
   */
  removeSection: (builder: ReportBuilder, sectionId: string): ReportBuilder => {
    return {
      ...builder,
      sections: builder.sections.filter(section => section.id !== sectionId),
      updatedAt: new Date().toISOString(),
    }
  },

  /**
   * Reorder sections in the builder
   */
  reorderSections: (builder: ReportBuilder, sectionIds: string[]): ReportBuilder => {
    const sectionMap = new Map(builder.sections.map(s => [s.id, s]))
    const reorderedSections = sectionIds
      .map((id, index) => {
        const section = sectionMap.get(id)
        return section ? { ...section, order: index + 1 } : null
      })
      .filter(Boolean) as ReportSection[]

    return {
      ...builder,
      sections: reorderedSections,
      updatedAt: new Date().toISOString(),
    }
  },

  /**
   * Validate the entire builder
   */
  validateBuilder: (builder: ReportBuilder): ValidationResult => {
    const errors: ValidationError[] = []
    const warnings: ValidationWarning[] = []

    if (!builder.name.trim()) {
      errors.push({
        field: 'name',
        message: 'Report name is required',
        code: 'REQUIRED_FIELD',
        severity: 'error',
      })
    }

    if (builder.sections.length === 0) {
      errors.push({
        field: 'sections',
        message: 'Report must have at least one section',
        code: 'NO_SECTIONS',
        severity: 'error',
      })
    }

    // Validate sections
    builder.sections.forEach((section, index) => {
      if (!section.title.trim()) {
        errors.push({
          field: `sections[${index}].title`,
          message: 'Section title is required',
          code: 'REQUIRED_FIELD',
          severity: 'error',
        })
      }

      if (section.type === 'text' && !section.content.trim()) {
        warnings.push({
          field: `sections[${index}].content`,
          message: 'Text section is empty',
          code: 'EMPTY_CONTENT',
          suggestion: 'Add content to this section or remove it',
        })
      }
    })

    // Validate charts
    builder.charts.forEach((chart, index) => {
      if (!chart.title.trim()) {
        errors.push({
          field: `charts[${index}].title`,
          message: 'Chart title is required',
          code: 'REQUIRED_FIELD',
          severity: 'error',
        })
      }

      if (!chart.data) {
        warnings.push({
          field: `charts[${index}].data`,
          message: 'Chart has no data',
          code: 'NO_DATA',
          suggestion: 'Generate data for this chart or remove it',
        })
      }
    })

    // Validate tables
    builder.tables.forEach((table, index) => {
      if (!table.title.trim()) {
        errors.push({
          field: `tables[${index}].title`,
          message: 'Table title is required',
          code: 'REQUIRED_FIELD',
          severity: 'error',
        })
      }

      if (table.rows.length === 0) {
        warnings.push({
          field: `tables[${index}].rows`,
          message: 'Table has no data',
          code: 'NO_DATA',
          suggestion: 'Generate data for this table or remove it',
        })
      }
    })

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    }
  },
}

// Content Generation Utilities
export const contentUtils = {
  /**
   * Generate executive summary
   */
  generateExecutiveSummary: (data: any): string => {
    // This would typically call an AI service or use predefined templates
    return `Based on our analysis of ${data.symbol}, we recommend a ${data.rating} rating with a target price of $${data.targetPrice}. The company shows strong fundamentals with ${data.keyStrengths.join(', ')}. Key risks include ${data.keyRisks.join(', ')}.`
  },

  /**
   * Generate key findings
   */
  generateKeyFindings: (data: any): string[] => {
    return [
      `Revenue growth of ${data.revenueGrowth}% year-over-year`,
      `Operating margin improved to ${data.operatingMargin}%`,
      `Debt-to-equity ratio of ${data.debtToEquity}`,
      `ROE of ${data.roe}% above industry average`,
    ]
  },

  /**
   * Generate recommendations
   */
  generateRecommendations: (data: any): string[] => {
    const recommendations = []
    
    if (data.rating === 'buy') {
      recommendations.push('Accumulate on weakness')
      recommendations.push('Set stop-loss at 10% below entry')
    } else if (data.rating === 'hold') {
      recommendations.push('Maintain current position')
      recommendations.push('Monitor quarterly results')
    } else {
      recommendations.push('Consider reducing position')
      recommendations.push('Wait for better entry point')
    }

    return recommendations
  },

  /**
   * Generate citations
   */
  generateCitations: (sources: string[]): Citation[] => {
    return sources.map((source, index) => ({
      id: generateId(),
      type: 'data',
      source,
      date: new Date().toISOString(),
      description: `Data source ${index + 1}`,
      section: 'Data Sources',
    }))
  },

  /**
   * Format currency
   */
  formatCurrency: (value: number, currency: string = 'USD'): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(value)
  },

  /**
   * Format percentage
   */
  formatPercentage: (value: number, decimals: number = 2): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value / 100)
  },

  /**
   * Format number
   */
  formatNumber: (value: number, decimals: number = 2): string => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value)
  },
}

// Export Utilities
export const exportUtils = {
  /**
   * Get default export options
   */
  getDefaultOptions: (): ExportOptions => {
    return {
      includeCharts: true,
      includeTables: true,
      includeData: true,
      pageSize: 'A4',
      orientation: 'portrait',
      margins: {
        top: 1,
        right: 1,
        bottom: 1,
        left: 1,
      },
      header: {
        enabled: true,
        content: 'Equity Research Report',
        fontSize: 10,
        alignment: 'center',
        includePageNumbers: true,
      },
      footer: {
        enabled: true,
        content: 'Confidential - For Internal Use Only',
        fontSize: 8,
        alignment: 'center',
        includePageNumbers: false,
      },
      branding: {
        companyName: 'Equity Research Dashboard',
        colors: {
          primary: '#2563eb',
          secondary: '#64748b',
          accent: '#f59e0b',
        },
        fonts: {
          heading: 'Arial',
          body: 'Arial',
          monospace: 'Courier New',
        },
      },
      compression: true,
    }
  },

  /**
   * Validate export options
   */
  validateExportOptions: (options: ExportOptions): ValidationResult => {
    const errors: ValidationError[] = []
    const warnings: ValidationWarning[] = []

    if (options.margins.top < 0.5 || options.margins.top > 2) {
      warnings.push({
        field: 'margins.top',
        message: 'Top margin should be between 0.5 and 2 inches',
        code: 'MARGIN_RANGE',
      })
    }

    if (options.header && options.header.fontSize < 8 || options.header.fontSize > 16) {
      warnings.push({
        field: 'header.fontSize',
        message: 'Header font size should be between 8 and 16',
        code: 'FONT_SIZE_RANGE',
      })
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    }
  },

  /**
   * Generate filename for export
   */
  generateFilename: (reportTitle: string, format: string, timestamp?: string): string => {
    const date = timestamp ? new Date(timestamp) : new Date()
    const dateStr = date.toISOString().split('T')[0]
    const cleanTitle = reportTitle.replace(/[^a-zA-Z0-9\s]/g, '').replace(/\s+/g, '_')
    return `${cleanTitle}_${dateStr}.${format}`
  },
}

// Search and Filter Utilities
export const searchUtils = {
  /**
   * Search reports
   */
  searchReports: (reports: SavedReport[], filters: ReportSearchFilters): ReportSearchResult => {
    let filteredReports = [...reports]

    // Apply text search
    if (filters.query) {
      const query = filters.query.toLowerCase()
      filteredReports = filteredReports.filter(report =>
        report.title.toLowerCase().includes(query) ||
        report.metadata.author.toLowerCase().includes(query) ||
        report.tags.some(tag => tag.toLowerCase().includes(query))
      )
    }

    // Apply type filter
    if (filters.type) {
      filteredReports = filteredReports.filter(report => report.type === filters.type)
    }

    // Apply status filter
    if (filters.status) {
      filteredReports = filteredReports.filter(report => report.status === filters.status)
    }

    // Apply author filter
    if (filters.author) {
      filteredReports = filteredReports.filter(report => report.metadata.author === filters.author)
    }

    // Apply tags filter
    if (filters.tags && filters.tags.length > 0) {
      filteredReports = filteredReports.filter(report =>
        filters.tags!.some(tag => report.tags.includes(tag))
      )
    }

    // Apply date range filter
    if (filters.dateRange) {
      const startDate = new Date(filters.dateRange.start)
      const endDate = new Date(filters.dateRange.end)
      filteredReports = filteredReports.filter(report => {
        const reportDate = new Date(report.createdAt)
        return reportDate >= startDate && reportDate <= endDate
      })
    }

    // Apply sorting
    const sortBy = filters.sortBy || 'createdAt'
    const sortOrder = filters.sortOrder || 'desc'
    
    filteredReports.sort((a, b) => {
      let aValue: any, bValue: any
      
      switch (sortBy) {
        case 'title':
          aValue = a.title.toLowerCase()
          bValue = b.title.toLowerCase()
          break
        case 'createdAt':
          aValue = new Date(a.createdAt)
          bValue = new Date(b.createdAt)
          break
        case 'updatedAt':
          aValue = new Date(a.updatedAt)
          bValue = new Date(b.updatedAt)
          break
        case 'viewCount':
          aValue = a.viewCount
          bValue = b.viewCount
          break
        case 'rating':
          aValue = a.analytics.rating || 0
          bValue = b.analytics.rating || 0
          break
        default:
          aValue = a[sortBy as keyof SavedReport]
          bValue = b[sortBy as keyof SavedReport]
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1
      return 0
    })

    // Apply pagination
    const page = filters.page || 1
    const limit = filters.limit || 20
    const startIndex = (page - 1) * limit
    const endIndex = startIndex + limit
    const paginatedReports = filteredReports.slice(startIndex, endIndex)

    // Generate facets
    const facets = generateFacets(reports, filters)

    return {
      reports: paginatedReports,
      total: filteredReports.length,
      page,
      limit,
      hasNext: endIndex < filteredReports.length,
      hasPrev: page > 1,
      facets,
    }
  },

  /**
   * Generate search facets
   */
  generateFacets: (reports: SavedReport[], filters: ReportSearchFilters): SearchFacets => {
    const facets: SearchFacets = {
      types: {},
      statuses: {},
      authors: {},
      tags: {},
      dateRanges: {},
    }

    reports.forEach(report => {
      // Count types
      facets.types[report.type] = (facets.types[report.type] || 0) + 1
      
      // Count statuses
      facets.statuses[report.status] = (facets.statuses[report.status] || 0) + 1
      
      // Count authors
      facets.authors[report.metadata.author] = (facets.authors[report.metadata.author] || 0) + 1
      
      // Count tags
      report.tags.forEach(tag => {
        facets.tags[tag] = (facets.tags[tag] || 0) + 1
      })
      
      // Count date ranges
      const date = new Date(report.createdAt)
      const month = date.toISOString().substring(0, 7) // YYYY-MM
      facets.dateRanges[month] = (facets.dateRanges[month] || 0) + 1
    })

    return facets
  },
}

// Annotation Utilities
export const annotationUtils = {
  /**
   * Create a new annotation
   */
  createAnnotation: (data: Partial<Annotation>): Annotation => {
    return {
      id: generateId(),
      type: data.type || 'note',
      content: data.content || '',
      position: data.position || { sectionId: '', x: 0, y: 0 },
      author: data.author || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isResolved: false,
      replies: [],
    }
  },

  /**
   * Create a new bookmark
   */
  createBookmark: (data: Partial<Bookmark>): Bookmark => {
    return {
      id: generateId(),
      title: data.title || 'New Bookmark',
      sectionId: data.sectionId || '',
      position: data.position || 0,
      description: data.description || '',
      createdAt: new Date().toISOString(),
    }
  },

  /**
   * Create a new highlight
   */
  createHighlight: (data: Partial<Highlight>): Highlight => {
    return {
      id: generateId(),
      text: data.text || '',
      sectionId: data.sectionId || '',
      startOffset: data.startOffset || 0,
      endOffset: data.endOffset || 0,
      color: data.color || '#ffff00',
      author: data.author || '',
      createdAt: new Date().toISOString(),
    }
  },

  /**
   * Create a new note
   */
  createNote: (data: Partial<Note>): Note => {
    return {
      id: generateId(),
      content: data.content || '',
      sectionId: data.sectionId || '',
      position: data.position || { sectionId: '', x: 0, y: 0 },
      author: data.author || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isPrivate: data.isPrivate || false,
    }
  },
}

// Drag and Drop Utilities
export const dragDropUtils = {
  /**
   * Create a drag item
   */
  createDragItem: (type: string, data: any): DragItem => {
    return {
      id: generateId(),
      type: type as any,
      data,
    }
  },

  /**
   * Handle drop result
   */
  handleDropResult: (result: DropResult, items: any[]): any[] => {
    if (!result.destination) {
      return items
    }

    const newItems = Array.from(items)
    const [reorderedItem] = newItems.splice(result.source.index, 1)
    newItems.splice(result.destination.index, 0, reorderedItem)

    return newItems
  },

  /**
   * Validate drop operation
   */
  validateDrop: (source: string, destination: string): boolean => {
    // Define valid drop combinations
    const validDrops: Record<string, string[]> = {
      'section': ['sections', 'builder'],
      'chart': ['charts', 'builder'],
      'table': ['tables', 'builder'],
      'template-section': ['sections', 'builder'],
      'template-chart': ['charts', 'builder'],
      'template-table': ['tables', 'builder'],
    }

    return validDrops[source]?.includes(destination) || false
  },
}

// Version Control Utilities
export const versionUtils = {
  /**
   * Create a new version
   */
  createVersion: (report: SavedReport, changes: string[]): ReportVersion => {
    return {
      id: generateId(),
      version: incrementVersion(report.version),
      title: report.title,
      changes,
      author: report.metadata.author,
      createdAt: new Date().toISOString(),
      content: report.content,
      isRestored: false,
    }
  },

  /**
   * Increment version number
   */
  incrementVersion: (version: string): string => {
    const parts = version.split('.')
    const major = parseInt(parts[0]) || 1
    const minor = parseInt(parts[1]) || 0
    const patch = parseInt(parts[2]) || 0
    
    return `${major}.${minor}.${patch + 1}`
  },

  /**
   * Compare versions
   */
  compareVersions: (version1: string, version2: string): number => {
    const v1Parts = version1.split('.').map(Number)
    const v2Parts = version2.split('.').map(Number)
    
    for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
      const v1Part = v1Parts[i] || 0
      const v2Part = v2Parts[i] || 0
      
      if (v1Part < v2Part) return -1
      if (v1Part > v2Part) return 1
    }
    
    return 0
  },
}

// Utility Functions
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9)
}

export const generateTimestamp = (): string => {
  return new Date().toISOString()
}

export const formatDate = (date: string | Date, format: 'short' | 'long' | 'relative' = 'short'): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  
  switch (format) {
    case 'short':
      return d.toLocaleDateString()
    case 'long':
      return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    case 'relative':
      return formatRelativeTime(d)
    default:
      return d.toLocaleDateString()
  }
}

export const formatRelativeTime = (date: Date): string => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`
  if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  return 'Just now'
}

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export const sanitizeHtml = (html: string): string => {
  // Basic HTML sanitization - in production, use a proper library like DOMPurify
  return html
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    .replace(/on\w+="[^"]*"/gi, '')
    .replace(/javascript:/gi, '')
}

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export const validateUrl = (url: string): boolean => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}
