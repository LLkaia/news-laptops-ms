from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Query

from server.scraper import scrap_content
from server.models.search_result import SearchResponseModel, ExtendArticleModel, Period
from server.database import (
    update_search_results,
    retrieve_search_result_by_id,
    retrieve_search_results_by_tags,
    retrieve_newest_search_results,
    update_content_of_article,
)


router = APIRouter()


@router.get("/search", status_code=status.HTTP_200_OK, response_model=SearchResponseModel)
async def get_search_results(find: Annotated[str | None, Query(description='Write search query here')] = None,
                             page: Annotated[int, Query(ge=1)] = 1,
                             limit: Annotated[int, Query(ge=1, le=10)] = 5,
                             period: Period = Period.all):
    """Find articles by search query

    Get list of articles which match with search query from database.
    If count of articles is less than 10, scrap new articles and add
    them to a database. If 'find' param is empty, return newest
    articles.
    """
    if find:
        count, results = await retrieve_search_results_by_tags(find.split(), page, limit, period)
        if count < 5:
            await update_search_results(find)
            count, results = await retrieve_search_results_by_tags(find.split(), page, limit, period)
        return {'count': count, 'results': results}
    count, results = await retrieve_newest_search_results(page, limit)
    return {'count': count, 'results': results}


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ExtendArticleModel)
async def get_article(id: str):
    """Get concrete article with content

    Find article by ID in database and if it exists, check if it
    has content in 'content' field. If it is, return it, else scrap
    this content. If article is not exist in db, return 404.
    """
    result = await retrieve_search_result_by_id(id)
    if result:
        if not result['content']:
            content = scrap_content(result['link'])
            result = await update_content_of_article(id, content)
        return result
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
