# Contributing Guide

## 🤝 Welcome Contributors!

Thank you for your interest in contributing to the Equity Research Dashboard! This guide will help you get started with contributing to our project.

## 🎯 How to Contribute

### **Ways to Contribute**

- **🐛 Bug Reports**: Report bugs and issues
- **✨ Feature Requests**: Suggest new features and improvements
- **📝 Documentation**: Improve documentation and guides
- **💻 Code Contributions**: Submit code improvements and new features
- **🧪 Testing**: Help improve test coverage and quality
- **🎨 UI/UX**: Improve user interface and user experience
- **🔧 DevOps**: Help with deployment and infrastructure

## 🚀 Getting Started

### **Prerequisites**

- **Node.js**: 18+ (LTS recommended)
- **npm**: 9+ or **yarn**: 1.22+
- **Git**: Latest version
- **Code Editor**: VS Code, WebStorm, or similar
- **Browser**: Chrome, Firefox, Safari, or Edge

### **Development Setup**

1. **Fork the Repository**
   ```bash
   # Fork the repository on GitHub
   # Then clone your fork
   git clone https://github.com/YOUR_USERNAME/equity-research-dashboard.git
   cd equity-research-dashboard
   ```

2. **Set Up Development Environment**
   ```bash
   # Navigate to the modern implementation
   cd v2-modern
   
   # Install dependencies
   npm install
   
   # Start development server
   npm run dev
   ```

3. **Create a Branch**
   ```bash
   # Create a new branch for your feature
   git checkout -b feature/your-feature-name
   
   # Or for bug fixes
   git checkout -b fix/your-bug-fix
   ```

## 📋 Development Workflow

### **Branch Naming Convention**

- **Features**: `feature/feature-name` (e.g., `feature/portfolio-optimization`)
- **Bug Fixes**: `fix/bug-description` (e.g., `fix/chart-rendering-issue`)
- **Documentation**: `docs/documentation-update` (e.g., `docs/api-documentation`)
- **Refactoring**: `refactor/component-name` (e.g., `refactor/stock-chart-component`)
- **Hotfixes**: `hotfix/critical-issue` (e.g., `hotfix/security-vulnerability`)

### **Commit Message Convention**

We use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### **Types**
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### **Examples**
```bash
feat(portfolio): add portfolio optimization feature
fix(charts): resolve chart rendering issue on mobile
docs(api): update API documentation for new endpoints
style(components): format code with prettier
refactor(hooks): simplify usePortfolio hook
test(utils): add tests for financial calculations
chore(deps): update dependencies to latest versions
```

## 🏗️ Project Structure

### **Modern Implementation (v2-modern/)**

```
v2-modern/
├── src/
│   ├── components/          # React components
│   │   ├── ui/             # Reusable UI components
│   │   ├── dashboard/      # Dashboard components
│   │   ├── portfolio/      # Portfolio components
│   │   ├── stock/          # Stock analysis components
│   │   └── reports/        # Report components
│   ├── pages/              # Page components
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API services
│   ├── store/              # State management
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   └── workers/            # Web workers
├── public/                 # Static assets
├── tests/                  # Test files
└── docs/                   # Component documentation
```

### **Legacy Implementation (v1-legacy/)**

```
v1-legacy/
├── app/                    # Flask/Dash application
├── analysis/               # Financial analysis modules
├── data/                   # Data layer
├── visualizations/         # Chart generation
├── models/                 # Financial models
├── tests/                  # Test suite
├── templates/              # Jinja2 templates
└── static/                 # CSS/JS assets
```

## 🧪 Testing

### **Running Tests**

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- --testPathPattern=portfolio

# Run e2e tests
npm run test:e2e
```

### **Writing Tests**

#### **Component Tests**
```typescript
// src/components/__tests__/StockCard.test.tsx
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

#### **Hook Tests**
```typescript
// src/hooks/__tests__/usePortfolio.test.ts
import { renderHook, act } from '@testing-library/react';
import { usePortfolio } from '../usePortfolio';

describe('usePortfolio', () => {
  it('should fetch portfolio data', async () => {
    const { result } = renderHook(() => usePortfolio('portfolio-id'));
    
    expect(result.current.isLoading).toBe(true);
    
    await act(async () => {
      await result.current.refetch();
    });
    
    expect(result.current.data).toBeDefined();
    expect(result.current.isLoading).toBe(false);
  });
});
```

#### **Utility Tests**
```typescript
// src/utils/__tests__/financial-calculations.test.ts
import { calculateDCF, calculatePortfolioReturn } from '../financial-calculations';

describe('Financial Calculations', () => {
  describe('calculateDCF', () => {
    it('should calculate DCF correctly', () => {
      const assumptions = {
        growthRate: 0.05,
        terminalGrowthRate: 0.03,
        discountRate: 0.10
      };
      
      const result = calculateDCF(assumptions);
      
      expect(result).toBeGreaterThan(0);
      expect(typeof result).toBe('number');
    });
  });
});
```

### **Test Coverage**

We aim for:
- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **E2E Tests**: Critical user flows covered

## 🎨 Code Style

### **TypeScript**

- **Strict Mode**: Always use strict TypeScript
- **Type Definitions**: Define types for all props and data
- **Interfaces**: Use interfaces for object shapes
- **Enums**: Use enums for constants
- **Generics**: Use generics for reusable components

```typescript
// Good
interface StockProps {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

const StockCard: React.FC<StockProps> = ({ symbol, name, price, change, changePercent }) => {
  // Component implementation
};

// Bad
const StockCard = ({ symbol, name, price, change, changePercent }) => {
  // Component implementation
};
```

### **React**

- **Functional Components**: Use functional components with hooks
- **Custom Hooks**: Extract reusable logic into custom hooks
- **Props Interface**: Define props interface for all components
- **Default Props**: Use default parameters instead of defaultProps

```typescript
// Good
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  disabled = false,
  onClick,
  children
}) => {
  // Component implementation
};

// Bad
const Button = ({ variant, size, disabled, onClick, children }) => {
  // Component implementation
};
```

### **CSS/Styling**

- **Tailwind CSS**: Use Tailwind utility classes
- **Component Styles**: Use CSS modules for component-specific styles
- **Responsive Design**: Mobile-first approach
- **Accessibility**: Ensure proper contrast and focus states

```typescript
// Good
<div className="flex flex-col space-y-4 p-6 bg-white rounded-lg shadow-md">
  <h2 className="text-xl font-semibold text-gray-900">Portfolio Overview</h2>
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {/* Content */}
  </div>
</div>

// Bad
<div style={{ display: 'flex', flexDirection: 'column', padding: '24px' }}>
  <h2 style={{ fontSize: '20px', fontWeight: 'bold' }}>Portfolio Overview</h2>
</div>
```

## 📝 Documentation

### **Component Documentation**

Each component should have:
- **JSDoc comments** for props and methods
- **Usage examples** in Storybook
- **README.md** for complex components

```typescript
/**
 * StockCard component displays stock information in a card format
 * 
 * @param stock - Stock data object
 * @param onSelect - Callback when stock is selected
 * @param showChart - Whether to show mini chart
 * @example
 * ```tsx
 * <StockCard 
 *   stock={stockData} 
 *   onSelect={handleSelect}
 *   showChart={true}
 * />
 * ```
 */
interface StockCardProps {
  stock: Stock;
  onSelect?: (stock: Stock) => void;
  showChart?: boolean;
}

const StockCard: React.FC<StockCardProps> = ({ stock, onSelect, showChart = false }) => {
  // Component implementation
};
```

### **API Documentation**

- **OpenAPI/Swagger** for API endpoints
- **Type definitions** for request/response
- **Usage examples** for each endpoint
- **Error handling** documentation

### **README Files**

Each major directory should have a README.md with:
- **Purpose** of the directory
- **Key components** and their usage
- **Setup instructions** if applicable
- **Examples** of common usage

## 🔍 Code Review Process

### **Pull Request Guidelines**

1. **Create Pull Request**
   - Use descriptive title and description
   - Link to related issues
   - Include screenshots for UI changes
   - Add tests for new features

2. **Pull Request Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

3. **Review Process**
   - **Automated Checks**: CI/CD pipeline must pass
   - **Code Review**: At least one reviewer approval
   - **Testing**: All tests must pass
   - **Documentation**: Documentation updated if needed

### **Review Checklist**

#### **For Reviewers**
- [ ] **Code Quality**: Code is clean and follows conventions
- [ ] **Functionality**: Feature works as expected
- [ ] **Performance**: No performance regressions
- [ ] **Security**: No security vulnerabilities
- [ ] **Tests**: Adequate test coverage
- [ ] **Documentation**: Documentation is updated
- [ ] **Accessibility**: Accessibility requirements met

#### **For Authors**
- [ ] **Self Review**: Code reviewed by author
- [ ] **Tests**: Tests written and passing
- [ ] **Documentation**: Documentation updated
- [ ] **Breaking Changes**: Breaking changes documented
- [ ] **Performance**: Performance impact considered
- [ ] **Security**: Security implications reviewed

## 🐛 Bug Reports

### **Bug Report Template**

```markdown
## Bug Description
Clear and concise description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Screenshots
If applicable, add screenshots

## Environment
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Browser: [e.g., Chrome 95, Firefox 94, Safari 15]
- Version: [e.g., 2.0.0]

## Additional Context
Any other context about the problem
```

## ✨ Feature Requests

### **Feature Request Template**

```markdown
## Feature Description
Clear and concise description of the feature

## Problem Statement
What problem does this feature solve?

## Proposed Solution
Describe your proposed solution

## Alternatives Considered
Describe any alternative solutions

## Additional Context
Any other context, mockups, or examples
```

## 🏷️ Issue Labels

### **Bug Labels**
- `bug`: Something isn't working
- `critical`: Critical bug that needs immediate attention
- `regression`: Bug that was working before

### **Feature Labels**
- `enhancement`: New feature or request
- `feature-request`: Feature request from community
- `good-first-issue`: Good for newcomers

### **Documentation Labels**
- `documentation`: Improvements or additions to documentation
- `docs`: Documentation related

### **Priority Labels**
- `priority-high`: High priority
- `priority-medium`: Medium priority
- `priority-low`: Low priority

## 🎯 Development Guidelines

### **Performance**

- **Bundle Size**: Keep bundle size minimal
- **Lazy Loading**: Use lazy loading for routes and components
- **Memoization**: Use React.memo and useMemo appropriately
- **Virtual Scrolling**: Use for large lists
- **Image Optimization**: Optimize images and use appropriate formats

### **Accessibility**

- **WCAG 2.1 AA**: Follow WCAG 2.1 AA guidelines
- **Keyboard Navigation**: Ensure keyboard accessibility
- **Screen Readers**: Test with screen readers
- **Color Contrast**: Ensure proper color contrast
- **Focus Management**: Proper focus management

### **Security**

- **Input Validation**: Validate all user inputs
- **XSS Prevention**: Prevent cross-site scripting
- **CSRF Protection**: Protect against CSRF attacks
- **Authentication**: Secure authentication implementation
- **Data Sanitization**: Sanitize data before processing

## 🚀 Release Process

### **Version Numbering**

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### **Release Checklist**

- [ ] **Code Review**: All PRs reviewed and approved
- [ ] **Tests**: All tests passing
- [ ] **Documentation**: Documentation updated
- [ ] **Changelog**: Changelog updated
- [ ] **Version**: Version bumped
- [ ] **Release Notes**: Release notes prepared
- [ ] **Deployment**: Deployed to production
- [ ] **Announcement**: Community notified

## 📞 Getting Help

### **Community Support**

- **GitHub Discussions**: For questions and discussions
- **GitHub Issues**: For bug reports and feature requests
- **Discord**: For real-time community chat
- **Email**: For security issues and private matters

### **Resources**

- **[Architecture Guide](ARCHITECTURE.md)**: System architecture
- **[API Documentation](API.md)**: API endpoints and usage
- **[Migration Guide](MIGRATION.md)**: Upgrading from v1 to v2
- **[Deployment Guide](DEPLOYMENT.md)**: Deployment instructions

## 🙏 Recognition

### **Contributors**

We recognize all contributors in our:
- **README.md**: List of contributors
- **Release Notes**: Contributors for each release
- **GitHub**: Contributor statistics and graphs

### **Contributor Levels**

- **🥉 Bronze**: 1-5 contributions
- **🥈 Silver**: 6-15 contributions
- **🥇 Gold**: 16+ contributions
- **💎 Diamond**: Core maintainer

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you for contributing to the Equity Research Dashboard! Your contributions help make this project better for everyone. 🚀
