"""Formularios WTForms para el módulo de autenticación."""

from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp, ValidationError
from app.models import User


class SignupForm(FlaskForm):
    """Formulario de registro de nuevos usuarios con validación avanzada."""

    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[
        DataRequired(),
        EqualTo('password2', message=_l('Passwords must match.')),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
            message=_l('Password: min 8 chars, uppercase, lowercase, digit, special char.')
        )
    ])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired()])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        """Valida que el nombre de usuario no esté ya registrado."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))


class LoginForm(FlaskForm):
    """Formulario para inicio de sesión de usuarios existentes."""

    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    submit = SubmitField(_l('Log In'))

