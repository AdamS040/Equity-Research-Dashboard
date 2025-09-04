/**
 * Report System Types
 * 
 * Comprehensive type definitions for the research reports generation system
 */

// Base Report Types
export interface ReportTemplate {
  id: string
  name: string
  type: 'full' | 'valuation' | 'risk' | 'technical' | 'custom'
  description: string
  category: 'equity' | 'portfolio' | 'market' | 'sector'
  sections: ReportSectionTemplate[]
  charts: ReportChartTemplate[]
  tables: ReportTableTemplate[]
  parameters: ReportParameter[]
  isPublic: boolean
  isDefault: boolean
  version: string
  author: string
  tags: string[]
  createdAt: string
  updatedAt: string
  usageCount: number
  rating: number
  preview?: string
}

export interface ReportSectionTemplate {
  id: string
  title: string
  type: 'text' | 'analysis' | 'chart' | 'table' | 'executive_summary' | 'risk_assessment' | 'valuation' | 'technical_analysis' | 'peer_comparison'
  order: number
  required: boolean
  config: Record<string, any>
  content?: string
  placeholder?: string
}

export interface ReportChartTemplate {
  id: string
  title: string
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'candlestick' | 'heatmap' | 'gauge' | 'treemap'
  dataSource: string
  config: ChartConfig
  order: number
  required: boolean
}

export interface ReportTableTemplate {
  id: string
  title: string
  dataSource: string
  columns: TableColumn[]
  config: TableConfig
  order: number
  required: boolean
}

export interface ReportParameter {
  id: string
  name: string
  type: 'string' | 'number' | 'boolean' | 'select' | 'multiselect' | 'date' | 'symbol' | 'portfolio'
  label: string
  description: string
  required: boolean
  defaultValue?: any
  options?: { value: any; label: string }[]
  validation?: ParameterValidation
}

export interface ParameterValidation {
  min?: number
  max?: number
  pattern?: string
  custom?: (value: any) => boolean | string
}

// Report Builder Types
export interface ReportBuilder {
  id: string
  name: string
  template?: string
  sections: ReportSection[]
  charts: ReportChart[]
  tables: ReportTable[]
  parameters: Record<string, any>
  metadata: ReportMetadata
  status: 'draft' | 'building' | 'ready' | 'generating' | 'completed' | 'error'
  createdAt: string
  updatedAt: string
}

export interface ReportSection {
  id: string
  templateId?: string
  title: string
  type: 'text' | 'analysis' | 'chart' | 'table' | 'executive_summary' | 'risk_assessment' | 'valuation' | 'technical_analysis' | 'peer_comparison'
  content: string
  order: number
  config: Record<string, any>
  isCollapsed: boolean
  isValid: boolean
  errors: string[]
  warnings: string[]
}

export interface ReportChart {
  id: string
  templateId?: string
  title: string
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'candlestick' | 'heatmap' | 'gauge' | 'treemap'
  dataSource: string
  data: any
  config: ChartConfig
  order: number
  isVisible: boolean
  isValid: boolean
  errors: string[]
}

export interface ReportTable {
  id: string
  templateId?: string
  title: string
  dataSource: string
  headers: string[]
  rows: any[][]
  config: TableConfig
  order: number
  isVisible: boolean
  isValid: boolean
  errors: string[]
}

// Chart and Table Configuration
export interface ChartConfig {
  width?: number
  height?: number
  responsive?: boolean
  theme?: 'light' | 'dark'
  colors?: string[]
  animations?: boolean
  legend?: LegendConfig
  axes?: AxesConfig
  tooltip?: TooltipConfig
  [key: string]: any
}

export interface LegendConfig {
  show: boolean
  position: 'top' | 'bottom' | 'left' | 'right'
  align: 'start' | 'center' | 'end'
}

export interface AxesConfig {
  x: AxisConfig
  y: AxisConfig
}

export interface AxisConfig {
  show: boolean
  title?: string
  min?: number
  max?: number
  format?: string
  gridLines?: boolean
}

export interface TooltipConfig {
  show: boolean
  format?: string
  custom?: (data: any) => string
}

export interface TableConfig {
  sortable: boolean
  filterable: boolean
  pagination: boolean
  pageSize: number
  striped: boolean
  bordered: boolean
  hover: boolean
  responsive: boolean
  exportable: boolean
}

export interface TableColumn {
  key: string
  title: string
  type: 'string' | 'number' | 'date' | 'currency' | 'percentage' | 'boolean'
  sortable: boolean
  filterable: boolean
  width?: number
  align?: 'left' | 'center' | 'right'
  format?: string
  render?: (value: any, row: any) => React.ReactNode
}

// Report Generation Types
export interface ReportGenerator {
  id: string
  reportId: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  currentStep: string
  steps: GenerationStep[]
  dataSources: DataSource[]
  parameters: Record<string, any>
  startedAt: string
  completedAt?: string
  error?: string
  results: GenerationResults
}

export interface GenerationStep {
  id: string
  name: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  progress: number
  startedAt?: string
  completedAt?: string
  error?: string
  duration?: number
}

export interface DataSource {
  id: string
  name: string
  type: 'api' | 'database' | 'file' | 'calculation'
  endpoint?: string
  query?: string
  parameters: Record<string, any>
  status: 'pending' | 'connected' | 'error'
  lastUpdated?: string
  data?: any
}

export interface GenerationResults {
  sections: GeneratedSection[]
  charts: GeneratedChart[]
  tables: GeneratedTable[]
  summary: GeneratedSummary
  metadata: GeneratedMetadata
  citations: Citation[]
  warnings: string[]
  errors: string[]
}

export interface GeneratedSection {
  id: string
  title: string
  content: string
  type: string
  data?: any
  citations: string[]
}

export interface GeneratedChart {
  id: string
  title: string
  type: string
  data: any
  config: ChartConfig
  citations: string[]
}

export interface GeneratedTable {
  id: string
  title: string
  data: any
  config: TableConfig
  citations: string[]
}

export interface GeneratedSummary {
  executive: string
  keyFindings: string[]
  recommendations: string[]
  risks: string[]
  opportunities: string[]
  targetPrice?: number
  rating?: 'buy' | 'hold' | 'sell'
  confidence: number
}

export interface GeneratedMetadata {
  generatedAt: string
  dataAsOf: string
  sources: string[]
  methodology: string
  assumptions: string[]
  disclaimers: string[]
}

export interface Citation {
  id: string
  type: 'data' | 'analysis' | 'news' | 'research'
  source: string
  url?: string
  date: string
  description: string
  section: string
}

// Report Export Types
export interface ReportExport {
  id: string
  reportId: string
  format: 'pdf' | 'docx' | 'xlsx' | 'html' | 'json'
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  fileUrl?: string
  fileName: string
  fileSize?: number
  options: ExportOptions
  startedAt: string
  completedAt?: string
  error?: string
}

export interface ExportOptions {
  includeCharts: boolean
  includeTables: boolean
  includeData: boolean
  pageSize: 'A4' | 'Letter' | 'Legal'
  orientation: 'portrait' | 'landscape'
  margins: MarginConfig
  header?: HeaderFooterConfig
  footer?: HeaderFooterConfig
  branding?: BrandingConfig
  watermark?: string
  password?: string
  compression?: boolean
}

export interface MarginConfig {
  top: number
  right: number
  bottom: number
  left: number
}

export interface HeaderFooterConfig {
  enabled: boolean
  content: string
  fontSize: number
  alignment: 'left' | 'center' | 'right'
  includePageNumbers: boolean
}

export interface BrandingConfig {
  logo?: string
  companyName: string
  colors: {
    primary: string
    secondary: string
    accent: string
  }
  fonts: {
    heading: string
    body: string
    monospace: string
  }
}

// Report Management Types
export interface ReportManagement {
  reports: SavedReport[]
  templates: ReportTemplate[]
  schedules: ReportSchedule[]
  analytics: ReportAnalytics
  settings: ReportSettings
}

export interface SavedReport {
  id: string
  title: string
  type: string
  symbol?: string
  portfolioId?: string
  templateId?: string
  status: 'draft' | 'published' | 'archived'
  version: string
  author: string
  collaborators: Collaborator[]
  tags: string[]
  isFavorite: boolean
  isShared: boolean
  shareUrl?: string
  permissions: ReportPermissions
  metadata: ReportMetadata
  content: ReportContent
  history: ReportVersion[]
  comments: ReportComment[]
  analytics: ReportUsageAnalytics
  createdAt: string
  updatedAt: string
  publishedAt?: string
  lastViewedAt?: string
  viewCount: number
  downloadCount: number
  shareCount: number
}

export interface ReportVersion {
  id: string
  version: string
  title: string
  changes: string[]
  author: string
  createdAt: string
  content: ReportContent
  isRestored: boolean
}

export interface ReportComment {
  id: string
  author: string
  content: string
  sectionId?: string
  position?: { x: number; y: number }
  isResolved: boolean
  replies: CommentReply[]
  createdAt: string
  updatedAt: string
}

export interface CommentReply {
  id: string
  author: string
  content: string
  createdAt: string
}

export interface Collaborator {
  id: string
  email: string
  name: string
  role: 'viewer' | 'editor' | 'admin'
  permissions: string[]
  addedAt: string
  addedBy: string
}

export interface ReportPermissions {
  canView: boolean
  canEdit: boolean
  canDelete: boolean
  canShare: boolean
  canComment: boolean
  canExport: boolean
  canSchedule: boolean
}

export interface ReportSchedule {
  id: string
  reportId: string
  name: string
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'custom'
  cronExpression?: string
  dayOfWeek?: number
  dayOfMonth?: number
  time: string
  timezone: string
  recipients: string[]
  format: 'pdf' | 'docx' | 'xlsx' | 'html'
  options: ExportOptions
  isActive: boolean
  lastRun?: string
  nextRun: string
  runCount: number
  successCount: number
  failureCount: number
  createdAt: string
  updatedAt: string
}

export interface ReportAnalytics {
  totalReports: number
  totalViews: number
  totalDownloads: number
  totalShares: number
  popularReports: PopularReport[]
  recentActivity: ActivityItem[]
  usageByType: UsageByType[]
  usageByUser: UsageByUser[]
  performanceMetrics: PerformanceMetrics
}

export interface PopularReport {
  id: string
  title: string
  views: number
  downloads: number
  shares: number
  rating: number
}

export interface ActivityItem {
  id: string
  type: 'created' | 'updated' | 'viewed' | 'downloaded' | 'shared' | 'commented'
  reportId: string
  reportTitle: string
  user: string
  timestamp: string
  details?: any
}

export interface UsageByType {
  type: string
  count: number
  percentage: number
}

export interface UsageByUser {
  userId: string
  userName: string
  reportsCreated: number
  reportsViewed: number
  reportsDownloaded: number
}

export interface PerformanceMetrics {
  averageGenerationTime: number
  averageExportTime: number
  successRate: number
  errorRate: number
  userSatisfaction: number
}

export interface ReportUsageAnalytics {
  views: number
  downloads: number
  shares: number
  comments: number
  lastViewedAt?: string
  lastDownloadedAt?: string
  lastSharedAt?: string
  viewHistory: ViewEvent[]
  downloadHistory: DownloadEvent[]
  shareHistory: ShareEvent[]
}

export interface ViewEvent {
  id: string
  userId: string
  timestamp: string
  duration: number
  sections: string[]
}

export interface DownloadEvent {
  id: string
  userId: string
  format: string
  timestamp: string
  fileSize: number
}

export interface ShareEvent {
  id: string
  userId: string
  method: 'email' | 'link' | 'api'
  recipients: string[]
  timestamp: string
}

export interface ReportSettings {
  defaultTemplate: string
  defaultFormat: 'pdf' | 'docx' | 'xlsx' | 'html'
  autoSave: boolean
  autoSaveInterval: number
  notifications: NotificationSettings
  branding: BrandingConfig
  dataRetention: DataRetentionSettings
  security: SecuritySettings
}

export interface NotificationSettings {
  email: boolean
  push: boolean
  reportGenerated: boolean
  reportShared: boolean
  reportCommented: boolean
  reportScheduled: boolean
}

export interface DataRetentionSettings {
  keepVersions: number
  keepHistory: number
  autoArchive: boolean
  archiveAfterDays: number
}

export interface SecuritySettings {
  requirePassword: boolean
  allowSharing: boolean
  allowExport: boolean
  watermark: boolean
  auditLog: boolean
}

// Report Viewer Types
export interface ReportViewer {
  report: SavedReport
  currentSection: string
  viewMode: 'full' | 'section' | 'print'
  zoom: number
  annotations: Annotation[]
  bookmarks: Bookmark[]
  highlights: Highlight[]
  notes: Note[]
  isFullscreen: boolean
  isPrintMode: boolean
  showComments: boolean
  showAnnotations: boolean
  showBookmarks: boolean
  showHighlights: boolean
  showNotes: boolean
}

export interface Annotation {
  id: string
  type: 'note' | 'highlight' | 'comment' | 'drawing'
  content: string
  position: AnnotationPosition
  author: string
  createdAt: string
  updatedAt: string
  isResolved: boolean
  replies: CommentReply[]
}

export interface AnnotationPosition {
  sectionId: string
  x: number
  y: number
  width?: number
  height?: number
  page?: number
}

export interface Bookmark {
  id: string
  title: string
  sectionId: string
  position: number
  description?: string
  createdAt: string
}

export interface Highlight {
  id: string
  text: string
  sectionId: string
  startOffset: number
  endOffset: number
  color: string
  author: string
  createdAt: string
}

export interface Note {
  id: string
  content: string
  sectionId: string
  position: AnnotationPosition
  author: string
  createdAt: string
  updatedAt: string
  isPrivate: boolean
}

// Report Content Types (extending existing types)
export interface ReportContent {
  sections: ReportSection[]
  charts: ReportChart[]
  tables: ReportTable[]
  summary: ReportSummary
  recommendations: Recommendation[]
  disclaimers: string[]
  citations: Citation[]
  metadata: ReportMetadata
}

export interface ReportSummary {
  executive: string
  keyFindings: string[]
  investmentHighlights: string[]
  riskFactors: string[]
  opportunities: string[]
  targetPrice?: number
  rating?: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell'
  confidence: number
  timeHorizon: string
  catalysts: string[]
}

export interface Recommendation {
  id: string
  type: 'buy' | 'hold' | 'sell'
  targetPrice?: number
  timeHorizon: string
  confidence: number
  rationale: string
  risks: string[]
  catalysts: string[]
}

export interface ReportMetadata {
  author: string
  version: string
  tags: string[]
  language: string
  format: 'pdf' | 'html' | 'markdown' | 'docx'
  generatedAt: string
  dataAsOf: string
  sources: string[]
  methodology: string
  assumptions: string[]
  disclaimers: string[]
  compliance: ComplianceInfo
}

export interface ComplianceInfo {
  regulatory: string[]
  disclosures: string[]
  conflicts: string[]
  certifications: string[]
}

// Drag and Drop Types
export interface DragItem {
  id: string
  type: 'section' | 'chart' | 'table'
  data: any
}

export interface DropResult {
  destination?: {
    droppableId: string
    index: number
  }
  source: {
    droppableId: string
    index: number
  }
  draggableId: string
}

// Validation Types
export interface ValidationResult {
  isValid: boolean
  errors: ValidationError[]
  warnings: ValidationWarning[]
}

export interface ValidationError {
  field: string
  message: string
  code: string
  severity: 'error' | 'warning'
}

export interface ValidationWarning {
  field: string
  message: string
  code: string
  suggestion?: string
}

// Search and Filter Types
export interface ReportSearchFilters {
  query?: string
  type?: string
  status?: string
  author?: string
  tags?: string[]
  dateRange?: {
    start: string
    end: string
  }
  sortBy?: 'title' | 'createdAt' | 'updatedAt' | 'viewCount' | 'rating'
  sortOrder?: 'asc' | 'desc'
  page?: number
  limit?: number
}

export interface ReportSearchResult {
  reports: SavedReport[]
  total: number
  page: number
  limit: number
  hasNext: boolean
  hasPrev: boolean
  facets: SearchFacets
}

export interface SearchFacets {
  types: { [key: string]: number }
  statuses: { [key: string]: number }
  authors: { [key: string]: number }
  tags: { [key: string]: number }
  dateRanges: { [key: string]: number }
}
