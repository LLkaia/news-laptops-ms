from fastapi import FastAPI

from server.routes.search_result import router as SearchResultRouter


app = FastAPI()
app.include_router(SearchResultRouter, tags=["News"], prefix="/news")
