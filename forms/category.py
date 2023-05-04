from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# Форма добавления категории
class CategoryForm(FlaskForm):
    title = StringField('Название категории', validators=[DataRequired()])
    submit = SubmitField('Добавить категорию')