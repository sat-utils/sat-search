import sys
import logging

logging.getLogger('urllib3').propagate = False
logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)
