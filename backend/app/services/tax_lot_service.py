"""
Tax lot management service.

Provides tax lot tracking and cost basis calculations for portfolio holdings.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
import logging

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.portfolio import (
    Portfolio, PortfolioHolding, PortfolioTransaction, TaxLot
)
from app.schemas.portfolio import TaxLotSummary

logger = logging.getLogger(__name__)


class TaxLotService:
    """Service for managing tax lots and cost basis calculations."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
    
    async def create_tax_lot(
        self, 
        portfolio_id: uuid.UUID, 
        transaction_id: uuid.UUID,
        symbol: str,
        shares: Decimal,
        cost_basis: Decimal,
        purchase_date: datetime
    ) -> TaxLot:
        """Create a new tax lot."""
        try:
            tax_lot = TaxLot(
                portfolio_id=portfolio_id,
                transaction_id=transaction_id,
                symbol=symbol,
                shares=shares,
                cost_basis=cost_basis,
                purchase_date=purchase_date,
                remaining_shares=shares
            )
            
            self.db.add(tax_lot)
            self.db.commit()
            self.db.refresh(tax_lot)
            
            logger.info(f"Created tax lot {tax_lot.id} for {symbol}")
            return tax_lot
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create tax lot: {e}")
            raise
    
    async def update_tax_lot_prices(self, portfolio_id: uuid.UUID, current_prices: Dict[str, Decimal]):
        """Update current prices for tax lots."""
        try:
            tax_lots = self.db.query(TaxLot).filter(
                and_(
                    TaxLot.portfolio_id == portfolio_id,
                    TaxLot.remaining_shares > 0
                )
            ).all()
            
            for tax_lot in tax_lots:
                if tax_lot.symbol in current_prices:
                    current_price = current_prices[tax_lot.symbol]
                    tax_lot.current_price = current_price
                    tax_lot.current_value = tax_lot.remaining_shares * current_price
                    
                    # Calculate unrealized gain/loss
                    tax_lot.unrealized_gain_loss = tax_lot.current_value - tax_lot.cost_basis
                    if tax_lot.cost_basis > 0:
                        tax_lot.unrealized_gain_loss_percent = (
                            tax_lot.unrealized_gain_loss / tax_lot.cost_basis
                        ) * 100
                    
                    # Calculate holding period
                    holding_days = (datetime.utcnow() - tax_lot.purchase_date).days
                    tax_lot.holding_period_days = holding_days
                    tax_lot.is_long_term = holding_days >= 365  # Long-term if held > 1 year
            
            self.db.commit()
            logger.info(f"Updated prices for {len(tax_lots)} tax lots")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update tax lot prices: {e}")
            raise
    
    async def process_sale_transaction(
        self, 
        portfolio_id: uuid.UUID, 
        symbol: str, 
        shares_sold: Decimal,
        sale_price: Decimal,
        sale_date: datetime,
        cost_basis_method: str = "FIFO"
    ) -> List[Dict[str, Any]]:
        """Process a sale transaction and update tax lots."""
        try:
            # Get available tax lots for this symbol
            tax_lots = self.db.query(TaxLot).filter(
                and_(
                    TaxLot.portfolio_id == portfolio_id,
                    TaxLot.symbol == symbol,
                    TaxLot.remaining_shares > 0
                )
            ).order_by(
                TaxLot.purchase_date.asc() if cost_basis_method == "FIFO" 
                else TaxLot.purchase_date.desc()
            ).all()
            
            if not tax_lots:
                raise ValueError(f"No tax lots found for symbol {symbol}")
            
            # Calculate total available shares
            total_available = sum(tl.remaining_shares for tl in tax_lots)
            if total_available < shares_sold:
                raise ValueError(f"Insufficient shares. Available: {total_available}, Requested: {shares_sold}")
            
            # Process sale using specified method
            remaining_to_sell = shares_sold
            sale_details = []
            
            for tax_lot in tax_lots:
                if remaining_to_sell <= 0:
                    break
                
                # Determine shares to sell from this lot
                shares_from_lot = min(remaining_to_sell, tax_lot.remaining_shares)
                
                # Calculate cost basis for this portion
                cost_basis_per_share = tax_lot.cost_basis / tax_lot.shares
                cost_basis_for_sale = shares_from_lot * cost_basis_per_share
                
                # Calculate gain/loss
                proceeds = shares_from_lot * sale_price
                gain_loss = proceeds - cost_basis_for_sale
                
                # Update tax lot
                tax_lot.remaining_shares -= shares_from_lot
                tax_lot.cost_basis -= cost_basis_for_sale
                
                # Store sale details
                sale_details.append({
                    'tax_lot_id': tax_lot.id,
                    'shares_sold': shares_from_lot,
                    'cost_basis': cost_basis_for_sale,
                    'proceeds': proceeds,
                    'gain_loss': gain_loss,
                    'holding_period_days': (sale_date - tax_lot.purchase_date).days,
                    'is_long_term': (sale_date - tax_lot.purchase_date).days >= 365
                })
                
                remaining_to_sell -= shares_from_lot
            
            self.db.commit()
            logger.info(f"Processed sale of {shares_sold} shares of {symbol}")
            return sale_details
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to process sale transaction: {e}")
            raise
    
    async def get_tax_lot_summary(self, portfolio_id: uuid.UUID, symbol: str) -> TaxLotSummary:
        """Get tax lot summary for a specific symbol."""
        try:
            tax_lots = self.db.query(TaxLot).filter(
                and_(
                    TaxLot.portfolio_id == portfolio_id,
                    TaxLot.symbol == symbol
                )
            ).all()
            
            if not tax_lots:
                return TaxLotSummary(
                    symbol=symbol,
                    total_shares=Decimal('0'),
                    total_cost_basis=Decimal('0'),
                    average_cost_basis=Decimal('0'),
                    current_value=Decimal('0'),
                    unrealized_gain_loss=Decimal('0'),
                    unrealized_gain_loss_percent=Decimal('0'),
                    long_term_shares=Decimal('0'),
                    short_term_shares=Decimal('0'),
                    long_term_gain_loss=Decimal('0'),
                    short_term_gain_loss=Decimal('0'),
                    tax_lots=[]
                )
            
            # Calculate summary metrics
            total_shares = sum(tl.remaining_shares for tl in tax_lots)
            total_cost_basis = sum(tl.cost_basis for tl in tax_lots)
            average_cost_basis = total_cost_basis / total_shares if total_shares > 0 else Decimal('0')
            current_value = sum(tl.current_value or Decimal('0') for tl in tax_lots)
            unrealized_gain_loss = current_value - total_cost_basis
            unrealized_gain_loss_percent = (
                (unrealized_gain_loss / total_cost_basis * 100) if total_cost_basis > 0 else Decimal('0')
            )
            
            # Separate long-term and short-term
            long_term_shares = sum(tl.remaining_shares for tl in tax_lots if tl.is_long_term)
            short_term_shares = total_shares - long_term_shares
            long_term_gain_loss = sum(
                (tl.current_value or Decimal('0')) - tl.cost_basis 
                for tl in tax_lots if tl.is_long_term
            )
            short_term_gain_loss = unrealized_gain_loss - long_term_gain_loss
            
            return TaxLotSummary(
                symbol=symbol,
                total_shares=total_shares,
                total_cost_basis=total_cost_basis,
                average_cost_basis=average_cost_basis,
                current_value=current_value,
                unrealized_gain_loss=unrealized_gain_loss,
                unrealized_gain_loss_percent=unrealized_gain_loss_percent,
                long_term_shares=long_term_shares,
                short_term_shares=short_term_shares,
                long_term_gain_loss=long_term_gain_loss,
                short_term_gain_loss=short_term_gain_loss,
                tax_lots=tax_lots
            )
            
        except Exception as e:
            logger.error(f"Failed to get tax lot summary: {e}")
            raise
    
    async def get_portfolio_tax_lots(self, portfolio_id: uuid.UUID) -> List[TaxLotSummary]:
        """Get tax lot summaries for all symbols in a portfolio."""
        try:
            # Get all unique symbols with tax lots
            symbols = self.db.query(TaxLot.symbol).filter(
                and_(
                    TaxLot.portfolio_id == portfolio_id,
                    TaxLot.remaining_shares > 0
                )
            ).distinct().all()
            
            summaries = []
            for (symbol,) in symbols:
                summary = await self.get_tax_lot_summary(portfolio_id, symbol)
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to get portfolio tax lots: {e}")
            raise
    
    async def calculate_tax_impact(
        self, 
        portfolio_id: uuid.UUID, 
        proposed_sales: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate tax impact of proposed sales."""
        try:
            total_proceeds = Decimal('0')
            total_cost_basis = Decimal('0')
            total_gain_loss = Decimal('0')
            long_term_gain_loss = Decimal('0')
            short_term_gain_loss = Decimal('0')
            
            sale_details = []
            
            for sale in proposed_sales:
                symbol = sale['symbol']
                shares = Decimal(str(sale['shares']))
                price = Decimal(str(sale['price']))
                
                # Process the sale to get tax lot details
                details = await self.process_sale_transaction(
                    portfolio_id, symbol, shares, price, datetime.utcnow()
                )
                
                for detail in details:
                    total_proceeds += detail['proceeds']
                    total_cost_basis += detail['cost_basis']
                    total_gain_loss += detail['gain_loss']
                    
                    if detail['is_long_term']:
                        long_term_gain_loss += detail['gain_loss']
                    else:
                        short_term_gain_loss += detail['gain_loss']
                    
                    sale_details.append(detail)
            
            # Calculate tax impact (simplified - would need actual tax rates)
            # Assuming 20% long-term capital gains, 37% short-term
            long_term_tax = long_term_gain_loss * Decimal('0.20') if long_term_gain_loss > 0 else Decimal('0')
            short_term_tax = short_term_gain_loss * Decimal('0.37') if short_term_gain_loss > 0 else Decimal('0')
            total_tax = long_term_tax + short_term_tax
            
            return {
                'total_proceeds': total_proceeds,
                'total_cost_basis': total_cost_basis,
                'total_gain_loss': total_gain_loss,
                'long_term_gain_loss': long_term_gain_loss,
                'short_term_gain_loss': short_term_gain_loss,
                'long_term_tax': long_term_tax,
                'short_term_tax': short_term_tax,
                'total_tax': total_tax,
                'after_tax_proceeds': total_proceeds - total_tax,
                'sale_details': sale_details
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate tax impact: {e}")
            raise
    
    async def optimize_tax_loss_harvesting(
        self, 
        portfolio_id: uuid.UUID, 
        target_loss: Decimal
    ) -> List[Dict[str, Any]]:
        """Suggest tax loss harvesting opportunities."""
        try:
            # Get all tax lots with unrealized losses
            tax_lots = self.db.query(TaxLot).filter(
                and_(
                    TaxLot.portfolio_id == portfolio_id,
                    TaxLot.remaining_shares > 0,
                    TaxLot.unrealized_gain_loss < 0  # Only losses
                )
            ).order_by(TaxLot.unrealized_gain_loss.asc()).all()  # Largest losses first
            
            suggestions = []
            total_loss = Decimal('0')
            
            for tax_lot in tax_lots:
                if total_loss >= target_loss:
                    break
                
                # Calculate potential loss from selling this lot
                potential_loss = abs(tax_lot.unrealized_gain_loss)
                
                # Check for wash sale rules (simplified)
                # In real implementation, you'd check for purchases within 30 days
                is_wash_sale = False  # Placeholder
                
                if not is_wash_sale:
                    suggestions.append({
                        'symbol': tax_lot.symbol,
                        'shares': tax_lot.remaining_shares,
                        'cost_basis': tax_lot.cost_basis,
                        'current_value': tax_lot.current_value,
                        'unrealized_loss': tax_lot.unrealized_gain_loss,
                        'holding_period_days': tax_lot.holding_period_days,
                        'is_long_term': tax_lot.is_long_term,
                        'tax_benefit': abs(tax_lot.unrealized_gain_loss) * Decimal('0.37')  # Assuming 37% tax rate
                    })
                    
                    total_loss += potential_loss
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to optimize tax loss harvesting: {e}")
            raise
    
    async def get_tax_report(
        self, 
        portfolio_id: uuid.UUID, 
        year: int
    ) -> Dict[str, Any]:
        """Generate tax report for a specific year."""
        try:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            
            # Get all transactions for the year
            transactions = self.db.query(PortfolioTransaction).filter(
                and_(
                    PortfolioTransaction.portfolio_id == portfolio_id,
                    PortfolioTransaction.date >= start_date,
                    PortfolioTransaction.date <= end_date,
                    PortfolioTransaction.transaction_type.in_(['sell', 'dividend'])
                )
            ).all()
            
            # Calculate realized gains/losses
            realized_gains = Decimal('0')
            realized_losses = Decimal('0')
            dividends = Decimal('0')
            
            for transaction in transactions:
                if transaction.transaction_type == 'sell':
                    # This would need to be calculated from tax lot sales
                    # Simplified for now
                    pass
                elif transaction.transaction_type == 'dividend':
                    dividends += transaction.total_amount
            
            return {
                'year': year,
                'realized_gains': realized_gains,
                'realized_losses': realized_losses,
                'net_realized_gain_loss': realized_gains + realized_losses,
                'dividends': dividends,
                'transactions': len(transactions)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate tax report: {e}")
            raise
