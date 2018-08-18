from contextlib import contextmanager
from settings import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base = declarative_base(bind=engine)
session_maker = sessionmaker(bind=engine)


@contextmanager
def auto_commit(session, throw=True):
    try:
        yield
        session.commit()
    except Exception as e:
        session.rollback()
        if throw:
            raise e
