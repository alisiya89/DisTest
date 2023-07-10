import csv
import os
import datetime

import flask_login
from flask import Flask, render_template, redirect, abort, request, send_from_directory, current_app
from flask_login import login_user, logout_user, login_required
from flask_login import LoginManager
from wtforms import FieldList, FormField

from data import db_session
from forms.user import RegisterForm, LoginForm
from forms.poll import PollForm, QuestionForm, AnswerForm
from forms.test import TestForm, AskForm, ManyAskForm, OneAskForm
from data.users import User
from data.polls import Poll
from data.questions import Question
from data.answers import Answer
from data.types import Type
from data.results import Result
from data.result_questions import ResultQuestion
from data.result_answers import ResultAnswer


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'diss_teamwork'
question_types = ['С одним ответом', 'С несколькими ответами', 'Без ответов']

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
def test_page(id):
    if id:
        db_sess = db_session.create_session()
        poll = db_sess.query(Poll).filter(Poll.id == id).first()
        questions = poll.questions
        no_answer_questions = list(filter(lambda x: x.type.name == question_types[2], questions))
        one_answer_questions = list(filter(lambda x: x.type.name == question_types[0], questions))
        many_answer_questions = list(filter(lambda x: x.type.name == question_types[1], questions))
        class LocalForm(TestForm): pass
        LocalForm.no_questions = FieldList(FormField(AskForm), min_entries=len(no_answer_questions))
        LocalForm.one_questions = FieldList(FormField(OneAskForm), min_entries=len(one_answer_questions))
        LocalForm.many_questions = FieldList(FormField(ManyAskForm), min_entries=len(many_answer_questions))
        form = LocalForm()
        form.id.data = poll.id
        for i in range(len(no_answer_questions)):
            form.no_questions[i].num.data = no_answer_questions[i].number
            form.no_questions[i].id = no_answer_questions[i].id
            form.no_questions[i].question = no_answer_questions[i].text
        for i in range(len(one_answer_questions)):
            form.one_questions[i].num.data = one_answer_questions[i].number
            form.one_questions[i].id = one_answer_questions[i].id
            form.one_questions[i].question = one_answer_questions[i].text
            form.one_questions[i].one_answer.choices = [(answer.id, answer.text) for answer in one_answer_questions[i].answers]
        for i in range(len(many_answer_questions)):
            form.many_questions[i].num.data = many_answer_questions[i].number
            form.many_questions[i].id = many_answer_questions[i].id
            form.many_questions[i].question = many_answer_questions[i].text
            form.many_questions[i].many_answer.choices = [(answer.id, answer.text) for answer in many_answer_questions[i].answers]
        questions = list(form.no_questions) + list(form.one_questions) + list(form.many_questions)
        questions = sorted(questions, key=lambda x: int(x.num.data))
        if form.is_submitted():
            mark = 0
            result = Result()
            result.date = datetime.date.today()
            result.poll_id = form.id.data
            for question in form.one_questions:
                result_question = ResultQuestion()
                current_question = db_sess.query(Question).filter(Question.id == question.id).first()
                result_question.question = current_question
                result_answer = ResultAnswer()
                result_answer.answer = list(filter(lambda x: x.id == question.one_answer.data, current_question.answers))[0]
                if result_answer.answer.right:
                    mark += 1
                result_question.answers.append(result_answer)
                result.questions.append(result_question)
            for question in form.many_questions:
                result_question = ResultQuestion()
                current_question = db_sess.query(Question).filter(Question.id == question.id).first()
                result_question.question = current_question
                ans_mark = 0
                for ans in question.many_answer.data:
                    result_answer = ResultAnswer()
                    result_answer.answer = list(filter(lambda x: x.id == int(ans), current_question.answers))[0]
                    if result_answer.answer.right:
                        ans_mark += 1 / len(list(filter(lambda x: x.right, current_question.answers)))
                    else:
                        ans_mark += 1 / len(list(filter(lambda x: x.right, current_question.answers)))
                    result_question.answers.append(result_answer)
                if ans_mark < 0:
                    ans_mark = 0
                mark += ans_mark
                result.questions.append(result_question)
            result.mark = mark
            db_sess.merge(result)
            db_sess.commit()
            return render_template('thank.html')
    return render_template("test.html",
                           title=poll.title,
                           poll=poll,
                           form=form,
                           questions=questions)


# Экспорт ответов
@app.route('/poll_export/<int:id>', methods=['GET'])
@login_required
def poll_export(id):
    db_sess = db_session.create_session()
    poll = db_sess.query(Poll).filter(Poll.id == id).first()
    if poll:
        with open(f'static/result_{poll.title}.csv', 'w', newline='', encoding="utf8") as f:
            writer = csv.DictWriter(
                f, fieldnames=['Дата', 'Балл'],
                delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for result in poll.results:
                writer.writerow({'Дата':result.date, 'Балл':result.mark})
        return send_from_directory('static', f'result_{poll.title}.csv')
    else:
        abort(404)




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
        answer_form = AnswerForm()
        if form.validate_on_submit() and form.id.data == 'question':
            question_text = form.text.data
            for item in poll.questions:
                if question_text.lower() == item.text.lower():
                    message = "В данном опросе уже есть такой вопрос"
                    return render_template("poll.html",
                                           title=poll.title,
                                           poll=poll,
                                           questions=sorted(questions),
                                           form=[form,answer_form],
                                           message=['q', item.id, message])
            question = Question()
            question.text = question_text
            question.type = db_sess.query(Type).filter(Type.name == form.type.data).first()
            if poll.questions:
                question.number = max(poll.questions, key=lambda x: x.number).number + 1
            else:
                question.number = 1
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
                                           questions=sorted(questions),
                                           form=[form,answer_form],
                                           message=['a', question.id, message])
            if question.type.name == question_types[0] and any([ans.right for ans in question.answers]) and answer_form.right.data:
                message = "В данном вопросе не может быть несколько верных ответов"
                return render_template("poll.html",
                                       title=poll.title,
                                       poll=poll,
                                       questions=sorted(questions),
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
                           questions=sorted(questions),
                           form=[form,answer_form],
                           message=['','',''])


# Изменение ответа
@app.route('/answer_change/<int:poll_id>/<int:question_id>/<int:id>', methods=['GET'])
@login_required
def answer_change(poll_id, question_id, id):
    db_sess = db_session.create_session()
    answer = db_sess.query(Answer).filter(Answer.id == id).first()
    question = db_sess.query(Question).filter(Question.id == question_id).first()
    if question.type.name == question_types[0]:
        right_answer = list(filter(lambda x: x.right, question.answers))
        if right_answer:
            right_answer[0].right = False
    answer.right = not answer.right
    db_sess.commit()
    return redirect(f'/poll/{poll_id}')

# Удаление ответа
@app.route('/answer_delete/<int:poll_id>/<int:question_id>/<int:id>', methods=['GET'])
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
@app.route('/question_delete/<int:poll_id>/<int:id>', methods=['GET'])
@login_required
def question_delete(poll_id, id):
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id == id).first()
    next_questions = db_sess.query(Question).filter(Question.number > question.number)
    poll = db_sess.query(Poll).filter(Poll.id == poll_id).first()
    poll.questions.remove(question)
    db_sess.merge(poll)
    db_sess.commit()
    db_sess.delete(question)
    db_sess.commit()
    for quest in next_questions:
        quest.number -= 1
        db_sess.merge(quest)
        db_sess.commit()
    return redirect(f'/poll/{poll_id}')

# Перемещение вопроса
@app.route('/question_locate/<int:poll_id>/<int:id>/<string:direct>', methods=['GET'])
@login_required
def question_locate(poll_id, id, direct):
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id == id).first()
    d = 0
    poll = db_sess.query(Poll).filter(Poll.id == poll_id).first()
    if direct == 'up' and question.number > 1:
        d = -1
    elif direct == 'down' and question.number < len(poll.questions):
        d = 1
    if d:
        near_question = db_sess.query(Question).filter(Question.number == question.number + d).first()
        question.number, near_question.number = near_question.number, question.number
        db_sess.merge(question, near_question)
        db_sess.commit()
    return redirect(f'/poll/{poll_id}')


# Удаление опроса
@app.route('/poll_delete/<int:id>', methods=['GET'])
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
@app.route('/poll_publish/<int:poll_id>', methods=['GET'])
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
