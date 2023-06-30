import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# Опрос
class Poll(SqlAlchemyBase):
    __tablename__ = 'polls'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    ref = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    questions = orm.relation("Question", back_populates='poll')

    def __lt__(self, other):
        return self.title < other.title

    def __eq__(self, other):
        return self.title == other.title

    def __gt__(self, other):
        return self.title > other.title