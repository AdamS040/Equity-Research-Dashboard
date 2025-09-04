import { useState } from 'react'
import { 
  MagnifyingGlassIcon, 
  DocumentTextIcon, 
  CalendarIcon,
  UserIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline'
import { formatDate } from '../utils'

// Mock research reports data
const mockReports = [
  {
    id: '1',
    title: 'Apple Inc. (AAPL) - Q4 2023 Earnings Analysis',
    author: 'John Smith',
    date: '2023-11-15',
    type: 'Earnings',
    rating: 'Buy',
    targetPrice: 200,
    currentPrice: 175.43,
    summary: 'Strong iPhone sales and services growth drive record revenue. Maintain Buy rating with $200 price target.',
    tags: ['Technology', 'Earnings', 'Large Cap']
  },
  {
    id: '2',
    title: 'Tesla Inc. (TSLA) - EV Market Leadership Analysis',
    author: 'Sarah Johnson',
    date: '2023-11-10',
    type: 'Industry',
    rating: 'Hold',
    targetPrice: 250,
    currentPrice: 248.50,
    summary: 'Tesla maintains EV market leadership but faces increasing competition. Hold rating maintained.',
    tags: ['Automotive', 'EV', 'Growth']
  },
  {
    id: '3',
    title: 'Microsoft Corp. (MSFT) - Cloud Computing Outlook',
    author: 'Michael Chen',
    date: '2023-11-08',
    type: 'Sector',
    rating: 'Strong Buy',
    targetPrice: 420,
    currentPrice: 378.85,
    summary: 'Azure growth accelerates with AI integration. Strong Buy rating with $420 price target.',
    tags: ['Technology', 'Cloud', 'AI']
  },
  {
    id: '4',
    title: 'Johnson & Johnson (JNJ) - Healthcare Sector Analysis',
    author: 'Emily Davis',
    date: '2023-11-05',
    type: 'Sector',
    rating: 'Buy',
    targetPrice: 180,
    currentPrice: 156.00,
    summary: 'Pharmaceutical division shows strong pipeline. Buy rating with $180 price target.',
    tags: ['Healthcare', 'Pharmaceutical', 'Dividend']
  }
]

const reportTypes = ['All', 'Earnings', 'Industry', 'Sector', 'Company']
const ratings = ['All', 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell']

export const Research = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('All')
  const [selectedRating, setSelectedRating] = useState('All')

  const filteredReports = mockReports.filter(report => {
    const matchesSearch = report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         report.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         report.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesType = selectedType === 'All' || report.type === selectedType
    const matchesRating = selectedRating === 'All' || report.rating === selectedRating
    
    return matchesSearch && matchesType && matchesRating
  })

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'Strong Buy': return 'bg-success-100 text-success-800'
      case 'Buy': return 'bg-primary-100 text-primary-800'
      case 'Hold': return 'bg-warning-100 text-warning-800'
      case 'Sell': return 'bg-danger-100 text-danger-800'
      case 'Strong Sell': return 'bg-danger-100 text-danger-800'
      default: return 'bg-neutral-100 text-neutral-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Research Reports</h1>
        <p className="text-neutral-600">Access comprehensive equity research and analysis reports.</p>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          {/* Search */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-400" />
              <input
                type="text"
                placeholder="Search reports..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filters */}
          <div className="flex space-x-4">
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {reportTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            
            <select
              value={selectedRating}
              onChange={(e) => setSelectedRating(e.target.value)}
              className="px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {ratings.map(rating => (
                <option key={rating} value={rating}>{rating}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredReports.map((report) => (
          <div key={report.id} className="card hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-neutral-900 mb-2 line-clamp-2">
                  {report.title}
                </h3>
                <div className="flex items-center space-x-4 text-sm text-neutral-600 mb-3">
                  <div className="flex items-center space-x-1">
                    <UserIcon className="w-4 h-4" />
                    <span>{report.author}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <CalendarIcon className="w-4 h-4" />
                    <span>{formatDate(report.date)}</span>
                  </div>
                </div>
              </div>
              <button className="p-2 text-neutral-400 hover:text-neutral-600">
                <ArrowDownTrayIcon className="w-5 h-5" />
              </button>
            </div>

            <p className="text-neutral-600 mb-4 line-clamp-3">{report.summary}</p>

            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-neutral-600">Rating:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRatingColor(report.rating)}`}>
                  {report.rating}
                </span>
              </div>
              <div className="text-right">
                <div className="text-sm text-neutral-600">Target Price</div>
                <div className="font-semibold text-neutral-900">${report.targetPrice}</div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex flex-wrap gap-1">
                {report.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-neutral-100 text-neutral-600 text-xs rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              <button className="btn-primary text-sm">
                Read Report
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* No Results */}
      {filteredReports.length === 0 && (
        <div className="card text-center py-12">
          <DocumentTextIcon className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-neutral-900 mb-2">No reports found</h3>
          <p className="text-neutral-600">Try adjusting your search criteria or filters.</p>
        </div>
      )}
    </div>
  )
}
