from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.search_result import router as SearchResultRouter


app = FastAPI()
app.include_router(SearchResultRouter, tags=["News"], prefix="/news")


origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
