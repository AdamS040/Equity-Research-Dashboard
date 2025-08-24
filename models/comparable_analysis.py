"""
Comparable Company Analysis Module
Comprehensive peer comparison and benchmarking
"""
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class ComparableAnalysis:
    """
    Comprehensive comparable company analysis
    """
    
    def __init__(self):
        """Initialize comparable analysis"""
        pass
    
    def get_peer_companies(self, symbol: str, sector: Optional[str] = None) -> List[str]:
        """
        Get peer companies for comparison
        
        Args:
            symbol (str): Target stock symbol
            sector (str): Sector filter
            
        Returns:
            List[str]: List of peer symbols
        """
        try:
            # Default peer groups by sector
            sector_peers = {
                'Technology': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'ADBE', 'CRM', 'NFLX', 'TSLA'],
                'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'DHR', 'MRK', 'ABT', 'BMY', 'AMGN'],
                'Financials': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'V'],
                'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW', 'TJX', 'BKNG', 'MAR'],
                'Communication Services': ['GOOGL', 'META', 'NFLX', 'CMCSA', 'CHTR', 'TMUS', 'VZ', 'T', 'DISH', 'PARA'],
                'Industrials': ['BA', 'CAT', 'MMM', 'GE', 'HON', 'UPS', 'RTX', 'LMT', 'DE', 'EMR'],
                'Consumer Staples': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'PM', 'MO', 'CL', 'GIS', 'KMB'],
                'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'HAL'],
                'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'SRE', 'XEL', 'WEC', 'DTE', 'ED'],
                'Real Estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'O', 'SPG', 'DLR', 'WELL', 'AVB'],
                'Materials': ['LIN', 'APD', 'FCX', 'NEM', 'ECL', 'BLL', 'SHW', 'NUE', 'DD', 'DOW']
            }
            
            # Get company info
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Determine sector
            if sector:
                company_sector = sector
            else:
                company_sector = info.get('sector', 'Technology')
            
            # Get peers for the sector
            if company_sector in sector_peers:
                peers = sector_peers[company_sector]
                # Remove the target company if it's in the list
                if symbol in peers:
                    peers.remove(symbol)
                return peers[:8]  # Return top 8 peers
            else:
                # Default to technology peers
                return ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'ADBE', 'CRM']
                
        except Exception as e:
            print(f"Error getting peer companies for {symbol}: {e}")
            return ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'ADBE', 'CRM']
    
    def calculate_valuation_metrics(self, symbol: str) -> Dict:
        """
        Calculate comprehensive valuation metrics
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Valuation metrics
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return {}
            
            # Basic valuation metrics
            metrics = {
                'P/E Ratio': info.get('trailingPE', 0),
                'Forward P/E': info.get('forwardPE', 0),
                'P/B Ratio': info.get('priceToBook', 0),
                'P/S Ratio': info.get('priceToSalesTrailing12Months', 0),
                'EV/EBITDA': info.get('enterpriseToEbitda', 0),
                'EV/Revenue': info.get('enterpriseToRevenue', 0),
                'Price/Cash Flow': info.get('priceToCashflow', 0),
                'Dividend Yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'Payout Ratio': info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') else 0
            }
            
            # Growth metrics
            metrics.update({
                'Revenue Growth (5Y)': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0,
                'Earnings Growth (5Y)': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0,
                'EPS Growth (5Y)': info.get('earningsQuarterlyGrowth', 0) * 100 if info.get('earningsQuarterlyGrowth') else 0
            })
            
            # Profitability metrics
            metrics.update({
                'ROE': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
                'ROA': info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0,
                'ROIC': info.get('returnOnCapital', 0) * 100 if info.get('returnOnCapital') else 0,
                'Gross Margin': info.get('grossMargins', 0) * 100 if info.get('grossMargins') else 0,
                'Operating Margin': info.get('operatingMargins', 0) * 100 if info.get('operatingMargins') else 0,
                'Net Margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
            })
            
            # Financial strength metrics
            metrics.update({
                'Current Ratio': info.get('currentRatio', 0),
                'Debt/Equity': info.get('debtToEquity', 0),
                'Interest Coverage': info.get('interestCoverage', 0)
            })
            
            return {k: round(v, 2) for k, v in metrics.items()}
            
        except Exception as e:
            print(f"Error calculating valuation metrics for {symbol}: {e}")
            return {}
    
    def get_peer_comparison(self, symbol: str, peer_symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get comprehensive peer comparison
        
        Args:
            symbol (str): Target stock symbol
            peer_symbols (List[str]): List of peer symbols
            
        Returns:
            pd.DataFrame: Peer comparison table
        """
        try:
            if peer_symbols is None:
                peer_symbols = self.get_peer_companies(symbol)
            
            all_symbols = [symbol] + peer_symbols
            comparison_data = []
            
            for sym in all_symbols:
                metrics = self.calculate_valuation_metrics(sym)
                if metrics:
                    # Get additional info
                    ticker = yf.Ticker(sym)
                    info = ticker.info
                    
                    row = {
                        'Symbol': sym,
                        'Company Name': info.get('longName', sym),
                        'Sector': info.get('sector', 'N/A'),
                        'Market Cap (B)': round(info.get('marketCap', 0) / 1e9, 2),
                        'Current Price': info.get('currentPrice', 0),
                        'P/E Ratio': metrics.get('P/E Ratio', 0),
                        'Forward P/E': metrics.get('Forward P/E', 0),
                        'P/B Ratio': metrics.get('P/B Ratio', 0),
                        'P/S Ratio': metrics.get('P/S Ratio', 0),
                        'EV/EBITDA': metrics.get('EV/EBITDA', 0),
                        'ROE (%)': metrics.get('ROE', 0),
                        'ROA (%)': metrics.get('ROA', 0),
                        'Debt/Equity': metrics.get('Debt/Equity', 0),
                        'Revenue Growth (%)': metrics.get('Revenue Growth (5Y)', 0),
                        'Dividend Yield (%)': metrics.get('Dividend Yield', 0)
                    }
                    comparison_data.append(row)
            
            if comparison_data:
                df = pd.DataFrame(comparison_data)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error in peer comparison for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_relative_valuation(self, symbol: str, peer_symbols: Optional[List[str]] = None) -> Dict:
        """
        Calculate relative valuation metrics
        
        Args:
            symbol (str): Target stock symbol
            peer_symbols (List[str]): List of peer symbols
            
        Returns:
            Dict: Relative valuation analysis
        """
        try:
            if peer_symbols is None:
                peer_symbols = self.get_peer_companies(symbol)
            
            # Get comparison data
            comparison_df = self.get_peer_comparison(symbol, peer_symbols)
            
            if comparison_df.empty:
                return {}
            
            # Calculate relative metrics
            target_metrics = comparison_df[comparison_df['Symbol'] == symbol].iloc[0]
            peer_metrics = comparison_df[comparison_df['Symbol'] != symbol]
            
            relative_analysis = {}
            
            # Valuation ratios comparison
            valuation_ratios = ['P/E Ratio', 'Forward P/E', 'P/B Ratio', 'P/S Ratio', 'EV/EBITDA']
            
            for ratio in valuation_ratios:
                if ratio in target_metrics and ratio in peer_metrics.columns:
                    target_value = target_metrics[ratio]
                    peer_mean = peer_metrics[ratio].mean()
                    peer_median = peer_metrics[ratio].median()
                    
                    if peer_mean > 0:
                        relative_analysis[f'{ratio}_vs_Peer_Mean'] = {
                            'Target': target_value,
                            'Peer_Mean': peer_mean,
                            'Peer_Median': peer_median,
                            'Relative_Value': target_value / peer_mean,
                            'Percentile': (peer_metrics[ratio] <= target_value).mean() * 100
                        }
            
            # Growth comparison
            growth_metrics = ['Revenue Growth (%)', 'ROE (%)', 'ROA (%)']
            
            for metric in growth_metrics:
                if metric in target_metrics and metric in peer_metrics.columns:
                    target_value = target_metrics[metric]
                    peer_mean = peer_metrics[metric].mean()
                    peer_median = peer_metrics[metric].median()
                    
                    if peer_mean != 0:
                        relative_analysis[f'{metric}_vs_Peer_Mean'] = {
                            'Target': target_value,
                            'Peer_Mean': peer_mean,
                            'Peer_Median': peer_median,
                            'Relative_Growth': target_value / peer_mean,
                            'Percentile': (peer_metrics[metric] <= target_value).mean() * 100
                        }
            
            return relative_analysis
            
        except Exception as e:
            print(f"Error calculating relative valuation for {symbol}: {e}")
            return {}
    
    def calculate_implied_value(self, symbol: str, peer_symbols: Optional[List[str]] = None) -> Dict:
        """
        Calculate implied value based on peer multiples
        
        Args:
            symbol (str): Target stock symbol
            peer_symbols (List[str]): List of peer symbols
            
        Returns:
            Dict: Implied value analysis
        """
        try:
            if peer_symbols is None:
                peer_symbols = self.get_peer_companies(symbol)
            
            # Get comparison data
            comparison_df = self.get_peer_comparison(symbol, peer_symbols)
            
            if comparison_df.empty:
                return {}
            
            target_row = comparison_df[comparison_df['Symbol'] == symbol]
            peer_data = comparison_df[comparison_df['Symbol'] != symbol]
            
            if target_row.empty:
                return {}
            
            target = target_row.iloc[0]
            current_price = target['Current Price']
            
            implied_values = {}
            
            # Get financial data for target
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Calculate implied values using different multiples
            multiples = {
                'P/E Ratio': {
                    'target_metric': target['P/E Ratio'],
                    'peer_multiple': peer_data['P/E Ratio'].median(),
                    'financial_metric': info.get('trailingEps', 0)
                },
                'P/B Ratio': {
                    'target_metric': target['P/B Ratio'],
                    'peer_multiple': peer_data['P/B Ratio'].median(),
                    'financial_metric': info.get('bookValue', 0)
                },
                'P/S Ratio': {
                    'target_metric': target['P/S Ratio'],
                    'peer_multiple': peer_data['P/S Ratio'].median(),
                    'financial_metric': info.get('totalRevenue', 0) / info.get('sharesOutstanding', 1)
                },
                'EV/EBITDA': {
                    'target_metric': target['EV/EBITDA'],
                    'peer_multiple': peer_data['EV/EBITDA'].median(),
                    'financial_metric': info.get('ebitda', 0)
                }
            }
            
            for multiple_name, data in multiples.items():
                if data['peer_multiple'] > 0 and data['financial_metric'] > 0:
                    implied_value = data['peer_multiple'] * data['financial_metric']
                    upside = ((implied_value - current_price) / current_price) * 100
                    
                    implied_values[multiple_name] = {
                        'Current_Price': current_price,
                        'Implied_Value': implied_value,
                        'Upside_Percent': upside,
                        'Peer_Multiple': data['peer_multiple'],
                        'Target_Multiple': data['target_metric']
                    }
            
            # Calculate average implied value
            if implied_values:
                implied_prices = [v['Implied_Value'] for v in implied_values.values()]
                avg_implied_value = np.mean(implied_prices)
                avg_upside = ((avg_implied_value - current_price) / current_price) * 100
                
                implied_values['Average'] = {
                    'Current_Price': current_price,
                    'Implied_Value': avg_implied_value,
                    'Upside_Percent': avg_upside,
                    'Peer_Multiple': 'N/A',
                    'Target_Multiple': 'N/A'
                }
            
            return implied_values
            
        except Exception as e:
            print(f"Error calculating implied value for {symbol}: {e}")
            return {}
    
    def get_sector_analysis(self, symbol: str) -> Dict:
        """
        Get sector-level analysis
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Sector analysis
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return {}
            
            sector = info.get('sector', 'Technology')
            industry = info.get('industry', 'N/A')
            
            # Get sector peers
            sector_peers = self.get_peer_companies(symbol, sector)
            
            # Get sector performance
            sector_etfs = {
                'Technology': 'XLK',
                'Healthcare': 'XLV',
                'Financials': 'XLF',
                'Consumer Discretionary': 'XLY',
                'Communication Services': 'XLC',
                'Industrials': 'XLI',
                'Consumer Staples': 'XLP',
                'Energy': 'XLE',
                'Utilities': 'XLU',
                'Real Estate': 'XLRE',
                'Materials': 'XLB'
            }
            
            sector_analysis = {
                'Sector': sector,
                'Industry': industry,
                'Sector_Peers': sector_peers,
                'Sector_ETF': sector_etfs.get(sector, 'N/A')
            }
            
            # Get sector ETF performance if available
            if sector in sector_etfs:
                etf_symbol = sector_etfs[sector]
                etf_data = yf.Ticker(etf_symbol).history(period='1y')
                
                if not etf_data.empty:
                    etf_returns = etf_data['Close'].pct_change().dropna()
                    sector_analysis['Sector_Performance'] = {
                        'Annual_Return': etf_returns.mean() * 252,
                        'Annual_Volatility': etf_returns.std() * np.sqrt(252),
                        'Sharpe_Ratio': (etf_returns.mean() * 252) / (etf_returns.std() * np.sqrt(252)) if etf_returns.std() > 0 else 0
                    }
            
            return sector_analysis
            
        except Exception as e:
            print(f"Error in sector analysis for {symbol}: {e}")
            return {}
    
    def generate_comparable_report(self, symbol: str, peer_symbols: Optional[List[str]] = None) -> Dict:
        """
        Generate comprehensive comparable analysis report
        
        Args:
            symbol (str): Target stock symbol
            peer_symbols (List[str]): List of peer symbols
            
        Returns:
            Dict: Comprehensive comparable analysis report
        """
        try:
            if peer_symbols is None:
                peer_symbols = self.get_peer_companies(symbol)
            
            report = {
                'target_symbol': symbol,
                'peer_symbols': peer_symbols,
                'comparison_table': self.get_peer_comparison(symbol, peer_symbols),
                'relative_valuation': self.calculate_relative_valuation(symbol, peer_symbols),
                'implied_value': self.calculate_implied_value(symbol, peer_symbols),
                'sector_analysis': self.get_sector_analysis(symbol)
            }
            
            # Add summary metrics
            if not report['comparison_table'].empty:
                target_row = report['comparison_table'][report['comparison_table']['Symbol'] == symbol]
                if not target_row.empty:
                    target = target_row.iloc[0]
                    
                    report['summary'] = {
                        'current_price': target['Current Price'],
                        'market_cap': target['Market Cap (B)'],
                        'pe_ratio': target['P/E Ratio'],
                        'pb_ratio': target['P/B Ratio'],
                        'roe': target['ROE (%)'],
                        'revenue_growth': target['Revenue Growth (%)']
                    }
            
            return report
            
        except Exception as e:
            print(f"Error generating comparable report for {symbol}: {e}")
            return {}
