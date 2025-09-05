"""
WebSocket service for real-time market data streaming.

Handles WebSocket connections, subscriptions, and real-time data broadcasting.
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.market_data import WebSocketMessage, WebSocketSubscription, WebSocketResponse
from app.services.market_data_service import market_data_service
from app.utils.logging import get_logger
from app.utils.redis_client import redis_manager

logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""
    
    def __init__(self):
        # Active connections by user ID
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Subscriptions by connection
        self.connection_subscriptions: Dict[WebSocket, Set[str]] = {}
        # Symbol subscriptions
        self.symbol_subscriptions: Dict[str, Set[WebSocket]] = {}
        # Channel subscriptions
        self.channel_subscriptions: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a WebSocket connection."""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        self.connection_subscriptions[websocket] = set()
        
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove from subscriptions
        if websocket in self.connection_subscriptions:
            subscriptions = self.connection_subscriptions[websocket]
            
            # Remove from symbol subscriptions
            for symbol in subscriptions:
                if symbol in self.symbol_subscriptions:
                    self.symbol_subscriptions[symbol].discard(websocket)
                    if not self.symbol_subscriptions[symbol]:
                        del self.symbol_subscriptions[symbol]
            
            # Remove from channel subscriptions
            for channel in subscriptions:
                if channel in self.channel_subscriptions:
                    self.channel_subscriptions[channel].discard(websocket)
                    if not self.channel_subscriptions[channel]:
                        del self.channel_subscriptions[channel]
            
            del self.connection_subscriptions[websocket]
        
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def subscribe(self, websocket: WebSocket, subscription: WebSocketSubscription):
        """Subscribe to market data channels."""
        if websocket not in self.connection_subscriptions:
            return False
        
        subscriptions = self.connection_subscriptions[websocket]
        
        if subscription.type == "stock_quotes" and subscription.symbols:
            for symbol in subscription.symbols:
                subscriptions.add(symbol)
                
                if symbol not in self.symbol_subscriptions:
                    self.symbol_subscriptions[symbol] = set()
                self.symbol_subscriptions[symbol].add(websocket)
        
        elif subscription.type in ["market_data", "sector_data", "sentiment_data"]:
            channel = subscription.type
            subscriptions.add(channel)
            
            if channel not in self.channel_subscriptions:
                self.channel_subscriptions[channel] = set()
            self.channel_subscriptions[channel].add(websocket)
        
        logger.info(f"Subscribed to {subscription.type}: {subscription.symbols or subscription.channels}")
        return True
    
    async def unsubscribe(self, websocket: WebSocket, subscription: WebSocketSubscription):
        """Unsubscribe from market data channels."""
        if websocket not in self.connection_subscriptions:
            return False
        
        subscriptions = self.connection_subscriptions[websocket]
        
        if subscription.type == "stock_quotes" and subscription.symbols:
            for symbol in subscription.symbols:
                subscriptions.discard(symbol)
                
                if symbol in self.symbol_subscriptions:
                    self.symbol_subscriptions[symbol].discard(websocket)
                    if not self.symbol_subscriptions[symbol]:
                        del self.symbol_subscriptions[symbol]
        
        elif subscription.type in ["market_data", "sector_data", "sentiment_data"]:
            channel = subscription.type
            subscriptions.discard(channel)
            
            if channel in self.channel_subscriptions:
                self.channel_subscriptions[channel].discard(websocket)
                if not self.channel_subscriptions[channel]:
                    del self.channel_subscriptions[channel]
        
        logger.info(f"Unsubscribed from {subscription.type}: {subscription.symbols or subscription.channels}")
        return True
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_symbol(self, symbol: str, message: str):
        """Broadcast a message to all connections subscribed to a symbol."""
        if symbol in self.symbol_subscriptions:
            connections = self.symbol_subscriptions[symbol].copy()
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to symbol {symbol}: {e}")
                    # Remove dead connections
                    self.symbol_subscriptions[symbol].discard(connection)
    
    async def broadcast_to_channel(self, channel: str, message: str):
        """Broadcast a message to all connections subscribed to a channel."""
        if channel in self.channel_subscriptions:
            connections = self.channel_subscriptions[channel].copy()
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to channel {channel}: {e}")
                    # Remove dead connections
                    self.channel_subscriptions[channel].discard(connection)
    
    async def broadcast_to_all(self, message: str):
        """Broadcast a message to all active connections."""
        for user_connections in self.active_connections.values():
            for connection in user_connections.copy():
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to all: {e}")


class WebSocketService:
    """WebSocket service for real-time market data."""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.is_running = False
        self.data_update_task = None
    
    async def start(self):
        """Start the WebSocket service."""
        if not self.is_running:
            self.is_running = True
            self.data_update_task = asyncio.create_task(self._data_update_loop())
            logger.info("WebSocket service started")
    
    async def stop(self):
        """Stop the WebSocket service."""
        if self.is_running:
            self.is_running = False
            if self.data_update_task:
                self.data_update_task.cancel()
                try:
                    await self.data_update_task
                except asyncio.CancelledError:
                    pass
            logger.info("WebSocket service stopped")
    
    async def handle_connection(self, websocket: WebSocket, user: User):
        """Handle a WebSocket connection."""
        user_id = str(user.id)
        
        try:
            await self.connection_manager.connect(websocket, user_id)
            
            # Send welcome message
            welcome_message = WebSocketMessage(
                type="market_update",
                data={
                    "message": "Connected to real-time market data",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            await self.connection_manager.send_personal_message(
                welcome_message.json(), websocket
            )
            
            # Handle messages from client
            while True:
                try:
                    data = await websocket.receive_text()
                    await self._handle_client_message(websocket, data)
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error handling client message: {e}")
                    error_message = WebSocketMessage(
                        type="error",
                        data={
                            "error": "Invalid message format",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    await self.connection_manager.send_personal_message(
                        error_message.json(), websocket
                    )
        
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            self.connection_manager.disconnect(websocket, user_id)
    
    async def _handle_client_message(self, websocket: WebSocket, data: str):
        """Handle incoming client messages."""
        try:
            message_data = json.loads(data)
            message_type = message_data.get("type")
            
            if message_type == "subscribe":
                subscription_data = message_data.get("data", {})
                subscription = WebSocketSubscription(**subscription_data)
                
                success = await self.connection_manager.subscribe(websocket, subscription)
                
                response = WebSocketResponse(
                    success=success,
                    message="Subscribed successfully" if success else "Subscription failed",
                    data={"subscription": subscription_data}
                )
                await self.connection_manager.send_personal_message(
                    response.json(), websocket
                )
            
            elif message_type == "unsubscribe":
                subscription_data = message_data.get("data", {})
                subscription = WebSocketSubscription(**subscription_data)
                
                success = await self.connection_manager.unsubscribe(websocket, subscription)
                
                response = WebSocketResponse(
                    success=success,
                    message="Unsubscribed successfully" if success else "Unsubscription failed",
                    data={"subscription": subscription_data}
                )
                await self.connection_manager.send_personal_message(
                    response.json(), websocket
                )
            
            elif message_type == "ping":
                pong_message = WebSocketMessage(
                    type="pong",
                    data={"timestamp": datetime.utcnow().isoformat()}
                )
                await self.connection_manager.send_personal_message(
                    pong_message.json(), websocket
                )
            
            else:
                error_message = WebSocketMessage(
                    type="error",
                    data={
                        "error": f"Unknown message type: {message_type}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                await self.connection_manager.send_personal_message(
                    error_message.json(), websocket
                )
        
        except json.JSONDecodeError:
            error_message = WebSocketMessage(
                type="error",
                data={
                    "error": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            await self.connection_manager.send_personal_message(
                error_message.json(), websocket
            )
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            error_message = WebSocketMessage(
                type="error",
                data={
                    "error": "Internal server error",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            await self.connection_manager.send_personal_message(
                error_message.json(), websocket
            )
    
    async def _data_update_loop(self):
        """Background task to update and broadcast market data."""
        while self.is_running:
            try:
                # Update market data every 30 seconds
                await asyncio.sleep(30)
                
                # Get market indices
                indices = await market_data_service.get_market_indices()
                if indices:
                    message = WebSocketMessage(
                        type="market_update",
                        data={
                            "indices": indices,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    await self.connection_manager.broadcast_to_channel(
                        "market_data", message.json()
                    )
                
                # Get market sentiment
                sentiment = await market_data_service.get_market_sentiment()
                if sentiment:
                    message = WebSocketMessage(
                        type="sentiment_update",
                        data={
                            "sentiment": sentiment,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    await self.connection_manager.broadcast_to_channel(
                        "sentiment_data", message.json()
                    )
                
                # Update subscribed stock quotes
                for symbol in self.connection_manager.symbol_subscriptions.keys():
                    quote = await market_data_service.get_stock_quote(symbol)
                    if quote:
                        message = WebSocketMessage(
                            type="quote_update",
                            data={
                                "symbol": symbol,
                                "quote": quote,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )
                        await self.connection_manager.broadcast_to_symbol(
                            symbol, message.json()
                        )
                
            except Exception as e:
                logger.error(f"Error in data update loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def broadcast_quote_update(self, symbol: str, quote_data: Dict[str, Any]):
        """Broadcast a quote update to subscribed connections."""
        message = WebSocketMessage(
            type="quote_update",
            data={
                "symbol": symbol,
                "quote": quote_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        await self.connection_manager.broadcast_to_symbol(symbol, message.json())
    
    async def broadcast_market_update(self, market_data: Dict[str, Any]):
        """Broadcast a market update to subscribed connections."""
        message = WebSocketMessage(
            type="market_update",
            data={
                "market": market_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        await self.connection_manager.broadcast_to_channel("market_data", message.json())
    
    async def broadcast_sector_update(self, sector_data: List[Dict[str, Any]]):
        """Broadcast a sector update to subscribed connections."""
        message = WebSocketMessage(
            type="sector_update",
            data={
                "sectors": sector_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        await self.connection_manager.broadcast_to_channel("sector_data", message.json())
    
    async def broadcast_sentiment_update(self, sentiment_data: Dict[str, Any]):
        """Broadcast a sentiment update to subscribed connections."""
        message = WebSocketMessage(
            type="sentiment_update",
            data={
                "sentiment": sentiment_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        await self.connection_manager.broadcast_to_channel("sentiment_data", message.json())
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics."""
        total_connections = sum(len(connections) for connections in self.connection_manager.active_connections.values())
        total_users = len(self.connection_manager.active_connections)
        total_symbol_subscriptions = len(self.connection_manager.symbol_subscriptions)
        total_channel_subscriptions = len(self.connection_manager.channel_subscriptions)
        
        return {
            "total_connections": total_connections,
            "total_users": total_users,
            "symbol_subscriptions": total_symbol_subscriptions,
            "channel_subscriptions": total_channel_subscriptions,
            "is_running": self.is_running
        }


# Global WebSocket service instance
websocket_service = WebSocketService()
