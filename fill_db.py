import json

from server.database import update_search_results


async def fill():
    with open('laptop_models.json') as f:
        laptops = json.load(f)
        print('[INFO] loaded laptops')
    for i, laptop in enumerate(laptops):
        name = (laptop.get('producer') + ' ' + laptop.get('model')).lower()
        print(f'[INFO] process {i} laptop')
        await update_search_results(name)

if __name__ == '__main__':
    import asyncio
    asyncio.run(fill())
