from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import PasswordField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, ValidationError


# Форма регистрации
class RegisterForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


# Форма авторизации
class LoginForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


# Проверка файла на разрешенное расширение
def allowed_extension():
    def _allowed_extension(form, field):
        extensions = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
        if not field.data.filename[field.data.filename.find('.') + 1:] in extensions:
            raise ValidationError('Выберите файл с изображением')
    return _allowed_extension


# Форма загрузки файла
class FileForm(FlaskForm):
    file = FileField('Выберите файл', validators=[FileRequired(), allowed_extension()])
    submit = SubmitField('Отправить')