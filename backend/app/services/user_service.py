"""
User service for user management operations.

Handles user creation, authentication, and user-related business logic.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserSession
from app.schemas.auth import UserCreate, UserUpdate
from app.auth.security import get_password_hash, verify_password
from app.utils.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """Service class for user management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User: User object or None
        """
        try:
            result = await self.db.execute(
                select(User).where(User.id == uuid.UUID(user_id))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User: User object or None
        """
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User: User object or None
        """
        try:
            result = await self.db.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            User: Created user object
            
        Raises:
            ValueError: If user creation fails
        """
        try:
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user object
            user = User(
                email=user_data.email,
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone=user_data.phone,
                timezone=user_data.timezone,
                language=user_data.language,
                hashed_password=hashed_password,
                is_active=True,
                is_verified=False,
                is_superuser=False,
                role="user",
                permissions=[],
                preferences={}
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"User created successfully: {user.email}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating user: {e}")
            raise ValueError(f"Failed to create user: {e}")
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """
        Update user information.
        
        Args:
            user_id: User ID
            user_data: User update data
            
        Returns:
            User: Updated user object or None
        """
        try:
            # Get user
            user = await self.get_by_id(user_id)
            if not user:
                return None
            
            # Update fields
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"User updated successfully: {user.email}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    async def update_password(self, user_id: str, new_password: str) -> bool:
        """
        Update user password.
        
        Args:
            user_id: User ID
            new_password: New password
            
        Returns:
            bool: True if successful
        """
        try:
            hashed_password = get_password_hash(new_password)
            
            await self.db.execute(
                update(User)
                .where(User.id == uuid.UUID(user_id))
                .values(
                    hashed_password=hashed_password,
                    updated_at=datetime.utcnow()
                )
            )
            
            await self.db.commit()
            logger.info(f"Password updated for user {user_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating password for user {user_id}: {e}")
            return False
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User: Authenticated user or None
        """
        try:
            user = await self.get_by_email(email)
            if not user:
                return None
            
            if not verify_password(password, user.hashed_password):
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return None
    
    async def update_last_login(self, user_id: str) -> bool:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if successful
        """
        try:
            await self.db.execute(
                update(User)
                .where(User.id == uuid.UUID(user_id))
                .values(
                    last_login=datetime.utcnow(),
                    last_activity=datetime.utcnow()
                )
            )
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating last login for user {user_id}: {e}")
            return False
    
    async def update_last_activity(self, user_id: str) -> bool:
        """
        Update user's last activity timestamp.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if successful
        """
        try:
            await self.db.execute(
                update(User)
                .where(User.id == uuid.UUID(user_id))
                .values(last_activity=datetime.utcnow())
            )
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating last activity for user {user_id}: {e}")
            return False
    
    async def verify_email(self, user_id: str) -> bool:
        """
        Mark user's email as verified.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if successful
        """
        try:
            await self.db.execute(
                update(User)
                .where(User.id == uuid.UUID(user_id))
                .values(
                    is_verified=True,
                    email_verified_at=datetime.utcnow(),
                    email_verification_token=None,
                    updated_at=datetime.utcnow()
                )
            )
            
            await self.db.commit()
            logger.info(f"Email verified for user {user_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error verifying email for user {user_id}: {e}")
            return False
    
    async def update_email_verification_token(self, user_id: str, token: str) -> bool:
        """
        Update user's email verification token.
        
        Args:
            user_id: User ID
            token: Verification token
            
        Returns:
            bool: True if successful
        """
        try:
            await self.db.execute(
                update(User)
                .where(User.id == uuid.UUID(user_id))
                .values(email_verification_token=token)
            )
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating email verification token for user {user_id}: {e}")
            return False
    
    async def update_password_reset_token(self, user_id: str, token: str) -> bool:
        """
        Update user's password reset token.
        
        Args:
            user_id: User ID
            token: Reset token
            
        Returns:
            bool: True if successful
        """
        try:
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            await self.db.execute(
                update(User)
                .where(User.id == uuid.UUID(user_id))
                .values(
                    password_reset_token=token,
                    password_reset_expires=expires_at
                )
            )
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating password reset token for user {user_id}: {e}")
            return False
    
    async def clear_password_reset_token(self, user_id: str) -> bool:
        """
        Clear user's password reset token.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if successful
        """
        try:
            await self.db.execute(
                update(User)
                .where(User.id == uuid.UUID(user_id))
                .values(
                    password_reset_token=None,
                    password_reset_expires=None
                )
            )
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error clearing password reset token for user {user_id}: {e}")
            return False
    
    async def create_session(
        self, 
        user_id: str, 
        access_token: str, 
        refresh_token: str,
        user_agent: str = None,
        ip_address: str = None
    ) -> Optional[UserSession]:
        """
        Create a new user session.
        
        Args:
            user_id: User ID
            access_token: Access token
            refresh_token: Refresh token
            user_agent: User agent string
            ip_address: IP address
            
        Returns:
            UserSession: Created session or None
        """
        try:
            expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days
            
            session = UserSession(
                user_id=uuid.UUID(user_id),
                access_token=access_token,
                refresh_token=refresh_token,
                user_agent=user_agent,
                ip_address=ip_address,
                expires_at=expires_at,
                is_active=True
            )
            
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)
            
            logger.info(f"Session created for user {user_id}")
            return session
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating session for user {user_id}: {e}")
            return None
    
    async def update_session_tokens(
        self, 
        user_id: str, 
        old_refresh_token: str,
        new_access_token: str, 
        new_refresh_token: str
    ) -> bool:
        """
        Update session tokens.
        
        Args:
            user_id: User ID
            old_refresh_token: Old refresh token
            new_access_token: New access token
            new_refresh_token: New refresh token
            
        Returns:
            bool: True if successful
        """
        try:
            expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days
            
            await self.db.execute(
                update(UserSession)
                .where(
                    UserSession.user_id == uuid.UUID(user_id),
                    UserSession.refresh_token == old_refresh_token
                )
                .values(
                    access_token=new_access_token,
                    refresh_token=new_refresh_token,
                    expires_at=expires_at,
                    last_used=datetime.utcnow()
                )
            )
            
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating session tokens for user {user_id}: {e}")
            return False
    
    async def revoke_session(self, user_id: str, session_id: str) -> bool:
        """
        Revoke a specific session.
        
        Args:
            user_id: User ID
            session_id: Session ID
            
        Returns:
            bool: True if successful
        """
        try:
            await self.db.execute(
                update(UserSession)
                .where(
                    UserSession.id == uuid.UUID(session_id),
                    UserSession.user_id == uuid.UUID(user_id)
                )
                .values(
                    is_active=False,
                    revoked_at=datetime.utcnow()
                )
            )
            
            await self.db.commit()
            logger.info(f"Session {session_id} revoked for user {user_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error revoking session {session_id} for user {user_id}: {e}")
            return False
    
    async def revoke_all_sessions(self, user_id: str) -> bool:
        """
        Revoke all sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if successful
        """
        try:
            await self.db.execute(
                update(UserSession)
                .where(UserSession.user_id == uuid.UUID(user_id))
                .values(
                    is_active=False,
                    revoked_at=datetime.utcnow()
                )
            )
            
            await self.db.commit()
            logger.info(f"All sessions revoked for user {user_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error revoking all sessions for user {user_id}: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[UserSession]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List[UserSession]: List of user sessions
        """
        try:
            result = await self.db.execute(
                select(UserSession)
                .where(
                    UserSession.user_id == uuid.UUID(user_id),
                    UserSession.is_active == True
                )
                .order_by(UserSession.created_at.desc())
            )
            
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}")
            return []
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if successful
        """
        try:
            # Delete user (cascade will handle related records)
            await self.db.execute(
                delete(User).where(User.id == uuid.UUID(user_id))
            )
            
            await self.db.commit()
            logger.info(f"User {user_id} deleted successfully")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
