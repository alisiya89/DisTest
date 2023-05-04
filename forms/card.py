from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# Форма добавления карточки
class CardForm(FlaskForm):
    word = StringField('Слово', validators=[DataRequired()])
    submit = SubmitField('Добавить слово')

