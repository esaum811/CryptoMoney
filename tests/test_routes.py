"""Pruebas unitarias e integración para las Rutas Principales y Endpoints API (Main Blueprint)."""

from unittest.mock import patch
from app.models import PriceAlerts, Transaction, Watchlist, User


def test_health_check_endpoint(client):
    """19. Verifica que el endpoint /api/health devuelva estado 200 y la estructura JSON de salud."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['database'] == 'connected'
    assert 'version' in data


@patch('app.main.routes.get_candlestick_data')
@patch('app.main.routes._load_crypto_choices')
def test_dashboard_authenticated(mock_choices, mock_kline, auth_client):
    """20. Verifica que la ruta principal /index se renderice exitosamente para un usuario autenticado."""
    mock_choices.return_value = [('BTCUSDT', 'BTCUSDT')]
    import pandas as pd
    df = pd.DataFrame([{'times': '2023-01-01 00:00:00', 'open': 50000, 'high': 51000, 'low': 49000, 'close': 50500}])
    mock_kline.return_value = df

    response = auth_client.get('/index')
    assert response.status_code == 200


def test_add_price_alert_route(auth_client, db, test_user):
    """21. Verifica la creación de una alerta de precio mediante el endpoint POST /add_price_alert."""
    payload = {
        'crypto_name': 'BTCUSDT',
        'lower_limit': 60000.0,
        'upper_limit': 75000.0
    }
    response = auth_client.post('/add_price_alert', json=payload)
    assert response.status_code == 200
    assert response.get_json()['message'] is not None

    alert = PriceAlerts.query.filter_by(user_id=test_user.id, symbol='BTCUSDT').first()
    assert alert is not None
    assert alert.lower_limit == 60000.0
    assert alert.upper_limit == 75000.0


def test_portfolio_add_transaction(auth_client, db, test_user):
    """22. Verifica el registro de una transacción de compra en el portafolio vía POST /portfolio."""
    response = auth_client.post('/portfolio', data={
        'symbol': 'ETHUSDT',
        'type': 'BUY',
        'quantity': 2.5,
        'price': 3000.0
    }, follow_redirects=True)

    assert response.status_code == 200
    tx = Transaction.query.filter_by(user_id=test_user.id, symbol='ETHUSDT').first()
    assert tx is not None
    assert tx.quantity == 2.5
    assert tx.price_at_transaction == 3000.0


@patch('app.main.routes.send_portfolio_summary')
def test_toggle_email_preferences(mock_summary, auth_client, db, test_user):
    """23. Verifica la actualización de preferencias de notificaciones por correo electrónico."""
    response = auth_client.post('/sign_up_for_portfolio_email', json={'sign_up': True})
    assert response.status_code == 200

    updated_user = db.session.get(User, test_user.id)
    assert updated_user.receive_portfolio_email is True


def test_remove_from_watchlist(auth_client, db, test_user):
    """24. Verifica la eliminación de una criptomoneda de la lista de seguimiento."""
    # Primero agregar item
    item = Watchlist(user_id=test_user.id, crypto_name='ADAUSDT')
    db.session.add(item)
    db.session.commit()

    response = auth_client.post('/remove_from_watchlist/ADAUSDT')
    assert response.status_code == 200

    deleted = Watchlist.query.filter_by(user_id=test_user.id, crypto_name='ADAUSDT').first()
    assert deleted is None
