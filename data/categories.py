import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# Категория
class Category(SqlAlchemyBase):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    cards = orm.relation("Card", secondary="association", backref="categories")


    def __lt__(self, other):
        if self.title < other.title:
            return True
        return False