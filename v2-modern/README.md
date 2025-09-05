# Equity Research Dashboard - Modern Implementation (v2)

[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0+-orange.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.0+-blue.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Modern React TypeScript implementation** of the Equity Research Dashboard featuring real-time market data, advanced financial modeling, portfolio optimization, and comprehensive risk analysis.

## 🎯 Overview

This is the **primary and recommended** implementation of the Equity Research Dashboard. Built with modern React TypeScript technologies, it provides a professional-grade user experience with industry-standard performance and accessibility.

### 🏆 Key Features

- **🔬 Advanced Financial Modeling**: Complete DCF, DDM, and comparable analysis implementations
- **📈 Real-Time Market Integration**: Live data feeds with WebSocket integration
- **⚡ Portfolio Optimization**: Modern Portfolio Theory with multiple optimization strategies
- **🛡️ Risk Management**: Comprehensive VaR, stress testing, and Monte Carlo simulations
- **🎨 Professional UI/UX**: Responsive design with smooth animations and micro-interactions
- **📱 Mobile-First Design**: Touch-optimized with responsive layouts
- **♿ Accessibility**: WCAG 2.1 AA compliant with screen reader support
- **🧪 Production-Ready**: Extensive testing, error handling, and documentation

## 🚀 Quick Start

### **Prerequisites**

- **Node.js**: 18+ (LTS recommended)
- **npm**: 9+ or **yarn**: 1.22+

### **Installation**

```bash
# Clone the repository
git clone <repository-url>
cd equity-research-dashboard/v2-modern

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### **Environment Setup**

```bash
# Copy environment file
cp env.example .env

# Edit environment variables
# VITE_API_BASE_URL=http://localhost:5000/api
# VITE_WS_URL=ws://localhost:5000/ws
```

## 🏗️ Tech Stack

### **Frontend Framework**
- **React 18** - Component-based architecture with concurrent rendering
- **TypeScript** - Type safety and better IDE support
- **Vite** - Lightning-fast build tool and dev server

### **State Management**
- **Zustand** - Lightweight, simple state management
- **React Query** - Server state management, caching, background updates

### **UI Framework**
- **Tailwind CSS** - Utility-first CSS framework
- **Headless UI** - Unstyled, accessible UI components
- **Framer Motion** - Smooth animations and transitions

### **Charts & Visualization**
- **Recharts** - React-native charting library
- **D3.js** - Custom visualizations for complex financial charts

### **Development & Quality**
- **ESLint + Prettier** - Code quality and formatting
- **Jest + React Testing Library** - Comprehensive testing
- **Storybook** - Component development and documentation

## 📁 Project Structure

```
v2-modern/
├── src/
│   ├── components/          # React components
│   │   ├── ui/             # Reusable UI components
│   │   ├── dashboard/      # Dashboard components
│   │   ├── portfolio/      # Portfolio components
│   │   ├── stock/          # Stock analysis components
│   │   ├── reports/        # Report components
│   │   └── analytics/      # Analytics components
│   ├── pages/              # Page components
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API services
│   ├── store/              # State management
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   └── workers/            # Web workers
├── public/                 # Static assets
├── tests/                  # Test files
├── stories/                # Storybook stories
└── docs/                   # Component documentation
```

## 🎯 Key Features

### **Dashboard**
- Real-time market data with live updates
- Interactive charts and visualizations
- Market sentiment analysis
- Sector performance tracking
- Top movers and market indices

### **Portfolio Management**
- Create and manage multiple portfolios
- Real-time portfolio tracking
- Performance analytics and reporting
- Risk analysis and optimization
- Rebalancing recommendations

### **Stock Analysis**
- **DCF Analysis**: Discounted cash flow valuation
- **Comparable Analysis**: Peer company comparisons
- **Risk Analysis**: VaR, stress testing, Monte Carlo simulations
- **Technical Analysis**: Chart patterns and indicators
- **Options Analysis**: Greeks and strategy analysis

### **Research Reports**
- Automated report generation
- Customizable templates
- Export to PDF, Excel, Word
- Collaboration features
- Scheduled reports

### **Advanced Features**
- **Real-time Data**: WebSocket integration for live updates
- **Mobile-First**: Responsive design with touch interactions
- **Accessibility**: WCAG 2.1 AA compliant
- **Performance**: Optimized loading and caching
- **Security**: JWT authentication and secure data handling

## 🛠️ Development

### **Available Scripts**

```bash
# Development
npm run dev              # Start development server
npm run dev:host         # Start with network access

# Building
npm run build            # Build for production
npm run build:analyze    # Build with bundle analysis
npm run preview          # Preview production build

# Testing
npm run test             # Run unit tests
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Run tests with coverage
npm run test:e2e         # Run end-to-end tests

# Code Quality
npm run lint             # Run ESLint
npm run lint:fix         # Fix ESLint issues
npm run format           # Format code with Prettier
npm run type-check       # Run TypeScript type checking

# Storybook
npm run storybook        # Start Storybook
npm run build-storybook  # Build Storybook

# Utilities
npm run clean            # Clean build artifacts
npm run postinstall      # Post-install setup
```

### **Development Workflow**

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   npm run test
   npm run lint
   npm run type-check
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

## 🧪 Testing

### **Test Structure**

```
tests/
├── components/           # Component tests
├── hooks/               # Hook tests
├── utils/               # Utility tests
├── services/            # Service tests
├── e2e/                 # End-to-end tests
└── __mocks__/           # Test mocks
```

### **Running Tests**

```bash
# Run all tests
npm test

# Run specific test file
npm test -- --testPathPattern=StockCard

# Run tests with coverage
npm run test:coverage

# Run e2e tests
npm run test:e2e
```

### **Writing Tests**

```typescript
// Example component test
import { render, screen } from '@testing-library/react';
import { StockCard } from '../StockCard';

describe('StockCard', () => {
  it('renders stock information correctly', () => {
    const stock = {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      price: 150.25,
      change: 2.15,
      changePercent: 1.45
    };

    render(<StockCard stock={stock} />);
    
    expect(screen.getByText('AAPL')).toBeInTheDocument();
    expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
    expect(screen.getByText('$150.25')).toBeInTheDocument();
  });
});
```

## 🎨 Styling

### **Tailwind CSS**

We use Tailwind CSS for styling with a custom design system:

```typescript
// Example component with Tailwind
const StockCard = ({ stock }: StockCardProps) => (
  <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
    <h3 className="text-lg font-semibold text-gray-900">{stock.symbol}</h3>
    <p className="text-sm text-gray-600">{stock.name}</p>
    <div className="mt-4">
      <span className="text-2xl font-bold text-gray-900">
        ${stock.price.toFixed(2)}
      </span>
      <span className={`ml-2 text-sm font-medium ${
        stock.change >= 0 ? 'text-green-600' : 'text-red-600'
      }`}>
        {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} 
        ({stock.changePercent.toFixed(2)}%)
      </span>
    </div>
  </div>
);
```

### **Design System**

- **Colors**: Semantic color system with light/dark themes
- **Typography**: Responsive font sizes with proper hierarchy
- **Spacing**: 4px grid system for consistent spacing
- **Components**: Reusable component library

## 🔧 Configuration

### **Environment Variables**

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:5000/api
VITE_WS_URL=ws://localhost:5000/ws

# Application Configuration
VITE_APP_NAME=Equity Research Dashboard
VITE_APP_VERSION=2.0.0

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG=false

# External Services
VITE_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
VITE_SENTRY_DSN=https://your-sentry-dsn
```

### **Vite Configuration**

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
```

## 📱 Mobile Support

### **Responsive Design**

- **Mobile-First**: Designed for mobile devices first
- **Touch Interactions**: Optimized for touch input
- **Gesture Support**: Swipe gestures for navigation
- **Performance**: Optimized for mobile performance

### **Progressive Web App**

- **Service Worker**: Offline functionality
- **App Manifest**: Installable on mobile devices
- **Push Notifications**: Real-time notifications
- **Background Sync**: Sync data when online

## ♿ Accessibility

### **WCAG 2.1 AA Compliance**

- **Color Contrast**: 4.5:1 minimum contrast ratio
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: Proper ARIA labels and roles
- **Focus Management**: Visible focus indicators
- **Reduced Motion**: Respects user preferences

### **Accessibility Features**

```typescript
// Example accessible component
const AccessibleButton = ({ children, onClick, disabled }: ButtonProps) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
    aria-label={typeof children === 'string' ? children : 'Button'}
  >
    {children}
  </button>
);
```

## 🚀 Deployment

### **Build for Production**

```bash
# Build the application
npm run build

# Preview the build
npm run preview
```

### **Deployment Options**

- **Static Hosting**: Netlify, Vercel, GitHub Pages
- **CDN**: CloudFront, Cloudflare
- **Container**: Docker, Kubernetes
- **Cloud Platforms**: AWS, GCP, Azure

## 📚 Documentation

- **[Architecture Guide](../docs/ARCHITECTURE.md)** - System architecture
- **[API Documentation](../docs/API.md)** - API endpoints and usage
- **[Migration Guide](../docs/MIGRATION.md)** - Upgrading from v1
- **[Deployment Guide](../docs/DEPLOYMENT.md)** - Deployment instructions
- **[Contributing Guide](../docs/CONTRIBUTING.md)** - How to contribute

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](../docs/CONTRIBUTING.md) for details on how to contribute to the project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- **Financial Data**: Yahoo Finance API via yfinance
- **Charts**: Recharts and D3.js for visualizations
- **UI Components**: Headless UI and Tailwind CSS
- **Icons**: Heroicons for the icon set

---

**Note**: This is the **primary and recommended** implementation. For the legacy Python/Dash implementation, see [v1-legacy](../v1-legacy/README.md).