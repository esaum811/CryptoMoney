"""Servicio para el envío de correos electrónicos transaccionales y notificaciones de alerta."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app, render_template
from app.services.bybit_client import get_symbol_info


def send_email(recipient_email, subject, body):
    """Envía un correo electrónico con formato HTML mediante el servidor SMTP de Gmail."""
    sender = current_app.config.get('MAIL_SENDER', '')
    password = current_app.config.get('MAIL_PASSWORD', '')
    if not sender or not password:
        print("Credenciales SMTP no configuradas — omitiendo envío de correo.")
        return False
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(sender, password)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient_email
        msg.attach(MIMEText(body, 'html'))
        s.sendmail(sender, recipient_email, msg.as_string())
        s.quit()
        print(f"Correo enviado exitosamente a {recipient_email}")
        return True
    except Exception as e:
        print(f"Error al enviar correo electrónico: {e}")
        return False


def send_alert_email(recipient_email, symbol, price, percentage_change):
    """Genera la plantilla y envía la notificación de alerta de precio alcanzado."""
    body = render_template(
        'email/price_alert.html',
        symbol=symbol,
        price=price,
        percentage_change=percentage_change
    )
    return send_email(recipient_email, "Notificación de Alerta de Precio", body)


def send_portfolio_summary(user):
    """Construye y envía el resumen diario consolidado del portafolio del usuario."""
    sender = current_app.config.get('MAIL_SENDER', '')
    password = current_app.config.get('MAIL_PASSWORD', '')
    if not sender or not password or not user.receive_portfolio_email:
        return
    body = "Aquí tienes la actualización diaria de tu lista de seguimiento:\n\n"
    for item in user.watchlist:
        info = get_symbol_info(item.crypto_name)
        if info:
            data = info[0]
            last_price = float(data.get('lastPrice', 0))
            change = float(data.get('price24hPcnt', 0))
            body += f"{item.crypto_name}: ${last_price:.2f} (Cambio 24h: {change:.4f}%)\n"
    send_email(user.email, "Resumen Diario del Portafolio", body)

