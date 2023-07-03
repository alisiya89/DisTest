from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FormField, FieldList, SelectField, BooleanField, RadioField, Label
from wtforms.validators import DataRequired


# Форма ответа на вопрос
class AskForm(FlaskForm):

    id = StringField()
    question = Label(field_id=0, text='')
    type = ''
    one_answer = RadioField()
    many_answer = SelectField()



# Форма прохождения опроса
class TestForm(FlaskForm):

    id = StringField()
    questions = FieldList(FormField(AskForm))
    submit = SubmitField('Отправить ответы')
    #
    # def __init__(self, count):
    #     super(TestForm, self).__init__()
    #     self.questions = [[Label(field_id=i, text=''), RadioField()] for i in range(count)]




# Форма добавления ответа
class AnswerForm(FlaskForm):
    id = StringField()
    question = StringField()
    text = StringField('Ответ', validators=[DataRequired()])
    right = BooleanField('Правильный')
    submit = SubmitField('Добавить ответ')