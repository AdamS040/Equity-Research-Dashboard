import React, { useState, useEffect } from 'react'
import { clsx } from 'clsx'
import { 
  Card, 
  CardBody, 
  Button, 
  Spinner 
} from '../ui'
import { 
  ChartBarIcon,
  CogIcon,
  DocumentTextIcon,
  NewspaperIcon,
  TrendingUpIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline'
import { useSearchParams } from 'react-router-dom'

interface AnalysisTabsProps {
  symbol: string
  children: React.ReactNode
  loading?: boolean
}

interface Tab {
  id: string
  label: string
  icon: React.ComponentType<any>
  description: string
}

const TABS: Tab[] = [
  {
    id: 'overview',
    label: 'Overview',
    icon: ChartBarIcon,
    description: 'Price charts and key metrics'
  },
  {
    id: 'technical',
    label: 'Technical',
    icon: TrendingUpIcon,
    description: 'Technical indicators and signals'
  },
  {
    id: 'financial',
    label: 'Financial',
    icon: BuildingOfficeIcon,
    description: 'Financial metrics and ratios'
  },
  {
    id: 'news',
    label: 'News',
    icon: NewspaperIcon,
    description: 'Latest news and sentiment'
  },
  {
    id: 'analysis',
    label: 'Analysis',
    icon: DocumentTextIcon,
    description: 'DCF and comparable analysis'
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: CogIcon,
    description: 'Chart and display preferences'
  }
]

export const AnalysisTabs: React.FC<AnalysisTabsProps> = ({
  symbol,
  children,
  loading = false
}) => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [activeTab, setActiveTab] = useState('overview')

  // Initialize active tab from URL
  useEffect(() => {
    const tabFromUrl = searchParams.get('tab')
    if (tabFromUrl && TABS.some(tab => tab.id === tabFromUrl)) {
      setActiveTab(tabFromUrl)
    }
  }, [searchParams])

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId)
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev)
      newParams.set('tab', tabId)
      return newParams
    })
  }

  const activeTabData = TABS.find(tab => tab.id === activeTab)

  if (loading) {
    return (
      <Card className="mb-6">
        <CardBody className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </CardBody>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <Card>
        <CardBody padding="none">
          <div className="flex flex-col lg:flex-row">
            {/* Desktop Tab Navigation */}
            <div className="hidden lg:flex border-b border-neutral-200">
              {TABS.map((tab) => {
                const Icon = tab.icon
                const isActive = activeTab === tab.id
                
                return (
                  <button
                    key={tab.id}
                    onClick={() => handleTabChange(tab.id)}
                    className={clsx(
                      'flex items-center gap-3 px-6 py-4 text-sm font-medium transition-colors border-b-2',
                      isActive
                        ? 'text-blue-600 border-blue-600 bg-blue-50'
                        : 'text-neutral-600 border-transparent hover:text-neutral-900 hover:bg-neutral-50'
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </button>
                )
              })}
            </div>

            {/* Mobile Tab Navigation */}
            <div className="lg:hidden">
              <select
                value={activeTab}
                onChange={(e) => handleTabChange(e.target.value)}
                className="w-full p-4 border-b border-neutral-200 bg-transparent text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {TABS.map((tab) => (
                  <option key={tab.id} value={tab.id}>
                    {tab.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Tab Content Header */}
      {activeTabData && (
        <Card>
          <CardBody>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <activeTabData.icon className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-neutral-900">
                  {activeTabData.label} Analysis
                </h2>
                <p className="text-neutral-600">
                  {activeTabData.description} for {symbol}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Tab Content */}
      <div className="min-h-96">
        {children}
      </div>

      {/* Tab Footer Navigation */}
      <Card>
        <CardBody>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-neutral-600">
              <span>Quick Navigation:</span>
              <div className="flex gap-1">
                {TABS.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => handleTabChange(tab.id)}
                    className={clsx(
                      'px-2 py-1 rounded text-xs transition-colors',
                      activeTab === tab.id
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100'
                    )}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="flex items-center gap-2 text-sm text-neutral-500">
              <span>Last updated:</span>
              <span>{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

// Tab Content Components
interface TabContentProps {
  symbol: string
  activeTab: string
}

export const TabContent: React.FC<TabContentProps> = ({ symbol, activeTab }) => {
  // This would be replaced with actual component imports
  // For now, we'll show placeholder content
  
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="text-center py-12">
            <ChartBarIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              Overview Analysis
            </h3>
            <p className="text-neutral-600">
              Price charts, key metrics, and market overview for {symbol}
            </p>
          </div>
        )
      
      case 'technical':
        return (
          <div className="text-center py-12">
            <TrendingUpIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              Technical Analysis
            </h3>
            <p className="text-neutral-600">
              RSI, MACD, moving averages, and trading signals for {symbol}
            </p>
          </div>
        )
      
      case 'financial':
        return (
          <div className="text-center py-12">
            <BuildingOfficeIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              Financial Metrics
            </h3>
            <p className="text-neutral-600">
              Profitability, liquidity, leverage, and efficiency ratios for {symbol}
            </p>
          </div>
        )
      
      case 'news':
        return (
          <div className="text-center py-12">
            <NewspaperIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              News & Sentiment
            </h3>
            <p className="text-neutral-600">
              Latest news articles and sentiment analysis for {symbol}
            </p>
          </div>
        )
      
      case 'analysis':
        return (
          <div className="text-center py-12">
            <DocumentTextIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              Advanced Analysis
            </h3>
            <p className="text-neutral-600">
              DCF valuation, comparable analysis, and risk assessment for {symbol}
            </p>
          </div>
        )
      
      case 'settings':
        return (
          <div className="text-center py-12">
            <CogIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              Settings & Preferences
            </h3>
            <p className="text-neutral-600">
              Customize chart settings, display preferences, and analysis parameters for {symbol}
            </p>
          </div>
        )
      
      default:
        return (
          <div className="text-center py-12">
            <ChartBarIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              Select a Tab
            </h3>
            <p className="text-neutral-600">
              Choose an analysis type from the tabs above
            </p>
          </div>
        )
    }
  }

  return (
    <Card>
      <CardBody>
        {renderTabContent()}
      </CardBody>
    </Card>
  )
}
