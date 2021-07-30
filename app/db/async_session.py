from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, future=True)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine,expire_on_commit=False, class_=AsyncSession)

