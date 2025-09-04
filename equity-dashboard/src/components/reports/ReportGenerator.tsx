/**
 * Report Generator Component
 * 
 * Automated data collection, chart generation, and analysis
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react'
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
  Container,
  Progress
} from '../ui'
import { 
  ReportGenerator as ReportGeneratorType,
  GenerationStep,
  DataSource,
  GenerationResults,
  GeneratedSection,
  GeneratedChart,
  GeneratedTable,
  GeneratedSummary,
  Citation
} from '../../types/reports'
import { contentUtils } from '../../utils/reports'
import { useGenerateReport, useReport } from '../../hooks/api/useReports'

interface ReportGeneratorProps {
  reportId: string
  parameters: Record<string, any>
  onComplete?: (results: GenerationResults) => void
  onError?: (error: string) => void
  autoStart?: boolean
}

export const ReportGenerator: React.FC<ReportGeneratorProps> = ({
  reportId,
  parameters,
  onComplete,
  onError,
  autoStart = false,
}) => {
  const [generator, setGenerator] = useState<ReportGeneratorType | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [currentStep, setCurrentStep] = useState<string>('')
  const [progress, setProgress] = useState(0)
  const [showDetails, setShowDetails] = useState(false)
  const [dataSources, setDataSources] = useState<DataSource[]>([])
  const [results, setResults] = useState<GenerationResults | null>(null)

  // API hooks
  const { data: report } = useReport(reportId)
  const generateReportMutation = useGenerateReport()

  // Initialize generator
  useEffect(() => {
    if (report) {
      const initialGenerator: ReportGeneratorType = {
        id: `gen-${Date.now()}`,
        reportId,
        status: 'pending',
        progress: 0,
        currentStep: 'Initializing...',
        steps: [
          {
            id: 'validate-parameters',
            name: 'Validate Parameters',
            description: 'Validate input parameters and requirements',
            status: 'pending',
            progress: 0,
          },
          {
            id: 'connect-data-sources',
            name: 'Connect Data Sources',
            description: 'Establish connections to data providers',
            status: 'pending',
            progress: 0,
          },
          {
            id: 'collect-data',
            name: 'Collect Data',
            description: 'Fetch and process data from various sources',
            status: 'pending',
            progress: 0,
          },
          {
            id: 'generate-analysis',
            name: 'Generate Analysis',
            description: 'Perform financial analysis and calculations',
            status: 'pending',
            progress: 0,
          },
          {
            id: 'create-charts',
            name: 'Create Charts',
            description: 'Generate visualizations and charts',
            status: 'pending',
            progress: 0,
          },
          {
            id: 'generate-content',
            name: 'Generate Content',
            description: 'Create report sections and summaries',
            status: 'pending',
            progress: 0,
          },
          {
            id: 'validate-results',
            name: 'Validate Results',
            description: 'Validate generated content and data',
            status: 'pending',
            progress: 0,
          },
          {
            id: 'finalize-report',
            name: 'Finalize Report',
            description: 'Compile final report and citations',
            status: 'pending',
            progress: 0,
          },
        ],
        dataSources: [],
        parameters,
        startedAt: new Date().toISOString(),
        results: {
          sections: [],
          charts: [],
          tables: [],
          summary: {
            executive: '',
            keyFindings: [],
            recommendations: [],
            risks: [],
            opportunities: [],
            confidence: 0,
          },
          metadata: {
            generatedAt: new Date().toISOString(),
            dataAsOf: new Date().toISOString(),
            sources: [],
            methodology: '',
            assumptions: [],
            disclaimers: [],
          },
          citations: [],
          warnings: [],
          errors: [],
        },
      }

      setGenerator(initialGenerator)
      setDataSources(initialGenerator.dataSources)

      if (autoStart) {
        startGeneration(initialGenerator)
      }
    }
  }, [report, reportId, parameters, autoStart])

  // Start generation process
  const startGeneration = useCallback(async (gen: ReportGeneratorType) => {
    setIsRunning(true)
    setGenerator({ ...gen, status: 'running', startedAt: new Date().toISOString() })

    try {
      // Simulate generation process
      await simulateGenerationProcess(gen)
    } catch (error) {
      console.error('Generation failed:', error)
      setGenerator(prev => prev ? { ...prev, status: 'failed', error: error.message } : null)
      setIsRunning(false)
      if (onError) {
        onError(error.message)
      }
    }
  }, [onError])

  // Simulate generation process
  const simulateGenerationProcess = async (gen: ReportGeneratorType) => {
    const steps = [...gen.steps]
    let currentProgress = 0

    for (let i = 0; i < steps.length; i++) {
      const step = steps[i]
      
      // Update current step
      setCurrentStep(step.name)
      setProgress((i / steps.length) * 100)

      // Update step status
      steps[i] = { ...step, status: 'running', startedAt: new Date().toISOString() }
      setGenerator(prev => prev ? { 
        ...prev, 
        currentStep: step.name,
        progress: (i / steps.length) * 100,
        steps: [...steps]
      } : null)

      // Simulate step execution
      await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000))

      // Update step completion
      steps[i] = { 
        ...step, 
        status: 'completed', 
        progress: 100,
        completedAt: new Date().toISOString(),
        duration: 2000 + Math.random() * 3000
      }

      // Update data sources if this is the data collection step
      if (step.id === 'collect-data') {
        const newDataSources = await generateDataSources(parameters)
        setDataSources(newDataSources)
      }

      // Update results if this is content generation
      if (step.id === 'generate-content') {
        const newResults = await generateReportContent(parameters, dataSources)
        setResults(newResults)
      }

      setGenerator(prev => prev ? { 
        ...prev, 
        progress: ((i + 1) / steps.length) * 100,
        steps: [...steps]
      } : null)
    }

    // Complete generation
    const finalResults = await generateReportContent(parameters, dataSources)
    setResults(finalResults)
    setGenerator(prev => prev ? { 
      ...prev, 
      status: 'completed',
      progress: 100,
      completedAt: new Date().toISOString(),
      results: finalResults
    } : null)
    setIsRunning(false)

    if (onComplete) {
      onComplete(finalResults)
    }
  }

  // Generate data sources
  const generateDataSources = async (params: Record<string, any>): Promise<DataSource[]> => {
    const sources: DataSource[] = [
      {
        id: 'market-data',
        name: 'Market Data',
        type: 'api',
        endpoint: 'https://api.marketdata.com/quote',
        parameters: { symbol: params.symbol },
        status: 'connected',
        lastUpdated: new Date().toISOString(),
        data: {
          price: 150.25,
          change: 2.35,
          changePercent: 1.58,
          volume: 1250000,
        },
      },
      {
        id: 'financial-data',
        name: 'Financial Statements',
        type: 'api',
        endpoint: 'https://api.financialdata.com/statements',
        parameters: { symbol: params.symbol },
        status: 'connected',
        lastUpdated: new Date().toISOString(),
        data: {
          revenue: 5000000000,
          netIncome: 750000000,
          totalAssets: 25000000000,
        },
      },
      {
        id: 'news-data',
        name: 'News & Sentiment',
        type: 'api',
        endpoint: 'https://api.newsdata.com/sentiment',
        parameters: { symbol: params.symbol },
        status: 'connected',
        lastUpdated: new Date().toISOString(),
        data: {
          sentiment: 'positive',
          newsCount: 15,
          averageScore: 0.75,
        },
      },
    ]

    return sources
  }

  // Generate report content
  const generateReportContent = async (params: Record<string, any>, sources: DataSource[]): Promise<GenerationResults> => {
    const sections: GeneratedSection[] = [
      {
        id: 'executive-summary',
        title: 'Executive Summary',
        content: contentUtils.generateExecutiveSummary({
          symbol: params.symbol,
          rating: 'buy',
          targetPrice: 165.00,
          keyStrengths: ['Strong revenue growth', 'Market leadership'],
          keyRisks: ['Competition', 'Market volatility'],
        }),
        type: 'executive_summary',
        citations: ['market-data', 'financial-data'],
      },
      {
        id: 'financial-analysis',
        title: 'Financial Analysis',
        content: 'Based on the latest financial statements, the company shows strong fundamentals with revenue growth of 12% year-over-year and improving margins.',
        type: 'analysis',
        citations: ['financial-data'],
      },
    ]

    const charts: GeneratedChart[] = [
      {
        id: 'price-chart',
        title: 'Price Performance',
        type: 'candlestick',
        data: {
          dates: ['2024-01-01', '2024-02-01', '2024-03-01'],
          prices: [145, 150, 155],
        },
        config: {},
        citations: ['market-data'],
      },
      {
        id: 'financial-metrics',
        title: 'Key Financial Metrics',
        type: 'bar',
        data: {
          metrics: ['Revenue', 'Net Income', 'ROE'],
          values: [5000, 750, 15.2],
        },
        config: {},
        citations: ['financial-data'],
      },
    ]

    const tables: GeneratedTable[] = [
      {
        id: 'financial-statements',
        title: 'Financial Statements Summary',
        data: {
          headers: ['Metric', '2023', '2022', 'Change'],
          rows: [
            ['Revenue', '$5.0B', '$4.5B', '+11.1%'],
            ['Net Income', '$750M', '$650M', '+15.4%'],
            ['EPS', '$3.25', '$2.85', '+14.0%'],
          ],
        },
        config: {},
        citations: ['financial-data'],
      },
    ]

    const summary: GeneratedSummary = {
      executive: contentUtils.generateExecutiveSummary({
        symbol: params.symbol,
        rating: 'buy',
        targetPrice: 165.00,
        keyStrengths: ['Strong revenue growth', 'Market leadership'],
        keyRisks: ['Competition', 'Market volatility'],
      }),
      keyFindings: contentUtils.generateKeyFindings({
        revenueGrowth: 12,
        operatingMargin: 18.5,
        debtToEquity: 0.3,
        roe: 15.2,
      }),
      recommendations: contentUtils.generateRecommendations({
        rating: 'buy',
      }),
      risks: ['Market volatility', 'Competitive pressure', 'Regulatory changes'],
      opportunities: ['Market expansion', 'Product innovation', 'Strategic partnerships'],
      targetPrice: 165.00,
      rating: 'buy',
      confidence: 85,
    }

    const citations: Citation[] = contentUtils.generateCitations([
      'Market Data API',
      'Financial Statements API',
      'News & Sentiment API',
    ])

    return {
      sections,
      charts,
      tables,
      summary,
      metadata: {
        generatedAt: new Date().toISOString(),
        dataAsOf: new Date().toISOString(),
        sources: sources.map(s => s.name),
        methodology: 'DCF Analysis with comparable company analysis',
        assumptions: [
          'Revenue growth rate of 8-12%',
          'Operating margin improvement to 20%',
          'Discount rate of 10%',
        ],
        disclaimers: [
          'This analysis is for informational purposes only',
          'Past performance does not guarantee future results',
          'Investment decisions should be based on individual circumstances',
        ],
      },
      citations,
      warnings: [
        'Limited historical data available',
        'Market conditions may change rapidly',
      ],
      errors: [],
    }
  }

  // Handle manual start
  const handleStartGeneration = useCallback(() => {
    if (generator) {
      startGeneration(generator)
    }
  }, [generator, startGeneration])

  // Handle stop generation
  const handleStopGeneration = useCallback(() => {
    setIsRunning(false)
    setGenerator(prev => prev ? { ...prev, status: 'failed', error: 'Generation stopped by user' } : null)
  }, [])

  if (!generator) {
    return (
      <Container>
        <Card>
          <CardBody>
            <Flex justify="center" align="center" style={{ height: '200px' }}>
              <Spinner size="lg" />
            </Flex>
          </CardBody>
        </Card>
      </Container>
    )
  }

  return (
    <Container>
      {/* Header */}
      <Card mb="lg">
        <CardBody>
          <Flex justify="between" align="center">
            <div>
              <Heading level={2}>Report Generation</Heading>
              <Text color="gray" size="sm">
                Generating report for {parameters.symbol || 'selected security'}
              </Text>
            </div>
            <Flex gap="md" align="center">
              <Badge 
                variant={
                  generator.status === 'completed' ? 'success' :
                  generator.status === 'failed' ? 'error' :
                  generator.status === 'running' ? 'primary' : 'secondary'
                }
              >
                {generator.status}
              </Badge>
              {!isRunning && generator.status === 'pending' && (
                <Button variant="primary" onClick={handleStartGeneration}>
                  Start Generation
                </Button>
              )}
              {isRunning && (
                <Button variant="outline" onClick={handleStopGeneration}>
                  Stop Generation
                </Button>
              )}
            </Flex>
          </Flex>
        </CardBody>
      </Card>

      {/* Progress Overview */}
      <Card mb="lg">
        <CardHeader>
          <Flex justify="between" align="center">
            <Heading level={4}>Generation Progress</Heading>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDetails(!showDetails)}
            >
              {showDetails ? 'Hide' : 'Show'} Details
            </Button>
          </Flex>
        </CardHeader>
        <CardBody>
          <Flex direction="column" gap="md">
            <div>
              <Flex justify="between" align="center" mb="xs">
                <Text weight="medium">{currentStep}</Text>
                <Text size="sm" color="gray">{Math.round(progress)}%</Text>
              </Flex>
              <Progress value={progress} max={100} />
            </div>

            {generator.status === 'completed' && (
              <Flex gap="md" align="center">
                <Badge variant="success">✓ Generation Complete</Badge>
                <Text size="sm" color="gray">
                  Completed in {generator.completedAt && generator.startedAt ? 
                    Math.round((new Date(generator.completedAt).getTime() - new Date(generator.startedAt).getTime()) / 1000) : 0}s
                </Text>
              </Flex>
            )}

            {generator.status === 'failed' && (
              <Flex gap="md" align="center">
                <Badge variant="error">✗ Generation Failed</Badge>
                <Text size="sm" color="red">{generator.error}</Text>
              </Flex>
            )}
          </Flex>
        </CardBody>
      </Card>

      {/* Detailed Steps */}
      {showDetails && (
        <Card mb="lg">
          <CardHeader>
            <Heading level={4}>Generation Steps</Heading>
          </CardHeader>
          <CardBody>
            <div>
              {generator.steps.map((step, index) => (
                <StepCard key={step.id} step={step} index={index} />
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Data Sources */}
      {dataSources.length > 0 && (
        <Card mb="lg">
          <CardHeader>
            <Heading level={4}>Data Sources</Heading>
          </CardHeader>
          <CardBody>
            <Grid columns={3} gap="md">
              {dataSources.map((source) => (
                <GridItem key={source.id}>
                  <DataSourceCard source={source} />
                </GridItem>
              ))}
            </Grid>
          </CardBody>
        </Card>
      )}

      {/* Results Preview */}
      {results && (
        <Card mb="lg">
          <CardHeader>
            <Heading level={4}>Generated Content Preview</Heading>
          </CardHeader>
          <CardBody>
            <Grid columns={2} gap="lg">
              <GridItem>
                <div>
                  <Heading level={5} mb="sm">Sections ({results.sections.length})</Heading>
                  {results.sections.map((section) => (
                    <div key={section.id} style={{ 
                      padding: '8px', 
                      border: '1px solid #e5e7eb', 
                      borderRadius: '4px',
                      marginBottom: '8px'
                    }}>
                      <Text weight="medium">{section.title}</Text>
                      <Text size="sm" color="gray">{section.type}</Text>
                    </div>
                  ))}
                </div>
              </GridItem>
              <GridItem>
                <div>
                  <Heading level={5} mb="sm">Charts ({results.charts.length})</Heading>
                  {results.charts.map((chart) => (
                    <div key={chart.id} style={{ 
                      padding: '8px', 
                      border: '1px solid #e5e7eb', 
                      borderRadius: '4px',
                      marginBottom: '8px'
                    }}>
                      <Text weight="medium">{chart.title}</Text>
                      <Text size="sm" color="gray">{chart.type} chart</Text>
                    </div>
                  ))}
                </div>
              </GridItem>
            </Grid>

            {/* Executive Summary Preview */}
            {results.summary.executive && (
              <div style={{ marginTop: '16px' }}>
                <Heading level={5} mb="sm">Executive Summary</Heading>
                <div style={{ 
                  padding: '12px', 
                  backgroundColor: '#f9fafb', 
                  border: '1px solid #e5e7eb', 
                  borderRadius: '4px'
                }}>
                  <Text>{results.summary.executive}</Text>
                </div>
              </div>
            )}

            {/* Key Findings */}
            {results.summary.keyFindings.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <Heading level={5} mb="sm">Key Findings</Heading>
                <ul style={{ paddingLeft: '20px' }}>
                  {results.summary.keyFindings.map((finding, index) => (
                    <li key={index} style={{ marginBottom: '4px' }}>
                      <Text>{finding}</Text>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendations */}
            {results.summary.recommendations.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <Heading level={5} mb="sm">Recommendations</Heading>
                <ul style={{ paddingLeft: '20px' }}>
                  {results.summary.recommendations.map((rec, index) => (
                    <li key={index} style={{ marginBottom: '4px' }}>
                      <Text>{rec}</Text>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Warnings */}
            {results.warnings.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <Heading level={5} mb="sm">Warnings</Heading>
                <div style={{ 
                  padding: '12px', 
                  backgroundColor: '#fef3c7', 
                  border: '1px solid #f59e0b', 
                  borderRadius: '4px'
                }}>
                  {results.warnings.map((warning, index) => (
                    <Text key={index} color="orange">⚠️ {warning}</Text>
                  ))}
                </div>
              </div>
            )}

            {/* Citations */}
            {results.citations.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <Heading level={5} mb="sm">Data Sources & Citations</Heading>
                <div style={{ 
                  padding: '12px', 
                  backgroundColor: '#f9fafb', 
                  border: '1px solid #e5e7eb', 
                  borderRadius: '4px'
                }}>
                  {results.citations.map((citation, index) => (
                    <div key={index} style={{ marginBottom: '4px' }}>
                      <Text size="sm">
                        {index + 1}. {citation.source} - {citation.date}
                      </Text>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardBody>
        </Card>
      )}
    </Container>
  )
}

// Step Card Component
interface StepCardProps {
  step: GenerationStep
  index: number
}

const StepCard: React.FC<StepCardProps> = ({ step, index }) => {
  const getStatusIcon = () => {
    switch (step.status) {
      case 'completed':
        return '✓'
      case 'running':
        return <Spinner size="sm" />
      case 'failed':
        return '✗'
      default:
        return '○'
    }
  }

  const getStatusColor = () => {
    switch (step.status) {
      case 'completed':
        return 'green'
      case 'running':
        return 'blue'
      case 'failed':
        return 'red'
      default:
        return 'gray'
    }
  }

  return (
    <div style={{ 
      padding: '12px', 
      border: '1px solid #e5e7eb', 
      borderRadius: '4px',
      marginBottom: '8px',
      backgroundColor: step.status === 'running' ? '#f0f9ff' : 'white'
    }}>
      <Flex justify="between" align="center">
        <Flex align="center" gap="md">
          <div style={{ 
            width: '24px', 
            height: '24px', 
            borderRadius: '50%', 
            backgroundColor: getStatusColor() === 'green' ? '#10b981' : 
                           getStatusColor() === 'blue' ? '#3b82f6' : 
                           getStatusColor() === 'red' ? '#ef4444' : '#6b7280',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '12px'
          }}>
            {getStatusIcon()}
          </div>
          <div>
            <Text weight="medium">{index + 1}. {step.name}</Text>
            <Text size="sm" color="gray">{step.description}</Text>
          </div>
        </Flex>
        <div style={{ textAlign: 'right' }}>
          {step.status === 'running' && (
            <Progress value={step.progress} max={100} size="sm" />
          )}
          {step.duration && (
            <Text size="sm" color="gray">
              {Math.round(step.duration / 1000)}s
            </Text>
          )}
        </div>
      </Flex>
    </div>
  )
}

// Data Source Card Component
interface DataSourceCardProps {
  source: DataSource
}

const DataSourceCard: React.FC<DataSourceCardProps> = ({ source }) => {
  return (
    <Card>
      <CardHeader>
        <Flex justify="between" align="center">
          <Heading level={5}>{source.name}</Heading>
          <Badge 
            variant={source.status === 'connected' ? 'success' : 
                    source.status === 'error' ? 'error' : 'secondary'}
          >
            {source.status}
          </Badge>
        </Flex>
      </CardHeader>
      <CardBody>
        <Flex direction="column" gap="xs">
          <Text size="sm" color="gray">Type: {source.type}</Text>
          {source.endpoint && (
            <Text size="sm" color="gray">Endpoint: {source.endpoint}</Text>
          )}
          {source.lastUpdated && (
            <Text size="sm" color="gray">
              Updated: {new Date(source.lastUpdated).toLocaleTimeString()}
            </Text>
          )}
          {source.data && (
            <div style={{ 
              marginTop: '8px', 
              padding: '8px', 
              backgroundColor: '#f9fafb', 
              borderRadius: '4px' 
            }}>
              <Text size="sm" weight="medium">Sample Data:</Text>
              <pre style={{ 
                fontSize: '12px', 
                margin: '4px 0 0 0', 
                color: '#6b7280',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}>
                {JSON.stringify(source.data, null, 2).substring(0, 100)}...
              </pre>
            </div>
          )}
        </Flex>
      </CardBody>
    </Card>
  )
}

export default ReportGenerator
