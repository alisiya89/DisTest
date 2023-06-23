import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# Тип вопроса
class Type(SqlAlchemyBase):
    __tablename__ = 'types'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)