import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# Вопросы результата
class ResultQuestion(SqlAlchemyBase):
    __tablename__ = 'result_questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    result_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("results.id"))
    result = orm.relation('Result')
    question_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("questions.id"))
    question = orm.relation('Question')

    answers = orm.relation("ResultAnswer", back_populates='question')

