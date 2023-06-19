from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired


# Форма добавления опроса
class PollForm(FlaskForm):
    title = StringField('Название опроса', validators=[DataRequired()])
    submit = SubmitField('Добавить опрос')


# Форма добавления вопроса
class QuestionForm(FlaskForm):
    id = StringField()
    text = TextAreaField('Вопрос', validators=[DataRequired()])
    submit = SubmitField('Добавить вопрос')


# Форма добавления ответа
class AnswerForm(FlaskForm):
    id = StringField()
    question = StringField()
    text = StringField('Ответ', validators=[DataRequired()])
    right = BooleanField('Правильный')
    submit = SubmitField('Добавить ответ')