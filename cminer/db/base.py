from settings import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as session_maker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base = declarative_base(bind=engine)
session_maker = session_maker(bind=engine)
