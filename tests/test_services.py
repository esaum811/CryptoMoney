"""Pruebas unitarias para la Capa de Servicios (Bybit Client, Email Service, Tasks)."""

from unittest.mock import patch, MagicMock
import pandas as pd
from app.services.bybit_client import get_symbols, get_symbol_info, get_candlestick_data
from app.services.email_service import send_email, send_alert_email, send_portfolio_summary
from app.tasks import check_price_alerts
from app.models import PriceAlerts, AlertLog, Watchlist


@patch('requests.get')
def test_bybit_get_symbols_success(mock_get):
    """6. Verifica la obtención exitosa de la lista de pares spot desde la API de Bybit."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'result': {
            'list': [{'name': 'BTCUSDT'}, {'name': 'ETHUSDT'}]
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    symbols = get_symbols()
    assert len(symbols) == 2
    assert symbols[0]['name'] == 'BTCUSDT'


@patch('requests.get')
def test_bybit_get_symbols_error_handling(mock_get):
    """7. Verifica la respuesta de fallback cuando la API externa presenta fallos o timeout."""
    mock_get.side_effect = Exception("Connection timeout")

    symbols = get_symbols()
    assert isinstance(symbols, list)
    assert len(symbols) >= 1
    assert symbols[0]['name'] == 'BTCUSDT'


@patch('requests.get')
def test_bybit_candlestick_data(mock_get):
    """8. Verifica el procesamiento de datos OHLC para gráficos candlestick en un DataFrame."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'result': {
            'list': [
                [1700000000000, '50000', '51000', '49500', '50500'],
                [1700000060000, '50500', '52000', '50000', '51500']
            ]
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    df = get_candlestick_data('BTCUSDT', '5m', 2)
    assert isinstance(df, pd.DataFrame)
    assert 'open' in df.columns
    assert 'close' in df.columns
    assert len(df) == 2


@patch('smtplib.SMTP')
def test_email_service_send_alert(mock_smtp, app):
    """9. Verifica la preparación y envío simulado de un correo de alerta de precio."""
    with app.app_context():
        app.config['MAIL_SENDER'] = 'test@gmail.com'
        app.config['MAIL_PASSWORD'] = 'secret'

        instance = mock_smtp.return_value
        result = send_alert_email('user@test.com', 'BTCUSDT', 65000.0, 5.2)

        assert result is True
        assert instance.sendmail.called


@patch('app.services.email_service.send_email')
@patch('app.services.email_service.get_symbol_info')
def test_email_service_summary(mock_info, mock_send, app, db, test_user):
    """10. Verifica la generación del resumen diario del portafolio del usuario."""
    with app.app_context():
        app.config['MAIL_SENDER'] = 'test@gmail.com'
        app.config['MAIL_PASSWORD'] = 'secret'
        test_user.receive_portfolio_email = True

        # Agregar watchlist item
        item = Watchlist(user_id=test_user.id, crypto_name='BTCUSDT')
        db.session.add(item)
        db.session.commit()

        mock_info.return_value = [{'lastPrice': '62000.00', 'price24hPcnt': '0.035'}]
        mock_send.return_value = True

        send_portfolio_summary(test_user)
        assert mock_send.called
        assert "BTCUSDT" in mock_send.call_args[0][2]


@patch('app.tasks.get_symbol_info')
@patch('app.tasks.send_alert_email')
def test_check_price_alerts_task(mock_send_email, mock_get_info, app, db, test_user):
    """11. Verifica la ejecución periódica de la tarea Celery/Background de alertas de precio."""
    with app.app_context():
        # Crear alerta activa
        alert = PriceAlerts(
            user_id=test_user.id,
            symbol='BTCUSDT',
            lower_limit=50000.0,
            upper_limit=70000.0,
            is_triggered=False
        )
        db.session.add(alert)
        db.session.commit()

        # Simular precio de mercado superando el límite superior
        mock_get_info.return_value = [{'lastPrice': '72000.00', 'price24hPcnt': '0.05'}]
        mock_send_email.return_value = True

        check_price_alerts(app)

        updated_alert = db.session.get(PriceAlerts, alert.id)
        assert updated_alert.is_triggered is True

        log = AlertLog.query.filter_by(user_id=test_user.id).first()
        assert log is not None
        assert log.alert_type == 'UPPER'
        assert log.trigger_price == 72000.0
