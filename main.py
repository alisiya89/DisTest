import os

import flask_login
from flask import Flask, render_template, redirect, abort
from flask_login import login_user, logout_user, login_required
from flask_login import LoginManager

from data import db_session
from forms.user import RegisterForm, LoginForm, FileForm
from forms.category import CategoryForm
from forms.card import CardForm
from data.users import User
from data.categories import Category
from data.cards import Card
from api import API


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# Главная страница / страница со списком категорий пользователя
@app.route("/", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    categories = []
    form = None
    if flask_login.current_user.is_authenticated:
        current_user = flask_login.current_user
        user = db_sess.query(User).filter(User.name == current_user.name).first()
        categories = db_sess.query(Category).filter(Category.user_id == user.id)
        form = CategoryForm()
        if form.validate_on_submit():
            category_title = form.title.data
            for item in current_user.categories:
                if category_title.lower() == item.title.lower():
                    message = "У вас уже есть такая категория"
                    return render_template("index.html",
                                           title='EnglishCards',
                                           categories=sorted(categories),
                                           form=form,
                                           message=message)
            db_sess = db_session.create_session()
            category = Category()
            category.title = category_title
            category.user_id = user.id
            current_user.categories.append(category)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
    return render_template("index.html",
                           title='EnglishCards',
                           categories=sorted(categories),
                           form=form)


# Страница с карточками выбранной категории
@app.route("/category/<int:id>", methods=['GET', 'POST'])
@login_required
def category(id):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.id == id).first()
    cards = sorted(category.cards)
    form = None
    if id:
        form = CardForm()
        if form.validate_on_submit():
            card_word = form.word.data
            for item in category.cards:
                if card_word.lower() == item.word.lower():
                    message = "В данной категории уже есть такое слово"
                    return render_template("category.html",
                                           title=category.title,
                                           category = category,
                                           cards=cards, form=form,
                                           message=message)
            db_sess = db_session.create_session()
            card = Card()
            card.word = form.word.data
            api = API()
            translation = api.get_translation(card.word)
            if translation != 404:
                card.translation = api.get_translation(card.word)
                category.cards.append(card)
                db_sess.merge(category)
                db_sess.commit()
            else:
                return render_template('/category.html',
                                       title=category.title,
                                       category = category,
                                       cards=cards,
                                       form=form,
                                       message="Перевод не найден")
            return redirect(f'/category/{id}')
    return render_template("category.html",
                           title=category.title,
                           category = category,
                           cards=cards,
                           form=form)


# Удаление карточки
@app.route('/card_delete/<int:cat_id>/<int:id>', methods=['GET', 'POST'])
@login_required
def card_delete(cat_id, id):
    db_sess = db_session.create_session()
    card = db_sess.query(Card).filter(Card.id == id).first()
    category = db_sess.query(Category).filter(Category.id == cat_id).first()
    category.cards.remove(card)
    db_sess.merge(category)
    db_sess.commit()
    categories = card.categories
    if len(categories) == 0:
        db_sess.delete(card)
        db_sess.commit()
    return redirect(f'/category/{cat_id}')


# Удаление категории
@app.route('/category_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def category_delete(id):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.id == id).first()
    if category:
        db_sess.delete(category)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


# Выход из личного кабинета
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Загрузка картинки для аватара
@app.route('/load_image', methods=['GET', 'POST'])
@login_required
def load_image():
    form = FileForm()
    if form.validate_on_submit():
        user = flask_login.current_user
        file = form.file.data
        filename = f'images/{user.id}{file.filename[file.filename.find("."):]}'
        with open(f'static/{filename}', "wb") as f:
            f.write(file.read())
        user.set_avatar(filename)
        db_sess = db_session.create_session()
        db_sess.merge(user)
        db_sess.commit()
        return redirect("/")
    return render_template('load_image.html', title='Загрузка файла', form=form)


# Регистрация пользователя
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
        )
        user.set_password(form.password.data)
        user.set_avatar('images/avatar.png')
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


# Авторизация пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/cards.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)