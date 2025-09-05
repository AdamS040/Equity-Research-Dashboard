"""
Authentication endpoints.

Handles user authentication, registration, and token management.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserLogin, UserRegister, Token, AuthResponse, 
    PasswordReset, PasswordResetConfirm, EmailVerification,
    MessageResponse, UserResponse
)
from app.auth.dependencies import get_current_user
from app.auth.security import (
    create_access_token, create_refresh_token, verify_token,
    generate_password_reset_token, verify_password_reset_token,
    generate_email_verification_token, verify_email_verification_token
)
from app.services.user_service import UserService
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/register", response_model=AuthResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        AuthResponse: User data and authentication tokens
        
    Raises:
        HTTPException: If registration fails
    """
    user_service = UserService(db)
    
    # Check if user already exists
    existing_user = await user_service.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check username if provided
    if user_data.username:
        existing_username = await user_service.get_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create user
    user = await user_service.create_user(user_data)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Generate email verification token
    verification_token = generate_email_verification_token(user.email)
    await user_service.update_email_verification_token(user.id, verification_token)
    
    logger.info("User registered successfully", user_id=str(user.id), email=user.email)
    
    return AuthResponse(
        user=UserResponse.from_orm(user),
        tokens=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=15 * 60  # 15 minutes
        ),
        message="Registration successful. Please verify your email."
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return tokens.
    
    Args:
        user_credentials: User login credentials
        db: Database session
        
    Returns:
        AuthResponse: User data and authentication tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    user_service = UserService(db)
    
    # Authenticate user
    user = await user_service.authenticate_user(
        user_credentials.email, 
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update last login
    await user_service.update_last_login(user.id)
    
    # Create session record
    await user_service.create_session(
        user.id, 
        access_token, 
        refresh_token,
        user_agent="",  # Would be extracted from request headers
        ip_address=""   # Would be extracted from request
    )
    
    logger.info("User logged in successfully", user_id=str(user.id), email=user.email)
    
    return AuthResponse(
        user=UserResponse.from_orm(user),
        tokens=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=15 * 60  # 15 minutes
        ),
        message="Login successful"
    )


@router.post("/login/oauth2", response_model=AuthResponse)
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible login endpoint.
    
    Args:
        form_data: OAuth2 form data
        db: Database session
        
    Returns:
        AuthResponse: User data and authentication tokens
    """
    user_service = UserService(db)
    
    # Authenticate user
    user = await user_service.authenticate_user(
        form_data.username,  # OAuth2 uses username field for email
        form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update last login
    await user_service.update_last_login(user.id)
    
    logger.info("User logged in via OAuth2", user_id=str(user.id), email=user.email)
    
    return AuthResponse(
        user=UserResponse.from_orm(user),
        tokens=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=15 * 60  # 15 minutes
        ),
        message="Login successful"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_data: Refresh token data
        db: Database session
        
    Returns:
        Token: New access and refresh tokens
        
    Raises:
        HTTPException: If refresh fails
    """
    refresh_token = refresh_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token required"
        )
    
    # Verify refresh token
    token_data = verify_token(refresh_token, "refresh")
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user
    user_service = UserService(db)
    user = await user_service.get_by_id(token_data["sub"])
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update session
    await user_service.update_session_tokens(
        user.id, 
        refresh_token, 
        access_token, 
        new_refresh_token
    )
    
    logger.info("Token refreshed successfully", user_id=str(user.id))
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=15 * 60  # 15 minutes
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user and invalidate session.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Logout confirmation
    """
    user_service = UserService(db)
    
    # Revoke all user sessions
    await user_service.revoke_all_sessions(current_user.id)
    
    logger.info("User logged out successfully", user_id=str(current_user.id))
    
    return MessageResponse(message="Logout successful")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    email_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset.
    
    Args:
        email_data: Email for password reset
        db: Database session
        
    Returns:
        MessageResponse: Reset request confirmation
    """
    user_service = UserService(db)
    
    # Check if user exists
    user = await user_service.get_by_email(email_data.email)
    if not user:
        # Don't reveal if email exists or not
        return MessageResponse(message="If the email exists, a reset link has been sent")
    
    # Generate reset token
    reset_token = generate_password_reset_token(user.email)
    await user_service.update_password_reset_token(user.id, reset_token)
    
    # TODO: Send email with reset link
    logger.info("Password reset requested", user_id=str(user.id), email=user.email)
    
    return MessageResponse(message="If the email exists, a reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using reset token.
    
    Args:
        reset_data: Password reset confirmation data
        db: Database session
        
    Returns:
        MessageResponse: Reset confirmation
        
    Raises:
        HTTPException: If reset fails
    """
    user_service = UserService(db)
    
    # Verify reset token
    email = verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    user = await user_service.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    # Update password
    await user_service.update_password(user.id, reset_data.new_password)
    
    # Clear reset token
    await user_service.clear_password_reset_token(user.id)
    
    # Revoke all sessions
    await user_service.revoke_all_sessions(user.id)
    
    logger.info("Password reset successfully", user_id=str(user.id), email=user.email)
    
    return MessageResponse(message="Password reset successful")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification_data: EmailVerification,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user email address.
    
    Args:
        verification_data: Email verification data
        db: Database session
        
    Returns:
        MessageResponse: Verification confirmation
        
    Raises:
        HTTPException: If verification fails
    """
    user_service = UserService(db)
    
    # Verify token
    email = verify_email_verification_token(verification_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Get user
    user = await user_service.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    # Mark email as verified
    await user_service.verify_email(user.id)
    
    logger.info("Email verified successfully", user_id=str(user.id), email=user.email)
    
    return MessageResponse(message="Email verified successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user data
    """
    return UserResponse.from_orm(current_user)
