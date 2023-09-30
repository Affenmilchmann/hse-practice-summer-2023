JOURNAL_NAME = "LANGUAGE"
JOURNAL_LINK = "https://muse.jhu.edu/journal/112"
JOURNAL_DOMAIN = "https://muse.jhu.edu"
DELAY_MIN, DELAY_MAX = 1, 2 # wait for randint(DELAY_MIN, DELAY_MAX) seconds

from typing import List, Dict
import logging
import re
if __name__ == "__main__":
    from utils import *
else:
    from .utils import *

logger = logging.getLogger(__name__)
logging.basicConfig(filename=f'journals/log/{JOURNAL_NAME.lower()}.log', level=logging.INFO)
CSV_FILE = get_csv_name(JOURNAL_NAME)


def get_volumes_links() -> List[str]:
    logger.debug(f"Parsing volumes links. Journal: {JOURNAL_NAME}; link: {JOURNAL_LINK}")
    bs = parse_link(JOURNAL_LINK, fake_agent=True)

    links_container = bs.find(id="available_issues_list_text")
    all_links = [ JOURNAL_DOMAIN + x.get('href') for x in links_container.find_all("a") ]
    logger.info(f"Retrieved {len(all_links)} volumes links from {JOURNAL_LINK}")

    return all_links

def parse_volume(link) -> List[str]:
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

    return all_links, title

def get_all_articles_links() -> List[str]:
    articles_links = []
    volumes_links = get_volumes_links()
    
    for i, vol in enumerate(volumes_links):
        logger.debug(f"Parsing volume's articles. Link: {vol}")
        new_links, title = parse_volume(vol)
        articles_links += new_links
        logger.info(f"[{i+1}/{len(volumes_links)}] Retrieved {len(new_links)} article links from '{title}'. ({len(articles_links)} total links)")
        random_sleep(DELAY_MIN, DELAY_MAX)

    logger.info(f"Retrieved {len(articles_links)} articles links ({len(set(articles_links))} are unique)")
    return list(set(articles_links))

def parse_article(link) -> Dict:
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

def parse():
    article_links = get_all_articles_links()
    for i, l in enumerate(article_links):
        logger.info(f"[{i+1}/{len(article_links)}] Parsing article {l}")

        try:
            parsed_data = parse_article(l)
            add_to_csv(CSV_FILE, parsed_data)
        except Exception as e:
            logger.exception(f"Exception occurred while parsing articles {l}: {e}")
            parsed_data = None
            continue

        random_sleep(DELAY_MIN, DELAY_MAX)
