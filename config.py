"""
Configuration file for Equity Research Dashboard
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    
    # Application Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///equity_research.db'
    
    # API Keys
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
    FINANCIAL_MODELING_PREP_API_KEY = os.environ.get('FINANCIAL_MODELING_PREP_API_KEY')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
    QUANDL_API_KEY = os.environ.get('QUANDL_API_KEY')
    
    # Redis Configuration (for caching)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Data Settings
    DEFAULT_STOCKS = [
        'AAPL', 'JPM', 'JNJ', 'PG', 'XOM'
    ]
    
    # Market Data Settings
    MARKET_INDICES = {
        'S&P 500': '^GSPC',
        'NASDAQ': '^IXIC',
        'DOW JONES': '^DJI',
        'VIX': '^VIX',
        'Russell 2000': '^RUT'
    }
    
    # Risk-Free Rate (10-Year Treasury)
    RISK_FREE_RATE_SYMBOL = '^TNX'
    
    # Cache Settings
    CACHE_TIMEOUT = 300  # 5 minutes for real-time data
    HISTORICAL_CACHE_TIMEOUT = 3600  # 1 hour for historical data
    
    # Analysis Settings
    DEFAULT_DCF_YEARS = 5
    DEFAULT_TERMINAL_GROWTH_RATE = 0.025  # 2.5%
    DEFAULT_DISCOUNT_RATE = 0.10  # 10% WACC assumption
    
    # Monte Carlo Settings
    MC_SIMULATIONS = 10000
    CONFIDENCE_LEVELS = [0.90, 0.95, 0.99]
    
    # Portfolio Optimization
    MAX_WEIGHT_SINGLE_STOCK = 0.40  # 40% max allocation
    MIN_WEIGHT_SINGLE_STOCK = 0.01  # 1% min allocation
    
    # Dashboard Settings
    UPDATE_INTERVAL = 30  # seconds
    MAX_CHART_POINTS = 252  # 1 year of trading days


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///test_equity_research.db'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}