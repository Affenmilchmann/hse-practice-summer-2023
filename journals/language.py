JOURNAL_NAME = "LANGUAGE"
JOURNAL_LINK = "https://muse.jhu.edu/journal/112"
JOURNAL_DOMAIN = "https://muse.jhu.edu"
DELAY_MIN, DELAY_MAX = 2, 4 # wait for randint(REQUEST_DELAY) seconds

from typing import List, Dict
from requests import get
from pprint import pprint
import logging
import re

if __name__ == "__main__":
    from utils import *
else:
    from .utils import *

logger = logging.getLogger(__name__)
CSV_FILE = get_csv_name(JOURNAL_NAME)

# faking user agent since 
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}

def get_volumes_links() -> List[str]:
    logger.debug(f"Parsing volumes links. Journal: {JOURNAL_NAME}; link: {JOURNAL_LINK}")
    bs = parse_link(JOURNAL_LINK, fake_agent=True)

    links_container = bs.find(id="available_issues_list_text")
    all_links = [ JOURNAL_DOMAIN + x.get('href') for x in links_container.find_all("a") ]
    logger.info(f"Retrieved {len(all_links)} volumes links from {JOURNAL_LINK}")

    return all_links

def parse_volume(link) -> List[str]:
    logger.debug(f"Parsing volume's articles. Link: {link}")
    bs = parse_link(link, fake_agent=True)

    # getting containers of every article
    all_containers = bs.find_all(class_="card_text")
    title_container = all_containers[0]
    article_containers = all_containers[1:]
    # getting title
    title = title_container.find('a').text
    # first link in every container is an article link
    all_links = [ x.find('a').get('href') for x in article_containers ]
    # filtering hrefs. Target link format example: "/pub/24/article/452307/summary"
    all_links = filter(lambda x: x and re.match(r'.*/article/.*', x), all_links)
    all_links = [ JOURNAL_DOMAIN + x for x in all_links ]
    logger.info(f"Retrieved {len(all_links)} article links from '{title}'.")

    return all_links

def get_all_papers_links() -> List[str]:
    papers_links = []
    volumes_links = get_volumes_links()
    
    for vol in volumes_links[:1]:
        papers_links += parse_volume(vol)
        random_sleep(DELAY_MIN, DELAY_MAX)

    pprint(papers_links)
    logger.info(f"Retrieved {len(papers_links)} paper links ({len(set(papers_links))} are unique)")
    return list(set(papers_links))

def parse_paper(link) -> Dict:
    logger.info(f"Parsing paper {link}")
    bs = parse_link(link, fake_agent=True)

    authors_containers = bs.find_all('meta', attrs={'name':'citation_author'})
    authors = '; '.join([ x.get('content') for x in authors_containers ])

    abstract_container = bs.find('div', attrs={'class':'abstract'})
    abstract_paragraphs = [ x.text for x in abstract_container.find('p') ]
    abs_stoplist = ['abstract', 'abstract:']
    abs_filter = lambda x: x and isinstance(x, str) and x.lower().strip() not in abs_stoplist
    abstract_paragraphs = filter(abs_filter, abstract_paragraphs)

    return {
        'doi':      bs.find('meta',     attrs={'name':'citation_doi'}).get('content'),
        'author':   authors,
        'title':    bs.find('meta',     attrs={'name':'citation_title'}).get('content'),
        'year':     bs.find('meta',     attrs={'name':'citation_year'}).get('content'),
        'abstract': ''.join(abstract_paragraphs),
        'journal':  JOURNAL_NAME
    }

def parsed_papers() -> Dict:
    paper_links = get_all_papers_links()
    for l in paper_links:
        parsed_data = parse_paper(l)

        add_to_csv(CSV_FILE, parsed_data)
        yield parsed_data
        
        random_sleep(DELAY_MIN, DELAY_MAX)
