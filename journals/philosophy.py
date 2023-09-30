# http://www.springeronline.com/journal/10988/about

JOURNAL_NAME = "LINGUISTICS AND PHILOSOPHY"
JOURNAL_LINK = "https://link.springer.com/journal/10988/volumes-and-issues"
JOURNAL_DOMAIN = "https://link.springer.com"
DELAY_MIN, DELAY_MAX = 1, 4 # wait for randint(DELAY_MIN, DELAY_MAX) seconds

SLEEP_ON_NETWORK_ERR = 60

from typing import List, Dict
from pprint import pprint
import logging
import re
from tqdm import tqdm

from utils import *

logger = logging.getLogger(__name__)
logging.basicConfig(filename=f'journals/log/{JOURNAL_NAME.replace(" ", "_").lower()}.log', level=logging.INFO)
CSV_FILE = get_csv_name(JOURNAL_NAME.replace(' ', '_'))

def get_issues() -> List[str]:
    bs = parse_link(JOURNAL_LINK)
    volumes_container = bs.find(class_='u-list-reset')
    return list(set([ JOURNAL_DOMAIN + x.get('href') for x in volumes_container.find_all('a') ]))

def parse_issue(link) -> List[str]:
    bs = parse_link(link)
    article_headings = bs.find_all('h3', class_='c-card__title')
    return list(set([ x.find('a').get('href') for x in article_headings ]))

def parse_article(link) -> Dict:
    bs = parse_link(link)

    authors_containers = bs.find_all('meta', attrs={'name':'citation_author'})
    authors = [ x.get('content') for x in authors_containers ]
    # for some reason author format is "Heller, Daphna" instead of "Daphna Heller" or "Cresswell, M. J." instead of "M. J. Cresswell"
    # We split it "Cresswell, M. J." -> ["Cresswell", "M. J."]
    # Then reversing the list and joining it -> "M. J. Cresswell"
    authors = [ ' '.join(x.split(', ')[::-1]) for x in authors ]
    authors = '; '.join(authors)

    raw_pub_year = bs.find('meta',     attrs={'name':'citation_publication_date'}).get('content')
    # raw_pub_year format example: 1986/04. We need only year
    year = re.sub(r'/.*', '', raw_pub_year)

    return {
        'doi':      bs.find('meta',     attrs={'name':'citation_doi'}).get('content'),
        'author':   authors,
        'title':    bs.find('meta',     attrs={'name':'citation_title'}).get('content'),
        'year':     year,
        'abstract': bs.find('meta',     attrs={'name':'dc.description'}).get('content'),
        'journal':  JOURNAL_NAME
    }

if __name__ == "__main__":
    issues = get_issues()
    logger.info(f"Retrieved {len(issues)} issues.")
    
    articles = []
    for link in tqdm(issues, desc="Issues"):
        new_articles = parse_issue(link)
        articles += new_articles
        logger.info(f"Retrieved {len(new_articles)} articles links from {link}. Total artices: {len(articles)}")
        random_sleep(DELAY_MIN, DELAY_MAX)
    
    for link in tqdm(articles, desc="Articles"):
        logger.info(f"Parsing article {link}")

        try:
            parsed_data = parse_article(link)
            add_to_csv(CSV_FILE, parsed_data)
        except Exception as e:
            logger.exception(f"Exception occurred while parsing article {link}: {e}")
            parsed_data = None
            continue

        random_sleep(DELAY_MIN, DELAY_MAX)
