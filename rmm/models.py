from datetime import datetime, timedelta

import os
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from utils import session_scope

Base = declarative_base()
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING", 'sqlite:///db.sqlite')

print('connecting to DB:', DB_CONNECTION_STRING, flush=True)
engine = create_engine(DB_CONNECTION_STRING, echo=False)


class Meme(Base):
    __tablename__ = 'memes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    posted_at = Column(DateTime)
    user_id = Column(String, ForeignKey('users.id'))
    file_type = Column(String)
    file_id = Column(String)

    def __init__(self, user_id, file_type, file_id):
        self.posted_at = datetime.utcnow().replace(microsecond=0)
        self.user_id = user_id
        self.file_type = file_type
        self.file_id = file_id

    def save(self):
        with session_scope(engine) as session:
            session.add(self)
            session.commit()
        return self

    def __repr__(self):
        return f'Meme(id={self.id}, user_id={self.user_id}, file_type={self.file_type})'


class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    voted_at = Column(DateTime)
    meme_id = Column(Integer, ForeignKey('memes.id'))
    mark = Column(Integer)

    def __init__(self, user_id, meme_id, mark):
        self.voted_at = datetime.utcnow().replace(microsecond=0)
        self.user_id = user_id
        self.meme_id = meme_id
        self.mark = mark

    def save(self):
        with session_scope(engine) as session:
            session.add(self)
            session.commit()
        return self

    @staticmethod
    def is_voted(user_id, meme_id):
        with session_scope(engine) as session:
            query = session.query(Vote).join(Meme).filter(Meme.user_id == user_id, Meme.id == meme_id)
            is_marked = query.count() > 0
            return is_marked


class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    registred_at = Column(DateTime)
    points = Column(Integer, default=0)
    username = Column(String)
    fullname = Column(String)

    def __init__(self, id, username, fullname):
        self.registred_at = datetime.utcnow().replace(microsecond=0)
        self.points = 0
        self.username = username
        self.fullname = fullname
        self.id = id

    def save(self):
        with session_scope(engine) as session:
            session.add(self)
            session.commit()
        return self

    def __repr__(self):
        return f'User(id={self.id}, username={self.username}, fullname={self.fullname}, points={self.points})'

    @staticmethod
    def add_points(user_id, points):
        with session_scope(engine) as session:
            user = session.query(User).filter_by(id=user_id).first()
            user.points += points

    @staticmethod
    def is_exists(id):
        with session_scope(engine) as session:
            return (session.query(User).filter_by(id=id).count()) > 0

    @staticmethod
    def get(id):
        with session_scope(engine) as session:
            return session.query(User).filter_by(id=id).first()


def init_models():
    Base.metadata.create_all(engine)


# Создание таблицы
if __name__ == '__main__':
    Vote.is_voted(1, 1)
    # Base.metadata.create_all(engine)
