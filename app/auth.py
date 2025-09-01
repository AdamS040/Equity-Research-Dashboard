"""
Authentication and User Management System for Dash
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
import re

from flask import Flask, request, session, redirect, url_for, flash, current_app, render_template_string, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc


class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, user_id: int, username: str, email: str, role: str = 'user'):
        self.id = user_id
        self.username = username
        self.email = email
        self.role = role
        self._is_active = True
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_active(self):
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        self._is_active = value
    
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
        self.login_manager.login_view = 'login'
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
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        computed_hash = hash_obj.hex()
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
                return redirect(url_for('login'))
            
            if current_user.role != role and current_user.role != 'admin':
                flash('Insufficient permissions', 'error')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_admin(f):
    """Decorator to require admin role"""
    return require_role('admin')(f)


# Dash Authentication Components
def create_login_layout():
    """Create Dash login layout"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("🔐 Login", className="text-center mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.FormGroup([
                                dbc.Label("Username"),
                                dbc.Input(
                                    id="login-username",
                                    type="text",
                                    placeholder="Enter username",
                                    className="mb-3"
                                )
                            ]),
                            dbc.FormGroup([
                                dbc.Label("Password"),
                                dbc.Input(
                                    id="login-password",
                                    type="password",
                                    placeholder="Enter password",
                                    className="mb-3"
                                )
                            ]),
                            dbc.Button(
                                "Login",
                                id="login-button",
                                color="primary",
                                className="w-100 mb-3"
                            ),
                            html.Hr(),
                            html.P([
                                "Don't have an account? ",
                                dbc.Button("Register", id="register-link", color="link", className="p-0")
                            ], className="text-center mb-0")
                        ])
                    ])
                ], className="shadow")
            ], width=6, className="mx-auto")
        ], className="justify-content-center align-items-center", style={"minHeight": "80vh"})
    ], fluid=True)


def create_register_layout():
    """Create Dash register layout"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("📝 Register", className="text-center mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.FormGroup([
                                dbc.Label("Username"),
                                dbc.Input(
                                    id="register-username",
                                    type="text",
                                    placeholder="Enter username",
                                    className="mb-3"
                                )
                            ]),
                            dbc.FormGroup([
                                dbc.Label("Email"),
                                dbc.Input(
                                    id="register-email",
                                    type="email",
                                    placeholder="Enter email",
                                    className="mb-3"
                                )
                            ]),
                            dbc.FormGroup([
                                dbc.Label("Password"),
                                dbc.Input(
                                    id="register-password",
                                    type="password",
                                    placeholder="Enter password",
                                    className="mb-3"
                                )
                            ]),
                            dbc.FormGroup([
                                dbc.Label("Confirm Password"),
                                dbc.Input(
                                    id="register-confirm-password",
                                    type="password",
                                    placeholder="Confirm password",
                                    className="mb-3"
                                )
                            ]),
                            dbc.Button(
                                "Register",
                                id="register-button",
                                color="success",
                                className="w-100 mb-3"
                            ),
                            html.Hr(),
                            html.P([
                                "Already have an account? ",
                                dbc.Button("Login", id="login-link", color="link", className="p-0")
                            ], className="text-center mb-0")
                        ])
                    ])
                ], className="shadow")
            ], width=6, className="mx-auto")
        ], className="justify-content-center align-items-center", style={"minHeight": "80vh"})
    ], fluid=True)


def create_profile_layout():
    """Create Dash profile layout"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("👤 User Profile", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5("Account Information"),
                                html.P(f"Username: {current_user.username if current_user.is_authenticated else 'N/A'}"),
                                html.P(f"Email: {current_user.email if current_user.is_authenticated else 'N/A'}"),
                                html.P(f"Role: {current_user.role if current_user.is_authenticated else 'N/A'}"),
                            ], width=6),
                            dbc.Col([
                                html.H5("Quick Actions"),
                                dbc.Button("Change Password", id="change-password-btn", color="warning", className="mb-2 w-100"),
                                dbc.Button("View Portfolios", id="view-portfolios-btn", color="info", className="mb-2 w-100"),
                                dbc.Button("View Reports", id="view-reports-btn", color="secondary", className="mb-2 w-100"),
                            ], width=6)
                        ])
                    ])
                ])
            ])
        ])
    ], fluid=True)


# Flask routes for authentication (for direct Flask access)
def init_auth_routes(app: Flask, auth_manager: AuthManager):
    """Initialize authentication routes for Flask"""
    
    @app.route('/auth/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            # Validate input fields
            if not username:
                flash('Please enter your username.', 'error')
                return render_template('login.html')
            
            if not password:
                flash('Please enter your password.', 'error')
                return render_template('login.html')
            
            # Attempt authentication
            try:
                user = auth_manager.authenticate_user(username, password)
                if user:
                    login_user(user)
                    next_page = request.args.get('next')
                    if not next_page or not next_page.startswith('/'):
                        next_page = '/'
                    
                    flash(f'Welcome back, {user.username}!', 'success')
                    return redirect(next_page)
                else:
                    flash('Invalid username or password. Please check your credentials and try again.', 'error')
            except Exception as e:
                # Log the error for debugging but don't expose it to the user
                current_app.logger.error(f"Login error for user {username}: {str(e)}")
                flash('An error occurred during login. Please try again later.', 'error')
        
        return render_template('login.html')
    
    @app.route('/auth/logout')
    @login_required
    def logout():
        username = current_user.username
        logout_user()
        flash(f'You have been successfully logged out, {username}.', 'info')
        return redirect('/auth/login')
    
    @app.route('/auth/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            terms_accept = request.form.get('terms_accept')
            
            # Validate input fields
            errors = []
            
            if not username:
                errors.append('Username is required.')
            elif len(username) < 3 or len(username) > 30:
                errors.append('Username must be between 3 and 30 characters.')
            elif not re.match(r'^[a-zA-Z0-9_-]+$', username):
                errors.append('Username can only contain letters, numbers, hyphens, and underscores.')
            
            if not email:
                errors.append('Email address is required.')
            elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                errors.append('Please enter a valid email address.')
            
            if not password:
                errors.append('Password is required.')
            elif len(password) < 8:
                errors.append('Password must be at least 8 characters long.')
            elif not re.search(r'[A-Z]', password):
                errors.append('Password must contain at least one uppercase letter.')
            elif not re.search(r'[a-z]', password):
                errors.append('Password must contain at least one lowercase letter.')
            elif not re.search(r'\d', password):
                errors.append('Password must contain at least one number.')
            elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                errors.append('Password must contain at least one special character.')
            
            if password != confirm_password:
                errors.append('Passwords do not match.')
            
            if not terms_accept:
                errors.append('You must accept the terms and conditions to continue.')
            
            # If there are validation errors, show them all
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('register.html')
            
            # Attempt user registration
            try:
                result = auth_manager.register_user(username, email, password)
                if result['success']:
                    flash('Account created successfully! Please log in with your new credentials.', 'success')
                    return redirect('/auth/login')
                else:
                    # Handle specific registration errors
                    if 'already exists' in result['error'].lower():
                        if 'username' in result['error'].lower():
                            flash('This username is already taken. Please choose a different username.', 'error')
                        elif 'email' in result['error'].lower():
                            flash('An account with this email address already exists. Please use a different email or try logging in.', 'error')
                        else:
                            flash('This username or email is already registered. Please choose different credentials.', 'error')
                    else:
                        flash('Registration failed. Please try again later.', 'error')
                        
                    current_app.logger.error(f"Registration error for {username}: {result['error']}")
            except Exception as e:
                current_app.logger.error(f"Registration exception for {username}: {str(e)}")
                flash('An unexpected error occurred during registration. Please try again later.', 'error')
        
        return render_template('register.html')
    
    @app.route('/auth/profile')
    @login_required
    def profile():
        try:
            preferences = auth_manager.get_user_preferences(current_user.id)
            portfolios = auth_manager.get_user_portfolios(current_user.id)
            reports = auth_manager.get_user_reports(current_user.id)
        except Exception as e:
            current_app.logger.error(f"Error loading profile data: {e}")
            preferences = {}
            portfolios = []
            reports = []
        
        return render_template('profile.html', 
                            user=current_user, 
                            portfolios=portfolios, 
                            reports=reports)
    
    @app.route('/auth/change_password', methods=['POST'])
    @login_required
    def change_password():
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect('/auth/profile')
        
        # Verify current password
        user = auth_manager.authenticate_user(current_user.username, current_password)
        if not user:
            flash('Current password is incorrect', 'error')
            return redirect('/auth/profile')
        
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
        
        return redirect('/auth/profile')
