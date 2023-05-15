import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# Ответ результата
class ResultAnswer(SqlAlchemyBase):
    __tablename__ = 'result_answers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    right = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    question_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("result_questions.id"))
    question = orm.relation('ResultQuestion')
    answer_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("answers.id"))
    answer = orm.relation('Answer')