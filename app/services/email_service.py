import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app, render_template
from app.services.bybit_client import get_symbol_info


def send_email(recipient_email, subject, body):
    """Send HTML email via Gmail SMTP. Credentials from app config."""
    sender = current_app.config.get('MAIL_SENDER', '')
    password = current_app.config.get('MAIL_PASSWORD', '')
    if not sender or not password:
        print("Email not configured — skipping send.")
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
        print(f"Email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_alert_email(recipient_email, symbol, price, percentage_change):
    """Send a price alert notification email."""
    body = render_template(
        'email/price_alert.html',
        symbol=symbol,
        price=price,
        percentage_change=percentage_change
    )
    return send_email(recipient_email, "Price Alert Triggered", body)


def send_portfolio_summary(user):
    """Build full portfolio summary and send as ONE email (fixed bug: was sending partial emails inside loop)."""
    sender = current_app.config.get('MAIL_SENDER', '')
    password = current_app.config.get('MAIL_PASSWORD', '')
    if not sender or not password or not user.receive_portfolio_email:
        return
    body = "Here is your daily portfolio update:\n\n"
    for item in user.watchlist:
        info = get_symbol_info(item.crypto_name)
        if info:
            data = info[0]
            last_price = float(data.get('lastPrice', 0))
            change = float(data.get('price24hPcnt', 0))
            body += f"{item.crypto_name}: ${last_price:.2f} (Change: {change:.4f}%)\n"
    send_email(user.email, "Daily Portfolio Update", body)
