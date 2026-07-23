"""Fábrica de aplicaciones Flask (Application Factory Pattern)."""

from flask import Flask, jsonify, session, request
from sqlalchemy import text
from datetime import datetime
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
        return User.query.get(int(user_id))

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

    # Inyección de locale en el contexto de plantillas HTML
    @app.context_processor
    def inject_locale():
        return {'get_locale': get_locale}

    # Endpoint de estado del servicio (/api/health)
    @app.route('/api/health')
    def health_check():
        """Verifica la salud del servidor y la conexión a la base de datos."""
        health = {
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat(),
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
    return session.get('lang', request.accept_languages.best_match(['en', 'es'], default='en'))

