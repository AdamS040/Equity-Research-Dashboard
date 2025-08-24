"""
Authentication and User Management System
Handles user registration, login, logout, and session management
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
import sqlite3
import json

from flask import Flask, request, session, redirect, url_for, flash, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user


class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, user_id: int, username: str, email: str, role: str = 'user'):
        self.id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.is_active = True
    
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False


class AuthManager:
    """Authentication manager for user operations"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.db_path = os.path.join(app.instance_path, 'users.db')
        self.login_manager = LoginManager()
        self.login_manager.init_app(app)
        self.login_manager.login_view = 'auth.login'
        self.login_manager.login_message = 'Please log in to access this page.'
        
        # Setup login manager
        @self.login_manager.user_loader
        def load_user(user_id):
            return self.get_user_by_id(int(user_id))
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the user database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    preferences TEXT DEFAULT '{}'
                )
            ''')
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create user portfolios table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    portfolio_name TEXT NOT NULL,
                    portfolio_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create user reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    report_name TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    report_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return salt, hash_obj.hex()
    
    def _verify_password(self, password: str, salt: str, password_hash: str) -> bool:
        """Verify password against stored hash"""
        _, computed_hash = self._hash_password(password, salt)
        return computed_hash == password_hash
    
    def register_user(self, username: str, email: str, password: str, role: str = 'user') -> Dict[str, Any]:
        """Register a new user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if username or email already exists
                cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
                if cursor.fetchone():
                    return {'success': False, 'error': 'Username or email already exists'}
                
                # Hash password
                salt, password_hash = self._hash_password(password)
                
                # Insert new user
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, salt, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, password_hash, salt, role))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'message': 'User registered successfully'
                }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email, password_hash, salt, role
                    FROM users WHERE username = ? AND is_active = 1
                ''', (username,))
                
                user_data = cursor.fetchone()
                if not user_data:
                    return None
                
                user_id, username, email, password_hash, salt, role = user_data
                
                # Verify password
                if not self._verify_password(password, salt, password_hash):
                    return None
                
                # Update last login
                cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
                conn.commit()
                
                return User(user_id, username, email, role)
        
        except Exception:
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email, role
                    FROM users WHERE id = ? AND is_active = 1
                ''', (user_id,))
                
                user_data = cursor.fetchone()
                if user_data:
                    user_id, username, email, role = user_data
                    return User(user_id, username, email, role)
                
                return None
        
        except Exception:
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email, role
                    FROM users WHERE username = ? AND is_active = 1
                ''', (username,))
                
                user_data = cursor.fetchone()
                if user_data:
                    user_id, username, email, role = user_data
                    return User(user_id, username, email, role)
                
                return None
        
        except Exception:
            return None
    
    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users SET preferences = ? WHERE id = ?
                ''', (json.dumps(preferences), user_id))
                
                conn.commit()
                return True
        
        except Exception:
            return False
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT preferences FROM users WHERE id = ?', (user_id,))
                result = cursor.fetchone()
                
                if result and result[0]:
                    return json.loads(result[0])
                
                return {}
        
        except Exception:
            return {}
    
    def save_user_portfolio(self, user_id: int, portfolio_name: str, portfolio_data: Dict[str, Any]) -> bool:
        """Save user portfolio"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_portfolios (user_id, portfolio_name, portfolio_data, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, portfolio_name, json.dumps(portfolio_data)))
                
                conn.commit()
                return True
        
        except Exception:
            return False
    
    def get_user_portfolios(self, user_id: int) -> list:
        """Get user portfolios"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT portfolio_name, portfolio_data, created_at, updated_at
                    FROM user_portfolios WHERE user_id = ?
                    ORDER BY updated_at DESC
                ''', (user_id,))
                
                portfolios = []
                for row in cursor.fetchall():
                    portfolio_name, portfolio_data, created_at, updated_at = row
                    portfolios.append({
                        'name': portfolio_name,
                        'data': json.loads(portfolio_data),
                        'created_at': created_at,
                        'updated_at': updated_at
                    })
                
                return portfolios
        
        except Exception:
            return []
    
    def save_user_report(self, user_id: int, report_name: str, report_type: str, report_data: Dict[str, Any]) -> bool:
        """Save user report"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO user_reports (user_id, report_name, report_type, report_data)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, report_name, report_type, json.dumps(report_data)))
                
                conn.commit()
                return True
        
        except Exception:
            return False
    
    def get_user_reports(self, user_id: int) -> list:
        """Get user reports"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT report_name, report_type, report_data, created_at
                    FROM user_reports WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                
                reports = []
                for row in cursor.fetchall():
                    report_name, report_type, report_data, created_at = row
                    reports.append({
                        'name': report_name,
                        'type': report_type,
                        'data': json.loads(report_data),
                        'created_at': created_at
                    })
                
                return reports
        
        except Exception:
            return []
    
    def delete_user_report(self, user_id: int, report_name: str) -> bool:
        """Delete user report"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM user_reports WHERE user_id = ? AND report_name = ?
                ''', (user_id, report_name))
                
                conn.commit()
                return True
        
        except Exception:
            return False


def require_role(role: str):
    """Decorator to require specific user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if current_user.role != role and current_user.role != 'admin':
                flash('Insufficient permissions', 'error')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_admin(f):
    """Decorator to require admin role"""
    return require_role('admin')(f)


# Flask routes for authentication
def init_auth_routes(app: Flask, auth_manager: AuthManager):
    """Initialize authentication routes"""
    
    @app.route('/auth/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = auth_manager.authenticate_user(username, password)
            if user:
                login_user(user)
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('main.dashboard')
                return redirect(next_page)
            else:
                flash('Invalid username or password', 'error')
        
        return app.send_static_file('login.html')
    
    @app.route('/auth/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('auth.login'))
    
    @app.route('/auth/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return app.send_static_file('register.html')
            
            result = auth_manager.register_user(username, email, password)
            if result['success']:
                flash('Registration successful. Please log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(result['error'], 'error')
        
        return app.send_static_file('register.html')
    
    @app.route('/auth/profile')
    @login_required
    def profile():
        preferences = auth_manager.get_user_preferences(current_user.id)
        portfolios = auth_manager.get_user_portfolios(current_user.id)
        reports = auth_manager.get_user_reports(current_user.id)
        
        return app.send_static_file('profile.html')
    
    @app.route('/auth/change_password', methods=['POST'])
    @login_required
    def change_password():
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('auth.profile'))
        
        # Verify current password
        user = auth_manager.authenticate_user(current_user.username, current_password)
        if not user:
            flash('Current password is incorrect', 'error')
            return redirect(url_for('auth.profile'))
        
        # Update password
        try:
            with sqlite3.connect(auth_manager.db_path) as conn:
                cursor = conn.cursor()
                salt, password_hash = auth_manager._hash_password(new_password)
                
                cursor.execute('''
                    UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
                ''', (password_hash, salt, current_user.id))
                
                conn.commit()
                flash('Password updated successfully', 'success')
        
        except Exception:
            flash('Error updating password', 'error')
        
        return redirect(url_for('auth.profile'))
