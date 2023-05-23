import os

import flask_login
from flask import Flask, render_template, redirect, abort
from flask_login import login_user, logout_user, login_required
from flask_login import LoginManager

from data import db_session
from forms.user import RegisterForm, LoginForm
from forms.poll import PollForm
from forms.question import QuestionForm
from data.users import User
from data.polls import Poll
from data.questions import Question


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'diss_teamwork'

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# Главная страница / страница со списком тестов
@app.route("/", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    polls = []
    form = None
    if flask_login.current_user.is_authenticated:
        current_user = flask_login.current_user
        user = db_sess.query(User).filter(User.name == current_user.name).first()
        polls = db_sess.query(Poll).filter(Poll.user_id == user.id)
        form = PollForm()
        if form.validate_on_submit():
            poll_title = form.title.data
            for item in current_user.polls:
                if poll_title.lower() == item.name.lower():
                    message = "У вас уже есть опрос с таким названием"
                    return render_template("index.html",
                                           title='DissTest',
                                           polls=sorted(polls),
                                           form=form,
                                           message=message)
            db_sess = db_session.create_session()
            poll = Poll()
            poll.title = poll_title
            poll.user_id = user.id
            current_user.polls.append(poll)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
    return render_template("index.html",
                           title='DissTest',
                           polls=sorted(polls),
                           form=form)


# Страница с вопросами выбранного опроса
@app.route("/poll/<int:id>", methods=['GET', 'POST'])
@login_required
def question_page(id):
    db_sess = db_session.create_session()
    poll = db_sess.query(Poll).filter(Poll.id == id).first()
    questions = sorted(poll.questions)
    form = None
    if id:
        form = QuestionForm()
        if form.validate_on_submit():
            question_text = form.text.data
            for item in poll.questions:
                if question_text.lower() == item.text.lower():
                    message = "В данном опросе уже есть такой вопрос"
                    return render_template("poll.html",
                                           title=poll.title,
                                           poll=poll,
                                           questions=questions,
                                           form=form,
                                           message=message)
            db_sess = db_session.create_session()
            question = Question()
            question.text = form.text.data
            poll.questions.append(question)
            db_sess.merge(poll)
            db_sess.commit()
            return redirect(f'/poll/{id}')
    return render_template("poll.html",
                           title=poll.title,
                           poll=poll,
                           questions=questions,
                           form=form)


# Удаление вопроса
@app.route('/question_delete/<int:poll_id>/<int:id>', methods=['GET', 'POST'])
@login_required
def question_delete(poll_id, id):
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id == id).first()
    poll = db_sess.query(Poll).filter(Poll.id == poll_id).first()
    poll.questions.remove(question)
    db_sess.merge(poll)
    db_sess.commit()
    db_sess.delete(question)
    db_sess.commit()
    return redirect(f'/poll/{poll_id}')


# Удаление опроса
@app.route('/poll_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def poll_delete(id):
    db_sess = db_session.create_session()
    poll = db_sess.query(Poll).filter(Poll.id == id).first()
    if poll:
        db_sess.delete(poll)
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
            name=form.name.data
        )
        user.set_password(form.password.data)
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
            login_user(user)
            return redirect("/")
        return render_template('login.html',
                               title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/poll.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)