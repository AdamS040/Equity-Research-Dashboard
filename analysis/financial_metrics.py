"""
Financial Metrics Analysis Module
Comprehensive financial ratio calculations and analysis
"""
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


def safe_financial_lookup(df: pd.DataFrame, label: str, column_index: int = 0) -> float:
    """
    Safe accessor for financial statement data with fallback logic for missing labels.
    
    This function handles common variations in yfinance data labels and returns np.nan
    for missing data instead of raising KeyError or IndexError.
    
    Args:
        df (pd.DataFrame): Financial statement DataFrame (income statement, balance sheet, etc.)
        label (str): The financial metric label to look up
        column_index (int): Column index to extract (default 0 for most recent period)
        
    Returns:
        float: The financial metric value or np.nan if not found
        
    Examples:
        >>> revenue = safe_financial_lookup(income_stmt, 'Total Revenue')
        >>> assets = safe_financial_lookup(balance_sheet, 'Total Assets')
    """
    if df is None or df.empty:
        return np.nan
    
    # Direct lookup first
    if label in df.index:
        try:
            return float(df.loc[label].iloc[column_index])
        except (IndexError, KeyError, ValueError):
            return np.nan
    
    # Case-insensitive lookup
    label_lower = label.lower()
    for idx in df.index:
        if idx.lower() == label_lower:
            try:
                return float(df.loc[idx].iloc[column_index])
            except (IndexError, KeyError, ValueError):
                return np.nan
    
    # Common label variations mapping
    label_variations = {
        'Total Revenue': ['Revenue', 'Total Revenue', 'Sales', 'Net Sales', 'Operating Revenue'],
        'Net Income': ['Net Income', 'Net Earnings', 'Profit After Tax', 'Net Profit', 'Earnings'],
        'Gross Profit': ['Gross Profit', 'Gross Income', 'Gross Earnings'],
        'Operating Income': ['Operating Income', 'Operating Profit', 'Operating Earnings', 'EBIT'],
        'EBIT': ['EBIT', 'Operating Income', 'Operating Profit', 'Earnings Before Interest and Tax'],
        'Total Assets': ['Total Assets', 'Assets', 'Total Asset'],
        'Total Current Assets': ['Current Assets', 'Total Current Assets', 'Current Asset'],
        'Total Current Liabilities': ['Current Liabilities', 'Total Current Liabilities', 'Current Liability'],
        'Total Stockholder Equity': ['Stockholders Equity', 'Total Stockholder Equity', 'Shareholders Equity', 'Total Equity', 'Equity'],
        'Cash': ['Cash', 'Cash and Cash Equivalents', 'Cash & Cash Equivalents'],
        'Inventory': ['Inventory', 'Inventories', 'Total Inventory'],
        'Net Receivables': ['Accounts Receivable', 'Net Receivables', 'Receivables', 'Trade Receivables'],
        'Accounts Payable': ['Accounts Payable', 'Payables', 'Trade Payables'],
        'Total Debt': ['Total Debt', 'Debt', 'Total Liabilities', 'Long Term Debt']
    }
    
    # Check variations for the requested label
    if label in label_variations:
        for variation in label_variations[label]:
            if variation in df.index:
                try:
                    return float(df.loc[variation].iloc[column_index])
                except (IndexError, KeyError, ValueError):
                    continue
    
    # Partial match lookup (case-insensitive)
    for idx in df.index:
        if label_lower in idx.lower() or idx.lower() in label_lower:
            try:
                return float(df.loc[idx].iloc[column_index])
            except (IndexError, KeyError, ValueError):
                continue
    
    return np.nan


class FinancialAnalyzer:
    """
    Comprehensive financial metrics analyzer
    Calculates various financial ratios and indicators
    """
    
    def __init__(self):
        """Initialize the financial analyzer"""
        pass
    
    def get_financial_statements(self, symbol: str) -> Dict:
        """
        Get comprehensive financial statements
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Financial statements data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            return {
                'income_statement': ticker.income_stmt,
                'balance_sheet': ticker.balance_sheet,
                'cash_flow': ticker.cashflow,
                'info': ticker.info
            }
        except Exception as e:
            print(f"Error fetching financial statements for {symbol}: {e}")
            return {}
    
    def calculate_profitability_ratios(self, symbol: str) -> Dict:
        """
        Calculate profitability ratios
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Profitability ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            income_stmt = ticker.income_stmt
            balance_sheet = ticker.balance_sheet
            info = ticker.info
            
            if income_stmt.empty or balance_sheet.empty:
                return {}
            
            # Get most recent year data
            revenue = safe_financial_lookup(income_stmt, 'Total Revenue')
            net_income = safe_financial_lookup(income_stmt, 'Net Income')
            total_assets = safe_financial_lookup(balance_sheet, 'Total Assets')
            total_equity = safe_financial_lookup(balance_sheet, 'Total Stockholder Equity')
            
            # Calculate ratios
            gross_profit = safe_financial_lookup(income_stmt, 'Gross Profit')
            if np.isnan(gross_profit):
                gross_profit = revenue * 0.6 if not np.isnan(revenue) else np.nan
            operating_income = safe_financial_lookup(income_stmt, 'Operating Income')
            if np.isnan(operating_income):
                operating_income = net_income * 1.2 if not np.isnan(net_income) else np.nan
            
            ratios = {
                'gross_margin': gross_profit / revenue if not np.isnan(revenue) and revenue > 0 and not np.isnan(gross_profit) else np.nan,
                'operating_margin': operating_income / revenue if not np.isnan(revenue) and revenue > 0 and not np.isnan(operating_income) else np.nan,
                'net_margin': net_income / revenue if not np.isnan(revenue) and revenue > 0 and not np.isnan(net_income) else np.nan,
                'roa': net_income / total_assets if not np.isnan(total_assets) and total_assets > 0 and not np.isnan(net_income) else np.nan,
                'roe': net_income / total_equity if not np.isnan(total_equity) and total_equity > 0 and not np.isnan(net_income) else np.nan,
                'roic': net_income / (total_assets - safe_financial_lookup(balance_sheet, 'Total Current Liabilities')) if not np.isnan(total_assets) and total_assets > 0 and not np.isnan(net_income) else np.nan
            }
            
            return {k: round(v * 100, 2) if not np.isnan(v) else np.nan for k, v in ratios.items()}
            
        except Exception as e:
            print(f"Error calculating profitability ratios for {symbol}: {e}")
            return {}
    
    def calculate_liquidity_ratios(self, symbol: str) -> Dict:
        """
        Calculate liquidity ratios
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Liquidity ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            balance_sheet = ticker.balance_sheet
            
            if balance_sheet.empty:
                return {}
            
            # Get most recent year data
            current_assets = safe_financial_lookup(balance_sheet, 'Total Current Assets')
            current_liabilities = safe_financial_lookup(balance_sheet, 'Total Current Liabilities')
            cash = safe_financial_lookup(balance_sheet, 'Cash')
            if np.isnan(cash):
                cash = current_assets * 0.1 if not np.isnan(current_assets) else np.nan
            inventory = safe_financial_lookup(balance_sheet, 'Inventory')
            if np.isnan(inventory):
                inventory = 0
            
            ratios = {
                'current_ratio': current_assets / current_liabilities if not np.isnan(current_liabilities) and current_liabilities > 0 and not np.isnan(current_assets) else np.nan,
                'quick_ratio': (current_assets - inventory) / current_liabilities if not np.isnan(current_liabilities) and current_liabilities > 0 and not np.isnan(current_assets) and not np.isnan(inventory) else np.nan,
                'cash_ratio': cash / current_liabilities if not np.isnan(current_liabilities) and current_liabilities > 0 and not np.isnan(cash) else np.nan,
                'working_capital': current_assets - current_liabilities if not np.isnan(current_assets) and not np.isnan(current_liabilities) else np.nan
            }
            
            return {k: round(v, 2) if not np.isnan(v) else np.nan for k, v in ratios.items()}
            
        except Exception as e:
            print(f"Error calculating liquidity ratios for {symbol}: {e}")
            return {}
    
    def calculate_solvency_ratios(self, symbol: str) -> Dict:
        """
        Calculate solvency ratios
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Solvency ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            balance_sheet = ticker.balance_sheet
            income_stmt = ticker.income_stmt
            info = ticker.info
            
            if balance_sheet.empty or income_stmt.empty:
                return {}
            
            # Get most recent year data
            total_assets = safe_financial_lookup(balance_sheet, 'Total Assets')
            total_debt = info.get('totalDebt', 0)
            total_equity = safe_financial_lookup(balance_sheet, 'Total Stockholder Equity')
            ebit = safe_financial_lookup(income_stmt, 'EBIT')
            if np.isnan(ebit):
                net_income = safe_financial_lookup(income_stmt, 'Net Income')
                ebit = net_income * 1.3 if not np.isnan(net_income) else np.nan
            
            ratios = {
                'debt_to_equity': total_debt / total_equity if not np.isnan(total_equity) and total_equity > 0 else np.nan,
                'debt_to_assets': total_debt / total_assets if not np.isnan(total_assets) and total_assets > 0 else np.nan,
                'equity_ratio': total_equity / total_assets if not np.isnan(total_assets) and total_assets > 0 and not np.isnan(total_equity) else np.nan,
                'interest_coverage': ebit / info.get('interestExpense', 1) if info.get('interestExpense', 0) > 0 and not np.isnan(ebit) else np.nan
            }
            
            return {k: round(v, 2) if not np.isnan(v) else np.nan for k, v in ratios.items()}
            
        except Exception as e:
            print(f"Error calculating solvency ratios for {symbol}: {e}")
            return {}
    
    def calculate_efficiency_ratios(self, symbol: str) -> Dict:
        """
        Calculate efficiency ratios
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Efficiency ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            balance_sheet = ticker.balance_sheet
            income_stmt = ticker.income_stmt
            
            if balance_sheet.empty or income_stmt.empty:
                return {}
            
            # Get most recent year data
            revenue = safe_financial_lookup(income_stmt, 'Total Revenue')
            total_assets = safe_financial_lookup(balance_sheet, 'Total Assets')
            inventory = safe_financial_lookup(balance_sheet, 'Inventory')
            if np.isnan(inventory):
                inventory = 0
            accounts_receivable = safe_financial_lookup(balance_sheet, 'Net Receivables')
            if np.isnan(accounts_receivable):
                accounts_receivable = 0
            accounts_payable = safe_financial_lookup(balance_sheet, 'Accounts Payable')
            if np.isnan(accounts_payable):
                accounts_payable = 0
            
            # Calculate COGS if not available
            gross_profit = safe_financial_lookup(income_stmt, 'Gross Profit')
            if np.isnan(gross_profit):
                gross_profit = revenue * 0.6 if not np.isnan(revenue) else np.nan
            cogs = revenue - gross_profit
            
            ratios = {
                'asset_turnover': revenue / total_assets if not np.isnan(total_assets) and total_assets > 0 and not np.isnan(revenue) else np.nan,
                'inventory_turnover': cogs / inventory if not np.isnan(inventory) and inventory > 0 and not np.isnan(cogs) else np.nan,
                'receivables_turnover': revenue / accounts_receivable if not np.isnan(accounts_receivable) and accounts_receivable > 0 and not np.isnan(revenue) else np.nan,
                'payables_turnover': cogs / accounts_payable if not np.isnan(accounts_payable) and accounts_payable > 0 and not np.isnan(cogs) else np.nan
            }
            
            return {k: round(v, 2) if not np.isnan(v) else np.nan for k, v in ratios.items()}
            
        except Exception as e:
            print(f"Error calculating efficiency ratios for {symbol}: {e}")
            return {}
    
    def calculate_valuation_ratios(self, symbol: str) -> Dict:
        """
        Calculate valuation ratios
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Valuation ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            income_stmt = ticker.income_stmt
            balance_sheet = ticker.balance_sheet
            
            if income_stmt.empty or balance_sheet.empty:
                return {}
            
            # Get key metrics
            current_price = info.get('currentPrice', 0)
            market_cap = info.get('marketCap', 0)
            shares_outstanding = info.get('sharesOutstanding', 0)
            net_income = safe_financial_lookup(income_stmt, 'Net Income')
            total_equity = safe_financial_lookup(balance_sheet, 'Total Stockholder Equity')
            total_assets = safe_financial_lookup(balance_sheet, 'Total Assets')
            
            # Calculate ratios
            ratios = {
                'pe_ratio': current_price / (net_income / shares_outstanding) if not np.isnan(net_income) and net_income > 0 and shares_outstanding > 0 else np.nan,
                'pb_ratio': current_price / (total_equity / shares_outstanding) if not np.isnan(total_equity) and total_equity > 0 and shares_outstanding > 0 else np.nan,
                'ps_ratio': current_price / (safe_financial_lookup(income_stmt, 'Total Revenue') / shares_outstanding) if shares_outstanding > 0 and not np.isnan(safe_financial_lookup(income_stmt, 'Total Revenue')) else np.nan,
                'ev_ebitda': (market_cap + info.get('totalDebt', 0) - info.get('totalCash', 0)) / info.get('ebitda', net_income * 1.5) if info.get('ebitda', 0) > 0 and not np.isnan(net_income) else np.nan,
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else np.nan,
                'payout_ratio': info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') else np.nan
            }
            
            return {k: round(v, 2) if not np.isnan(v) else np.nan for k, v in ratios.items()}
            
        except Exception as e:
            print(f"Error calculating valuation ratios for {symbol}: {e}")
            return {}
    
    def calculate_growth_metrics(self, symbol: str) -> Dict:
        """
        Calculate growth metrics
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Growth metrics
        """
        try:
            ticker = yf.Ticker(symbol)
            income_stmt = ticker.income_stmt
            balance_sheet = ticker.balance_sheet
            info = ticker.info
            
            if income_stmt.empty or balance_sheet.empty:
                return {}
            
            # Get historical data for growth calculation
            if len(income_stmt.columns) >= 2:
                current_revenue = safe_financial_lookup(income_stmt, 'Total Revenue', 0)
                previous_revenue = safe_financial_lookup(income_stmt, 'Total Revenue', 1)
                if not np.isnan(current_revenue) and not np.isnan(previous_revenue) and previous_revenue > 0:
                    revenue_growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
                else:
                    revenue_growth = np.nan
                
                current_net_income = safe_financial_lookup(income_stmt, 'Net Income', 0)
                previous_net_income = safe_financial_lookup(income_stmt, 'Net Income', 1)
                if not np.isnan(current_net_income) and not np.isnan(previous_net_income) and previous_net_income > 0:
                    earnings_growth = ((current_net_income - previous_net_income) / previous_net_income) * 100
                else:
                    earnings_growth = np.nan
            else:
                revenue_growth = info.get('revenueGrowth', 0) * 100
                earnings_growth = 0
            
            metrics = {
                'revenue_growth': revenue_growth,
                'earnings_growth': earnings_growth,
                'revenue_growth_5y': info.get('revenueGrowth', 0) * 100,
                'earnings_growth_5y': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0
            }
            
            return {k: round(v, 2) if not np.isnan(v) else np.nan for k, v in metrics.items()}
            
        except Exception as e:
            print(f"Error calculating growth metrics for {symbol}: {e}")
            return {}
    
    def get_comprehensive_analysis(self, symbol: str) -> Dict:
        """
        Get comprehensive financial analysis
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Comprehensive financial analysis
        """
        try:
            analysis = {
                'profitability': self.calculate_profitability_ratios(symbol),
                'liquidity': self.calculate_liquidity_ratios(symbol),
                'solvency': self.calculate_solvency_ratios(symbol),
                'efficiency': self.calculate_efficiency_ratios(symbol),
                'valuation': self.calculate_valuation_ratios(symbol),
                'growth': self.calculate_growth_metrics(symbol)
            }
            
            # Add overall financial health score
            health_score = self.calculate_financial_health_score(analysis)
            analysis['financial_health_score'] = health_score
            
            return analysis
            
        except Exception as e:
            print(f"Error in comprehensive analysis for {symbol}: {e}")
            return {}
    
    def calculate_financial_health_score(self, analysis: Dict) -> float:
        """
        Calculate overall financial health score (0-100)
        
        Args:
            analysis (Dict): Financial analysis results
            
        Returns:
            float: Financial health score
        """
        try:
            score = 0
            max_score = 0
            
            # Profitability (25 points)
            if 'profitability' in analysis:
                prof = analysis['profitability']
                if prof.get('roe', 0) > 15: score += 10
                elif prof.get('roe', 0) > 10: score += 7
                elif prof.get('roe', 0) > 5: score += 4
                max_score += 10
                
                if prof.get('roa', 0) > 8: score += 8
                elif prof.get('roa', 0) > 5: score += 5
                elif prof.get('roa', 0) > 2: score += 3
                max_score += 8
                
                if prof.get('net_margin', 0) > 15: score += 7
                elif prof.get('net_margin', 0) > 10: score += 5
                elif prof.get('net_margin', 0) > 5: score += 3
                max_score += 7
            
            # Liquidity (20 points)
            if 'liquidity' in analysis:
                liq = analysis['liquidity']
                if liq.get('current_ratio', 0) > 2: score += 10
                elif liq.get('current_ratio', 0) > 1.5: score += 7
                elif liq.get('current_ratio', 0) > 1: score += 4
                max_score += 10
                
                if liq.get('quick_ratio', 0) > 1: score += 10
                elif liq.get('quick_ratio', 0) > 0.8: score += 7
                elif liq.get('quick_ratio', 0) > 0.5: score += 4
                max_score += 10
            
            # Solvency (20 points)
            if 'solvency' in analysis:
                sol = analysis['solvency']
                if sol.get('debt_to_equity', 0) < 0.5: score += 10
                elif sol.get('debt_to_equity', 0) < 1: score += 7
                elif sol.get('debt_to_equity', 0) < 1.5: score += 4
                max_score += 10
                
                if sol.get('interest_coverage', 0) > 5: score += 10
                elif sol.get('interest_coverage', 0) > 3: score += 7
                elif sol.get('interest_coverage', 0) > 1.5: score += 4
                max_score += 10
            
            # Growth (15 points)
            if 'growth' in analysis:
                growth = analysis['growth']
                if growth.get('revenue_growth', 0) > 10: score += 8
                elif growth.get('revenue_growth', 0) > 5: score += 5
                elif growth.get('revenue_growth', 0) > 0: score += 3
                max_score += 8
                
                if growth.get('earnings_growth', 0) > 10: score += 7
                elif growth.get('earnings_growth', 0) > 5: score += 5
                elif growth.get('earnings_growth', 0) > 0: score += 3
                max_score += 7
            
            # Efficiency (20 points)
            if 'efficiency' in analysis:
                eff = analysis['efficiency']
                if eff.get('asset_turnover', 0) > 1: score += 10
                elif eff.get('asset_turnover', 0) > 0.5: score += 7
                elif eff.get('asset_turnover', 0) > 0.2: score += 4
                max_score += 10
                
                if eff.get('inventory_turnover', 0) > 5: score += 10
                elif eff.get('inventory_turnover', 0) > 3: score += 7
                elif eff.get('inventory_turnover', 0) > 1: score += 4
                max_score += 10
            
            return round((score / max_score) * 100, 1) if max_score > 0 else 0
            
        except Exception as e:
            print(f"Error calculating financial health score: {e}")
            return 0
    
    def compare_with_peers(self, symbol: str, peer_symbols: List[str]) -> pd.DataFrame:
        """
        Compare financial metrics with peer companies
        
        Args:
            symbol (str): Target stock symbol
            peer_symbols (List[str]): List of peer symbols
            
        Returns:
            pd.DataFrame: Comparison table
        """
        try:
            all_symbols = [symbol] + peer_symbols
            comparison_data = []
            
            for sym in all_symbols:
                analysis = self.get_comprehensive_analysis(sym)
                if analysis:
                    row = {
                        'Symbol': sym,
                        'ROE (%)': analysis.get('profitability', {}).get('roe', 0),
                        'ROA (%)': analysis.get('profitability', {}).get('roa', 0),
                        'Net Margin (%)': analysis.get('profitability', {}).get('net_margin', 0),
                        'Current Ratio': analysis.get('liquidity', {}).get('current_ratio', 0),
                        'Debt/Equity': analysis.get('solvency', {}).get('debt_to_equity', 0),
                        'P/E Ratio': analysis.get('valuation', {}).get('pe_ratio', 0),
                        'P/B Ratio': analysis.get('valuation', {}).get('pb_ratio', 0),
                        'Revenue Growth (%)': analysis.get('growth', {}).get('revenue_growth', 0),
                        'Financial Health Score': analysis.get('financial_health_score', 0)
                    }
                    comparison_data.append(row)
            
            return pd.DataFrame(comparison_data)
            
        except Exception as e:
            print(f"Error in peer comparison for {symbol}: {e}")
            return pd.DataFrame()
