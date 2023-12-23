from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ArticleModel(BaseModel):
    id: str
    link: HttpUrl
    title: str
    author: str | None = None
    image: HttpUrl | None = None
    date: datetime | None = None
    description: str = ""
    tags: set[str] = set()


class SearchResponseModel(BaseModel):
    count: int
    results: list[ArticleModel]


class ExtendArticleModel(ArticleModel):
    content: list[list] = []
