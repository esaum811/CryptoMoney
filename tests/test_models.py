"""Pruebas unitarias para la Capa de Modelos (User, Watchlist, PriceAlerts, Transaction, AlertLog)."""

import pytest
from sqlalchemy.exc import IntegrityError
from app.models import User, Watchlist, PriceAlerts, Transaction, AlertLog


def test_user_password_hashing(db):
    """1. Verifica la generación de hashes de contraseña y su correcta comprobación."""
    user = User(username='hash_user', email='hash@test.com')
    user.set_password('Password123!')

    assert user.password_hash is not None
    assert user.password_hash != 'Password123!'
    assert user.check_password('Password123!') is True
    assert user.check_password('WrongPassword') is False


def test_user_creation_and_uniqueness(db):
    """2. Verifica la creación de usuarios y la restricción de unicidad en username y email."""
    user1 = User(username='unique_user', email='unique@test.com')
    db.session.add(user1)
    db.session.commit()

    assert user1.id is not None

    # Intentar duplicar username
    user_duplicate = User(username='unique_user', email='other@test.com')
    db.session.add(user_duplicate)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_portfolio_and_transaction_creation(db, test_user):
    """3. Verifica el registro de transacciones de compra/venta y la relación con el usuario."""
    tx_buy = Transaction(
        user_id=test_user.id,
        symbol='BTCUSDT',
        type='BUY',
        quantity=0.5,
        price_at_transaction=60000.0
    )
    tx_sell = Transaction(
        user_id=test_user.id,
        symbol='BTCUSDT',
        type='SELL',
        quantity=0.2,
        price_at_transaction=65000.0
    )
    db.session.add_all([tx_buy, tx_sell])
    db.session.commit()

    user_txs = Transaction.query.filter_by(user_id=test_user.id).all()
    assert len(user_txs) == 2
    assert user_txs[0].symbol == 'BTCUSDT'
    assert user_txs[0].quantity == 0.5
    assert user_txs[1].type == 'SELL'


def test_price_alert_model(db, test_user):
    """4. Verifica la creación de alertas de precio, cambio de estado e historial log."""
    alert = PriceAlerts(
        user_id=test_user.id,
        symbol='ETHUSDT',
        lower_limit=2500.0,
        upper_limit=3500.0,
        is_triggered=False
    )
    db.session.add(alert)
    db.session.commit()

    assert alert.id is not None
    assert alert.is_triggered is False

    # Disparar alerta y registrar log
    alert.is_triggered = True
    log = AlertLog(
        user_id=test_user.id,
        symbol='ETHUSDT',
        alert_type='UPPER',
        trigger_price=3600.0,
        limit_value=3500.0,
        email_sent=True
    )
    db.session.add(log)
    db.session.commit()

    updated_alert = PriceAlerts.query.get(alert.id)
    assert updated_alert.is_triggered is True
    saved_log = AlertLog.query.filter_by(user_id=test_user.id).first()
    assert saved_log.trigger_price == 3600.0


def test_watchlist_model(db, test_user):
    """5. Verifica la adición de criptomonedas a la lista de seguimiento (Watchlist)."""
    item = Watchlist(
        user_id=test_user.id,
        crypto_name='SOLUSDT',
        lower_limit=100.0,
        upper_limit=200.0
    )
    db.session.add(item)
    db.session.commit()

    watchlist_items = Watchlist.query.filter_by(user_id=test_user.id).all()
    assert len(watchlist_items) == 1
    assert watchlist_items[0].crypto_name == 'SOLUSDT'
    assert watchlist_items[0].user.username == 'testuser'
