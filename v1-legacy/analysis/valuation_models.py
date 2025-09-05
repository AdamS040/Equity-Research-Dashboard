"""
Valuation Models Module
DCF, DDM, and other valuation methodologies
"""
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class DCFModel:
    """
    Discounted Cash Flow Valuation Model
    """
    
    def __init__(self, forecast_years: int = 5, terminal_growth_rate: float = 0.025):
        """
        Initialize DCF model
        
        Args:
            forecast_years (int): Number of forecast years
            terminal_growth_rate (float): Terminal growth rate
        """
        self.forecast_years = forecast_years
        self.terminal_growth_rate = terminal_growth_rate
    
    def calculate_wacc(self, symbol: str, risk_free_rate: float = 0.025, 
                      market_premium: float = 0.06) -> float:
        """
        Calculate Weighted Average Cost of Capital (WACC)
        
        Args:
            symbol (str): Stock symbol
            risk_free_rate (float): Risk-free rate
            market_premium (float): Market risk premium
            
        Returns:
            float: WACC
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            balance_sheet = ticker.balance_sheet
            
            # Get beta
            beta = info.get('beta', 1.0)
            
            # Cost of equity (CAPM)
            cost_of_equity = risk_free_rate + beta * market_premium
            
            # Get debt and equity values
            market_cap = info.get('marketCap', 0)
            total_debt = info.get('totalDebt', 0)
            
            if total_debt == 0 or market_cap == 0:
                return cost_of_equity  # No debt, use cost of equity
            
            # Cost of debt (simplified)
            interest_expense = 0
            if not balance_sheet.empty:
                try:
                    # Try to get interest expense from financials
                    financials = ticker.financials
                    if not financials.empty and 'Interest Expense' in financials.index:
                        interest_expense = abs(financials.loc['Interest Expense'].iloc[0])
                except:
                    pass
            
            cost_of_debt = interest_expense / total_debt if total_debt > 0 else 0.05
            
            # Tax rate (simplified)
            tax_rate = info.get('taxRate', 0.25)
            
            # Calculate weights
            total_value = market_cap + total_debt
            weight_equity = market_cap / total_value
            weight_debt = total_debt / total_value
            
            # WACC calculation
            wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt * (1 - tax_rate))
            
            return max(wacc, 0.05)  # Minimum 5% WACC
            
        except Exception as e:
            print(f"Error calculating WACC for {symbol}: {e}")
            return 0.10  # Default 10%
    
    def project_cash_flows(self, symbol: str, growth_rates: Optional[List[float]] = None) -> pd.DataFrame:
        """
        Project future free cash flows
        
        Args:
            symbol (str): Stock symbol
            growth_rates (List[float], optional): Custom growth rates
            
        Returns:
            pd.DataFrame: Projected cash flows
        """
        try:
            ticker = yf.Ticker(symbol)
            cashflow = ticker.cashflow
            info = ticker.info
            
            if cashflow.empty:
                return pd.DataFrame()
            
            # Get historical free cash flow
            try:
                fcf_history = cashflow.loc['Free Cash Flow']
                base_fcf = fcf_history.iloc[0]  # Most recent year
            except:
                # Calculate FCF if not available
                operating_cf = cashflow.loc['Total Cash From Operating Activities'].iloc[0]
                capex = cashflow.loc['Capital Expenditures'].iloc[0] if 'Capital Expenditures' in cashflow.index else 0
                base_fcf = operating_cf + capex  # capex is usually negative
            
            # Default growth rates if not provided
            if growth_rates is None:
                revenue_growth = info.get('revenueGrowth', 0.05)
                # Declining growth rates
                growth_rates = [
                    revenue_growth,
                    revenue_growth * 0.8,
                    revenue_growth * 0.6,
                    revenue_growth * 0.4,
                    revenue_growth * 0.2
                ][:self.forecast_years]
            
            # Project cash flows
            projections = []
            current_fcf = base_fcf
            
            for year in range(1, self.forecast_years + 1):
                if year <= len(growth_rates):
                    growth = growth_rates[year - 1]
                else:
                    growth = self.terminal_growth_rate
                
                current_fcf = current_fcf * (1 + growth)
                projections.append({
                    'year': year,
                    'growth_rate': growth,
                    'free_cash_flow': current_fcf
                })
            
            # Terminal value
            terminal_fcf = current_fcf * (1 + self.terminal_growth_rate)
            projections.append({
                'year': 'Terminal',
                'growth_rate': self.terminal_growth_rate,
                'free_cash_flow': terminal_fcf
            })
            
            return pd.DataFrame(projections)
            
        except Exception as e:
            print(f"Error projecting cash flows for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_dcf_value(self, symbol: str, growth_rates: Optional[List[float]] = None,
                           discount_rate: Optional[float] = None) -> Dict:
        """
        Calculate DCF valuation
        
        Args:
            symbol (str): Stock symbol
            growth_rates (List[float], optional): Custom growth rates
            discount_rate (float, optional): Custom discount rate
            
        Returns:
            Dict: DCF valuation results
        """
        try:
            # Get discount rate (WACC)
            if discount_rate is None:
                discount_rate = self.calculate_wacc(symbol)
            
            # Project cash flows
            projections = self.project_cash_flows(symbol, growth_rates)
            
            if projections.empty:
                return {'error': 'Unable to project cash flows'}
            
            # Calculate present values
            pv_fcf = 0
            pv_terminal = 0
            
            for idx, row in projections.iterrows():
                year = row['year']
                fcf = row['free_cash_flow']
                
                if year == 'Terminal':
                    # Terminal value calculation
                    terminal_value = fcf / (discount_rate - self.terminal_growth_rate)
                    pv_terminal = terminal_value / ((1 + discount_rate) ** self.forecast_years)
                else:
                    # Present value of explicit forecast
                    pv = fcf / ((1 + discount_rate) ** year)
                    pv_fcf += pv
            
            # Enterprise value
            enterprise_value = pv_fcf + pv_terminal
            
            # Get financial info
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Calculate equity value
            cash = info.get('totalCash', 0)
            debt = info.get('totalDebt', 0)
            equity_value = enterprise_value + cash - debt
            
            # Per share value
            shares_outstanding = info.get('sharesOutstanding', 0)
            value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
            
            # Current price comparison
            current_price = info.get('currentPrice', 0)
            upside_downside = (value_per_share - current_price) / current_price if current_price > 0 else 0
            
            return {
                'enterprise_value': enterprise_value,
                'equity_value': equity_value,
                'value_per_share': value_per_share,
                'current_price': current_price,
                'upside_downside': upside_downside,
                'pv_fcf': pv_fcf,
                'pv_terminal': pv_terminal,
                'discount_rate': discount_rate,
                'terminal_growth_rate': self.terminal_growth_rate,
                'projections': projections.to_dict('records')
            }
            
        except Exception as e:
            print(f"Error calculating DCF for {symbol}: {e}")
            return {'error': str(e)}
    
    def sensitivity_analysis(self, symbol: str, discount_rate_range: Tuple[float, float] = (0.08, 0.15),
                           growth_rate_range: Tuple[float, float] = (0.015, 0.035)) -> pd.DataFrame:
        """
        Perform sensitivity analysis on DCF valuation
        
        Args:
            symbol (str): Stock symbol
            discount_rate_range (Tuple[float, float]): Range of discount rates
            growth_rate_range (Tuple[float, float]): Range of terminal growth rates
            
        Returns:
            pd.DataFrame: Sensitivity analysis results
        """
        try:
            # Create ranges
            discount_rates = np.linspace(discount_rate_range[0], discount_rate_range[1], 5)
            growth_rates = np.linspace(growth_rate_range[0], growth_rate_range[1], 5)
            
            results = []
            
            for dr in discount_rates:
                for gr in growth_rates:
                    # Temporarily set terminal growth rate
                    original_tgr = self.terminal_growth_rate
                    self.terminal_growth_rate = gr
                    
                    # Calculate DCF value
                    dcf_result = self.calculate_dcf_value(symbol, discount_rate=dr)
                    
                    if 'value_per_share' in dcf_result:
                        results.append({
                            'discount_rate': dr,
                            'terminal_growth_rate': gr,
                            'value_per_share': dcf_result['value_per_share']
                        })
                    
                    # Restore original terminal growth rate
                    self.terminal_growth_rate = original_tgr
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"Error in sensitivity analysis for {symbol}: {e}")
            return pd.DataFrame()

class DividendDiscountModel:
    """
    Dividend Discount Model (DDM)
    """
    
    def __init__(self):
        """Initialize DDM"""
        pass
    
    def gordon_growth_model(self, symbol: str, required_return: Optional[float] = None) -> Dict:
        """
        Gordon Growth Model (constant growth DDM)
        
        Args:
            symbol (str): Stock symbol
            required_return (float, optional): Required return rate
            
        Returns:
            Dict: DDM valuation results
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get dividend information
            dividend_yield = info.get('dividendYield', 0)
            current_price = info.get('currentPrice', 0)
            
            if dividend_yield == 0 or current_price == 0:
                return {'error': 'No dividend data available'}
            
            # Calculate current dividend
            current_dividend = current_price * dividend_yield
            
            # Estimate dividend growth rate (simplified)
            dividend_growth = info.get('dividendGrowthRate', 0.05)
            
            # Required return (use CAPM if not provided)
            if required_return is None:
                beta = info.get('beta', 1.0)
                risk_free_rate = 0.025
                market_premium = 0.06
                required_return = risk_free_rate + beta * market_premium
            
            # Gordon Growth Model calculation
            if required_return <= dividend_growth:
                return {'error': 'Required return must be greater than dividend growth rate'}
            
            intrinsic_value = current_dividend * (1 + dividend_growth) / (required_return - dividend_growth)
            
            # Compare to current price
            upside_downside = (intrinsic_value - current_price) / current_price if current_price > 0 else 0
            
            return {
                'intrinsic_value': intrinsic_value,
                'current_price': current_price,
                'current_dividend': current_dividend,
                'dividend_growth_rate': dividend_growth,
                'required_return': required_return,
                'upside_downside': upside_downside
            }
            
        except Exception as e:
            print(f"Error in Gordon Growth Model for {symbol}: {e}")
            return {'error': str(e)}

class ComparableValuation:
    """
    Comparable Company Analysis (Comps)
    """
    
    def __init__(self):
        """Initialize comparable valuation"""
        pass
    
    def get_peer_multiples(self, symbols: List[str]) -> pd.DataFrame:
        """
        Get valuation multiples for peer companies
        
        Args:
            symbols (List[str]): List of peer company symbols
            
        Returns:
            pd.DataFrame: Peer multiples data
        """
        try:
            peer_data = []
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                peer_data.append({
                    'Symbol': symbol,
                    'Company': info.get('longName', symbol),
                    'Market Cap': info.get('marketCap', 0),
                    'P/E Ratio': info.get('trailingPE', 0),
                    'P/B Ratio': info.get('priceToBook', 0),
                    'P/S Ratio': info.get('priceToSalesTrailing12Months', 0),
                    'EV/EBITDA': info.get('enterpriseToEbitda', 0),
                    'EV/Revenue': info.get('enterpriseToRevenue', 0),
                    'ROE': info.get('returnOnEquity', 0),
                    'ROA': info.get('returnOnAssets', 0),
                    'Debt/Equity': info.get('debtToEquity', 0),
                    'Current Price': info.get('currentPrice', 0)
                })
            
            df = pd.DataFrame(peer_data)
            
            # Calculate statistics
            numeric_cols = ['P/E Ratio', 'P/B Ratio', 'P/S Ratio', 'EV/EBITDA', 'EV/Revenue']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            print(f"Error getting peer multiples: {e}")
            return pd.DataFrame()
    
    def calculate_implied_value(self, target_symbol: str, peer_symbols: List[str]) -> Dict:
        """
        Calculate implied value based on peer multiples
        
        Args:
            target_symbol (str): Target company symbol
            peer_symbols (List[str]): Peer company symbols
            
        Returns:
            Dict: Implied valuation results
        """
        try:
            # Get peer multiples
            peer_df = self.get_peer_multiples(peer_symbols + [target_symbol])
            
            if peer_df.empty:
                return {'error': 'Unable to get peer data'}
            
            # Separate target from peers
            target_data = peer_df[peer_df['Symbol'] == target_symbol].iloc[0]
            peer_data = peer_df[peer_df['Symbol'] != target_symbol]
            
            # Calculate peer medians
            multiples = ['P/E Ratio', 'P/B Ratio', 'P/S Ratio', 'EV/EBITDA', 'EV/Revenue']
            peer_medians = peer_data[multiples].median()
            
            # Get target fundamentals
            target_ticker = yf.Ticker(target_symbol)
            target_info = target_ticker.info
            
            # Calculate implied values
            implied_values = {}
            
            # P/E based valuation
            eps = target_info.get('trailingEps', 0)
            if eps > 0 and not pd.isna(peer_medians['P/E Ratio']):
                implied_values['PE_implied'] = eps * peer_medians['P/E Ratio']
            
            # P/B based valuation
            book_value = target_info.get('bookValue', 0)
            if book_value > 0 and not pd.isna(peer_medians['P/B Ratio']):
                implied_values['PB_implied'] = book_value * peer_medians['P/B Ratio']
            
            # P/S based valuation
            revenue_per_share = target_info.get('revenuePerShare', 0)
            if revenue_per_share > 0 and not pd.isna(peer_medians['P/S Ratio']):
                implied_values['PS_implied'] = revenue_per_share * peer_medians['P/S Ratio']
            
            # Average implied value
            values = [v for v in implied_values.values() if v > 0]
            avg_implied_value = np.mean(values) if values else 0
            
            current_price = target_data['Current Price']
            upside_downside = (avg_implied_value - current_price) / current_price if current_price > 0 else 0
            
            return {
                'target_symbol': target_symbol,
                'current_price': current_price,
                'implied_values': implied_values,
                'average_implied_value': avg_implied_value,
                'upside_downside': upside_downside,
                'peer_medians': peer_medians.to_dict(),
                'target_multiples': {
                    'P/E Ratio': target_data['P/E Ratio'],
                    'P/B Ratio': target_data['P/B Ratio'],
                    'P/S Ratio': target_data['P/S Ratio'],
                    'EV/EBITDA': target_data['EV/EBITDA'],
                    'EV/Revenue': target_data['EV/Revenue']
                }
            }
            
        except Exception as e:
            print(f"Error calculating implied value for {target_symbol}: {e}")
            return {'error': str(e)}

class AssetBasedValuation:
    """
    Asset-based valuation methods
    """
    
    def __init__(self):
        """Initialize asset-based valuation"""
        pass
    
    def book_value_analysis(self, symbol: str) -> Dict:
        """
        Book value analysis
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Book value analysis results
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            balance_sheet = ticker.balance_sheet
            
            # Basic book value metrics
            book_value = info.get('bookValue', 0)
            current_price = info.get('currentPrice', 0)
            pb_ratio = info.get('priceToBook', 0)
            
            # Tangible book value (if available)
            market_cap = info.get('marketCap', 0)
            total_equity = info.get('totalStockholderEquity', 0)
            
            # Calculate adjusted metrics
            if not balance_sheet.empty:
                try:
                    # Get goodwill and intangibles
                    goodwill = balance_sheet.loc['Goodwill'].iloc[0] if 'Goodwill' in balance_sheet.index else 0
                    intangibles = balance_sheet.loc['Intangible Assets'].iloc[0] if 'Intangible Assets' in balance_sheet.index else 0
                    
                    tangible_book_value = book_value - (goodwill + intangibles) / info.get('sharesOutstanding', 1)
                except:
                    tangible_book_value = book_value
            else:
                tangible_book_value = book_value
            
            return {
                'book_value': book_value,
                'tangible_book_value': tangible_book_value,
                'current_price': current_price,
                'pb_ratio': pb_ratio,
                'price_to_tangible_book': current_price / tangible_book_value if tangible_book_value > 0 else 0,
                'book_value_discount': (current_price - book_value) / book_value if book_value > 0 else 0
            }
            
        except Exception as e:
            print(f"Error in book value analysis for {symbol}: {e}")
            return {'error': str(e)}

class ValuationSummary:
    """
    Comprehensive valuation summary combining multiple methods
    """
    
    def __init__(self):
        """Initialize valuation summary"""
        self.dcf_model = DCFModel()
        self.ddm_model = DividendDiscountModel()
        self.comp_valuation = ComparableValuation()
        self.asset_valuation = AssetBasedValuation()
    
    def comprehensive_valuation(self, symbol: str, peer_symbols: Optional[List[str]] = None) -> Dict:
        """
        Perform comprehensive valuation using multiple methods
        
        Args:
            symbol (str): Stock symbol
            peer_symbols (List[str], optional): Peer company symbols
            
        Returns:
            Dict: Comprehensive valuation results
        """
        try:
            results = {'symbol': symbol}
            
            # DCF Valuation
            dcf_result = self.dcf_model.calculate_dcf_value(symbol)
            if 'error' not in dcf_result:
                results['dcf_valuation'] = dcf_result
            
            # DDM Valuation (if applicable)
            ddm_result = self.ddm_model.gordon_growth_model(symbol)
            if 'error' not in ddm_result:
                results['ddm_valuation'] = ddm_result
            
            # Comparable Valuation
            if peer_symbols:
                comp_result = self.comp_valuation.calculate_implied_value(symbol, peer_symbols)
                if 'error' not in comp_result:
                    results['comparable_valuation'] = comp_result
            
            # Asset-based Valuation
            asset_result = self.asset_valuation.book_value_analysis(symbol)
            if 'error' not in asset_result:
                results['asset_valuation'] = asset_result
            
            # Calculate weighted average if multiple valuations available
            valuations = []
            weights = []
            
            if 'dcf_valuation' in results:
                valuations.append(results['dcf_valuation']['value_per_share'])
                weights.append(0.4)  # 40% weight to DCF
            
            if 'ddm_valuation' in results:
                valuations.append(results['ddm_valuation']['intrinsic_value'])
                weights.append(0.3)  # 30% weight to DDM
            
            if 'comparable_valuation' in results:
                valuations.append(results['comparable_valuation']['average_implied_value'])
                weights.append(0.3)  # 30% weight to comparables
            
            if valuations:
                # Normalize weights
                total_weight = sum(weights)
                normalized_weights = [w/total_weight for w in weights]
                
                weighted_average = sum(v*w for v, w in zip(valuations, normalized_weights))
                
                # Current price for comparison
                ticker = yf.Ticker(symbol)
                current_price = ticker.info.get('currentPrice', 0)
                
                results['summary'] = {
                    'weighted_average_value': weighted_average,
                    'current_price': current_price,
                    'upside_downside': (weighted_average - current_price) / current_price if current_price > 0 else 0,
                    'valuation_methods_used': len(valuations),
                    'individual_valuations': dict(zip(['DCF', 'DDM', 'Comparables'][:len(valuations)], valuations)),
                    'weights_used': dict(zip(['DCF', 'DDM', 'Comparables'][:len(weights)], normalized_weights))
                }
            
            return results
            
        except Exception as e:
            print(f"Error in comprehensive valuation for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}