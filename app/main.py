import secrets
import string
from contextlib import asynccontextmanager

import validators
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import MetaData, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .src import models
from .src.database import engine, get_session


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)
        await conn.run_sync(MetaData().create_all)

    yield


app = FastAPI(lifespan=lifespan)


@app.post('/url')
async def shorten_url(url: str, session: AsyncSession = Depends(get_session)):
    if not validators.url(url):
        raise HTTPException(status_code=400, detail='Invalid URL provided')

    def generate_short_url(): return 'const.com/' + ''.join(secrets.choice(string.ascii_letters + string.digits)
                                             for _ in range(10))  # 10 is arbitrary
    short_url = generate_short_url()

    # in case short_url already exists
    while await models.URL.get_by_short_url(short_url, session) is not None:
        short_url = generate_short_url()

    db_url = models.URL(short_url=short_url, long_url=url)

    session.add(db_url)
    await session.commit()

    return short_url


@app.get('/url')
async def get_long_url(short_url: str, session: AsyncSession = Depends(get_session)):
    if db_url := await models.URL.get_by_short_url(short_url, session):
        return db_url.long_url
    else:
        raise HTTPException(status_code=404, detail=f'{short_url} not found')


@app.delete('/url')
async def delete_short_url(short_url: str, session: AsyncSession = Depends(get_session)):
    if await models.URL.delete_by_short_url(short_url, session) is None:
        raise HTTPException(status_code=404, detail=f'{short_url} not found')
