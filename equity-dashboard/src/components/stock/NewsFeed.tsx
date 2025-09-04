import React, { useState, useMemo } from 'react'
import { clsx } from 'clsx'
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Badge, 
  Spinner,
  Button 
} from '../ui'
import { 
  NewspaperIcon,
  ClockIcon,
  ExternalLinkIcon,
  FunnelIcon,
  CalendarIcon,
  StarIcon,
  ChatBubbleLeftRightIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  MinusIcon
} from '@heroicons/react/24/outline'
import { 
  StarIcon as StarSolidIcon 
} from '@heroicons/react/24/solid'
import { StockNews } from '../../types/api'

interface NewsFeedProps {
  symbol: string
  news: StockNews[]
  loading?: boolean
  onNewsClick?: (news: StockNews) => void
}

interface NewsFilter {
  sentiment: 'all' | 'positive' | 'negative' | 'neutral'
  timeframe: 'all' | 'today' | 'week' | 'month'
  relevance: 'all' | 'high' | 'medium' | 'low'
}

export const NewsFeed: React.FC<NewsFeedProps> = ({
  symbol,
  news,
  loading = false,
  onNewsClick
}) => {
  const [filters, setFilters] = useState<NewsFilter>({
    sentiment: 'all',
    timeframe: 'all',
    relevance: 'all'
  })
  const [expandedNews, setExpandedNews] = useState<string | null>(null)
  const [bookmarkedNews, setBookmarkedNews] = useState<Set<string>>(new Set())

  // Filter and sort news
  const filteredNews = useMemo(() => {
    if (!news || news.length === 0) return []

    let filtered = news.filter(item => {
      // Sentiment filter
      if (filters.sentiment !== 'all' && item.sentiment !== filters.sentiment) {
        return false
      }

      // Timeframe filter
      if (filters.timeframe !== 'all') {
        const newsDate = new Date(item.publishedAt)
        const now = new Date()
        const diffTime = now.getTime() - newsDate.getTime()
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

        switch (filters.timeframe) {
          case 'today':
            if (diffDays > 1) return false
            break
          case 'week':
            if (diffDays > 7) return false
            break
          case 'month':
            if (diffDays > 30) return false
            break
        }
      }

      // Relevance filter
      if (filters.relevance !== 'all') {
        const relevanceThreshold = {
          high: 0.8,
          medium: 0.5,
          low: 0.2
        }[filters.relevance]

        if (item.relevance < relevanceThreshold) return false
      }

      return true
    })

    // Sort by relevance and date
    return filtered.sort((a, b) => {
      // First by relevance (descending)
      if (a.relevance !== b.relevance) {
        return b.relevance - a.relevance
      }
      // Then by date (descending)
      return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
    })
  }, [news, filters])

  // Calculate sentiment statistics
  const sentimentStats = useMemo(() => {
    if (!news || news.length === 0) {
      return { positive: 0, negative: 0, neutral: 0, total: 0 }
    }

    const stats = news.reduce((acc, item) => {
      acc[item.sentiment]++
      acc.total++
      return acc
    }, { positive: 0, negative: 0, neutral: 0, total: 0 })

    return stats
  }, [news])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
    const diffMinutes = Math.floor(diffTime / (1000 * 60))

    if (diffMinutes < 60) {
      return `${diffMinutes}m ago`
    } else if (diffHours < 24) {
      return `${diffHours}h ago`
    } else if (diffDays < 7) {
      return `${diffDays}d ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />
      case 'negative':
        return <ArrowTrendingDownIcon className="w-4 h-4 text-red-500" />
      default:
        return <MinusIcon className="w-4 h-4 text-neutral-500" />
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'success'
      case 'negative':
        return 'danger'
      default:
        return 'neutral'
    }
  }

  const getRelevanceColor = (relevance: number) => {
    if (relevance >= 0.8) return 'success'
    if (relevance >= 0.5) return 'warning'
    return 'neutral'
  }

  const getSourceCredibility = (source: string) => {
    const credibleSources = [
      'Reuters', 'Bloomberg', 'Wall Street Journal', 'Financial Times',
      'CNBC', 'MarketWatch', 'Yahoo Finance', 'Seeking Alpha'
    ]
    
    return credibleSources.some(credible => 
      source.toLowerCase().includes(credible.toLowerCase())
    )
  }

  const toggleBookmark = (newsId: string) => {
    setBookmarkedNews(prev => {
      const newSet = new Set(prev)
      if (newSet.has(newsId)) {
        newSet.delete(newsId)
      } else {
        newSet.add(newsId)
      }
      return newSet
    })
  }

  const toggleExpanded = (newsId: string) => {
    setExpandedNews(prev => prev === newsId ? null : newsId)
  }

  if (loading) {
    return (
      <Card className="mb-6">
        <CardHeader 
          title="News Feed" 
          subtitle={`${symbol} - Loading news...`}
        />
        <CardBody className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </CardBody>
      </Card>
    )
  }

  if (!news || news.length === 0) {
    return (
      <Card className="mb-6">
        <CardHeader 
          title="News Feed" 
          subtitle={`${symbol} - No news available`}
        />
        <CardBody className="flex items-center justify-center py-12">
          <div className="text-center">
            <NewspaperIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <p className="text-neutral-600">No news articles available for this symbol</p>
          </div>
        </CardBody>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* News Overview */}
      <Card>
        <CardHeader 
          title="News Feed" 
          subtitle={`${symbol} - Latest news and sentiment`}
        />
        <CardBody>
          {/* Sentiment Overview */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
              <ArrowTrendingUpIcon className="w-8 h-8 text-green-500 mx-auto mb-2" />
              <h3 className="font-semibold text-green-800 mb-1">Positive</h3>
              <p className="text-2xl font-bold text-green-900">
                {sentimentStats.positive}
              </p>
              <p className="text-xs text-green-700">
                {sentimentStats.total > 0 ? Math.round((sentimentStats.positive / sentimentStats.total) * 100) : 0}%
              </p>
            </div>
            
            <div className="text-center p-4 bg-red-50 rounded-lg border border-red-200">
              <ArrowTrendingDownIcon className="w-8 h-8 text-red-500 mx-auto mb-2" />
              <h3 className="font-semibold text-red-800 mb-1">Negative</h3>
              <p className="text-2xl font-bold text-red-900">
                {sentimentStats.negative}
              </p>
              <p className="text-xs text-red-700">
                {sentimentStats.total > 0 ? Math.round((sentimentStats.negative / sentimentStats.total) * 100) : 0}%
              </p>
            </div>
            
            <div className="text-center p-4 bg-neutral-50 rounded-lg border border-neutral-200">
              <MinusIcon className="w-8 h-8 text-neutral-500 mx-auto mb-2" />
              <h3 className="font-semibold text-neutral-800 mb-1">Neutral</h3>
              <p className="text-2xl font-bold text-neutral-900">
                {sentimentStats.neutral}
              </p>
              <p className="text-xs text-neutral-700">
                {sentimentStats.total > 0 ? Math.round((sentimentStats.neutral / sentimentStats.total) * 100) : 0}%
              </p>
            </div>
            
            <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
              <NewspaperIcon className="w-8 h-8 text-blue-500 mx-auto mb-2" />
              <h3 className="font-semibold text-blue-800 mb-1">Total</h3>
              <p className="text-2xl font-bold text-blue-900">
                {sentimentStats.total}
              </p>
              <p className="text-xs text-blue-700">Articles</p>
            </div>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <div className="flex items-center gap-2">
              <FunnelIcon className="w-4 h-4 text-neutral-500" />
              <span className="text-sm font-medium text-neutral-700">Filters:</span>
            </div>
            
            <select
              value={filters.sentiment}
              onChange={(e) => setFilters(prev => ({ ...prev, sentiment: e.target.value as any }))}
              className="px-3 py-1 border border-neutral-300 rounded-md text-sm"
            >
              <option value="all">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
              <option value="neutral">Neutral</option>
            </select>
            
            <select
              value={filters.timeframe}
              onChange={(e) => setFilters(prev => ({ ...prev, timeframe: e.target.value as any }))}
              className="px-3 py-1 border border-neutral-300 rounded-md text-sm"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
            
            <select
              value={filters.relevance}
              onChange={(e) => setFilters(prev => ({ ...prev, relevance: e.target.value as any }))}
              className="px-3 py-1 border border-neutral-300 rounded-md text-sm"
            >
              <option value="all">All Relevance</option>
              <option value="high">High Relevance</option>
              <option value="medium">Medium Relevance</option>
              <option value="low">Low Relevance</option>
            </select>
          </div>
        </CardBody>
      </Card>

      {/* News Articles */}
      <div className="space-y-4">
        {filteredNews.map((article) => (
          <Card key={article.id} className="hover:shadow-md transition-shadow">
            <CardBody>
              <div className="flex items-start gap-4">
                {/* Sentiment Indicator */}
                <div className="flex-shrink-0 mt-1">
                  {getSentimentIcon(article.sentiment)}
                </div>
                
                {/* Article Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold text-neutral-900 line-clamp-2">
                      {article.title}
                    </h3>
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => toggleBookmark(article.id)}
                        className="p-1 hover:bg-neutral-100 rounded"
                      >
                        {bookmarkedNews.has(article.id) ? (
                          <StarSolidIcon className="w-5 h-5 text-yellow-500" />
                        ) : (
                          <StarIcon className="w-5 h-5 text-neutral-400" />
                        )}
                      </button>
                    </div>
                  </div>
                  
                  <p className="text-neutral-700 mb-3 line-clamp-3">
                    {article.summary}
                  </p>
                  
                  {/* Article Metadata */}
                  <div className="flex items-center gap-4 text-sm text-neutral-600 mb-3">
                    <div className="flex items-center gap-1">
                      <ClockIcon className="w-4 h-4" />
                      <span>{formatDate(article.publishedAt)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <ChatBubbleLeftRightIcon className="w-4 h-4" />
                      <span>{article.source}</span>
                    </div>
                    {getSourceCredibility(article.source) && (
                      <Badge color="success" variant="outline" size="sm">
                        Verified
                      </Badge>
                    )}
                  </div>
                  
                  {/* Tags */}
                  <div className="flex items-center gap-2 mb-3">
                    <Badge 
                      color={getSentimentColor(article.sentiment)} 
                      variant="solid"
                      size="sm"
                    >
                      {article.sentiment}
                    </Badge>
                    <Badge 
                      color={getRelevanceColor(article.relevance)} 
                      variant="outline"
                      size="sm"
                    >
                      {Math.round(article.relevance * 100)}% relevant
                    </Badge>
                  </div>
                  
                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleExpanded(article.id)}
                    >
                      {expandedNews === article.id ? 'Show Less' : 'Read More'}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onNewsClick?.(article)}
                      leftIcon={<ExternalLinkIcon className="w-4 h-4" />}
                    >
                      View Full Article
                    </Button>
                  </div>
                  
                  {/* Expanded Content */}
                  {expandedNews === article.id && (
                    <div className="mt-4 p-4 bg-neutral-50 rounded-lg">
                      <p className="text-neutral-700 whitespace-pre-wrap">
                        {article.content}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>
      
      {filteredNews.length === 0 && (
        <Card>
          <CardBody className="text-center py-12">
            <NewspaperIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <p className="text-neutral-600">No news articles match your current filters</p>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFilters({ sentiment: 'all', timeframe: 'all', relevance: 'all' })}
              className="mt-4"
            >
              Clear Filters
            </Button>
          </CardBody>
        </Card>
      )}
    </div>
  )
}
