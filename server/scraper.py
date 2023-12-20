import requests
from bs4 import BeautifulSoup


headers = {
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/'
        'webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
}


def scrap_from_search(search: str) -> list[dict]:
    """Take search query and return list of articles

    :param search: Query string with what user want to find
    :return: Result of search - list of articles
    """
    link_src = f'https://www.laptopmag.com/search?searchTerm={search}&articleType=best-pick'
    page_src = requests.get(link_src, headers)
    soup_src = BeautifulSoup(page_src.content, 'html.parser')

    # parse search result
    laptops = soup_src.find_all('div', class_='listingResult')
    laptops_data = []
    for laptop in laptops:
        dct = dict()
        dct['link'] = laptop.find('a', class_='article-link').get('href')
        dct['image'] = laptop.find('img').get('data-pin-media')
        dct['title'] = laptop.find('h3', class_='article-name').text.strip()
        dct['author'] = laptop.find('span', attrs={'style': 'white-space:nowrap'}).text.strip()
        dct['date'] = laptop.find('time').get('datetime')
        dct['description'] = laptop.find('p', class_='synopsis').text.strip()
        dct['tags'] = search.split()
        dct['content'] = []
        laptops_data.append(dct)
    return laptops_data


def scrap_content(link: str) -> list[list]:
    """Parse concrete article's content

    :param link: URL of article
    :return: list of content where each list contain type of content and content itself
    """
    page_src = requests.get(link, headers)
    soup_src = BeautifulSoup(page_src.content, 'html.parser')

    content = []
    body = soup_src.find('div', id='article-body')
    for block in body.children:
        if block.name == 'p':
            paragraph = block.text
            if ' ' in paragraph:
                paragraph = paragraph.replace(' ', ' ')
            content.append(('paragraph', paragraph))
        elif block.name == 'h2':
            title = block.text
            content.append(('title', title))
        elif block.name == 'figure':
            image = block.find('img').get('data-pin-media')
            content.append(('image', image))
    return content
