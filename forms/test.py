from flask_wtf import FlaskForm
from wtforms import Field, StringField, SubmitField, FormField, FieldList, SelectMultipleField, RadioField, Label, Form
from wtforms.validators import DataRequired, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput

class RightManyAnswer:
    def __init__(self):
        self.message = 'Выберите хотя бы один вариант'
    def __call__(self, form, field):
        if True:
            raise ValidationError(self.message)


# Форма ответа на вопрос
class AskForm(Form):
    id = StringField()
    num = StringField()
    question = Label(field_id=0, text='')


class OneAskForm(AskForm):
    one_answer = RadioField(coerce=int)


class ManyAskForm(AskForm):
    # # TODO валидация поля с множественным выбором
    many_answer = SelectMultipleField(
        widget=ListWidget(html_tag='ul', prefix_label=False),
        option_widget=CheckboxInput(), )


# Форма прохождения опроса
class TestForm(FlaskForm):
    id = StringField()
    no_questions = FieldList(FormField(AskForm))
    one_questions = FieldList(FormField(OneAskForm))
    many_questions = FieldList(FormField(ManyAskForm))
    submit = SubmitField(label='Отправить ответы')
    #
    # def __init__(self, count, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.questions.min_entries = count
