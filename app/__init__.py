from flask import Flask, jsonify, session, request
from sqlalchemy import text
from datetime import datetime
from config import Config
from app.extensions import db, login_manager, migrate, babel


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app, locale_selector=get_locale)

    # Import models so they are registered with SQLAlchemy
    from app import models  # noqa: F401

    # Register user loader
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Template filters
    @app.template_filter('truncate_email')
    def truncate_email(email, max_length=20):
        if len(email) <= max_length:
            return email
        half = max_length // 2
        return email[:half] + '****' + email[-half:]

    # Context processor for locale in templates
    @app.context_processor
    def inject_locale():
        return {'get_locale': get_locale}

    # Health check endpoint (Phase 6 requirement)
    @app.route('/api/health')
    def health_check():
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

    # Create tables
    with app.app_context():
        db.create_all()

    return app


def get_locale():
    from flask import session, request
    return session.get('lang', request.accept_languages.best_match(['en', 'es'], default='en'))
