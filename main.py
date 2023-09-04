import logging
from pprint import pprint
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

urllib3_logger = logging.getLogger('urllib3.connectionpool')
urllib3_logger.propagate = False

from journals.language import parsed_papers as parse_language

for p in parse_language():
    pprint(p)
