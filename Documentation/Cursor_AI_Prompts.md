# Cursor AI Implementation Prompts - UI Redesign

## Overview
This document contains all the prompts needed to implement the UI redesign plan using Cursor AI. Each prompt is optimized for maximum Cursor performance and includes specific context, requirements, and expected outputs.

**Important**: Execute these prompts in order, as each builds upon the previous work.

---

## Phase 1: Foundation Setup (Week 1-2)

### Prompt 1.1: Project Initialization and Setup
```
Create a new React TypeScript project for an equity research dashboard with the following requirements:

1. Initialize a Vite React TypeScript project named "equity-dashboard"
2. Install these core dependencies:
   - zustand (state management)
   - @tanstack/react-query (server state)
   - tailwindcss (styling)
   - @headlessui/react (UI components)
   - recharts (charts)
   - d3 (data visualization)
   - framer-motion (animations)
   - react-router-dom (routing)
   - @heroicons/react (icons)
   - clsx (conditional classes)

3. Configure Tailwind CSS with a custom design system:
   - Primary colors: blue palette (#eff6ff to #1e3a8a)
   - Success colors: green palette (#10b981, #059669)
   - Warning colors: orange palette (#f59e0b, #d97706)
   - Danger colors: red palette (#ef4444, #dc2626)
   - Neutral grays: (#f9fafb to #111827)

4. Set up the project structure:
   - src/components/ (reusable components)
   - src/pages/ (page components)
   - src/hooks/ (custom hooks)
   - src/services/ (API services)
   - src/types/ (TypeScript types)
   - src/utils/ (utility functions)
   - src/store/ (Zustand stores)

5. Configure ESLint and Prettier for code quality
6. Set up React Query client with default options
7. Create a basic App.tsx with routing setup

Provide the complete setup commands and initial file structure.
```

### Prompt 1.2: Design System Implementation
```
Create a comprehensive design system for the equity research dashboard with the following components:

1. **Base Components** (in src/components/ui/):
   - Button: Primary, secondary, outline, ghost variants with loading states
   - Input: Text, number, search variants with validation states
   - Card: Container with header, body, footer sections
   - Badge: Status indicators with color variants
   - Spinner: Loading indicators in different sizes
   - Modal: Accessible modal with backdrop and close functionality

2. **Typography System**:
   - Configure Inter font as primary font
   - JetBrains Mono for financial data
   - Define text size scale (xs, sm, base, lg, xl, 2xl, 3xl, 4xl)
   - Define font weight scale (normal, medium, semibold, bold)

3. **Layout Components**:
   - Container: Responsive container with max-width
   - Grid: 12-column responsive grid system
   - Flex: Common flex layouts (row, column, center, between)

4. **Color System**:
   - Define CSS custom properties for all colors
   - Create utility classes for text and background colors
   - Include hover and focus states

5. **Spacing System**:
   - 4px base unit spacing scale
   - Margin and padding utilities
   - Gap utilities for flexbox and grid

Create TypeScript interfaces for all component props and include comprehensive JSDoc comments.
```

### Prompt 1.3: Backend API Development
```
Convert the existing Flask/Dash backend to a RESTful API with the following requirements:

1. **API Structure** (create in src/services/api/):
   - Base API client with error handling and request/response interceptors
   - Authentication service with JWT token management
   - Stock data service for market data, charts, and analysis
   - Portfolio service for holdings and optimization
   - Reports service for generating and managing reports

2. **TypeScript Types** (in src/types/):
   - Stock data interfaces (price, metrics, charts, news)
   - Portfolio interfaces (holdings, performance, risk metrics)
   - API response wrappers with error handling
   - User and authentication types

3. **React Query Integration**:
   - Custom hooks for each API endpoint
   - Proper caching strategies (30s for real-time, 5min for historical)
   - Background refetching and stale-while-revalidate patterns
   - Optimistic updates for user actions

4. **Error Handling**:
   - Global error boundary component
   - API error types and handling
   - User-friendly error messages
   - Retry mechanisms for failed requests

5. **Authentication Flow**:
   - Login/logout functionality
   - Token refresh mechanism
   - Protected route wrapper
   - User session management

Include comprehensive error handling and loading states for all API calls.
```

---

## Phase 2: Core Features Migration (Week 3-4)

### Prompt 2.1: Dashboard Layout and Navigation
```
Create the main dashboard layout with professional navigation:

1. **Layout Structure**:
   - Sidebar navigation with collapsible functionality
   - Top header with user menu and search
   - Main content area with proper spacing
   - Responsive design for mobile/tablet

2. **Sidebar Navigation** (src/components/layout/Sidebar.tsx):
   - Dashboard icon and link
   - Stock Analysis icon and link
   - Portfolio icon and link
   - Reports icon and link
   - Settings icon and link
   - Collapse/expand functionality
   - Active state indicators
   - Smooth animations with Framer Motion

3. **Header Component** (src/components/layout/Header.tsx):
   - Stock symbol search with autocomplete
   - Theme toggle (light/dark mode)
   - User profile dropdown
   - Notifications indicator
   - Breadcrumb navigation

4. **Routing Setup**:
   - React Router configuration
   - Protected routes with authentication
   - Lazy loading for page components
   - Route-based code splitting

5. **Responsive Behavior**:
   - Mobile hamburger menu
   - Touch-friendly interactions
   - Proper viewport handling
   - Sidebar overlay on mobile

Use Tailwind CSS for styling and ensure accessibility compliance (WCAG 2.1 AA).
```

### Prompt 2.2: Market Overview Dashboard
```
Create the market overview dashboard with real-time data:

1. **Market Indices Cards** (src/components/dashboard/MarketIndices.tsx):
   - S&P 500, NASDAQ, DOW, VIX display
   - Real-time price updates
   - Percentage change with color coding
   - Trend indicators (up/down arrows)
   - Loading states and error handling

2. **Sector Performance** (src/components/dashboard/SectorPerformance.tsx):
   - Interactive sector breakdown chart
   - Hover tooltips with detailed information
   - Color-coded performance indicators
   - Click to drill down to sector details

3. **Top Movers Table** (src/components/dashboard/TopMovers.tsx):
   - Daily gainers and losers
   - Volume and percentage change
   - Sortable columns
   - Pagination for large datasets
   - Real-time updates

4. **Market Sentiment Widget** (src/components/dashboard/MarketSentiment.tsx):
   - Market breadth indicators
   - Fear & Greed index
   - VIX level with interpretation
   - Historical comparison

5. **Data Integration**:
   - React Query hooks for data fetching
   - WebSocket connection for real-time updates
   - Error boundaries for failed data loads
   - Skeleton loading states

6. **Performance Optimization**:
   - Memoized components to prevent unnecessary re-renders
   - Virtual scrolling for large datasets
   - Debounced search functionality
   - Efficient chart rendering

Use Recharts for data visualization and ensure smooth animations.
```

### Prompt 2.3: Stock Analysis Page
```
Create a comprehensive stock analysis page with multiple analysis types:

1. **Stock Header** (src/components/stock/StockHeader.tsx):
   - Stock symbol and company name
   - Current price with change indicators
   - Key metrics (P/E, Market Cap, Volume)
   - Watchlist toggle functionality
   - Share/export options

2. **Price Chart** (src/components/stock/PriceChart.tsx):
   - Interactive candlestick chart
   - Multiple timeframes (1D, 5D, 1M, 3M, 1Y, 5Y)
   - Technical indicators overlay (MA, Bollinger Bands)
   - Volume chart below price chart
   - Zoom and pan functionality
   - Mobile-friendly touch interactions

3. **Technical Analysis Panel** (src/components/stock/TechnicalAnalysis.tsx):
   - RSI indicator with overbought/oversold levels
   - MACD with signal line
   - Moving averages (20, 50, 200 day)
   - Support and resistance levels
   - Trading signals and recommendations

4. **Financial Metrics** (src/components/stock/FinancialMetrics.tsx):
   - Profitability ratios (ROE, ROA, Margins)
   - Liquidity ratios (Current, Quick)
   - Leverage ratios (Debt/Equity, Interest Coverage)
   - Efficiency ratios (Asset Turnover, Inventory)
   - Growth metrics (Revenue, Earnings growth)

5. **News Feed** (src/components/stock/NewsFeed.tsx):
   - Real-time news articles
   - Sentiment analysis indicators
   - Source credibility indicators
   - Article preview with full text option
   - Filtering by date and relevance

6. **Analysis Tabs**:
   - Tabbed interface for different analysis types
   - Smooth transitions between tabs
   - Persistent state for user preferences
   - URL-based navigation for sharing

Implement proper error handling and loading states for all components.
```

---

## Phase 3: Advanced Features (Week 5-6)

### Prompt 3.1: Portfolio Management System
```
Create a comprehensive portfolio management system:

1. **Portfolio Overview** (src/components/portfolio/PortfolioOverview.tsx):
   - Total portfolio value with change indicators
   - Daily P&L with percentage change
   - Portfolio performance vs benchmark
   - Risk metrics (Sharpe ratio, Beta, VaR)
   - Asset allocation pie chart

2. **Holdings Table** (src/components/portfolio/HoldingsTable.tsx):
   - Sortable and filterable holdings list
   - Individual stock performance
   - Unrealized P&L with color coding
   - Weight percentage and allocation
   - Edit/remove position functionality
   - Bulk actions (select multiple positions)

3. **Add Position Modal** (src/components/portfolio/AddPositionModal.tsx):
   - Stock symbol search with autocomplete
   - Number of shares input with validation
   - Purchase price and date inputs
   - Commission and fees calculation
   - Real-time position value preview
   - Form validation and error handling

4. **Performance Charts** (src/components/portfolio/PerformanceCharts.tsx):
   - Portfolio value over time
   - Cumulative returns chart
   - Rolling returns analysis
   - Drawdown visualization
   - Benchmark comparison (S&P 500)
   - Interactive time period selection

5. **Risk Analysis** (src/components/portfolio/RiskAnalysis.tsx):
   - Value at Risk (VaR) calculations
   - Maximum drawdown analysis
   - Correlation matrix heatmap
   - Beta analysis vs market
   - Stress testing scenarios
   - Risk-adjusted returns

6. **Portfolio Optimization** (src/components/portfolio/PortfolioOptimization.tsx):
   - Modern Portfolio Theory implementation
   - Efficient frontier visualization
   - Risk tolerance slider
   - Optimization methods (Max Sharpe, Min Volatility)
   - Rebalancing recommendations
   - Transaction cost analysis

Implement proper state management with Zustand and ensure all calculations are accurate.
```

### Prompt 3.2: Research Reports System
```
Create a comprehensive research reports generation system:

1. **Report Templates** (src/components/reports/ReportTemplates.tsx):
   - Pre-built report templates (Full, Valuation, Risk, Technical)
   - Template preview functionality
   - Custom template creation
   - Template sharing and import/export
   - Template versioning system

2. **Report Builder** (src/components/reports/ReportBuilder.tsx):
   - Drag-and-drop report sections
   - Customizable content blocks
   - Real-time preview
   - Section reordering and editing
   - Content validation and error checking

3. **Report Generation** (src/components/reports/ReportGenerator.tsx):
   - Automated data collection from multiple sources
   - Chart and table generation
   - Executive summary generation
   - Risk assessment automation
   - Valuation model integration
   - Peer comparison analysis

4. **Report Export** (src/components/reports/ReportExport.tsx):
   - PDF generation with professional formatting
   - DOCX export with editable content
   - Excel export for data tables
   - Email sharing functionality
   - Print-friendly layouts
   - Custom branding options

5. **Report Management** (src/components/reports/ReportManagement.tsx):
   - Saved reports list with search and filter
   - Report history and versioning
   - Sharing permissions and access control
   - Report scheduling and automation
   - Analytics on report usage

6. **Report Viewer** (src/components/reports/ReportViewer.tsx):
   - Full-screen report viewing
   - Interactive charts and tables
   - Annotation and highlighting
   - Bookmarking and favorites
   - Print and download options

Ensure all reports are professionally formatted and include proper citations.
```

### Prompt 3.3: Advanced Analytics and Modeling
```
Create advanced financial modeling and analytics tools:

1. **DCF Calculator** (src/components/analytics/DCFCalculator.tsx):
   - Interactive DCF model with sensitivity analysis
   - Revenue and margin projections
   - Terminal value calculations
   - WACC estimation with beta calculations
   - Scenario analysis (Base, Bull, Bear cases)
   - Monte Carlo simulation for uncertainty

2. **Comparable Analysis** (src/components/analytics/ComparableAnalysis.tsx):
   - Peer company selection and screening
   - Valuation multiples comparison (P/E, P/B, EV/EBITDA)
   - Financial metrics benchmarking
   - Relative valuation analysis
   - Peer ranking and scoring
   - Industry analysis and trends

3. **Risk Analysis Tools** (src/components/analytics/RiskAnalysis.tsx):
   - Monte Carlo simulation for portfolio risk
   - Stress testing scenarios
   - Correlation analysis and heatmaps
   - VaR calculations with different methods
   - Tail risk analysis
   - Scenario-based risk assessment

4. **Backtesting Engine** (src/components/analytics/BacktestingEngine.tsx):
   - Historical strategy performance testing
   - Portfolio optimization backtesting
   - Risk-adjusted return analysis
   - Drawdown analysis and recovery periods
   - Benchmark comparison
   - Transaction cost impact analysis

5. **Options Analysis** (src/components/analytics/OptionsAnalysis.tsx):
   - Options chain visualization
   - Greeks calculation and display
   - Implied volatility analysis
   - Options strategy builder
   - P&L diagrams for strategies
   - Risk profile analysis

6. **Economic Indicators** (src/components/analytics/EconomicIndicators.tsx):
   - Key economic data integration
   - Interest rate analysis
   - Inflation indicators
   - GDP and employment data
   - Market sentiment indicators
   - Economic calendar integration

Implement proper mathematical calculations and ensure accuracy of all financial models.
```

---

## Phase 4: Polish & Optimization (Week 7-8)

### Prompt 4.1: Performance Optimization
```
Optimize the application for maximum performance:

1. **Code Splitting and Lazy Loading**:
   - Implement route-based code splitting
   - Lazy load heavy components (charts, reports)
   - Dynamic imports for large libraries
   - Preload critical resources
   - Optimize bundle size analysis

2. **React Performance Optimization**:
   - Implement React.memo for expensive components
   - Use useMemo and useCallback for expensive calculations
   - Optimize re-renders with proper dependency arrays
   - Implement virtual scrolling for large lists
   - Use React.Suspense for loading states

3. **Data Optimization**:
   - Implement efficient caching strategies
   - Use React Query for background updates
   - Optimize API calls with proper debouncing
   - Implement data pagination and virtualization
   - Use Web Workers for heavy calculations

4. **Asset Optimization**:
   - Optimize images with WebP format and fallbacks
   - Implement image lazy loading
   - Compress and minify assets
   - Use CDN for static assets
   - Implement service worker for caching

5. **Bundle Analysis**:
   - Analyze bundle size with webpack-bundle-analyzer
   - Remove unused dependencies
   - Optimize imports and tree shaking
   - Implement dynamic imports for large libraries
   - Monitor bundle size in CI/CD

6. **Performance Monitoring**:
   - Implement performance metrics tracking
   - Use React DevTools Profiler
   - Monitor Core Web Vitals
   - Set up performance budgets
   - Implement error tracking and monitoring

Target: < 2s page load time, < 500KB bundle size, > 90 Lighthouse score.
```

### Prompt 4.2: User Experience Enhancements
```
Enhance the user experience with professional polish:

1. **Loading States and Skeletons**:
   - Create skeleton screens for all major components
   - Implement progressive loading for charts
   - Add loading spinners for async operations
   - Use Framer Motion for smooth transitions
   - Implement optimistic updates for user actions

2. **Error Handling and Boundaries**:
   - Create comprehensive error boundaries
   - Implement user-friendly error messages
   - Add retry mechanisms for failed operations
   - Create fallback UI for broken components
   - Implement error reporting and logging

3. **Animations and Micro-interactions**:
   - Add smooth page transitions
   - Implement hover effects and focus states
   - Create loading animations for data fetching
   - Add success/error feedback animations
   - Implement gesture-based interactions

4. **Accessibility Improvements**:
   - Ensure WCAG 2.1 AA compliance
   - Implement proper ARIA labels and roles
   - Add keyboard navigation support
   - Ensure color contrast compliance
   - Implement screen reader support

5. **Mobile Experience**:
   - Optimize touch interactions
   - Implement swipe gestures for navigation
   - Add pull-to-refresh functionality
   - Optimize for mobile performance
   - Implement mobile-specific UI patterns

6. **User Preferences**:
   - Implement theme switching (light/dark)
   - Add customizable dashboard layouts
   - Save user preferences in localStorage
   - Implement personalized default settings
   - Add user onboarding and tutorials

Focus on creating a polished, professional experience that rivals industry leaders.
```

### Prompt 4.3: Testing and Quality Assurance
```
Implement comprehensive testing and quality assurance:

1. **Unit Testing** (Jest + React Testing Library):
   - Test all utility functions and hooks
   - Test component rendering and behavior
   - Test user interactions and events
   - Test error handling and edge cases
   - Achieve > 80% code coverage

2. **Integration Testing**:
   - Test API integration and data flow
   - Test component interactions
   - Test routing and navigation
   - Test state management
   - Test error boundaries

3. **End-to-End Testing** (Playwright):
   - Test critical user journeys
   - Test cross-browser compatibility
   - Test mobile responsiveness
   - Test performance under load
   - Test accessibility compliance

4. **Visual Regression Testing**:
   - Implement screenshot testing
   - Test component visual consistency
   - Test responsive design breakpoints
   - Test theme switching
   - Test cross-browser visual consistency

5. **Performance Testing**:
   - Test page load times
   - Test bundle size limits
   - Test memory usage
   - Test API response times
   - Test under various network conditions

6. **Accessibility Testing**:
   - Automated accessibility testing
   - Screen reader testing
   - Keyboard navigation testing
   - Color contrast validation
   - WCAG compliance verification

7. **Code Quality**:
   - ESLint configuration and rules
   - Prettier formatting
   - TypeScript strict mode
   - Husky pre-commit hooks
   - Code review guidelines

Set up CI/CD pipeline with automated testing and quality gates.
```

### Prompt 4.4: Deployment and Production Setup
```
Set up production deployment and monitoring:

1. **Build Optimization**:
   - Configure production build settings
   - Implement environment-specific configurations
   - Set up build caching and optimization
   - Configure asset compression and minification
   - Implement build size monitoring

2. **Deployment Configuration**:
   - Set up Docker containerization
   - Configure nginx for static file serving
   - Implement blue-green deployment strategy
   - Set up SSL certificates and security headers
   - Configure CDN for global distribution

3. **Environment Management**:
   - Set up development, staging, and production environments
   - Configure environment variables and secrets
   - Implement feature flags for gradual rollouts
   - Set up database migrations and backups
   - Configure monitoring and alerting

4. **Performance Monitoring**:
   - Implement application performance monitoring (APM)
   - Set up error tracking and logging
   - Monitor Core Web Vitals
   - Track user analytics and behavior
   - Set up uptime monitoring

5. **Security Implementation**:
   - Implement HTTPS and security headers
   - Set up authentication and authorization
   - Configure CORS and CSP policies
   - Implement rate limiting and DDoS protection
   - Set up security scanning and vulnerability assessment

6. **Backup and Recovery**:
   - Set up automated database backups
   - Implement disaster recovery procedures
   - Configure data retention policies
   - Set up monitoring and alerting
   - Test recovery procedures

7. **Documentation**:
   - Create deployment documentation
   - Document environment setup procedures
   - Create troubleshooting guides
   - Document monitoring and alerting
   - Create user documentation and help guides

Ensure production readiness with proper monitoring, security, and documentation.
```

---

## Additional Optimization Prompts

### Prompt A.1: Advanced Chart Customization
```
Enhance the charting system with advanced customization:

1. **Custom Chart Components**:
   - Create reusable chart wrapper components
   - Implement chart theme system
   - Add chart export functionality (PNG, SVG, PDF)
   - Implement chart annotation tools
   - Add chart comparison features

2. **Interactive Features**:
   - Implement crosshair and tooltip customization
   - Add zoom and pan with proper bounds
   - Create chart overlay system for indicators
   - Implement chart synchronization
   - Add chart sharing and embedding

3. **Performance Optimization**:
   - Implement chart data virtualization
   - Add chart rendering optimization
   - Create efficient data update mechanisms
   - Implement chart caching strategies
   - Optimize for mobile chart interactions

4. **Accessibility**:
   - Add keyboard navigation for charts
   - Implement screen reader support
   - Add high contrast mode support
   - Create alternative data representations
   - Implement chart description generation

Focus on creating professional-grade charts that rival Bloomberg Terminal quality.
```

### Prompt A.2: Real-time Data Integration
```
Implement comprehensive real-time data integration:

1. **WebSocket Implementation**:
   - Set up WebSocket connections for real-time data
   - Implement connection management and reconnection
   - Add data buffering and throttling
   - Create real-time data synchronization
   - Implement offline/online state handling

2. **Data Streaming**:
   - Implement efficient data streaming protocols
   - Add data compression and optimization
   - Create real-time chart updates
   - Implement data aggregation and sampling
   - Add data quality monitoring

3. **Performance Optimization**:
   - Implement efficient data update mechanisms
   - Add data caching and persistence
   - Create background data processing
   - Implement data deduplication
   - Optimize for high-frequency updates

4. **User Experience**:
   - Add real-time notifications
   - Implement data freshness indicators
   - Create smooth data transitions
   - Add real-time search and filtering
   - Implement data synchronization across tabs

Ensure real-time data updates are smooth and don't impact performance.
```

### Prompt A.3: Advanced Search and Filtering
```
Create advanced search and filtering capabilities:

1. **Global Search**:
   - Implement fuzzy search for stocks and companies
   - Add search suggestions and autocomplete
   - Create search history and favorites
   - Implement search result ranking
   - Add search analytics and insights

2. **Advanced Filtering**:
   - Create multi-criteria filtering system
   - Implement saved filter presets
   - Add filter combinations and logic
   - Create filter visualization and management
   - Implement filter sharing and collaboration

3. **Data Discovery**:
   - Add related stock suggestions
   - Implement sector and industry filtering
   - Create market cap and volume filters
   - Add technical indicator filters
   - Implement custom screening criteria

4. **Performance**:
   - Implement search indexing and optimization
   - Add search result caching
   - Create efficient filter algorithms
   - Implement search result pagination
   - Optimize for large datasets

Focus on creating an intuitive and powerful search experience.
```

---

## Usage Instructions

1. **Execute prompts in order**: Each prompt builds upon the previous work
2. **Review output carefully**: Ensure each implementation meets requirements
3. **Test thoroughly**: Run tests after each major implementation
4. **Iterate as needed**: Refine implementations based on results
5. **Document changes**: Keep track of modifications and decisions

## Success Criteria

- **Performance**: < 2s page load, < 500KB bundle, > 90 Lighthouse score
- **Functionality**: All existing features replicated with improvements
- **User Experience**: Professional, intuitive interface
- **Code Quality**: Type-safe, well-tested, maintainable code
- **Accessibility**: WCAG 2.1 AA compliance

This prompt guide will transform your equity research dashboard into a professional-grade application that impresses recruiters and provides an excellent user experience.
