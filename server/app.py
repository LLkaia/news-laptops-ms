from fastapi import FastAPI

from server.routes.search_result import router as SearchResultRouter


app = FastAPI()
app.include_router(SearchResultRouter, tags=["Search"], prefix="/news/search")


@app.get('/', tags=['Root'])
async def read_root():
    return {'message': 'Welcome!'}
