from satsearch.search import Search

import logging

# quiet loggers
logging.getLogger('urllib3').propagate = False
logging.getLogger('requests').propagate = False
