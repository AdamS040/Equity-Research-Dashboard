"""
User management endpoints.

Handles user profile management and user-related operations.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserResponse, UserUpdate, UserProfile, 
    PasswordChange, UserSessionResponse, 
    UserPreferenceUpdate, UserPreferenceResponse,
    UserActivityResponse, MessageResponse
)
from app.auth.dependencies import get_current_user, get_current_superuser
from app.services.user_service import UserService
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserProfile: User profile data
    """
    return UserProfile.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile.
    
    Args:
        user_data: User update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserResponse: Updated user data
        
    Raises:
        HTTPException: If update fails
    """
    user_service = UserService(db)
    
    # Check username uniqueness if provided
    if user_data.username and user_data.username != current_user.username:
        existing_user = await user_service.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    updated_user = await user_service.update_user(str(current_user.id), user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    logger.info(f"Profile updated for user {current_user.id}")
    return UserResponse.from_orm(updated_user)


@router.post("/me/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password.
    
    Args:
        password_data: Password change data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Change confirmation
        
    Raises:
        HTTPException: If password change fails
    """
    user_service = UserService(db)
    
    # Verify current password
    if not await user_service.authenticate_user(current_user.email, password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    success = await user_service.update_password(str(current_user.id), password_data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update password"
        )
    
    # Revoke all sessions except current one
    await user_service.revoke_all_sessions(str(current_user.id))
    
    logger.info(f"Password changed for user {current_user.id}")
    return MessageResponse(message="Password changed successfully")


@router.get("/me/sessions", response_model=List[UserSessionResponse])
async def get_my_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's active sessions.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[UserSessionResponse]: List of user sessions
    """
    user_service = UserService(db)
    sessions = await user_service.get_user_sessions(str(current_user.id))
    
    return [UserSessionResponse.from_orm(session) for session in sessions]


@router.delete("/me/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke a specific session.
    
    Args:
        session_id: Session ID to revoke
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Revocation confirmation
        
    Raises:
        HTTPException: If revocation fails
    """
    user_service = UserService(db)
    
    success = await user_service.revoke_session(str(current_user.id), str(session_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to revoke session"
        )
    
    logger.info(f"Session {session_id} revoked for user {current_user.id}")
    return MessageResponse(message="Session revoked successfully")


@router.delete("/me/sessions", response_model=MessageResponse)
async def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke all sessions for current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Revocation confirmation
        
    Raises:
        HTTPException: If revocation fails
    """
    user_service = UserService(db)
    
    success = await user_service.revoke_all_sessions(str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to revoke sessions"
        )
    
    logger.info(f"All sessions revoked for user {current_user.id}")
    return MessageResponse(message="All sessions revoked successfully")


@router.delete("/me", response_model=MessageResponse)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete current user's account.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Deletion confirmation
        
    Raises:
        HTTPException: If deletion fails
    """
    user_service = UserService(db)
    
    success = await user_service.delete_user(str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete account"
        )
    
    logger.info(f"Account deleted for user {current_user.id}")
    return MessageResponse(message="Account deleted successfully")


# Admin endpoints
@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users (admin only).
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated superuser
        db: Database session
        
    Returns:
        List[UserResponse]: List of users
    """
    # This would be implemented with proper pagination
    # For now, return empty list
    return []


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID (admin only).
    
    Args:
        user_id: User ID
        current_user: Current authenticated superuser
        db: Database session
        
    Returns:
        UserResponse: User data
        
    Raises:
        HTTPException: If user not found
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(str(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user by ID (admin only).
    
    Args:
        user_id: User ID
        user_data: User update data
        current_user: Current authenticated superuser
        db: Database session
        
    Returns:
        UserResponse: Updated user data
        
    Raises:
        HTTPException: If update fails
    """
    user_service = UserService(db)
    
    # Check if user exists
    user = await user_service.get_by_id(str(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check username uniqueness if provided
    if user_data.username and user_data.username != user.username:
        existing_user = await user_service.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    updated_user = await user_service.update_user(str(user_id), user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )
    
    logger.info(f"User {user_id} updated by admin {current_user.id}")
    return UserResponse.from_orm(updated_user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user by ID (admin only).
    
    Args:
        user_id: User ID
        current_user: Current authenticated superuser
        db: Database session
        
    Returns:
        MessageResponse: Deletion confirmation
        
    Raises:
        HTTPException: If deletion fails
    """
    user_service = UserService(db)
    
    # Check if user exists
    user = await user_service.get_by_id(str(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-deletion
    if str(user_id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = await user_service.delete_user(str(user_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete user"
        )
    
    logger.info(f"User {user_id} deleted by admin {current_user.id}")
    return MessageResponse(message="User deleted successfully")
