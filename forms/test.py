from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FormField, FieldList, SelectMultipleField, BooleanField, RadioField, Label
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput


# Форма ответа на вопрос
class AskForm(FlaskForm):

    id = StringField()
    question = Label(field_id=0, text='')
    type = ''
    one_answer = RadioField()
    many_answer = SelectMultipleField(
        widget=ListWidget(html_tag='ul', prefix_label=False),
        option_widget=CheckboxInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# Форма прохождения опроса
class TestForm(FlaskForm):

    id = StringField()
    questions = FieldList(FormField(AskForm))
    submit = SubmitField('Отправить ответы')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.questions = [[Label(field_id=i, text=''), RadioField()] for i in range(count)]




# Форма добавления ответа
class AnswerForm(FlaskForm):
    id = StringField()
    question = StringField()
    text = StringField('Ответ', validators=[DataRequired()])
    right = BooleanField('Правильный')
    submit = SubmitField('Добавить ответ')