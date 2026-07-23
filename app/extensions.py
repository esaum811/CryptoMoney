"""Instanciación centralizada de extensiones Flask."""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel

# ORM para interacción con la base de datos
db = SQLAlchemy()

# Gestor de autenticación y sesiones de usuario
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Herramienta de migraciones de la base de datos (Alembic)
migrate = Migrate()

# Herramienta de traducción e internacionalización
babel = Babel()

