from fastapi import FastAPI
from fastapi_pagination import add_pagination

from server.routes.search_result import router as SearchResultRouter


app = FastAPI()
add_pagination(app)
app.include_router(SearchResultRouter, tags=["News"], prefix="/news")


@app.get('/', tags=['Root'])
async def read_root():
    return {'message': 'Welcome!'}
