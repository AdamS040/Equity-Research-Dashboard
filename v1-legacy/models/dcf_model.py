"""
Discounted Cash Flow (DCF) Valuation Model
Professional-grade DCF implementation with sensitivity analysis
"""
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class DCFModel:
    """
    Comprehensive DCF valuation model
    """
    
    def __init__(self):
        """Initialize DCF model"""
        self.default_assumptions = {
            'projection_years': 5,
            'terminal_growth_rate': 0.025,  # 2.5%
            'discount_rate': 0.10,          # 10% WACC
            'tax_rate': 0.21,               # 21% corporate tax rate
            'capex_percent_of_revenue': 0.03, # 3% of revenue
            'depreciation_percent_of_capex': 0.10, # 10% of CapEx
            'working_capital_percent_of_revenue': 0.02  # 2% of revenue
        }
    
    def get_financial_data(self, symbol: str) -> Dict:
        """
        Extract financial data for DCF analysis
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Financial data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get financial statements
            income_stmt = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow
            info = ticker.info
            
            # Extract key metrics
            data = {}
            
            # Revenue (Total Revenue or Net Income if revenue not available)
            if 'Total Revenue' in income_stmt.index:
                data['revenue'] = income_stmt.loc['Total Revenue'].iloc[0]
            elif 'Net Income' in income_stmt.index:
                # Fallback - estimate revenue from net income and margin
                net_income = income_stmt.loc['Net Income'].iloc[0]
                profit_margin = info.get('profitMargins', 0.10)
                data['revenue'] = net_income / profit_margin if profit_margin > 0 else net_income * 10
            else:
                data['revenue'] = info.get('totalRevenue', 1000000000)  # Default 1B
            
            # EBIT/Operating Income
            if 'Operating Income' in income_stmt.index:
                data['ebit'] = income_stmt.loc['Operating Income'].iloc[0]
            elif 'Ebit' in income_stmt.index:
                data['ebit'] = income_stmt.loc['Ebit'].iloc[0]
            else:
                # Estimate from revenue and operating margin
                operating_margin = info.get('operatingMargins', 0.15)
                data['ebit'] = data['revenue'] * operating_margin
            
            # Net Income
            if 'Net Income' in income_stmt.index:
                data['net_income'] = income_stmt.loc['Net Income'].iloc[0]
            else:
                data['net_income'] = data['ebit'] * (1 - self.default_assumptions['tax_rate'])
            
            # Free Cash Flow
            if 'Free Cash Flow' in cashflow.index:
                data['free_cash_flow'] = cashflow.loc['Free Cash Flow'].iloc[0]
            elif 'Operating Cash Flow' in cashflow.index and 'Capital Expenditures' in cashflow.index:
                data['free_cash_flow'] = (cashflow.loc['Operating Cash Flow'].iloc[0] + 
                                        cashflow.loc['Capital Expenditures'].iloc[0])
            else:
                # Estimate FCF
                data['free_cash_flow'] = data['net_income'] * 1.1  # Assume FCF is 110% of net income
            
            # CapEx
            if 'Capital Expenditures' in cashflow.index:
                data['capex'] = abs(cashflow.loc['Capital Expenditures'].iloc[0])
            else:
                data['capex'] = data['revenue'] * self.default_assumptions['capex_percent_of_revenue']
            
            # Depreciation
            if 'Depreciation' in cashflow.index:
                data['depreciation'] = cashflow.loc['Depreciation'].iloc[0]
            elif 'Depreciation And Amortization' in cashflow.index:
                data['depreciation'] = cashflow.loc['Depreciation And Amortization'].iloc[0]
            else:
                data['depreciation'] = data['capex'] * self.default_assumptions['depreciation_percent_of_capex']
            
            # Working Capital Change
            if 'Change In Working Capital' in cashflow.index:
                data['working_capital_change'] = cashflow.loc['Change In Working Capital'].iloc[0]
            else:
                data['working_capital_change'] = data['revenue'] * self.default_assumptions['working_capital_percent_of_revenue']
            
            # Market data
            data['shares_outstanding'] = info.get('sharesOutstanding', 1000000000)  # Default 1B shares
            data['current_price'] = info.get('currentPrice', 100)  # Default $100
            data['market_cap'] = info.get('marketCap', data['shares_outstanding'] * data['current_price'])
            data['enterprise_value'] = info.get('enterpriseValue', data['market_cap'])
            data['total_debt'] = info.get('totalDebt', 0)
            data['cash'] = info.get('totalCash', 0)
            
            # Growth rates
            data['revenue_growth'] = info.get('revenueGrowth', 0.05)  # Default 5%
            data['earnings_growth'] = info.get('earningsGrowth', 0.05)  # Default 5%
            
            return data
            
        except Exception as e:
            print(f"Error getting financial data for {symbol}: {e}")
            return self._get_default_data(symbol)
    
    def _get_default_data(self, symbol: str) -> Dict:
        """Get default financial data when actual data is unavailable"""
        return {
            'revenue': 1000000000,  # $1B
            'ebit': 150000000,      # $150M
            'net_income': 100000000, # $100M
            'free_cash_flow': 110000000, # $110M
            'capex': 30000000,      # $30M
            'depreciation': 20000000, # $20M
            'working_capital_change': 5000000, # $5M
            'shares_outstanding': 100000000,   # 100M shares
            'current_price': 50,    # $50
            'market_cap': 5000000000, # $5B
            'enterprise_value': 5000000000,
            'total_debt': 500000000, # $500M
            'cash': 200000000,      # $200M
            'revenue_growth': 0.05,
            'earnings_growth': 0.05
        }
    
    def project_financials(self, data: Dict, assumptions: Dict) -> pd.DataFrame:
        """
        Project future financials
        
        Args:
            data (Dict): Historical financial data
            assumptions (Dict): DCF assumptions
            
        Returns:
            pd.DataFrame: Projected financials
        """
        years = assumptions.get('projection_years', 5)
        
        # Create projection DataFrame
        projection = pd.DataFrame(index=range(1, years + 1))
        
        # Revenue projections with declining growth
        initial_growth = assumptions.get('revenue_growth_y1', data['revenue_growth'])
        terminal_growth = assumptions.get('terminal_growth_rate', 0.025)
        
        # Linear decline in growth rate
        growth_rates = np.linspace(initial_growth, terminal_growth, years)
        
        revenues = [data['revenue']]
        for i, growth_rate in enumerate(growth_rates):
            next_revenue = revenues[-1] * (1 + growth_rate)
            revenues.append(next_revenue)
        
        projection['Revenue'] = revenues[1:]  # Exclude base year
        projection['Revenue_Growth'] = growth_rates
        
        # EBIT projections (maintain EBIT margin)
        ebit_margin = data['ebit'] / data['revenue'] if data['revenue'] > 0 else 0.15
        projection['EBIT'] = projection['Revenue'] * ebit_margin
        
        # Tax calculations
        tax_rate = assumptions.get('tax_rate', 0.21)
        projection['Taxes'] = projection['EBIT'] * tax_rate
        projection['NOPAT'] = projection['EBIT'] - projection['Taxes']
        
        # CapEx projections
        capex_percent = assumptions.get('capex_percent_of_revenue', 0.03)
        projection['CapEx'] = projection['Revenue'] * capex_percent
        
        # Depreciation projections
        depreciation_percent = assumptions.get('depreciation_percent_of_capex', 0.10)
        projection['Depreciation'] = projection['CapEx'] * depreciation_percent
        
        # Working capital projections
        wc_percent = assumptions.get('working_capital_percent_of_revenue', 0.02)
        projection['Working_Capital'] = projection['Revenue'] * wc_percent
        projection['WC_Change'] = projection['Working_Capital'].diff().fillna(projection['Working_Capital'].iloc[0] - (data['revenue'] * wc_percent))
        
        # Free Cash Flow calculation
        projection['Free_Cash_Flow'] = (projection['NOPAT'] + 
                                      projection['Depreciation'] - 
                                      projection['CapEx'] - 
                                      projection['WC_Change'])
        
        return projection
    
    def calculate_terminal_value(self, final_fcf: float, assumptions: Dict) -> float:
        """
        Calculate terminal value using Gordon Growth Model
        
        Args:
            final_fcf (float): Final year free cash flow
            assumptions (Dict): DCF assumptions
            
        Returns:
            float: Terminal value
        """
        terminal_growth = assumptions.get('terminal_growth_rate', 0.025)
        discount_rate = assumptions.get('discount_rate', 0.10)
        
        if discount_rate <= terminal_growth:
            # Avoid division by zero or negative denominator
            terminal_growth = discount_rate - 0.01
        
        terminal_fcf = final_fcf * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        
        return terminal_value
    
    def calculate_present_value(self, cash_flows: pd.Series, terminal_value: float, 
                              discount_rate: float) -> Tuple[float, float]:
        """
        Calculate present value of cash flows and terminal value
        
        Args:
            cash_flows (pd.Series): Projected cash flows
            terminal_value (float): Terminal value
            discount_rate (float): Discount rate (WACC)
            
        Returns:
            Tuple[float, float]: (PV of cash flows, PV of terminal value)
        """
        # Present value of projected cash flows
        pv_cash_flows = 0
        for year, fcf in enumerate(cash_flows, 1):
            pv_cash_flows += fcf / ((1 + discount_rate) ** year)
        
        # Present value of terminal value
        final_year = len(cash_flows)
        pv_terminal_value = terminal_value / ((1 + discount_rate) ** final_year)
        
        return pv_cash_flows, pv_terminal_value
    
    def value_company(self, symbol: str, assumptions: Optional[Dict] = None) -> Dict:
        """
        Perform complete DCF valuation
        
        Args:
            symbol (str): Stock symbol
            assumptions (Dict, optional): Custom assumptions
            
        Returns:
            Dict: Valuation results
        """
        # Merge custom assumptions with defaults
        dcf_assumptions = self.default_assumptions.copy()
        if assumptions:
            dcf_assumptions.update(assumptions)
        
        # Get financial data
        data = self.get_financial_data(symbol)
        
        # Project financials
        projections = self.project_financials(data, dcf_assumptions)
        
        # Calculate terminal value
        final_fcf = projections['Free_Cash_Flow'].iloc[-1]
        terminal_value = self.calculate_terminal_value(final_fcf, dcf_assumptions)
        
        # Calculate present values
        discount_rate = dcf_assumptions['discount_rate']
        pv_cash_flows, pv_terminal_value = self.calculate_present_value(
            projections['Free_Cash_Flow'], terminal_value, discount_rate
        )
        
        # Enterprise value
        enterprise_value = pv_cash_flows + pv_terminal_value
        
        # Equity value
        net_debt = data['total_debt'] - data['cash']
        equity_value = enterprise_value - net_debt
        
        # Per share value
        shares_outstanding = data['shares_outstanding']
        value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
        
        # Current metrics
        current_price = data['current_price']
        upside_downside = (value_per_share - current_price) / current_price if current_price > 0 else 0
        
        return {
            'symbol': symbol,
            'enterprise_value': enterprise_value,
            'equity_value': equity_value,
            'value_per_share': value_per_share,
            'current_price': current_price,
            'upside_downside_percent': upside_downside,
            'pv_cash_flows': pv_cash_flows,
            'pv_terminal_value': pv_terminal_value,
            'terminal_value': terminal_value,
            'net_debt': net_debt,
            'shares_outstanding': shares_outstanding,
            'assumptions': dcf_assumptions,
            'projections': projections,
            'historical_data': data
        }
    
    def sensitivity_analysis(self, symbol: str, base_assumptions: Optional[Dict] = None) -> pd.DataFrame:
        """
        Perform sensitivity analysis on key assumptions
        
        Args:
            symbol (str): Stock symbol
            base_assumptions (Dict, optional): Base case assumptions
            
        Returns:
            pd.DataFrame: Sensitivity analysis results
        """
        # Base case assumptions
        assumptions = self.default_assumptions.copy()
        if base_assumptions:
            assumptions.update(base_assumptions)
        
        # Get base case valuation
        base_valuation = self.value_company(symbol, assumptions)
        base_value = base_valuation['value_per_share']
        
        # Define sensitivity ranges
        discount_rate_range = np.arange(0.08, 0.13, 0.005)  # 8% to 12%
        terminal_growth_range = np.arange(0.015, 0.035, 0.0025)  # 1.5% to 3.5%
        
        # Create sensitivity matrix
        sensitivity_matrix = np.zeros((len(discount_rate_range), len(terminal_growth_range)))
        
        for i, discount_rate in enumerate(discount_rate_range):
            for j, terminal_growth in enumerate(terminal_growth_range):
                # Update assumptions
                test_assumptions = assumptions.copy()
                test_assumptions['discount_rate'] = discount_rate
                test_assumptions['terminal_growth_rate'] = terminal_growth
                
                # Calculate valuation
                try:
                    valuation = self.value_company(symbol, test_assumptions)
                    sensitivity_matrix[i, j] = valuation['value_per_share']
                except:
                    sensitivity_matrix[i, j] = 0
        
        # Convert to DataFrame
        sensitivity_df = pd.DataFrame(
            sensitivity_matrix,
            index=[f"{dr:.1%}" for dr in discount_rate_range],
            columns=[f"{tg:.1%}" for tg in terminal_growth_range]
        )
        
        return sensitivity_df
    
    def monte_carlo_simulation(self, symbol: str, assumptions: Optional[Dict] = None, 
                             num_simulations: int = 10000) -> Dict:
        """
        Perform Monte Carlo simulation for valuation
        
        Args:
            symbol (str): Stock symbol
            assumptions (Dict, optional): Base assumptions
            num_simulations (int): Number of simulation runs
            
        Returns:
            Dict: Simulation results
        """
        # Base assumptions
        base_assumptions = self.default_assumptions.copy()
        if assumptions:
            base_assumptions.update(assumptions)
        
        # Define probability distributions for key variables
        # Revenue growth: normal distribution
        revenue_growth_mean = base_assumptions.get('revenue_growth_y1', 0.05)
        revenue_growth_std = 0.02  # 2% standard deviation
        
        # Discount rate: normal distribution
        discount_rate_mean = base_assumptions['discount_rate']
        discount_rate_std = 0.01  # 1% standard deviation
        
        # Terminal growth: normal distribution
        terminal_growth_mean = base_assumptions['terminal_growth_rate']
        terminal_growth_std = 0.005  # 0.5% standard deviation
        
        # EBIT margin: normal distribution
        data = self.get_financial_data(symbol)
        ebit_margin_mean = data['ebit'] / data['revenue'] if data['revenue'] > 0 else 0.15
        ebit_margin_std = 0.02  # 2% standard deviation
        
        simulation_results = []
        
        for _ in range(num_simulations):
            # Sample random variables
            revenue_growth = max(0, np.random.normal(revenue_growth_mean, revenue_growth_std))
            discount_rate = max(0.05, np.random.normal(discount_rate_mean, discount_rate_std))
            terminal_growth = max(0, min(discount_rate - 0.01, 
                                       np.random.normal(terminal_growth_mean, terminal_growth_std)))
            ebit_margin = max(0.01, np.random.normal(ebit_margin_mean, ebit_margin_std))
            
            # Create simulation assumptions
            sim_assumptions = base_assumptions.copy()
            sim_assumptions.update({
                'revenue_growth_y1': revenue_growth,
                'discount_rate': discount_rate,
                'terminal_growth_rate': terminal_growth,
                'ebit_margin': ebit_margin
            })
            
            try:
                # Run valuation
                valuation = self.value_company(symbol, sim_assumptions)
                simulation_results.append(valuation['value_per_share'])
            except:
                simulation_results.append(0)
        
        # Calculate statistics
        simulation_results = np.array(simulation_results)
        simulation_results = simulation_results[simulation_results > 0]  # Remove failed simulations
        
        if len(simulation_results) == 0:
            return {'error': 'All simulations failed'}
        
        return {
            'mean': np.mean(simulation_results),
            'median': np.median(simulation_results),
            'std': np.std(simulation_results),
            'min': np.min(simulation_results),
            'max': np.max(simulation_results),
            'percentile_5': np.percentile(simulation_results, 5),
            'percentile_25': np.percentile(simulation_results, 25),
            'percentile_75': np.percentile(simulation_results, 75),
            'percentile_95': np.percentile(simulation_results, 95),
            'current_price': data['current_price'],
            'probability_above_current': np.sum(simulation_results > data['current_price']) / len(simulation_results),
            'num_successful_simulations': len(simulation_results),
            'all_results': simulation_results
        }
    
    def scenario_analysis(self, symbol: str, assumptions: Optional[Dict] = None) -> Dict:
        """
        Perform scenario analysis (Bull, Base, Bear cases)
        
        Args:
            symbol (str): Stock symbol
            assumptions (Dict, optional): Base case assumptions
            
        Returns:
            Dict: Scenario analysis results
        """
        # Base case assumptions
        base_assumptions = self.default_assumptions.copy()
        if assumptions:
            base_assumptions.update(assumptions)
        
        # Define scenarios
        scenarios = {
            'Bear Case': {
                'revenue_growth_y1': base_assumptions.get('revenue_growth_y1', 0.05) * 0.5,  # 50% of base
                'discount_rate': base_assumptions['discount_rate'] + 0.02,  # +2%
                'terminal_growth_rate': base_assumptions['terminal_growth_rate'] * 0.5,  # 50% of base
                'capex_percent_of_revenue': base_assumptions['capex_percent_of_revenue'] * 1.5  # 150% of base
            },
            'Base Case': base_assumptions.copy(),
            'Bull Case': {
                'revenue_growth_y1': base_assumptions.get('revenue_growth_y1', 0.05) * 1.5,  # 150% of base
                'discount_rate': base_assumptions['discount_rate'] - 0.01,  # -1%
                'terminal_growth_rate': min(0.04, base_assumptions['terminal_growth_rate'] * 1.2),  # 120% of base, max 4%
                'capex_percent_of_revenue': base_assumptions['capex_percent_of_revenue'] * 0.8  # 80% of base
            }
        }
        
        results = {}
        for scenario_name, scenario_assumptions in scenarios.items():
            # Merge with base assumptions
            full_assumptions = base_assumptions.copy()
            full_assumptions.update(scenario_assumptions)
            
            # Run valuation
            valuation = self.value_company(symbol, full_assumptions)
            results[scenario_name] = {
                'value_per_share': valuation['value_per_share'],
                'enterprise_value': valuation['enterprise_value'],
                'upside_downside': valuation['upside_downside_percent'],
                'assumptions': full_assumptions
            }
        
        return results
    
    def generate_valuation_summary(self, symbol: str, assumptions: Optional[Dict] = None) -> Dict:
        """
        Generate comprehensive valuation summary
        
        Args:
            symbol (str): Stock symbol
            assumptions (Dict, optional): Custom assumptions
            
        Returns:
            Dict: Comprehensive valuation summary
        """
        # Base DCF valuation
        dcf_valuation = self.value_company(symbol, assumptions)
        
        # Scenario analysis
        scenarios = self.scenario_analysis(symbol, assumptions)
        
        # Sensitivity analysis
        sensitivity = self.sensitivity_analysis(symbol, assumptions)
        
        # Monte Carlo simulation (reduced for performance)
        monte_carlo = self.monte_carlo_simulation(symbol, assumptions, 1000)
        
        return {
            'symbol': symbol,
            'dcf_valuation': dcf_valuation,
            'scenario_analysis': scenarios,
            'sensitivity_analysis': sensitivity,
            'monte_carlo_simulation': monte_carlo,
            'summary': {
                'base_case_value': dcf_valuation['value_per_share'],
                'current_price': dcf_valuation['current_price'],
                'upside_potential': dcf_valuation['upside_downside_percent'],
                'bear_case_value': scenarios['Bear Case']['value_per_share'],
                'bull_case_value': scenarios['Bull Case']['value_per_share'],
                'monte_carlo_mean': monte_carlo.get('mean', 0),
                'probability_of_upside': monte_carlo.get('probability_above_current', 0)
            }
        }


# Utility functions for external use
def quick_dcf_valuation(symbol: str, custom_assumptions: Optional[Dict] = None) -> Dict:
    """
    Quick DCF valuation function
    
    Args:
        symbol (str): Stock symbol
        custom_assumptions (Dict, optional): Custom assumptions
        
    Returns:
        Dict: Valuation results
    """
    dcf_model = DCFModel()
    return dcf_model.value_company(symbol, custom_assumptions)

def dcf_price_target(symbol: str, target_return: float = 0.15) -> float:
    """
    Calculate price target based on required return
    
    Args:
        symbol (str): Stock symbol
        target_return (float): Required annual return
        
    Returns:
        float: Price target
    """
    dcf_model = DCFModel()
    
    # Adjust discount rate to achieve target return
    assumptions = dcf_model.default_assumptions.copy()
    assumptions['discount_rate'] = target_return
    
    valuation = dcf_model.value_company(symbol, assumptions)
    return valuation['value_per_share']