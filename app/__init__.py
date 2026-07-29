"""Fábrica de aplicaciones Flask (Application Factory Pattern)."""
from flask import Flask, jsonify, session, request, has_request_context
from sqlalchemy import text
from datetime import datetime, timezone
from config import Config
from app.extensions import db, login_manager, migrate, babel


def create_app(config_class=Config):
    """Inicializa y configura la instancia de la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicialización de extensiones compartidas
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app, locale_selector=get_locale)

    # Importar modelos para su registro en SQLAlchemy
    from app import models  # noqa: F401
    from app.models import User

    # Cargador de usuarios para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Registro de Blueprints de la aplicación
    from app.auth import auth_bp
    from app.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Filtros personalizados de Jinja2 para plantillas HTML
    @app.template_filter('truncate_email')
    def truncate_email(email, max_length=20):
        """Trunca emails largos en la interfaz gráfica."""
        if len(email) <= max_length:
            return email
        half = max_length // 2
        return email[:half] + '****' + email[-half:]

    # Diccionario de traducciones dinámicas al español
    SPANISH_TRANSLATIONS = {
        'Dashboard': 'Panel Principal',
        'Portfolio': 'Portafolio',
        'Alert History': 'Historial de Alertas',
        'Watchlist': 'Lista de Seguimiento',
        'Search cryptocurrency...': 'Buscar criptomoneda...',
        'Select Crypto': 'Seleccionar Cripto',
        'No coins in watchlist': 'No hay criptomonedas en la lista',
        'No matches found': 'No se encontraron coincidencias',
        'Loading...': 'Cargando...',
        'Loading chart data...': 'Cargando datos del gráfico...',
        'Close': 'Cerrar',
        'Login': 'Iniciar Sesión',
        'Logout': 'Cerrar Sesión',
        'Register': 'Registrarse',
        'Username': 'Nombre de Usuario',
        'Email': 'Correo Electrónico',
        'Password': 'Contraseña',
        'Repeat Password': 'Repetir Contraseña',
        'Set Alert': 'Establecer Alerta',
        'Remove': 'Eliminar',
        'Set Price Alert': 'Configurar Alerta de Precio',
        'Asset': 'Activo',
        'Current Price': 'Precio Actual',
        'Alert Condition': 'Condición de Alerta',
        'Price rises above': 'El precio sube por encima de',
        'Price falls below': 'El precio cae por debajo de',
        'Target Price (USD)': 'Precio Objetivo (USD)',
        'Create Alert': 'Crear Alerta',
        'Cancel': 'Cancelar',
        'Add Transaction': 'Agregar Transacción',
        'Record Transaction': 'Registrar Transacción',
        'Symbol': 'Símbolo',
        'Type': 'Tipo',
        'Quantity': 'Cantidad',
        'Price': 'Precio',
        'Buy': 'Comprar',
        'Sell': 'Vender',
        'Save Transaction': 'Guardar Transacción',
        'Current Holdings': 'Tenencias Actuales',
        'Total Value': 'Valor Total',
        'Total Cost': 'Costo Total',
        'Total P&L': 'Ganancia/Pérdida Total',
        'Qty': 'Cant.',
        'Avg Price': 'Precio Prom.',
        'P&L %': '% Gan/Perd',
        'Action': 'Acción',
        'Trigger Price': 'Precio de Disparo',
        'Limit Price': 'Precio Límite',
        'Triggered At': 'Fecha de Disparo',
        'Status': 'Estado',
        'Email Sent': 'Correo Enviado',
        'Not Sent': 'No Enviado',
        'No alerts triggered yet.': 'No hay alertas disparadas aún.',
        'Passwords must match.': 'Las contraseñas deben coincidir.',
        'Please use a different username.': 'Por favor usa un nombre de usuario diferente.',
        'Invalid username or password': 'Usuario o contraseña inválidos'
    }

    def custom_translate(text):
        lang = session.get('lang', 'en') if has_request_context() else 'en'
        if lang == 'es':
            return SPANISH_TRANSLATIONS.get(str(text), str(text))
        return str(text)

    app.jinja_env.globals['_'] = custom_translate

    # Inyección de locale en el contexto de plantillas HTML
    @app.context_processor
    def inject_locale():
        lang = session.get('lang', 'en') if has_request_context() else 'en'
        return {
            'get_locale': get_locale,
            '_': custom_translate,
            'current_lang': lang
        }

    # Endpoint de estado del servicio (/api/health)
    @app.route('/api/health')
    def health_check():
        """Verifica la salud del servidor y la conexión a la base de datos."""
        health = {
            'status': 'ok',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'database': 'connected',
            'version': '2.0.0'
        }
        try:
            db.session.execute(text('SELECT 1'))
        except Exception:
            health['database'] = 'disconnected'
            health['status'] = 'degraded'
        code = 200 if health['status'] == 'ok' else 503
        return jsonify(health), code

    # Creación inicial de tablas de la base de datos si no existen
    with app.app_context():
        db.create_all()

    return app


def get_locale():
    """Determina el idioma preferido del usuario (inglés o español)."""
    if has_request_context():
        return session.get('lang', request.accept_languages.best_match(['en', 'es'], default='en'))
    return 'en'


