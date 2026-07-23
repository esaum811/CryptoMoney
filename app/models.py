"""Modelos de la base de datos (SQLAlchemy ORM)."""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    """Modelo para representar los usuarios registrados en el sistema."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    receive_portfolio_email = db.Column(db.Boolean, default=False)

    # Relación uno-a-muchos con la lista de seguimiento
    watchlist = db.relationship('Watchlist', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Genera y almacena el hash de la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña ingresada contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)


class Watchlist(db.Model):
    """Modelo para la lista de seguimiento de criptomonedas por usuario."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    crypto_name = db.Column(db.String(64))
    lower_limit = db.Column(db.Float)
    upper_limit = db.Column(db.Float)


class PriceAlerts(db.Model):
    """Modelo para las alertas de precio (límites superior e inferior)."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='price_alerts')
    symbol = db.Column(db.String(20), nullable=False)
    lower_limit = db.Column(db.Float, nullable=False)
    upper_limit = db.Column(db.Float, nullable=False)
    is_triggered = db.Column(db.Boolean, default=False)


class AlertLog(db.Model):
    """Historial de alertas de precio disparadas en el sistema."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    alert_type = db.Column(db.String(10))
    trigger_price = db.Column(db.Float)
    limit_value = db.Column(db.Float)
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    email_sent = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='alert_logs')


class Transaction(db.Model):
    """Registro de transacciones de compra/venta para el portafolio P&L."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(4), nullable=False)  # 'BUY' o 'SELL'
    quantity = db.Column(db.Float, nullable=False)
    price_at_transaction = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='transactions')

