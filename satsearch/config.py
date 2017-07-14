import os

# API URL
SAT_API = os.getenv('SAT_API', 'https://api.developmentseed.org/satellites')

# Data directory to store downloaded imagery
DATADIR = os.getenv('SATUTILS_DATADIR', os.path.expanduser('~/satutils-data'))

# do not create subdirectories of satellite_name/scene_id when saving imagery
NOSUBDIRS = False
