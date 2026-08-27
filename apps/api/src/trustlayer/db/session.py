from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from trustlayer.config import settings

engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
