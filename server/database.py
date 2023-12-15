import motor.motor_asyncio
from bson import ObjectId
from bson.errors import InvalidId


MONGO_DETAILS = 'mongodb://localhost:27017'
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
db = client.news

search_results_collection = db.get_collection('search_results')


def search_results_helper(search_result):
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


async def add_search_results(results: list[dict]):
    new_results = []
    for result in results:
        if await search_results_collection.find_one({"link": result['link']}):
            new_result = await search_results_collection.find_one({"link": result['link']})
            new_result["tags"] = list(set(new_result["tags"] + result['tags']))
            await search_results_collection.update_one({"_id": ObjectId(new_result["_id"])}, {"$set": new_result})
        else:
            result = await search_results_collection.insert_one(result)
            new_result = await search_results_collection.find_one({"_id": result.inserted_id})
        new_results.append(search_results_helper(new_result))
    return new_results


async def retrieve_search_result_by_id(id_: str):
    try:
        result = await search_results_collection.find_one({"_id": ObjectId(id_)})
        if result:
            return search_results_helper(result)
    except InvalidId:
        return


async def retrieve_search_results_by_tags(tags: list[str]):
    matched_result = []
    results = search_results_collection.find()
    search_tags = set(tags)
    async for result in results:
        common = search_tags.intersection(result["tags"])
        if len(common) > len(search_tags) / 2:
            matched_result.append(search_results_helper(result))
    return matched_result


async def retrieve_newest_search_results():
    results = []
    async for result in search_results_collection.find().sort('date', -1).limit(20):
        results.append(search_results_helper(result))
    return results


async def update_content_of_article(id_: str, content: list[list]):
    await search_results_collection.update_one({'_id': ObjectId(id_)}, {"$set": {"content": content}})
    article = await search_results_collection.find_one({'_id': ObjectId(id_)})
    return search_results_helper(article)
