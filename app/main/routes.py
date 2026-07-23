"""Rutas y controladores del Blueprint principal (Dashboard, Velas, Alertas, Watchlist, Portafolio P&L)."""

from flask import render_template, redirect, url_for, flash, session, request, jsonify
from flask_login import current_user, login_required
from flask_babel import _
from datetime import datetime
import pandas as pd
from app.main import main_bp
from app.main.forms import WatchlistForm, TransactionForm
from app.models import Watchlist, PriceAlerts, AlertLog, Transaction, User
from app.extensions import db
from app.services.bybit_client import get_symbols, get_symbol_info, get_candlestick_data
from app.services.email_service import send_alert_email, send_portfolio_summary


def _load_crypto_choices():
    """Carga y procesa la lista de pares de criptomonedas disponibles desde Bybit."""
    try:
        symbols = get_symbols()
        return [(s['name'], s['name']) for s in symbols]
    except Exception:
        return [('BTCUSDT', 'BTCUSDT'), ('ETHUSDT', 'ETHUSDT')]


# ── Dashboard / Chart ──────────────────────────────────────────────

@main_bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """Ruta principal: muestra el gráfico candlestick interactivo y la watchlist."""
    watchlist_form = WatchlistForm()
    watchlist_form.crypto.choices = _load_crypto_choices()
    watchlist = Watchlist.query.filter_by(user_id=current_user.id).all()

    if watchlist_form.validate_on_submit():
        crypto = Watchlist(
            user_id=current_user.id,
            crypto_name=watchlist_form.crypto.data,
            lower_limit=watchlist_form.lower_limit.data,
            upper_limit=watchlist_form.upper_limit.data
        )
        db.session.add(crypto)
        db.session.commit()
        flash(_('Added to watchlist!'), 'success')
        return redirect(url_for('main.index'))

    selected = request.args.get('crypto', 'BTCUSDT')
    timeline = request.args.get('timeline', '5')
    data = get_candlestick_data(selected, timeline, 100)
    data['times'] = pd.to_datetime(data['times'])
    data['times'] = data['times'].dt.strftime('%Y-%m-%d %H:%M:%S')

    session['saved_symbol'] = selected

    # Alertas activas para superposición en el gráfico
    alerts = PriceAlerts.query.filter_by(
        user_id=current_user.id, is_triggered=False
    ).all()
    alert_data = [{'symbol': a.symbol, 'lower': a.lower_limit, 'upper': a.upper_limit} for a in alerts]

    return render_template(
        'main/index.html',
        watchlist_form=watchlist_form,
        watchlist=watchlist,
        candlestick_data=data.to_dict(orient='records'),
        alert_data=alert_data,
        selected_crypto=selected
    )


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Redirección de compatibilidad hacia la vista principal."""
    watchlist = Watchlist.query.filter_by(user_id=current_user.id).all()
    return redirect(url_for('main.index'))


# ── API Endpoints ──────────────────────────────────────────────────

@main_bp.route('/candlestick_data')
@login_required
def candlestick_data():
    """Endpoint JSON: Devuelve los datos OHLC para renderizar velas en Plotly.js."""
    selected = request.args.get('symbol') or request.args.get('crypto') or session.get('saved_symbol', 'BTCUSDT')
    if selected == 'None':
        selected = session.get('saved_symbol', 'BTCUSDT')
    timeline = request.args.get('timeline', '15m')
    data = get_candlestick_data(selected, timeline, 100)
    data['times'] = pd.to_datetime(data['times'])
    data['times'] = data['times'].dt.strftime('%Y-%m-%d %H:%M:%S')
    session['saved_symbol'] = selected
    return jsonify(data.to_dict(orient='records'))


@main_bp.route('/symbol_info')
@login_required
def symbol_info():
    """Endpoint JSON: Devuelve la información del ticker en tiempo real (precio, cambio 24h, etc.)."""
    symbol = request.args.get('symbol', 'BTCUSDT')
    info = get_symbol_info(symbol)
    if info and len(info) > 0:
        raw = info[0]
        return jsonify({
            'symbol': raw.get('symbol', symbol),
            'current_price': raw.get('lastPrice', '0'),
            'change_24h': str(float(raw.get('price24hPcnt', 0)) * 100),
            'high_24h': raw.get('highPrice24h', '0'),
            'low_24h': raw.get('lowPrice24h', '0'),
            'volume_24h': raw.get('volume24h', '0'),
        })
    return jsonify({'symbol': symbol, 'current_price': '0', 'change_24h': '0', 'high_24h': '0', 'low_24h': '0'})


# ── Price Alerts ───────────────────────────────────────────────────

@main_bp.route('/add_price_alert', methods=['POST'])
@login_required
def add_price_alert():
    """Crea una nueva alerta de precio (límite superior e inferior)."""
    data = request.get_json()
    if not data:
        return jsonify({'message': _('Invalid request')}), 400
    symbol = data.get('crypto_name', 'BTCUSDT')
    try:
        lower = float(data.get('lower_limit', 0))
        upper = float(data.get('upper_limit', 0))
    except (TypeError, ValueError):
        return jsonify({'message': _('Invalid limit values')}), 400
    alert = PriceAlerts(
        user_id=current_user.id, symbol=symbol,
        lower_limit=lower, upper_limit=upper
    )
    db.session.add(alert)
    db.session.commit()
    return jsonify({'message': _('Price alert added successfully.')}), 200


@main_bp.route('/check_alerts')
@login_required
def check_alerts():
    """Verifica si alguna alerta activa ha sido alcanzada por el precio de mercado."""
    triggered = []
    alerts = PriceAlerts.query.filter_by(
        user_id=current_user.id, is_triggered=False
    ).all()
    for alert in alerts:
        info = get_symbol_info(alert.symbol)
        if not info:
            continue
        last_price = float(info[0].get('lastPrice', 0))
        if last_price >= alert.upper_limit or last_price <= alert.lower_limit:
            change = float(info[0].get('price24hPcnt', 0))
            alert_type = 'UPPER' if last_price >= alert.upper_limit else 'LOWER'
            # Registrar evento en la BD
            log = AlertLog(
                user_id=alert.user_id, symbol=alert.symbol,
                alert_type=alert_type, trigger_price=last_price,
                limit_value=alert.upper_limit if alert_type == 'UPPER' else alert.lower_limit,
                email_sent=True
            )
            db.session.add(log)
            alert.is_triggered = True
            db.session.commit()
            send_alert_email(current_user.email, alert.symbol, last_price, change)
            triggered.append(alert.symbol)
    return jsonify({'triggered_alerts': triggered})


# ── Alert History ──────────────────────────────────────────────────

@main_bp.route('/alert_history')
@login_required
def alert_history():
    """Muestra el historial de alertas disparadas para el usuario autenticado."""
    logs = AlertLog.query.filter_by(user_id=current_user.id)\
        .order_by(AlertLog.triggered_at.desc()).all()
    return render_template('main/alert_history.html', logs=logs)


# ── Watchlist ──────────────────────────────────────────────────────

@main_bp.route('/add_to_watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    """Agrega una criptomoneda a la lista de seguimiento del usuario."""
    crypto_name = request.form.get('crypto') or request.form.get('crypto_name')
    if crypto_name:
        existing = Watchlist.query.filter_by(user_id=current_user.id, crypto_name=crypto_name).first()
        if not existing:
            crypto = Watchlist(user_id=current_user.id, crypto_name=crypto_name)
            db.session.add(crypto)
            db.session.commit()
            flash(_('Crypto added to watchlist!'), 'success')
        else:
            flash(_('Already in watchlist'), 'warning')
    return redirect(url_for('main.index'))


@main_bp.route('/remove_from_watchlist/<crypto_name>', methods=['POST'])
@login_required
def remove_from_watchlist(crypto_name):
    """Elimina una criptomoneda de la lista de seguimiento del usuario."""
    crypto = Watchlist.query.filter_by(
        user_id=current_user.id, crypto_name=crypto_name
    ).first()
    if crypto:
        db.session.delete(crypto)
        db.session.commit()
    return jsonify({'message': _('Removed successfully')}), 200


# ── Portfolio (Transactions P&L) ───────────────────────────────────

@main_bp.route('/portfolio', methods=['GET', 'POST'])
@login_required
def portfolio():
    """Gestión del portafolio P&L: registro de compras/ventas y cálculo de pérdidas/ganancias."""
    form = TransactionForm()
    crypto_choices = _load_crypto_choices()
    form.symbol.choices = crypto_choices

    if request.method == 'POST':
        symbol = request.form.get('symbol')
        tx_type = request.form.get('type', 'BUY')
        try:
            quantity = float(request.form.get('quantity', 0))
            price = float(request.form.get('price', 0))
        except (ValueError, TypeError):
            quantity = 0
            price = 0

        if symbol and quantity > 0 and price >= 0:
            tx = Transaction(
                user_id=current_user.id,
                symbol=symbol.strip().upper(),
                type=tx_type,
                quantity=quantity,
                price_at_transaction=price
            )
            db.session.add(tx)
            db.session.commit()
            flash(_('Transaction recorded!'), 'success')
            return redirect(url_for('main.portfolio'))
        else:
            flash(_('Invalid transaction values. Please check symbol, quantity and price.'), 'danger')

    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.timestamp.desc()).all()

    # Cálculo consolidado del portafolio
    holdings = {}
    for tx in transactions:
        if tx.symbol not in holdings:
            holdings[tx.symbol] = {'qty': 0, 'cost': 0}
        if tx.type == 'BUY':
            holdings[tx.symbol]['qty'] += tx.quantity
            holdings[tx.symbol]['cost'] += tx.quantity * tx.price_at_transaction
        else:
            holdings[tx.symbol]['qty'] -= tx.quantity
            holdings[tx.symbol]['cost'] -= tx.quantity * tx.price_at_transaction

    portfolio_data = []
    total_value = 0
    total_cost = 0
    for symbol, data in holdings.items():
        if data['qty'] <= 0:
            continue
        info = get_symbol_info(symbol)
        current_price = float(info[0]['lastPrice']) if info else 0
        value = data['qty'] * current_price
        cost = data['cost']
        pnl = value - cost
        pnl_pct = (pnl / cost * 100) if cost > 0 else 0
        portfolio_data.append({
            'symbol': symbol, 'qty': data['qty'],
            'avg_price': cost / data['qty'] if data['qty'] > 0 else 0,
            'current_price': current_price, 'value': value,
            'pnl': pnl, 'pnl_pct': pnl_pct
        })
        total_value += value
        total_cost += cost

    return render_template(
        'main/portfolio.html', form=form, transactions=transactions,
        portfolio_data=portfolio_data, total_value=total_value,
        total_cost=total_cost, total_pnl=total_value - total_cost
    )


# ── Email Preferences ─────────────────────────────────────────────

@main_bp.route('/sign_up_for_portfolio_email', methods=['POST'])
@login_required
def toggle_email():
    """Activa o desactiva la recepción de reportes por correo electrónico."""
    data = request.get_json()
    current_user.receive_portfolio_email = data.get('sign_up', False)
    db.session.commit()
    if current_user.receive_portfolio_email:
        send_portfolio_summary(current_user)
    return jsonify({'message': _('Email preference updated')}), 200


@main_bp.route('/check_portfolio_email')
@login_required
def check_email_pref():
    """Consulta el estado de la preferencia de email del usuario."""
    return jsonify({'value': current_user.receive_portfolio_email})

