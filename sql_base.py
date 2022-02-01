from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://mta:mta@127.0.0.1:3307/mta', pool_recycle=3600)
_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


def session():
    Base.metadata.create_all(engine)
    return _SessionFactory()
