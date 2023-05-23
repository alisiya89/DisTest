from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# Форма добавления опроса
class PollForm(FlaskForm):
    title = StringField('Название опроса', validators=[DataRequired()])
    submit = SubmitField('Добавить опрос')