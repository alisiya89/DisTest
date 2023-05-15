import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# Результаты
class Result(SqlAlchemyBase):
    __tablename__ = 'results'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    mark = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    poll_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("polls.id"))
    poll = orm.relation('Poll')

    questions = orm.relation("ResultQuestion", back_populates='result')
