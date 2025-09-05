/**
 * Report Export Component
 * 
 * PDF, DOCX, Excel export and sharing functionality
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
  ReportExport as ReportExportType,
  ExportOptions,
  MarginConfig,
  HeaderFooterConfig,
  BrandingConfig,
  ValidationResult
} from '../../types/reports'
import { exportUtils } from '../../utils/reports'
import { useExportReport, useShareReport } from '../../hooks/api/useReports'

interface ReportExportProps {
  reportId: string
  reportTitle: string
  onExportComplete?: (exportData: ReportExportType) => void
  onShareComplete?: (shareData: any) => void
}

export const ReportExport: React.FC<ReportExportProps> = ({
  reportId,
  reportTitle,
  onExportComplete,
  onShareComplete,
}) => {
  const [showExportModal, setShowExportModal] = useState(false)
  const [showShareModal, setShowShareModal] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'docx' | 'xlsx' | 'html'>('pdf')
  const [exportOptions, setExportOptions] = useState<ExportOptions>(exportUtils.getDefaultOptions())
  const [shareOptions, setShareOptions] = useState({
    recipients: [] as string[],
    message: '',
    expiresAt: '',
    allowDownload: true,
  })
  const [isExporting, setIsExporting] = useState(false)
  const [isSharing, setIsSharing] = useState(false)
  const [exportHistory, setExportHistory] = useState<ReportExportType[]>([])
  const [validation, setValidation] = useState<ValidationResult | null>(null)

  // API hooks
  const exportReportMutation = useExportReport()
  const shareReportMutation = useShareReport()

  // Validate export options
  const validateOptions = useCallback((options: ExportOptions) => {
    const result = exportUtils.validateExportOptions(options)
    setValidation(result)
    return result.isValid
  }, [])

  // Handle format selection
  const handleFormatChange = useCallback((format: 'pdf' | 'docx' | 'xlsx' | 'html') => {
    setSelectedFormat(format)
    
    // Update options based on format
    const newOptions = { ...exportOptions }
    
    if (format === 'pdf') {
      newOptions.pageSize = 'A4'
      newOptions.orientation = 'portrait'
    } else if (format === 'docx') {
      newOptions.includeCharts = true
      newOptions.includeTables = true
    } else if (format === 'xlsx') {
      newOptions.includeCharts = false
      newOptions.includeTables = true
      newOptions.includeData = true
    } else if (format === 'html') {
      newOptions.includeCharts = true
      newOptions.includeTables = true
      newOptions.includeData = true
    }
    
    setExportOptions(newOptions)
    validateOptions(newOptions)
  }, [exportOptions, validateOptions])

  // Handle export
  const handleExport = useCallback(async () => {
    if (!validateOptions(exportOptions)) {
      return
    }

    setIsExporting(true)
    
    try {
      const blob = await exportReportMutation.mutateAsync({
        reportId,
        format: selectedFormat,
      })

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = exportUtils.generateFilename(reportTitle, selectedFormat)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      // Add to export history
      const newExport: ReportExportType = {
        id: `export-${Date.now()}`,
        reportId,
        format: selectedFormat,
        status: 'completed',
        progress: 100,
        fileName: link.download,
        fileSize: blob.size,
        options: exportOptions,
        startedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
      }
      
      setExportHistory(prev => [newExport, ...prev])
      setShowExportModal(false)
      
      if (onExportComplete) {
        onExportComplete(newExport)
      }
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
    }
  }, [reportId, selectedFormat, exportOptions, reportTitle, validateOptions, exportReportMutation, onExportComplete])

  // Handle share
  const handleShare = useCallback(async () => {
    setIsSharing(true)
    
    try {
      const shareData = await shareReportMutation.mutateAsync({
        reportId,
        options: shareOptions,
      })

      setShowShareModal(false)
      
      if (onShareComplete) {
        onShareComplete(shareData)
      }
    } catch (error) {
      console.error('Share failed:', error)
    } finally {
      setIsSharing(false)
    }
  }, [reportId, shareOptions, shareReportMutation, onShareComplete])

  // Update export options
  const updateExportOptions = useCallback((updates: Partial<ExportOptions>) => {
    const newOptions = { ...exportOptions, ...updates }
    setExportOptions(newOptions)
    validateOptions(newOptions)
  }, [exportOptions, validateOptions])

  // Format options for different export types
  const formatOptions = useMemo(() => ({
    pdf: {
      name: 'PDF Document',
      description: 'Professional PDF with charts and tables',
      icon: '📄',
      features: ['Print-ready', 'Charts included', 'Professional layout'],
    },
    docx: {
      name: 'Word Document',
      description: 'Editable Word document',
      icon: '📝',
      features: ['Editable content', 'Charts as images', 'Table formatting'],
    },
    xlsx: {
      name: 'Excel Spreadsheet',
      description: 'Data tables and charts in Excel',
      icon: '📊',
      features: ['Data tables', 'Interactive charts', 'Formulas preserved'],
    },
    html: {
      name: 'HTML Web Page',
      description: 'Web-ready HTML document',
      icon: '🌐',
      features: ['Web compatible', 'Interactive charts', 'Responsive design'],
    },
  }), [])

  return (
    <Container>
      {/* Header */}
      <Card mb="lg">
        <CardBody>
          <Flex justify="between" align="center">
            <div>
              <Heading level={2}>Export & Share Report</Heading>
              <Text color="gray" size="sm">
                Export your report in various formats or share with others
              </Text>
            </div>
            <Flex gap="md">
              <Button variant="outline" onClick={() => setShowShareModal(true)}>
                Share Report
              </Button>
              <Button variant="primary" onClick={() => setShowExportModal(true)}>
                Export Report
              </Button>
            </Flex>
          </Flex>
        </CardBody>
      </Card>

      {/* Export History */}
      {exportHistory.length > 0 && (
        <Card mb="lg">
          <CardHeader>
            <Heading level={4}>Recent Exports</Heading>
          </CardHeader>
          <CardBody>
            <div>
              {exportHistory.slice(0, 5).map((exportItem) => (
                <div key={exportItem.id} style={{ 
                  padding: '12px', 
                  border: '1px solid #e5e7eb', 
                  borderRadius: '4px',
                  marginBottom: '8px'
                }}>
                  <Flex justify="between" align="center">
                    <Flex align="center" gap="md">
                      <span style={{ fontSize: '20px' }}>
                        {formatOptions[exportItem.format].icon}
                      </span>
                      <div>
                        <Text weight="medium">{exportItem.fileName}</Text>
                        <Text size="sm" color="gray">
                          {formatOptions[exportItem.format].name} • 
                          {exportItem.fileSize ? ` ${Math.round(exportItem.fileSize / 1024)}KB` : ''} • 
                          {new Date(exportItem.completedAt || exportItem.startedAt).toLocaleString()}
                        </Text>
                      </div>
                    </Flex>
                    <Badge variant={exportItem.status === 'completed' ? 'success' : 'secondary'}>
                      {exportItem.status}
                    </Badge>
                  </Flex>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Export Modal */}
      {showExportModal && (
        <ExportModal
          reportTitle={reportTitle}
          selectedFormat={selectedFormat}
          exportOptions={exportOptions}
          validation={validation}
          isExporting={isExporting}
          onFormatChange={handleFormatChange}
          onOptionsChange={updateExportOptions}
          onExport={handleExport}
          onClose={() => setShowExportModal(false)}
        />
      )}

      {/* Share Modal */}
      {showShareModal && (
        <ShareModal
          shareOptions={shareOptions}
          isSharing={isSharing}
          onOptionsChange={setShareOptions}
          onShare={handleShare}
          onClose={() => setShowShareModal(false)}
        />
      )}
    </Container>
  )
}

// Export Modal Component
interface ExportModalProps {
  reportTitle: string
  selectedFormat: 'pdf' | 'docx' | 'xlsx' | 'html'
  exportOptions: ExportOptions
  validation: ValidationResult | null
  isExporting: boolean
  onFormatChange: (format: 'pdf' | 'docx' | 'xlsx' | 'html') => void
  onOptionsChange: (options: Partial<ExportOptions>) => void
  onExport: () => void
  onClose: () => void
}

const ExportModal: React.FC<ExportModalProps> = ({
  reportTitle,
  selectedFormat,
  exportOptions,
  validation,
  isExporting,
  onFormatChange,
  onOptionsChange,
  onExport,
  onClose,
}) => {
  const formatOptions = {
    pdf: { name: 'PDF Document', icon: '📄', description: 'Professional PDF with charts and tables' },
    docx: { name: 'Word Document', icon: '📝', description: 'Editable Word document' },
    xlsx: { name: 'Excel Spreadsheet', icon: '📊', description: 'Data tables and charts in Excel' },
    html: { name: 'HTML Web Page', icon: '🌐', description: 'Web-ready HTML document' },
  }

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Export Report"
      size="xl"
    >
      <div style={{ padding: '16px' }}>
        {/* Format Selection */}
        <div style={{ marginBottom: '24px' }}>
          <Heading level={4} mb="md">Select Export Format</Heading>
          <Grid columns={4} gap="md">
            {Object.entries(formatOptions).map(([format, options]) => (
              <GridItem key={format}>
                <Card 
                  hoverable 
                  onClick={() => onFormatChange(format as any)}
                  style={{ 
                    cursor: 'pointer',
                    border: selectedFormat === format ? '2px solid #3b82f6' : '1px solid #e5e7eb',
                    backgroundColor: selectedFormat === format ? '#f0f9ff' : 'white'
                  }}
                >
                  <CardBody style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '32px', marginBottom: '8px' }}>
                      {options.icon}
                    </div>
                    <Heading level={5} mb="xs">{options.name}</Heading>
                    <Text size="sm" color="gray">{options.description}</Text>
                  </CardBody>
                </Card>
              </GridItem>
            ))}
          </Grid>
        </div>

        {/* Export Options */}
        <div style={{ marginBottom: '24px' }}>
          <Heading level={4} mb="md">Export Options</Heading>
          
          {/* Basic Options */}
          <Grid columns={2} gap="md" mb="md">
            <GridItem>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={exportOptions.includeCharts}
                  onChange={(e) => onOptionsChange({ includeCharts: e.target.checked })}
                />
                <span>Include Charts</span>
              </label>
            </GridItem>
            <GridItem>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={exportOptions.includeTables}
                  onChange={(e) => onOptionsChange({ includeTables: e.target.checked })}
                />
                <span>Include Tables</span>
              </label>
            </GridItem>
            <GridItem>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={exportOptions.includeData}
                  onChange={(e) => onOptionsChange({ includeData: e.target.checked })}
                />
                <span>Include Raw Data</span>
              </label>
            </GridItem>
            <GridItem>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={exportOptions.compression}
                  onChange={(e) => onOptionsChange({ compression: e.target.checked })}
                />
                <span>Compress File</span>
              </label>
            </GridItem>
          </Grid>

          {/* PDF Specific Options */}
          {selectedFormat === 'pdf' && (
            <div>
              <Grid columns={2} gap="md" mb="md">
                <GridItem>
                  <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                    Page Size
                  </label>
                  <select
                    value={exportOptions.pageSize}
                    onChange={(e) => onOptionsChange({ pageSize: e.target.value as any })}
                    style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px' }}
                  >
                    <option value="A4">A4</option>
                    <option value="Letter">Letter</option>
                    <option value="Legal">Legal</option>
                  </select>
                </GridItem>
                <GridItem>
                  <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
                    Orientation
                  </label>
                  <select
                    value={exportOptions.orientation}
                    onChange={(e) => onOptionsChange({ orientation: e.target.value as any })}
                    style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px' }}
                  >
                    <option value="portrait">Portrait</option>
                    <option value="landscape">Landscape</option>
                  </select>
                </GridItem>
              </Grid>

              {/* Margins */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                  Margins (inches)
                </label>
                <Grid columns={4} gap="sm">
                  <GridItem>
                    <Input
                      type="number"
                      step="0.1"
                      min="0.5"
                      max="2"
                      value={exportOptions.margins.top}
                      onChange={(e) => onOptionsChange({ 
                        margins: { ...exportOptions.margins, top: parseFloat(e.target.value) }
                      })}
                      placeholder="Top"
                    />
                  </GridItem>
                  <GridItem>
                    <Input
                      type="number"
                      step="0.1"
                      min="0.5"
                      max="2"
                      value={exportOptions.margins.right}
                      onChange={(e) => onOptionsChange({ 
                        margins: { ...exportOptions.margins, right: parseFloat(e.target.value) }
                      })}
                      placeholder="Right"
                    />
                  </GridItem>
                  <GridItem>
                    <Input
                      type="number"
                      step="0.1"
                      min="0.5"
                      max="2"
                      value={exportOptions.margins.bottom}
                      onChange={(e) => onOptionsChange({ 
                        margins: { ...exportOptions.margins, bottom: parseFloat(e.target.value) }
                      })}
                      placeholder="Bottom"
                    />
                  </GridItem>
                  <GridItem>
                    <Input
                      type="number"
                      step="0.1"
                      min="0.5"
                      max="2"
                      value={exportOptions.margins.left}
                      onChange={(e) => onOptionsChange({ 
                        margins: { ...exportOptions.margins, left: parseFloat(e.target.value) }
                      })}
                      placeholder="Left"
                    />
                  </GridItem>
                </Grid>
              </div>
            </div>
          )}

          {/* Header/Footer Options */}
          <div style={{ marginBottom: '16px' }}>
            <Heading level={5} mb="sm">Header & Footer</Heading>
            <Grid columns={2} gap="md">
              <GridItem>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={exportOptions.header?.enabled || false}
                    onChange={(e) => onOptionsChange({ 
                      header: { ...exportOptions.header, enabled: e.target.checked } as HeaderFooterConfig
                    })}
                  />
                  <span>Include Header</span>
                </label>
                {exportOptions.header?.enabled && (
                  <Input
                    value={exportOptions.header.content}
                    onChange={(e) => onOptionsChange({ 
                      header: { ...exportOptions.header, content: e.target.value } as HeaderFooterConfig
                    })}
                    placeholder="Header content"
                    style={{ marginTop: '8px' }}
                  />
                )}
              </GridItem>
              <GridItem>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={exportOptions.footer?.enabled || false}
                    onChange={(e) => onOptionsChange({ 
                      footer: { ...exportOptions.footer, enabled: e.target.checked } as HeaderFooterConfig
                    })}
                  />
                  <span>Include Footer</span>
                </label>
                {exportOptions.footer?.enabled && (
                  <Input
                    value={exportOptions.footer.content}
                    onChange={(e) => onOptionsChange({ 
                      footer: { ...exportOptions.footer, content: e.target.value } as HeaderFooterConfig
                    })}
                    placeholder="Footer content"
                    style={{ marginTop: '8px' }}
                  />
                )}
              </GridItem>
            </Grid>
          </div>

          {/* Branding Options */}
          <div style={{ marginBottom: '16px' }}>
            <Heading level={5} mb="sm">Branding</Heading>
            <Grid columns={2} gap="md">
              <GridItem>
                <Input
                  value={exportOptions.branding?.companyName || ''}
                  onChange={(e) => onOptionsChange({ 
                    branding: { ...exportOptions.branding, companyName: e.target.value } as BrandingConfig
                  })}
                  placeholder="Company Name"
                />
              </GridItem>
              <GridItem>
                <Input
                  value={exportOptions.branding?.logo || ''}
                  onChange={(e) => onOptionsChange({ 
                    branding: { ...exportOptions.branding, logo: e.target.value } as BrandingConfig
                  })}
                  placeholder="Logo URL"
                />
              </GridItem>
            </Grid>
          </div>
        </div>

        {/* Validation Messages */}
        {validation && !validation.isValid && (
          <div style={{ 
            padding: '12px', 
            backgroundColor: '#fef2f2', 
            border: '1px solid #fecaca', 
            borderRadius: '4px',
            marginBottom: '16px'
          }}>
            <Text color="red" weight="medium" mb="xs">Validation Errors:</Text>
            {validation.errors.map((error, index) => (
              <Text key={index} color="red" size="sm">• {error.message}</Text>
            ))}
          </div>
        )}

        {validation && validation.warnings.length > 0 && (
          <div style={{ 
            padding: '12px', 
            backgroundColor: '#fffbeb', 
            border: '1px solid #fed7aa', 
            borderRadius: '4px',
            marginBottom: '16px'
          }}>
            <Text color="orange" weight="medium" mb="xs">Warnings:</Text>
            {validation.warnings.map((warning, index) => (
              <Text key={index} color="orange" size="sm">• {warning.message}</Text>
            ))}
          </div>
        )}

        {/* File Preview */}
        <div style={{ 
          padding: '12px', 
          backgroundColor: '#f9fafb', 
          border: '1px solid #e5e7eb', 
          borderRadius: '4px',
          marginBottom: '16px'
        }}>
          <Text weight="medium" mb="xs">Export Preview:</Text>
          <Text size="sm" color="gray">
            <strong>File:</strong> {exportUtils.generateFilename(reportTitle, selectedFormat)}<br/>
            <strong>Format:</strong> {formatOptions[selectedFormat].name}<br/>
            <strong>Size:</strong> Estimated {selectedFormat === 'pdf' ? '2-5MB' : selectedFormat === 'docx' ? '1-3MB' : '500KB-2MB'}
          </Text>
        </div>
      </div>

      {/* Modal Actions */}
      <Flex justify="end" gap="md" style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button 
          variant="primary" 
          onClick={onExport}
          disabled={isExporting || (validation && !validation.isValid)}
        >
          {isExporting ? (
            <>
              <Spinner size="sm" />
              Exporting...
            </>
          ) : (
            `Export ${formatOptions[selectedFormat].name}`
          )}
        </Button>
      </Flex>
    </Modal>
  )
}

// Share Modal Component
interface ShareModalProps {
  shareOptions: {
    recipients: string[]
    message: string
    expiresAt: string
    allowDownload: boolean
  }
  isSharing: boolean
  onOptionsChange: (options: any) => void
  onShare: () => void
  onClose: () => void
}

const ShareModal: React.FC<ShareModalProps> = ({
  shareOptions,
  isSharing,
  onOptionsChange,
  onShare,
  onClose,
}) => {
  const [emailInput, setEmailInput] = useState('')

  const handleAddRecipient = () => {
    if (emailInput.trim() && !shareOptions.recipients.includes(emailInput.trim())) {
      onOptionsChange({
        ...shareOptions,
        recipients: [...shareOptions.recipients, emailInput.trim()],
      })
      setEmailInput('')
    }
  }

  const handleRemoveRecipient = (email: string) => {
    onOptionsChange({
      ...shareOptions,
      recipients: shareOptions.recipients.filter(r => r !== email),
    })
  }

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Share Report"
      size="md"
    >
      <div style={{ padding: '16px' }}>
        <Flex direction="column" gap="md">
          {/* Recipients */}
          <div>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
              Recipients *
            </label>
            <Flex gap="sm" mb="sm">
              <Input
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                placeholder="Enter email address"
                onKeyPress={(e) => e.key === 'Enter' && handleAddRecipient()}
              />
              <Button variant="outline" onClick={handleAddRecipient}>
                Add
              </Button>
            </Flex>
            {shareOptions.recipients.length > 0 && (
              <div>
                {shareOptions.recipients.map((email) => (
                  <Badge key={email} variant="secondary" style={{ margin: '2px' }}>
                    {email}
                    <button
                      onClick={() => handleRemoveRecipient(email)}
                      style={{ 
                        marginLeft: '8px', 
                        background: 'none', 
                        border: 'none', 
                        cursor: 'pointer' 
                      }}
                    >
                      ×
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Message */}
          <div>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
              Message
            </label>
            <textarea
              value={shareOptions.message}
              onChange={(e) => onOptionsChange({ ...shareOptions, message: e.target.value })}
              placeholder="Add a message (optional)"
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

          {/* Expiration */}
          <div>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>
              Expires At
            </label>
            <Input
              type="datetime-local"
              value={shareOptions.expiresAt}
              onChange={(e) => onOptionsChange({ ...shareOptions, expiresAt: e.target.value })}
            />
          </div>

          {/* Options */}
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="checkbox"
                checked={shareOptions.allowDownload}
                onChange={(e) => onOptionsChange({ ...shareOptions, allowDownload: e.target.checked })}
              />
              <span>Allow recipients to download the report</span>
            </label>
          </div>
        </Flex>
      </div>

      <Flex justify="end" gap="md" style={{ padding: '16px', borderTop: '1px solid #e5e7eb' }}>
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button 
          variant="primary" 
          onClick={onShare}
          disabled={isSharing || shareOptions.recipients.length === 0}
        >
          {isSharing ? (
            <>
              <Spinner size="sm" />
              Sharing...
            </>
          ) : (
            'Share Report'
          )}
        </Button>
      </Flex>
    </Modal>
  )
}

export default ReportExport
