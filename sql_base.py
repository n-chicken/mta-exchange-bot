from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    'mysql+pymysql://mta:mta@127.0.0.1:3307/mta', 
    connect_args={'connect_timeout': 120},
    pool_pre_ping=True,
    pool_recycle=900)

_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


def session():
    Base.metadata.create_all(engine)
    return _SessionFactory()
