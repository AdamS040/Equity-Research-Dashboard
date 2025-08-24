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
            revenue = income_stmt.loc['Total Revenue'].iloc[0]
            net_income = income_stmt.loc['Net Income'].iloc[0]
            total_assets = balance_sheet.loc['Total Assets'].iloc[0]
            total_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[0]
            
            # Calculate ratios
            gross_profit = income_stmt.loc['Gross Profit'].iloc[0] if 'Gross Profit' in income_stmt.index else revenue * 0.6
            operating_income = income_stmt.loc['Operating Income'].iloc[0] if 'Operating Income' in income_stmt.index else net_income * 1.2
            
            ratios = {
                'gross_margin': gross_profit / revenue if revenue > 0 else 0,
                'operating_margin': operating_income / revenue if revenue > 0 else 0,
                'net_margin': net_income / revenue if revenue > 0 else 0,
                'roa': net_income / total_assets if total_assets > 0 else 0,
                'roe': net_income / total_equity if total_equity > 0 else 0,
                'roic': net_income / (total_assets - balance_sheet.loc['Total Current Liabilities'].iloc[0]) if total_assets > 0 else 0
            }
            
            return {k: round(v * 100, 2) for k, v in ratios.items()}
            
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
            current_assets = balance_sheet.loc['Total Current Assets'].iloc[0]
            current_liabilities = balance_sheet.loc['Total Current Liabilities'].iloc[0]
            cash = balance_sheet.loc['Cash'].iloc[0] if 'Cash' in balance_sheet.index else current_assets * 0.1
            inventory = balance_sheet.loc['Inventory'].iloc[0] if 'Inventory' in balance_sheet.index else 0
            
            ratios = {
                'current_ratio': current_assets / current_liabilities if current_liabilities > 0 else 0,
                'quick_ratio': (current_assets - inventory) / current_liabilities if current_liabilities > 0 else 0,
                'cash_ratio': cash / current_liabilities if current_liabilities > 0 else 0,
                'working_capital': current_assets - current_liabilities
            }
            
            return {k: round(v, 2) for k, v in ratios.items()}
            
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
            total_assets = balance_sheet.loc['Total Assets'].iloc[0]
            total_debt = info.get('totalDebt', 0)
            total_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[0]
            ebit = income_stmt.loc['EBIT'].iloc[0] if 'EBIT' in income_stmt.index else income_stmt.loc['Net Income'].iloc[0] * 1.3
            
            ratios = {
                'debt_to_equity': total_debt / total_equity if total_equity > 0 else 0,
                'debt_to_assets': total_debt / total_assets if total_assets > 0 else 0,
                'equity_ratio': total_equity / total_assets if total_assets > 0 else 0,
                'interest_coverage': ebit / info.get('interestExpense', 1) if info.get('interestExpense', 0) > 0 else 999
            }
            
            return {k: round(v, 2) for k, v in ratios.items()}
            
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
            revenue = income_stmt.loc['Total Revenue'].iloc[0]
            total_assets = balance_sheet.loc['Total Assets'].iloc[0]
            inventory = balance_sheet.loc['Inventory'].iloc[0] if 'Inventory' in balance_sheet.index else 0
            accounts_receivable = balance_sheet.loc['Net Receivables'].iloc[0] if 'Net Receivables' in balance_sheet.index else 0
            accounts_payable = balance_sheet.loc['Accounts Payable'].iloc[0] if 'Accounts Payable' in balance_sheet.index else 0
            
            # Calculate COGS if not available
            gross_profit = income_stmt.loc['Gross Profit'].iloc[0] if 'Gross Profit' in income_stmt.index else revenue * 0.6
            cogs = revenue - gross_profit
            
            ratios = {
                'asset_turnover': revenue / total_assets if total_assets > 0 else 0,
                'inventory_turnover': cogs / inventory if inventory > 0 else 0,
                'receivables_turnover': revenue / accounts_receivable if accounts_receivable > 0 else 0,
                'payables_turnover': cogs / accounts_payable if accounts_payable > 0 else 0
            }
            
            return {k: round(v, 2) for k, v in ratios.items()}
            
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
            net_income = income_stmt.loc['Net Income'].iloc[0]
            total_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[0]
            total_assets = balance_sheet.loc['Total Assets'].iloc[0]
            
            # Calculate ratios
            ratios = {
                'pe_ratio': current_price / (net_income / shares_outstanding) if net_income > 0 and shares_outstanding > 0 else 0,
                'pb_ratio': current_price / (total_equity / shares_outstanding) if total_equity > 0 and shares_outstanding > 0 else 0,
                'ps_ratio': current_price / (income_stmt.loc['Total Revenue'].iloc[0] / shares_outstanding) if shares_outstanding > 0 else 0,
                'ev_ebitda': (market_cap + info.get('totalDebt', 0) - info.get('totalCash', 0)) / info.get('ebitda', net_income * 1.5) if info.get('ebitda', 0) > 0 else 0,
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'payout_ratio': info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') else 0
            }
            
            return {k: round(v, 2) for k, v in ratios.items()}
            
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
                current_revenue = income_stmt.loc['Total Revenue'].iloc[0]
                previous_revenue = income_stmt.loc['Total Revenue'].iloc[1]
                revenue_growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
                
                current_net_income = income_stmt.loc['Net Income'].iloc[0]
                previous_net_income = income_stmt.loc['Net Income'].iloc[1]
                earnings_growth = ((current_net_income - previous_net_income) / previous_net_income) * 100 if previous_net_income > 0 else 0
            else:
                revenue_growth = info.get('revenueGrowth', 0) * 100
                earnings_growth = 0
            
            metrics = {
                'revenue_growth': revenue_growth,
                'earnings_growth': earnings_growth,
                'revenue_growth_5y': info.get('revenueGrowth', 0) * 100,
                'earnings_growth_5y': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0
            }
            
            return {k: round(v, 2) for k, v in metrics.items()}
            
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
