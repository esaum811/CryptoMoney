"""Formularios WTForms para el módulo principal (Watchlist y Transacciones)."""

from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import SelectField, FloatField, SubmitField, StringField
from wtforms.validators import DataRequired, NumberRange


class WatchlistForm(FlaskForm):
    """Formulario para agregar criptomonedas a la lista de seguimiento."""

    crypto = SelectField(_l('Cryptocurrency'), choices=[])
    lower_limit = FloatField(_l('Lower Price Limit'), validators=[])
    upper_limit = FloatField(_l('Upper Price Limit'), validators=[])
    submit = SubmitField(_l('Add'))


class TransactionForm(FlaskForm):
    """Formulario para registrar operaciones de compra o venta en el portafolio P&L."""

    symbol = SelectField(_l('Cryptocurrency'), choices=[])
    type = SelectField(_l('Type'), choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
    quantity = FloatField(_l('Quantity'), validators=[DataRequired(), NumberRange(min=0.00000001)])
    price = FloatField(_l('Price per unit'), validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField(_l('Add Transaction'))

