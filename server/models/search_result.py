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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "657b4a8d9e6d5419e28aa3e1",
                    "link": "https://www.laptopmag.com/best-picks/tips-to-improve-macbook-sound",
                    "tags": ["acer", "aspire", "nvidia"],
                    "image": "https://cdn.mos.cms.futurecdn.net/vzWy7ZzZy4rfZUESfUw4Lg.jpg",
                    "title": "7 ways to improve sound on your MacBook",
                    "author": "Alex Bracetti",
                    "date": "2023-05-20T07:00:53Z",
                    "description": "Unhappy with the MacBook’s sound quality? Here are some tips and tricks to enhance "
                                   "the audio performance on your Apple laptop."
                },
            ]
        }
    }


class ExtendArticleModel(ArticleModel):
    content: list[list] = []
