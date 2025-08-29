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

from flask import Flask, request, session, redirect, url_for, flash, current_app, render_template_string
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
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = auth_manager.authenticate_user(username, password)
            if user:
                login_user(user)
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = '/'
                return redirect(next_page)
            else:
                flash('Invalid username or password', 'error')
        
        # Return login form HTML
        login_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - Equity Research Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h3 class="text-center">Login</h3>
                            </div>
                            <div class="card-body">
                                <form method="POST">
                                    <div class="mb-3">
                                        <label for="username" class="form-label">Username</label>
                                        <input type="text" class="form-control" id="username" name="username" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="password" class="form-label">Password</label>
                                        <input type="password" class="form-control" id="password" name="password" required>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100">Login</button>
                                </form>
                                <hr>
                                <p class="text-center">
                                    Don't have an account? <a href="/auth/register">Register</a>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
        return render_template_string(login_html)
    
    @app.route('/auth/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out', 'info')
        return redirect('/auth/login')
    
    @app.route('/auth/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect('/auth/register')
            
            result = auth_manager.register_user(username, email, password)
            if result['success']:
                flash('Registration successful. Please log in.', 'success')
                return redirect('/auth/login')
            else:
                flash(result['error'], 'error')
        
        # Return register form HTML
        register_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Register - Equity Research Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h3 class="text-center">Register</h3>
                            </div>
                            <div class="card-body">
                                <form method="POST">
                                    <div class="mb-3">
                                        <label for="username" class="form-label">Username</label>
                                        <input type="text" class="form-control" id="username" name="username" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="email" class="form-label">Email</label>
                                        <input type="email" class="form-control" id="email" name="email" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="password" class="form-label">Password</label>
                                        <input type="password" class="form-control" id="password" name="password" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="confirm_password" class="form-label">Confirm Password</label>
                                        <input type="password" class="form-control" id="confirm_password" name="confirm_password" required>
                                    </div>
                                    <button type="submit" class="btn btn-success w-100">Register</button>
                                </form>
                                <hr>
                                <p class="text-center">
                                    Already have an account? <a href="/auth/login">Login</a>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
        return render_template_string(register_html)
    
    @app.route('/auth/profile')
    @login_required
    def profile():
        try:
            preferences = auth_manager.get_user_preferences(current_user.id)
            portfolios = auth_manager.get_user_portfolios(current_user.id)
            reports = auth_manager.get_user_reports(current_user.id)
        except Exception as e:
            print(f"Error loading profile data: {e}")
            preferences = {}
            portfolios = []
            reports = []
        
        # Return profile HTML
        profile_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Profile - Equity Research Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                .portfolio-card {{
                    transition: all 0.3s ease;
                    cursor: pointer;
                    border: 2px solid #e9ecef;
                }}
                .portfolio-card:hover {{
                    border-color: #007bff;
                    box-shadow: 0 4px 8px rgba(0,123,255,0.2);
                    transform: translateY(-2px);
                }}
                .portfolio-card.active {{
                    border-color: #007bff;
                    background-color: #f8f9fa;
                }}
                .portfolio-details {{
                    display: none;
                    margin-top: 15px;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                }}
                .metric-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                }}
                .metric-value {{
                    font-size: 1.5rem;
                    font-weight: bold;
                }}
                .metric-label {{
                    font-size: 0.9rem;
                    opacity: 0.9;
                }}
                .allocation-chart {{
                    height: 300px;
                    margin: 15px 0;
                }}
                .performance-chart {{
                    height: 250px;
                    margin: 15px 0;
                }}
                .btn-view {{
                    background: linear-gradient(45deg, #007bff, #0056b3);
                    border: none;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    transition: all 0.3s ease;
                }}
                .btn-view:hover {{
                    background: linear-gradient(45deg, #0056b3, #004085);
                    transform: translateY(-1px);
                    color: white;
                }}
                .empty-state {{
                    text-align: center;
                    padding: 40px;
                    color: #6c757d;
                }}
                .empty-state i {{
                    font-size: 3rem;
                    margin-bottom: 15px;
                    opacity: 0.5;
                }}
            </style>
        </head>
        <body>
            <div class="container mt-4">
                <!-- Header -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h2><i class="fas fa-user-circle me-2"></i>User Profile</h2>
                                <p class="text-muted mb-0">Welcome back, {current_user.username}!</p>
                            </div>
                            <div>
                                <a href="/" class="btn btn-outline-primary me-2">
                                    <i class="fas fa-chart-line me-1"></i>Dashboard
                                </a>
                                <a href="/auth/logout" class="btn btn-outline-danger">
                                    <i class="fas fa-sign-out-alt me-1"></i>Logout
                                </a>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Account Information -->
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>Account Information</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <strong><i class="fas fa-user me-2"></i>Username:</strong>
                                    <span class="float-end">{current_user.username}</span>
                                </div>
                                <div class="mb-3">
                                    <strong><i class="fas fa-envelope me-2"></i>Email:</strong>
                                    <span class="float-end">{current_user.email}</span>
                                </div>
                                <div class="mb-0">
                                    <strong><i class="fas fa-shield-alt me-2"></i>Role:</strong>
                                    <span class="float-end badge bg-success">{current_user.role}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header bg-success text-white">
                                <h5 class="mb-0"><i class="fas fa-chart-pie me-2"></i>Portfolio Summary</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-4 text-center">
                                        <div class="metric-card">
                                            <div class="metric-value">{len(portfolios)}</div>
                                            <div class="metric-label">Saved Portfolios</div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 text-center">
                                        <div class="metric-card">
                                            <div class="metric-value">{len(reports)}</div>
                                            <div class="metric-label">Research Reports</div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 text-center">
                                        <div class="metric-card">
                                            <div class="metric-value">{sum(len(p.get('data', {}).get('symbols', [])) for p in portfolios)}</div>
                                            <div class="metric-label">Total Assets</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Portfolios Section -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header bg-info text-white">
                                <h5 class="mb-0"><i class="fas fa-briefcase me-2"></i>Saved Portfolios ({len(portfolios)})</h5>
                            </div>
                            <div class="card-body">
                                {f'''
                                <div class="row">
                                    {''.join([f'''
                                    <div class="col-md-6 mb-3">
                                        <div class="card portfolio-card" onclick="togglePortfolioDetails('portfolio-{i}')">
                                            <div class="card-body">
                                                                                                 <div class="d-flex justify-content-between align-items-start">
                                                     <div>
                                                         <h6 class="card-title mb-1">
                                                             <i class="fas fa-chart-line me-2"></i>{p["name"]}
                                                         </h6>
                                                         <p class="text-muted mb-2">
                                                             <i class="fas fa-calendar me-1"></i>{p["created_at"]}
                                                         </p>
                                                         <div class="mb-2">
                                                             <span class="badge bg-primary me-1">
                                                                 <i class="fas fa-tag me-1"></i>{p.get('data', {}).get('method', 'Unknown').replace('_', ' ').title()}
                                                             </span>
                                                             <span class="badge bg-secondary">
                                                                 <i class="fas fa-coins me-1"></i>{len(p.get('data', {}).get('symbols', []))} Assets
                                                             </span>
                                                         </div>
                                                     </div>
                                                     <button class="btn btn-view" type="button" data-portfolio-id="portfolio-{i}">
                                                         <i class="fas fa-eye me-1"></i>View
                                                     </button>
                                                 </div>
                                                
                                                <div id="portfolio-{i}" class="portfolio-details">
                                                    <div class="row">
                                                        <div class="col-md-6">
                                                            <h6><i class="fas fa-chart-pie me-2"></i>Asset Allocation</h6>
                                                            <div id="allocation-chart-{i}" class="allocation-chart"></div>
                                                        </div>
                                                        <div class="col-md-6">
                                                            <h6><i class="fas fa-chart-line me-2"></i>Portfolio Metrics</h6>
                                                            <div class="row">
                                                                <div class="col-6">
                                                                    <div class="metric-card">
                                                                        <div class="metric-value">{p.get('data', {}).get('portfolio_metrics', {}).get('annual_return', 0):.1%}</div>
                                                                        <div class="metric-label">Annual Return</div>
                                                                    </div>
                                                                </div>
                                                                <div class="col-6">
                                                                    <div class="metric-card">
                                                                        <div class="metric-value">{p.get('data', {}).get('portfolio_metrics', {}).get('sharpe_ratio', 0):.2f}</div>
                                                                        <div class="metric-label">Sharpe Ratio</div>
                                                                    </div>
                                                                </div>
                                                                <div class="col-6">
                                                                    <div class="metric-card">
                                                                        <div class="metric-value">{p.get('data', {}).get('portfolio_metrics', {}).get('annual_volatility', 0):.1%}</div>
                                                                        <div class="metric-label">Volatility</div>
                                                                    </div>
                                                                </div>
                                                                <div class="col-6">
                                                                    <div class="metric-card">
                                                                        <div class="metric-value">{p.get('data', {}).get('portfolio_metrics', {}).get('max_drawdown', 0):.1%}</div>
                                                                        <div class="metric-label">Max Drawdown</div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    
                                                    <div class="mt-3">
                                                        <h6><i class="fas fa-list me-2"></i>Portfolio Holdings</h6>
                                                        <div class="table-responsive">
                                                            <table class="table table-sm">
                                                                <thead>
                                                                    <tr>
                                                                        <th>Symbol</th>
                                                                        <th>Weight</th>
                                                                        <th>Expected Return</th>
                                                                        <th>Volatility</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody>
                                                                    {''.join([f'''
                                                                    <tr>
                                                                        <td><strong>{symbol}</strong></td>
                                                                        <td>{p.get('data', {}).get('optimal_weights', {}).get(symbol, 0):.1%}</td>
                                                                        <td>{p.get('data', {}).get('stock_metrics', {}).get(symbol, {}).get('expected_return', 0):.1%}</td>
                                                                        <td>{p.get('data', {}).get('stock_metrics', {}).get(symbol, {}).get('volatility', 0):.1%}</td>
                                                                    </tr>
                                                                    ''' for symbol in p.get('data', {}).get('symbols', [])])}
                                                                </tbody>
                                                            </table>
                                                        </div>
                                                    </div>
                                                    
                                                    <div class="mt-3 text-center">
                                                        <button class="btn btn-outline-primary me-2" onclick="exportPortfolio({i})">
                                                            <i class="fas fa-download me-1"></i>Export JSON
                                                        </button>
                                                        <button class="btn btn-outline-success" onclick="exportPortfolioCSV({i})">
                                                            <i class="fas fa-file-csv me-1"></i>Export CSV
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    ''' for i, p in enumerate(portfolios)])}
                                </div>
                                ''' if portfolios else '''
                                <div class="empty-state">
                                    <i class="fas fa-briefcase"></i>
                                    <h5>No Portfolios Yet</h5>
                                    <p>You haven't saved any portfolios yet. Create and optimize portfolios in the Portfolio section to see them here.</p>
                                    <a href="/" class="btn btn-primary">
                                        <i class="fas fa-plus me-1"></i>Create Portfolio
                                    </a>
                                </div>
                                '''}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Reports Section -->
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header bg-warning text-dark">
                                <h5 class="mb-0"><i class="fas fa-file-alt me-2"></i>Research Reports ({len(reports)})</h5>
                            </div>
                            <div class="card-body">
                                {f'''
                                <div class="row">
                                    {''.join([f'''
                                    <div class="col-md-6 mb-3">
                                        <div class="card">
                                            <div class="card-body">
                                                <h6 class="card-title">
                                                    <i class="fas fa-file-alt me-2"></i>{r["name"]}
                                                </h6>
                                                <p class="text-muted mb-2">
                                                    <i class="fas fa-calendar me-1"></i>{r["created_at"]}
                                                </p>
                                                <span class="badge bg-warning text-dark">
                                                    <i class="fas fa-tag me-1"></i>{r["type"]}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    ''' for r in reports])}
                                </div>
                                ''' if reports else '''
                                <div class="empty-state">
                                    <i class="fas fa-file-alt"></i>
                                    <h5>No Reports Yet</h5>
                                    <p>You haven't generated any research reports yet. Use the Reports section to create comprehensive stock analysis reports.</p>
                                    <a href="/" class="btn btn-primary">
                                        <i class="fas fa-plus me-1"></i>Generate Report
                                    </a>
                                </div>
                                '''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

                         <script>
                 // Portfolio Management System
                 class PortfolioViewer {{
                     constructor() {{
                         this.initializeEventListeners();
                         this.portfolioData = {json.dumps([p.get('data', {}) for p in portfolios])};
                         this.portfolioNames = {json.dumps([p.get('name', '') for p in portfolios])};
                         console.log('PortfolioViewer initialized with', this.portfolioData.length, 'portfolios');
                     }}
                     
                     initializeEventListeners() {{
                         // Add event listeners for View buttons
                         document.addEventListener('DOMContentLoaded', () => {{
                             console.log('DOM loaded, setting up event listeners');
                             
                             // View button event listeners
                             document.querySelectorAll('.btn-view').forEach(button => {{
                                 button.addEventListener('click', (e) => {{
                                     e.preventDefault();
                                     e.stopPropagation();
                                     const portfolioId = button.getAttribute('data-portfolio-id');
                                     console.log('View button clicked for:', portfolioId);
                                     this.togglePortfolioDetails(portfolioId);
                                 }});
                             }});
                             
                             // Card click event listeners
                             document.querySelectorAll('.portfolio-card').forEach(card => {{
                                 card.addEventListener('click', (e) => {{
                                     if (!e.target.closest('.btn-view')) {{
                                         const portfolioId = card.querySelector('.portfolio-details')?.id;
                                         if (portfolioId) {{
                                             console.log('Card clicked for:', portfolioId);
                                             this.togglePortfolioDetails(portfolioId);
                                         }}
                                     }}
                                 }});
                             }});
                             
                             console.log('Event listeners initialized');
                         }});
                     }}
                     
                     togglePortfolioDetails(portfolioId) {{
                         console.log('Toggle called for:', portfolioId);
                         const details = document.getElementById(portfolioId);
                         const card = details?.closest('.portfolio-card');
                         
                         if (!details) {{
                             console.error('Portfolio details element not found:', portfolioId);
                             return;
                         }}
                         
                         const isCurrentlyHidden = details.style.display === 'none' || details.style.display === '';
                         
                         if (isCurrentlyHidden) {{
                             console.log('Opening portfolio details');
                             // Close all other portfolio details
                             document.querySelectorAll('.portfolio-details').forEach(el => {{
                                 el.style.display = 'none';
                             }});
                             document.querySelectorAll('.portfolio-card').forEach(el => {{
                                 el.classList.remove('active');
                             }});
                             
                             // Open this portfolio
                             details.style.display = 'block';
                             if (card) card.classList.add('active');
                             
                             // Create allocation chart
                             this.createAllocationChart(portfolioId);
                             
                             // Smooth scroll to the details
                             details.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                         }} else {{
                             console.log('Closing portfolio details');
                             details.style.display = 'none';
                             if (card) card.classList.remove('active');
                         }}
                     }}
                     
                     createAllocationChart(portfolioId) {{
                         try {{
                             const portfolioIndex = portfolioId.split('-')[1];
                             const portfolioData = this.portfolioData[portfolioIndex];
                             
                             if (!portfolioData || !portfolioData.optimal_weights) {{
                                 console.warn('No portfolio data or weights found for index:', portfolioIndex);
                                 return;
                             }}
                             
                             const symbols = Object.keys(portfolioData.optimal_weights);
                             const weights = Object.values(portfolioData.optimal_weights);
                             
                             if (symbols.length === 0) {{
                                 console.warn('No symbols found in portfolio data');
                                 return;
                             }}
                             
                             const data = [{{
                                 values: weights,
                                 labels: symbols,
                                 type: 'pie',
                                 hole: 0.4,
                                 marker: {{
                                     colors: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
                                 }},
                                 textinfo: 'label+percent',
                                 textposition: 'outside'
                             }}];
                             
                             const layout = {{
                                 title: {{
                                     text: 'Asset Allocation',
                                     font: {{ size: 16, color: '#333' }}
                                 }},
                                 height: 300,
                                 margin: {{ t: 40, b: 30, l: 30, r: 30 }},
                                 showlegend: true,
                                 legend: {{ 
                                     orientation: 'h', 
                                     y: -0.1,
                                     font: {{ size: 12 }}
                                 }},
                                 paper_bgcolor: 'rgba(0,0,0,0)',
                                 plot_bgcolor: 'rgba(0,0,0,0)'
                             }};
                             
                             const config = {{
                                 displayModeBar: false,
                                 responsive: true
                             }};
                             
                             Plotly.newPlot(`allocation-chart-${{portfolioIndex}}`, data, layout, config);
                             console.log('Allocation chart created for portfolio:', portfolioIndex);
                         }} catch (error) {{
                             console.error('Error creating allocation chart:', error);
                         }}
                     }}
                     
                     exportPortfolio(index) {{
                         try {{
                             const portfolioData = this.portfolioData[index];
                             const portfolioName = this.portfolioNames[index];
                             
                             if (!portfolioData || !portfolioName) {{
                                 console.error('Invalid portfolio data for export');
                                 return;
                             }}
                             
                             const exportData = {{
                                 portfolio_info: {{
                                     name: portfolioName,
                                     symbols: portfolioData.symbols || [],
                                     optimization_method: portfolioData.method || 'Unknown',
                                     export_date: new Date().toISOString(),
                                     version: '1.0'
                                 }},
                                 optimization_results: portfolioData
                             }};
                             
                             const dataStr = JSON.stringify(exportData, null, 2);
                             const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
                             const url = URL.createObjectURL(dataBlob);
                             const link = document.createElement('a');
                             link.href = url;
                             link.download = `${{portfolioName.replace(/\\s+/g, '_')}}_export.json`;
                             document.body.appendChild(link);
                             link.click();
                             document.body.removeChild(link);
                             URL.revokeObjectURL(url);
                             
                             console.log('Portfolio exported successfully:', portfolioName);
                         }} catch (error) {{
                             console.error('Error exporting portfolio:', error);
                         }}
                     }}
                     
                     exportPortfolioCSV(index) {{
                         try {{
                             const portfolioData = this.portfolioData[index];
                             const portfolioName = this.portfolioNames[index];
                             
                             if (!portfolioData || !portfolioName) {{
                                 console.error('Invalid portfolio data for CSV export');
                                 return;
                             }}
                             
                             let csvContent = 'Symbol,Weight,Expected Return,Volatility\\n';
                             
                             if (portfolioData.optimal_weights) {{
                                 Object.keys(portfolioData.optimal_weights).forEach(symbol => {{
                                     const weight = portfolioData.optimal_weights[symbol];
                                     const expectedReturn = portfolioData.stock_metrics?.[symbol]?.expected_return || 0;
                                     const volatility = portfolioData.stock_metrics?.[symbol]?.volatility || 0;
                                     
                                     csvContent += `${{symbol}},${{weight:.4f}},${{expectedReturn:.4f}},${{volatility:.4f}}\\n`;
                                 }});
                             }}
                             
                             const dataBlob = new Blob([csvContent], {{type: 'text/csv'}});
                             const url = URL.createObjectURL(dataBlob);
                             const link = document.createElement('a');
                             link.href = url;
                             link.download = `${{portfolioName.replace(/\\s+/g, '_')}}_export.csv`;
                             document.body.appendChild(link);
                             link.click();
                             document.body.removeChild(link);
                             URL.revokeObjectURL(url);
                             
                             console.log('Portfolio CSV exported successfully:', portfolioName);
                         }} catch (error) {{
                             console.error('Error exporting portfolio CSV:', error);
                         }}
                     }}
                 }}
                 
                 // Initialize the portfolio viewer when the page loads
                 document.addEventListener('DOMContentLoaded', () => {{
                     console.log('Initializing PortfolioViewer...');
                     window.portfolioViewer = new PortfolioViewer();
                     
                     // Make functions globally available for onclick handlers
                     window.togglePortfolioDetails = (portfolioId) => window.portfolioViewer.togglePortfolioDetails(portfolioId);
                     window.exportPortfolio = (index) => window.portfolioViewer.exportPortfolio(index);
                     window.exportPortfolioCSV = (index) => window.portfolioViewer.exportPortfolioCSV(index);
                     
                     console.log('PortfolioViewer initialized successfully');
                 }});
             </script>
        </body>
        </html>
        '''
        return render_template_string(profile_html)
    
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
