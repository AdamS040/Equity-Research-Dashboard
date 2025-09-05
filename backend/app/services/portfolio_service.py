"""
Portfolio management service.

Provides comprehensive portfolio management functionality including
CRUD operations, real-time updates, and financial calculations.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
import logging

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from fastapi import HTTPException, status

from app.models.portfolio import (
    Portfolio, PortfolioHolding, PortfolioTransaction, PortfolioPerformance,
    PortfolioAlert, TaxLot, PortfolioRiskMetrics, PortfolioAllocation,
    PortfolioOptimization, PortfolioRebalancing
)
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioCreate, PortfolioUpdate, PortfolioHoldingCreate, PortfolioHoldingUpdate,
    PortfolioTransactionCreate, PortfolioTransactionUpdate, PortfolioAlertCreate,
    OptimizationConstraints, RebalancingRequest
)
from app.services.portfolio_calculations import PortfolioCalculator
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)


class PortfolioService:
    """Portfolio management service."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
        self.calculator = PortfolioCalculator()
        self.market_data_service = MarketDataService()
    
    # Portfolio CRUD operations
    async def create_portfolio(self, user_id: uuid.UUID, portfolio_data: PortfolioCreate) -> Portfolio:
        """Create a new portfolio."""
        try:
            portfolio = Portfolio(
                user_id=user_id,
                name=portfolio_data.name,
                description=portfolio_data.description,
                currency=portfolio_data.currency,
                benchmark_symbol=portfolio_data.benchmark_symbol,
                risk_tolerance=portfolio_data.risk_tolerance.value,
                settings=portfolio_data.settings,
                is_public=portfolio_data.is_public
            )
            
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
            
            logger.info(f"Created portfolio {portfolio.id} for user {user_id}")
            return portfolio
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create portfolio: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create portfolio"
            )
    
    async def get_portfolios(
        self, 
        user_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Portfolio], int]:
        """Get user's portfolios with pagination and filtering."""
        try:
            query = self.db.query(Portfolio).filter(Portfolio.user_id == user_id)
            
            # Search filter
            if search:
                query = query.filter(
                    or_(
                        Portfolio.name.ilike(f"%{search}%"),
                        Portfolio.description.ilike(f"%{search}%")
                    )
                )
            
            # Sorting
            sort_column = getattr(Portfolio, sort_by, Portfolio.created_at)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Get total count
            total = query.count()
            
            # Pagination
            portfolios = query.offset(skip).limit(limit).all()
            
            return portfolios, total
            
        except Exception as e:
            logger.error(f"Failed to get portfolios: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve portfolios"
            )
    
    async def get_portfolio(self, portfolio_id: uuid.UUID, user_id: uuid.UUID) -> Portfolio:
        """Get a specific portfolio."""
        portfolio = self.db.query(Portfolio).filter(
            and_(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == user_id
            )
        ).first()
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        return portfolio
    
    async def update_portfolio(
        self, 
        portfolio_id: uuid.UUID, 
        user_id: uuid.UUID, 
        portfolio_data: PortfolioUpdate
    ) -> Portfolio:
        """Update a portfolio."""
        portfolio = await self.get_portfolio(portfolio_id, user_id)
        
        try:
            # Update fields
            update_data = portfolio_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(portfolio, field):
                    setattr(portfolio, field, value)
            
            portfolio.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(portfolio)
            
            logger.info(f"Updated portfolio {portfolio_id}")
            return portfolio
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update portfolio: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update portfolio"
            )
    
    async def delete_portfolio(self, portfolio_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete a portfolio."""
        portfolio = await self.get_portfolio(portfolio_id, user_id)
        
        try:
            self.db.delete(portfolio)
            self.db.commit()
            
            logger.info(f"Deleted portfolio {portfolio_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete portfolio: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete portfolio"
            )
    
    async def duplicate_portfolio(
        self, 
        portfolio_id: uuid.UUID, 
        user_id: uuid.UUID, 
        new_name: str
    ) -> Portfolio:
        """Duplicate a portfolio."""
        original_portfolio = await self.get_portfolio(portfolio_id, user_id)
        
        try:
            # Create new portfolio
            new_portfolio = Portfolio(
                user_id=user_id,
                name=new_name,
                description=original_portfolio.description,
                currency=original_portfolio.currency,
                benchmark_symbol=original_portfolio.benchmark_symbol,
                risk_tolerance=original_portfolio.risk_tolerance,
                settings=original_portfolio.settings,
                is_public=False  # Duplicated portfolios are private by default
            )
            
            self.db.add(new_portfolio)
            self.db.flush()  # Get the ID
            
            # Copy holdings
            for holding in original_portfolio.holdings:
                new_holding = PortfolioHolding(
                    portfolio_id=new_portfolio.id,
                    symbol=holding.symbol,
                    name=holding.name,
                    exchange=holding.exchange,
                    shares=holding.shares,
                    average_price=holding.average_price,
                    current_price=holding.current_price,
                    sector=holding.sector,
                    industry=holding.industry,
                    market_cap=holding.market_cap
                )
                self.db.add(new_holding)
            
            # Copy transactions
            for transaction in original_portfolio.transactions:
                new_transaction = PortfolioTransaction(
                    portfolio_id=new_portfolio.id,
                    symbol=transaction.symbol,
                    transaction_type=transaction.transaction_type,
                    shares=transaction.shares,
                    price=transaction.price,
                    commission=transaction.commission,
                    fees=transaction.fees,
                    date=transaction.date,
                    notes=transaction.notes,
                    order_id=transaction.order_id,
                    broker=transaction.broker,
                    metadata=transaction.metadata
                )
                self.db.add(new_transaction)
            
            self.db.commit()
            self.db.refresh(new_portfolio)
            
            # Recalculate portfolio metrics
            await self.update_portfolio_metrics(new_portfolio.id)
            
            logger.info(f"Duplicated portfolio {portfolio_id} to {new_portfolio.id}")
            return new_portfolio
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to duplicate portfolio: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to duplicate portfolio"
            )
    
    # Holdings management
    async def add_holding(
        self, 
        portfolio_id: uuid.UUID, 
        user_id: uuid.UUID, 
        holding_data: PortfolioHoldingCreate
    ) -> PortfolioHolding:
        """Add a holding to a portfolio."""
        portfolio = await self.get_portfolio(portfolio_id, user_id)
        
        try:
            # Check if holding already exists
            existing_holding = self.db.query(PortfolioHolding).filter(
                and_(
                    PortfolioHolding.portfolio_id == portfolio_id,
                    PortfolioHolding.symbol == holding_data.symbol
                )
            ).first()
            
            if existing_holding:
                # Update existing holding
                existing_holding.shares += holding_data.shares
                # Recalculate average price
                total_cost = (existing_holding.shares * existing_holding.average_price + 
                            holding_data.shares * holding_data.average_price)
                existing_holding.shares += holding_data.shares
                existing_holding.average_price = total_cost / existing_holding.shares
                existing_holding.updated_at = datetime.utcnow()
                
                holding = existing_holding
            else:
                # Create new holding
                holding = PortfolioHolding(
                    portfolio_id=portfolio_id,
                    symbol=holding_data.symbol,
                    name=holding_data.name,
                    exchange=holding_data.exchange,
                    shares=holding_data.shares,
                    average_price=holding_data.average_price,
                    current_price=holding_data.current_price,
                    sector=holding_data.sector,
                    industry=holding_data.industry,
                    market_cap=holding_data.market_cap
                )
                self.db.add(holding)
            
            self.db.commit()
            self.db.refresh(holding)
            
            # Update portfolio metrics
            await self.update_portfolio_metrics(portfolio_id)
            
            logger.info(f"Added holding {holding_data.symbol} to portfolio {portfolio_id}")
            return holding
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add holding: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add holding"
            )
    
    async def update_holding(
        self, 
        portfolio_id: uuid.UUID, 
        holding_id: uuid.UUID, 
        user_id: uuid.UUID, 
        holding_data: PortfolioHoldingUpdate
    ) -> PortfolioHolding:
        """Update a holding."""
        # Verify portfolio ownership
        await self.get_portfolio(portfolio_id, user_id)
        
        holding = self.db.query(PortfolioHolding).filter(
            and_(
                PortfolioHolding.id == holding_id,
                PortfolioHolding.portfolio_id == portfolio_id
            )
        ).first()
        
        if not holding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Holding not found"
            )
        
        try:
            # Update fields
            update_data = holding_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(holding, field):
                    setattr(holding, field, value)
            
            holding.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(holding)
            
            # Update portfolio metrics
            await self.update_portfolio_metrics(portfolio_id)
            
            logger.info(f"Updated holding {holding_id}")
            return holding
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update holding: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update holding"
            )
    
    async def remove_holding(
        self, 
        portfolio_id: uuid.UUID, 
        holding_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> bool:
        """Remove a holding from portfolio."""
        # Verify portfolio ownership
        await self.get_portfolio(portfolio_id, user_id)
        
        holding = self.db.query(PortfolioHolding).filter(
            and_(
                PortfolioHolding.id == holding_id,
                PortfolioHolding.portfolio_id == portfolio_id
            )
        ).first()
        
        if not holding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Holding not found"
            )
        
        try:
            self.db.delete(holding)
            self.db.commit()
            
            # Update portfolio metrics
            await self.update_portfolio_metrics(portfolio_id)
            
            logger.info(f"Removed holding {holding_id} from portfolio {portfolio_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to remove holding: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove holding"
            )
    
    # Transaction management
    async def add_transaction(
        self, 
        portfolio_id: uuid.UUID, 
        user_id: uuid.UUID, 
        transaction_data: PortfolioTransactionCreate
    ) -> PortfolioTransaction:
        """Add a transaction to a portfolio."""
        portfolio = await self.get_portfolio(portfolio_id, user_id)
        
        try:
            transaction = PortfolioTransaction(
                portfolio_id=portfolio_id,
                symbol=transaction_data.symbol,
                transaction_type=transaction_data.transaction_type.value,
                shares=transaction_data.shares,
                price=transaction_data.price,
                commission=transaction_data.commission,
                fees=transaction_data.fees,
                date=transaction_data.date,
                notes=transaction_data.notes,
                order_id=transaction_data.order_id,
                broker=transaction_data.broker,
                metadata=transaction_data.metadata
            )
            
            # Calculate total amount
            transaction.total_amount = transaction.shares * transaction.price + transaction.commission + transaction.fees
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            # Update holdings based on transaction
            await self._update_holdings_from_transaction(portfolio_id, transaction)
            
            # Update portfolio metrics
            await self.update_portfolio_metrics(portfolio_id)
            
            logger.info(f"Added transaction {transaction.id} to portfolio {portfolio_id}")
            return transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add transaction: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add transaction"
            )
    
    async def get_transactions(
        self, 
        portfolio_id: uuid.UUID, 
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        symbol: Optional[str] = None,
        transaction_type: Optional[str] = None
    ) -> Tuple[List[PortfolioTransaction], int]:
        """Get portfolio transactions with filtering."""
        # Verify portfolio ownership
        await self.get_portfolio(portfolio_id, user_id)
        
        try:
            query = self.db.query(PortfolioTransaction).filter(
                PortfolioTransaction.portfolio_id == portfolio_id
            )
            
            # Apply filters
            if symbol:
                query = query.filter(PortfolioTransaction.symbol == symbol)
            if transaction_type:
                query = query.filter(PortfolioTransaction.transaction_type == transaction_type)
            
            # Get total count
            total = query.count()
            
            # Pagination and sorting
            transactions = query.order_by(desc(PortfolioTransaction.date)).offset(skip).limit(limit).all()
            
            return transactions, total
            
        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve transactions"
            )
    
    # Portfolio metrics and calculations
    async def update_portfolio_metrics(self, portfolio_id: uuid.UUID) -> bool:
        """Update portfolio metrics and valuations."""
        try:
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return False
            
            # Get current holdings
            holdings = self.db.query(PortfolioHolding).filter(
                PortfolioHolding.portfolio_id == portfolio_id
            ).all()
            
            # Update current prices
            await self._update_holding_prices(holdings)
            
            # Calculate portfolio metrics
            total_value = Decimal('0')
            total_cost = Decimal('0')
            
            for holding in holdings:
                if holding.current_price:
                    market_value = holding.shares * holding.current_price
                    holding.market_value = market_value
                    total_value += market_value
                
                cost_basis = holding.shares * holding.average_price
                holding.total_cost = cost_basis
                total_cost += cost_basis
                
                # Calculate unrealized gain/loss
                if holding.market_value:
                    holding.unrealized_gain_loss = holding.market_value - holding.total_cost
                    if holding.total_cost > 0:
                        holding.unrealized_gain_loss_percent = (
                            holding.unrealized_gain_loss / holding.total_cost
                        ) * 100
            
            # Update portfolio totals
            portfolio.total_value = total_value
            portfolio.total_cost = total_cost
            portfolio.total_gain_loss = total_value - total_cost
            
            if total_cost > 0:
                portfolio.total_gain_loss_percent = (portfolio.total_gain_loss / total_cost) * 100
            
            portfolio.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Updated portfolio metrics for {portfolio_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update portfolio metrics: {e}")
            return False
    
    async def get_portfolio_analytics(
        self, 
        portfolio_id: uuid.UUID, 
        user_id: uuid.UUID,
        period: str = "1y"
    ) -> Dict[str, Any]:
        """Get comprehensive portfolio analytics."""
        portfolio = await self.get_portfolio(portfolio_id, user_id)
        
        try:
            # Get holdings data
            holdings = self.db.query(PortfolioHolding).filter(
                PortfolioHolding.portfolio_id == portfolio_id
            ).all()
            
            # Get performance history
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=365)  # Default to 1 year
            
            if period == "1m":
                start_date = end_date - timedelta(days=30)
            elif period == "3m":
                start_date = end_date - timedelta(days=90)
            elif period == "6m":
                start_date = end_date - timedelta(days=180)
            elif period == "2y":
                start_date = end_date - timedelta(days=730)
            elif period == "5y":
                start_date = end_date - timedelta(days=1825)
            
            performance_data = self.db.query(PortfolioPerformance).filter(
                and_(
                    PortfolioPerformance.portfolio_id == portfolio_id,
                    PortfolioPerformance.date >= start_date,
                    PortfolioPerformance.date <= end_date
                )
            ).order_by(PortfolioPerformance.date).all()
            
            # Calculate analytics
            analytics = {}
            
            # Performance metrics
            if performance_data:
                portfolio_values = [p.total_value for p in performance_data]
                returns = self.calculator.calculate_portfolio_returns(portfolio_values)
                
                if returns:
                    analytics['performance'] = self.calculator.calculate_performance_metrics(
                        returns, portfolio_values
                    )
            
            # Allocation metrics
            holdings_data = [
                {
                    'symbol': h.symbol,
                    'name': h.name,
                    'shares': h.shares,
                    'current_price': h.current_price,
                    'sector': h.sector,
                    'industry': h.industry,
                    'market_cap': h.market_cap
                }
                for h in holdings
            ]
            
            analytics['allocation'] = self.calculator.calculate_allocation_metrics(holdings_data)
            
            # Risk metrics (if benchmark data available)
            if portfolio.benchmark_symbol and performance_data:
                # Get benchmark data
                benchmark_data = await self._get_benchmark_data(
                    portfolio.benchmark_symbol, start_date, end_date
                )
                
                if benchmark_data and returns:
                    benchmark_returns = self.calculator.calculate_portfolio_returns(benchmark_data)
                    analytics['risk'] = self.calculator.calculate_risk_metrics(returns, benchmark_returns)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get portfolio analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate portfolio analytics"
            )
    
    # Private helper methods
    async def _update_holding_prices(self, holdings: List[PortfolioHolding]) -> None:
        """Update current prices for holdings."""
        symbols = [h.symbol for h in holdings]
        
        try:
            # Get current quotes
            quotes = await self.market_data_service.get_quotes(symbols)
            
            for holding in holdings:
                if holding.symbol in quotes:
                    quote = quotes[holding.symbol]
                    holding.current_price = Decimal(str(quote.get('price', 0)))
                    holding.last_price_update = datetime.utcnow()
        
        except Exception as e:
            logger.warning(f"Failed to update holding prices: {e}")
    
    async def _update_holdings_from_transaction(
        self, 
        portfolio_id: uuid.UUID, 
        transaction: PortfolioTransaction
    ) -> None:
        """Update holdings based on transaction."""
        holding = self.db.query(PortfolioHolding).filter(
            and_(
                PortfolioHolding.portfolio_id == portfolio_id,
                PortfolioHolding.symbol == transaction.symbol
            )
        ).first()
        
        if transaction.transaction_type == "buy":
            if holding:
                # Update existing holding
                total_shares = holding.shares + transaction.shares
                total_cost = (holding.shares * holding.average_price + 
                            transaction.shares * transaction.price)
                holding.shares = total_shares
                holding.average_price = total_cost / total_shares
            else:
                # Create new holding
                holding = PortfolioHolding(
                    portfolio_id=portfolio_id,
                    symbol=transaction.symbol,
                    shares=transaction.shares,
                    average_price=transaction.price
                )
                self.db.add(holding)
        
        elif transaction.transaction_type == "sell":
            if holding and holding.shares >= transaction.shares:
                holding.shares -= transaction.shares
                if holding.shares == 0:
                    self.db.delete(holding)
    
    async def _get_benchmark_data(
        self, 
        benchmark_symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Optional[List[Decimal]]:
        """Get benchmark data for comparison."""
        try:
            # This would integrate with market data service
            # For now, return None
            return None
        except Exception as e:
            logger.warning(f"Failed to get benchmark data: {e}")
            return None
