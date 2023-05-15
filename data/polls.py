import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# Опрос
class Poll(SqlAlchemyBase):
    __tablename__ = 'polls'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    ref = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    questions = orm.relation("Question", back_populates='poll')