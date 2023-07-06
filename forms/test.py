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

class MyRadioField(RadioField):
    def __init__(self, *args, **kwargs):
        super(MyRadioField, self).__init__(*args, **kwargs)

    # def __call__(self, field, **kwargs):
    #     if field.checked:
    #         kwargs["checked"] = True
    #     return super(MyRadioField, self).__call__(field, **kwargs)
    #
    def process_formdata(self, value):
        print("Это я", value)

# Форма ответа на вопрос
class AskForm(Form):
    id = StringField()
    question = Label(field_id=0, text='')
    vid = ''
    one_answer = RadioField(coerce=int)
    # # TODO валидация поля с множественным выбором
    # many_answer = SelectMultipleField(
    #     widget=ListWidget(html_tag='ul', prefix_label=False),
    #     option_widget=CheckboxInput(), )


# Форма прохождения опроса
class TestForm(FlaskForm):
    id = StringField()
    questions = FieldList(FormField(AskForm))
    submit = SubmitField(label='Отправить ответы')
    #
    # def __init__(self, count, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.questions.min_entries = count
