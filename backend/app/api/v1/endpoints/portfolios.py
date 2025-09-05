"""
Portfolio management API endpoints.

Provides comprehensive portfolio management functionality including
CRUD operations, holdings management, and financial analytics.
"""

import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.portfolio import PortfolioHolding, PortfolioTransaction, PortfolioAlert
from app.schemas.portfolio import (
    PortfolioCreate, PortfolioUpdate, PortfolioResponse, PortfolioListResponse,
    PortfolioHoldingCreate, PortfolioHoldingUpdate, PortfolioHoldingResponse,
    PortfolioTransactionCreate, PortfolioTransactionResponse,
    PortfolioAlertCreate, PortfolioAlertUpdate, PortfolioAlertResponse,
    HoldingsListResponse, TransactionsListResponse, PerformanceResponse,
    OptimizationRequest, OptimizationResult, RebalancingRequest, RebalancingPlan,
    PortfolioAnalytics, PortfolioDetailResponse
)
from app.services.portfolio_service import PortfolioService
from app.services.portfolio_calculations import PortfolioCalculator

router = APIRouter()


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new portfolio."""
    service = PortfolioService(db)
    portfolio = await service.create_portfolio(current_user.id, portfolio_data)
    return portfolio


@router.get("/", response_model=PortfolioListResponse)
async def get_portfolios(
    skip: int = Query(0, ge=0, description="Number of portfolios to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of portfolios to return"),
    search: Optional[str] = Query(None, description="Search term for portfolio name or description"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's portfolios with pagination and filtering."""
    service = PortfolioService(db)
    portfolios, total = await service.get_portfolios(
        current_user.id, skip, limit, search, sort_by, sort_order
    )
    
    has_next = skip + limit < total
    has_prev = skip > 0
    
    return PortfolioListResponse(
        portfolios=portfolios,
        total=total,
        page=skip // limit + 1,
        limit=limit,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/{portfolio_id}", response_model=PortfolioDetailResponse)
async def get_portfolio(
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific portfolio with detailed information."""
    service = PortfolioService(db)
    
    # Get portfolio
    portfolio = await service.get_portfolio(portfolio_id, current_user.id)
    
    # Get holdings
    holdings = db.query(PortfolioHolding).filter(
        PortfolioHolding.portfolio_id == portfolio_id
    ).all()
    
    # Get recent transactions
    transactions = db.query(PortfolioTransaction).filter(
        PortfolioTransaction.portfolio_id == portfolio_id
    ).order_by(PortfolioTransaction.date.desc()).limit(10).all()
    
    # Get analytics
    analytics = await service.get_portfolio_analytics(portfolio_id, current_user.id)
    
    # Get alerts
    alerts = db.query(PortfolioAlert).filter(
        PortfolioAlert.portfolio_id == portfolio_id
    ).all()
    
    return PortfolioDetailResponse(
        portfolio=portfolio,
        holdings=holdings,
        transactions=transactions,
        analytics=analytics,
        alerts=alerts,
        tax_lots=[]  # TODO: Implement tax lot retrieval
    )


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_data: PortfolioUpdate,
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a portfolio."""
    service = PortfolioService(db)
    portfolio = await service.update_portfolio(portfolio_id, current_user.id, portfolio_data)
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a portfolio."""
    service = PortfolioService(db)
    await service.delete_portfolio(portfolio_id, current_user.id)


@router.post("/{portfolio_id}/duplicate", response_model=PortfolioResponse)
async def duplicate_portfolio(
    new_name: str = Query(..., description="Name for the duplicated portfolio"),
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID to duplicate"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Duplicate a portfolio."""
    service = PortfolioService(db)
    portfolio = await service.duplicate_portfolio(portfolio_id, current_user.id, new_name)
    return portfolio


# Holdings endpoints
@router.get("/{portfolio_id}/holdings", response_model=HoldingsListResponse)
async def get_holdings(
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio holdings."""
    service = PortfolioService(db)
    
    # Verify portfolio ownership
    portfolio = await service.get_portfolio(portfolio_id, current_user.id)
    
    # Get holdings
    holdings = db.query(PortfolioHolding).filter(
        PortfolioHolding.portfolio_id == portfolio_id
    ).all()
    
    # Calculate totals
    total_value = sum(h.market_value or 0 for h in holdings)
    total_cost = sum(h.total_cost for h in holdings)
    total_gain_loss = total_value - total_cost
    total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
    
    return HoldingsListResponse(
        holdings=holdings,
        total=len(holdings),
        total_value=total_value,
        total_cost=total_cost,
        total_gain_loss=total_gain_loss,
        total_gain_loss_percent=total_gain_loss_percent
    )


@router.post("/{portfolio_id}/holdings", response_model=PortfolioHoldingResponse)
async def add_holding(
    holding_data: PortfolioHoldingCreate,
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a holding to a portfolio."""
    service = PortfolioService(db)
    holding = await service.add_holding(portfolio_id, current_user.id, holding_data)
    return holding


@router.put("/{portfolio_id}/holdings/{holding_id}", response_model=PortfolioHoldingResponse)
async def update_holding(
    holding_data: PortfolioHoldingUpdate,
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    holding_id: uuid.UUID = Path(..., description="Holding ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a holding."""
    service = PortfolioService(db)
    holding = await service.update_holding(portfolio_id, holding_id, current_user.id, holding_data)
    return holding


@router.delete("/{portfolio_id}/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_holding(
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    holding_id: uuid.UUID = Path(..., description="Holding ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a holding from portfolio."""
    service = PortfolioService(db)
    await service.remove_holding(portfolio_id, holding_id, current_user.id)


# Transaction endpoints
@router.get("/{portfolio_id}/transactions", response_model=TransactionsListResponse)
async def get_transactions(
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of transactions to return"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio transactions."""
    service = PortfolioService(db)
    transactions, total = await service.get_transactions(
        portfolio_id, current_user.id, skip, limit, symbol, transaction_type
    )
    
    has_next = skip + limit < total
    has_prev = skip > 0
    
    return TransactionsListResponse(
        transactions=transactions,
        total=total,
        page=skip // limit + 1,
        limit=limit,
        has_next=has_next,
        has_prev=has_prev
    )


@router.post("/{portfolio_id}/transactions", response_model=PortfolioTransactionResponse)
async def add_transaction(
    transaction_data: PortfolioTransactionCreate,
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a transaction to a portfolio."""
    service = PortfolioService(db)
    transaction = await service.add_transaction(portfolio_id, current_user.id, transaction_data)
    return transaction


# Performance and analytics endpoints
@router.get("/{portfolio_id}/performance", response_model=PerformanceResponse)
async def get_performance(
    period: str = Query("1y", regex="^(1m|3m|6m|1y|2y|5y)$", description="Performance period"),
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio performance metrics."""
    service = PortfolioService(db)
    analytics = await service.get_portfolio_analytics(portfolio_id, current_user.id, period)
    
    # Extract performance data
    performance = analytics.get('performance')
    risk = analytics.get('risk')
    benchmark_comparison = analytics.get('benchmark_comparison')
    
    # Get performance history
    performance_history = []  # TODO: Implement performance history retrieval
    
    return PerformanceResponse(
        portfolio_id=portfolio_id,
        period=period,
        performance=performance,
        risk=risk,
        benchmark_comparison=benchmark_comparison,
        performance_history=performance_history
    )


@router.get("/{portfolio_id}/analytics", response_model=PortfolioAnalytics)
async def get_analytics(
    period: str = Query("1y", regex="^(1m|3m|6m|1y|2y|5y)$", description="Analytics period"),
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive portfolio analytics."""
    service = PortfolioService(db)
    analytics = await service.get_portfolio_analytics(portfolio_id, current_user.id, period)
    return analytics


# Utility endpoints
@router.post("/{portfolio_id}/refresh", status_code=status.HTTP_200_OK)
async def refresh_portfolio(
    portfolio_id: uuid.UUID = Path(..., description="Portfolio ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh portfolio metrics and valuations."""
    service = PortfolioService(db)
    
    # Verify portfolio ownership
    await service.get_portfolio(portfolio_id, current_user.id)
    
    # Update portfolio metrics
    success = await service.update_portfolio_metrics(portfolio_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh portfolio"
        )
    
    return {"message": "Portfolio refreshed successfully"}