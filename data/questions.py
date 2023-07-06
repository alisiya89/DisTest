import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# Вопрос
class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("types.id"))
    number = sqlalchemy.Column(sqlalchemy.Integer)
    type = orm.relation('Type')
    poll_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("polls.id"))
    poll = orm.relation('Poll')

    answers = orm.relation("Answer", back_populates='question')

    def __lt__(self, other):
        return self.number < other.number
