"""
Portfolio WebSocket endpoints for real-time updates.
"""

import uuid
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user_websocket
from app.models.user import User
from app.services.portfolio_websocket import PortfolioWebSocketService

router = APIRouter()


@router.websocket("/ws/portfolios")
async def portfolio_websocket(
    websocket: WebSocket,
    portfolio_ids: str = Query(..., description="Comma-separated list of portfolio IDs"),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time portfolio updates."""
    try:
        # Parse portfolio IDs
        portfolio_id_strings = [pid.strip() for pid in portfolio_ids.split(',')]
        portfolio_ids_list = []
        
        for pid_str in portfolio_id_strings:
            try:
                portfolio_id = uuid.UUID(pid_str)
                portfolio_ids_list.append(portfolio_id)
            except ValueError:
                await websocket.close(code=4000, reason="Invalid portfolio ID format")
                return
        
        # Authenticate user (simplified - in real implementation, you'd use proper auth)
        # For now, we'll use a placeholder user ID
        user_id = uuid.uuid4()  # This should come from authentication
        
        # Initialize WebSocket service
        ws_service = PortfolioWebSocketService(db)
        
        # Handle WebSocket connection
        await ws_service.handle_websocket_connection(websocket, user_id, portfolio_ids_list)
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=4000, reason="Internal server error")
        except:
            pass


@router.websocket("/ws/portfolios/{portfolio_id}")
async def single_portfolio_websocket(
    websocket: WebSocket,
    portfolio_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for single portfolio updates."""
    try:
        # Authenticate user (simplified)
        user_id = uuid.uuid4()  # This should come from authentication
        
        # Initialize WebSocket service
        ws_service = PortfolioWebSocketService(db)
        
        # Handle WebSocket connection for single portfolio
        await ws_service.handle_websocket_connection(websocket, user_id, [portfolio_id])
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=4000, reason="Internal server error")
        except:
            pass
