import os

import flask_login
from flask import Flask, render_template, redirect, abort, request
from flask_login import login_user, logout_user, login_required
from flask_login import LoginManager

from data import db_session
from forms.user import RegisterForm, LoginForm
from forms.poll import PollForm, QuestionForm, AnswerForm
from forms.test import TestForm, AskForm
from data.users import User
from data.polls import Poll
from data.questions import Question
from data.answers import Answer
from data.types import Type


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'diss_teamwork'
quest_type = 'С одним ответом'

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
                if poll_title.lower() == item.title.lower():
                    message = "У вас уже есть опрос с таким названием"
                    return render_template("index.html",
                                           title='DissTest',
                                           polls=sorted(polls),
                                           form=form,
                                           message=message)
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


# Страница с опросом для прохождения
@app.route("/test/<int:id>", methods=['GET', 'POST'])
@login_required
def test_page(id):
    form = None
    if id:
        db_sess = db_session.create_session()
        poll = db_sess.query(Poll).filter(Poll.id == id).first()
        questions = poll.questions
        form = TestForm()
        question_list = []
        for i in range(len(questions)):
            ask_form = AskForm()
            ask_form.question = questions[i].text
            if questions[i].type.name == quest_type:
                ask_form.type = 'one'
                ask_form.one_answer.name = str(i)
                ask_form.one_answer.choices = [answer.text for answer in questions[i].answers]
            else:
                ask_form.type = 'many'
                ask_form.many_answer.name = str(i)
                ask_form.many_answer.choices = [answer.text for answer in questions[i].answers]
            question_list.append(ask_form)
        form.questions = question_list
    return render_template("test.html",
                           title=poll.title,
                           poll=poll,
                           form=form)


# Страница с вопросами выбранного опроса
@app.route("/poll/<int:id>", methods=['GET', 'POST'])
@login_required
def question_page(id):
    db_sess = db_session.create_session()
    poll = db_sess.query(Poll).filter(Poll.id == id).first()
    questions = poll.questions
    form = None
    if id:
        types = [type.name for type in db_sess.query(Type).all()]
        form = QuestionForm()
        form.type.choices = types
        # form.type.default = types[0]
        # form.process()
        answer_form = AnswerForm()
        if form.validate_on_submit() and form.id.data == 'question':
            question_text = form.text.data
            for item in poll.questions:
                if question_text.lower() == item.text.lower():
                    message = "В данном опросе уже есть такой вопрос"
                    return render_template("poll.html",
                                           title=poll.title,
                                           poll=poll,
                                           questions=questions,
                                           form=[form,answer_form],
                                           message=['q', item.id, message])
            question = Question()
            question.text = question_text
            question.type = db_sess.query(Type).filter(Type.name == form.type.data).first()
            poll.questions.append(question)
            db_sess.merge(poll)
            db_sess.commit()
            return redirect(f'/poll/{id}')
        elif answer_form.validate_on_submit() and answer_form.id.data == 'answer':
            answer_text = answer_form.text.data
            question = db_sess.query(Question).filter(Question.id == answer_form.question.data).first()
            answers = question.answers
            for item in answers:
                if answer_text.lower() == item.text.lower():
                    message = "В данном вопросе уже есть такой ответ"
                    return render_template("poll.html",
                                           title=poll.title,
                                           poll=poll,
                                           questions=questions,
                                           form=[form,answer_form],
                                           message=['a', question.id, message])
            if question.type.name == quest_type and any([ans.right for ans in question.answers]) and answer_form.right.data:
                message = "В данном вопросе не может быть несколько верных ответов"
                return render_template("poll.html",
                                       title=poll.title,
                                       poll=poll,
                                       questions=questions,
                                       form=[form, answer_form],
                                       message=['a', question.id, message])
            answer = Answer()
            answer.text = answer_text
            answer.right = answer_form.right.data
            question.answers.append(answer)
            db_sess.merge(question)
            db_sess.commit()
            return redirect(f'/poll/{id}')
    return render_template("poll.html",
                           title=poll.title,
                           poll=poll,
                           questions=questions,
                           form=[form,answer_form],
                           message=['','',''])


# Изменение ответа
@app.route('/answer_change/<int:poll_id>/<int:question_id>/<int:id>', methods=['GET', 'POST'])
@login_required
def answer_change(poll_id, question_id, id):
    db_sess = db_session.create_session()
    answer = db_sess.query(Answer).filter(Answer.id == id).first()
    question = db_sess.query(Question).filter(Question.id == question_id).first()
    if question.type.name == quest_type:
        right_answer = list(filter(lambda x: x.right, question.answers))
        if right_answer:
            right_answer[0].right = False
    answer.right = not answer.right
    db_sess.commit()
    return redirect(f'/poll/{poll_id}')

# Удаление ответа
@app.route('/answer_delete/<int:poll_id>/<int:question_id>/<int:id>', methods=['GET', 'POST'])
@login_required
def answer_delete(poll_id, question_id, id):
    db_sess = db_session.create_session()
    answer = db_sess.query(Answer).filter(Answer.id == id).first()
    question = db_sess.query(Question).filter(Question.id == question_id).first()
    question.answers.remove(answer)
    db_sess.merge(question)
    db_sess.commit()
    db_sess.delete(answer)
    db_sess.commit()
    return redirect(f'/poll/{poll_id}')

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


# Публикация/снятие с публикации опроса
@app.route('/poll_publish/<int:poll_id>', methods=['GET', 'POST'])
@login_required
def poll_publish(poll_id):
    db_sess = db_session.create_session()
    poll = db_sess.query(Poll).filter(Poll.id == poll_id).first()
    if poll.ref:
        poll.ref = None
    else:
        poll.ref = f'{request.host_url}test/{poll_id}'
    db_sess.commit()
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

def add_types():
    db_sess = db_session.create_session()
    question_types = ['С одним ответом', 'С несколькими ответами', 'Без ответов']
    for item in question_types:
        type = Type(name=item)
        db_sess.add(type)
    db_sess.commit()

if __name__ == '__main__':
    db_session.global_init("db/poll.db")
    db_sess = db_session.create_session()
    if not db_sess.query(Type).first():
        add_types()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
