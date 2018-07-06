import os

# API URL
API_URL = os.getenv('SATUTILS_API_URL', 'https://sat-api.developmentseed.org')

# data directory to store downloaded imagery
DATADIR = os.getenv('SATUTILS_DATADIR', './${eo:platform}/${date}')

# filename pattern for saving files
FILENAME = os.getenv('SATUTILS_FILENAME', '${id}')
