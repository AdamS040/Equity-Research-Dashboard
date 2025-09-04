import React, { useState, useEffect } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { 
  Container, 
  ErrorDisplay, 
  Spinner 
} from '../components/ui'
import { 
  StockHeader, 
  PriceChart, 
  TechnicalAnalysis, 
  FinancialMetrics, 
  NewsFeed 
} from '../components/stock'
import { AnalysisTabs } from '../components/stock/AnalysisTabs'
import { 
  useStock, 
  useStockQuote, 
  useHistoricalData, 
  useFinancialMetrics, 
  useStockNews,
  useTechnicalIndicators 
} from '../hooks/api/useStocks'

export const StockAnalysis: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('overview')

  // Initialize active tab from URL
  useEffect(() => {
    const tabFromUrl = searchParams.get('tab')
    if (tabFromUrl) {
      setActiveTab(tabFromUrl)
    }
  }, [searchParams])

  // Fetch stock data
  const { 
    data: stock, 
    isLoading: stockLoading, 
    error: stockError 
  } = useStock(symbol || '', !!symbol)

  const { 
    data: quote, 
    isLoading: quoteLoading, 
    error: quoteError 
  } = useStockQuote(symbol || '', !!symbol)

  const { 
    data: historicalData, 
    isLoading: historicalLoading, 
    error: historicalError 
  } = useHistoricalData(symbol || '', '1y', '1d', !!symbol)

  const { 
    data: financialMetrics, 
    isLoading: financialLoading, 
    error: financialError 
  } = useFinancialMetrics(symbol || '', 'annual', !!symbol)

  const { 
    data: news, 
    isLoading: newsLoading, 
    error: newsError 
  } = useStockNews(symbol || '', {}, !!symbol)

  const { 
    data: technicalIndicators, 
    isLoading: technicalLoading, 
    error: technicalError 
  } = useTechnicalIndicators(symbol || '', ['sma', 'ema', 'rsi', 'macd'], !!symbol)

  // Handle errors
  const hasError = stockError || quoteError || historicalError || financialError || newsError || technicalError
  const isLoading = stockLoading || quoteLoading || historicalLoading || financialLoading || newsLoading || technicalLoading

  // Handle share functionality
  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `${symbol} Stock Analysis`,
        text: `Check out the stock analysis for ${symbol}`,
        url: window.location.href
      })
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href)
      // You could show a toast notification here
    }
  }

  // Handle export functionality
  const handleExport = () => {
    // Implement export functionality
    console.log('Export data for', symbol)
  }

  // Handle news click
  const handleNewsClick = (news: any) => {
    window.open(news.url, '_blank')
  }

  // Handle timeframe change
  const handleTimeframeChange = (timeframe: string) => {
    console.log('Timeframe changed to:', timeframe)
    // This would trigger a new data fetch with the selected timeframe
  }

  if (!symbol) {
    return (
      <Container>
        <ErrorDisplay
          title="Invalid Symbol"
          message="No stock symbol provided in the URL"
          action={{
            label: 'Go to Dashboard',
            onClick: () => navigate('/dashboard')
          }}
        />
      </Container>
    )
  }

  if (hasError) {
    return (
      <Container>
        <ErrorDisplay
          title="Error Loading Stock Data"
          message="Failed to load stock information. Please try again later."
          action={{
            label: 'Retry',
            onClick: () => window.location.reload()
          }}
        />
      </Container>
    )
  }

  if (isLoading) {
    return (
      <Container>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <Spinner size="lg" />
            <p className="mt-4 text-neutral-600">Loading stock analysis for {symbol}...</p>
          </div>
        </div>
      </Container>
    )
  }

  if (!stock || !quote) {
    return (
      <Container>
        <ErrorDisplay
          title="Stock Not Found"
          message={`No data available for symbol: ${symbol}`}
          action={{
            label: 'Go to Dashboard',
            onClick: () => navigate('/dashboard')
          }}
        />
      </Container>
    )
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-6">
            <PriceChart
              symbol={symbol}
              data={historicalData || []}
              loading={historicalLoading}
              onTimeframeChange={handleTimeframeChange}
            />
          </div>
        )
      
      case 'technical':
        return (
          <TechnicalAnalysis
            symbol={symbol}
            data={historicalData || []}
            loading={technicalLoading}
          />
        )
      
      case 'financial':
        return (
          <FinancialMetrics
            symbol={symbol}
            data={financialMetrics || []}
            loading={financialLoading}
          />
        )
      
      case 'news':
        return (
          <NewsFeed
            symbol={symbol}
            news={news?.data || []}
            loading={newsLoading}
            onNewsClick={handleNewsClick}
          />
        )
      
      case 'analysis':
        return (
          <div className="text-center py-12">
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              Advanced Analysis
            </h3>
            <p className="text-neutral-600">
              DCF valuation, comparable analysis, and risk assessment features coming soon.
            </p>
          </div>
        )
      
      case 'settings':
        return (
          <div className="text-center py-12">
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              Settings & Preferences
            </h3>
            <p className="text-neutral-600">
              Chart settings and display preferences coming soon.
            </p>
          </div>
        )
      
      default:
        return (
          <div className="text-center py-12">
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              Select a Tab
            </h3>
            <p className="text-neutral-600">
              Choose an analysis type from the tabs above.
            </p>
          </div>
        )
    }
  }

  return (
    <Container>
      <div className="space-y-6">
        {/* Stock Header */}
        <StockHeader
          stock={stock}
          quote={quote}
          loading={stockLoading || quoteLoading}
          onShare={handleShare}
          onExport={handleExport}
        />

        {/* Analysis Tabs */}
        <AnalysisTabs
          symbol={symbol}
          loading={isLoading}
        >
          {renderTabContent()}
        </AnalysisTabs>
      </div>
    </Container>
  )
}
