from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app.auth import auth_bp
from app.auth.forms import SignupForm, LoginForm
from app.models import User
from app.extensions import db


@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'), 'danger')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', form=form)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash(_('Username already taken.'), 'warning')
            return redirect(url_for('auth.signup'))
        if User.query.filter_by(email=form.email.data).first():
            flash(_('Email already registered. Please login.'), 'warning')
            return redirect(url_for('auth.login'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Account created successfully! Please login.'), 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/signup.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['en', 'es']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('auth.login'))
