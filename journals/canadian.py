# http://journals.cambridge.org/CNJ

JOURNAL_NAME = "CANADIAN JOURNAL OF LINGUISTICS"
JOURNAL_LINK = "https://www.cambridge.org/core/journals/canadian-journal-of-linguistics-revue-canadienne-de-linguistique/all-issues"
JOURNAL_DOMAIN = "http://cambridge.org"
DELAY_MIN, DELAY_MAX = 0.5, 1.5 # wait for randint(DELAY_MIN, DELAY_MAX) seconds

from typing import List, Dict
import logging
from pprint import pprint
import re
""" if __name__ == "__main__":
    from utils import *
else:
    from .utils import * """
from utils import *

logger = logging.getLogger(__name__)
logging.basicConfig(filename=f'journals/log/{JOURNAL_NAME.lower().replace(" ", "_")}.log', level=logging.INFO)
CSV_FILE = get_csv_name(JOURNAL_NAME.replace(' ', '_'))

def get_issues_links() -> List[str]:
    bs = parse_link(JOURNAL_LINK)
    issues_container = bs.find(class_='journal-all-issues')
    all_links = [ JOURNAL_DOMAIN + x.get('href') for x in issues_container.find_all("a") ]
    all_links = list(filter(lambda x: re.match(r'.*/issue/.*', x), all_links))

    return all_links

def parse_issue(link) -> List[str]:
    bs = parse_link(link)
    # only articles have abstracts. So we search abstracts first
    abstracts = bs.select('li.accordion.abstract')
    articles = [ x.parent for x in abstracts ]
    articles_links = [ x.find('h3').find('a').get('href') for x in articles ]

    return [ JOURNAL_DOMAIN + x for x in articles_links ]

def parse_artile(link) -> Dict:
    bs = parse_link(link)

    raw_doi = bs.find('meta',     attrs={'name':'dc.identifier'}).get('content')
    doi = raw_doi.replace('doi:', '')

    authors_containers = bs.find_all('meta', attrs={'name':'citation_author'})
    authors = '; '.join([ x.get('content') for x in authors_containers ])

    raw_pub_year = bs.find('meta',     attrs={'name':'citation_publication_date'}).get('content')
    # raw_pub_year format example: 1987/08. We need only year
    year = re.sub(r'/.*', '', raw_pub_year)

    return {
        'doi':      doi,
        'author':   authors,
        'title':    bs.find('meta',     attrs={'name':'citation_title'}).get('content'),
        'year':     year,
        'abstract': bs.find('meta',     attrs={'name':'citation_abstract'}).get('content'),
        'journal':  JOURNAL_NAME
    }

if __name__ == '__main__':
    logger.debug(f"Parsing issues links. Journal: '{JOURNAL_NAME}'; link: {JOURNAL_LINK}")
    issues_links = get_issues_links()
    logger.info(f"Retrieved {len(issues_links)} issues links from {JOURNAL_LINK}")

    articles_links = []
    for i, link in enumerate(issues_links):
        new_article_links = parse_issue(link)
        articles_links += new_article_links
        logger.info(f"[{i+1}/{len(issues_links)}] Retrieved {len(new_article_links)} articles links from {link}. Total artices: {len(articles_links)}")
        random_sleep(DELAY_MIN, DELAY_MAX)

    for i, link in enumerate(articles_links):
        logger.info(f"[{i+1}/{len(articles_links)}] Parsing article {link}")
        
        try:
            parsed_data = parse_artile(link)
            add_to_csv(CSV_FILE, parsed_data)
        except Exception as e:
            logger.exception(f"Exception occurred while parsing article {link}: {e}")
            parsed_data = None
            continue

        random_sleep(DELAY_MIN, DELAY_MAX)
