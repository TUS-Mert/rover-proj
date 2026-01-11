from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please choose a different one.', 'warning')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            email=email,
            password_hash=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))