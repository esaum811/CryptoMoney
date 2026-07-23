import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env si existe
load_dotenv()


class Config:
    """Configuración centralizada de la aplicación Flask."""

    # Clave secreta para firma de cookies y sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-in-production')

    # URI de conexión a la base de datos (SQLite por defecto)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///crypto.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración del broker y backend de Celery (Redis)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Credenciales para el envío de correos electrónicos (SMTP)
    MAIL_SENDER = os.environ.get('MAIL_SENDER', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

    # Configuración de internacionalización (Flask-Babel)
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en', 'es']

