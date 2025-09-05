"""
Security utilities for authentication and authorization.

Handles password hashing, JWT token generation/validation, and security helpers.
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

from app.config import settings

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.bcrypt_rounds
)


def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
        
    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.refresh_token_expire_days
        )
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token to verify
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        
        # Check token type
        if payload.get("type") != token_type:
            return None
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        return payload
        
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def generate_password_reset_token(email: str) -> str:
    """
    Generate password reset token.
    
    Args:
        email: User email
        
    Returns:
        str: Password reset token
    """
    delta = timedelta(hours=1)  # Reset token expires in 1 hour
    now = datetime.utcnow()
    expires = now + delta
    
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "password_reset"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token and return email.
    
    Args:
        token: Password reset token
        
    Returns:
        str: User email if token is valid, None otherwise
    """
    try:
        decoded_token = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        
        if decoded_token.get("type") != "password_reset":
            return None
        
        return decoded_token.get("sub")
        
    except JWTError:
        return None


def generate_email_verification_token(email: str) -> str:
    """
    Generate email verification token.
    
    Args:
        email: User email
        
    Returns:
        str: Email verification token
    """
    delta = timedelta(days=1)  # Verification token expires in 1 day
    now = datetime.utcnow()
    expires = now + delta
    
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "email_verification"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    
    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[str]:
    """
    Verify email verification token and return email.
    
    Args:
        token: Email verification token
        
    Returns:
        str: User email if token is valid, None otherwise
    """
    try:
        decoded_token = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        
        if decoded_token.get("type") != "email_verification":
            return None
        
        return decoded_token.get("sub")
        
    except JWTError:
        return None


def generate_api_key() -> str:
    """
    Generate a secure API key.
    
    Returns:
        str: Random API key
    """
    return secrets.token_urlsafe(32)


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Args:
        length: Token length in bytes
        
    Returns:
        str: Random token
    """
    return secrets.token_urlsafe(length)


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        dict: Validation results with score and feedback
    """
    score = 0
    feedback = []
    
    # Length check
    if len(password) < settings.password_min_length:
        feedback.append(f"Password must be at least {settings.password_min_length} characters long")
    else:
        score += 1
    
    # Character variety checks
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if has_lower:
        score += 1
    else:
        feedback.append("Password should contain lowercase letters")
    
    if has_upper:
        score += 1
    else:
        feedback.append("Password should contain uppercase letters")
    
    if has_digit:
        score += 1
    else:
        feedback.append("Password should contain numbers")
    
    if has_special:
        score += 1
    else:
        feedback.append("Password should contain special characters")
    
    # Common password check (simplified)
    common_passwords = ["password", "123456", "qwerty", "abc123", "password123"]
    if password.lower() in common_passwords:
        score = 0
        feedback.append("Password is too common")
    
    # Determine strength level
    if score <= 2:
        strength = "weak"
    elif score <= 3:
        strength = "medium"
    else:
        strength = "strong"
    
    return {
        "score": score,
        "max_score": 5,
        "strength": strength,
        "is_valid": score >= 3 and len(password) >= settings.password_min_length,
        "feedback": feedback
    }
