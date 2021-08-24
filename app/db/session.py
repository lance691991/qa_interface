from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from elasticsearch_dsl import connections

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SessionES = connections.create_connection(hosts=settings.ES_URI, timeout=20)

# postgres connection