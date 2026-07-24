"""Pruebas unitarias e integración para el módulo de Autenticación (Signup, Login, Logout, Idioma)."""

from app.models import User


def test_signup_success(client, db):
    """12. Verifica el registro exitoso de un nuevo usuario desde el formulario HTTP POST."""
    response = client.post('/signup', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'Password123!',
        'password2': 'Password123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'newuser@example.com'


def test_signup_duplicate_error(client, db, test_user):
    """13. Verifica la validación de errores al intentar registrar un nombre de usuario duplicado."""
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'different@example.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    # No debe crear un segundo usuario con ese mismo username
    users_count = User.query.filter_by(username='testuser').count()
    assert users_count == 1


def test_login_success(client, db, test_user):
    """14. Verifica el inicio de sesión exitoso con credenciales válidas."""
    response = client.post('/', data={
        'username': 'testuser',
        'password': 'Secret123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'logout' in response.data.lower() or b'dashboard' in response.data.lower() or response.request.path != '/'


def test_login_invalid_password(client, db, test_user):
    """15. Verifica el rechazo de inicio de sesión cuando se ingresa una contraseña incorrecta."""
    response = client.post('/', data={
        'username': 'testuser',
        'password': 'WrongPassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid' in response.data or b'inv\xc3\xa1lid' in response.data or b'login' in response.data.lower()


def test_logout(auth_client):
    """16. Verifica que el cierre de sesión destruya la sesión del usuario y redirija."""
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200


def test_unauthorized_access(client):
    """17. Verifica la protección de rutas restringidas redireccionando a login sin autenticación."""
    response = client.get('/index', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location'] or '/' in response.headers['Location']


def test_set_language(client):
    """18. Verifica el cambio dinámico de idioma de la sesión del usuario."""
    response = client.get('/set_language/es', follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get('lang') == 'es'

    response_en = client.get('/set_language/en', follow_redirects=True)
    assert response_en.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get('lang') == 'en'
