# https://journals.flvc.org/sal

JOURNAL_NAME = "STUDIES IN AFRICAN LINGUISTICS"
JOURNAL_LINK = "https://www.cambridge.org/core/journals/canadian-journal-of-linguistics-revue-canadienne-de-linguistique/all-issues"
JOURNAL_DOMAIN = "http://cambridge.org"
DELAY_MIN, DELAY_MAX = 0.5, 1.5 # wait for randint(DELAY_MIN, DELAY_MAX) seconds

from typing import List, Dict
from pprint import pprint
import logging
import re

from utils import *

logger = logging.getLogger(__name__)
logging.basicConfig(filename=f'journals/log/{JOURNAL_NAME.lower().replace(" ", "_")}.log', level=logging.INFO)
CSV_FILE = get_csv_name(JOURNAL_NAME.replace(' ', '_'))