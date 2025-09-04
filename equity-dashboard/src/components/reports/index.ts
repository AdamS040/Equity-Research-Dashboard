/**
 * Reports Components Index
 * 
 * Exports all report-related components for easy importing
 */

// Main Components
export { ReportTemplates } from './ReportTemplates'
export { ReportBuilderComponent as ReportBuilder } from './ReportBuilder'
export { ReportGenerator } from './ReportGenerator'
export { ReportExport } from './ReportExport'
export { ReportManagement } from './ReportManagement'
export { ReportViewer } from './ReportViewer'

// Re-export types for convenience
export type {
  // Report Types
  ReportTemplate,
  ReportBuilder,
  ReportSection,
  ReportChart,
  ReportTable,
  ReportParameter,
  ReportGenerator as ReportGeneratorType,
  GenerationStep,
  DataSource,
  GenerationResults,
  GeneratedSection,
  GeneratedChart,
  GeneratedTable,
  GeneratedSummary,
  Citation,
  
  // Export Types
  ReportExport as ReportExportType,
  ExportOptions,
  MarginConfig,
  HeaderFooterConfig,
  BrandingConfig,
  
  // Management Types
  SavedReport,
  ReportSearchFilters,
  ReportSearchResult,
  SearchFacets,
  ReportVersion,
  ReportComment,
  ReportSchedule,
  ReportAnalytics,
  ReportUsageAnalytics,
  
  // Viewer Types
  ReportViewer as ReportViewerType,
  Annotation,
  Bookmark,
  Highlight,
  Note,
  AnnotationPosition,
  
  // Validation Types
  ValidationResult,
  ValidationError,
  ValidationWarning,
  
  // Drag and Drop Types
  DragItem,
  DropResult,
  
  // Chart and Table Configuration
  ChartConfig,
  TableConfig,
  TableColumn,
  LegendConfig,
  AxesConfig,
  AxisConfig,
  TooltipConfig,
} from '../../types/reports'

// Re-export utilities for convenience
export {
  templateUtils,
  builderUtils,
  contentUtils,
  exportUtils,
  searchUtils,
  annotationUtils,
  dragDropUtils,
  versionUtils,
  generateId,
  generateTimestamp,
  formatDate,
  formatRelativeTime,
  truncateText,
  sanitizeHtml,
  validateEmail,
  validateUrl,
  debounce,
  throttle,
} from '../../utils/reports'
