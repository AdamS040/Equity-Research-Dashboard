import React from 'react'
import { Card, CardBody, Spinner } from '../ui'
import { 
  ChartBarIcon, 
  TrendingUpIcon, 
  BuildingOfficeIcon, 
  NewspaperIcon 
} from '@heroicons/react/24/outline'

interface StockLoadingStateProps {
  type?: 'header' | 'chart' | 'technical' | 'financial' | 'news' | 'general'
  message?: string
}

export const StockLoadingState: React.FC<StockLoadingStateProps> = ({
  type = 'general',
  message
}) => {
  const getLoadingContent = () => {
    switch (type) {
      case 'header':
        return {
          icon: <ChartBarIcon className="w-12 h-12 text-blue-500" />,
          title: 'Loading Stock Information',
          description: 'Fetching current price and key metrics...'
        }
      
      case 'chart':
        return {
          icon: <ChartBarIcon className="w-12 h-12 text-green-500" />,
          title: 'Loading Price Chart',
          description: 'Preparing historical data and technical indicators...'
        }
      
      case 'technical':
        return {
          icon: <TrendingUpIcon className="w-12 h-12 text-purple-500" />,
          title: 'Loading Technical Analysis',
          description: 'Calculating RSI, MACD, and moving averages...'
        }
      
      case 'financial':
        return {
          icon: <BuildingOfficeIcon className="w-12 h-12 text-orange-500" />,
          title: 'Loading Financial Metrics',
          description: 'Processing profitability and liquidity ratios...'
        }
      
      case 'news':
        return {
          icon: <NewspaperIcon className="w-12 h-12 text-red-500" />,
          title: 'Loading News Feed',
          description: 'Fetching latest articles and sentiment analysis...'
        }
      
      default:
        return {
          icon: <Spinner size="lg" />,
          title: 'Loading...',
          description: message || 'Please wait while we load the data...'
        }
    }
  }

  const content = getLoadingContent()

  return (
    <Card className="mb-6">
      <CardBody>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="mb-4">
              {content.icon}
            </div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              {content.title}
            </h3>
            <p className="text-neutral-600">
              {content.description}
            </p>
          </div>
        </div>
      </CardBody>
    </Card>
  )
}

// Skeleton loading components for different sections
export const StockHeaderSkeleton: React.FC = () => (
  <Card className="mb-6">
    <CardBody>
      <div className="animate-pulse">
        <div className="flex items-start gap-4 mb-4">
          <div className="w-16 h-16 bg-neutral-200 rounded-lg"></div>
          <div className="flex-1">
            <div className="h-6 bg-neutral-200 rounded w-1/4 mb-2"></div>
            <div className="h-4 bg-neutral-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-neutral-200 rounded w-1/3"></div>
          </div>
        </div>
        <div className="h-8 bg-neutral-200 rounded w-1/3 mb-4"></div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-neutral-100 rounded-lg p-3">
              <div className="h-3 bg-neutral-200 rounded w-1/2 mb-1"></div>
              <div className="h-5 bg-neutral-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    </CardBody>
  </Card>
)

export const ChartSkeleton: React.FC = () => (
  <Card className="mb-6">
    <CardBody>
      <div className="animate-pulse">
        <div className="flex justify-between items-center mb-6">
          <div className="h-6 bg-neutral-200 rounded w-1/4"></div>
          <div className="flex gap-2">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-8 bg-neutral-200 rounded w-12"></div>
            ))}
          </div>
        </div>
        <div className="h-96 bg-neutral-100 rounded-lg"></div>
      </div>
    </CardBody>
  </Card>
)

export const MetricsSkeleton: React.FC = () => (
  <Card className="mb-6">
    <CardBody>
      <div className="animate-pulse">
        <div className="h-6 bg-neutral-200 rounded w-1/3 mb-6"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="p-4 bg-neutral-100 rounded-lg">
              <div className="h-4 bg-neutral-200 rounded w-3/4 mb-2"></div>
              <div className="h-6 bg-neutral-200 rounded w-1/2 mb-1"></div>
              <div className="h-3 bg-neutral-200 rounded w-full"></div>
            </div>
          ))}
        </div>
      </div>
    </CardBody>
  </Card>
)

export const NewsSkeleton: React.FC = () => (
  <div className="space-y-4">
    {[...Array(3)].map((_, i) => (
      <Card key={i}>
        <CardBody>
          <div className="animate-pulse">
            <div className="flex items-start gap-4">
              <div className="w-4 h-4 bg-neutral-200 rounded mt-1"></div>
              <div className="flex-1">
                <div className="h-5 bg-neutral-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-neutral-200 rounded w-full mb-1"></div>
                <div className="h-4 bg-neutral-200 rounded w-2/3 mb-3"></div>
                <div className="flex gap-2">
                  <div className="h-6 bg-neutral-200 rounded w-16"></div>
                  <div className="h-6 bg-neutral-200 rounded w-20"></div>
                </div>
              </div>
            </div>
          </div>
        </CardBody>
      </Card>
    ))}
  </div>
)
