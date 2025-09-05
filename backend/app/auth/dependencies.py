"""
Authentication dependencies for FastAPI.

Provides dependency injection for authentication, authorization, and user context.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import TokenData
from app.auth.security import verify_token
from app.services.user_service import UserService

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token
    token_data = verify_token(credentials.credentials, "access")
    if token_data is None:
        raise credentials_exception
    
    # Get user ID from token
    user_id: str = token_data.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current superuser.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def require_role(required_role: str):
    """
    Create a dependency that requires a specific role.
    
    Args:
        required_role: Required role name
        
    Returns:
        function: Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    
    return role_checker


def require_any_role(*required_roles: str):
    """
    Create a dependency that requires any of the specified roles.
    
    Args:
        *required_roles: Required role names
        
    Returns:
        function: Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if (current_user.role not in required_roles and 
            not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {', '.join(required_roles)}"
            )
        return current_user
    
    return role_checker


def require_permission(permission: str):
    """
    Create a dependency that requires a specific permission.
    
    Args:
        permission: Required permission name
        
    Returns:
        function: Dependency function
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        # This would check user permissions - simplified for now
        # In a real implementation, you'd check against user permissions
        if not current_user.is_superuser:
            # For now, just check if user has basic permissions
            # You would implement proper permission checking here
            pass
        return current_user
    
    return permission_checker


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    
    Args:
        credentials: HTTP Bearer token credentials (optional)
        db: Database session
        
    Returns:
        User: Current authenticated user or None
    """
    if not credentials:
        return None
    
    try:
        # Verify token
        token_data = verify_token(credentials.credentials, "access")
        if token_data is None:
            return None
        
        # Get user ID from token
        user_id: str = token_data.get("sub")
        if user_id is None:
            return None
        
        # Get user from database
        user_service = UserService(db)
        user = await user_service.get_by_id(user_id)
        if user is None or not user.is_active:
            return None
        
        return user
        
    except Exception:
        return None


class RoleChecker:
    """Role-based access control checker."""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if (current_user.role not in self.allowed_roles and 
            not current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role '{current_user.role}'"
            )
        return current_user


class PermissionChecker:
    """Permission-based access control checker."""
    
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        # This would check user permissions - simplified for now
        # In a real implementation, you'd check against user permissions
        if not current_user.is_superuser:
            # For now, just check if user has basic permissions
            # You would implement proper permission checking here
            pass
        return current_user
