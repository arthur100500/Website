import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Maps(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'maps'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name_map = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    file1 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    file2 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    downoload_map = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
