import asyncio

from server.database import add_newest_news
from server.scraper import scrap_newest


if __name__ == '__main__':
    laptops = scrap_newest()
    asyncio.run(add_newest_news(laptops))
