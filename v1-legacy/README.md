# Equity Research Dashboard - Legacy Implementation (v1)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/Dash-2.0+-orange.svg)](https://dash.plotly.com/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Deprecated-red.svg)]()

> **Legacy Python Flask/Dash implementation** of the Equity Research Dashboard. This version is maintained for historical reference and backward compatibility.

## ⚠️ Important Notice

**This is the legacy implementation and is no longer actively developed.** 

- **Status**: Deprecated
- **Recommendation**: Use the [modern implementation (v2)](../v2-modern/README.md)
- **Support**: Limited support for critical security issues only
- **Migration**: See [Migration Guide](../docs/MIGRATION.md) for upgrading to v2

## 🎯 Overview

This legacy implementation was built with Python Flask/Dash and provides basic equity research functionality. While functional, it lacks the modern features, performance, and user experience of the v2 implementation.

### 🏆 Key Features (Legacy)

- **🔬 Basic Financial Modeling**: DCF and comparable analysis
- **📈 Market Data Integration**: Yahoo Finance API integration
- **⚡ Portfolio Management**: Basic portfolio tracking
- **🛡️ Risk Analysis**: Basic risk metrics
- **🎨 Web Interface**: Flask/Dash web application
- **🧪 Testing**: Basic test coverage

## 🚀 Quick Start

### **Prerequisites**

- **Python**: 3.8+
- **pip**: Latest version

### **Installation**

```bash
# Clone the repository
git clone <repository-url>
cd equity-research-dashboard/v1-legacy

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py

# Open http://localhost:5000
```

## 🏗️ Tech Stack

### **Backend Framework**
- **Python 3.8+** - Core programming language
- **Dash/Flask** - Web framework for interactive applications
- **Flask-Login** - Secure user authentication system
- **SQLite** - Database for user management and data persistence

### **Financial Analysis & Modeling**
- **yfinance** - Real-time financial data integration
- **pandas/numpy** - Data manipulation and numerical computing
- **scipy** - Scientific computing and optimization algorithms
- **scikit-learn** - Machine learning and statistical analysis
- **statsmodels** - Advanced statistical modeling

### **Visualization & Frontend**
- **Plotly** - Interactive charts and dashboards
- **Dash Bootstrap Components** - Professional UI components
- **Custom CSS/JS** - Responsive design and user interactions

### **Development & Quality**
- **pytest** - Comprehensive testing framework
- **black/flake8** - Code formatting and linting
- **Type hints** - Code documentation and IDE support

## 📁 Project Structure

```
v1-legacy/
├── app/                    # Main application
│   ├── main.py            # Dash application with callbacks
│   ├── auth.py            # User authentication system
│   └── utils.py           # Utility functions
├── analysis/               # Financial analysis modules
│   ├── financial_metrics.py  # Ratio calculations
│   ├── valuation_models.py   # DCF, DDM, comparable analysis
│   ├── risk_analysis.py      # Risk metrics and VaR
│   └── portfolio_optimizer.py # MPT optimization
├── data/                   # Data layer
│   ├── data_fetcher.py    # API integration
│   ├── financial_data.py  # Data processing
│   └── market_data.py     # Market data fetching
├── visualizations/         # Chart generation
│   ├── charts.py          # Interactive charts
│   ├── tables.py          # Data tables
│   └── dashboards.py      # Dashboard layouts
├── models/                 # Financial models
│   ├── dcf_model.py       # DCF implementation
│   ├── comparable_analysis.py # Peer analysis
│   └── monte_carlo.py     # Monte Carlo simulations
├── tests/                  # Comprehensive test suite
├── templates/              # Jinja2 templates
├── static/                 # CSS/JS assets
├── instance/               # SQLite database
├── cache/                  # Cache directory
├── venv/                   # Python virtual environment
├── requirements.txt        # Python dependencies
├── setup.py               # Python setup
├── run.py                 # Entry point
└── config.py              # Configuration
```

## 🎯 Key Features

### **Dashboard**
- Basic market overview
- Simple portfolio summary
- Stock charts with Plotly
- News feed integration

### **Portfolio Management**
- Basic portfolio creation and management
- Holdings tracking
- Simple performance metrics
- Basic risk analysis

### **Stock Analysis**
- **DCF Analysis**: Basic discounted cash flow valuation
- **Comparable Analysis**: Peer company comparisons
- **Risk Metrics**: Basic risk calculations
- **Technical Analysis**: Simple chart patterns

### **Research Reports**
- Basic report generation
- PDF export functionality
- Simple templates

## 🛠️ Development

### **Available Scripts**

```bash
# Development
python run.py              # Start development server

# Testing
pytest                     # Run all tests
pytest tests/              # Run specific test directory
pytest -v                  # Run tests with verbose output
pytest --cov              # Run tests with coverage

# Code Quality
black .                    # Format code with Black
flake8 .                   # Lint code with Flake8
mypy .                     # Type checking with MyPy

# Database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"  # Create database tables
```

### **Development Workflow**

1. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```

2. **Make Changes**
   - Write code following Python style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   pytest
   black .
   flake8 .
   ```

4. **Run Application**
   ```bash
   python run.py
   ```

## 🧪 Testing

### **Test Structure**

```
tests/
├── test_analysis.py                    # Analysis module tests
├── test_data.py                        # Data layer tests
├── test_models.py                      # Model tests
├── test_financial_metrics.py           # Financial metrics tests
├── test_portfolio_optimizer_edge_cases.py # Portfolio optimizer tests
├── test_charts_error_handling.py       # Chart error handling tests
└── e2e/                                # End-to-end tests
```

### **Running Tests**

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_analysis.py

# Run tests with coverage
pytest --cov=app --cov=analysis --cov=data

# Run tests with verbose output
pytest -v
```

### **Writing Tests**

```python
# Example test
import pytest
from analysis.financial_metrics import calculate_pe_ratio

def test_calculate_pe_ratio():
    """Test PE ratio calculation."""
    price = 100.0
    earnings = 5.0
    expected_pe = 20.0
    
    result = calculate_pe_ratio(price, earnings)
    
    assert result == expected_pe
    assert isinstance(result, float)
```

## 🔧 Configuration

### **Environment Variables**

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
```

### **Database Configuration**

```python
# Database setup
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    login_manager.init_app(app)
    
    return app
```

## 📊 Performance Considerations

### **Known Limitations**

- **Server-side Rendering**: Every interaction requires server round-trips
- **Limited Caching**: No intelligent client-side caching
- **Basic Mobile Support**: Limited responsive design
- **Performance Issues**: Slower loading and interactions
- **Limited Real-time**: Basic polling for data updates

### **Optimization Tips**

- **Database Indexing**: Ensure proper database indexes
- **Query Optimization**: Optimize database queries
- **Caching**: Implement server-side caching
- **Static Assets**: Use CDN for static assets
- **Database Connection Pooling**: Use connection pooling

## 🔒 Security

### **Authentication**

```python
# Basic Flask-Login implementation
from flask_login import UserMixin, login_user, logout_user

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### **Security Best Practices**

- **Password Hashing**: Use Werkzeug password hashing
- **CSRF Protection**: Enable CSRF protection
- **Input Validation**: Validate all user inputs
- **SQL Injection**: Use parameterized queries
- **XSS Protection**: Sanitize user inputs

## 🚀 Deployment

### **Production Deployment**

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# Or with Docker
docker build -t equity-dashboard-legacy .
docker run -p 5000:5000 equity-dashboard-legacy
```

### **Environment Setup**

```bash
# Set environment variables
export FLASK_APP=run.py
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export DATABASE_URL=postgresql://user:pass@localhost/equity_dashboard
```

## 📚 Documentation

- **[Architecture Guide](../docs/ARCHITECTURE.md)** - System architecture
- **[API Documentation](../docs/API.md)** - API endpoints and usage
- **[Migration Guide](../docs/MIGRATION.md)** - Upgrading to v2
- **[Deployment Guide](../docs/DEPLOYMENT.md)** - Deployment instructions

## 🔄 Migration to v2

### **Why Migrate?**

The modern implementation (v2) offers significant improvements:

- **Better Performance**: Client-side rendering with caching
- **Modern UI/UX**: Professional polish with animations
- **Mobile Support**: Mobile-first responsive design
- **Accessibility**: WCAG 2.1 AA compliance
- **Real-time Data**: WebSocket integration
- **Better Architecture**: Modern React TypeScript stack

### **Migration Steps**

1. **Review Migration Guide**: See [Migration Guide](../docs/MIGRATION.md)
2. **Export Data**: Export your portfolio and user data
3. **Set Up v2**: Follow v2 setup instructions
4. **Import Data**: Import your data into v2
5. **Test Features**: Verify all functionality works
6. **Update Users**: Notify users of the migration

## 🤝 Contributing

**Note**: This legacy implementation is no longer accepting new features. 

- **Bug Fixes**: Critical security issues only
- **Documentation**: Updates to reflect deprecation
- **Migration**: Help users migrate to v2

For active development, please contribute to the [modern implementation (v2)](../v2-modern/README.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- **Financial Data**: Yahoo Finance API via yfinance
- **Charts**: Plotly for interactive visualizations
- **Web Framework**: Dash and Flask for the web application
- **Data Processing**: pandas and numpy for data manipulation

---

**⚠️ This legacy implementation is deprecated. Please use the [modern implementation (v2)](../v2-modern/README.md) for new projects and active development.**
