import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# Ответ
class Answer(SqlAlchemyBase):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    right = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    question_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("questions.id"))
    question = orm.relation('Question')

