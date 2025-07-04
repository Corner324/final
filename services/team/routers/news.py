from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from deps.db import get_db
from crud.news import (
    create_news,
    get_news_item,
    get_team_news,
    update_news_item,
    delete_news_item,
)
from schemas.news import NewsCreate, NewsUpdate, NewsOut
from typing import List

router = APIRouter(prefix="/news", tags=["news"])


@router.post("/", response_model=NewsOut, status_code=status.HTTP_201_CREATED)
async def add_news(data: NewsCreate, db: AsyncSession = Depends(get_db)):
    return await create_news(db, data)


@router.get("/team/{team_id}", response_model=List[NewsOut])
async def list_team_news(team_id: int, db: AsyncSession = Depends(get_db)):
    return await get_team_news(db, team_id)


@router.get("/{news_id}", response_model=NewsOut)
async def get_news(news_id: int, db: AsyncSession = Depends(get_db)):
    item = await get_news_item(db, news_id)
    if not item:
        raise HTTPException(404, detail="News not found")
    return item


@router.patch("/{news_id}", response_model=NewsOut)
async def update_news(
    news_id: int, data: NewsUpdate, db: AsyncSession = Depends(get_db)
):
    item = await get_news_item(db, news_id)
    if not item:
        raise HTTPException(404, detail="News not found")
    item = await update_news_item(db, item, data)
    return item


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(news_id: int, db: AsyncSession = Depends(get_db)):
    item = await get_news_item(db, news_id)
    if not item:
        raise HTTPException(404, detail="News not found")
    await delete_news_item(db, item)
    return None
