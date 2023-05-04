import sqlalchemy
from .db_session import SqlAlchemyBase


association_table = sqlalchemy.Table(
    'association',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('card', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('cards.id')),
    sqlalchemy.Column('category', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('categories.id'))
)


# Карточка со словом и его переводом
class Card(SqlAlchemyBase):
    __tablename__ = 'cards'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    word = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    translation = sqlalchemy.Column(sqlalchemy.String, nullable=False)


    def __lt__(self, other):
        if self.word < other.word:
            return True
        return False