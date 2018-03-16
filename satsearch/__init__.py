from satsearch.search import Search
from satsearch.scene import Scene, Scenes

import logging

# quiet loggers
logging.getLogger('urllib3').propagate = False
logging.getLogger('requests').propagate = False
