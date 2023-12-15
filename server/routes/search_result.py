from fastapi import APIRouter, status, HTTPException

from server.scraper import scrap_from_search, scrap_content
from server.models.search_result import ArticleModel, ExtendArticleModel
from server.database import (
    add_search_results,
    retrieve_search_result_by_id,
    retrieve_search_results_by_tags,
    retrieve_newest_search_results,
    update_content_of_article,
)


router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ArticleModel])
async def get_search_results(find: str | None = None) -> list[ArticleModel]:
    if find:
        results = await retrieve_search_results_by_tags(find.split())
        if len(results) < 20:
            new_results = scrap_from_search(find)
            new_results = await add_search_results(new_results)
            results.extend(new_results)
        return results[:20]
    return await retrieve_newest_search_results()


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ExtendArticleModel)
async def get_article(id: str) -> ExtendArticleModel:
    result = await retrieve_search_result_by_id(id)
    if result:
        if not result['content']:
            content = scrap_content(result['link'])
            result = await update_content_of_article(id, content)
        return result
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
