from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from models import db, User

def role_required(*roles):
    """Decorator to restrict access to users having one of the allowed roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        # API or Form submission handling
        data = request.form if request.form else request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'success': True, 'message': 'Logged in successfully', 'role': user.role})
            return redirect(url_for('index'))
            
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        flash('Invalid email or password', 'error')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        data = request.form if request.form else request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'Citizen')
        if role not in ['Citizen', 'Lawyer', 'Judge', 'Admin']:
            role = 'Citizen'

        if User.query.filter_by(email=email).first():
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'success': False, 'message': 'Email already registered'}), 400
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'success': False, 'message': 'Username already taken'}), 400
            flash('Username already taken', 'error')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'success': True, 'message': 'Registration successful'})
        return redirect(url_for('index'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
