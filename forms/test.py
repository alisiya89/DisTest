from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, BooleanField, RadioField, Label
from wtforms.validators import DataRequired


# Форма прохождения опроса
class TestForm(FlaskForm):
    id = StringField()
    questions = []
    submit = SubmitField('Отправить ответы')

    def __init__(self, count):
        FlaskForm.__init__(self)
        self.questions = [[Label(field_id=i, text=''), RadioField()] for i in range(count)]


# Форма добавления вопроса
class QuestionForm(FlaskForm):

    id = StringField()
    text = TextAreaField('Вопрос', validators=[DataRequired()])
    type = RadioField('Типы вопросов')
    submit = SubmitField('Добавить вопрос')


# Форма добавления ответа
class AnswerForm(FlaskForm):
    id = StringField()
    question = StringField()
    text = StringField('Ответ', validators=[DataRequired()])
    right = BooleanField('Правильный')
    submit = SubmitField('Добавить ответ')