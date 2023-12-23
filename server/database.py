import motor.motor_asyncio
from bson import ObjectId
from bson.errors import InvalidId

from server.scraper import scrap_from_search


MONGO_DETAILS = 'mongodb://localhost:27017'
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


async def retrieve_search_results_by_tags(tags: list[str]):
    """Find articles by tags

    Take search words and check if database contain articles,
    which have more than :percentage: of words in 'tags' fields matches
    with words in search query. If database have them, return
    this articles.
    :param tags: List of search words
    :return: List of articles
    """
    percentage = 0.75
    tags = list(set(tags))
    js_function = """
    function() {
        const searchTags = %s;
        const documentTags = this.tags;
        const intersection = documentTags.filter(tag => searchTags.includes(tag));
        return intersection.length >= (searchTags.length * %f);
    }
    """ % (str(tags), percentage)
    documents = search_results_collection.find({'$where': js_function})
    return [search_results_helper(result) async for result in documents]


async def retrieve_newest_search_results():
    """Get 20 newest articles from database"""
    results = []
    async for result in search_results_collection.find().sort('date', -1).limit(20):
        results.append(search_results_helper(result))
    return results


async def update_content_of_article(id_: str, content: list[list]):
    """Add content to article

    :param id_: ID of existing article
    :param content: List of content
    :return: Article with content
    """
    await search_results_collection.update_one({'_id': ObjectId(id_)}, {"$set": {"content": content}})
    article = await search_results_collection.find_one({'_id': ObjectId(id_)})
    return search_results_helper(article)
