"""Tareas en segundo plano y procesamiento asíncrono de alertas."""

from app.extensions import db
from app.models import PriceAlerts, AlertLog, User
from app.services.bybit_client import get_symbol_info
from app.services.email_service import send_alert_email


def check_price_alerts(app):
    """Tarea periódica: evalúa alertas de precio activas y envía correos cuando se superan los límites."""
    with app.app_context():
        alerts = PriceAlerts.query.filter_by(is_triggered=False).all()
        for alert in alerts:
            info = get_symbol_info(alert.symbol)
            if not info:
                continue
            try:
                last_price = float(info[0].get('lastPrice', 0))
                price_change = float(info[0].get('price24hPcnt', 0))
            except (IndexError, KeyError, ValueError):
                continue

            triggered = False
            alert_type = None
            if last_price >= alert.upper_limit:
                triggered = True
                alert_type = 'UPPER'
            elif last_price <= alert.lower_limit:
                triggered = True
                alert_type = 'LOWER'

            if triggered:
                # Almacenar el registro histórico de la alerta disparada
                log = AlertLog(
                    user_id=alert.user_id,
                    symbol=alert.symbol,
                    alert_type=alert_type,
                    trigger_price=last_price,
                    limit_value=alert.upper_limit if alert_type == 'UPPER' else alert.lower_limit,
                    email_sent=False
                )
                alert.is_triggered = True
                user = db.session.get(User, alert.user_id)
                if user:
                    # Notificar al usuario por email
                    success = send_alert_email(user.email, alert.symbol, last_price, price_change)
                    log.email_sent = success
                db.session.add(log)
                db.session.commit()
                print(f"Alerta disparada para {alert.symbol} en {last_price}")

