import logging
logging.basicConfig(filename='main.log', level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)

urllib3_logger = logging.getLogger('urllib3.connectionpool')
urllib3_logger.propagate = False

from journals.language import parsed_articles as parse_language

for p in parse_language():
    pass
