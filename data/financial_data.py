"""
Financial Data Processing Module
Handles financial statements, ratios, and data cleaning operations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
import yfinance as yf
from app.utils import validator, formatter, calculator, error_handler


class FinancialDataProcessor:
    """Process and clean financial data"""
    
    def __init__(self):
        self.currency_converter = {
            'USD': 1.0,
            'EUR': 1.18,
            'GBP': 1.38,
            'JPY': 0.009,
            'CAD': 0.79,
            'AUD': 0.73
        }
    
    def clean_financial_statement(self, statement_data: pd.DataFrame, statement_type: str) -> pd.DataFrame:
        """Clean and standardize financial statement data"""
        if statement_data.empty:
            return statement_data
        
        # Create a copy to avoid modifying original
        cleaned_data = statement_data.copy()
        
        # Remove rows with all NaN values
        cleaned_data = cleaned_data.dropna(how='all')
        
        # Convert string numbers to float
        for col in cleaned_data.columns:
            if cleaned_data[col].dtype == 'object':
                cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')
        
        # Handle negative values (parentheses in financial statements)
        for col in cleaned_data.columns:
            if cleaned_data[col].dtype in ['float64', 'int64']:
                # Convert negative values (stored as positive with sign)
                cleaned_data[col] = cleaned_data[col].abs()
        
        # Standardize column names
        cleaned_data.columns = [col.strip().upper() for col in cleaned_data.columns]
        
        # Sort by date (most recent first)
        if len(cleaned_data.columns) > 0:
            date_cols = [col for col in cleaned_data.columns if 'DATE' in col or 'YEAR' in col]
            if date_cols:
                cleaned_data = cleaned_data.sort_values(by=date_cols[0], ascending=False)
        
        return cleaned_data
    
    def calculate_financial_ratios(self, income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame, 
                                 cash_flow: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate comprehensive financial ratios"""
        ratios = {}
        
        try:
            # Get most recent data
            if not income_stmt.empty:
                latest_income = income_stmt.iloc[0]
                ratios['profitability'] = self._calculate_profitability_ratios(latest_income, balance_sheet.iloc[0] if not balance_sheet.empty else None)
            
            if not balance_sheet.empty:
                latest_balance = balance_sheet.iloc[0]
                ratios['liquidity'] = self._calculate_liquidity_ratios(latest_balance)
                ratios['solvency'] = self._calculate_solvency_ratios(latest_balance)
                ratios['efficiency'] = self._calculate_efficiency_ratios(latest_income, latest_balance)
            
            if not cash_flow.empty:
                latest_cash_flow = cash_flow.iloc[0]
                ratios['cash_flow'] = self._calculate_cash_flow_ratios(latest_cash_flow, latest_balance)
            
            # Calculate growth rates if historical data available
            if len(income_stmt) > 1:
                ratios['growth'] = self._calculate_growth_rates(income_stmt, balance_sheet, cash_flow)
            
        except Exception as e:
            error_handler.handle_data_error(e, "calculate_financial_ratios")
        
        return ratios
    
    def _calculate_profitability_ratios(self, income_data: pd.Series, balance_data: pd.Series) -> Dict[str, float]:
        """Calculate profitability ratios"""
        ratios = {}
        
        try:
            # Extract key metrics
            revenue = self._get_value(income_data, ['TOTAL REVENUE', 'REVENUE', 'SALES'])
            net_income = self._get_value(income_data, ['NET INCOME', 'NET EARNINGS'])
            gross_profit = self._get_value(income_data, ['GROSS PROFIT'])
            ebit = self._get_value(income_data, ['EBIT', 'OPERATING INCOME'])
            ebitda = self._get_value(income_data, ['EBITDA'])
            
            total_assets = self._get_value(balance_data, ['TOTAL ASSETS']) if balance_data is not None else None
            total_equity = self._get_value(balance_data, ['TOTAL EQUITY', 'SHAREHOLDERS EQUITY']) if balance_data is not None else None
            
            # Calculate ratios
            if revenue and revenue != 0:
                if net_income:
                    ratios['net_margin'] = net_income / revenue
                if gross_profit:
                    ratios['gross_margin'] = gross_profit / revenue
                if ebit:
                    ratios['operating_margin'] = ebit / revenue
            
            if total_assets and total_assets != 0:
                if net_income:
                    ratios['roa'] = net_income / total_assets
                if ebit:
                    ratios['roa_operating'] = ebit / total_assets
            
            if total_equity and total_equity != 0 and net_income:
                ratios['roe'] = net_income / total_equity
            
            if ebit and ebitda:
                ratios['ebitda_margin'] = ebitda / revenue if revenue and revenue != 0 else None
        
        except Exception as e:
            error_handler.handle_data_error(e, "profitability_ratios")
        
        return ratios
    
    def _calculate_liquidity_ratios(self, balance_data: pd.Series) -> Dict[str, float]:
        """Calculate liquidity ratios"""
        ratios = {}
        
        try:
            current_assets = self._get_value(balance_data, ['TOTAL CURRENT ASSETS', 'CURRENT ASSETS'])
            current_liabilities = self._get_value(balance_data, ['TOTAL CURRENT LIABILITIES', 'CURRENT LIABILITIES'])
            cash = self._get_value(balance_data, ['CASH AND CASH EQUIVALENTS', 'CASH'])
            inventory = self._get_value(balance_data, ['INVENTORY'])
            
            if current_assets and current_liabilities and current_liabilities != 0:
                ratios['current_ratio'] = current_assets / current_liabilities
            
            if cash and current_liabilities and current_liabilities != 0:
                ratios['cash_ratio'] = cash / current_liabilities
            
            if current_assets and inventory and current_liabilities and current_liabilities != 0:
                quick_assets = current_assets - inventory
                ratios['quick_ratio'] = quick_assets / current_liabilities
        
        except Exception as e:
            error_handler.handle_data_error(e, "liquidity_ratios")
        
        return ratios
    
    def _calculate_solvency_ratios(self, balance_data: pd.Series) -> Dict[str, float]:
        """Calculate solvency ratios"""
        ratios = {}
        
        try:
            total_assets = self._get_value(balance_data, ['TOTAL ASSETS'])
            total_liabilities = self._get_value(balance_data, ['TOTAL LIABILITIES'])
            total_debt = self._get_value(balance_data, ['TOTAL DEBT', 'LONG TERM DEBT'])
            total_equity = self._get_value(balance_data, ['TOTAL EQUITY', 'SHAREHOLDERS EQUITY'])
            
            if total_assets and total_assets != 0:
                if total_liabilities:
                    ratios['debt_to_assets'] = total_liabilities / total_assets
                if total_debt:
                    ratios['debt_to_assets_debt'] = total_debt / total_assets
            
            if total_equity and total_equity != 0:
                if total_debt:
                    ratios['debt_to_equity'] = total_debt / total_equity
                if total_liabilities:
                    ratios['liabilities_to_equity'] = total_liabilities / total_equity
            
            if total_assets and total_liabilities:
                ratios['equity_ratio'] = (total_assets - total_liabilities) / total_assets
        
        except Exception as e:
            error_handler.handle_data_error(e, "solvency_ratios")
        
        return ratios
    
    def _calculate_efficiency_ratios(self, income_data: pd.Series, balance_data: pd.Series) -> Dict[str, float]:
        """Calculate efficiency ratios"""
        ratios = {}
        
        try:
            revenue = self._get_value(income_data, ['TOTAL REVENUE', 'REVENUE', 'SALES'])
            total_assets = self._get_value(balance_data, ['TOTAL ASSETS'])
            inventory = self._get_value(balance_data, ['INVENTORY'])
            accounts_receivable = self._get_value(balance_data, ['ACCOUNTS RECEIVABLE', 'NET RECEIVABLES'])
            accounts_payable = self._get_value(balance_data, ['ACCOUNTS PAYABLE'])
            
            if revenue and total_assets and total_assets != 0:
                ratios['asset_turnover'] = revenue / total_assets
            
            if revenue and inventory and inventory != 0:
                ratios['inventory_turnover'] = revenue / inventory
            
            if revenue and accounts_receivable and accounts_receivable != 0:
                ratios['receivables_turnover'] = revenue / accounts_receivable
            
            if accounts_payable and accounts_payable != 0:
                # Assuming cost of goods sold is roughly 70% of revenue
                cogs = revenue * 0.7 if revenue else None
                if cogs:
                    ratios['payables_turnover'] = cogs / accounts_payable
        
        except Exception as e:
            error_handler.handle_data_error(e, "efficiency_ratios")
        
        return ratios
    
    def _calculate_cash_flow_ratios(self, cash_flow_data: pd.Series, balance_data: pd.Series) -> Dict[str, float]:
        """Calculate cash flow ratios"""
        ratios = {}
        
        try:
            operating_cash_flow = self._get_value(cash_flow_data, ['OPERATING CASH FLOW', 'CASH FROM OPERATIONS'])
            free_cash_flow = self._get_value(cash_flow_data, ['FREE CASH FLOW'])
            capital_expenditure = self._get_value(cash_flow_data, ['CAPITAL EXPENDITURE'])
            total_debt = self._get_value(balance_data, ['TOTAL DEBT', 'LONG TERM DEBT']) if balance_data is not None else None
            
            if operating_cash_flow and total_debt and total_debt != 0:
                ratios['operating_cash_flow_to_debt'] = operating_cash_flow / total_debt
            
            if free_cash_flow and total_debt and total_debt != 0:
                ratios['free_cash_flow_to_debt'] = free_cash_flow / total_debt
            
            if operating_cash_flow and capital_expenditure and capital_expenditure != 0:
                ratios['cash_flow_coverage'] = operating_cash_flow / abs(capital_expenditure)
        
        except Exception as e:
            error_handler.handle_data_error(e, "cash_flow_ratios")
        
        return ratios
    
    def _calculate_growth_rates(self, income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame, 
                              cash_flow: pd.DataFrame) -> Dict[str, float]:
        """Calculate growth rates"""
        growth_rates = {}
        
        try:
            # Revenue growth
            if len(income_stmt) >= 2:
                revenue_col = self._find_column(income_stmt, ['TOTAL REVENUE', 'REVENUE', 'SALES'])
                if revenue_col:
                    current_revenue = income_stmt.iloc[0][revenue_col]
                    previous_revenue = income_stmt.iloc[1][revenue_col]
                    if previous_revenue and previous_revenue != 0:
                        growth_rates['revenue_growth'] = (current_revenue - previous_revenue) / previous_revenue
            
            # Net income growth
            if len(income_stmt) >= 2:
                net_income_col = self._find_column(income_stmt, ['NET INCOME', 'NET EARNINGS'])
                if net_income_col:
                    current_ni = income_stmt.iloc[0][net_income_col]
                    previous_ni = income_stmt.iloc[1][net_income_col]
                    if previous_ni and previous_ni != 0:
                        growth_rates['net_income_growth'] = (current_ni - previous_ni) / previous_ni
            
            # Asset growth
            if len(balance_sheet) >= 2:
                assets_col = self._find_column(balance_sheet, ['TOTAL ASSETS'])
                if assets_col:
                    current_assets = balance_sheet.iloc[0][assets_col]
                    previous_assets = balance_sheet.iloc[1][assets_col]
                    if previous_assets and previous_assets != 0:
                        growth_rates['asset_growth'] = (current_assets - previous_assets) / previous_assets
        
        except Exception as e:
            error_handler.handle_data_error(e, "growth_rates")
        
        return growth_rates
    
    def _get_value(self, data: pd.Series, possible_names: List[str]) -> Optional[float]:
        """Get value from series using possible column names"""
        for name in possible_names:
            if name in data.index:
                value = data[name]
                if pd.notna(value) and value != 0:
                    return float(value)
        return None
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find column in dataframe using possible names"""
        for name in possible_names:
            if name in df.columns:
                return name
        return None
    
    def normalize_currency(self, data: pd.DataFrame, from_currency: str, to_currency: str = 'USD') -> pd.DataFrame:
        """Normalize currency values"""
        if from_currency == to_currency:
            return data
        
        conversion_rate = self.currency_converter.get(from_currency, 1.0) / self.currency_converter.get(to_currency, 1.0)
        
        # Convert numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data[numeric_cols] = data[numeric_cols] * conversion_rate
        
        return data
    
    def calculate_valuation_metrics(self, stock_data: pd.Series, financial_data: Dict) -> Dict[str, float]:
        """Calculate valuation metrics"""
        metrics = {}
        
        try:
            current_price = stock_data.get('Close', 0)
            if not current_price:
                return metrics
            
            # P/E Ratio
            if 'net_income' in financial_data and financial_data['net_income']:
                shares_outstanding = stock_data.get('shares_outstanding', 1)
                eps = financial_data['net_income'] / shares_outstanding
                if eps and eps != 0:
                    metrics['pe_ratio'] = current_price / eps
            
            # P/B Ratio
            if 'total_equity' in financial_data and financial_data['total_equity']:
                shares_outstanding = stock_data.get('shares_outstanding', 1)
                book_value_per_share = financial_data['total_equity'] / shares_outstanding
                if book_value_per_share and book_value_per_share != 0:
                    metrics['pb_ratio'] = current_price / book_value_per_share
            
            # P/S Ratio
            if 'revenue' in financial_data and financial_data['revenue']:
                shares_outstanding = stock_data.get('shares_outstanding', 1)
                sales_per_share = financial_data['revenue'] / shares_outstanding
                if sales_per_share and sales_per_share != 0:
                    metrics['ps_ratio'] = current_price / sales_per_share
            
            # EV/EBITDA
            if 'ebitda' in financial_data and financial_data['ebitda']:
                market_cap = current_price * stock_data.get('shares_outstanding', 1)
                total_debt = financial_data.get('total_debt', 0)
                cash = financial_data.get('cash', 0)
                enterprise_value = market_cap + total_debt - cash
                
                if financial_data['ebitda'] and financial_data['ebitda'] != 0:
                    metrics['ev_ebitda'] = enterprise_value / financial_data['ebitda']
        
        except Exception as e:
            error_handler.handle_data_error(e, "valuation_metrics")
        
        return metrics
    
    def calculate_technical_indicators(self, price_data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate technical indicators"""
        indicators = {}
        
        try:
            if price_data.empty:
                return indicators
            
            # Moving averages
            indicators['sma_20'] = price_data['Close'].rolling(window=20).mean()
            indicators['sma_50'] = price_data['Close'].rolling(window=50).mean()
            indicators['sma_200'] = price_data['Close'].rolling(window=200).mean()
            
            # Exponential moving averages
            indicators['ema_12'] = price_data['Close'].ewm(span=12).mean()
            indicators['ema_26'] = price_data['Close'].ewm(span=26).mean()
            
            # MACD
            ema_12 = indicators['ema_12']
            ema_26 = indicators['ema_26']
            indicators['macd'] = ema_12 - ema_26
            indicators['macd_signal'] = indicators['macd'].ewm(span=9).mean()
            indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
            
            # RSI
            delta = price_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            sma_20 = indicators['sma_20']
            std_20 = price_data['Close'].rolling(window=20).std()
            indicators['bb_upper'] = sma_20 + (std_20 * 2)
            indicators['bb_lower'] = sma_20 - (std_20 * 2)
            indicators['bb_middle'] = sma_20
            
            # Volume indicators
            if 'Volume' in price_data.columns:
                indicators['volume_sma'] = price_data['Volume'].rolling(window=20).mean()
                indicators['volume_ratio'] = price_data['Volume'] / indicators['volume_sma']
            
            # ATR (Average True Range)
            high_low = price_data['High'] - price_data['Low']
            high_close = np.abs(price_data['High'] - price_data['Close'].shift())
            low_close = np.abs(price_data['Low'] - price_data['Close'].shift())
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            indicators['atr'] = true_range.rolling(window=14).mean()
        
        except Exception as e:
            error_handler.handle_data_error(e, "technical_indicators")
        
        return indicators
    
    def detect_anomalies(self, data: pd.Series, method: str = 'zscore', threshold: float = 3.0) -> pd.Series:
        """Detect anomalies in financial data"""
        anomalies = pd.Series(index=data.index, data=False)
        
        try:
            if method == 'zscore':
                z_scores = np.abs((data - data.mean()) / data.std())
                anomalies = z_scores > threshold
            
            elif method == 'iqr':
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                anomalies = (data < lower_bound) | (data > upper_bound)
            
            elif method == 'mad':
                median = data.median()
                mad = np.median(np.abs(data - median))
                modified_z_scores = 0.6745 * (data - median) / mad
                anomalies = np.abs(modified_z_scores) > threshold
        
        except Exception as e:
            error_handler.handle_data_error(e, "anomaly_detection")
        
        return anomalies
    
    def calculate_rolling_metrics(self, data: pd.DataFrame, window: int = 252) -> Dict[str, pd.Series]:
        """Calculate rolling financial metrics"""
        metrics = {}
        
        try:
            if 'Close' in data.columns:
                returns = data['Close'].pct_change().dropna()
                
                # Rolling volatility
                metrics['rolling_volatility'] = returns.rolling(window=window).std() * np.sqrt(252)
                
                # Rolling Sharpe ratio
                risk_free_rate = 0.02  # 2% annual risk-free rate
                excess_returns = returns - risk_free_rate / 252
                rolling_sharpe = excess_returns.rolling(window=window).mean() / excess_returns.rolling(window=window).std() * np.sqrt(252)
                metrics['rolling_sharpe'] = rolling_sharpe
                
                # Rolling beta (if market data available)
                if 'Market_Returns' in data.columns:
                    market_returns = data['Market_Returns']
                    rolling_beta = returns.rolling(window=window).cov(market_returns) / market_returns.rolling(window=window).var()
                    metrics['rolling_beta'] = rolling_beta
                
                # Rolling maximum drawdown
                cumulative_returns = (1 + returns).cumprod()
                rolling_max = cumulative_returns.rolling(window=window).max()
                rolling_drawdown = (cumulative_returns - rolling_max) / rolling_max
                metrics['rolling_drawdown'] = rolling_drawdown
        
        except Exception as e:
            error_handler.handle_data_error(e, "rolling_metrics")
        
        return metrics


class FinancialDataAggregator:
    """Aggregate financial data from multiple sources"""
    
    def __init__(self):
        self.processor = FinancialDataProcessor()
    
    def aggregate_company_data(self, symbol: str) -> Dict[str, Any]:
        """Aggregate all company financial data"""
        aggregated_data = {}
        
        try:
            # Get stock info
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get financial statements
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            # Clean statements
            cleaned_income = self.processor.clean_financial_statement(income_stmt, 'income')
            cleaned_balance = self.processor.clean_financial_statement(balance_sheet, 'balance')
            cleaned_cash_flow = self.processor.clean_financial_statement(cash_flow, 'cash_flow')
            
            # Calculate ratios
            ratios = self.processor.calculate_financial_ratios(cleaned_income, cleaned_balance, cleaned_cash_flow)
            
            # Get latest stock data
            stock_data = stock.history(period='1y')
            
            # Calculate technical indicators
            technical_indicators = self.processor.calculate_technical_indicators(stock_data)
            
            # Aggregate all data
            aggregated_data = {
                'symbol': symbol,
                'company_info': info,
                'financial_statements': {
                    'income_statement': cleaned_income,
                    'balance_sheet': cleaned_balance,
                    'cash_flow': cleaned_cash_flow
                },
                'financial_ratios': ratios,
                'stock_data': stock_data,
                'technical_indicators': technical_indicators,
                'last_updated': datetime.now().isoformat()
            }
        
        except Exception as e:
            error_handler.handle_data_error(e, f"aggregate_company_data for {symbol}")
        
        return aggregated_data
    
    def compare_companies(self, symbols: List[str]) -> Dict[str, Any]:
        """Compare multiple companies"""
        comparison_data = {}
        
        try:
            for symbol in symbols:
                if validator.is_valid_stock_symbol(symbol):
                    company_data = self.aggregate_company_data(symbol)
                    if company_data:
                        comparison_data[symbol] = company_data
            
            # Calculate relative metrics
            if len(comparison_data) > 1:
                comparison_data['relative_metrics'] = self._calculate_relative_metrics(comparison_data)
        
        except Exception as e:
            error_handler.handle_data_error(e, "compare_companies")
        
        return comparison_data
    
    def _calculate_relative_metrics(self, companies_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate relative metrics between companies"""
        relative_metrics = {}
        
        try:
            # Extract key metrics for comparison
            metrics_data = {}
            for symbol, data in companies_data.items():
                if symbol != 'relative_metrics':
                    ratios = data.get('financial_ratios', {})
                    metrics_data[symbol] = {
                        'pe_ratio': ratios.get('valuation', {}).get('pe_ratio'),
                        'pb_ratio': ratios.get('valuation', {}).get('pb_ratio'),
                        'roe': ratios.get('profitability', {}).get('roe'),
                        'roa': ratios.get('profitability', {}).get('roa'),
                        'debt_to_equity': ratios.get('solvency', {}).get('debt_to_equity'),
                        'current_ratio': ratios.get('liquidity', {}).get('current_ratio')
                    }
            
            # Calculate averages and rankings
            for metric in ['pe_ratio', 'pb_ratio', 'roe', 'roa', 'debt_to_equity', 'current_ratio']:
                values = [data[metric] for data in metrics_data.values() if data[metric] is not None]
                if values:
                    relative_metrics[f'{metric}_avg'] = np.mean(values)
                    relative_metrics[f'{metric}_median'] = np.median(values)
                    
                    # Rankings (lower is better for some metrics)
                    rankings = {}
                    for symbol, data in metrics_data.items():
                        if data[metric] is not None:
                            if metric in ['pe_ratio', 'pb_ratio', 'debt_to_equity']:
                                # Lower is better
                                rank = sum(1 for v in values if v < data[metric]) + 1
                            else:
                                # Higher is better
                                rank = sum(1 for v in values if v > data[metric]) + 1
                            rankings[symbol] = rank
                    
                    relative_metrics[f'{metric}_rankings'] = rankings
        
        except Exception as e:
            error_handler.handle_data_error(e, "relative_metrics")
        
        return relative_metrics


# Global instances
financial_processor = FinancialDataProcessor()
financial_aggregator = FinancialDataAggregator()