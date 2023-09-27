# https://journals.flvc.org/sal

JOURNAL_NAME = "STUDIES IN AFRICAN LINGUISTICS"
JOURNAL_LINK = "https://journals.flvc.org/sal/issue/archive"
JOURNAL_DOMAIN = "https://journals.flvc.org"
DELAY_MIN, DELAY_MAX = 1, 7 # wait for randint(DELAY_MIN, DELAY_MAX) seconds

SLEEP_ON_NETWORK_ERR = 60

from typing import List, Dict
from pprint import pprint
import logging
import re

from utils import *

logger = logging.getLogger(__name__)
logging.basicConfig(filename=f'journals/log/{JOURNAL_NAME.replace(" ", "_").lower()}.log', level=logging.INFO)
CSV_FILE = get_csv_name(JOURNAL_NAME.replace(' ', '_'))

def get_issues() -> List[str]:
    issues_links = []
    page = 1
    while True:
        logger.info(f"Parsing archive page {page}...")
        bs = parse_link(f"{JOURNAL_LINK}/{page}")
        issues_container = bs.find('ul', class_='issues_archive')
        if not issues_container:
            logger.info(f"Empty page reached. Issues parsing done!")
            break
        issues_titles = issues_container.find_all('a', class_='title')
        issues_links += [ x.get('href') for x in issues_titles ]
        logger.info(f"{len(issues_links)} issues links in total.")
        page += 1
        random_sleep(DELAY_MIN, DELAY_MAX)
    return list(set(issues_links))

def parse_issue(link) -> List[str]:
    article_links = []
    bs = parse_link(link)
    sections = bs.find_all('ul', class_='cmp_article_list')
    for sec in sections:
        heading = sec.previous_sibling.previous_sibling
        # there is link to full issue pdf which we dont want to parse
        if heading and 'full issue' in heading.text.lower():
            continue
        articles_titles = sec.find_all('h3', class_='title')
        article_links += [ x.find('a').get('href') for x in articles_titles ]
    return article_links

def parse_artile(link) -> Dict:
    bs = parse_link(link)

    authors_containers = bs.find_all('meta', attrs={'name':'citation_author'})
    authors = '; '.join([ x.get('content') for x in authors_containers ])

    raw_pub_year = bs.find('meta',     attrs={'name':'citation_date'}).get('content')
    # raw_pub_year format example: 1986/04/01. We need only year
    year = re.sub(r'/.*', '', raw_pub_year)

    return {
        'doi':      bs.find('meta',     attrs={'name':'citation_doi'}).get('content'),
        'author':   authors,
        'title':    bs.find('meta',     attrs={'name':'citation_title'}).get('content'),
        'year':     year,
        'abstract': bs.find('meta',     attrs={'name':'DC.Description'}).get('content'),
        'journal':  JOURNAL_NAME
    }

if __name__ == "__main__":
    logger.debug(f"Parsing issues links. Journal: '{JOURNAL_NAME}'; link: {JOURNAL_LINK}")
    issues_links = get_issues()
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
            logger.exception(f"Sleeping for {SLEEP_ON_NETWORK_ERR} seconds...")
            sleep(SLEEP_ON_NETWORK_ERR)
            continue

        random_sleep(DELAY_MIN, DELAY_MAX)

    pprint(articles_links)