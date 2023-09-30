# https://www.jbe-platform.com/content/journals/15699730

JOURNAL_NAME = "ENGLISH WORLD-WIDE"
JOURNAL_LINK = "https://www.jbe-platform.com/content/journals/15699730/browse?page=previous-issues"
JOURNAL_DOMAIN = "https://www.jbe-platform.com"
DELAY_MIN, DELAY_MAX = 3, 10 # wait for randint(DELAY_MIN, DELAY_MAX) seconds

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
    issues_links = []
    volume = 1
    max_volumes = 45
    pb = tqdm(initial=volume, unit="vol")
    while volume < max_volumes:
        link = f"https://www.jbe-platform.com/content/journals/15699730/issueslist?volume={volume}&showDates=false"
        logger.info(f"Parsing volume {link}...")
        bs = parse_link(link)
        issues_links.extend([ x.get('href') for x in bs.find_all('a') ])
        volume += 1; pb.update(); pb.set_description_str(f"Issues got {len(issues_links)}")
        random_sleep(DELAY_MIN, DELAY_MAX)
    return issues_links

def parse_issue(link) -> List[str]:
    bs = parse_link(JOURNAL_DOMAIN + link)
    article_box = bs.find('div', class_='issueTocContents')
    title_boxes = article_box.find_all('span', class_='articleTitle')
    hrefs = [ x.find('a').get('href') for x in title_boxes ]
    return hrefs

def parse_article(link) -> Dict:
    bs = parse_link(JOURNAL_DOMAIN + link)

    if "Welcome to e-content platform of John Benjamins Publishing" in bs.find('meta', attrs={'name':'description'}).get('content'):
        logger.info("Abstract placeholder found. Returning None")
        return None

    authors_containers = bs.find_all('meta', attrs={'name':'citation_author'})
    if len(authors_containers) == 0: 
        logger.info(f"No authors found. Returning None. ({authors_containers})")
        return None
    authors = '; '.join([ x.get('content') for x in authors_containers ])

    return {
        'doi':      bs.find('meta',     attrs={'name':'citation_doi'}).get('content'),
        'author':   authors,
        'title':    bs.find('meta',     attrs={'name':'citation_title'}).get('content'),
        'year':     bs.find('meta',     attrs={'name':'citation_year'}).get('content'),
        'abstract': bs.find('meta',     attrs={'name':'description'}).get('content'),
        'journal':  JOURNAL_NAME
    }

if __name__ == '__main__':
    issues = get_issues()
    logger.info(f"Retrieved {len(issues)} issues.")
    
    articles = []
    for link in tqdm(issues, desc="Issues"):
        new_articles = parse_issue(link)
        articles += new_articles
        logger.info(f"Retrieved {len(new_articles)} articles links from {link}. Total artices: {len(articles)}")
        random_sleep(DELAY_MIN, DELAY_MAX)
    
    for link in tqdm(articles, desc="Articles"):
        random_sleep(DELAY_MIN, DELAY_MAX)
        logger.info(f"Parsing article {link}")

        try:
            parsed_data = parse_article(link)
            if parsed_data == None:
                logger.info(f"Article parser returned None. Skipping.")
                continue
            add_to_csv(CSV_FILE, parsed_data)
        except Exception as e:
            logger.exception(f"Exception occurred while parsing article {link}: {e}")
            parsed_data = None
            continue
