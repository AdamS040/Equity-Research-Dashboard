"""
Economic Indicators Integration and Analysis System

This module provides comprehensive economic data analysis including:
- Key economic data integration
- Interest rate analysis
- Inflation indicators
- GDP and employment data
- Market sentiment indicators
- Economic calendar integration
- Macroeconomic impact analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import math
from scipy import stats
import logging
from decimal import Decimal, ROUND_HALF_UP
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class EconomicIndicator:
    """Economic Indicator Data Structure"""
    name: str
    symbol: str
    value: float
    previous_value: float
    change: float
    change_percent: float
    unit: str
    frequency: str
    last_updated: str
    source: str
    description: str
    importance: str  # Low, Medium, High
    country: str
    category: str  # GDP, Inflation, Employment, Interest Rates, etc.


@dataclass
class EconomicEvent:
    """Economic Calendar Event"""
    time: str
    country: str
    event: str
    importance: str  # Low, Medium, High
    actual: Optional[float]
    forecast: Optional[float]
    previous: Optional[float]
    unit: str
    impact: str  # Positive, Negative, Neutral


@dataclass
class InterestRateData:
    """Interest Rate Information"""
    rate: float
    previous_rate: float
    change: float
    effective_date: str
    next_meeting: str
    target_range: Dict[str, float]
    central_bank: str
    country: str


@dataclass
class InflationData:
    """Inflation Indicators"""
    cpi: float
    cpi_change: float
    core_cpi: float
    core_cpi_change: float
    pce: float
    pce_change: float
    core_pce: float
    core_pce_change: float
    last_updated: str
    country: str


@dataclass
class GDPData:
    """GDP Information"""
    gdp: float
    gdp_growth: float
    gdp_per_capita: float
    gdp_per_capita_growth: float
    last_updated: str
    quarter: str
    country: str


@dataclass
class EmploymentData:
    """Employment Statistics"""
    unemployment_rate: float
    unemployment_rate_change: float
    non_farm_payrolls: float
    non_farm_payrolls_change: float
    labor_force_participation: float
    labor_force_participation_change: float
    last_updated: str
    country: str


@dataclass
class MarketSentiment:
    """Market Sentiment Indicators"""
    vix: float
    vix_change: float
    fear_greed_index: float
    put_call_ratio: float
    insider_trading: float
    institutional_flow: float
    retail_flow: float
    last_updated: str


class EconomicDataProvider:
    """Economic Data Provider Interface"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_fred_data(self, series_id: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Fetch data from FRED (Federal Reserve Economic Data)"""
        try:
            if not self.session:
                raise ValueError("Session not initialized")
            
            # FRED API endpoint
            url = f"https://api.stlouisfed.org/fred/series/observations"
            
            params = {
                'series_id': series_id,
                'api_key': 'YOUR_FRED_API_KEY',  # Would need actual API key
                'file_type': 'json',
                'sort_order': 'asc'
            }
            
            if start_date:
                params['observation_start'] = start_date
            if end_date:
                params['observation_end'] = end_date
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    observations = data.get('observations', [])
                    
                    # Convert to DataFrame
                    df_data = []
                    for obs in observations:
                        if obs.get('value') != '.':
                            df_data.append({
                                'date': obs['date'],
                                'value': float(obs['value'])
                            })
                    
                    df = pd.DataFrame(df_data)
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    
                    return df
                else:
                    logger.error(f"FRED API request failed: {response.status}")
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"FRED data fetch failed: {e}")
            return pd.DataFrame()
    
    async def fetch_alpha_vantage_economic_data(self, function: str, symbol: str = None) -> pd.DataFrame:
        """Fetch economic data from Alpha Vantage"""
        try:
            if not self.session:
                raise ValueError("Session not initialized")
            
            url = "https://www.alphavantage.co/query"
            params = {
                'function': function,
                'apikey': 'YOUR_ALPHA_VANTAGE_API_KEY'  # Would need actual API key
            }
            
            if symbol:
                params['symbol'] = symbol
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse response based on function type
                    if function == 'REAL_GDP':
                        return self._parse_gdp_data(data)
                    elif function == 'INFLATION':
                        return self._parse_inflation_data(data)
                    elif function == 'UNEMPLOYMENT':
                        return self._parse_unemployment_data(data)
                    else:
                        return pd.DataFrame()
                else:
                    logger.error(f"Alpha Vantage API request failed: {response.status}")
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"Alpha Vantage data fetch failed: {e}")
            return pd.DataFrame()
    
    def _parse_gdp_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse GDP data from Alpha Vantage response"""
        try:
            gdp_data = data.get('data', [])
            df_data = []
            
            for item in gdp_data:
                df_data.append({
                    'date': item['date'],
                    'value': float(item['value'])
                })
            
            df = pd.DataFrame(df_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"GDP data parsing failed: {e}")
            return pd.DataFrame()
    
    def _parse_inflation_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse inflation data from Alpha Vantage response"""
        try:
            inflation_data = data.get('data', [])
            df_data = []
            
            for item in inflation_data:
                df_data.append({
                    'date': item['date'],
                    'value': float(item['value'])
                })
            
            df = pd.DataFrame(df_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Inflation data parsing failed: {e}")
            return pd.DataFrame()
    
    def _parse_unemployment_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse unemployment data from Alpha Vantage response"""
        try:
            unemployment_data = data.get('data', [])
            df_data = []
            
            for item in unemployment_data:
                df_data.append({
                    'date': item['date'],
                    'value': float(item['value'])
                })
            
            df = pd.DataFrame(df_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Unemployment data parsing failed: {e}")
            return pd.DataFrame()


class EconomicIndicatorsEngine:
    """Economic Indicators Analysis Engine"""
    
    def __init__(self):
        self.data_provider = EconomicDataProvider()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def get_key_indicators(self, country: str = 'US') -> Dict[str, EconomicIndicator]:
        """Get key economic indicators for a country"""
        try:
            indicators = {}
            
            # GDP
            gdp_indicator = await self._get_gdp_indicator(country)
            if gdp_indicator:
                indicators['gdp'] = gdp_indicator
            
            # Inflation
            inflation_indicator = await self._get_inflation_indicator(country)
            if inflation_indicator:
                indicators['inflation'] = inflation_indicator
            
            # Unemployment
            unemployment_indicator = await self._get_unemployment_indicator(country)
            if unemployment_indicator:
                indicators['unemployment'] = unemployment_indicator
            
            # Interest Rates
            interest_rate_indicator = await self._get_interest_rate_indicator(country)
            if interest_rate_indicator:
                indicators['interest_rate'] = interest_rate_indicator
            
            return indicators
            
        except Exception as e:
            logger.error(f"Key indicators fetch failed: {e}")
            return {}
    
    async def _get_gdp_indicator(self, country: str) -> Optional[EconomicIndicator]:
        """Get GDP indicator"""
        try:
            async with self.data_provider as provider:
                if country == 'US':
                    gdp_data = await provider.fetch_fred_data('GDP')
                else:
                    gdp_data = await provider.fetch_alpha_vantage_economic_data('REAL_GDP')
                
                if gdp_data.empty:
                    return None
                
                # Get latest values
                latest_value = gdp_data.iloc[-1]['value']
                previous_value = gdp_data.iloc[-2]['value'] if len(gdp_data) > 1 else latest_value
                
                change = latest_value - previous_value
                change_percent = (change / previous_value) * 100 if previous_value != 0 else 0
                
                return EconomicIndicator(
                    name='Gross Domestic Product',
                    symbol='GDP',
                    value=latest_value,
                    previous_value=previous_value,
                    change=change,
                    change_percent=change_percent,
                    unit='Billions USD',
                    frequency='Quarterly',
                    last_updated=gdp_data.index[-1].strftime('%Y-%m-%d'),
                    source='FRED' if country == 'US' else 'Alpha Vantage',
                    description='Total value of goods and services produced',
                    importance='High',
                    country=country,
                    category='GDP'
                )
                
        except Exception as e:
            logger.error(f"GDP indicator fetch failed: {e}")
            return None
    
    async def _get_inflation_indicator(self, country: str) -> Optional[EconomicIndicator]:
        """Get inflation indicator"""
        try:
            async with self.data_provider as provider:
                if country == 'US':
                    inflation_data = await provider.fetch_fred_data('CPIAUCSL')
                else:
                    inflation_data = await provider.fetch_alpha_vantage_economic_data('INFLATION')
                
                if inflation_data.empty:
                    return None
                
                # Get latest values
                latest_value = inflation_data.iloc[-1]['value']
                previous_value = inflation_data.iloc[-2]['value'] if len(inflation_data) > 1 else latest_value
                
                change = latest_value - previous_value
                change_percent = (change / previous_value) * 100 if previous_value != 0 else 0
                
                return EconomicIndicator(
                    name='Consumer Price Index',
                    symbol='CPI',
                    value=latest_value,
                    previous_value=previous_value,
                    change=change,
                    change_percent=change_percent,
                    unit='Index',
                    frequency='Monthly',
                    last_updated=inflation_data.index[-1].strftime('%Y-%m-%d'),
                    source='FRED' if country == 'US' else 'Alpha Vantage',
                    description='Measure of inflation based on consumer prices',
                    importance='High',
                    country=country,
                    category='Inflation'
                )
                
        except Exception as e:
            logger.error(f"Inflation indicator fetch failed: {e}")
            return None
    
    async def _get_unemployment_indicator(self, country: str) -> Optional[EconomicIndicator]:
        """Get unemployment indicator"""
        try:
            async with self.data_provider as provider:
                if country == 'US':
                    unemployment_data = await provider.fetch_fred_data('UNRATE')
                else:
                    unemployment_data = await provider.fetch_alpha_vantage_economic_data('UNEMPLOYMENT')
                
                if unemployment_data.empty:
                    return None
                
                # Get latest values
                latest_value = unemployment_data.iloc[-1]['value']
                previous_value = unemployment_data.iloc[-2]['value'] if len(unemployment_data) > 1 else latest_value
                
                change = latest_value - previous_value
                change_percent = (change / previous_value) * 100 if previous_value != 0 else 0
                
                return EconomicIndicator(
                    name='Unemployment Rate',
                    symbol='UNRATE',
                    value=latest_value,
                    previous_value=previous_value,
                    change=change,
                    change_percent=change_percent,
                    unit='Percent',
                    frequency='Monthly',
                    last_updated=unemployment_data.index[-1].strftime('%Y-%m-%d'),
                    source='FRED' if country == 'US' else 'Alpha Vantage',
                    description='Percentage of labor force that is unemployed',
                    importance='High',
                    country=country,
                    category='Employment'
                )
                
        except Exception as e:
            logger.error(f"Unemployment indicator fetch failed: {e}")
            return None
    
    async def _get_interest_rate_indicator(self, country: str) -> Optional[EconomicIndicator]:
        """Get interest rate indicator"""
        try:
            async with self.data_provider as provider:
                if country == 'US':
                    # Federal Funds Rate
                    rate_data = await provider.fetch_fred_data('FEDFUNDS')
                else:
                    # Would need country-specific rate series
                    rate_data = pd.DataFrame()
                
                if rate_data.empty:
                    return None
                
                # Get latest values
                latest_value = rate_data.iloc[-1]['value']
                previous_value = rate_data.iloc[-2]['value'] if len(rate_data) > 1 else latest_value
                
                change = latest_value - previous_value
                change_percent = (change / previous_value) * 100 if previous_value != 0 else 0
                
                return EconomicIndicator(
                    name='Federal Funds Rate' if country == 'US' else 'Central Bank Rate',
                    symbol='FEDFUNDS' if country == 'US' else 'CBRATE',
                    value=latest_value,
                    previous_value=previous_value,
                    change=change,
                    change_percent=change_percent,
                    unit='Percent',
                    frequency='Monthly',
                    last_updated=rate_data.index[-1].strftime('%Y-%m-%d'),
                    source='FRED',
                    description='Central bank interest rate',
                    importance='High',
                    country=country,
                    category='Interest Rates'
                )
                
        except Exception as e:
            logger.error(f"Interest rate indicator fetch failed: {e}")
            return None
    
    async def get_economic_calendar(self, start_date: str, end_date: str, 
                                  countries: List[str] = None) -> List[EconomicEvent]:
        """Get economic calendar events"""
        try:
            # This would typically integrate with a financial data provider
            # For now, return mock data
            events = []
            
            # Mock economic events
            mock_events = [
                {
                    'time': '2024-01-15 08:30',
                    'country': 'US',
                    'event': 'Consumer Price Index',
                    'importance': 'High',
                    'actual': 3.2,
                    'forecast': 3.1,
                    'previous': 3.0,
                    'unit': '%',
                    'impact': 'Positive'
                },
                {
                    'time': '2024-01-15 10:00',
                    'country': 'US',
                    'event': 'Retail Sales',
                    'importance': 'Medium',
                    'actual': 0.5,
                    'forecast': 0.3,
                    'previous': 0.2,
                    'unit': '%',
                    'impact': 'Positive'
                }
            ]
            
            for event_data in mock_events:
                events.append(EconomicEvent(**event_data))
            
            return events
            
        except Exception as e:
            logger.error(f"Economic calendar fetch failed: {e}")
            return []
    
    async def analyze_macroeconomic_impact(self, indicators: Dict[str, EconomicIndicator],
                                         market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze macroeconomic impact on markets"""
        try:
            analysis = {
                'overall_sentiment': 'Neutral',
                'key_drivers': [],
                'risks': [],
                'opportunities': [],
                'correlation_analysis': {},
                'impact_score': 0.0
            }
            
            # Analyze each indicator
            for indicator_name, indicator in indicators.items():
                impact = self._assess_indicator_impact(indicator)
                analysis['key_drivers'].append({
                    'indicator': indicator_name,
                    'impact': impact,
                    'value': indicator.value,
                    'change_percent': indicator.change_percent
                })
            
            # Calculate overall impact score
            impact_scores = []
            for driver in analysis['key_drivers']:
                if driver['impact'] == 'Positive':
                    impact_scores.append(1)
                elif driver['impact'] == 'Negative':
                    impact_scores.append(-1)
                else:
                    impact_scores.append(0)
            
            if impact_scores:
                analysis['impact_score'] = sum(impact_scores) / len(impact_scores)
            
            # Determine overall sentiment
            if analysis['impact_score'] > 0.3:
                analysis['overall_sentiment'] = 'Positive'
            elif analysis['impact_score'] < -0.3:
                analysis['overall_sentiment'] = 'Negative'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Macroeconomic impact analysis failed: {e}")
            return {}
    
    def _assess_indicator_impact(self, indicator: EconomicIndicator) -> str:
        """Assess the impact of an economic indicator"""
        try:
            if indicator.category == 'GDP':
                if indicator.change_percent > 0:
                    return 'Positive'
                else:
                    return 'Negative'
            
            elif indicator.category == 'Inflation':
                if indicator.change_percent > 0.5:  # High inflation
                    return 'Negative'
                elif indicator.change_percent < -0.5:  # Deflation
                    return 'Negative'
                else:
                    return 'Neutral'
            
            elif indicator.category == 'Employment':
                if indicator.change_percent < 0:  # Lower unemployment
                    return 'Positive'
                else:
                    return 'Negative'
            
            elif indicator.category == 'Interest Rates':
                if indicator.change_percent > 0:  # Higher rates
                    return 'Negative'
                else:
                    return 'Positive'
            
            return 'Neutral'
            
        except Exception as e:
            logger.error(f"Indicator impact assessment failed: {e}")
            return 'Neutral'
    
    async def get_market_sentiment(self) -> MarketSentiment:
        """Get market sentiment indicators"""
        try:
            # This would typically fetch from various sources
            # For now, return mock data
            return MarketSentiment(
                vix=18.5,
                vix_change=-2.1,
                fear_greed_index=65.0,
                put_call_ratio=0.85,
                insider_trading=0.02,
                institutional_flow=1500000000,
                retail_flow=-500000000,
                last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
        except Exception as e:
            logger.error(f"Market sentiment fetch failed: {e}")
            return MarketSentiment(0, 0, 0, 0, 0, 0, 0, '')
    
    def __del__(self):
        """Cleanup executor"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
