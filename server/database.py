from datetime import datetime, timedelta

import motor.motor_asyncio
from bson import ObjectId
from bson.errors import InvalidId

from server.scraper import scrap_from_search
from server.models.search_result import Period


MONGO_DETAILS = 'mongodb://mongodb:27017'
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
db = client.news

search_results_collection = db.get_collection('search_results')


def search_results_helper(search_result):
    """Take each article and convert it to JSONable format"""
    return {
        "id": str(search_result["_id"]),
        "link": search_result["link"],
        "title": search_result["title"],
        "author": search_result["author"],
        "image": search_result["image"],
        "date": search_result["date"],
        "tags": search_result["tags"],
        "description": search_result["description"],
        "content": search_result["content"]
    }


async def update_search_results(search: str):
    """Add articles to database

    Check if each article does not exist in database. If it does,
    add search words to article's 'tags' field. Else, article will
    be added to a database.
    :param search: Search query
    :return: List of articles added to a database
    """
    results = scrap_from_search(search)
    for result in results:
        if await search_results_collection.find_one({"link": result['link']}):
            new_result = await search_results_collection.find_one({"link": result['link']})
            new_result["tags"] = list(set(new_result["tags"] + result['tags']))
            await search_results_collection.update_one({"_id": ObjectId(new_result["_id"])}, {"$set": new_result})
        else:
            await search_results_collection.insert_one(result)


async def retrieve_search_result_by_id(id_: str):
    """Find concrete article in a database by ID"""
    try:
        result = await search_results_collection.find_one({"_id": ObjectId(id_)})
        if result:
            return search_results_helper(result)
    except InvalidId:
        return


async def retrieve_search_results_by_tags(tags: list[str], page: int, limit: int, period: Period):
    """Find articles by tags

    Take search words and check if database contain articles,
    which have more than 'percentage' of words in 'tags' fields matches
    with words in search query. If database have them, return
    paginated articles and total amount of them.
    :param limit: Page size
    :param page: Number of page
    :param tags: List of search words
    :param period: Filtering period
    :return: Count and List of articles
    """
    tags = list(set(tags))
    filter_expression = {
        **resolve_period_expression(period),
        **resolve_tags_expression(tags)
    }
    results = search_results_collection.find(filter_expression).sort('date', -1).skip((page - 1) * limit).limit(limit)
    count = await search_results_collection.count_documents(filter_expression)
    return count, [search_results_helper(result) async for result in results]


async def retrieve_newest_search_results(page: int, limit: int):
    """Get the newest articles from database

    :param limit: Page size
    :param page: Number of page
    :return: Count and List of articles
    """
    results = search_results_collection.find().sort('date', -1).skip((page - 1) * limit).limit(limit)
    count = await search_results_collection.count_documents({})
    return count, [search_results_helper(result) async for result in results]


async def update_content_of_article(id_: str, content: list[list]):
    """Add content to article

    :param id_: ID of existing article
    :param content: List of content
    :return: Article with content
    """
    await search_results_collection.update_one({'_id': ObjectId(id_)}, {"$set": {"content": content}})
    article = await search_results_collection.find_one({'_id': ObjectId(id_)})
    return search_results_helper(article)


def resolve_period_expression(period: Period) -> dict:
    """Create expression based on Period from query"""
    if period is Period.last_week:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        end_date = end_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        start_date = start_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        return {'date': {'$gte': start_date, '$lt': end_date}}
    if period is Period.last_month:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        end_date = end_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        start_date = start_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        return {'date': {'$gte': start_date, '$lt': end_date}}
    return {}


def resolve_tags_expression(tags: list[str]) -> dict:
    """Create expression based on search tags"""
    percentage = 0.75
    return {
        '$expr': {
            '$function': {
                'body': """
                    function(search, document, percentage) {
                        const searchTags = search;
                        const documentTags = document;
                        const intersection = documentTags.filter(tag => searchTags.includes(tag));
                        return intersection.length >= (searchTags.length * percentage);
                    }
                    """,
                'args': [tags, '$tags', percentage],
                'lang': 'js'
            }
        }
    }
