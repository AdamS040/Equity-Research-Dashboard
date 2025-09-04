# Research Reports Generation System

A comprehensive system for creating, managing, and sharing professional equity research reports with automated data collection, analysis, and export capabilities.

## Overview

The Research Reports Generation System provides a complete solution for equity research professionals to create, manage, and share detailed financial analysis reports. The system includes pre-built templates, drag-and-drop report building, automated data collection, and professional export capabilities.

## Components

### 1. ReportTemplates (`ReportTemplates.tsx`)

Pre-built report templates with preview, custom creation, and versioning capabilities.

**Features:**
- Pre-built templates (Full Analysis, Valuation, Risk Analysis, Technical Analysis)
- Template preview functionality
- Custom template creation
- Template sharing and import/export
- Template versioning system
- Search and filter templates
- Rating and usage statistics

**Usage:**
```tsx
import { ReportTemplates } from '@/components/reports'

<ReportTemplates
  onSelectTemplate={(template) => console.log('Selected:', template)}
  onCreateCustom={() => console.log('Create custom template')}
  showCreateButton={true}
  showEditButton={false}
/>
```

### 2. ReportBuilder (`ReportBuilder.tsx`)

Drag-and-drop report builder with real-time preview and content validation.

**Features:**
- Drag-and-drop report sections
- Customizable content blocks
- Real-time preview
- Section reordering and editing
- Content validation and error checking
- Auto-save functionality
- Template-based building

**Usage:**
```tsx
import { ReportBuilder } from '@/components/reports'

<ReportBuilder
  initialBuilder={builder}
  template={template}
  onSave={(builder) => console.log('Saved:', builder)}
  onPreview={(builder) => console.log('Preview:', builder)}
  readOnly={false}
/>
```

### 3. ReportGenerator (`ReportGenerator.tsx`)

Automated data collection, chart generation, and analysis.

**Features:**
- Automated data collection from multiple sources
- Chart and table generation
- Executive summary generation
- Risk assessment automation
- Valuation model integration
- Peer comparison analysis
- Progress tracking
- Error handling and validation

**Usage:**
```tsx
import { ReportGenerator } from '@/components/reports'

<ReportGenerator
  reportId="report-123"
  parameters={{ symbol: 'AAPL', timeframe: '1y' }}
  onComplete={(results) => console.log('Generated:', results)}
  onError={(error) => console.error('Error:', error)}
  autoStart={true}
/>
```

### 4. ReportExport (`ReportExport.tsx`)

PDF, DOCX, Excel export and sharing functionality.

**Features:**
- PDF generation with professional formatting
- DOCX export with editable content
- Excel export for data tables
- Email sharing functionality
- Print-friendly layouts
- Custom branding options
- Export history tracking

**Usage:**
```tsx
import { ReportExport } from '@/components/reports'

<ReportExport
  reportId="report-123"
  reportTitle="Apple Inc. Analysis"
  onExportComplete={(exportData) => console.log('Exported:', exportData)}
  onShareComplete={(shareData) => console.log('Shared:', shareData)}
/>
```

### 5. ReportManagement (`ReportManagement.tsx`)

Saved reports list with search, filter, versioning, and analytics.

**Features:**
- Saved reports list with search and filter
- Report history and versioning
- Sharing permissions and access control
- Report scheduling and automation
- Analytics on report usage
- Favorites management
- Bulk operations

**Usage:**
```tsx
import { ReportManagement } from '@/components/reports'

<ReportManagement
  onSelectReport={(report) => console.log('Selected:', report)}
  onEditReport={(report) => console.log('Edit:', report)}
  onCreateReport={() => console.log('Create new')}
  showCreateButton={true}
  showEditButton={true}
  showDeleteButton={true}
  showAnalytics={true}
/>
```

### 6. ReportViewer (`ReportViewer.tsx`)

Full-screen report viewing with interactive charts, annotations, and bookmarks.

**Features:**
- Full-screen report viewing
- Interactive charts and tables
- Annotation and highlighting
- Bookmarking and favorites
- Print and download options
- Zoom and navigation controls
- Sidebar with outline, annotations, bookmarks, comments, and versions

**Usage:**
```tsx
import { ReportViewer } from '@/components/reports'

<ReportViewer
  reportId="report-123"
  onClose={() => console.log('Close viewer')}
  onEdit={() => console.log('Edit report')}
  onExport={() => console.log('Export report')}
  onShare={() => console.log('Share report')}
  readOnly={false}
  showAnnotations={true}
  showBookmarks={true}
  showComments={true}
/>
```

## Types and Interfaces

The system includes comprehensive TypeScript types and interfaces:

- **Report Types**: `ReportTemplate`, `ReportBuilder`, `ReportSection`, `ReportChart`, `ReportTable`
- **Generation Types**: `ReportGenerator`, `GenerationStep`, `DataSource`, `GenerationResults`
- **Export Types**: `ReportExport`, `ExportOptions`, `BrandingConfig`
- **Management Types**: `SavedReport`, `ReportSearchFilters`, `ReportVersion`, `ReportComment`
- **Viewer Types**: `ReportViewer`, `Annotation`, `Bookmark`, `Highlight`, `Note`
- **Validation Types**: `ValidationResult`, `ValidationError`, `ValidationWarning`

## Utilities

The system includes utility functions for:

- **Template Management**: Creating, cloning, and validating templates
- **Report Building**: Adding sections, charts, tables, and validation
- **Content Generation**: Executive summaries, key findings, recommendations
- **Export Utilities**: Format validation, filename generation, options management
- **Search and Filter**: Report search, filtering, and faceting
- **Annotation Management**: Creating and managing annotations, bookmarks, highlights
- **Version Control**: Version management and comparison
- **General Utilities**: Date formatting, text truncation, validation helpers

## API Integration

The system integrates with the existing API hooks:

- `useReports` - Get reports with filtering and pagination
- `useReport` - Get individual report details
- `useCreateReport` - Create new reports
- `useUpdateReport` - Update existing reports
- `useDeleteReport` - Delete reports
- `useGenerateReport` - Generate report content
- `useExportReport` - Export reports in various formats
- `useShareReport` - Share reports with others
- `useReportTemplates` - Get report templates
- `useReportComments` - Manage report comments
- `useReportVersions` - Manage report versions

## Usage Examples

### Creating a New Report

```tsx
import { ReportTemplates, ReportBuilder } from '@/components/reports'

function CreateReport() {
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [showBuilder, setShowBuilder] = useState(false)

  return (
    <div>
      {!showBuilder ? (
        <ReportTemplates
          onSelectTemplate={(template) => {
            setSelectedTemplate(template)
            setShowBuilder(true)
          }}
        />
      ) : (
        <ReportBuilder
          template={selectedTemplate}
          onSave={(builder) => {
            console.log('Report saved:', builder)
            setShowBuilder(false)
          }}
        />
      )}
    </div>
  )
}
```

### Managing Reports

```tsx
import { ReportManagement, ReportViewer } from '@/components/reports'

function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState(null)
  const [viewMode, setViewMode] = useState('list')

  return (
    <div>
      {!selectedReport ? (
        <ReportManagement
          onSelectReport={(report) => setSelectedReport(report)}
          onEditReport={(report) => console.log('Edit:', report)}
        />
      ) : (
        <ReportViewer
          reportId={selectedReport.id}
          onClose={() => setSelectedReport(null)}
          onEdit={() => console.log('Edit report')}
        />
      )}
    </div>
  )
}
```

### Generating and Exporting Reports

```tsx
import { ReportGenerator, ReportExport } from '@/components/reports'

function ReportWorkflow() {
  const [reportId, setReportId] = useState(null)
  const [generationComplete, setGenerationComplete] = useState(false)

  return (
    <div>
      {!generationComplete ? (
        <ReportGenerator
          reportId={reportId}
          parameters={{ symbol: 'AAPL', timeframe: '1y' }}
          onComplete={(results) => {
            console.log('Generation complete:', results)
            setGenerationComplete(true)
          }}
          autoStart={true}
        />
      ) : (
        <ReportExport
          reportId={reportId}
          reportTitle="Apple Inc. Analysis"
          onExportComplete={(exportData) => {
            console.log('Export complete:', exportData)
          }}
        />
      )}
    </div>
  )
}
```

## Styling and Theming

The components use the existing design system and can be customized through:

- CSS custom properties for colors and spacing
- Theme provider for consistent styling
- Responsive design with mobile-first approach
- Accessibility features with ARIA labels and keyboard navigation

## Performance Considerations

- **Lazy Loading**: Components are loaded on demand
- **Virtual Scrolling**: For large lists of reports
- **Debounced Search**: To prevent excessive API calls
- **Memoization**: React.memo and useMemo for expensive operations
- **Code Splitting**: Components are split for better bundle size

## Accessibility

The system includes comprehensive accessibility features:

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Support**: ARIA labels and descriptions
- **High Contrast**: Support for high contrast themes
- **Focus Management**: Proper focus handling in modals and forms
- **Alternative Text**: For images and charts

## Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile Browsers**: iOS Safari 14+, Chrome Mobile 90+
- **Progressive Enhancement**: Graceful degradation for older browsers

## Contributing

When contributing to the reports system:

1. Follow the existing code style and patterns
2. Add comprehensive TypeScript types
3. Include proper error handling
4. Write unit tests for new functionality
5. Update documentation for new features
6. Ensure accessibility compliance

## License

This system is part of the Equity Research Dashboard and follows the same licensing terms.
