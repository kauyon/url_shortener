from __future__ import annotations

from sqlalchemy import Column, Integer, String, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import Base


class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer, index=True, primary_key=True)
    short_url = Column(String, unique=True, index=True)
    long_url = Column(String, index=True)

    @classmethod
    async def get_by_short_url(cls, short_url: str, session: AsyncSession) -> URL | None:
        result = await session.execute(select(URL).where(URL.short_url == short_url))
        return result.scalar()

    @classmethod
    async def delete_by_short_url(cls, short_url: str, session: AsyncSession) -> int | None:
        result = await session.execute(delete(URL).where(URL.short_url == short_url).returning(URL.id))
        await session.commit()
        return result.scalar()
