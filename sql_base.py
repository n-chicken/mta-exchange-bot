from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://mta:mta@127.0.0.1:3307/mta')
_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


def session_factory():
#     Base.metadata.create_all(engine) # temporarily removed due to alembic revisions
    return _SessionFactory()
