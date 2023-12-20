from fastapi import APIRouter, status, HTTPException, Query
from fastapi_pagination import Page, paginate

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
Page = Page.with_custom_options(
    size=Query(5, ge=1, le=10),
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=Page[ArticleModel])
async def get_search_results(find: str | None = None) -> Page[ArticleModel]:
    """Find articles by search query

    Get list of articles which match with search query from database.
    If count of articles is less than 10, scrap new articles and add
    them to a database. If 'find' param is empty, return newest
    articles.
    """
    if find:
        results = await retrieve_search_results_by_tags(find.split())
        if len(results) < 10:
            new_results = scrap_from_search(find)
            new_results = await add_search_results(new_results)

            # check for adding only unic
            for new_one in new_results:
                repeats = False
                for old_one in results:
                    if new_one['id'] == old_one['id']:
                        repeats = True
                        break
                if not repeats:
                    results.append(new_one)

        return paginate(results)
    return paginate(await retrieve_newest_search_results())


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ExtendArticleModel)
async def get_article(id: str) -> ExtendArticleModel:
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
