import os

# API URL
API_URL = os.getenv('SATUTILS_API_URL', 'https://earth-search-legacy.aws.element84.com')

# data directory to store downloaded imagery
DATADIR = os.getenv('SATUTILS_DATADIR', '${collection}/${date}')

# filename pattern for saving files
FILENAME = os.getenv('SATUTILS_FILENAME', '${id}')
