"""
Tables module for Equity Research Dashboard
Provides functionality for creating and displaying financial data tables,
statements, and formatted data displays.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')


class TableGenerator:
    """Generate formatted tables for financial data display"""
    
    def __init__(self):
        pass
    
    def create_financial_statement_table(self, data: Dict, statement_type: str = 'income') -> go.Figure:
        """
        Create a formatted table for financial statements
        
        Args:
            data: Financial statement data
            statement_type: Type of statement ('income', 'balance', 'cash_flow')
            
        Returns:
            Plotly table figure
        """
        if not data or 'data' not in data:
            return self._create_empty_table("No financial data available")
        
        df = data['data']
        if df.empty:
            return self._create_empty_table("No financial data available")
        
        # Format the data for display
        formatted_df = self._format_financial_data(df, statement_type)
        
        # Create table
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Metric'] + list(formatted_df.columns),
                fill_color='#667eea',
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[formatted_df.index] + [formatted_df[col] for col in formatted_df.columns],
                fill_color='lavender',
                font=dict(size=11),
                align='left',
                height=30
            )
        )])
        
        fig.update_layout(
            title=f"{statement_type.replace('_', ' ').title()} Statement",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def create_ratio_comparison_table(self, ratios: Dict, peer_ratios: Optional[Dict] = None) -> go.Figure:
        """
        Create a table comparing financial ratios
        
        Args:
            ratios: Company ratios
            peer_ratios: Peer company ratios
            
        Returns:
            Plotly table figure
        """
        if not ratios:
            return self._create_empty_table("No ratio data available")
        
        # Prepare data for table
        ratio_data = []
        for category, metrics in ratios.items():
            for metric, value in metrics.items():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    ratio_data.append({
                        'Category': category,
                        'Metric': metric,
                        'Value': value,
                        'Peer Avg': peer_ratios.get(category, {}).get(metric, 'N/A') if peer_ratios else 'N/A'
                    })
        
        if not ratio_data:
            return self._create_empty_table("No ratio data available")
        
        df = pd.DataFrame(ratio_data)
        
        # Format values
        df['Value'] = df['Value'].apply(self._format_ratio_value)
        df['Peer Avg'] = df['Peer Avg'].apply(lambda x: self._format_ratio_value(x) if x != 'N/A' else 'N/A')
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Category', 'Metric', 'Value', 'Peer Average'],
                fill_color='#667eea',
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[df['Category'], df['Metric'], df['Value'], df['Peer Avg']],
                fill_color='lavender',
                font=dict(size=11),
                align='left',
                height=30
            )
        )])
        
        fig.update_layout(
            title="Financial Ratios Comparison",
            height=500,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def create_valuation_table(self, valuation_data: Dict) -> go.Figure:
        """
        Create a table for valuation metrics
        
        Args:
            valuation_data: Valuation metrics and multiples
            
        Returns:
            Plotly table figure
        """
        if not valuation_data:
            return self._create_empty_table("No valuation data available")
        
        # Prepare data
        table_data = []
        for category, metrics in valuation_data.items():
            for metric, value in metrics.items():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    table_data.append({
                        'Category': category,
                        'Metric': metric,
                        'Value': value
                    })
        
        if not table_data:
            return self._create_empty_table("No valuation data available")
        
        df = pd.DataFrame(table_data)
        df['Value'] = df['Value'].apply(self._format_valuation_value)
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Category', 'Metric', 'Value'],
                fill_color='#667eea',
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[df['Category'], df['Metric'], df['Value']],
                fill_color='lavender',
                font=dict(size=11),
                align='left',
                height=30
            )
        )])
        
        fig.update_layout(
            title="Valuation Metrics",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def create_risk_metrics_table(self, risk_data: Dict) -> go.Figure:
        """
        Create a table for risk metrics
        
        Args:
            risk_data: Risk metrics and statistics
            
        Returns:
            Plotly table figure
        """
        if not risk_data:
            return self._create_empty_table("No risk data available")
        
        # Prepare data
        table_data = []
        for category, metrics in risk_data.items():
            for metric, value in metrics.items():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    table_data.append({
                        'Category': category,
                        'Metric': metric,
                        'Value': value
                    })
        
        if not table_data:
            return self._create_empty_table("No risk data available")
        
        df = pd.DataFrame(table_data)
        df['Value'] = df['Value'].apply(self._format_risk_value)
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Category', 'Metric', 'Value'],
                fill_color='#667eea',
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[df['Category'], df['Metric'], df['Value']],
                fill_color='lavender',
                font=dict(size=11),
                align='left',
                height=30
            )
        )])
        
        fig.update_layout(
            title="Risk Metrics",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def create_portfolio_table(self, portfolio_data: List[Dict]) -> go.Figure:
        """
        Create a table for portfolio holdings
        
        Args:
            portfolio_data: List of portfolio holdings
            
        Returns:
            Plotly table figure
        """
        if not portfolio_data:
            return self._create_empty_table("No portfolio data available")
        
        df = pd.DataFrame(portfolio_data)
        
        # Format values
        if 'marketValue' in df.columns:
            df['Market Value'] = df['marketValue'].apply(self._format_currency)
        if 'unrealizedPnL' in df.columns:
            df['Unrealized P&L'] = df['unrealizedPnL'].apply(self._format_currency)
        if 'weight' in df.columns:
            df['Weight'] = df['weight'].apply(self._format_percent)
        if 'avgPrice' in df.columns:
            df['Avg Price'] = df['avgPrice'].apply(self._format_currency)
        if 'currentPrice' in df.columns:
            df['Current Price'] = df['currentPrice'].apply(self._format_currency)
        
        # Select columns to display
        display_columns = ['symbol', 'shares', 'Avg Price', 'Current Price', 'Market Value', 'Unrealized P&L', 'Weight']
        available_columns = [col for col in display_columns if col in df.columns]
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[col.replace('symbol', 'Symbol').replace('shares', 'Shares') for col in available_columns],
                fill_color='#667eea',
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[df[col] for col in available_columns],
                fill_color='lavender',
                font=dict(size=11),
                align='left',
                height=30
            )
        )])
        
        fig.update_layout(
            title="Portfolio Holdings",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def create_earnings_table(self, earnings_data: Dict) -> go.Figure:
        """
        Create a table for earnings data
        
        Args:
            earnings_data: Earnings and estimates data
            
        Returns:
            Plotly table figure
        """
        if not earnings_data or 'earnings' not in earnings_data:
            return self._create_empty_table("No earnings data available")
        
        earnings = earnings_data['earnings']
        if not earnings:
            return self._create_empty_table("No earnings data available")
        
        # Prepare data
        table_data = []
        for quarter in earnings:
            table_data.append({
                'Date': quarter.get('date', 'N/A'),
                'EPS': self._format_currency(quarter.get('eps', 0)),
                'Revenue': self._format_large_number(quarter.get('revenue', 0)),
                'Estimate': self._format_currency(quarter.get('estimate', 0)),
                'Surprise': self._format_percent(quarter.get('surprise', 0))
            })
        
        df = pd.DataFrame(table_data)
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Date', 'EPS', 'Revenue', 'Estimate', 'Surprise'],
                fill_color='#667eea',
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[df['Date'], df['EPS'], df['Revenue'], df['Estimate'], df['Surprise']],
                fill_color='lavender',
                font=dict(size=11),
                align='left',
                height=30
            )
        )])
        
        fig.update_layout(
            title="Earnings History",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def create_analyst_table(self, analyst_data: Dict) -> go.Figure:
        """
        Create a table for analyst recommendations
        
        Args:
            analyst_data: Analyst recommendations and ratings
            
        Returns:
            Plotly table figure
        """
        if not analyst_data or 'recommendations' not in analyst_data:
            return self._create_empty_table("No analyst data available")
        
        recommendations = analyst_data['recommendations']
        if not recommendations:
            return self._create_empty_table("No analyst data available")
        
        # Prepare data
        table_data = []
        for rec in recommendations:
            table_data.append({
                'Firm': rec.get('firm', 'N/A'),
                'Rating': rec.get('rating', 'N/A'),
                'Target Price': self._format_currency(rec.get('targetPrice', 0)),
                'Date': rec.get('date', 'N/A')
            })
        
        df = pd.DataFrame(table_data)
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Firm', 'Rating', 'Target Price', 'Date'],
                fill_color='#667eea',
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[df['Firm'], df['Rating'], df['Target Price'], df['Date']],
                fill_color='lavender',
                font=dict(size=11),
                align='left',
                height=30
            )
        )])
        
        fig.update_layout(
            title="Analyst Recommendations",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def _format_financial_data(self, df: pd.DataFrame, statement_type: str) -> pd.DataFrame:
        """Format financial data for display"""
        formatted_df = df.copy()
        
        for col in formatted_df.columns:
            if col != 'Metric':
                formatted_df[col] = formatted_df[col].apply(self._format_large_number)
        
        return formatted_df
    
    def _format_ratio_value(self, value: Union[float, str]) -> str:
        """Format ratio values"""
        if isinstance(value, str):
            return value
        if np.isnan(value):
            return 'N/A'
        if abs(value) >= 1:
            return f"{value:.2f}"
        else:
            return f"{value:.4f}"
    
    def _format_valuation_value(self, value: Union[float, str]) -> str:
        """Format valuation values"""
        if isinstance(value, str):
            return value
        if np.isnan(value):
            return 'N/A'
        if abs(value) >= 1:
            return f"{value:.2f}"
        else:
            return f"{value:.4f}"
    
    def _format_risk_value(self, value: Union[float, str]) -> str:
        """Format risk values"""
        if isinstance(value, str):
            return value
        if np.isnan(value):
            return 'N/A'
        if abs(value) >= 1:
            return f"{value:.2f}"
        else:
            return f"{value:.4f}"
    
    def _format_currency(self, value: Union[float, str]) -> str:
        """Format currency values"""
        if isinstance(value, str):
            return value
        if np.isnan(value):
            return 'N/A'
        return f"${value:,.2f}"
    
    def _format_percent(self, value: Union[float, str]) -> str:
        """Format percentage values"""
        if isinstance(value, str):
            return value
        if np.isnan(value):
            return 'N/A'
        return f"{value:.2f}%"
    
    def _format_large_number(self, value: Union[float, str]) -> str:
        """Format large numbers with K, M, B suffixes"""
        if isinstance(value, str):
            return value
        if np.isnan(value):
            return 'N/A'
        
        if abs(value) >= 1e12:
            return f"${value/1e12:.2f}T"
        elif abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.2f}K"
        else:
            return f"${value:,.2f}"
    
    def _create_empty_table(self, message: str) -> go.Figure:
        """Create an empty table with a message"""
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Message'],
                fill_color='#667eea',
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[[message]],
                fill_color='lavender',
                font=dict(size=11),
                align='left',
                height=30
            )
        )])
        
        fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig


class FinancialTableFormatter:
    """Format financial data for table display"""
    
    @staticmethod
    def format_income_statement(df: pd.DataFrame) -> pd.DataFrame:
        """Format income statement data"""
        formatted_df = df.copy()
        
        # Format revenue and expense items
        for col in formatted_df.columns:
            if col != 'Metric':
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: f"${x:,.0f}" if pd.notna(x) else 'N/A'
                )
        
        return formatted_df
    
    @staticmethod
    def format_balance_sheet(df: pd.DataFrame) -> pd.DataFrame:
        """Format balance sheet data"""
        formatted_df = df.copy()
        
        # Format asset and liability items
        for col in formatted_df.columns:
            if col != 'Metric':
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: f"${x:,.0f}" if pd.notna(x) else 'N/A'
                )
        
        return formatted_df
    
    @staticmethod
    def format_cash_flow(df: pd.DataFrame) -> pd.DataFrame:
        """Format cash flow statement data"""
        formatted_df = df.copy()
        
        # Format cash flow items
        for col in formatted_df.columns:
            if col != 'Metric':
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: f"${x:,.0f}" if pd.notna(x) else 'N/A'
                )
        
        return formatted_df
