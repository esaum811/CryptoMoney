"""Fixtures globales de Pytest para inicialización de Flask, base de datos y clientes de prueba."""

import pytest
from app import create_app
from app.extensions import db as _db
from app.models import User
from config import Config


class TestConfig(Config):
    """Configuración especial para entorno de pruebas de Pytest."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'


@pytest.fixture(scope='session')
def app():
    """Crea y retorna una instancia de la aplicación Flask en modo TESTING."""
    _app = create_app(TestConfig)
    with _app.app_context():
        yield _app


@pytest.fixture(scope='function')
def client(app):
    """Cliente HTTP simulado para probar endpoints y peticiones en Flask."""
    return app.test_client()


@pytest.fixture(scope='function')
def db(app):
    """Inicializa una base de datos en memoria para cada prueba y la limpia al finalizar."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def test_user(db):
    """Crea un usuario de prueba en la base de datos."""
    user = User(username='testuser', email='test@example.com')
    user.set_password('Secret123!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def auth_client(client, test_user):
    """Cliente HTTP autenticado con sesión iniciada para el usuario de prueba."""
    client.post('/', data={
        'username': 'testuser',
        'password': 'Secret123!'
    }, follow_redirects=True)
    return client
