"""
Portfolio WebSocket service for real-time updates.

Provides real-time portfolio updates, price changes, and notifications.
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.portfolio import Portfolio, PortfolioHolding, PortfolioAlert
from app.services.portfolio_service import PortfolioService
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)


class PortfolioWebSocketManager:
    """Manages WebSocket connections for portfolio updates."""
    
    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        self.price_update_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def connect(self, websocket: WebSocket, user_id: UUID, portfolio_ids: List[UUID]):
        """Accept WebSocket connection and register for portfolio updates."""
        await websocket.accept()
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            'user_id': user_id,
            'portfolio_ids': portfolio_ids,
            'connected_at': datetime.utcnow(),
            'last_ping': datetime.utcnow()
        }
        
        # Register connection for each portfolio
        for portfolio_id in portfolio_ids:
            if portfolio_id not in self.active_connections:
                self.active_connections[portfolio_id] = set()
            self.active_connections[portfolio_id].add(websocket)
        
        logger.info(f"WebSocket connected for user {user_id}, portfolios: {portfolio_ids}")
        
        # Start price update task if not running
        if not self.is_running:
            await self.start_price_updates()
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.connection_metadata:
            metadata = self.connection_metadata[websocket]
            user_id = metadata['user_id']
            portfolio_ids = metadata['portfolio_ids']
            
            # Remove from all portfolio connections
            for portfolio_id in portfolio_ids:
                if portfolio_id in self.active_connections:
                    self.active_connections[portfolio_id].discard(websocket)
                    if not self.active_connections[portfolio_id]:
                        del self.active_connections[portfolio_id]
            
            # Remove metadata
            del self.connection_metadata[websocket]
            
            logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def send_portfolio_update(self, portfolio_id: UUID, message: Dict[str, Any]):
        """Send update to all connections subscribed to a portfolio."""
        if portfolio_id in self.active_connections:
            connections = self.active_connections[portfolio_id].copy()
            for connection in connections:
                await self.send_personal_message(message, connection)
    
    async def broadcast_to_user(self, user_id: UUID, message: Dict[str, Any]):
        """Send message to all connections for a specific user."""
        user_connections = [
            ws for ws, metadata in self.connection_metadata.items()
            if metadata['user_id'] == user_id
        ]
        
        for connection in user_connections:
            await self.send_personal_message(message, connection)
    
    async def start_price_updates(self):
        """Start background task for price updates."""
        if self.is_running:
            return
        
        self.is_running = True
        self.price_update_task = asyncio.create_task(self._price_update_loop())
        logger.info("Started portfolio price update loop")
    
    async def stop_price_updates(self):
        """Stop background price update task."""
        self.is_running = False
        if self.price_update_task:
            self.price_update_task.cancel()
            try:
                await self.price_update_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped portfolio price update loop")
    
    async def _price_update_loop(self):
        """Background loop for updating portfolio prices."""
        while self.is_running:
            try:
                if not self.active_connections:
                    await asyncio.sleep(5)
                    continue
                
                # Get all unique symbols from active portfolios
                symbols = await self._get_active_symbols()
                
                if symbols:
                    # Get current prices
                    market_service = MarketDataService()
                    quotes = await market_service.get_quotes(symbols)
                    
                    # Update portfolios and send notifications
                    await self._update_portfolio_prices(quotes)
                
                # Wait before next update
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in price update loop: {e}")
                await asyncio.sleep(10)
    
    async def _get_active_symbols(self) -> Set[str]:
        """Get all symbols from active portfolios."""
        symbols = set()
        
        for portfolio_id in self.active_connections.keys():
            # Get holdings for this portfolio
            # This would need database access - simplified for now
            # In real implementation, you'd query the database
            pass
        
        return symbols
    
    async def _update_portfolio_prices(self, quotes: Dict[str, Any]):
        """Update portfolio prices and send notifications."""
        # This would update the database and send WebSocket notifications
        # Implementation depends on your database setup
        pass
    
    async def handle_portfolio_update(self, portfolio_id: UUID, update_type: str, data: Any):
        """Handle portfolio update and broadcast to subscribers."""
        message = {
            'type': 'portfolio_update',
            'portfolio_id': str(portfolio_id),
            'update_type': update_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.send_portfolio_update(portfolio_id, message)
    
    async def handle_holding_update(self, portfolio_id: UUID, holding_id: UUID, data: Any):
        """Handle holding update and broadcast to subscribers."""
        message = {
            'type': 'holding_update',
            'portfolio_id': str(portfolio_id),
            'holding_id': str(holding_id),
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.send_portfolio_update(portfolio_id, message)
    
    async def handle_performance_update(self, portfolio_id: UUID, data: Any):
        """Handle performance update and broadcast to subscribers."""
        message = {
            'type': 'performance_update',
            'portfolio_id': str(portfolio_id),
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.send_portfolio_update(portfolio_id, message)
    
    async def handle_risk_update(self, portfolio_id: UUID, data: Any):
        """Handle risk update and broadcast to subscribers."""
        message = {
            'type': 'risk_update',
            'portfolio_id': str(portfolio_id),
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.send_portfolio_update(portfolio_id, message)
    
    async def handle_alert_triggered(self, portfolio_id: UUID, alert_id: UUID, data: Any):
        """Handle alert trigger and broadcast to subscribers."""
        message = {
            'type': 'alert_triggered',
            'portfolio_id': str(portfolio_id),
            'alert_id': str(alert_id),
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.send_portfolio_update(portfolio_id, message)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return len(self.connection_metadata)
    
    def get_portfolio_subscribers(self, portfolio_id: UUID) -> int:
        """Get number of subscribers for a portfolio."""
        return len(self.active_connections.get(portfolio_id, set()))
    
    def get_user_connections(self, user_id: UUID) -> int:
        """Get number of connections for a user."""
        return len([
            ws for ws, metadata in self.connection_metadata.items()
            if metadata['user_id'] == user_id
        ])


# Global WebSocket manager instance
portfolio_ws_manager = PortfolioWebSocketManager()


class PortfolioWebSocketService:
    """Service for handling portfolio WebSocket operations."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
        self.portfolio_service = PortfolioService(db)
    
    async def handle_websocket_connection(
        self, 
        websocket: WebSocket, 
        user_id: UUID, 
        portfolio_ids: List[UUID]
    ):
        """Handle WebSocket connection for portfolio updates."""
        await portfolio_ws_manager.connect(websocket, user_id, portfolio_ids)
        
        try:
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await self._handle_client_message(websocket, user_id, message)
                
        except WebSocketDisconnect:
            portfolio_ws_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            portfolio_ws_manager.disconnect(websocket)
    
    async def _handle_client_message(self, websocket: WebSocket, user_id: UUID, message: Dict[str, Any]):
        """Handle message from WebSocket client."""
        message_type = message.get('type')
        
        if message_type == 'ping':
            # Update last ping time
            if websocket in portfolio_ws_manager.connection_metadata:
                portfolio_ws_manager.connection_metadata[websocket]['last_ping'] = datetime.utcnow()
            
            # Send pong response
            await portfolio_ws_manager.send_personal_message({
                'type': 'pong',
                'timestamp': datetime.utcnow().isoformat()
            }, websocket)
        
        elif message_type == 'subscribe':
            # Subscribe to additional portfolios
            portfolio_ids = message.get('portfolio_ids', [])
            await self._subscribe_to_portfolios(websocket, user_id, portfolio_ids)
        
        elif message_type == 'unsubscribe':
            # Unsubscribe from portfolios
            portfolio_ids = message.get('portfolio_ids', [])
            await self._unsubscribe_from_portfolios(websocket, portfolio_ids)
        
        elif message_type == 'refresh_portfolio':
            # Refresh specific portfolio
            portfolio_id = message.get('portfolio_id')
            if portfolio_id:
                await self._refresh_portfolio(websocket, user_id, UUID(portfolio_id))
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def _subscribe_to_portfolios(self, websocket: WebSocket, user_id: UUID, portfolio_ids: List[str]):
        """Subscribe WebSocket to additional portfolios."""
        try:
            # Verify user owns these portfolios
            valid_portfolio_ids = []
            for portfolio_id_str in portfolio_ids:
                try:
                    portfolio_id = UUID(portfolio_id_str)
                    portfolio = await self.portfolio_service.get_portfolio(portfolio_id, user_id)
                    valid_portfolio_ids.append(portfolio_id)
                except Exception:
                    continue
            
            # Update connection metadata
            if websocket in portfolio_ws_manager.connection_metadata:
                current_portfolios = portfolio_ws_manager.connection_metadata[websocket]['portfolio_ids']
                new_portfolios = list(set(current_portfolios + valid_portfolio_ids))
                portfolio_ws_manager.connection_metadata[websocket]['portfolio_ids'] = new_portfolios
                
                # Add to active connections
                for portfolio_id in valid_portfolio_ids:
                    if portfolio_id not in portfolio_ws_manager.active_connections:
                        portfolio_ws_manager.active_connections[portfolio_id] = set()
                    portfolio_ws_manager.active_connections[portfolio_id].add(websocket)
            
            await portfolio_ws_manager.send_personal_message({
                'type': 'subscription_confirmed',
                'portfolio_ids': [str(pid) for pid in valid_portfolio_ids],
                'timestamp': datetime.utcnow().isoformat()
            }, websocket)
            
        except Exception as e:
            logger.error(f"Failed to subscribe to portfolios: {e}")
            await portfolio_ws_manager.send_personal_message({
                'type': 'error',
                'message': 'Failed to subscribe to portfolios',
                'timestamp': datetime.utcnow().isoformat()
            }, websocket)
    
    async def _unsubscribe_from_portfolios(self, websocket: WebSocket, portfolio_ids: List[str]):
        """Unsubscribe WebSocket from portfolios."""
        try:
            # Update connection metadata
            if websocket in portfolio_ws_manager.connection_metadata:
                current_portfolios = portfolio_ws_manager.connection_metadata[websocket]['portfolio_ids']
                portfolio_ids_to_remove = [UUID(pid) for pid in portfolio_ids if UUID(pid) in current_portfolios]
                
                # Remove from active connections
                for portfolio_id in portfolio_ids_to_remove:
                    if portfolio_id in portfolio_ws_manager.active_connections:
                        portfolio_ws_manager.active_connections[portfolio_id].discard(websocket)
                        if not portfolio_ws_manager.active_connections[portfolio_id]:
                            del portfolio_ws_manager.active_connections[portfolio_id]
                
                # Update metadata
                new_portfolios = [pid for pid in current_portfolios if pid not in portfolio_ids_to_remove]
                portfolio_ws_manager.connection_metadata[websocket]['portfolio_ids'] = new_portfolios
            
            await portfolio_ws_manager.send_personal_message({
                'type': 'unsubscription_confirmed',
                'portfolio_ids': portfolio_ids,
                'timestamp': datetime.utcnow().isoformat()
            }, websocket)
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from portfolios: {e}")
    
    async def _refresh_portfolio(self, websocket: WebSocket, user_id: UUID, portfolio_id: UUID):
        """Refresh portfolio data and send update."""
        try:
            # Get updated portfolio data
            portfolio = await self.portfolio_service.get_portfolio(portfolio_id, user_id)
            analytics = await self.portfolio_service.get_portfolio_analytics(portfolio_id, user_id)
            
            # Send refresh data
            await portfolio_ws_manager.send_personal_message({
                'type': 'portfolio_refresh',
                'portfolio_id': str(portfolio_id),
                'data': {
                    'portfolio': portfolio.__dict__,
                    'analytics': analytics
                },
                'timestamp': datetime.utcnow().isoformat()
            }, websocket)
            
        except Exception as e:
            logger.error(f"Failed to refresh portfolio: {e}")
            await portfolio_ws_manager.send_personal_message({
                'type': 'error',
                'message': 'Failed to refresh portfolio',
                'timestamp': datetime.utcnow().isoformat()
            }, websocket)
    
    async def notify_portfolio_update(self, portfolio_id: UUID, update_type: str, data: Any):
        """Notify all subscribers of portfolio update."""
        await portfolio_ws_manager.handle_portfolio_update(portfolio_id, update_type, data)
    
    async def notify_holding_update(self, portfolio_id: UUID, holding_id: UUID, data: Any):
        """Notify all subscribers of holding update."""
        await portfolio_ws_manager.handle_holding_update(portfolio_id, holding_id, data)
    
    async def notify_performance_update(self, portfolio_id: UUID, data: Any):
        """Notify all subscribers of performance update."""
        await portfolio_ws_manager.handle_performance_update(portfolio_id, data)
    
    async def notify_risk_update(self, portfolio_id: UUID, data: Any):
        """Notify all subscribers of risk update."""
        await portfolio_ws_manager.handle_risk_update(portfolio_id, data)
    
    async def notify_alert_triggered(self, portfolio_id: UUID, alert_id: UUID, data: Any):
        """Notify all subscribers of alert trigger."""
        await portfolio_ws_manager.handle_alert_triggered(portfolio_id, alert_id, data)
