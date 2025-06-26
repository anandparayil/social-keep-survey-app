"""
Authentication utilities for Social Keep
"""
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def participant_required(f):
    """Decorator to require participant privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'participant':
            flash('Access denied. Participant privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user information from session"""
    if 'user_id' in session:
        return {
            'id': session['user_id'],
            'username': session['username'],
            'email': session['email'],
            'user_type': session['user_type']
        }
    return None

def is_admin():
    """Check if current user is admin"""
    return session.get('user_type') == 'admin'

def is_participant():
    """Check if current user is participant"""
    return session.get('user_type') == 'participant'