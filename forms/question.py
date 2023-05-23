from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# Форма добавления вопроса
class QuestionForm(FlaskForm):
    text = StringField('Слово', validators=[DataRequired()])
    submit = SubmitField('Добавить слово')

