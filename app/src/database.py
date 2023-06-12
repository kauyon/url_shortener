from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .env import DB_URL

engine = create_async_engine(DB_URL, echo=True)
Session = sessionmaker(engine, autocommit=False, autoflush=False, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_session() -> AsyncSession:
    async with Session() as session:
        yield session
